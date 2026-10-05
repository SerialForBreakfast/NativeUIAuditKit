import unittest
import numpy as np
from contrast188 import connected,summarize

class Tests(unittest.TestCase):
    def test_connected_transitive(self):
        cases=[dict(id='a',kind='original',label=1,group='z'),dict(id='b',kind='identity',label=0,ancestry=[dict(group='z'),dict(group='y')]),dict(id='c',kind='identity',label=0,ancestry=[dict(group='y'),dict(group='x')])]
        self.assertEqual(connected(cases),['x']*3)
    def test_population_and_rank(self):
        cases=[dict(id='b',kind='original',label=0,group='g'),dict(id='a',kind='original',label=1,group='g')]
        v=np.zeros((3,3,2,768));r=summarize(v,cases)
        self.assertEqual(r['topTen'][0]['id'],'a');self.assertEqual(r['variantCountPerPlacement'],1536)
        self.assertEqual(r['summary']['both']['populations']['changed']['consensus']['confidentFlips'],768)
        self.assertEqual(r['summary']['both']['equalSourceFlipRate'],.5)
        v[0,0,0,0]=np.nan
        with self.assertRaises(Exception):summarize(v,cases)

if __name__=='__main__':unittest.main()
