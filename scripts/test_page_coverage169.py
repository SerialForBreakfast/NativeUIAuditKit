import unittest
from page_coverage169 import parse,summary

class CoverageTests(unittest.TestCase):
    def test_empty_and_boxes(self):
        self.assertEqual(parse('\n',41),[])
        self.assertEqual(summary(parse('1 .5 .5 .2 .2',41))['horizontalThirds'],{'middle':1})
    def test_reject_invalid(self):
        for text in ('1 nan .5 .2 .2','1 .5 .5 -1 .2','41 .5 .5 .2 .2',
                     '1.5 .5 .5 .2 .2','1 .01 .5 .2 .2','1 .5 .5 .2','1 .5 .5 inf .2'):
            with self.subTest(text=text),self.assertRaises(Exception):parse(text,41)
    def test_third_boundaries(self):
        rows=[[1,x,.5,.01,.01] for x in (.2,1/3,2/3,.8)]
        self.assertEqual(summary(rows)['horizontalThirds'],dict(left=1,middle=1,right=2))
        self.assertIsNone(summary([])['ranges']['cx'])

if __name__=='__main__':unittest.main()
