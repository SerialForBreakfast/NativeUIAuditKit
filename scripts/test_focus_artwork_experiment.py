import copy
import unittest
from unittest.mock import patch

import focus_artwork_experiment as a


class ArtworkTests(unittest.TestCase):
    def data(self):
        rows=[dict(id=str(i), reasons=[],sourceElementID='catalog-poster-0',
                   producerSplit='calibration',crop=dict(pixelSHA256=str(i)),label=i%2,
                   sourceID=str(i//2),recipeSHA256='recipe') for i in range(12)]
        return dict(candidates=rows,recipes={'recipe':{}},conditionalOwnedComparison={
            'comparison':{'proposedAdditionIDs':[r['id'] for r in rows]}})

    def test_only_exact_twelve_preserve_original_role(self):
        rows=a.admitted_rows(self.data())
        self.assertEqual(len(rows),12)
        self.assertTrue(all(r['split']=='train' and r['producerSplit']=='calibration' for r in rows))
        self.assertEqual(sum(r['label'] for r in rows),6)

    def test_incomplete_duplicate_protected_and_blocked_fail(self):
        for change in ('count','duplicate','blocked','role','target'):
            d=self.data()
            if change=='count':d['conditionalOwnedComparison']['comparison']['proposedAdditionIDs'].pop()
            if change=='duplicate':d['candidates'][1]['crop']['pixelSHA256']='0'
            if change=='blocked':d['candidates'][0]['reasons']=['protected_pixel']
            if change=='role':d['candidates'][0]['producerSplit']='test'
            if change=='target':d['candidates'][0]['sourceElementID']='other'
            with self.subTest(change=change),self.assertRaises(ValueError):a.admitted_rows(d)

    def test_adapter_uses_identical_detail_model_and_propagates_state(self):
        def prepare(report,*args):
            self.assertEqual(report['arm'],'visual-local-partial')
            report.update(initialTailSHA256='tail',initialBNSHA256='bn')
            return ('model','train','val')
        for arm in a.ARMS:
            report=dict(arm=arm)
            with patch.object(a.visual,'prepare_features',side_effect=prepare):
                self.assertEqual(a.prepare_features(report,[],[],'cpu',None),('model','train','val'))
            self.assertEqual(report,dict(arm=arm,initialTailSHA256='tail',initialBNSHA256='bn'))

    def test_approval_binds_arm_and_protocol(self):
        p=dict(protocolSHA256='sha',authority={'path':'decision'},arm='artwork-control-partial')
        one=a.approval(p);two=a.approval(dict(p,arm='artwork-added-partial'))
        self.assertNotEqual(one,two)
        self.assertEqual(one['name'],'fdr031-artwork-control')


if __name__=='__main__':unittest.main()
