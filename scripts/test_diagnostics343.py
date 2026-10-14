import unittest
from diagnostics343 import counts


class CountTests(unittest.TestCase):
    def test_errors_and_abstentions(self):
        rows=[dict(changed=x,layout='a',condition='b') for x in [0,1,0,1]]
        result=counts(rows,[.9,.1,.5,.9],[.1,.9,.1,.5])['a/b']
        self.assertEqual(result,dict(count=4,correct=1,falseChange=1,missedChange=1,abstentions=1,lost=3,gained=1))

    def test_missing_and_invalid(self):
        with self.assertRaises(ValueError):counts([dict(changed=0)],[])
        with self.assertRaises(ValueError):counts([dict(changed=0)],[float('nan')])
        self.assertEqual(counts([],[]),{})


if __name__=='__main__':unittest.main()
