import unittest
from pathlib import Path
from focus_representative_validation import summarize, stratum, synthetic_rows, validate, VERSION
from focus_dataset_contract import digest


def sample(i,control,label,frame='frame'):
    return dict(id=str(i),control=control,label=label,family='fixture',theme='dark',hard=False,
                pixelSHA256=str(i),frameID=frame,population='candidate',settlement='settled')


class RepresentativeTests(unittest.TestCase):
    def test_four_strata_have_equal_macro_weight(self):
        rows=[sample(0,'primaryButton',1),sample(1,'focus:tabItem',1),
              sample(2,'collectionItem',1),sample(3,'listRow',1)]
        rows += [sample(i,'collectionItem',0) for i in range(4,100)]
        pred=[dict(id=r['id'],probability=1. if r['id']=='0' else 0.) for r in rows]
        result=summarize(rows,pred)
        self.assertEqual(result['macroRecall'],.25)
        self.assertEqual(result['supportedMacroStrata'],4)

    def test_absent_and_negative_only_strata_are_unavailable_for_recall(self):
        r=[sample(0,'listRow',0)];p=[dict(id='0',probability=.1)]
        result=summarize(r,p)
        self.assertIsNone(result['macroRecall'])
        self.assertIsNone(result['strata']['rows']['recall'])
        self.assertEqual(result['strata']['tabs']['status'],'unavailable')

    def test_prediction_membership_and_finite_scores(self):
        r=[sample(0,'listRow',1)]
        for p in [[],[dict(id='different',probability=.2)],
                  [dict(id='0',probability=float('nan'))],[dict(id='0',probability=True)],
                  [dict(id='0',probability=2.)]]:
            with self.assertRaises(ValueError):summarize(r,p)
        with self.assertRaises(ValueError):summarize(r,[dict(id='0',probability=.2)]*2)

    def test_changed_seal_and_challenge_policy_rejected_before_runtime(self):
        with self.assertRaises(ValueError):validate({'seal':'wrong'})
        doc=dict(version=VERSION,role='final-challenge')
        doc['seal']=digest(doc)
        with self.assertRaises(ValueError):validate(doc)

    def test_source_training_or_challenge_rejected_before_pixels(self):
        for purpose in ('train','final-challenge'):
            with self.assertRaises(ValueError):synthetic_rows(dict(purpose=purpose),Path('.'))

    def test_frame_outcomes_and_incomplete_candidate_set(self):
        rows=[sample(0,'primaryButton',1),sample(1,'primaryButton',0)]
        policy=dict(populations=dict(candidate=['0','1'],auxiliary=[],unresolved=[]),
                    frames=[dict(id='frame',coverage='complete',settlement='settled')])
        for values,expected in [([.9,.1],'unique_correct'),([.1,.9],'wrong'),
                                ([.1,.1],'no_focus'),([.9,.9],'multiple_focus')]:
            p=[dict(id=str(i),probability=v) for i,v in enumerate(values)]
            self.assertEqual(summarize(rows,p,policy)['metrics']['completeFrameSelection']['counts'],{expected:1})
        policy['frames'][0]['coverage']='incomplete'
        self.assertEqual(summarize(rows,p,policy)['metrics']['completeFrameSelection']['status'],'unavailable')

    def test_unknown_control_and_native_tab_override(self):
        self.assertEqual(stratum(sample(0,'focus:otherFocusable',1)),'other')
        self.assertEqual(stratum(dict(sample(0,'primaryButton',1),stratum='tabs')),'tabs')

    def test_unsettled_candidates_excluded_not_silently_scored(self):
        rows=[sample(0,'listRow',1)];rows[0]['settlement']='unsettled'
        policy=dict(populations=dict(candidate=['0'],auxiliary=[],unresolved=[]),
                    frames=[dict(id='frame',coverage='complete',settlement='unsettled')])
        r=summarize(rows,[dict(id='0',probability=.9)],policy)
        self.assertEqual(r['metrics']['excludedCandidates'],['0'])
        self.assertIsNone(r['macroRecall'])


if __name__=='__main__':unittest.main()
