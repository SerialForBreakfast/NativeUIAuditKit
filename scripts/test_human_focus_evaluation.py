"""Offline generated fixtures; no real model execution or prior report dependencies."""
import copy
from unittest.mock import patch
import unittest

import human_annotation_review as h
import human_focus_evaluation as e
from focus_dataset_contract import validate_manifest
from focus_surface_evaluation import validate as legacy_validate
import test_human_review_audit as fixtures


class EvaluationTests(unittest.TestCase):
    # Reuse fixture construction, not inherited audit tests.
    def setUp(self):
        fixtures.AuditTests.setUp(self)
        self.report, self.rows = e.admitted(self.revision, self.crops)
        self.runtime = dict(crop=h.read(self.crops)["runtime"], fake="offline-test-only")
        self.patch_runtime = patch.object(e, "runtime", return_value=self.runtime)
        self.patch_runtime.start()
        self.patch_model = patch.object(e, "model_contract", return_value=dict(sha256="fake"))
        self.patch_model.start()
        self.models = dict(shipped=dict(path=".build/fake-not-loaded",sha256="fake"), fdr009=h.ref(self.revision))
        self.roles = []
        for kind in ("training-retention", "reserved", "historical-protected"):
            path = self.f.root/(kind+".json")
            key = "remotesSamples" if kind == "historical-protected" else "samples"
            self.f.dump(path,{key:[dict(id="a",frame=self.report["frames"][0]["image"],
                                       framePixelSHA256=self.report["frames"][0]["pixelSHA256"],
                                       crop=dict(self.rows[0]["crop"],pixelSHA256=self.rows[0]["pixelSHA256"]))]})
            self.roles.append(dict(kind=kind,manifest=h.ref(path)))
        self.approval = self.f.root/"approval.json"
        self.spec = dict(version="human-focus-evaluation-approval-v1",approved=True,maxRuns=1,
                         role=e.ROLE,reviewer="test-only",authorizationReference="generated-test",
                         threshold=.85,trainingApproved=False,promotionApproved=False,
                         revision=h.ref(self.revision),crops=h.ref(self.crops),
                         membership=[r["id"] for r in self.rows],pairs=self.report["pairs"],coverage=self.report["coverage"],
                         models=self.models,roleManifests=self.roles,
                         output=str((self.f.root/"run").relative_to(h.ROOT)))
        self.f.dump(self.approval,self.spec)
        self.protocol = self.f.root/"protocol.json"
        self.doc = e.freeze(self.approval,self.protocol)

    def tearDown(self):
        self.patch_runtime.stop(); self.patch_model.stop()
        fixtures.AuditTests.tearDown(self)

    def test_admission_retains_originals_and_rejects_legacy_consumers(self):
        original = self.revision.read_bytes()
        e.validate(self.doc)
        self.assertEqual(original,self.revision.read_bytes())
        self.assertFalse(self.doc["trainingEligible"])
        self.assertTrue(self.doc["overlap"]["inventories"][0]["matches"])
        with self.assertRaises(ValueError): validate_manifest(self.doc,self.f.root)
        with self.assertRaises(ValueError): legacy_validate(self.doc)

    def test_policy_role_membership_and_runtime_rejected(self):
        for key,value in (("role","final-challenge"),("trainingEligible",True),("completeFrameCandidates",True),
                          ("threshold",.5),("samples",[]),("runtime",{}),("implementation",[])):
            doc = copy.deepcopy(self.doc); doc[key] = value
            doc.pop("seal");doc["seal"]=h.digest(doc)
            with self.subTest(key=key),self.assertRaises(ValueError):e.validate(doc)

    def test_approval_changed_or_unconfirmed_rejected(self):
        for key,value in (("approved",False),("role","train"),("membership",[]),("coverage",{}),("maxRuns",2)):
            bad=copy.deepcopy(self.spec);bad[key]=value
            self.f.dump(self.approval,bad)
            with self.subTest(key=key),self.assertRaises(ValueError):e.freeze(self.approval,self.f.root/(key+".json"))

    def test_missing_or_corrupt_crop_and_wrong_role_inventory(self):
        path=e.check(self.rows[0]["crop"]);path.write_bytes(b"not png")
        with self.assertRaises(ValueError):e.validate(self.doc)
        with self.assertRaises(ValueError):e.role_audit(self.report,self.roles[:1])

    def test_scores_missing_duplicate_invalid_ties_and_pairs(self):
        good=[dict(id=r["id"],probability=.85) for r in self.rows]
        result=e.metrics(self.rows,good,self.report["pairs"])
        self.assertFalse(result["pairs"][0]["bothCorrect"])
        self.assertEqual(result["pairs"][0]["delta"],0)
        self.assertEqual(result["completeFrameSelection"]["status"],"unavailable")
        for bad in (good[:1],good+good, [dict(good[0],probability=float('nan')),good[1]],
                    [dict(good[0],probability=True),good[1]], [dict(good[0],probability=1.1),good[1]]):
            with self.assertRaises(ValueError):e.metrics(self.rows,bad,self.report["pairs"])
        with self.assertRaises(ValueError):e.metrics(self.rows,good,[dict(controlID="missing",frames=["x","y"])])

    def test_no_positives_and_no_positive_predictions_are_unavailable(self):
        rows=[self.rows[1]]
        m=e.metrics(rows,[dict(id=rows[0]["id"],probability=0)],[])["full"]["groups"]["overall"]
        self.assertIsNone(m["precision"]);self.assertIsNone(m["recall"])

    def test_full_caller_failures_accounted_and_no_retry(self):
        def fake(name,doc,predictions,receipts):
            predictions.append(dict(id=doc["samples"][0]["id"],probability=.9))
            raise RuntimeError("injected failure")
        with patch.object(e,"infer",side_effect=fake):
            result=e.run(self.protocol,self.f.root/"run")
        self.assertFalse(result["completed"])
        for r in result["results"].values():
            self.assertEqual(r["scored"],1);self.assertEqual(len(r["unscored"]),1);self.assertIsNone(r["metrics"])
        self.assertTrue(self.approval.with_suffix(".started.json").exists())
        with self.assertRaises(ValueError):e.run(self.protocol,self.f.root/"other-run")

    def test_runner_nonfinite_scores_leave_serializable_failure_receipts(self):
        def fake(name,doc,predictions,receipts):
            predictions.extend(dict(id=r["id"],probability=float('nan')) for r in doc["samples"])
        with patch.object(e,"infer",side_effect=fake):
            result=e.run(self.protocol,self.f.root/"run")
        self.assertFalse(result["completed"])
        for r in result["results"].values():
            self.assertEqual(len(r["invalidPredictions"]),2)
            self.assertEqual(len(r["unscored"]),2)
            self.assertEqual(r["scored"],0)

    def test_full_caller_and_deterministic_render_no_model_on_render(self):
        def fake(name,doc,predictions,receipts):
            predictions.extend(dict(id=r["id"],probability=0) for r in doc["samples"])
        with patch.object(e,"infer",side_effect=fake):
            result=e.run(self.protocol,self.f.root/"run")
        self.assertTrue(result["completed"])
        with patch.object(e,"infer",side_effect=AssertionError("render must not infer")), \
             patch.object(e,"runtime",side_effect=AssertionError("no inference runtime")), \
             patch.object(e,"role_audit",side_effect=AssertionError("no protected traversal")):
            a=e.render(self.protocol,self.f.root/"run/comparison.json",self.f.root/"sheets1")
            b=e.render(self.protocol,self.f.root/"run/comparison.json",self.f.root/"sheets2")
        self.assertEqual([(r["sample"],r["sheet"]["sha256"]) for r in a],[(r["sample"],r["sheet"]["sha256"]) for r in b])


if __name__ == "__main__":unittest.main()
