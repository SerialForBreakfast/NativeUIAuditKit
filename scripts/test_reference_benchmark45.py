import copy
import unittest
from test_real_model_scorecard import example
from reference_benchmark45 import select_frames, arm_score, score, summary


class BenchmarkTests(unittest.TestCase):
    def frame(self):
        f,_=example(False)
        return dict(f,image={'path':'test.png','sha256':f['sha256']},family='catalog',
                    aliases=['a'],conditions=['appearance'])

    def test_focus_and_known_negative_are_separate(self):
        f=self.frame();f['controls'].append(dict(id='b',bounds=[20,0,10,10],state='unfocused'))
        a=arm_score(f,[[0,0,10,10],[20,0,10,10]],[[20,0,10,10]])
        self.assertTrue(a['localized']['0.5']);self.assertEqual(a['selection'],'known_unfocused')
        self.assertEqual(a['selectedOnKnownUnfocused'],1)

    def test_partial_unmatched_not_false_positive(self):
        a=arm_score(self.frame(),[[30,30,5,5]],[[30,30,5,5]])
        self.assertEqual(a['selection'],'unreviewed_geometry');self.assertEqual(a['selectedOnKnownUnfocused'],0)

    def test_no_and_multiple_focus(self):
        self.assertEqual(arm_score(self.frame(),[],[])['selection'],'none')
        self.assertEqual(arm_score(self.frame(),[],[[0,0,10,10],[20,0,10,10]])['selection'],'multiple')

    def test_fixed_threshold_and_model_identity(self):
        f=self.frame();_,p=example(False)
        row=score(f,[dict(box=[0,0,10,10],score=.1)],p)
        self.assertEqual(row['candidate']['selection'],'none')
        self.assertEqual(row['lowConfidenceCandidateBestIoU'],1)
        p['configuration']['minConfidence']=.2
        with self.assertRaises(ValueError):score(f,[],p)

    def test_exact_duplicate_grouping_and_conflicting_labels(self):
        p=dict(id='a',sourceRole='calibration',disposition='imported',pixelSHA256='same',
               image={'path':'test.png','sha256':'a'},evidenceKind='appearance',
               recipe=dict(appearance=dict(referencePack=dict(screen='catalog'))),
               proposals=[dict(sourceElementID='x',bounds=[0,0,10,10],state='focused',**{'class':'primaryButton'})])
        q=copy.deepcopy(p);q['id']='b';q['evidenceKind']='scroll_unchanged'
        self.assertEqual(select_frames({'frames':[p,q]})[0]['aliases'],['a','b'])
        q['proposals'][0]['bounds'][0]=1
        with self.assertRaisesRegex(ValueError,'duplicate_label_conflict'):select_frames({'frames':[p,q]})

    def test_weighted_and_unique_counts(self):
        f=self.frame();_,p=example(False);f['aliases']=['a','b']
        row=score(f,[dict(box=[0,0,10,10],score=.9)],p)
        result=summary([row])['all']['candidate']
        self.assertEqual(result['localized']['0.5'],1)
        self.assertEqual(result['sourceEntryWeightedLocalized50'],2)


if __name__=='__main__':unittest.main()
