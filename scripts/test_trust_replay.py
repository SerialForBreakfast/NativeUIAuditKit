"""Check evidence conversion without running models."""
import unittest

from trust_replay import prediction_rows


class ReplayEvidenceTests(unittest.TestCase):
    def test_preserve_scores_and_groups(self):
        row = dict(id='a', changed=1, group='same-scene')
        result = prediction_rows(dict(sets={name: dict(rows=[row], probabilities=[0.7]) for name in ('forward', 'reverse')}))
        self.assertEqual(len(result), 2)
        self.assertEqual({r['group'] for r in result}, {'same-scene'})
        self.assertEqual(result[0]['probability'], 0.7)

    def test_missing_score_fails(self):
        with self.assertRaises(ValueError):
            prediction_rows(dict(rows=[dict(id='a', changed=1, group='g')], probabilities=[]))

    def test_invalid_score_fails(self):
        with self.assertRaises(ValueError):
            prediction_rows(dict(rows=[dict(id='a', changed=1, group='g')], probabilities=[1.05]))


if __name__ == '__main__':
    unittest.main()
