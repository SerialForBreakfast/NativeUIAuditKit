"""Check fixed-score diagnoses without model execution."""
import copy
import unittest
from followup373 import analyze, merge, margin


class FollowupTests(unittest.TestCase):
    def row(self):
        return dict(id='a', role='development', group='g', images=[dict(path='x',sha256='a'*64)],
                    layout='grid',condition='movement',changed=1,ancestryRole='train',
                    scores=dict(FOCUS329=.9,gamma348=.9,movement349=.9,control=.8,notification=.1))

    def test_loss_and_fixed_margins(self):
        row=self.row(); d=analyze([row],'losses',None)
        self.assertEqual(len(d['lostSuccesses']),1)
        self.assertFalse(d['lostSuccesses'][0]['controlCorrect'])
        self.assertAlmostEqual(margin(row,'notification'),-.75)
        self.assertFalse(analyze([row],'margins',None)['thresholdsChanged'])

    def test_abstention_is_missed_change(self):
        row=self.row();row['scores']['notification']=.5
        for mode in ('conditions','groups'):
            scores=analyze([row],mode,None)['slices'][0]['scores']['notification']
            self.assertEqual(scores['abstentions'],1);self.assertEqual(scores['missedChanges'],1)

    def test_ancestry_never_admits_final_audit(self):
        row=self.row();train=copy.deepcopy(row);train['role']='train'
        result=analyze([row],'ancestry',dict(rows=[train],trainingEligible=True,pixelDisjoint=False,limitation='Shared artwork'))
        self.assertEqual(result['sharedEncodedImageHashes'],['a'*64]);self.assertFalse(result['finalAuditEligible'])
        self.assertFalse(result['decodedPixelsRechecked'])

    def test_merge_rejects_missing_and_changed_membership(self):
        row=self.row();model=dict(path='weights',sha256='b'*64)
        old=dict(rows=[row],scores={n:dict(probabilities=[.9],model=model) for n in ('FOCUS329','gamma348','movement349')})
        part=dict(rows=[row],probabilities=dict(gamma=[.1]))
        current=dict(configuration=dict(models=dict(gamma=model)),sets=dict(one=part))
        rows,_=merge([old],dict(notification=[current]));self.assertEqual(len(rows),1)
        for key,value in [('changed',0),('images',[]),('role','audit')]:
            changed=copy.deepcopy(current);changed['sets']['one']['rows'][0][key]=value
            with self.assertRaisesRegex(ValueError,'case_identity'):merge([old],dict(notification=[changed]))
        with self.assertRaisesRegex(ValueError,'comparison_membership'):merge([old],dict(notification=[]))

    def test_invalid_probability(self):
        row=self.row();model=dict(path='x',sha256='a'*64)
        old=dict(rows=[row],scores=dict(FOCUS329=dict(model=model,probabilities=[float('nan')])))
        with self.assertRaisesRegex(ValueError,'invalid_probability'):merge([old],{})

if __name__=='__main__':unittest.main()
