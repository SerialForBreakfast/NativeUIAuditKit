import json
from pathlib import Path
import tempfile
import unittest

from compress_focus_ring_coreml import preflight
from focus_ring_baseline import artifact_digest


class CompressionTests(unittest.TestCase):
    def setUp(self):
        parent = Path(__file__).resolve().parents[1] / ".build/debug-output/compression-tests"
        parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / "model.mlpackage"
        self.package.mkdir(); (self.package / "weights.bin").write_bytes(b"test-only")
        self.report = self.root / "report.json"
        self.data = {"releaseEligible": False, "mlpackage": str(self.package), "experimentalID": "old-test"}
        self.report.write_text(json.dumps(self.data))
        self.output = self.root / "output"
        self.digest = artifact_digest(self.package)

    def check(self, package=None, destination=None, expected=None):
        return preflight(package or self.package, self.report, destination or self.output, "new-test", expected or self.digest)

    def test_preflight_does_not_write_or_import_coreml(self):
        self.check(); self.assertFalse(self.output.exists())
        self.assertEqual(artifact_digest(self.package), self.digest)

    def test_changed_bytes(self):
        with self.assertRaisesRegex(ValueError, "source_package_changed"): self.check(expected="0"*64)

    def test_collision(self):
        self.output.mkdir()
        with self.assertRaisesRegex(ValueError, "output_collision"): self.check()

    def test_overlap(self):
        with self.assertRaisesRegex(ValueError, "source_output_overlap"): self.check(destination=self.package / "child")

    def test_symlink(self):
        link = self.root / "alias"; link.symlink_to(self.package)
        with self.assertRaisesRegex(ValueError, "symlink_package_path"): self.check(package=link)

    def test_report_binding(self):
        self.data["mlpackage"] = str(self.root / "other")
        self.report.write_text(json.dumps(self.data))
        with self.assertRaisesRegex(ValueError, "source_report_mismatch"): self.check()

    def test_release_source(self):
        self.data["releaseEligible"] = True; self.report.write_text(json.dumps(self.data))
        with self.assertRaisesRegex(ValueError, "experimental_source_required"): self.check()

    def test_production_destination(self):
        root = Path(__file__).resolve().parents[1]
        with self.assertRaisesRegex(ValueError, "production_export_forbidden"):
            self.check(destination=root / "NativeUIAuditKitModels/no-compression-test")
