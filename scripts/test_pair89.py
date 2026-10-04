import unittest
from diagnose_pair89 import select_pair


class PairTests(unittest.TestCase):
    def test_persistent_distractor_cancels(self):
        pool=[dict(id='focus',bounds=[0,0,40,20]),dict(id='decor',bounds=[80,0,10,10])]
        result=select_pair(pool,pool,[10,20],[1,20])
        self.assertEqual(result['candidate']['id'],'focus');self.assertEqual(result['delta'],9)
    def test_no_correspondence_or_label_leak(self):
        pool=[dict(id='a',bounds=[0,0,10,10])]
        self.assertIsNone(select_pair(pool,[dict(id='b',bounds=[80,80,10,10])],[1],[2]))
        with self.assertRaises(ValueError):select_pair([dict(pool[0],focused=True)],pool,[1],[2])
        with self.assertRaises(ValueError):select_pair(pool,pool,[],[1])


if __name__=='__main__':unittest.main()
