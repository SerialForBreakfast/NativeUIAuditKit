"""Actual intake CLI and adversarial probe exports; no native simulator needed."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image
from validate_visual_probe import ROOT, sha256, validate

TARGET = "9026ECA9-77DB-4AE6-8FE6-BB239E9571FA"


class ProbeIntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / ".build", prefix="probe-intake-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "batch"
        self.root.mkdir()
        self.catalog = Path(self.tmp.name) / "expected-catalog.json"
        planned = subprocess.run([str(ROOT / ".build/debug/NativeUIDatasetGenerator"),
            "--plan-visual-addon", "--content-seed", "19"], capture_output=True, timeout=10)
        self.assertEqual(planned.returncode, 0, planned.stderr)
        self.catalog.write_bytes(planned.stdout)
        catalog = json.loads(planned.stdout)
        row = catalog["cases"][0]; c = row["config"]
        self.ids = [row["id"]]
        self.row = row
        scale = c["pixelScale"]
        w, h = [n * scale for n in c["osProfile"]["screenSize"]]
        Image.new("RGB", (w, h), "gray").save(self.root / "probe-000.png")
        (self.root / "catalog.json").write_bytes(self.catalog.read_bytes())
        image = {k: c[k] for k in ("deviceName", "colorScheme", "dynamicTypeSize", "locale", "layoutDirection")}
        image.update({k: c["accessibilityFlags"][k] for k in ("reduceTransparency", "increaseContrast", "boldText", "buttonShapes", "onOffLabels", "smartInvert")})
        image.update(fileName="probe-000.png", pixelWidth=w, pixelHeight=h, scale=scale,
                     platform="iOS", osVersion="unknown", interfaceIdiom="phone", orientation="portrait",
                     safeAreaInsets=dict(top=c["osProfile"]["safeAreaTopInset"], bottom=c["osProfile"]["safeAreaBottomInset"], left=0, right=0))
        self.ann = dict(schemaVersion="1.2", imageSHA256=sha256(self.root / "probe-000.png"), image=image,
            generatorProfile=dict(templateFamily=c["templateFamily"], seed=c["seed"], generatorVersion="visual-probe-1",
                isolationTemplate=False, lowDensity=False,
                simulatorState={k: v for k, v in c["simulatorOverride"].items() if k != "cellularMode"}),
            elements=[dict(id="button", elementType="primaryButton", framework="UIKit", traits=[], knownIssues=[],
                state=dict(isEnabled=True, isSelected=None), excluded=False, occluded=False,
                boundsPoints=dict(x=10,y=10,width=20,height=20),
                boundsPixels=dict(x=10*scale,y=10*scale,width=20*scale,height=20*scale),
                boundsVisionNormalized=dict(x=10*scale/w,y=1-30*scale/h,width=20*scale/w,height=20*scale/h))])
        self.receipt = dict(version="visual-probe-capture-v1", completion="captured_pending_visual_review",
            trainingEligible=False, partition="development", catalogSHA256=sha256(self.catalog), simulatorUUID=TARGET,
            runtimeOS="26.0", expectedCount=1, actualCount=1, unsupportedIntersections=catalog["unsupportedIntersections"],
            members=[dict(id=row["id"], group=row["group"], image="probe-000.png", annotation="probe-000.json",
                imageSHA256=self.ann["imageSHA256"], annotationSHA256="")])
        self.seal()

    def seal(self):
        (self.root / "probe-000.json").write_text(json.dumps(self.ann))
        self.receipt["members"][0]["annotationSHA256"] = sha256(self.root / "probe-000.json")
        self.receipt["members"][0]["imageSHA256"] = sha256(self.root / "probe-000.png")
        (self.root / "capture.json").write_text(json.dumps(self.receipt))

    def run_intake(self):
        return validate(self.root, self.catalog, self.ids, TARGET)

    def test_real_cli_and_development_semantics(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_visual_probe.py"),
            "--batch", str(self.root), "--catalog", str(self.catalog), "--case-id", self.ids[0], "--target", TARGET],
            capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["acceptedCount"], 1)
        self.assertFalse(report["trainingEligible"])
        self.assertEqual(report["visualReview"], "pending")
        self.assertEqual(report["requestedCoverage"][0]["theme"], "dark")
        (self.root / "failure.json").write_text("{}")
        failed = subprocess.run([sys.executable, str(ROOT / "scripts/validate_visual_probe.py"),
            "--batch", str(self.root), "--catalog", str(self.catalog), "--case-id", self.ids[0], "--target", TARGET],
            capture_output=True, text=True, timeout=20)
        self.assertEqual(failed.returncode, 1)
        self.assertEqual(failed.stdout, "")
        self.assertFalse(json.loads(failed.stderr)["trainingEligible"])

    def test_receipt_claims_and_membership_rejected(self):
        original = copy.deepcopy(self.receipt)
        for key, value in [("trainingEligible", True), ("completion", "partial"), ("partition", "test"),
            ("version", "v99"), ("actualCount", True), ("expectedCount", 2), ("simulatorUUID", "other"),
            ("unsupportedIntersections", []), ("catalogSHA256", "0"*64)]:
            with self.subTest(key=key):
                self.receipt = copy.deepcopy(original); self.receipt[key] = value; self.seal()
                with self.assertRaises(ValueError): self.run_intake()
        (self.root / "capture.json").write_text("[]")
        with self.assertRaisesRegex(ValueError, "invalid_receipt_root"): self.run_intake()

    def test_config_schema_geometry_and_unknown_state(self):
        original = copy.deepcopy(self.ann)
        mutations = [lambda a: a["image"].update(colorScheme="light"),
            lambda a: a.update(schemaVersion="1.0"),
            lambda a: a["elements"][0]["state"].pop("isEnabled"),
            lambda a: a["elements"][0]["boundsPixels"].update(x=99),
            lambda a: a["elements"][0]["boundsVisionNormalized"].update(y=0),
            lambda a: a["elements"][0].update(excluded=True),
            lambda a: a.update(elements=[])]
        for mutate in mutations:
            self.ann = copy.deepcopy(original); mutate(self.ann); self.seal()
            with self.assertRaises(ValueError): self.run_intake()

    def test_hash_corrupt_png_missing_and_symlink(self):
        original = (self.root / "probe-000.png").read_bytes()
        (self.root / "probe-000.png").write_bytes(b"not png")
        with self.assertRaises(ValueError): self.run_intake()
        self.ann["imageSHA256"] = sha256(self.root / "probe-000.png"); self.seal()
        with self.assertRaises(OSError): self.run_intake()
        (self.root / "probe-000.png").unlink()
        with self.assertRaises(ValueError): self.run_intake()
        (self.root / "other.png").write_bytes(original)
        (self.root / "probe-000.png").symlink_to(self.root / "other.png")
        with self.assertRaises(ValueError): self.run_intake()

    def test_duplicate_keys_selection_and_traversal(self):
        for selected in ([], self.ids * 2, ["missing"]):
            with self.assertRaises(ValueError): validate(self.root, self.catalog, selected, TARGET)
        self.receipt["members"][0]["image"] = "../escape.png"; self.seal()
        with self.assertRaises(ValueError): self.run_intake()
        (self.root / "capture.json").write_text('{"version":"one","version":"two"}')
        with self.assertRaises(ValueError): self.run_intake()

    def test_clipped_geometry_preserves_boundary_semantics(self):
        e = self.ann["elements"][0]; scale = self.ann["image"]["scale"]
        width = self.ann["image"]["pixelWidth"]
        e["boundsPoints"]["x"] = -5
        e["boundsPixels"]["x"] = -5 * scale
        e["boundsVisionNormalized"].update(x=0, width=15 * scale / width)
        e.update(occluded=True, occlusionType="imageBoundary")
        self.seal(); self.assertEqual(self.run_intake()["integrity"], "passed")
        e["occlusionType"] = "other"; self.seal()
        with self.assertRaises(ValueError): self.run_intake()

    def test_identical_pixels_are_reported_not_removed(self):
        row = json.loads(self.catalog.read_text())["cases"][1]
        self.ids.append(row["id"])
        second = copy.deepcopy(self.ann)
        second["image"].update(fileName="probe-001.png", colorScheme=row["config"]["colorScheme"])
        second["generatorProfile"]["simulatorState"] = {k: v for k, v in row["config"]["simulatorOverride"].items() if k != "cellularMode"}
        (self.root / "probe-001.png").write_bytes((self.root / "probe-000.png").read_bytes())
        (self.root / "probe-001.json").write_text(json.dumps(second))
        self.receipt["members"].append(dict(id=row["id"], group=row["group"], image="probe-001.png",
            annotation="probe-001.json", imageSHA256=second["imageSHA256"],
            annotationSHA256=sha256(self.root / "probe-001.json")))
        self.receipt.update(expectedCount=2, actualCount=2); self.seal()
        report = self.run_intake()
        self.assertEqual(report["duplicatePixelGroups"], [self.ids])
        self.assertEqual(report["acceptedCount"], 2)
        self.assertEqual(report["visualReview"], "pending")


if __name__ == "__main__": unittest.main()
