"""Check HCF study preparation without changing Simulator state."""
import unittest
import numpy as np
from hcf361 import design, measure, prototype_decision, union_box, validate_roles


class HCFStudyTests(unittest.TestCase):
    def test_nested_stages_preserve_roles(self):
        small, large = design(1000), design(5000)
        by_id = {r['id']: r for r in large['groups']}
        self.assertTrue(all(by_id[r['id']] == r for r in small['groups']))
        self.assertEqual(small['totalFrames'], 2720)
        self.assertEqual(small['requestedGroups']['train'], 250)
        self.assertEqual(len({r['id'] for r in small['groups']}), 340)
        self.assertFalse(small['trainingEligible'])
        self.assertFalse(small['finalAuditOpened'])

    def test_region_balance(self):
        rows = [r for r in design(1000)['groups'] if r['role'] == 'train']
        counts = [sum(r['targetRegion'] == i for r in rows) for i in range(9)]
        self.assertLessEqual(max(counts)-min(counts), 1)
        for region in range(9):
            self.assertEqual(len({r['theme'] for r in rows if r['targetRegion'] == region}), 3)

    def test_bad_stage(self):
        for n in (0, -1, 999, 50001):
            with self.assertRaises(ValueError): design(n)

    def test_ancestry(self):
        rows = [dict(id='a', role='train', ancestry=['template1', 'art1']),
                dict(id='b', role='train', ancestry=['art1', 'art2']),
                dict(id='c', role='audit', ancestry=['art2'])]
        with self.assertRaisesRegex(ValueError, 'cross_role'): validate_roles(rows)
        rows[-1]['role'] = 'train'
        self.assertEqual(validate_roles(rows)['rows'], 3)

    def test_missing_ancestry_and_duplicates(self):
        for rows in ([dict(id='a', role='train')],
                     [dict(id='a', role='train', ancestry=['x'])]*2):
            with self.assertRaises(ValueError): validate_roles(rows)

    def test_pixel_measurement(self):
        a = np.zeros((4, 4, 3), dtype=np.uint8); b = a.copy(); b[1, 2] = 255
        self.assertEqual(measure(a, a)['changedPixels'], 0)
        self.assertEqual(measure(a, b)['changedPixels'], 1)
        with self.assertRaises(ValueError): measure(a, b[:2])

    def test_boundary_keeps_growth(self):
        box = union_box([[30, 30, 20, 20], [25, 25, 30, 30]], [100, 100])
        self.assertLess(box[0], 25); self.assertGreater(box[2], 55)
        with self.assertRaises(Exception): union_box([[0, 0, float('nan'), 2]], [100, 100])

    def report(self):
        return dict(eligibleNativeHCF=True, frozenMembership=True, baselineComplete=True,
            retainedSuiteComplete=True, coreMLParity=True, auditFrozen=True,
            cases=100, correct=95, wrong=1, abstained=4,
            baselineCorrect=90, baselineWrong=1, lostPreviousSuccesses=0)

    def test_acceptance_is_not_deployment(self):
        result = prototype_decision(self.report())
        self.assertTrue(result['prototypeAccepted'])
        self.assertFalse(result['navigationAuthority']); self.assertFalse(result['deploymentApproved'])

    def test_missing_and_regressed(self):
        for key, value in [('eligibleNativeHCF', False), ('coreMLParity', False),
                           ('baselineCorrect', 95), ('lostPreviousSuccesses', 1)]:
            report = self.report(); report[key] = value
            self.assertFalse(prototype_decision(report)['prototypeAccepted'])

    def test_bad_counts(self):
        for key, value in [('wrong', -1), ('correct', 99), ('cases', True)]:
            report = self.report(); report[key] = value
            with self.assertRaises(ValueError): prototype_decision(report)


if __name__ == '__main__': unittest.main()
