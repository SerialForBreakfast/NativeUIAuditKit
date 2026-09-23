"""Real consumer/CLI/crop checks against source-shaped, explicitly test-only v2."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from PIL import Image
from focus_dataset_contract import ROOT, FocusDataError, validate_manifest
from harvest_bundle_validation import validate_bundle, HarvestValidationError
from harvest_sidecar_v2 import recipe_hash
from simulator_focus_manifest import build
from ttr_focus_manifest import derive


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scene(focused, generation):
    # Focus changes actual measured geometry; reusing focused boxes for the
    # baseline must be observable in the consumer test.
    bounds = [12, 8, 28, 20] if focused else [14, 10, 24, 16]
    x, y, w, h = bounds
    recipe = {"schema_version": 1, "archetype": "action_dialog", "element_count": 2,
              "theme": "high_contrast", "density": "regular", "seed": 7, "step_index": 0}
    recipe["recipe_hash"] = recipe_hash(recipe)
    return {"scene_width": 64, "scene_height": 48, "is_settled": True,
            "focused_element_id": focused, "harvest_challenge_active": False, "recipe": recipe,
            "elements": [{"element_id": "e", "taxonomy_class": "collectionItem", "is_focused": bool(focused),
                          "pixel_bounds": bounds, "normalized_bounds": [x/64,y/48,(x+w)/64,(y+h)/48]}],
            "focus_observation": {"generation": generation, "requestedID": focused, "observedID": focused,
                                  "verified": True, "source": "uikit_focus_system",
                                  "geometrySource": "uikit_window_converted_bounds", "plannedFocusIDs": ["e"]},
            "observation_diagnostics": {"sampleCount": 8, "sampleAgeMilliseconds": 20,
                "generation": generation, "sampledGeneration": generation, "nativeFocusResolved": True,
                "requestedID": focused, "observedID": focused, "requiredIDs": ["e"], "measuredIDs": ["e"],
                "missingIDs": [], "stableMilliseconds": 200, "requiredMilliseconds": 150, "reason": "ready",
                "nativeProbe": {"referenceAttached": True, "referenceFocused": focused is None,
                                "exclusionReasons": {}}}}


def write_bundle(root):
    root.mkdir()
    for name, color in (("u.png", (40,70,90)), ("f.png", (150,180,220))):
        im = Image.new("RGB", (64,48), color)
        im.putpixel((15,12), (255,0,0))
        im.save(root/name)
    baseline, focused = scene(None, 4), scene("e", 5)
    def capture(s, name, base):
        return {"before_scene": copy.deepcopy(s), "after_scene": copy.deepcopy(s),
                "before_scene_received_host_ns": base, "frame_received_host_ns": base+1,
                "after_scene_received_host_ns": base+2, "frame_png_sha256": sha(root/name),
                "frame_width": 64, "frame_height": 48, "correlation": "validated_capture_bracket"}
    meta = {**copy.deepcopy(focused), "schema_version": 2, "id": "test-only-pair", "unfocused_png": "u.png",
            "focused_png": "f.png", "unfocused_sha256": sha(root/"u.png"), "focused_sha256": sha(root/"f.png"),
            "bounds_semantics": "measured_view_bounds; not_focus_effect_segmentation", "layout_exclusions": {},
            "baseline_scene": baseline, "focused_scene": focused,
            "reference_capture": capture(baseline,"u.png",100), "focused_capture": capture(focused,"f.png",200)}
    (root/"m.json").write_text(json.dumps(meta))
    row = {"id": "test-only-pair", "path": "f.png", "sha256": sha(root/"f.png"), "expectedFocus": "e",
           "box": focused["elements"][0]["pixel_bounds"], "split": "calibration",
           "metadata": {"unfocusedPath":"u.png", "focusedPath":"f.png", "metadataPath":"m.json"}}
    for name, rows in (("manifest",[row]),("training",[]),("calibration",[row]),("held-out",[])):
        (root/(name+".json")).write_text(json.dumps(rows))
    (root/"harvest-receipt.json").write_text(json.dumps({"schemaVersion":1,"outcome":"completed","acceptedRowCount":1}))
    reindex(root)
    return meta


def reindex(root):
    artifacts = [{"path":p.name,"sha256":sha(p),"byteCount":p.stat().st_size} for p in sorted(root.iterdir())
                 if p.name not in {"dataset-index.json","harvest-receipt.json"}]
    index = {"datasetLayoutVersion":1,"telemetryContract":"harvest-canonical-v1; source-version-unverified",
             "producer":"TVTestRig","producerBuild":"test-only","provenance":"unverified-pixel-telemetry-binding",
             "normalizedCoordinates":"xyxy-top-left-unit","pixelCoordinates":"xywh-top-left-pixels","artifacts":artifacts}
    (root/"dataset-index.json").write_text(json.dumps(index))


class V2Tests(unittest.TestCase):
    def setUp(self):
        (ROOT/".build/debug-output").mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(dir=ROOT/".build/debug-output",prefix="v2-test-"))
        self.bundle=self.root/"bundle"
        self.meta=write_bundle(self.bundle)

    def tearDown(self):
        shutil.rmtree(self.root)

    def mutate(self, action):
        m=copy.deepcopy(self.meta); action(m)
        (self.bundle/"m.json").write_text(json.dumps(m)); reindex(self.bundle)

    def cli(self, script, *args):
        return subprocess.run([sys.executable,str(ROOT/"scripts"/script),*map(str,args)],capture_output=True,text=True,
                              timeout=120,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})

    def test_valid_contract_preserves_brackets_and_legacy_provenance(self):
        result=validate_bundle(self.bundle)
        row=result["usableRows"][0]
        self.assertEqual(row["sidecarVersion"],2)
        self.assertIsNone(row["identityEvidence"])
        self.assertFalse(row["eligibleForTraining"])
        p=build(result,"test-only","46dce7b",None)["pairs"][0]
        self.assertEqual(p["observationBinding"]["baselineScene"],self.meta["baseline_scene"])
        self.assertEqual(p["annotation"]["sha256"],sha(self.bundle/"m.json"))

    def test_unsupported_versions(self):
        for version in (1,3,None,"2",2.0,True):
            with self.subTest(version=version):
                self.mutate(lambda m:m.update(schema_version=version))
                with self.assertRaisesRegex(HarvestValidationError,"unsupported_version"): validate_bundle(self.bundle)

    def test_bracket_negative_matrix(self):
        cases = {
            "missing": lambda m:m.pop("reference_capture"),
            "before": lambda m:m["focused_capture"].pop("before_scene"),
            "hash": lambda m:m["focused_capture"].update(frame_png_sha256="0"*64),
            "dimensions": lambda m:m["focused_capture"].update(frame_width=32),
            "order": lambda m:m["focused_capture"].update(frame_received_host_ns=1),
            "clock": lambda m:m["focused_capture"].update(frame_received_host_ns=True),
            "pair_clock": lambda m:m["reference_capture"].update(before_scene_received_host_ns=400,frame_received_host_ns=401,after_scene_received_host_ns=402),
            "correlation": lambda m:m["focused_capture"].update(correlation="atomic"),
            "flat": lambda m:m.update(activeFocusId="wrong"),
            "excluded": lambda m:m.update(layout_exclusions={"e":"clipped"}),
            "recipe": lambda m:m["recipe"].update(theme="light"),
            "bounds": lambda m:m["focused_capture"]["before_scene"]["elements"][0].update(normalized_bounds=[0,0,1,1]),
            "stale": lambda m:m["reference_capture"]["before_scene"]["observation_diagnostics"].update(sampleAgeMilliseconds=1000),
            "nan": lambda m:m["reference_capture"]["before_scene"]["observation_diagnostics"].update(stableMilliseconds=float("nan")),
            "unsettled": lambda m:m["reference_capture"]["before_scene"].update(is_settled=False),
            "reference": lambda m:m["reference_capture"]["before_scene"]["observation_diagnostics"]["nativeProbe"].update(referenceFocused=False),
            "prediction": lambda m:m["focused_capture"]["before_scene"]["focus_observation"].update(source="modelPrediction"),
            "generation": lambda m:m["focused_capture"]["before_scene"]["focus_observation"].update(generation=99),
            "missing_labels": lambda m:m["reference_capture"]["before_scene"].update(elements=[]),
        }
        for name, action in cases.items():
            with self.subTest(name=name):
                self.mutate(action)
                with self.assertRaises(HarvestValidationError): validate_bundle(self.bundle)

    def test_changing_diagnostic_counters_does_not_require_scene_equality(self):
        self.mutate(lambda m:m["focused_capture"]["before_scene"]["observation_diagnostics"].update(sampleCount=7,sampleAgeMilliseconds=10))
        self.assertEqual(validate_bundle(self.bundle)["integrity"],"pass")

    def test_existing_manifest_and_crop_cli_plus_baseline_preflight(self):
        from focus_training_preflight import preflight
        from focus_ring_baseline import prepare_protocol
        manifest=self.root/"intake.json"
        r=self.cli("build_simulator_focus_manifest.py","--bundle",self.bundle,"--corpus-id","test-only","--producer-reference","46dce7b","--output",manifest)
        self.assertEqual(r.returncode,0,r.stderr)
        output=self.root/"crops"
        args=("--fixture-bundle",self.bundle,"--corpus-id","test-only","--producer-reference","46dce7b",
              "--output",output,"--ttr-sidecar-v2","--test-only")
        r=self.cli("harvest_focus_pairs.py",*args,"--dry-run")
        self.assertEqual(r.returncode,0,r.stdout+r.stderr); self.assertFalse(output.exists())
        r=self.cli("harvest_focus_pairs.py",*args)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        doc=json.loads((output/"focus_dataset_manifest.json").read_text())
        self.assertEqual(len(validate_manifest(doc,output)),1)
        p=doc["pairs"][0]
        self.assertNotEqual(p["frames"]["focused"]["bounds"],p["frames"]["unfocused"]["bounds"])
        self.assertNotIn("frameID",p["frames"]["focused"])
        self.assertEqual(doc["evidenceKind"],"test-only")
        self.assertFalse(preflight(output,"v2-offline-only")["launchEligible"])
        self.assertNotEqual(self.cli("harvest_focus_pairs.py",*args).returncode,0)
        model=ROOT/"NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc"
        protocol=prepare_protocol(doc,output,model)
        self.assertEqual(protocol["cropParity"]["backend"],"production-makeCrop")
        self.assertEqual(protocol["modelGatePassed"],"not_assessed")
        for mutate in (lambda d:d["pairs"][0].update(split="test"),
                       lambda d:d["pairs"][0]["frames"]["focused"].update(bounds=[0,0,1,1]),
                       lambda d:d.update(evidenceKind="reviewed-fixture"),
                       lambda d:d.update(observedSource={"assurance":"attested"}),
                       lambda d:d.update(trainingApproval={"approved":True})):
            bad=copy.deepcopy(doc); mutate(bad)
            with self.assertRaises(FocusDataError): validate_manifest(bad,output)
        (self.bundle/"f.png").write_bytes(b"bad")
        with self.assertRaises(ValueError): validate_manifest(doc,output)

    def test_legacy_not_upgraded_and_partial_not_admitted(self):
        self.mutate(lambda m:m.pop("schema_version"))
        self.assertIsNone(validate_bundle(self.bundle)["usableRows"][0]["observationBinding"])
        with self.assertRaisesRegex(FocusDataError,"v2_brackets_required"):
            derive(self.bundle,self.root/"out","test-only","46dce7b",test_only=True)
        receipt=self.bundle/"harvest-receipt.json"
        receipt.write_text(json.dumps({"schemaVersion":1,"outcome":"aborted","acceptedRowCount":1}))
        with self.assertRaisesRegex(HarvestValidationError,"incomplete_run"): validate_bundle(self.bundle)

    def test_review_is_bound_to_bundle_and_report(self):
        from ttr_focus_manifest import bundle_identity
        from focus_dataset_contract import digest
        report=self.root/"review.md"; report.write_text("Test-only review envelope; not genuine visual evidence.")
        review={"accepted":True,"sourceKind":"simulatorFixture","report":str(report.relative_to(ROOT)),
                "reportSHA256":sha(report),"bundleIdentitySHA256":digest(bundle_identity(self.bundle,validate_bundle(self.bundle)))}
        doc=derive(self.bundle,self.root/"review-crops","test-only-review","46dce7b",review=review)
        # Tests exercise the review mechanism, not a real source qualification.
        self.assertNotIn("trainingApproval",doc)
        report.write_text("changed")
        with self.assertRaisesRegex(FocusDataError,"changed_visual_review"):
            validate_manifest(doc,self.root/"review-crops")

    def test_manifest_cli_collision_and_false_source_remain_closed(self):
        output=self.root/"existing.json"; output.write_text("preserve")
        r=self.cli("build_simulator_focus_manifest.py","--bundle",self.bundle,"--corpus-id","test-only",
                   "--producer-reference","46dce7b","--output",output)
        self.assertNotEqual(r.returncode,0); self.assertEqual(output.read_text(),"preserve")
        index=json.loads((self.bundle/"dataset-index.json").read_text())
        index["sourceDescription"]={"captureMethod":"fixture-batch","collectedAt":0,
                "assurance":"reported-source; not-attested","environment":{"isSimulator":False}}
        (self.bundle/"dataset-index.json").write_text(json.dumps(index))
        with self.assertRaisesRegex(FocusDataError,"conflicting_simulator"):
            derive(self.bundle,self.root/"false-source","test-only","46dce7b",test_only=True)


if __name__ == "__main__": unittest.main()
