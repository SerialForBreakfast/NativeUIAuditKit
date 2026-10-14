"""Test duplicate handling without capture or model execution."""
import copy
import unittest
from capture_duplicates374 import groups_report, vision_pairs, distance_report


class DuplicateTests(unittest.TestCase):
    def row(self,ident='a'):
        return dict(id=ident,role='train',group='scene',profile='hcf',label=0,focus='item-0',
                    boxes={'item-0':[0,0,20,20]},pixel='same')

    def test_preserve_events(self):
        rows=[self.row(),self.row('b')]
        report=groups_report(rows,lambda r:r['pixel'],True)
        self.assertEqual(report['extraPixelCopies'],1)
        self.assertEqual(report['hardConflicts'],[])
        self.assertFalse(report['trainingApproved'])
        self.assertEqual(len(rows),2)

    def test_conflicting_labels(self):
        a,b=self.row(),self.row('b');b['label']=1
        self.assertEqual(len(groups_report([a,b],lambda r:r['pixel'],True)['hardConflicts']),1)

    def test_cross_roles(self):
        a,b=self.row(),self.row('b');b['role']='development'
        self.assertFalse(groups_report([a,b],lambda r:r['pixel'])['metadataIntegrityPassed'])

    def test_geometry_conflicts(self):
        a,b=self.row(),self.row('b');b['boxes']['item-0'][0]=2
        self.assertFalse(groups_report([a,b],lambda r:r['pixel'])['metadataIntegrityPassed'])

    def test_invalid_membership(self):
        for rows in ([],[self.row(),self.row()]):
            with self.assertRaises(ValueError):groups_report(rows,lambda r:r['pixel'])

    def test_pair_controls_and_audit_exclusion(self):
        rows=[dict(id=f'{c}-{p}-{f}',case=c,profile=p,focus=f'item-{f}',role='development')
              for c in range(3) for p in ('standard','hcf') for f in range(4)]
        selected,pairs=vision_pairs(rows)
        self.assertEqual(len(selected),24);self.assertEqual(len(pairs),50)
        measured=[dict(p,distance=0.0) for p in pairs]
        report=distance_report(pairs,measured)
        self.assertFalse(report['automaticExclusion']);self.assertIsNone(report['selectedThreshold'])
        self.assertEqual(report['operatingPoints'][0]['flaggedByKind']['focus-movement'],18)
        rows[0]['role']='audit'
        with self.assertRaisesRegex(ValueError,'development_only'):vision_pairs(rows)

    def test_missing_or_bad_distances(self):
        pair=dict(id='p',before='a',after='b',kind='focus-movement')
        for values in ([],[dict(pair,distance=float('nan'))],[dict(pair,distance=-1)]):
            with self.assertRaises(ValueError):distance_report([pair],values)
        with self.assertRaises(ValueError):distance_report([pair],[dict(pair,after='c',distance=0)])

if __name__=='__main__':unittest.main()
