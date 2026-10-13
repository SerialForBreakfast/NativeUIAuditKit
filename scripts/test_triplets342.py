import unittest
from triplets342 import connected


class GroupTests(unittest.TestCase):
    def test_transitive_groups(self):
        rows=[dict(id='a',keys=['x']),dict(id='b',keys=['x','y']),dict(id='c',keys=['y']),dict(id='d',keys=['z'])]
        self.assertEqual(connected(rows),[['a','b','c'],['d']])

    def test_duplicate_identity_fails(self):
        with self.assertRaisesRegex(ValueError,'duplicate_case'):
            connected([dict(id='a',keys=[]),dict(id='a',keys=[])])


if __name__=='__main__':unittest.main()
