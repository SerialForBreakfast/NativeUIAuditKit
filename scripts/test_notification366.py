"""Check admission, matched exposure, and conservative model decisions."""
import copy
import unittest
import numpy as np
import notification366 as n


class NotificationTests(unittest.TestCase):
    def corpus(self):
        row=dict(id='fresh',role='training-candidate',changed=1,condition='dim-movement',images=[dict(path='a',sha256='a'*64)])
        return dict(role='training-candidate',trainingEligible=False,sourceDomain='authored-headless',rows=[row])

    def test_new_rows_admitted_without_mutating_original(self):
        doc=self.corpus(); rows,_=n.admit_rows([doc],{'old'},lambda _: 'fresh')
        self.assertEqual(rows[0]['role'],'train')
        self.assertEqual(doc['rows'][0]['role'],'training-candidate')

    def test_development_pixels_rejected(self):
        with self.assertRaisesRegex(ValueError,'development_pixel_overlap'):
            n.admit_rows([self.corpus()],{'same'},lambda _: 'same')

    def test_development_role_rejected(self):
        doc=self.corpus();doc['role']='development'
        with self.assertRaisesRegex(ValueError,'candidate_role'):n.admit_rows([doc],set(),lambda _: 'fresh')

    def test_duplicate_case_rejected(self):
        with self.assertRaisesRegex(ValueError,'duplicate_case'):
            n.admit_rows([self.corpus(),self.corpus()],set(),lambda _: 'fresh')

    def test_schedule_visits_all_rows_and_preserves_labels(self):
        primary=np.array([0,1,0,1]);aux=np.array([0,0,0,1,1])
        result=n.schedule(primary,aux,3)
        np.testing.assert_array_equal(aux[result],np.tile(primary,(3,1)))
        self.assertEqual(len(np.unique(result)),len(aux))
        np.testing.assert_array_equal(result,n.schedule(primary,aux,3))

    def test_insufficient_exposure_rejected(self):
        with self.assertRaisesRegex(ValueError,'insufficient_exposure'):n.schedule([0,1],[0,0,1],1)

    def summaries(self):
        result=[]
        for arm in ('control','notification'):
            rows=[dict(job=f'focus366-{arm}-{i}',counts=dict(lost=0)) for i in range(28)]
            targets=[dict(id=str(i),changed=0,condition='banner-appearance',probability=.01) for i in range(392)]
            targets[0].update(id='artwork-s1-focus_maze-005',changed=1,condition='dim-movement',probability=.99)
            if arm=='control':targets[1]['probability']=.99
            result.append((f'focus366-{arm}-summary-0',dict(summaryRows=rows,targetPredictions=targets)))
        return result

    def test_gain_requires_review_not_promotion(self):
        result=n.decide(self.summaries())
        self.assertTrue(result['passesDevelopmentRule']);self.assertFalse(result['modelAccepted'])

    def test_corner_abstention_rejects(self):
        docs=self.summaries();docs[1][1]['targetPredictions'][0]['probability']=.8
        self.assertFalse(n.decide(docs)['passesDevelopmentRule'])

    def test_previous_loss_rejects(self):
        docs=self.summaries();docs[1][1]['summaryRows'][0]['counts']['lost']=1
        self.assertFalse(n.decide(docs)['passesDevelopmentRule'])

    def test_missing_comparison_rejects(self):
        docs=self.summaries();docs[1][1]['summaryRows'].pop()
        with self.assertRaisesRegex(ValueError,'missing_comparisons'):n.decide(docs)


if __name__=='__main__':unittest.main()
