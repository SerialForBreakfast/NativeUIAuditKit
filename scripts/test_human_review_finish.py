"""Generated offline fixtures for batch confirmation, never real human labels."""
import copy
import unittest
from unittest.mock import patch

import human_annotation_review as h
import human_review_finish as bulk
import test_human_annotation_review as fixtures


class FinishReviewTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.ReviewTests()
        self.f.setUp()
        self.batch = self.f.imported()
        self.path = self.f.batch / "batch.json"
        self.output = self.f.root / "bulk"

    def tearDown(self):
        self.f.tearDown()

    def editor(self, n=0):
        return self.f.batch / "editor" / (self.batch["frames"][n]["editorStem"]+".json")

    def change(self, fn, n=0):
        path = self.editor(n)
        doc = h.read(path)
        fn(doc)
        self.f.dump(path, doc)

    def apply(self, plan=None, **kwargs):
        return bulk.apply_preview(plan or bulk.preview(self.path), self.output,
                                  reviewer="generated-unit-fixture", attested=True, **kwargs)

    def test_readonly_preview_then_real_finish_and_backup(self):
        before = {self.editor(n): self.editor(n).read_bytes() for n in range(2)}
        raw = {p: h.sha(p) for p in (self.f.batch / "raw").iterdir()}
        plan = bulk.preview(self.path)
        self.assertTrue(all(r["ready"] for r in plan["frames"]))
        self.assertEqual(before, {p: p.read_bytes() for p in before})
        result = self.apply(plan)
        self.assertEqual(result["frameCounts"], {"reviewed": 2})
        self.assertFalse(result["trainingEligible"])
        revision = h.read(self.output / "revision/revision.json")
        self.assertEqual(revision["pairs"][0]["disposition"], "reviewed")
        for path, data in before.items():
            self.assertEqual((self.output / "before" / path.name).read_bytes(), data)
            doc = h.read(path)
            self.assertTrue(all(doc["flags"].values()))
            self.assertTrue(doc["shapes"][0]["flags"]["confirmed"])
        self.assertEqual(raw, {p: h.sha(p) for p in raw})

    def test_binary_default_preview_is_readonly_then_explicitly_committed(self):
        self.change(lambda d: d["shapes"][0]["flags"].update(focused=False))
        before = self.editor().read_bytes()
        plan = bulk.preview(self.path)
        self.assertTrue(plan['frames'][0]['ready'])
        self.assertEqual(before, self.editor().read_bytes())
        self.assertTrue(plan['frames'][0]['document']['shapes'][0]['flags']['unfocused'])
        self.assertEqual(self.apply(plan)["frameCounts"], {"reviewed": 2})
        flags = h.read(self.editor())['shapes'][0]['flags']
        self.assertFalse(flags['focused']); self.assertTrue(flags['unfocused'])
        self.assertEqual((self.output/'before'/self.editor().name).read_bytes(), before)

    def test_allocate_new_id_preserve_all_geometry_and_states(self):
        def append(doc):
            new = copy.deepcopy(doc["shapes"][0])
            new.update(group_id=None, description="manually drawn")
            new["flags"].update(focused=False, unfocused=True)
            doc["shapes"].append(new)
        self.change(append)
        before = h.read(self.editor())
        plan = bulk.preview(self.path)
        self.assertEqual(plan["frames"][0]["assignedIDs"], [{"box":2, "groupID":2}])
        self.apply(plan)
        after = h.read(self.editor())
        for a, b in zip(before["shapes"], after["shapes"]):
            self.assertEqual(a["points"], b["points"])
            self.assertEqual(a["label"], b["label"])
            self.assertEqual(a["flags"]["focused"], b["flags"]["focused"])
        self.assertEqual(after["shapes"][1]["description"], "manually drawn")

    def test_missing_original_identity_not_invented(self):
        self.change(lambda d: d["shapes"][0].update(group_id=None))
        row = bulk.preview(self.path)["frames"][0]
        self.assertFalse(row["ready"])
        self.assertIn("missing_original_control_id", row["issues"][0])

    def test_invalid_annotations_block_without_repair(self):
        original = h.read(self.editor())
        cases = [lambda d: d["shapes"][0]["flags"].update(unfocused=True),
                 lambda d: d["shapes"][0]["flags"].update(flagged=True),
                 lambda d: d["shapes"][0]["flags"].update(focused="yes"),
                 lambda d: d["shapes"][0].update(shape_type="polygon"),
                 lambda d: d["shapes"][0].update(points=[[0, 0], [1000, 1000]]),
                 lambda d: d["shapes"][0].update(label="not-a-class"),
                 lambda d: d["shapes"].append(copy.deepcopy(d["shapes"][0])),
                 lambda d: d["nuiak"].update(frameID="wrong")]
        for fn in cases:
            with self.subTest(case=fn):
                doc = copy.deepcopy(original)
                fn(doc)
                self.f.dump(self.editor(), doc)
                before = self.editor().read_bytes()
                self.assertFalse(bulk.preview(self.path)["frames"][0]["ready"])
                self.assertEqual(before, self.editor().read_bytes())

    def test_stale_preview_rejected_before_writes(self):
        plan = bulk.preview(self.path)
        self.change(lambda d: d["shapes"][0].update(description="newer edit"), n=1)
        with self.assertRaisesRegex(ValueError, "stale"):
            self.apply(plan)
        self.assertFalse(self.output.exists())

    def test_modified_preview_rejected(self):
        plan = bulk.preview(self.path)
        plan["frames"][0]["document"]["shapes"][0]["label"] = "label"
        with self.assertRaisesRegex(ValueError, "stale"):
            self.apply(plan)

    def test_explicit_consent_and_reviewer_required(self):
        plan = bulk.preview(self.path)
        for name, attested in [("reviewer", False), (" ", True)]:
            with self.assertRaises(ValueError):
                bulk.apply_preview(plan, self.output, reviewer=name, attested=attested)
        self.assertFalse(self.output.exists())

    def test_software_test_remains_blocked(self):
        self.assertEqual(self.apply(reviewer_kind="software-test")["frameCounts"], {"blocked": 2})

    def test_no_ready_frames(self):
        for n in range(2):
            self.change(lambda d: d["shapes"][0]["flags"].update(flagged=True), n)
        with self.assertRaisesRegex(ValueError, "no_ready_frames"):
            self.apply()

    def test_corrupt_json_and_working_pixels_remain_exceptions(self):
        self.editor().write_text("{")
        self.assertFalse(bulk.preview(self.path)["frames"][0]["ready"])
        self.editor(1).with_suffix(".png").write_bytes(b"broken")
        self.assertFalse(bulk.preview(self.path)["frames"][1]["ready"])

    def test_missing_membership_is_global_block(self):
        self.editor().rename(self.editor().with_suffix(".absent"))
        with self.assertRaisesRegex(ValueError, "membership"):
            bulk.preview(self.path)

    def test_io_failure_preserves_exact_backups_and_partial_accounting(self):
        before = {self.editor(n): self.editor(n).read_bytes() for n in range(2)}
        replace = bulk.os.replace
        calls = []
        def fail_second(source, dest):
            calls.append(dest)
            if len(calls) == 2:
                raise OSError("injected storage failure")
            replace(source, dest)
        with patch.object(bulk.os, "replace", side_effect=fail_second):
            with self.assertRaisesRegex(OSError, "storage failure"):
                self.apply()
        self.assertEqual(h.read(self.output / "failure.json")["appliedFrames"], ["frame-0"])
        for path, data in before.items():
            self.assertEqual((self.output / "before" / path.name).read_bytes(), data)
        self.assertEqual(self.editor(1).read_bytes(), before[self.editor(1)])
        self.assertFalse((self.output / "receipt.json").exists())


if __name__ == "__main__":
    unittest.main()
