"""Qualify policy comparisons without treating synthetic fixtures as model evidence."""
import copy
import unittest
import cached_focus_policy as p


class PolicyTests(unittest.TestCase):
    def row(self,profile='hcf'):
        return dict(id='a',group='g',profile=profile,noFocus=False,arms={'detector-plus-ring':dict(
            candidates=[dict(box=[0,0,10,10],source='mapped-ring'),dict(box=[20,0,10,10],source='detector')],
            models=dict(candidate=dict(scores=[.99,.98],outcome='miss'),baseline=dict(scores=[.99,0],outcome='correct')))})

    def test_ring_first_preserves_standard(self):
        row=self.row(); truth=[0,0,10,10]
        self.assertEqual(p.select(row,truth,'hcf-ring-first')['outcome'],'correct')
        row['profile']='standard'
        self.assertEqual(p.select(row,truth,'hcf-ring-first'),p.select(row,truth,'unchanged'))

    def test_fallback_and_unsafe_fallback(self):
        row=self.row(); truth=[0,0,10,10]
        self.assertTrue(p.select(row,truth,'abstention-fallback')['gain'])
        row['arms']['detector-plus-ring']['models']['baseline']=dict(scores=[0,.99],outcome='wrong')
        self.assertTrue(p.select(row,truth,'abstention-fallback')['newWrong'])

    def test_no_focus_and_empty(self):
        row=self.row();row['noFocus']=True
        row['arms']['detector-plus-ring']['models']['candidate']['outcome']='correct-abstention'
        row['arms']['detector-plus-ring']['models']['baseline']['outcome']='false-selection'
        self.assertEqual(p.select(row,None,'abstention-fallback')['outcome'],'false-selection')
        row['arms']['detector-plus-ring']=dict(candidates=[],models={m:dict(scores=[],outcome='correct-abstention') for m in ('baseline','candidate')})
        self.assertEqual(p.select(row,None,'hcf-ring-first')['outcome'],'correct-abstention')

    def test_invalid_and_changed_reference(self):
        row=self.row();truth=[0,0,10,10]
        with self.assertRaisesRegex(ValueError,'focus_policy_unknown'):p.select(row,truth,'invalid')
        row['arms']['detector-plus-ring']['models']['candidate']['outcome']='correct'
        with self.assertRaisesRegex(ValueError,'focus_policy_reference'):p.select(row,truth,'unchanged')

    def test_duplicate_and_missing_rows(self):
        row=p.select(self.row(),[0,0,10,10],'unchanged')
        with self.assertRaisesRegex(ValueError,'focus_policy_rows'):p.summarize([row,row],'unchanged')
        with self.assertRaisesRegex(ValueError,'focus_policy_rows'):p.summarize([],'unchanged')
        self.assertFalse(p.summarize([row],'unchanged')['modelAccepted'])


if __name__=='__main__':unittest.main()
