"""Offline tests for the actual retention CLI and new-only recovery mechanism."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import corpus_retention as r


class RetentionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=r.ROOT / ".build/debug-output")
        self.base = Path(self.tmp.name)
        self.source = self.base / "source"
        self.source.mkdir()
        (self.source / "train").mkdir()
        (self.source / "train/image.png").write_bytes(b"test-only-pixels")
        (self.source / "train/image.json").write_text('{"label":"fixture-only"}')
        (self.source / "manifest.json").write_text('{"scope":"test-only"}')
        self.doc = r.inventory(self.source)

    def tearDown(self):
        self.tmp.cleanup()

    def test_deterministic_complete_inventory_and_restore(self):
        self.assertEqual(self.doc, r.inventory(self.source))
        out = self.base / "restored"
        result = r.restore(self.doc, self.source, out)
        self.assertEqual(result["verifiedFiles"], 3)
        self.assertTrue(result["contentVerified"])
        self.assertFalse(result["independentBackupVerified"])
        self.assertEqual(r.verify(self.doc, out)["inventorySHA256"], self.doc["inventorySHA256"])

    def test_missing_member_and_partial_copy_rejected(self):
        (self.source / "train/image.json").unlink()
        with self.assertRaisesRegex(ValueError, "membership"):
            r.verify(self.doc, self.source)
        with self.assertRaises(ValueError):
            r.restore(self.doc, self.source, self.base / "never-created")
        self.assertFalse((self.base / "never-created").exists())

    def test_same_size_changed_bytes(self):
        p = self.source / "train/image.png"
        p.write_bytes(b"x" * p.stat().st_size)
        with self.assertRaisesRegex(ValueError, "hash_mismatch"):
            r.verify(self.doc, self.source)

    def test_extra_member_rejected(self):
        (self.source / "extra").write_text("unknown")
        with self.assertRaisesRegex(ValueError, "membership"):
            r.verify(self.doc, self.source)

    def test_explicit_finder_exclusion_preserves_strict_corpus_checks(self):
        auxiliary = self.source / ".DS_Store"
        auxiliary.write_bytes(b"first")
        strict = r.inventory(self.source)
        scoped = r.inventory(self.source, exclude_finder_metadata=True)
        self.assertEqual(scoped["excludedPathsAtInventory"], [".DS_Store"])
        auxiliary.write_bytes(b"second")
        with self.assertRaisesRegex(ValueError, "hash_mismatch"):
            r.verify(strict, self.source)
        self.assertTrue(r.verify(scoped, self.source)["contentVerified"])
        r.restore(scoped, self.source, self.base / "restored")
        self.assertFalse((self.base / "restored/.DS_Store").exists())
        (self.source / "unexplained.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "membership"):
            r.verify(scoped, self.source)

    def test_exclusion_cannot_hide_symlink_or_corpus_member(self):
        (self.source / ".DS_Store").symlink_to(self.base / "missing")
        with self.assertRaisesRegex(ValueError, "symlink"):
            r.inventory(self.source, exclude_finder_metadata=True)
        doc = copy.deepcopy(self.doc)
        doc["excludedAuxiliaryNames"] = ["manifest.json"]
        self.reseal(doc)
        with self.assertRaisesRegex(ValueError, "unsupported_auxiliary"):
            r.verify(doc, self.source)

    def test_inventory_seal_rejected(self):
        self.doc["members"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "changed_inventory"):
            r.verify(self.doc, self.source)

    def test_resealed_unsafe_duplicate_and_invalid_members_rejected(self):
        for value in ("../escape", "/absolute", "train/../escape", "train//image.png", ""):
            doc = copy.deepcopy(self.doc)
            doc["members"][0]["path"] = value
            self.reseal(doc)
            with self.assertRaises(ValueError):
                r.verify(doc, self.source)
        doc = copy.deepcopy(self.doc)
        doc["members"][1]["path"] = doc["members"][0]["path"]
        self.reseal(doc)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            r.verify(doc, self.source)

    def reseal(self, doc):
        doc["inventorySHA256"] = r.digest({k:v for k,v in doc.items() if k != "inventorySHA256"})

    def test_symlink_and_broken_dependency_rejected(self):
        for target in (self.source / "manifest.json", self.base / "missing"):
            link = self.source / "link"
            link.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "symlink"):
                r.inventory(self.source)
            link.unlink()

    def test_collision_preserves_existing_output(self):
        out = self.base / "existing"
        out.mkdir()
        marker = out / "keep"
        marker.write_text("preserve")
        with self.assertRaisesRegex(ValueError, "collision"):
            r.restore(self.doc, self.source, out)
        self.assertEqual(marker.read_text(), "preserve")

    def test_nested_restore_and_external_output_rejected(self):
        for out in (self.source / "new", Path("/not-authorized-corpus-output")):
            with self.assertRaises(ValueError):
                r.restore(self.doc, self.source, out)

    def test_failed_copy_retains_partial_evidence(self):
        out = self.base / "partial"
        with patch.object(r.shutil, "copyfileobj", side_effect=OSError("interrupted")):
            with self.assertRaisesRegex(OSError, "interrupted"):
                r.restore(self.doc, self.source, out)
        self.assertTrue(out.exists())
        self.assertTrue((out / "manifest.json").exists())
        self.assertEqual(r.inventory(self.source), self.doc)

    def test_changed_source_during_copy_rejected(self):
        real = r.shutil.copyfileobj
        def changed(src, dst):
            real(src, dst)
            Path(src.name).write_bytes(b"changed")
        with patch.object(r.shutil, "copyfileobj", changed):
            with self.assertRaisesRegex(ValueError, "source_or_copy_changed"):
                r.restore(self.doc, self.source, self.base / "partial")

    def cli(self, *args):
        return subprocess.run([sys.executable, str(r.ROOT / "scripts/corpus_retention.py"), *map(str,args)],
                              cwd=r.ROOT, capture_output=True, text=True, timeout=10)

    def test_real_cli_inventory_verify_restore_collision(self):
        inv = self.base / "inventory.json"
        result = self.cli("inventory", "--source", self.source, "--output", inv)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["fileCount"], 3)
        for command in ("verify", "restore"):
            args = [command, "--inventory", inv, "--copy", self.source]
            if command == "restore": args += ["--output", self.base / "restored"]
            result = self.cli(*args)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(json.loads(result.stdout)["contentVerified"])
        result = self.cli("inventory", "--source", self.source, "--output", inv)
        self.assertEqual(result.returncode, 2)

    def test_cli_rejects_inventory_output_inside_source(self):
        result = self.cli("inventory", "--source", self.source, "--output", self.source / "inventory.json")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.source / "inventory.json").exists())


if __name__ == "__main__": unittest.main()
