"""Read-only checks that artifact ignores do not hide distributable source/fixtures."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RepositoryIgnoreTests(unittest.TestCase):
    def ignored(self, path):
        result = subprocess.run(["git", "check-ignore", "--no-index", "--quiet", "--", path],
                                cwd=ROOT, capture_output=True, timeout=5)
        self.assertIn(result.returncode, (0, 1), result.stderr)
        return result.returncode == 0

    def test_generated_outputs_stay_local(self):
        for path in ["reports/work/FUTURE/run.log", "reports/work/FUTURE/nested/crop.png",
                     "reports/work/FUTURE/inventory.json", "reports/work/FUTURE/scratch.py",
                     "reports/work/FUTURE/run.xcresult/Info.plist", "dataset/pair.png",
                     "NativeUITrainer/reconstructed_corpora/version/manifest.json",
                     ".venv-export/bin/python", "NativeUITrainer/.torch/cache",
                     "new-checkpoint.pt", "new-export.mlpackage/Manifest.json"]:
            with self.subTest(path=path): self.assertTrue(self.ignored(path))

    def test_durable_source_and_intentional_fixtures_remain_visible(self):
        for path in ["reports/work/FUTURE/handoff.md", "reports/work/FUTURE/artifacts.sha256",
                     "Research/schemas/annotation.schema.v1.2.json", "Research/ArtifactRetention.md",
                     "Tests/Fixtures/catalog.json", "Tests/Fixtures/frame.png",
                     "scripts/validate_visual_probe.py", "Sources/NativeUIAuditKit/Example.swift",
                     "NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc/coremldata.bin"]:
            with self.subTest(path=path): self.assertFalse(self.ignored(path))


if __name__ == "__main__": unittest.main()
