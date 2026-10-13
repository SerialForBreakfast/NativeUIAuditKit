import unittest
from review_notification366 import compare


class GainTests(unittest.TestCase):
    def test_union_preserves_gamma_gain(self):
        old={'case':dict(changed=0,scores=dict(original=.9,gamma=.1))}
        new={'case':dict(changed=0,probability=.5,condition='banner-appearance')}
        self.assertEqual(compare(old,new)[0]['previousCorrect'],['gamma'])

    def test_correct_decision_passes(self):
        self.assertEqual(compare({'a':dict(changed=1,scores=dict(original=.9))},
            {'a':dict(changed=1,probability=.95,condition='dim-movement')}),[])

    def test_missing_case_fails(self):
        with self.assertRaisesRegex(ValueError,'gain_membership'):compare({'a':{}},{})


if __name__=='__main__':unittest.main()
