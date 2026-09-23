"""Retained recipe review contracts: no capture, inference or publication."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import focus_retained_review as subject
from focus_dataset_contract import ROOT, FocusDataError
import test_direct_tvos_resume as fixture


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.f=fixture.ResumeTests(); self.f.setUp(); self.addCleanup(self.f.doCleanups)

    def pair(self,pid,seed,f,u):
        return {"pairID":pid,"seed":seed,
                "focused":{"framePixelSHA256":"frame"+f,"cropPixelSHA256":f},
                "unfocused":{"framePixelSHA256":"frame"+u,"cropPixelSHA256":u}}

    def test_seed_components_and_pair_duplicates(self):
        pairs=[self.pair("a",7,"a","b"),self.pair("b",19,"c","b"),self.pair("c",29,"d","c")]
        result=subject.analyze(pairs)
        self.assertEqual([sorted(g) for g in result["seedComponents"]],[[7,19,29]])
        self.assertEqual(len(result["contradictoryCropGroups"]),1)
        self.assertEqual(result,subject.analyze(pairs))
        pairs.append(self.pair("copy",7,"a","b"))
        self.assertEqual(subject.analyze(pairs)["duplicatePairGroups"],[["a","copy"]])

    def test_shared_raw_frame_is_not_crop_label_conflict(self):
        a=self.pair("a",7,"a","b"); b=self.pair("b",19,"c","d")
        b["unfocused"]["framePixelSHA256"]=a["focused"]["framePixelSHA256"]
        result=subject.analyze([a,b])
        self.assertEqual([sorted(g) for g in result["seedComponents"]],[[7,19]])
        self.assertFalse(result["contradictoryCropGroups"])

    def test_actual_cli_preserves_failed_state_and_no_dataset(self):
        path=self.f.receipt("a",0,42,failed=True,actual_stop=1)
        original=path.read_bytes(); out=self.f.root/"review"
        command=[sys.executable,str(ROOT/"scripts/focus_retained_review.py"),"--receipts",str(path),"--output",str(out)]
        r=subprocess.run(command,capture_output=True,text=True,timeout=40)
        self.assertEqual(r.returncode,0,r.stderr)
        doc=json.loads((out/"review.json").read_text())
        self.assertEqual(doc["accounting"]["retainedPairs"],2)
        self.assertEqual(doc["sources"][0]["state"],"failed")
        self.assertFalse(doc["trainingEligible"]); self.assertFalse(doc["fullPilotComplete"])
        self.assertFalse((out/"direct-capture.json").exists())
        self.assertFalse((out/"focus_dataset_manifest.json").exists())
        self.assertEqual(path.read_bytes(),original)
        self.assertEqual(len(list((out/"crops").glob("*.png"))),4)
        self.assertEqual(subprocess.run(command,capture_output=True,text=True,timeout=40).returncode,2)

    def test_bad_bytes_and_incomplete_sweep_reject_before_render(self):
        path=self.f.receipt("a",0,42,failed=True,actual_stop=1)
        original=json.loads(path.read_text())
        bad=copy.deepcopy(original); bad["recipes"][0]["frames"].pop()
        path.write_text(json.dumps(bad))
        with patch.object(subject,"invoke") as render:
            with self.assertRaises(FocusDataError): subject.review([path],self.f.root/"out")
            render.assert_not_called()
        path.write_text(json.dumps(original))
        (path.parent/original["recipes"][0]["frames"][0]["path"]).write_bytes(b"corrupt")
        with self.assertRaises(FocusDataError): subject.review([path],self.f.root/"out")
        self.assertFalse((self.f.root/"out").exists())

    def test_runtime_mismatch_keeps_incomplete_output_unpublished(self):
        path=self.f.receipt("a",0,42,failed=True,actual_stop=1)
        out=self.f.root/"out"
        with patch.object(subject,"invoke",return_value={"results":[]}):
            with self.assertRaisesRegex(FocusDataError,"membership_mismatch"): subject.review([path],out)
        self.assertFalse((out/"review.json").exists())

    def test_output_symlink_rejected(self):
        alias=self.f.root/"alias"; alias.symlink_to(self.f.root,target_is_directory=True)
        with self.assertRaisesRegex(FocusDataError,"symlink_output"): subject.review([],alias/"new")


if __name__=="__main__": unittest.main()
