import json
from pathlib import Path
import shutil
import tempfile
import unittest
import copy

import corpus_retention as r
import seal_ios_reconstruction as s


class PrefixPreservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=r.ROOT / ".build/debug-output")
        self.root = Path(self.temp.name)
        self.prefix = self.root / "prefix"
        self.prefix.mkdir()
        (self.prefix / "one.png").write_bytes(b"test-only-image")
        (self.prefix / "one.json").write_text('{"label":"original"}')
        self.entry = {"fileName": "one.png", "split": "train", "templateFamily": "fixture"}
        (self.prefix / "manifest.json").write_text(json.dumps({"entries": [self.entry]}))
        (self.prefix / "capture-ledger.json").write_text(json.dumps({"accepted": {"pixel": "one.png"}, "rejected": []}))
        self.inventory = r.inventory(self.prefix)
        self.corpus = self.root / "corpus"
        shutil.copytree(self.prefix, self.corpus)

    def tearDown(self):
        self.temp.cleanup()

    def test_extended_membership_preserves_original(self):
        entries = [self.entry, {"fileName": "two.png"}]
        (self.corpus / "manifest.json").write_text(json.dumps({"entries": entries}))
        self.assertEqual(s.preserve_prefix(self.inventory, self.prefix, self.corpus)["prefixImagesPreserved"], 1)

    def test_original_pixel_or_annotation_change_rejected(self):
        for name in ("one.png", "one.json"):
            p = self.corpus / name
            old = p.read_bytes()
            p.write_bytes(b"altered")
            with self.assertRaisesRegex(ValueError, "prefix_byte_changed"):
                s.preserve_prefix(self.inventory, self.prefix, self.corpus)
            p.write_bytes(old)

    def test_split_or_ledger_rewrite_rejected(self):
        (self.corpus / "manifest.json").write_text(json.dumps({"entries": [{**self.entry, "split": "test"}]}))
        with self.assertRaisesRegex(ValueError, "lineage_changed"):
            s.preserve_prefix(self.inventory, self.prefix, self.corpus)
        shutil.copyfile(self.prefix / "manifest.json", self.corpus / "manifest.json")
        (self.corpus / "capture-ledger.json").write_text(json.dumps({"accepted": {}, "rejected": []}))
        with self.assertRaisesRegex(ValueError, "ledger_changed"):
            s.preserve_prefix(self.inventory, self.prefix, self.corpus)

    def test_changed_source_cannot_be_hidden_by_good_copy(self):
        (self.prefix / "one.png").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "hash_mismatch"):
            s.preserve_prefix(self.inventory, self.prefix, self.corpus)

    def test_duplicate_manifest_identity_rejected(self):
        (self.corpus / "manifest.json").write_text(json.dumps({"entries": [self.entry, self.entry]}))
        with self.assertRaisesRegex(ValueError, "duplicate_manifest"):
            s.preserve_prefix(self.inventory, self.prefix, self.corpus)

    def audit(self):
        return {"errors": [], "manifestEntries": 1, "rejectedDuplicates": [],
                "validatorSHA256": s.v.sha256(Path(s.v.__file__)),
                "schemaSHA256": s.v.sha256(s.v.SCHEMA), "generatorSHA256": s.v.sha256(s.v.GENERATOR),
                "manifestSHA256": s.v.sha256(self.corpus / "manifest.json"),
                "captureLedgerSHA256": s.v.sha256(self.corpus / "capture-ledger.json"),
                "members": [{"path": "one.png", "valid": True,
                   "imageSHA256": s.v.sha256(self.corpus / "one.png"),
                   "annotationSHA256": s.v.sha256(self.corpus / "one.json")}]}

    def test_finder_exclusion_preserves_metadata_and_only_excludes_that_name(self):
        metadata = self.corpus / ".DS_Store"
        metadata.write_bytes(b"mutable Finder state")
        audit = self.audit()
        audit["errors"] = [{"error": "unindexed_members", "members": [".DS_Store"]}]
        inventory = s.verify_audited_content(audit, self.corpus)
        self.assertEqual(inventory["excludedPathsAtInventory"], [".DS_Store"])
        self.assertEqual(metadata.read_bytes(), b"mutable Finder state")
        (self.corpus / "unknown.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "membership_changed"):
            s.verify_audited_content(audit, self.corpus)

    def test_reused_audit_rejects_pixel_label_manifest_and_auditor_changes(self):
        audit = self.audit()
        for name in ("one.png", "one.json", "manifest.json", "capture-ledger.json"):
            p = self.corpus / name
            original = p.read_bytes()
            p.write_bytes(b"changed")
            with self.assertRaises(ValueError):
                s.verify_audited_content(audit, self.corpus)
            p.write_bytes(original)
        changed = copy.deepcopy(audit)
        changed["validatorSHA256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "identity_changed"):
            s.verify_audited_content(changed, self.corpus)

    def test_other_failed_audits_and_false_membership_never_seal(self):
        audit = self.audit()
        for error in ({"error": "duplicate_decoded_pixels"},
                      {"error": "unindexed_members", "members": ["unknown.png"]}):
            changed = {**audit, "errors": [error]}
            with self.assertRaisesRegex(ValueError, "non_auxiliary"):
                s.verify_audited_content(changed, self.corpus)
        with self.assertRaisesRegex(ValueError, "invalid_audited_membership"):
            s.verify_audited_content({**audit, "manifestEntries": 2}, self.corpus)

    def test_excluded_name_does_not_hide_symlink(self):
        (self.corpus / ".DS_Store").symlink_to(self.corpus / "one.png")
        with self.assertRaisesRegex(ValueError, "symlink"):
            s.verify_audited_content(self.audit(), self.corpus)


if __name__ == "__main__":
    unittest.main()
