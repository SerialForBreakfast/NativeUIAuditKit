"""Offline tests; generated fixtures stay in .build/debug-output."""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import eval_run013 as ev
from prediction_artifact import build_artifact, load_request, make_result, sha256_file, PredictionArtifactError
from reference_comparison import ComparisonError, compare
from test_prediction_artifact import png_bytes


class Run013Tests(unittest.TestCase):
    def setUp(self):
        root = ev.ROOT / ".build/debug-output"
        root.mkdir(parents=True, exist_ok=True)
        self.work = Path(tempfile.mkdtemp(dir=root, prefix="r013-test-"))
        (self.work / "a.png").write_bytes(png_bytes(100, 200))
        (self.work / "a.txt").write_text("0 0.5 0.5 0.2 0.2\n")
        (self.work / "model.pt").write_bytes(b"synthetic checkpoint")
        self.manifest = self.work / "manifest.json"
        self.payload = {"formatVersion": ev.INPUT_FORMAT_VERSION, "corpusID": "test-only", "images": [
            {"imageID": "test/a.png", "imagePath": "a.png", "labelPath": "a.txt",
             "imageSHA256": sha256_file(self.work / "a.png"), "labelSHA256": sha256_file(self.work / "a.txt")} ]}
        self.manifest.write_text(json.dumps(self.payload))
        self.request = load_request(self.manifest, 41)

    def tearDown(self):
        shutil.rmtree(self.work)

    def artifact(self, detections=None, failed=False):
        row = make_result(self.request.images[0], 41, failure={"code":"test", "message":"synthetic"}) if failed else make_result(self.request.images[0],41,detections=detections or [])
        return build_artifact(self.request, self.work/"model.pt", ev.CATEGORY_MAP,"1.0",ev.PREDICTION_SETTINGS,[row])

    def validate(self, doc):
        return ev.validated_artifact(doc, self.request, sha256_file(self.work/"model.pt"))

    def test_metrics_geometry_and_missing_class(self):
        # GT [40,80,60,120], candidate IoU .6; distinguishes discovery from precision.
        doc = self.artifact([{"classID":0,"score":.9,"xyxyPixels":[45,80,65,120]}])
        result = ev.score(doc,self.request,["actionSheet","absent"])
        first, second = result["perClass"]
        self.assertEqual((first["ap50"],first["ap70"],first["ap90"]),(1,0,0))
        self.assertEqual(first["ap50_95"], .3)
        self.assertIsNone(second["ap50"])
        self.assertEqual(result["supportedClasses"],1)
        self.assertEqual(result["metrics"]["map50"],1)

    def test_empty_is_valid_but_failed_is_rejected(self):
        self.validate(self.artifact())
        result = ev.score(self.artifact(),self.request,["actionSheet"])
        self.assertEqual((result["perClass"][0]["fn"],result["perClass"][0]["ap50"]),(1,0))
        with self.assertRaises(ComparisonError): self.validate(self.artifact(failed=True))

    def test_strict_baseline_reuse_and_comparison(self):
        doc = self.artifact()
        self.validate(doc)
        doc["metrics"]={"ap50":.2,"missing":None}
        other=copy.deepcopy(doc); other["metrics"]["ap50"]=.7
        self.assertAlmostEqual(compare(doc,other)["deltas"]["ap50"],.5)
        self.assertNotIn("missing",compare(doc,other)["deltas"])
        for field, value in (("imageSHA256","changed"),("labelSHA256","changed"),("width",99),("status","ok")):
            bad=copy.deepcopy(doc); bad["results"][0][field]=value
            with self.assertRaises((ComparisonError,PredictionArtifactError)): self.validate(bad)
        bad=copy.deepcopy(doc); bad["settings"]["imgsz"]=320
        with self.assertRaises(ComparisonError): self.validate(bad)
        bad=copy.deepcopy(doc); bad["results"] *= 2
        with self.assertRaises(ComparisonError): self.validate(bad)
        bad=copy.deepcopy(doc); bad["completeness"]["resultCount"]=2
        with self.assertRaises(ComparisonError): self.validate(bad)
        bad=copy.deepcopy(doc); bad["model"]["checkpointSHA256"]="changed"
        with self.assertRaises(ComparisonError): self.validate(bad)
        bad=copy.deepcopy(doc); bad["results"]=[]
        with self.assertRaises(ComparisonError): self.validate(bad)

    def test_frozen_changed_bytes_and_corruption(self):
        (self.work/"a.txt").write_text("")
        with self.assertRaisesRegex(PredictionArtifactError,"frozen labelSHA256"):
            load_request(self.manifest,41)
        (self.work/"a.png").write_bytes(b"corrupt")
        with self.assertRaisesRegex(PredictionArtifactError,"cannot be decoded"):
            load_request(self.manifest,41)

    def test_population_split_and_unknown_rejection(self):
        for family in ev.DEFAULT_HOLDOUT_FAMILIES: self.assertEqual(ev.population(family),"withheld")
        for family in ev.ADDON_FAMILIES: self.assertEqual(ev.population(family),"addon")
        with self.assertRaises(ValueError): ev.population("new unreviewed family")

    def test_prepare_real_files_split_accounting_and_rejection(self):
        from PIL import Image
        source, dataset = self.work/"source", self.work/"dataset"
        entries = []
        specs = [("test", "CardDetail"), ("test", "ModalDialogueFlow"),
                 ("train", "ModalDialogueFlow")]
        for index, (split, family) in enumerate(specs):
            png = source/split/f"image{index}.png"
            png.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (100, 200), (index*60, 0, 0)).save(png)
            sidecar = {"generatorProfile":{"templateFamily":family},
                "imageSHA256":sha256_file(png), "image":{"pixelWidth":100,"pixelHeight":200},
                "elements":[{"elementType":ev.load_names()[0],
                    "boundsVisionNormalized":{"x":.4,"y":.4,"width":.2,"height":.2}}]}
            png.with_suffix(".json").write_text(json.dumps(sidecar))
            entries.append({"fileName":str(png.relative_to(source)), "split":split,
                            "templateFamily":family, "sha256":sha256_file(png)})
            images, labels = dataset/split/"images", dataset/split/"labels"
            images.mkdir(parents=True, exist_ok=True); labels.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(png, images/png.name)
            (labels/(png.stem+".txt")).write_text(ev.expected_label(sidecar,ev.load_names()))
        (source/"manifest.json").write_text(json.dumps({"entries":entries}))
        out=self.work/"prepared"
        with patch.object(ev,"CHECKPOINT",self.work/"model.pt"), patch.object(ev,"BASE_CHECKPOINT",self.work/"model.pt"):
            ev.prepare(out, dataset, source)
            audit=ev.read(out/"preflight.json")
            self.assertTrue(audit["integrityPassed"])
            self.assertEqual(audit["splitCounts"], {"test":2,"train":1})
            self.assertEqual(audit["testFamilyOverlap"], {"ModalDialogueFlow":{"test":1,"train":1}})
            self.assertEqual(audit["crossSplitPixelGroups"],[])
            withheld=load_request(out/"withheld_manifest.json",41)
            addon=load_request(out/"addon_manifest.json",41)
            combined=load_request(out/"combined_manifest.json",41)
            ids=lambda request:{i.image_id for i in request.images}
            self.assertFalse(ids(withheld)&ids(addon))
            self.assertEqual(ids(withheld)|ids(addon),ids(combined))
            (dataset/"test/labels/image0.txt").write_text("0 0.5 0.5 2 2\n")
            with self.assertRaisesRegex(ValueError,"preflight rejected"):
                ev.prepare(self.work/"rejected", dataset, source)
            self.assertFalse((self.work/"rejected/freeze.json").exists())
            self.assertEqual(len(ev.read(self.work/"rejected/preflight.json")["errors"]),1)

    def test_actual_exporter_empty_failure_and_collision(self):
        names=ev.load_names()
        class Model:
            def __init__(self,path): self.names=dict(enumerate(names))
            def predict(self,**kwargs):
                self_kwargs=kwargs
                assert self_kwargs["imgsz"] == 640 and self_kwargs["conf"] == .001
                return [SimpleNamespace(boxes=None)]
        output=self.work/"export.json"
        with patch.dict(sys.modules,{"ultralytics":SimpleNamespace(YOLO=Model)}):
            ev.export_predictions(self.manifest,self.work/"model.pt",output,"mps")
            self.validate(ev.read(output))
            with self.assertRaisesRegex(PredictionArtifactError,"already exists"):
                ev.export_predictions(self.manifest,self.work/"model.pt",output,"mps")
            with patch.object(Model,"predict",side_effect=RuntimeError("synthetic failure")):
                ev.export_predictions(self.manifest,self.work/"model.pt",self.work/"failed.json","mps")
            with self.assertRaises(ComparisonError): self.validate(ev.read(self.work/"failed.json"))

    def test_model_taxonomy_mismatch_rejected(self):
        model=SimpleNamespace(names={0:"wrong"})
        with patch.dict(sys.modules,{"ultralytics":SimpleNamespace(YOLO=lambda p:model)}):
            with self.assertRaisesRegex(PredictionArtifactError,"category order"):
                ev.export_predictions(self.manifest,self.work/"model.pt",self.work/"mismatch.json","mps")

    def test_cli_rejects_outside_output(self):
        result=subprocess.run([sys.executable,"-B",str(ev.ROOT/"scripts/eval_run013.py"),"prepare","--output","/not-project"],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn("output must stay inside project",result.stderr)

    def test_report_renderer_preserves_unavailable_and_deltas(self):
        import render_run013_report as renderer
        result=ev.score(self.artifact(),self.request,["actionSheet","absent"])
        result["perFamily"]={"fixture":copy.deepcopy(result)}
        baseline=copy.deepcopy(result)
        baseline["perClass"][0]["ap50"] = .4
        payload={"baseline":baseline, "populations":{p:result for p in ("withheld","addon","combined")}}
        (self.work/"evaluation.json").write_text(json.dumps(payload))
        with patch.object(renderer,"OUT",self.work):
            renderer.main()
            report=(self.work/"metrics.md").read_text()
            self.assertIn("| absent | 0 | unavailable",report)
            self.assertIn("| actionSheet | 1 | -0.4000",report)
            self.assertIn("historical original-corpus 0.586 has no numerical delta",report)
            with self.assertRaises(FileExistsError): renderer.main()


if __name__ == "__main__": unittest.main()
