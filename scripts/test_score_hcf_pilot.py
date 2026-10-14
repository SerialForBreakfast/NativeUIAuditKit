"""Test the HCF pilot scorer on synthetic inputs; these values make no accuracy claim."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import score_hcf_pilot as s

BOX = dict(x=100, y=100, width=200, height=100)
FAR = dict(x=1000, y=600, width=200, height=100)


def frame(fid, state="focused", family="fam-a", scene="s1", role="development", sha=None, profile="high_contrast"):
    focus = {"state": state}
    if state == "focused":
        focus["box"] = dict(BOX)
    return dict(frame_id=fid, sha256=sha or (fid * 64)[:64], width=1920, height=1080,
                profile=profile, family=family, scene=scene, role=role, focus=focus)


def truth(*frames):
    return {"version": s.TRUTH_VERSION, "frames": list(frames)}


def method(name, truth_doc, decisions, latency=None):
    rows = []
    for f in truth_doc["frames"]:
        d = decisions[f["frame_id"]]
        row = dict(frame_id=f["frame_id"], sha256=f["sha256"],
                   decision="abstain" if d is None else "select")
        if d is not None:
            row["box"] = dict(d)
        if latency is not None:
            row["latency_ms"] = latency[f["frame_id"]]
        rows.append(row)
    return {"version": s.PREDICTION_VERSION, "method": name, "frames": rows}


class OutcomeTests(unittest.TestCase):
    def test_every_outcome_row(self):
        t = truth(frame("a"), frame("b"), frame("c"), frame("d", "no_focus"), frame("e", "no_focus"),
                  frame("f", "uncertain"))
        m = method("rules", t, dict(a=BOX, b=FAR, c=None, d=None, e=BOX, f=BOX))
        r = s.score(t, [m], resamples=50)
        all_ = r["methods"]["rules"]["all"]
        self.assertEqual(all_["counts"], dict(correct=1, wrong_focus=2, miss=1, correct_abstention=1))
        self.assertEqual(r["uncertainExcluded"], 1)
        self.assertEqual(all_["scored"], 5)
        self.assertEqual(all_["focused"], 3)
        self.assertEqual(all_["noFocus"], 2)
        self.assertAlmostEqual(all_["wrongFocusRate"], 2 / 5)
        self.assertAlmostEqual(all_["missRate"], 1 / 3)
        self.assertAlmostEqual(all_["noFocusSpecificity"], 1 / 2)
        self.assertAlmostEqual(all_["coverage"], 3 / 5)
        self.assertAlmostEqual(all_["abstentionRate"], 2 / 5)
        self.assertAlmostEqual(all_["meanCorrectIoU"], 1.0)

    def test_iou_threshold_boundary(self):
        t = truth(frame("a"), frame("b"))
        half = dict(x=100, y=100, width=100, height=100)            # IoU exactly 0.5
        below = dict(x=100, y=100, width=99, height=100)            # IoU 0.495
        r = s.score(t, [method("m", t, dict(a=half, b=below))], resamples=10)
        self.assertEqual(r["methods"]["m"]["all"]["counts"]["correct"], 1)
        self.assertEqual(r["methods"]["m"]["all"]["counts"]["wrong_focus"], 1)

    def test_reserved_role_is_separate(self):
        t = truth(frame("a"), frame("b", role="reserved", family="fam-r"))
        r = s.score(t, [method("m", t, dict(a=BOX, b=FAR))], resamples=10)
        self.assertEqual(r["methods"]["m"]["development"]["counts"]["correct"], 1)
        self.assertEqual(r["methods"]["m"]["reserved"]["counts"]["wrong_focus"], 1)
        self.assertEqual(r["methods"]["m"]["all"]["scored"], 2)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.t = truth(frame("a"), frame("b", "no_focus"))
        self.m = method("m", self.t, dict(a=BOX, b=None))

    def bad(self, code, t=None, m=None):
        with self.assertRaisesRegex(ValueError, code):
            s.score(t or self.t, [m or self.m], resamples=10)

    def test_membership_and_hash(self):
        m = copy.deepcopy(self.m); m["frames"].pop()
        self.bad("membership_mismatch", m=m)
        m = copy.deepcopy(self.m); m["frames"][0]["sha256"] = "f" * 64
        self.bad("prediction_sha256_mismatch", m=m)

    def test_duplicates_and_versions(self):
        t = copy.deepcopy(self.t); t["frames"].append(copy.deepcopy(t["frames"][0]))
        self.bad("duplicate_truth_frame", t=t)
        m = copy.deepcopy(self.m); m["frames"].append(copy.deepcopy(m["frames"][0]))
        self.bad("duplicate_prediction_frame", m=m)
        self.bad("truth_version", t=dict(self.t, version="v0"))
        self.bad("prediction_version", m=dict(self.m, version="v0"))
        with self.assertRaisesRegex(ValueError, "duplicate_method"):
            s.score(self.t, [self.m, self.m], resamples=10)

    def test_boxes_and_decisions(self):
        for box, code in [(dict(BOX, width=0), "box_no_area"), (dict(BOX, x=1800), "box_outside_image"),
                          (dict(BOX, y=float("nan")), "box_not_finite"), ({"x": 1}, "box_fields")]:
            m = copy.deepcopy(self.m); m["frames"][0]["box"] = box
            with self.subTest(code=code):
                self.bad(code, m=m)
        m = copy.deepcopy(self.m); del m["frames"][0]["box"]
        self.bad("box_fields", m=m)
        m = copy.deepcopy(self.m); m["frames"][1]["box"] = dict(BOX)
        self.bad("abstain_with_box", m=m)
        m = copy.deepcopy(self.m); m["frames"][0]["decision"] = "maybe"
        self.bad("prediction_decision", m=m)
        t = copy.deepcopy(self.t); t["frames"][1]["focus"]["box"] = dict(BOX)
        self.bad("truth_box_without_focus", t=t)
        t = copy.deepcopy(self.t); t["frames"][0]["profile"] = "inverted"
        self.bad("truth_profile", t=t)
        m = copy.deepcopy(self.m); m["frames"][0]["latency_ms"] = -1
        self.bad("latency_invalid", m=m)


class GroupTests(unittest.TestCase):
    def test_repeated_image_in_group_counts_once(self):
        t = truth(frame("a", sha="1" * 64), frame("b", sha="1" * 64), frame("c", sha="1" * 64, scene="s2"))
        r = s.score(t, [method("m", t, dict(a=BOX, b=BOX, c=BOX))], resamples=10)
        self.assertEqual(r["duplicateFramesExcluded"], 1)
        self.assertEqual(r["methods"]["m"]["all"]["scored"], 2)

    def test_interval_resamples_groups_not_frames(self):
        frames = [frame(f"g1-{i}", scene="s1") for i in range(9)] + [frame("g2-0", scene="s2")]
        t = truth(*frames)
        decisions = {f["frame_id"]: BOX for f in frames}
        decisions["g2-0"] = FAR
        interval = s.score(t, [method("m", t, decisions)], resamples=400)["methods"]["m"]["all"][
            "wrongFocusGroupInterval"]
        self.assertEqual(interval["groups"], 2)
        # Resampling 2 groups gives rates 0, 0.1, or 1.0 only.
        self.assertEqual(interval["low"], 0.0)
        self.assertEqual(interval["high"], 1.0)

    def test_interval_is_deterministic(self):
        t = truth(frame("a"), frame("b", scene="s2"), frame("c", scene="s3"))
        m = method("m", t, dict(a=BOX, b=FAR, c=None))
        first = s.score(t, [m], seed=7, resamples=200)
        second = s.score(t, [m], seed=7, resamples=200)
        self.assertEqual(first, second)


class LatencyAndPairTests(unittest.TestCase):
    def test_latency_requires_every_frame(self):
        t = truth(frame("a"), frame("b"), frame("c"))
        full = method("m", t, dict(a=BOX, b=BOX, c=BOX), latency=dict(a=10, b=20, c=30))
        latency = s.score(t, [full], resamples=10)["methods"]["m"]["all"]["latencyMs"]
        self.assertEqual(latency["p50"], 20)
        self.assertAlmostEqual(latency["p95"], 29)
        partial = method("m", t, dict(a=BOX, b=BOX, c=BOX))
        partial["frames"][0]["latency_ms"] = 5
        self.assertIsNone(s.score(t, [partial], resamples=10)["methods"]["m"]["all"]["latencyMs"])

    def test_paired_counts(self):
        t = truth(frame("a"), frame("b"), frame("c", "no_focus"))
        rules = method("rules", t, dict(a=BOX, b=FAR, c=None))
        model = method("model", t, dict(a=BOX, b=BOX, c=BOX))
        pair = s.score(t, [rules, model], resamples=10)["paired"][0]
        self.assertEqual(pair["methods"], ["model", "rules"])
        self.assertEqual((pair["onlyFirstCorrect"], pair["onlySecondCorrect"], pair["bothCorrect"]), (1, 1, 1))


class CommandLineTests(unittest.TestCase):
    def test_cli_writes_once(self):
        t = truth(frame("a"))
        m = method("m", t, dict(a=BOX))
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent.parent / ".build") as d:
            d = Path(d)
            (d / "t.json").write_text(json.dumps(t))
            (d / "m.json").write_text(json.dumps(m))
            cmd = [sys.executable, str(Path(s.__file__)), str(d / "t.json"), str(d / "m.json"),
                   "--output", str(d / "r.json"), "--resamples", "10"]
            subprocess.run(cmd, check=True)
            self.assertEqual(json.loads((d / "r.json").read_text())["version"], s.REPORT_VERSION)
            again = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(again.returncode, 0)
            self.assertIn("output_exists", again.stderr)


if __name__ == "__main__":
    unittest.main()
