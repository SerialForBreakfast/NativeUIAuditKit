import unittest
from compare_annotation_proposals import match, validate_boxes

class MatchingTests(unittest.TestCase):
    def test_empty_duplicate_and_exact(self):
        b=[10,20,30,40]
        self.assertEqual(match([], [b],.5)['missedReviewed'],1)
        self.assertEqual(match([b,b], [b],.5)['matches'],1)
        self.assertEqual(match([b],[],.5)['unmatchedProposals'],1)
        self.assertEqual(match([b], [b],.75)['matches'],1)
    def test_bipartite_reassign_and_stricter_cutoff(self):
        a=[0,0,10,10];b=[5,0,10,10];p=[2,0,10,10]
        self.assertEqual(match([p,a],[a,b],.5)['matches'],2)
        self.assertEqual(match([p],[a],.75)['matches'],0)
    def test_invalid_coordinates(self):
        for b in ([0,0,0,1],[-1,0,1,1],[0,0,float('nan'),1],[0,0,101,1],[True,0,1,1]):
            with self.assertRaises(ValueError):validate_boxes([b],100,100)
        validate_boxes([[10,20,30,40]],100,100)

if __name__=='__main__':unittest.main()
