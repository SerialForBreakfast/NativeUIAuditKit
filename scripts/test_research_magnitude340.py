"""Check fixed matching rules without using captured images."""
import unittest
from research_magnitude340 import matched_pairs

class MatchTests(unittest.TestCase):
    def test_match_within_family_and_tolerance(self):
        rows=[dict(id='a',group='a',label=1,magnitude=.1),dict(id='b',group='a',label=0,magnitude=.105),
              dict(id='c',group='b',label=1,magnitude=.105),dict(id='d',group='a',label=0,magnitude=.5)]
        matches=matched_pairs(rows)
        self.assertEqual(len(matches),1)
        self.assertEqual(matches[0]['artwork']['id'],'b')

    def test_no_repeated_negative(self):
        rows=[dict(id='a',group='a',label=1,magnitude=.1),dict(id='b',group='a',label=1,magnitude=.1),
              dict(id='c',group='a',label=0,magnitude=.1)]
        self.assertEqual(len(matched_pairs(rows)),1)

    def test_no_support_is_not_success(self):
        self.assertEqual(matched_pairs([]),[])

if __name__=='__main__':unittest.main()
