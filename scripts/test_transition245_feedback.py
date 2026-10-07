"""Check truthful support and examples in model feedback."""
import unittest
import transition245_feedback as t


class FeedbackTests(unittest.TestCase):
    def test_zero_support_stays_zero(self):
        r=t.category('empty',[],{'a':[]},'none','native')
        self.assertEqual(r['support'],0)
        self.assertEqual(r['models']['a']['count'],0)
        self.assertEqual(r['examples'],[])

    def test_abstention_is_not_false_change(self):
        rows=[dict(id='a',role='development',group='g',changed=0),
              dict(id='b',role='development',group='g',changed=1)]
        r=t.category('test',rows,{'a':[.5,.01]},'review','native')
        self.assertEqual(r['models']['a']['abstentions'],1)
        self.assertEqual(r['models']['a']['falseChange'],0)
        self.assertEqual(r['models']['a']['missedChange'],1)
        self.assertEqual(r['groupCount'],1)
        self.assertFalse(r['independentTrials'])
        self.assertEqual([x['id'] for x in r['examples']],['a','b'])


if __name__=='__main__':unittest.main()
