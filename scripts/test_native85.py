import unittest
from audit_native85 import summarize


class CoverageTests(unittest.TestCase):
    def test_unknown_scroll_and_duplicate_pixels_are_not_independence(self):
        rows=[dict(id='a',kind='appearance-pair',theme='dark',style='poster',scroll=None,
            pixels=['one','two'],focusedBodies=[[0,0,80,90]]),
            dict(id='b',kind='recorded-action',theme='light',style='poster',scroll=False,
            pixels=['two','three'],focusedBodies=[[0,0,800,90]])]
        result=summarize(rows)
        self.assertEqual(result['observedScroll'],{'None':1,'False':1})
        self.assertEqual(result['repeatedPixelOccurrences'],1)
        self.assertEqual(result['smallFocusedBodies'],1)
        self.assertFalse(result['trainingEligible'])
        self.assertFalse(result['independentEvaluationEligible'])
        with self.assertRaises(ValueError):summarize(rows+[rows[0]])


if __name__=='__main__':unittest.main()
