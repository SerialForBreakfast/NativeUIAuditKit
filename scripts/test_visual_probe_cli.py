"""Offline integration tests of the real planning-only generator command."""
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / ".build/debug/NativeUIDatasetGenerator"


class VisualProbeCLITests(unittest.TestCase):
    def invoke(self, *args):
        return subprocess.run([str(BINARY), "--plan-visual-addon", *args],
                              cwd=ROOT, capture_output=True, timeout=10)

    def test_real_cli_is_deterministic_and_development_only(self):
        first = self.invoke("--content-seed", "19")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, self.invoke("--content-seed", "19").stdout)
        plan = json.loads(first.stdout)
        self.assertEqual(plan["version"], "visual-probe-catalog-v2")
        self.assertTrue(plan["planningOnly"])
        self.assertEqual(plan["partition"], "development")
        self.assertEqual(len(plan["cases"]), 144)
        self.assertEqual(plan["maximumCaptureBatch"], 48)
        self.assertEqual(len({row["id"] for row in plan["cases"]}), 144)
        self.assertEqual({row["config"]["seed"] for row in plan["cases"]}, {19})
        overflow = [row for row in plan["cases"] if row["config"]["templateFamily"] == "DynamicTypeOverflow"]
        self.assertEqual({row["config"]["dynamicTypeSize"] for row in overflow},
                         {"accessibilityExtraExtraExtraLarge"})
        self.assertIn("DynamicTypeOverflow/theme/type", plan["unsupportedIntersections"])

    def test_invalid_and_execution_arguments_rejected_before_pipeline(self):
        for args in [(), ("--content-seed",), ("--content-seed", "-1"),
                     ("--content-seed", "18446744073709551616"),
                     ("--content-seed", "x"),
                     ("--content-seed", "7", "--device-udid", "booted")]:
            with self.subTest(args=args):
                result = self.invoke(*args)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, b"")
                self.assertIn(b"planning only", result.stderr)


if __name__ == "__main__":
    unittest.main()
