import unittest
from hcf361_baseline import summarize


class BaselineTests(unittest.TestCase):
    def rows(self):
        return [dict(id='a', label=1, profile='hcf'), dict(id='b', label=0, profile='hcf')]

    def test_disagreements(self):
        d = summarize(self.rows(), [.2, .9])
        self.assertEqual(d['reportedFocusedMisses'], 1)
        self.assertEqual(d['reportedUnfocusedFalsePositives'], 1)
        self.assertIsNone(d['measuredQualifiedAccuracy'])
        self.assertFalse(d['modelAccepted'])

    def test_bad_predictions(self):
        for scores in ([.8], [float('nan'), .3], [1.1, .3]):
            with self.assertRaises(ValueError): summarize(self.rows(), scores)

    def test_duplicates(self):
        with self.assertRaises(ValueError): summarize(self.rows()[:1]*2, [.9, .9])


if __name__ == '__main__': unittest.main()
