"""Test proposal comparisons without treating agreement as a label."""
import copy
from pathlib import Path
import unittest
import report_hcf334 as r

B=dict(x=1,y=1,width=10,height=10)


class ComparisonTests(unittest.TestCase):
    def test_overlap(self):
        self.assertEqual(r.iou(B,B),1)
        self.assertEqual(r.iou(B,dict(B,x=30)),0)
        with self.assertRaises(ValueError):r.iou(B,dict(B,width=-1))

    def test_all_decisions(self):
        e=dict(elementType='collectionItem',boundingBoxPixels=B,state=dict(isFocused=True,focusScore=.9))
        c=dict(bounds=B)
        for elements,candidates,expected in [([e],[c],'agree'),([e],[dict(bounds=dict(B,x=30))],'disagree'),
            ([e],[],'model_only'),([],[c],'rule_only'),([],[],'both_abstain'),
            ([e,e],[c],'multiple_model_focus'),([e],[c,c],'ambiguous_rules')]:
            with self.subTest(expected=expected):self.assertEqual(r.compare(elements,candidates)['decision'],expected)

    def test_no_model_decision_is_not_unfocused(self):
        e=dict(elementType='collectionItem',boundingBoxPixels=B,state={})
        d=r.compare([e],[dict(bounds=B)])
        self.assertEqual(d['decision'],'rule_only');self.assertEqual(d['bestDetectorOverlap'],1)

    def test_missing_duplicate_and_changed_results(self):
        root=Path('/project')
        manifest=dict(frames=[dict(file='a.png',sha256='a',width=20,height=20)])
        row=dict(input='/project/a.png',inputSHA256='a',width=20,height=20,
            configuration=dict(minConfidence=.25,ocr=False,platform='tvOS',strict=False),
            runtime=dict(result=dict(focusExecution=dict(backend='coreML',modelScoringComplete=True,failedPredictions=0))))
        doc=dict(schemaVersion=1,failed=0,degraded=0,count=1,results=[row])
        self.assertEqual(len(r.validate_scans(doc,manifest,root)),1)
        for field,value in [('inputSHA256','b'),('width',10),('input','/project/wrong.png')]:
            bad=copy.deepcopy(doc);bad['results'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):r.validate_scans(bad,manifest,root)
        bad=copy.deepcopy(doc);bad.update(count=0,results=[])
        with self.assertRaises(ValueError):r.validate_scans(bad,manifest,root)
        bad=copy.deepcopy(doc);bad.update(count=2,results=[row,row])
        duplicate_manifest=dict(frames=manifest['frames']*2)
        with self.assertRaisesRegex(ValueError,'duplicate_scan'):r.validate_scans(bad,duplicate_manifest,root)


if __name__=='__main__':unittest.main()
