"""Deterministic integration tests; all approval/provenance records here are test-only."""
import base64
import copy
import io
import json
import sys
import unittest
from unittest.mock import patch
from PIL import Image

import focus_development_experiment as d
import focus_mixed_assembly as a
import focus_retained_review as review_tool
from focus_dataset_contract import ROOT, FocusDataError, digest, crop_frame, expanded_box
import test_direct_tvos_resume as receipt_fixture


class DevelopmentTests(unittest.TestCase):
    def save(self,name,doc):
        path=self.root/name; path.write_text(json.dumps(doc)); return a.reference(path)

    def reseal(self,ref,field,fn):
        doc=json.loads((ROOT/ref["path"]).read_text()); fn(doc)
        doc[field]=digest({k:v for k,v in doc.items() if k!=field})
        return self.save((ROOT/ref["path"]).name,doc)

    def setUp(self):
        self.f=receipt_fixture.ResumeTests(); self.f.setUp(); self.addCleanup(self.f.doCleanups); self.root=self.f.root
        def render(items,**kwargs):
            results=[]
            for item in items:
                with Image.open(item["path"]) as im: crop=crop_frame(im,expanded_box(item["bounds"],im.size))
                stream=io.BytesIO(); crop.save(stream,format="PNG")
                results.append({"id":item["id"],"png":base64.b64encode(stream.getvalue()).decode()})
            return {"results":results}
        for mod in (d,review_tool):
            p=patch.object(mod,"identity",return_value={"testOnly":True}); p.start(); self.addCleanup(p.stop)
            p=patch.object(mod,"invoke",side_effect=render); p.start(); self.addCleanup(p.stop)
        receipt=self.f.receipt("source",0,42,failed=True,actual_stop=1,genuine=True)
        # This genuine-shaped record is synthetic test data, never an actual admission.
        review=review_tool.review([receipt],self.root/"review")
        self.review=a.reference(self.root/"review/review.json")
        rows=[]
        for p in review["pairs"]:
            rows.append({**{k:p[k] for k in ("pairID","catalogIndex","family","theme","seed","edgeFlags")},
                         "disposition":"reviewed-development-candidate","visualReview":"both-production-crops-reviewed"})
        doc={"version":"focus-retained-dispositions-v1","reviewSHA256":review["reviewSHA256"],
             "reviewFileSHA256":self.review["sha256"],"trainingEligible":False,
             "counts":{"reviewed-development-candidate":2},"pairs":rows}
        doc["dispositionsSHA256"]=digest(doc)
        self.disposition=self.save("decisions.json",doc)
        baseline=self.root/"warm.pt"; baseline.write_bytes(b"test-only-never-deserialize")
        self.native_rows=[]
        for i,(scene,split) in enumerate(d.NATIVE_SPLITS.items()):
            for label in (0,1):
                path=self.root/f"native-{i}-{label}.png"
                Image.new("RGB",(256,256),(20+i,40+label,66)).save(path)
                ref=a.reference(path); rec=a.record(ROOT,ref)
                self.native_rows.append({"id":f"native{i}-{label}","sourceID":f"native{i}","pairID":f"p{i}",
                    "sourceKind":"tvos_simulator_os","scene":scene,"split":split,"label":label,
                    "priorUse":"development","sourceBlockers":["source_training_review_required"],
                    "crop":rec,"frame":rec,"bounds":[0,0,256,256],"relatedGroup":scene,"intrinsicGroup":scene,
                    "recipeSeed":None,"style":"unknown","control":"row"})
        self.native_spec={"version":"focus-assembly-input-v1","sources":[],"baseline":a.reference(baseline)}
        self.spec={"version":d.INPUT_VERSION,"nativeInput":self.save("native.json",self.native_spec),
                   "baseline":a.reference(baseline),"retainedReview":self.review,"dispositions":self.disposition,
                   "excludedDialogManifest":self.save("excluded.json",{"version":"1.4","sourceKind":"tvos_native_generator"})}
        original=a.assemble
        p=patch.object(a,"assemble",side_effect=lambda spec: {"samples":copy.deepcopy(self.native_rows)}
                       if spec==self.native_spec else original(spec))
        p.start(); self.addCleanup(p.stop)

    def build(self):
        doc=d.assemble(self.spec)
        out=self.root/"assembled"; out.mkdir(exist_ok=True)
        path=out/"focus_dataset_manifest.json"; path.write_text(json.dumps(doc))
        return path,doc

    def approval(self,doc,**overrides):
        ref=self.save("approval.json",{"version":"focus-development-approval-v1","approved":True,
            "protocolSHA256":doc["protocolSHA256"],"runName":self.root.name,"arm":"warm-stretch",
            "reviewer":"test-only","reviewReference":"synthetic test; no execution permission",**overrides})
        return ROOT/ref["path"]

    def test_build_load_approval_and_production_rejection(self):
        path,doc=self.build(); self.assertEqual(d.load(path),doc)
        report,rows=d.load_protocol(path,"warm-stretch",self.root.name)
        self.assertTrue(report["configurationValid"]); self.assertFalse(report["launchEligible"])
        report,rows=d.load_protocol(path,"warm-stretch",self.root.name,self.approval(doc))
        self.assertTrue(report["launchEligible"]); self.assertFalse(report["executionAuthorized"])
        self.assertEqual(len(rows),12); self.assertEqual(report["counts"],{"train":5,"validation":1})
        self.assertEqual(set(report["sampling"]["weights"]),{r["id"] for r in rows if r["split"]=="train"})
        from focus_training_preflight import preflight
        production=preflight(path.parent,self.root.name)
        self.assertFalse(production["launchEligible"])
        self.assertIn("development_protocol_requires_explicit_experiment_mode",production["blockers"])

    def test_real_assembly_and_trainer_entrypoints_no_model_import_or_run(self):
        spec=self.root/"spec.json"; spec.write_text(json.dumps(self.spec)); out=self.root/"cli"
        with patch.object(sys,"argv",["assembly","--input",str(spec),"--output",str(out)]),patch("builtins.print"):
            a.main()
        doc=json.loads((out/"focus_dataset_manifest.json").read_text()); approval=self.approval(doc)
        from train_focus_ring_detector import main
        args=["trainer","--name",self.root.name,"--experiment-protocol",str(out/"focus_dataset_manifest.json"),
              "--experiment-arm","warm-stretch","--dry-run"]
        before=set(self.root.rglob("*")); imported="torch" in sys.modules
        with patch.object(sys,"argv",args),patch("builtins.print"): self.assertEqual(main(),2)
        with patch.object(sys,"argv",args+["--experiment-approval",str(approval)]),patch("builtins.print"):
            self.assertEqual(main(),0)
        self.assertEqual(imported,"torch" in sys.modules); self.assertEqual(before,set(self.root.rglob("*")))
        self.assertFalse((ROOT/"NativeUITrainer/focus_ring_runs"/self.root.name).exists())
        with patch.object(sys,"argv",["assembly","--input",str(spec),"--output",str(out)]):
            with self.assertRaises(SystemExit) as e: a.main()
            self.assertEqual(e.exception.code,2)

    def test_stale_approval_arm_and_run(self):
        path,doc=self.build()
        for change in ({"approved":False},{"protocolSHA256":"stale"},{"runName":"other"},{"arm":"scratch-stretch"},{"reviewer":""}):
            self.assertFalse(d.load_protocol(path,"warm-stretch",self.root.name,self.approval(doc,**change))[0]["launchEligible"])
        with self.assertRaisesRegex(FocusDataError,"unsupported_development_arm"): d.load_protocol(path,"scratch-stretch",self.root.name)
        with self.assertRaises(FocusDataError): d.load_protocol(path,"warm-stretch","../escape")

    def test_source_and_disposition_binding(self):
        spec=copy.deepcopy(self.spec); spec["retainedReview"]["sha256"]="0"*64
        with self.assertRaisesRegex(FocusDataError,"changed_assembly_input"): d.assemble(spec)
        self.spec["dispositions"]=self.reseal(self.disposition,"dispositionsSHA256",lambda x:x["pairs"][0].update(disposition="excluded-first-experiment"))
        with self.assertRaisesRegex(FocusDataError,"unreviewed_pair"): d.assemble(self.spec)

    def test_prediction_geometry_and_crop_tampering(self):
        old=(ROOT/self.review["path"]).read_text()
        for field,value in (("labelSource","modelPrediction"),("control","invented")):
            (ROOT/self.review["path"]).write_text(old)
            self.spec["retainedReview"]=self.reseal(self.review,"reviewSHA256",lambda x:x["pairs"][0].update({field:value}))
            self.bind_new_review()
            with self.assertRaisesRegex(FocusDataError,"changed_retained_label"): d.assemble(self.spec)
        (ROOT/self.review["path"]).write_text(old); self.spec["retainedReview"]=self.review; self.bind_new_review()
        doc=json.loads(old); crop=ROOT/doc["pairs"][0]["focused"]["cropPath"]; crop.write_bytes(b"corrupt")
        with self.assertRaises(FocusDataError): d.assemble(self.spec)

    def bind_new_review(self):
        ref=self.spec["retainedReview"]; doc=json.loads((ROOT/ref["path"]).read_text())
        self.spec["dispositions"]=self.reseal(self.spec["dispositions"],"dispositionsSHA256",
            lambda x:x.update(reviewSHA256=doc["reviewSHA256"],reviewFileSHA256=ref["sha256"]))

    def test_native_role_conflict_and_cross_source_leakage(self):
        self.native_rows[-1]["split"]="train"
        with self.assertRaisesRegex(FocusDataError,"native_role_or_review_conflict"): d.assemble(self.spec)
        self.native_rows[-1]["split"]="validation"
        fixture=d.retained_rows(self.review,self.disposition)[0]
        self.native_rows[-1]["crop"]=fixture["crop"]; self.native_rows[-1]["label"]=fixture["label"]
        with self.assertRaisesRegex(FocusDataError,"cross_source_split_leakage"): d.assemble(self.spec)

    def test_resigned_protocol_membership_and_unsupported_version(self):
        path,doc=self.build(); doc["samples"][0]["split"]="test"
        doc["protocolSHA256"]=digest({k:v for k,v in doc.items() if k!="protocolSHA256"}); path.write_text(json.dumps(doc))
        with self.assertRaisesRegex(FocusDataError,"changed_experiment_membership"): d.load(path)
        doc["version"]="future"; path.write_text(json.dumps(doc))
        with self.assertRaisesRegex(FocusDataError,"unsupported_development_input"): d.load(path)

    def test_no_approval_execution_and_checkpoint_tie(self):
        path,doc=self.build()
        from train_focus_ring_detector import main,checkpoint_improved
        self.assertFalse(checkpoint_improved(.5,.5,d.CONFIG))
        self.assertTrue(checkpoint_improved(.4,.5,d.CONFIG))
        self.assertTrue(checkpoint_improved(.5,.5,{}))  # preserve previous protocols
        args=["trainer","--name",self.root.name,"--experiment-protocol",str(path),
              "--experiment-arm","warm-stretch","--execute"]
        imported="torch" in sys.modules
        with patch.object(sys,"argv",args),patch("builtins.print"): self.assertEqual(main(),2)
        with patch.object(sys,"argv",args+["--experiment-approval",str(self.approval(doc))]),patch("builtins.print"):
            self.assertEqual(main(),2)  # approval alone cannot bypass logged-run binding
        self.assertEqual(imported,"torch" in sys.modules)
        self.assertFalse((ROOT/"NativeUITrainer/focus_ring_runs"/self.root.name).exists())

    def test_test_only_partial_and_geometry_rejection(self):
        review=json.loads((ROOT/self.review["path"]).read_text()); receipt=ROOT/review["sources"][0]["path"]
        original=receipt.read_text(); doc=json.loads(original); doc["evidenceKind"]="test-only"; receipt.write_text(json.dumps(doc))
        self.spec["retainedReview"]=self.reseal(self.review,"reviewSHA256",
            lambda r:r["sources"][0].update(sha256=a.reference(receipt)["sha256"]))
        self.bind_new_review()
        with self.assertRaisesRegex(FocusDataError,"test_only_evidence"): d.assemble(self.spec)
        receipt.write_text(original)
        self.spec["retainedReview"]=self.reseal(self.spec["retainedReview"],"reviewSHA256",
            lambda r:r["sources"][0].update(sha256=a.reference(receipt)["sha256"]))
        self.bind_new_review()
        self.spec["retainedReview"]=self.reseal(self.spec["retainedReview"],"reviewSHA256",
            lambda r:r["pairs"][0]["focused"]["bounds"].__setitem__(0,99))
        self.bind_new_review()
        with self.assertRaisesRegex(FocusDataError,"changed_retained_geometry_or_label"): d.assemble(self.spec)


if __name__=="__main__": unittest.main()
