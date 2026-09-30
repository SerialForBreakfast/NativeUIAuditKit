"""Offline training-admission checks; no capture or training authority from tests."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import focus_training_extension as e
import focus_mixed_assembly as a
from focus_dataset_contract import ROOT, digest, FocusDataError
import test_focus_appearance_experiment as fixtures


class ExtensionTests(unittest.TestCase):
    save = fixtures.AppearanceTests.save
    row = fixtures.AppearanceTests.row
    complete = fixtures.AppearanceTests.complete

    def setUp(self):
        fixtures.AppearanceTests.setUp(self)
        self.complete()
        protected = {"version":"appearance-protected-evidence-audit-v1", "remotesSamples":[]}
        protected["auditSHA256"] = digest(protected)
        self.spec["protected"] = self.save("protected.json", protected)
        self.base = e.appearance.assemble(self.spec)
        self.base_ref = self.save("base.json", self.base)
        reserved = {"version":"surface-crops-v1", "samples":[]}
        reserved["seal"] = digest(reserved)
        self.input = {"version":e.INPUT_VERSION,"base":self.base_ref,
                      "reservedPixels":self.save("reserved.json", reserved),"additions":[{"id":"new"}]}
        self.sources["new"] = self.new_pair("new")
        self.validate_base = patch.object(e.appearance, "assemble", return_value=self.base)
        self.validate_base.start(); self.addCleanup(self.validate_base.stop)

    def new_pair(self, name):
        rows = [self.row(name, label, "simulatorFixture", "development") for label in (0,1)]
        for r in rows:
            r.update(manifestVersion="1.5", sourceBlockers=["development_only_source_contract"],
                     priorUse="development", intrinsicGroup="seed:100", relatedGroup="new-fixture", recipeSeed=100)
        return rows

    def test_extension_preserves_base_gates_and_membership(self):
        doc = e.assemble(self.input)
        original = {r["id"]:r for r in self.base["samples"]}
        self.assertEqual([r for r in doc["samples"] if r["id"] in original], self.base["samples"])
        for key in ("configuration","selection","warmCheckpoint","readinessBlockers"):
            self.assertEqual(doc[key], self.base[key])
        self.assertEqual(doc["admissionCounts"], {"admitted-training-pair":1})
        self.assertAlmostEqual(doc["sampling"]["sourceMass"]["native"], .5)
        self.assertAlmostEqual(doc["sampling"]["sourceMass"]["fixture"], .5)
        self.assertFalse(doc["trainingEligible"])

    def test_exact_duplicate_pair_accounted_without_training_twice(self):
        other = self.new_pair("other")
        for x,y in zip(other,self.sources["new"]): x["crop"] = y["crop"]
        self.sources["other"] = other; self.input["additions"].append({"id":"other"})
        doc=e.assemble(self.input)
        self.assertEqual(doc["admissionCounts"], {"admitted-training-pair":1,"duplicate-pair":1})
        self.assertEqual(len(doc["dispositions"]),2)

    def test_unsupported_unreviewed_or_unapproved_sources_rejected(self):
        for field,value in (("sourceBlockers",["development_only_source_contract","source_training_review_required"]),
                            ("sourceBlockers",["development_only_source_contract","unknown_source_relationships"]),
                            ("sourceBlockers",["test_only_evidence"]),("split","test"),("manifestVersion","1.3"),
                            ("sourceKind","physicalFixture"),("priorUse","untouched")):
            with self.subTest(field=field,value=value):
                rows=self.new_pair("case")
                rows[0][field]=value
                with self.assertRaisesRegex(FocusDataError,"unapproved_or_incompatible"):
                    e.extend(self.base,rows,[])

    def test_reserved_or_conflicting_pairs_excluded_explicitly(self):
        for reason in ("overlap", "conflict"):
            with self.subTest(reason=reason):
                rows=self.new_pair("bad"); good=self.new_pair("good")
                native=next(r for r in self.base["samples"] if r["split"]=="validation")
                reserved=[]
                if reason=="overlap": reserved=[rows[0]["frame"]["pixelSHA256"]]
                else: rows[0]["crop"]=next(r["crop"] for r in self.base["samples"] if r["label"]==1 and r["split"]=="train")
                _,decisions,_=e.extend(self.base,rows+good,[],reserved)
                self.assertEqual(sum(d["disposition"].startswith("excluded-") for d in decisions),1)

    def test_related_groups_cannot_cross_validation(self):
        rows=self.new_pair("leak")
        target=next(r for r in self.base["samples"] if r["split"]=="validation")
        for r in rows: r["relatedGroup"]=target["relatedGroup"]
        with self.assertRaisesRegex(FocusDataError,"cross_partition_lineage"):
            e.extend(self.base,rows,[])

    def test_incomplete_and_duplicate_ids_rejected(self):
        with self.assertRaisesRegex(FocusDataError,"incomplete_pair"):
            e.extend(self.base,self.sources["new"][:1],[])
        with self.assertRaisesRegex(FocusDataError,"duplicate_sample"):
            e.extend(self.base,self.sources["new"]*2,[])

    def test_protected_challenge_lineage_rejected_without_reading_images(self):
        protected=self.new_pair('protected-only-metadata')
        for r in protected:
            r.update(split='challenge',use='final-challenge')
        rows=self.new_pair('new-training')
        for r in rows:r['relatedGroup']=protected[0]['relatedGroup']
        # extend is metadata-only; deliberately impossible image paths prove that
        # source relationship protection needs no challenge rendering or scoring.
        for r in protected:
            r['frame']['path']='missing-protected-frame.png'
            r['crop']['path']='missing-protected-crop.png'
        with self.assertRaisesRegex(FocusDataError,'cross_partition_lineage'):
            e.extend(self.base,rows,protected)

    def test_empty_new_support_and_changed_base_rejected(self):
        with self.assertRaisesRegex(FocusDataError,"no_new_training_pairs"):
            e.extend(self.base,[],[])
        with patch.object(e.appearance,"assemble",return_value={}):
            with self.assertRaisesRegex(FocusDataError,"changed_base_candidate"): e.assemble(self.input)

    def test_actual_assembly_dispatch_and_preflight_cannot_bypass_gates(self):
        self.base["readinessBlockers"]=["independent_coverage_missing"]
        self.base["protocolSHA256"]=digest({k:v for k,v in self.base.items() if k!="protocolSHA256"})
        self.input["base"]=self.save("base-blocked.json",self.base)
        source=self.save("extension-input.json",self.input); out=self.root/"extension"
        with patch.object(sys,"argv",["assembly","--input",str(ROOT/source["path"]),"--output",str(out)]): a.main()
        path=out/"focus_dataset_manifest.json"; doc=json.loads(path.read_text())
        approval=self.save("extension-approval.json",{"version":"focus-training-extension-approval-v1","approved":True,
            "protocolSHA256":doc["protocolSHA256"],"arm":"warm-stretch","runName":self.root.name,
            "reviewer":"test-only","reviewReference":"synthetic-no-execution"})
        from focus_learning_experiment import load_protocol
        report,rows=load_protocol(path,"warm-stretch",self.root.name,ROOT/approval["path"])
        self.assertFalse(report["launchEligible"])
        self.assertEqual(report["blockers"],["independent_coverage_missing"])
        self.assertFalse(any(r["use"]=="final-challenge" for r in rows))
        self.assertFalse(report["executionAuthorized"])
        self.assertFalse((ROOT/"NativeUITrainer/focus_ring_runs"/self.root.name).exists())

    def test_missing_stale_approval_and_changed_protocol_rejected(self):
        doc=e.assemble(self.input); ref=self.save("protocol.json",doc); path=ROOT/ref["path"]
        report,_=e.load_protocol(path,"warm-stretch",self.root.name)
        self.assertIn("missing_experiment_approval",report["blockers"])
        approval=self.save("stale.json",{"version":"focus-training-extension-approval-v1","approved":True,
            "protocolSHA256":"stale","arm":"warm-stretch","runName":self.root.name})
        report,_=e.load_protocol(path,"warm-stretch",self.root.name,ROOT/approval["path"])
        self.assertIn("missing_or_stale_experiment_approval",report["blockers"])
        doc["samples"][0]["label"]=1-doc["samples"][0]["label"]
        path.write_text(json.dumps(doc))
        with self.assertRaisesRegex(FocusDataError,"changed_appearance_contract"):
            e.load_protocol(path,"warm-stretch",self.root.name)

    def test_reserved_metadata_changes_rejected_without_opening_challenge(self):
        path=ROOT/self.input["reservedPixels"]["path"]
        path.write_text("{}")
        with self.assertRaisesRegex(FocusDataError,"changed_assembly_input"):
            e.assemble(self.input)


if __name__ == "__main__": unittest.main()
