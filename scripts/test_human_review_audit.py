"""Generated-fixture audit/correction integration; no models or live data edits."""
import copy
import json
import subprocess
import sys
import unittest

import human_annotation_review as h
import human_review_audit as audit
import test_human_annotation_review as fixtures


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.ReviewTests()
        self.f.setUp()
        self.batch = self.f.imported()
        self.f.annotate()
        self.f.finish()
        self.revision = self.f.root / "revision/revision.json"
        h.crop_qa(self.f.batch / "batch.json", self.f.root / "crops", self.revision)
        self.crops = self.f.root / "crops/crop-qa.json"

    def tearDown(self):
        self.f.tearDown()

    def reseal(self, path, doc):
        doc.pop("seal", None)
        doc["seal"] = h.digest(doc)
        self.f.dump(path, doc)

    def test_deterministic_membership_complete_accounting_and_preservation(self):
        before = {p: h.sha(p) for p in self.f.root.rglob("*") if p.is_file()}
        a = audit.audit(self.revision, self.crops)
        b = audit.audit(self.revision, self.crops)
        self.assertEqual(a, b)
        self.assertEqual(a["counts"]["controls"], 2)
        self.assertEqual(a["randomQueue"]["strata"][0]["denominator"], 2)
        self.assertEqual(a["coverage"]["candidateCoverage"], "unknown")
        self.assertFalse(a["trainingEligible"])
        self.assertEqual(before, {p: h.sha(p) for p in before})

    def test_crop_missing_changed_and_invalid_membership(self):
        original = h.read(self.crops)
        for mutation in (lambda d: d["crops"].pop(), lambda d: d["crops"].append(d["crops"][0]),
                         lambda d: d.update(completed=999), lambda d: d.update(preprocessing={})):
            with self.subTest(mutation=mutation):
                doc = copy.deepcopy(original)
                mutation(doc)
                self.reseal(self.crops, doc)
                with self.assertRaises(ValueError):
                    audit.audit(self.revision, self.crops)
        self.reseal(self.crops, original)
        path = h.checked(h.ROOT, original["crops"][0]["crop"])
        path.write_bytes(b"corrupt")
        with self.assertRaises(ValueError):
            audit.audit(self.revision, self.crops)

    def test_missing_image_writes_failure_not_partial_audit(self):
        path = h.checked(h.ROOT, self.batch["frames"][0]["image"])
        path.rename(path.with_suffix(".absent"))
        output = self.f.root / "failed-audit"
        with self.assertRaises(ValueError):
            audit.run(self.revision, self.crops, output)
        self.assertFalse((output / "audit.json").exists())
        self.assertFalse(h.read(output / "failure.json")["completed"])

    def test_snapshot_hash_and_identity_fail_closed(self):
        doc = h.read(self.revision)
        path = h.checked(h.ROOT, doc["editorSnapshots"][0])
        snapshot = h.read(path)
        snapshot["nuiak"]["frameID"] = "wrong"
        self.f.dump(path, snapshot)
        with self.assertRaises(ValueError):
            audit.audit(self.revision, self.crops)

    def test_semantic_revision_tampering_rejected_even_resealed(self):
        doc = h.read(self.revision)
        doc["frames"][0]["controls"][0]["bounds"][0] += 1
        self.reseal(self.revision, doc)
        crop = h.read(self.crops)
        crop["revision"] = h.ref(self.revision)
        self.reseal(self.crops, crop)
        with self.assertRaisesRegex(ValueError, "snapshot"):
            audit.audit(self.revision, self.crops)

    def test_final_challenge_role_rejected(self):
        doc = h.read(self.revision)
        doc["partition"] = "test"
        self.reseal(self.revision, doc)
        with self.assertRaisesRegex(ValueError, "diagnostic_only"):
            audit.audit(self.revision, self.crops)

    def test_exact_crop_conflict_is_not_independent_evidence(self):
        doc = h.read(self.crops)
        first, second = [h.checked(h.ROOT, r["crop"]) for r in doc["crops"]]
        second.write_bytes(first.read_bytes())
        doc["crops"][1]["crop"] = h.ref(second)
        self.reseal(self.crops, doc)
        report = audit.audit(self.revision, self.crops)
        self.assertEqual(report["counts"]["distinctCropPixels"], 1)
        self.assertTrue(any(i["kind"] == "duplicate_crop_label_conflict" and i["severity"] == "hard" for i in report["issues"]))

    def test_wrong_revision_and_pair_membership_rejected(self):
        doc = h.read(self.revision)
        doc["pairs"][0]["frames"] = ["frame-0", "missing"]
        self.reseal(self.revision, doc)
        with self.assertRaisesRegex(ValueError, "wrong_crop_revision"):
            audit.audit(self.revision, self.crops)
        crop = h.read(self.crops)
        crop["revision"] = h.ref(self.revision)
        self.reseal(self.crops, crop)
        with self.assertRaisesRegex(ValueError, "pair_binding"):
            audit.audit(self.revision, self.crops)

    def test_cli_queue_correction_new_revision_revalidation(self):
        path = self.f.batch / "editor" / (self.batch["frames"][0]["editorStem"]+".json")
        doc = h.read(path)
        doc["shapes"][0]["flags"]["focused"] = False
        self.f.dump(path, doc)
        pending = self.f.root / "pending"
        h.finish(self.f.batch / "batch.json", pending, reviewer="generated-fixture", reference="test",
                 reviewer_kind="human", confirm_batch=True)
        pending_crops = self.f.root / "pending-crops"
        h.crop_qa(self.f.batch / "batch.json", pending_crops, pending / "revision.json")
        output = self.f.root / "queue"
        result = subprocess.run([sys.executable, str(h.ROOT / "scripts/human_review_audit.py"),
                                 str(pending / "revision.json"), str(pending_crops / "crop-qa.json"), str(output)],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = h.read(output / "audit.json")
        self.assertTrue(any(i["kind"] == "annotation_pending" for i in report["issues"]))
        self.assertIn("--frame frame-0", (output / "review.html").read_text())
        frozen_hash = h.sha(pending / "revision.json")
        doc["shapes"][0]["flags"]["focused"] = True
        self.f.dump(path, doc)
        corrected = self.f.root / "corrected"
        h.finish(self.f.batch / "batch.json", corrected, reviewer="generated-fixture", reference="corrected test",
                 reviewer_kind="human", confirm_batch=True)
        h.crop_qa(self.f.batch / "batch.json", self.f.root / "corrected-crops", corrected / "revision.json")
        report = audit.audit(corrected / "revision.json", self.f.root / "corrected-crops/crop-qa.json")
        self.assertFalse(any(i["kind"] in ("annotation_pending", "pair_pending") for i in report["issues"]))
        self.assertEqual(frozen_hash, h.sha(pending / "revision.json"))


if __name__ == "__main__":
    unittest.main()
