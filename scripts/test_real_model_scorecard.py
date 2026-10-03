import unittest
import real_model_scorecard as s


def example(complete=True):
    f=dict(sha256='abc',screen='settings',complete=complete,controls=[
        dict(id='one',bounds=[0,0,10,10],state='focused',**{'class':'listRow'})])
    d=dict(status='success',inputSHA256='abc',configuration=dict(platform='tvOS',ocr=False,minConfidence=.5),
      totalMs=1,runtime=dict(result=dict(focusExecution=dict(backend='coreML',modelScoringComplete=True),
        elements=[dict(boundingBoxPixels=dict(x=0,y=0,width=10,height=10),elementType='listRow',
          state=dict(isFocused=True,focusScore=.01))])))
    return f,d


class ScorecardTests(unittest.TestCase):
    def test_matching_augmenting_path(self):
        # First truth can take either prediction; second can only take the first.
        self.assertEqual(len(s.matching([[0,0,10,10],[3,0,10,10]],
                                       [[1,0,10,10],[-2,0,10,10]],.6)),2)

    def test_duplicate_prediction_not_double_credit(self):
        self.assertEqual(len(s.matching([[0,0,10,10]],[[0,0,10,10]]*2,.5)),1)

    def test_selected_policy_not_raw_probability(self):
        f,d=example();self.assertEqual(s.score(f,d)['focusOutcome'],'correct')
        d['runtime']['result']['elements'][0]['state']['isFocused']=False
        self.assertEqual(s.score(f,d)['focusOutcome'],'no_focus_selected')

    def test_partial_truth_excluded_from_complete_accuracy(self):
        f,d=example(False);r=s.score(f,d)
        self.assertFalse(r['focusEligible']);self.assertEqual(s.summarize([r])['focusEligible'],0)

    def test_nonunique_truth_excluded(self):
        f,d=example();f['controls'][0]['state']='unfocused'
        self.assertFalse(s.score(f,d)['focusEligible'])

    def test_selected_duplicate_box_is_not_lost_by_matching_tie(self):
        import copy
        f,d=example();e=d['runtime']['result']['elements']
        e.append(copy.deepcopy(e[0]));e[0]['state']['isFocused']=False
        self.assertEqual(s.score(f,d)['focusOutcome'],'correct')

    def test_unreviewed_prediction_never_false_positive(self):
        f,d=example();d['runtime']['result']['elements'].append(dict(
            boundingBoxPixels=dict(x=20,y=0,width=10,height=10),elementType='label',state={}))
        self.assertEqual(s.score(f,d)['unmatchedPredictionsUnreviewed'],1)

    def test_invalid_values_rejected(self):
        f,d=example();d['runtime']['result']['elements'][0]['boundingBoxPixels']['x']=float('nan')
        with self.assertRaises(ValueError):s.score(f,d)

    def test_input_identity_and_health(self):
        f,d=example();d['inputSHA256']='other'
        with self.assertRaises(ValueError):s.score(f,d)
        f,d=example();d['runtime']['result']['focusExecution']['modelScoringComplete']=False
        with self.assertRaises(ValueError):s.score(f,d)


if __name__=='__main__':unittest.main()
