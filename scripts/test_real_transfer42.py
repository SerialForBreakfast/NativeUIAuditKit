import copy
import unittest
import real_fullscreen42 as r
from test_real_model_scorecard import example


class TransferTests(unittest.TestCase):
    def score(self,ds,complete=True):
        f,p=example(complete);row=r.frame_metrics(f,ds,p)
        return row,r.summarize([f],[ds],[row])

    def test_single_correct_and_geometry(self):
        row,total=self.score([dict(box=[0,0,10,10],score=.9)])
        self.assertEqual(row['outcome'],'correct');self.assertEqual(total['completeAP']['0.9'],1)

    def test_partial_excluded_from_ap_and_accuracy(self):
        row,total=self.score([dict(box=[20,0,30,10],score=.9)],False)
        self.assertEqual(row['outcome'],'incomplete');self.assertIsNone(total['completeAP']['0.5'])
        self.assertEqual(total['partialUnreviewedPredictions'],1)

    def test_reviewed_target_not_counted_unreviewed(self):
        _,total=self.score([dict(box=[0,0,10,10],score=.9)],False)
        self.assertEqual(total['partialUnreviewedPredictions'],0)

    def test_known_unfocused_counted_separately(self):
        f,p=example(False);f['controls'].append(dict(id='other',bounds=[20,0,10,10],state='unfocused',**{'class':'listRow'}))
        ds=[dict(box=[20,0,30,10],score=.9)];row=r.frame_metrics(f,ds,p)
        total=r.summarize([f],[ds],[row]);self.assertEqual(total['detectionsOnKnownUnfocusedControls'],1)
        self.assertEqual(total['partialUnreviewedPredictions'],0)

    def test_multiple_not_forced_into_correct(self):
        row,_=self.score([dict(box=[0,0,10,10],score=.9),dict(box=[20,0,30,10],score=.8)])
        self.assertEqual(row['outcome'],'multiple_focus')

    def test_low_candidate_not_operating_prediction(self):
        row,total=self.score([dict(box=[0,0,10,10],score=.1)])
        self.assertEqual(row['outcome'],'no_focus');self.assertEqual(total['completeAP']['0.5'],1)

    def test_nonfinite_rejected(self):
        with self.assertRaisesRegex(ValueError,'invalid_candidate'):
            self.score([dict(box=[0,0,float('nan'),10],score=.9)])

    def test_ap_is_confidence_sorted(self):
        _,total=self.score([dict(box=[20,0,30,10],score=.2),dict(box=[0,0,10,10],score=.9)])
        self.assertEqual(total['completeAP']['0.5'],1)


if __name__=='__main__':unittest.main()
