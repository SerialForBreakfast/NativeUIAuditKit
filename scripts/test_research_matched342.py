import unittest
from research_matched342 import summarize


class MatchedTests(unittest.TestCase):
    def rows(self):
        return [dict(id=str(i),role='train',changed=i%2,group='g',condition='c') for i in range(4)]

    def test_raw_counts_and_abstentions(self):
        v=summarize(self.rows(),[.9,.1,.5,.9])['g/c']
        self.assertEqual(v,dict(count=4,correct=1,falseChange=1,missedChange=1,abstentions=1))

    def test_duplicates_and_wrong_roles(self):
        rows=self.rows();rows[1]['id']='0'
        with self.assertRaisesRegex(ValueError,'membership'):summarize(rows,[0]*4)
        rows=self.rows();rows[1]['role']='test'
        with self.assertRaisesRegex(ValueError,'role_or_label'):summarize(rows,[0]*4)

    def test_unknown_score(self):
        with self.assertRaises(ValueError):summarize(self.rows(),[0,1,float('nan'),0])


if __name__=='__main__':unittest.main()
