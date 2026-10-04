import unittest
from benchmark_shadow120 import classes


def pair(a,b):
    return {'before':{'sha256':a},'after':{'sha256':b}}


class CacheAccountingTests(unittest.TestCase):
    def test_identity_and_adjacent_reuse(self):
        self.assertEqual(classes([pair('a','b'),pair('b','c'),pair('c','c'),pair('a','b')]),
                         ['cold','mixed','cached','cached'])

    def test_lru_and_request_boundary(self):
        rows=[pair(str(i),str(i)) for i in range(9)]+[pair('0','0')]
        self.assertEqual(classes(rows),['mixed']*10)
        self.assertEqual(classes([pair('a','b')]*33),['cold']+['cached']*31+['cold'])


if __name__=='__main__':unittest.main()
