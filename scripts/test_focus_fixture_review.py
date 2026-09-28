"""Actual offline review CLI, deterministic sheets, and preserved source evidence."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from focus_dataset_contract import ROOT
import focus_fixture_review as review
from test_ttr_sidecar_v2 import write_bundle
from ttr_focus_manifest import derive


class ReviewTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT/".build/debug-output"; parent.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=parent); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.bundle = self.root/"bundle"
        write_bundle(self.bundle)
        self.crops = self.root/"crops"
        derive(self.bundle, self.crops, "test-only", "synthetic-no-execution", test_only=True)
        self.manifest = self.crops/"focus_dataset_manifest.json"

    def test_real_cli_and_deterministic_pages_no_approval(self):
        before = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.bundle.iterdir()}
        command = [sys.executable, str(ROOT/"scripts/focus_fixture_review.py"), "--manifests", str(self.manifest),
                   "--output", str(self.root/"one")]
        result = subprocess.run(command, capture_output=True, text=True, timeout=120,
                                env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
        self.assertEqual(result.returncode,0,result.stderr)
        first = json.loads((self.root/"one/inventory.json").read_text())
        second = review.prepare([self.manifest], self.root/"two")
        self.assertEqual(first,second); self.assertFalse(first["trainingApproval"])
        self.assertEqual(first["pairCount"],1)
        self.assertEqual((self.root/"one/sheet-001.png").read_bytes(),(self.root/"two/sheet-001.png").read_bytes())
        self.assertEqual(before,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.bundle.iterdir()})

    def test_empty_duplicate_and_output_collision(self):
        for paths in ([],[self.manifest,self.manifest]):
            with self.assertRaisesRegex(ValueError,"missing_or_duplicate"):
                review.prepare(paths,self.root/"unused")
        with self.assertRaisesRegex(ValueError,"output_collision"):
            review.prepare([self.manifest],self.crops)

    def test_missing_and_corrupt_originals_rejected(self):
        original=(self.bundle/"u.png").read_bytes()
        (self.bundle/"u.png").write_bytes(b"corrupt")
        with self.assertRaises(ValueError): review.prepare([self.manifest],self.root/"bad")
        (self.bundle/"u.png").write_bytes(original)
        (self.bundle/"u.png").unlink()
        with self.assertRaises((ValueError,OSError)): review.prepare([self.manifest],self.root/"missing")

    def test_incompatible_and_changed_membership_rejected(self):
        original=json.loads(self.manifest.read_text())
        for change in (lambda d:d.update(version="final-challenge"),lambda d:d["pairs"][0].update(split="test"),
                       lambda d:d["pairs"][0]["frames"]["focused"].update(bounds=[0,0,1,1])):
            doc=json.loads(json.dumps(original));change(doc);self.manifest.write_text(json.dumps(doc))
            with self.assertRaises(ValueError): review.prepare([self.manifest],self.root/"bad")

if __name__ == "__main__": unittest.main()
