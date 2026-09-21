"""Real crop/CLI integration and deterministic planning; all generated evidence test-only."""
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageChops, ImageStat

from focus_dataset_contract import ROOT, digest, validate_manifest, FocusDataError
from focus_runtime import render, recrop, identity, invoke
from focus_capture_plan import compile_plan, reconcile, PlanError
from focus_ring_baseline import prepare_protocol, score_protocol, evaluate
import test_focus_consumer_integration as fixture_module


def catalog():
    families = {"grid_matrix":20, "media_shelf":15, "settings_list":10,
                "action_dialog":5, "hero_carousel":5, "focus_maze":5}
    recipes=[]
    for seed in range(100,200):
        for family,n in families.items():
            for theme in ("light","dark","high_contrast"):
                recipes.append({"recipe":{"schema_version":1,"archetype":family,"element_count":n,
                                  "theme":theme,"density":"regular","seed":seed,"step_index":0},
                                "expectedTargets":[{"id":f"test-only-{i}","type":"imageView" if i%2 else "collectionItem"} for i in range(n)]})
    return {"version":"focus-recipe-catalog-v1","producerReference":"test-only-not-wire-compatible",
            "reviewReference":"unit-test-only","evidenceKind":"test-only","developmentSeeds":[7,1042],
            "seedGroups":{str(seed):f"family-group-{seed}" for seed in range(100,200)},"recipes":recipes}


class PlanTests(unittest.TestCase):
    def test_full_quota_plan_deterministic_and_grouped(self):
        c=catalog(); p=compile_plan(c)
        self.assertEqual(p["groupCounts"],{"train":80,"validation":10,"test":10})
        self.assertFalse(p["plannedCoverage"]["gaps"])
        self.assertEqual(p,compile_plan(c))
        self.assertTrue(all(len(b["recipeIDs"])<=100 for b in p["batches"]))
        groups={}
        for row in p["recipes"]: groups.setdefault(row["group"],set()).add(row["split"])
        self.assertTrue(all(len(s)==1 for s in groups.values()))
        self.assertFalse(p["trainingEligible"])

    def test_reject_development_unknown_limits_and_duplicates(self):
        for mutate in (lambda c:c["recipes"][0]["recipe"].update(seed=7),
                       lambda c:c["recipes"][0]["recipe"].update(theme="system"),
                       lambda c:c["recipes"][0]["recipe"].update(element_count=999),
                       lambda c:c["recipes"].append(copy.deepcopy(c["recipes"][0]))):
            c=catalog(); mutate(c)
            with self.assertRaises((PlanError,ValueError)): compile_plan(c)

    def test_related_seed_variants_share_one_partition_and_batch(self):
        c=catalog()
        c["seedGroups"]={str(s):f"group-{s//2}" for s in range(100,200)}
        p=compile_plan(c)
        self.assertEqual(p["groupCounts"],{"train":40,"validation":5,"test":5})
        batch_for={rid:b["id"] for b in p["batches"] for rid in b["recipeIDs"]}
        for group in {r["group"] for r in p["recipes"]}:
            members=[r for r in p["recipes"] if r["group"]==group]
            self.assertEqual(len({batch_for[r["id"]] for r in members}),1)
            self.assertEqual(len({r["split"] for r in members}),1)
        c["developmentGroups"]=["group-50"]
        with self.assertRaisesRegex(PlanError,"development_group"): compile_plan(c)

    def test_fixed_control_templates_do_not_assume_element_count_is_target_count(self):
        c=catalog()
        for entry in c["recipes"]:
            if entry["recipe"]["archetype"]=="hero_carousel":
                entry["recipe"]["element_count"]=1
                entry["expectedTargets"]=entry["expectedTargets"][:2]
        p=compile_plan(c)
        self.assertTrue(all(len(r["targets"])==2 for r in p["recipes"] if r["family"]=="heroCarousel"))

    def test_resume_and_actual_accounting(self):
        p=compile_plan(catalog()); ledger={"version":"focus-capture-ledger-v1","planSHA256":p["planSHA256"],"attempts":[]}
        self.assertEqual(reconcile(p,ledger)["resumeBatches"],p["batches"])
        b=p["batches"][0]
        ledger["attempts"]=[{"batchID":b["id"],"state":"failed","cleanup":"unknown"}]
        self.assertFalse(reconcile(p,ledger)["resumeBatches"])
        self.assertEqual(len(reconcile(p,ledger)["blockedBatches"]),1)
        rows={r["id"]:r for r in p["recipes"]}
        attempt={"batchID":b["id"],"state":"completed","cleanup":"clear","receiptSHA256":"a"*64,
                 "recipes":[{"recipeID":rid,"split":rows[rid]["split"],"acceptedPairs":[],
                             "rejectedTargetIDs":[t["id"] for t in rows[rid]["targets"]]} for rid in b["recipeIDs"]]}
        ledger["attempts"]=[attempt]; result=reconcile(p,ledger)
        self.assertEqual(result["acceptedCoverage"]["pairs"],0)
        self.assertTrue(result["acceptedCoverage"]["gaps"])
        self.assertEqual(len(result["resumeBatches"]),len(p["batches"])-1)
        attempt["recipes"][0]["split"]="wrong"
        with self.assertRaisesRegex(PlanError,"split_drift"): reconcile(p,ledger)
        ledger["planSHA256"]="changed"
        with self.assertRaisesRegex(PlanError,"incompatible"): reconcile(p,ledger)

    def test_cli_freeze_and_no_overwrite(self):
        root=ROOT/".build/debug-output/focus-launch"; root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            path=Path(tmp); (path/"catalog.json").write_text(json.dumps(catalog()))
            cmd=[sys.executable,str(ROOT/"scripts/focus_capture_plan.py"),"--catalog",str(path/"catalog.json"),"--output",str(path/"plan.json")]
            r=subprocess.run(cmd,capture_output=True,text=True); self.assertEqual(r.returncode,0,r.stderr)
            r=subprocess.run(cmd,capture_output=True,text=True); self.assertEqual(r.returncode,2)

    def test_accepted_ledger_rejects_duplicate_bytes_and_incomplete_accounting(self):
        p=compile_plan(catalog()); rows={r["id"]:r for r in p["recipes"]}
        def attempt(batch):
            members=[]
            for rid in batch["recipeIDs"]:
                row=rows[rid]; target=row["targets"][0]["id"]
                members.append({"recipeID":rid,"split":row["split"],
                    "acceptedPairs":[{"pairID":rid,"targetID":target,"labelSource":"fixtureCallback",
                        "unfocusedVerified":True,"focusedSHA256":digest([rid,1]),"unfocusedSHA256":digest([rid,0])}],
                    "rejectedTargetIDs":[t["id"] for t in row["targets"][1:]]})
            return {"batchID":batch["id"],"state":"completed","cleanup":"clear","receiptSHA256":"a"*64,"recipes":members}
        ledger={"version":"focus-capture-ledger-v1","planSHA256":p["planSHA256"],"attempts":[attempt(b) for b in p["batches"]]}
        self.assertEqual(reconcile(p,ledger)["acceptedCoverage"]["pairs"],len(p["recipes"]))
        original=copy.deepcopy(ledger)
        ledger["attempts"][0]["recipes"][0]["rejectedTargetIDs"].pop()
        with self.assertRaisesRegex(PlanError,"target_accounting"): reconcile(p,ledger)
        ledger=copy.deepcopy(original)
        members=[m for a in ledger["attempts"] for m in a["recipes"]]
        first=members[0]
        other=next(m for m in members if m["split"]!=first["split"])
        other["acceptedPairs"][0]["focusedSHA256"]=first["acceptedPairs"][0]["focusedSHA256"]
        with self.assertRaisesRegex(PlanError,"content_split_leakage"): reconcile(p,ledger)
        ledger=copy.deepcopy(original)
        members=ledger["attempts"][0]["recipes"]
        a=members[0]["acceptedPairs"][0]
        b=next(m["acceptedPairs"][0] for m in members[1:] if m["acceptedPairs"][0]["targetID"]==a["targetID"])
        b.update(focusedSHA256=a["focusedSHA256"],unfocusedSHA256=a["unfocusedSHA256"])
        with self.assertRaisesRegex(PlanError,"duplicate_pair_content"): reconcile(p,ledger)
        p["batches"][0]["timeoutSeconds"]=999
        with self.assertRaisesRegex(PlanError,"changed_plan"): reconcile(p,original)

    def test_abstentions_are_separate_from_binary_errors_in_each_slice(self):
        samples=[{"id":str(i),"label":i%2,"family":"grid","theme":"light","control":"imageView","hard":i%2==0} for i in range(4)]
        result=evaluate(samples,{"0":.1,"1":.9,"2":.75,"3":.8})
        for group in result["groups"].values():
            self.assertEqual(group["abstained"],2)
            self.assertEqual(group["decisionCoverage"],.5)
            self.assertEqual(group["selectiveAccuracy"],1)


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        # Reuse the prior real-byte fixture factory, not its test cases.
        self.fixture=fixture_module.ConsumerTests(); self.fixture.setUp()
        self.root=self.fixture.root
    def tearDown(self): self.fixture.tearDown()

    def test_production_recrop_parity_and_legacy_difference(self):
        f=self.fixture
        legacy=Image.open(f.data/f.doc["pairs"][0]["focused_crop"]).convert("RGB")
        first=render(f.doc); second=render(f.doc)
        for key in first: self.assertEqual(first[key][1].tobytes(),second[key][1].tobytes())
        delta=ImageStat.Stat(ImageChops.difference(legacy,first["a:1"][1]))
        self.assertGreater(sum(delta.mean),0)  # Do not declare Pillow equivalent.
        output=self.root/"runtime"; doc=recrop(f.doc,f.data,output)
        self.assertEqual(len(validate_manifest(doc,output)),1)
        self.assertEqual(doc["version"],"1.3")
        self.assertNotIn("trainingApproval",doc)
        with self.assertRaisesRegex(FocusDataError,"collision"): recrop(f.doc,f.data,output)
        doc["runtimeCrop"]["helperSHA256"]="changed"
        with self.assertRaisesRegex(FocusDataError,"implementation_changed"): validate_manifest(doc,output)

    def test_pixel_orientation_fractional_scaling_clipping_and_tiny_boxes(self):
        f=self.fixture
        image=Image.new("RGB",(100,80)); image.putdata([(x*2,y*3,0) for y in range(80) for x in range(100)])
        path=f.raw/"gradient.png"; image.save(path)
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        boxes=[[10,5,20,10],[10.5,5.5,20,10],[0,0,10,10],[90,70,10,10],[1,1,1,1],[8,3,24,14]]
        import base64,io
        from focus_dataset_contract import crop_frame,expanded_box
        evidence=[]
        reply=invoke([{"id":str(i),"path":str(path),"sha256":sha,"bounds":b} for i,b in enumerate(boxes)])
        for b,row in zip(boxes,reply["results"]):
            actual=Image.open(io.BytesIO(base64.b64decode(row["png"]))).convert("RGB")
            expected=crop_frame(image,expanded_box(b,image.size))
            delta=ImageStat.Stat(ImageChops.difference(actual,expected))
            # Smooth opaque gradient diagnoses orientation/location independently
            # of interpolation kernels. Not a universal pixel-parity threshold.
            self.assertLess(max(delta.mean),4,(b,delta.mean))
            self.assertLessEqual(actual.getpixel((128,0))[1],actual.getpixel((128,255))[1])
            evidence.append({"bounds":b,"legacyMeanAbsoluteChannelDifference":delta.mean})
        (ROOT/".build/debug-output/focus-launch/crop-parity.json").write_text(json.dumps({"testOnly":True,"cases":evidence,"runtime":identity()},indent=2))

    def test_actual_coreml_baseline_cli_test_only(self):
        f=self.fixture; out=self.root/"runtime"; doc=recrop(f.doc,f.data,out)
        model=ROOT/"NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc"
        args=["--manifest",out/"focus_dataset_manifest.json","--model",model]
        protocol=self.root/"protocol.json"; report=self.root/"report.json"
        r=f.cli("focus_ring_baseline.py",*args,"--prepare","--output",protocol)
        self.assertEqual(r.returncode,0,r.stderr)
        r=f.cli("focus_ring_baseline.py",*args,"--infer","--protocol",protocol,"--output",report)
        self.assertEqual(r.returncode,0,r.stderr)
        result=json.loads(report.read_text())
        self.assertEqual(result["evidenceKind"],"test-only")
        self.assertEqual(result["modelGatePassed"],"not_assessed")
        self.assertEqual(result["evaluation"]["groups"]["overall"]["n"],2)
        self.assertEqual(result["warmLatencyMs"]["n"],1)
        self.assertEqual(sum(result["decisions"][k] for k in ("focused","unfocused","abstained")),2)
        # Keep only explicit test-only evidence for the handoff; not genuine performance.
        evidence=ROOT/".build/debug-output/focus-launch/inference-test-report.json"
        evidence.write_text(json.dumps(result,indent=2))

    def test_runtime_rejects_changed_bytes_geometry_and_duplicates(self):
        f=self.fixture; p=f.doc["pairs"][0]; frame=p["frames"]["focused"]
        item={"id":"a","path":str(f.raw/frame["path"]),"sha256":frame["sha256"],"bounds":frame["bounds"]}
        for bad in ({**item,"sha256":"0"*64},{**item,"bounds":[-1,0,10,10]}):
            with self.assertRaisesRegex(FocusDataError,"runtime_failed"): invoke([bad])
        with self.assertRaisesRegex(FocusDataError,"runtime_failed"): invoke([item,item])

    def test_runtime_preflight_approval_and_no_output_side_effect(self):
        from focus_training_preflight import preflight
        f=self.fixture
        f.doc["pairs"][0]["split"]="train"
        f.add_pair("v","validation",2); f.add_pair("t","test",3)
        out=self.root/"runtime"; doc=recrop(f.doc,f.data,out)
        doc["evidenceKind"]="reviewed-fixture"
        doc["trainingApproval"]={"approved":True,"reviewReference":"test-only-mocked-quota-check",
                                 "membershipSHA256":digest(doc["pairs"])}
        (out/"focus_dataset_manifest.json").write_text(json.dumps(doc))
        before=set(self.root.rglob("*"))
        with patch("focus_training_preflight.validate",return_value={}):
            report=preflight(out,self.root.name)
        self.assertTrue(report["launchEligible"],report)
        self.assertFalse(report["executionAuthorized"])
        self.assertEqual(before,set(self.root.rglob("*")))
        self.assertFalse((ROOT/report["output"]).exists())

    def test_forged_runtime_crop_rejected(self):
        f=self.fixture; out=self.root/"runtime"; doc=recrop(f.doc,f.data,out)
        p=doc["pairs"][0]; crop=out/p["focused_crop"]
        Image.new("RGB",(256,256),"red").save(crop)
        p["focused_crop_sha256"]=hashlib.sha256(crop.read_bytes()).hexdigest()
        with self.assertRaisesRegex(FocusDataError,"crop_pixel_mismatch"): validate_manifest(doc,out)

if __name__=="__main__": unittest.main()
