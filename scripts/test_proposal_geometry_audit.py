import copy
import unittest
from proposal_geometry_audit import audit

class GeometryTests(unittest.TestCase):
    def report(self):
        arm=dict(candidates=[dict(box=[0,0,10,10])],models={m:dict(scores=[.9],outcome='correct') for m in ('baseline','candidate')})
        return dict(version='detector-focus-pilot-v1',rows=[dict(id='a',group='g',profile='standard',noFocus=False,
            arms={'known-box':copy.deepcopy(arm),'detector':copy.deepcopy(arm)})])
    def test_identity_and_size(self):
        r=self.report()
        self.assertEqual(audit(r)['matchedControls'],1)
        r['rows'][0]['arms']['detector']['candidates'][0]['box']=[-1,0,12,10]
        self.assertEqual(audit(r)['rows'][0]['controls'][0]['match']['widthRatio'],1.2)
    def test_missing_and_ambiguous(self):
        r=self.report(); arm=r['rows'][0]['arms']['detector']; arm['candidates']=[]
        for m in arm['models'].values(): m['scores']=[]
        self.assertEqual(audit(r)['missingControls'],1)
        r=self.report(); arm=r['rows'][0]['arms']['known-box']; arm['candidates']*=2
        for m in arm['models'].values(): m['scores']*=2
        self.assertEqual(audit(r)['rows'][0]['ambiguousMatches'],[0])
    def test_invalid(self):
        r=self.report(); r['rows']*=2
        with self.assertRaises(Exception): audit(r)
        r=self.report(); r['rows'][0]['arms']['detector']['models']['candidate']['scores']=[float('nan')]
        with self.assertRaises(Exception): audit(r)
