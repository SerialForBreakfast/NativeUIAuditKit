"""Offline B1 tests. Synthetic approvals never authorize a model run."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

import focus_appearance_experiment as e
import focus_mixed_assembly as a
from focus_dataset_contract import ROOT, FocusDataError, digest

REAL_RECONSTRUCT = e.reconstruct


class AppearanceTests(unittest.TestCase):
    def save(self,name,doc):
        p=self.root/name; p.write_text(json.dumps(doc)); return a.reference(p)

    def row(self,name,label,source,split,scene="scene"):
        p=self.root/(name+str(label)+".png")
        # Distinct synthetic pixels, not real training evidence.
        n=len(list(self.root.glob("*.png")))+1
        Image.new("RGB",(256,256),(n,10+label,30)).save(p)
        record=a.record(ROOT,a.reference(p))
        return {"id":name+str(label),"sourceID":name,"pairID":name,"label":label,"split":split,
                "sourceKind":source,"scene":scene,"style":"dark","control":"button",
                "relatedGroup":name,"intrinsicGroup":name,"recipeSeed":None,"frame":record,"crop":record,
                "priorUse":"untouched" if split=="test" else "development",
                "sourceBlockers":[],"manifestVersion":"1.3"}

    def setUp(self):
        parent=ROOT/".build/appearance-tests"; parent.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=parent); self.addCleanup(self.temp.cleanup); self.root=Path(self.temp.name)
        warm=self.root/"warm.pt"; warm.write_bytes(b"test-only-no-deserialization")
        rows=[]
        for name,kind,split in (("native","tvos_simulator_os","train"),("fixture","tvos_native_generator","train"),("retention","tvos_simulator_os","validation")):
            for label in (0,1):
                r=self.row(name,label,kind,split)
                r["proposedRole"]="train-candidate" if split=="train" else "retention-validation"
                rows.append(r)
        self.saved={"samples":rows,"initializationProposal":a.reference(warm)}
        self.protected=[]; self.visual=set(); self.sources={}
        p=patch.object(e,"reconstruct",side_effect=lambda spec:(copy.deepcopy(self.saved),copy.deepcopy(self.protected),self.visual)); p.start(); self.addCleanup(p.stop)
        p=patch.object(a,"source_rows",side_effect=lambda entry:copy.deepcopy(self.sources[entry["id"]])); p.start(); self.addCleanup(p.stop)
        self.spec={"version":e.INPUT_VERSION,"proposal":{},"protected":{},"additions":[],"evaluation":[],"selection":None}

    def complete(self):
        for role,split in (("appearance-validation","validation"),("final-challenge","test")):
            for stratum in sorted(e.STRATA):
                for i in range(2):
                    name=f"{role}-{stratum}-{i}"
                    rows=[self.row(name,l,"simulatorFixture",split) for l in (0,1)]
                    for r in rows: r["priorUse"]="untouched"
                    self.sources[name]=rows
                    source={"id":name,"review":self.save(name+"-review.json",{"independentFamily":name})}
                    reservation=self.save(name+"-reservation.json",{"version":"appearance-evaluation-reservation-v2",
                        "role":role,"stratum":stratum,"family":name,"previouslyUsed":False,
                        "source":source,"membershipSHA256":digest(sorted(rows,key=lambda r:r["id"])),
                        "reviewer":"test-only","reviewReference":"synthetic"})
                    self.spec["evaluation"].append({"role":role,"stratum":stratum,"source":source,"reservation":reservation})
        preliminary=e.assemble(self.spec)
        native=[r for r in preliminary["samples"] if r["use"]=="retention-validation"]
        reference=self.save("reference.json",{"version":"appearance-retention-reference-v1",
            "model":self.saved["initializationProposal"],"threshold":.85,"membershipSHA256":digest(native),
            "reviewer":"test-only","reviewReference":"synthetic",
            "predictions":[{"id":r["id"],"label":r["label"],"probability":.95 if r["label"] else .1} for r in native]})
        self.spec["selection"]={"policy":e.SELECTION,"threshold":.85,"nativeRetentionFloor":1.,"reference":reference}

    def rebind(self):
        # Explicitly revised synthetic reviews let independent semantic guards run.
        for entry in self.spec["evaluation"]:
            ref=entry["reservation"]; doc=json.loads((ROOT/ref["path"]).read_text())
            doc.update(source=entry["source"],membershipSHA256=digest(sorted(
                self.sources[entry["source"]["id"]],key=lambda r:r["id"])))
            entry["reservation"]=self.save(Path(ref["path"]).name,doc)

    def test_reservation_binding_rejects_changed_membership_and_source(self):
        self.complete(); entry=self.spec["evaluation"][0]
        ref=entry["reservation"]; original=json.loads((ROOT/ref["path"]).read_text())
        for change,reason in (({"version":"appearance-evaluation-reservation-v1"},"invalid_evaluation_reservation"),
                              ({"source":{"id":"another-source"}},"unbound_evaluation_reservation"),
                              ({"membershipSHA256":"0"*64},"unbound_evaluation_reservation")):
            entry["reservation"]=self.save("altered-reservation.json",{**original,**change})
            with self.assertRaisesRegex(FocusDataError,reason):e.assemble(self.spec)
        entry["reservation"]=ref
        self.sources[entry["source"]["id"]][0]["control"]="slider"
        with self.assertRaisesRegex(FocusDataError,"unbound_evaluation_reservation"):e.assemble(self.spec)
        self.rebind()
        self.assertFalse(e.assemble(self.spec)["readinessBlockers"])

    def test_reservation_reuse_and_membership_order(self):
        self.complete(); entry=self.spec["evaluation"][0]
        baseline=e.assemble(self.spec)
        self.sources[entry["source"]["id"]].reverse()
        self.assertEqual(e.assemble(self.spec),baseline)
        other=self.spec["evaluation"][1]
        doc=json.loads((ROOT/entry["reservation"]["path"]).read_text())
        # Even matching names and purpose do not bind another reviewed source.
        doc["family"]=other["source"]["id"]
        other["reservation"]=self.save("reused-reservation.json",doc)
        with self.assertRaisesRegex(FocusDataError,"unbound_evaluation_reservation"):e.assemble(self.spec)

    def build(self):
        doc=e.assemble(self.spec)
        path=self.root/"focus_dataset_manifest.json"; path.write_text(json.dumps(doc)); return path,doc

    def approval(self,doc,**change):
        ref=self.save("approval.json",{"version":"focus-appearance-approval-v1","approved":True,
            "protocolSHA256":doc["protocolSHA256"],"runName":self.root.name,"arm":"warm-stretch",
            "reviewer":"test-only","reviewReference":"not execution authority",**change})
        return ROOT/ref["path"]

    def test_complete_real_entrypoints_and_no_model_execution(self):
        self.complete(); spec=self.root/"input.json"; spec.write_text(json.dumps(self.spec)); out=self.root/"assembly"
        with patch.object(sys,"argv",["assembly","--input",str(spec),"--output",str(out)]),patch("builtins.print"):
            a.main()
        path=out/"focus_dataset_manifest.json"; doc=json.loads(path.read_text()); approval=self.approval(doc)
        from focus_learning_experiment import load_protocol
        report,rows=load_protocol(path,"warm-stretch",self.root.name,approval)
        self.assertTrue(report["launchEligible"]); self.assertFalse(report["executionAuthorized"])
        self.assertFalse(any(r["use"]=="final-challenge" for r in rows))
        self.assertEqual(set(report["sampling"]["weights"]),{r["id"] for r in rows if r["split"]=="train"})
        self.assertEqual(report["sampling"]["sourceMass"],{"fixture":.5,"native":.5})
        from train_focus_ring_detector import main
        args=["trainer","--name",self.root.name,"--experiment-protocol",str(path),"--experiment-arm","warm-stretch","--experiment-approval",str(approval)]
        before=set(self.root.rglob("*")); imported="torch" in sys.modules
        for suffix,expected in ((["--preflight"],0),(["--execute"],2),(["--dry-run","--epochs","2"],2)):
            with patch.object(sys,"argv",args+suffix),patch("builtins.print"): self.assertEqual(main(),expected)
        self.assertEqual(imported,"torch" in sys.modules); self.assertEqual(before,set(self.root.rglob("*")))
        with patch.object(sys,"argv",["assembly","--input",str(spec),"--output",str(out)]):
            with self.assertRaises(SystemExit) as ctx:a.main()
            self.assertEqual(ctx.exception.code,2)
        from focus_training_preflight import preflight
        self.assertIn("development_protocol_requires_explicit_experiment_mode",preflight(out,self.root.name)["blockers"])

    def test_missing_evaluation_and_selection_not_approval_bypass(self):
        path,doc=self.build()
        report,_=e.load_protocol(path,"warm-stretch",self.root.name,self.approval(doc))
        self.assertFalse(report["launchEligible"]); self.assertEqual(len(report["blockers"]),11)
        self.assertTrue(report["configurationValid"])

    def test_stale_approval_and_changed_weights(self):
        self.complete(); path,doc=self.build()
        for change in ({"approved":False},{"protocolSHA256":"wrong"},{"runName":"wrong"},{"arm":"scratch-stretch"}):
            self.assertFalse(e.load_protocol(path,"warm-stretch",self.root.name,self.approval(doc,**change))[0]["launchEligible"])
        self.assertFalse(e.load_protocol(path,"warm-stretch",self.root.name)[0]["launchEligible"])
        doc["sampling"]["weights"][next(iter(doc["sampling"]["weights"]))]=.9
        doc["protocolSHA256"]=digest({k:v for k,v in doc.items() if k!="protocolSHA256"}); path.write_text(json.dumps(doc))
        with self.assertRaisesRegex(FocusDataError,"changed_appearance_membership_or_weights"):e.load_protocol(path,"warm-stretch",self.root.name)

    def test_evaluation_reuse_pixels_and_transitive_family(self):
        self.complete(); key=self.spec["evaluation"][0]["source"]["id"]
        original=copy.deepcopy(self.sources[key]); self.sources[key][0]["priorUse"]="development"
        self.rebind()
        with self.assertRaisesRegex(FocusDataError,"reused_or_ineligible"):e.assemble(self.spec)
        self.sources[key]=copy.deepcopy(original); self.rebind(); self.visual.add(original[0]["frame"]["pixelSHA256"])
        with self.assertRaisesRegex(FocusDataError,"known_visual_evaluation_reuse"):e.assemble(self.spec)
        self.visual.clear(); self.sources[key][0]["frame"]=self.saved["samples"][0]["frame"]
        self.rebind()
        with self.assertRaisesRegex(FocusDataError,"cross_partition_lineage"):e.assemble(self.spec)
        self.sources[key]=copy.deepcopy(original)
        # One family edge plus a distinct original-lineage edge must join transitively.
        second=self.spec["evaluation"][1]; third=self.spec["evaluation"][-1]
        for r in self.sources[second["source"]["id"]]:r["relatedGroup"]=original[0]["relatedGroup"]
        family=second["source"]["id"]
        third["source"]["review"]=self.save("shared-family-review.json",{"independentFamily":family})
        third["reservation"]=self.save("shared-reservation.json",{"version":"appearance-evaluation-reservation-v2",
            "role":third["role"],"stratum":third["stratum"],"family":family,"previouslyUsed":False,"reviewer":"test","reviewReference":"synthetic"})
        self.rebind()
        with self.assertRaisesRegex(FocusDataError,"cross_partition_lineage"):e.assemble(self.spec)

    def test_duplicate_pair_conflict_and_cross_adapter_seed(self):
        extra=[self.row("addition",l,"simulatorFixture","development") for l in (0,1)]
        for r in extra:r.update(manifestVersion="1.5",recipeSeed=7)
        self.sources["addition"]=extra; self.spec["additions"]=[{"id":"addition"}]
        doc=e.assemble(self.spec)
        self.assertEqual(doc["sampling"]["sourceMass"],{"fixture":.5,"native":.5})
        for i in (0,1):extra[i]["crop"]=self.saved["samples"][2+i]["crop"]
        with self.assertRaisesRegex(FocusDataError,"duplicate_pair_disposition"):e.assemble(self.spec)
        extra[1]["crop"]=extra[0]["crop"]
        with self.assertRaisesRegex(FocusDataError,"contradictory_crop_labels"):e.assemble(self.spec)
        self.spec["additions"]=[]; self.complete()
        for r in self.saved["samples"][2:4]:r["recipeSeed"]=7
        key=self.spec["evaluation"][0]["source"]["id"]
        for r in self.sources[key]:r["recipeSeed"]=7
        self.rebind()
        with self.assertRaisesRegex(FocusDataError,"cross_partition_lineage"):e.assemble(self.spec)

    def test_selection_floor_reference_and_equal_source_scoring(self):
        self.complete(); self.spec["selection"]["nativeRetentionFloor"]=.8
        self.assertIn("retention_floor_differs_from_frozen_reference",e.assemble(self.spec)["readinessBlockers"])
        rows=[{"id":"n","label":1,"use":"retention-validation"}]+[{"id":str(i),"label":0,"use":"appearance-validation"} for i in range(10)]
        predictions=[{"id":r["id"],"label":r["label"],"probability":.8 if r["label"] else .1} for r in rows]
        metrics=e.selection_metrics(predictions,rows,{"threshold":.85,"nativeRetentionFloor":1.})
        self.assertFalse(metrics["checkpointEligible"])
        import math
        self.assertAlmostEqual(metrics["selectionLoss"],(-math.log(.8)-math.log(.9))/2)
        from train_focus_ring_detector import checkpoint_improved
        self.assertFalse(checkpoint_improved(.5,.5,e.CONFIG))
        predictions[0]["probability"]=float("nan")
        with self.assertRaisesRegex(FocusDataError,"invalid_validation"):e.selection_metrics(predictions,rows,self.spec["selection"])

    def test_invalid_version_output_and_changed_checkpoint(self):
        self.spec["version"]="future"
        with self.assertRaisesRegex(FocusDataError,"unsupported_appearance_input"):e.assemble(self.spec)
        self.spec["version"]=e.INPUT_VERSION; path,doc=self.build()
        with self.assertRaisesRegex(FocusDataError,"explicit_safe_run_name"):e.load_protocol(path,"warm-stretch","../escape")
        with self.assertRaisesRegex(FocusDataError,"unsupported_appearance_arm"):e.load_protocol(path,"scratch-stretch",self.root.name)
        (self.root/"warm.pt").write_bytes(b"changed")
        with self.assertRaisesRegex(FocusDataError,"changed_assembly_input"):e.assemble(self.spec)

    def test_missing_labels_stale_selection_and_old_selection_policy(self):
        saved=copy.deepcopy(self.saved)
        self.saved["samples"].pop(0)
        with self.assertRaisesRegex(FocusDataError,"incomplete_pair"):e.assemble(self.spec)
        self.saved=saved; self.complete()
        self.spec["selection"]["policy"]="minimum-native-validation-bce-earliest-tie"
        self.assertIn("unresolved_checkpoint_selection",e.assemble(self.spec)["readinessBlockers"])
        self.spec["selection"]["policy"]=e.SELECTION
        (ROOT/self.spec["selection"]["reference"]["path"]).write_text("{}")
        self.assertIn("changed_assembly_input",e.assemble(self.spec)["readinessBlockers"])

    def test_group_count_is_connected_components_not_declared_names(self):
        self.complete()
        for item in self.spec["evaluation"]:
            for row in self.sources[item["source"]["id"]]:row["relatedGroup"]=item["role"]
        self.rebind()
        doc=e.assemble(self.spec)
        self.assertEqual(sum(b.startswith("insufficient_independent_") for b in doc["readinessBlockers"]),10)

    def test_reconstruction_rejects_resealed_weights_before_protected_admission(self):
        ref=self.save("original.json",{})
        rebuilt={"version":"focus-appearance-proposal-v1","inputs":[ref]*3,"samples":[],"sampling":{"probabilities":{"test":1.}},"seconds":1.}
        changed=copy.deepcopy(rebuilt);changed["sampling"]["probabilities"]["test"]=.1
        changed["proposalSHA256"]=digest(changed)
        spec={"proposal":self.save("forged-proposal.json",changed)}
        with patch.object(e.legacy,"load",return_value={}),patch.object(e.proposal,"audit",return_value=rebuilt):
            with self.assertRaisesRegex(FocusDataError,"changed_proposal_membership_or_weights"):REAL_RECONSTRUCT(spec)


if __name__=="__main__":unittest.main()
