import copy
import unittest
from reference_diversity44 import summarize


def frame(fid, role, size, pixel):
    return dict(id=fid, sourcePairID='pair', sourceRole='calibration', evidenceKind='appearance',
                pixelSHA256=pixel, size=[100,100],
                recipe=dict(appearance=dict(referencePack=dict(screen='stingray_catalog'))),
                proposals=[dict(sourceElementID='ref-1', state=role, bounds=[10,10,size,size])])


class DiversityTests(unittest.TestCase):
    def batch(self):
        return dict(frames=[frame('a','unfocused',20,'a'),frame('b','focused',22,'b')],
                    records=[dict(disposition='producer_excluded',reason='partially_clipped_bounds')])

    def test_growth_not_erased_by_resize(self):
        result=summarize(self.batch())
        self.assertAlmostEqual(result['growth']['stingray_catalog']['medianAreaRatio'],1.21)
        self.assertEqual(result['commonControlPairs'],{'appearance':1})
        self.assertEqual(result['excludedObservations'],{'partially_clipped_bounds':1})

    def test_no_role_reassignment(self):
        batch=self.batch();before=copy.deepcopy(batch);result=summarize(batch)
        self.assertEqual(batch,before)
        self.assertEqual(result['roleCounts'],{'calibration':2})
        self.assertEqual(len(result['missingRequiredNativeFamilies']),3)

    def test_duplicates_remain_grouped(self):
        batch=self.batch();batch['frames'][1]['pixelSHA256']='a'
        result=summarize(batch)
        self.assertEqual(result['uniquePixels'],1)
        self.assertEqual(result['duplicateGroups'],[['a','b']])

    def test_incomplete_pair_fails(self):
        batch=self.batch();batch['frames'].pop()
        with self.assertRaisesRegex(ValueError,'pair_membership'):summarize(batch)

    def test_unchanged_not_fabricated_as_growth(self):
        batch=self.batch();batch['frames'][0]['proposals'][0]['state']='focused'
        self.assertEqual(summarize(batch)['growth'],{})


if __name__=='__main__':unittest.main()
