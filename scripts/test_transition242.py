"""Check native focus labels and data boundaries without captures."""
import unittest
import numpy as np
import transition242 as t


def scene(identity):
    return dict(focus_observation=dict(observedID=identity, requestedID='not-a-label',
                verified=True, source='uikit_focus_system'),
                focused_element_id=identity, is_settled=True)


class TransitionTests(unittest.TestCase):
    def test_observed_labels(self):
        self.assertEqual(t.label(scene('a'), scene('b')), 1)
        self.assertEqual(t.label(scene('a'), scene('a')), 0)

    def test_missing_conflicting_or_unsettled_observation(self):
        for key, value in [('focused_element_id', 'b'), ('is_settled', False),
                           ('focus_observation', {'requestedID': 'a'})]:
            invalid = dict(scene('a'), **{key:value})
            with self.assertRaisesRegex(ValueError, 'unverified_focus'):
                t.label(scene('a'), invalid)

    def test_training_pixel_leakage(self):
        rows = [dict(id='a', role='train', pixelHashes=['same']),
                dict(id='b', role='reserved', pixelHashes=['same'])]
        with self.assertRaisesRegex(ValueError, 'cross_role_pixels'):
            t.check_roles(rows)
        rows[1]['pixelHashes'] = ['different']
        t.check_roles(rows)

    def test_duplicate_pair_and_unknown_role(self):
        row = dict(id='a', role='train', pixelHashes=['same'])
        with self.assertRaisesRegex(ValueError, 'duplicate_pair'):
            t.check_roles([row, row])
        with self.assertRaisesRegex(ValueError, 'invalid_role'):
            t.check_roles([dict(row, role='test-in-training')])

    def test_counts_and_abstentions(self):
        rows = [dict(role='reserved', changed=1, conditions=['original_capture']),
                dict(role='development', changed=0, conditions=['artwork_contrast'])]
        result = t.summaries(np.array([.5, .9]), rows)
        self.assertEqual(result['reserved']['abstentions'], 1)
        self.assertEqual(result['artwork_0']['falseChange'], 1)
        self.assertEqual(result['artwork_1']['count'], 0)


if __name__ == '__main__':
    unittest.main()
