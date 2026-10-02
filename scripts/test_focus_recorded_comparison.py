"""OCR matching and fixed-arm scoring preserve truth isolation and abstentions."""
import copy
import unittest
import focus_recorded_semantics as s
import focus_recorded_comparison as c


class SemanticTests(unittest.TestCase):
    def fixture(self):
        frame=dict(image=dict(sha256='x'),controls=[dict(id='r',bounds=[100,200,600,60],state='focused')])
        ocr=dict(sha256='x',width=1000,height=600,errors=[],text=[
            dict(text='Settings',bounds=[400,30,160,40],confidence=.99),
            dict(text='Audio  Output',bounds=[120,210,180,30],confidence=.99),
            dict(text='On',bounds=[650,210,40,30],confidence=.99),
            dict(text='noise',bounds=[120,210,180,30],confidence=.2)])
        return frame,ocr

    def test_uses_title_and_left_label_not_value_or_focus(self):
        f,ocr=self.fixture();d=s.describe(f,ocr)
        self.assertEqual(d['title'],'settings');self.assertEqual(d['rows'][0]['text'],'audio output')
        f['controls'][0]['state']='unfocused';self.assertEqual(d,s.describe(f,ocr))

    def test_duplicate_empty_changed_title_reject(self):
        f,o=self.fixture();a=s.describe(f,o);b=copy.deepcopy(a);b['rows'][0]['id']='new'
        self.assertEqual(s.correspond(a,b)['matches'][0]['after'],'new')
        b['title']='apps';self.assertFalse(s.correspond(a,b)['sameTitle'])
        self.assertIsNone(s.correspond(a,b)['matches'][0]['after'])
        b['title']='settings';b['rows'].append(dict(b['rows'][0],id='duplicate'))
        self.assertIsNone(s.correspond(a,b)['matches'][0]['after'])
        a['rows'][0]['text']='';self.assertIsNone(s.correspond(a,b)['matches'][0]['after'])

    def test_source_errors_and_wrong_image(self):
        f,o=self.fixture();o['sha256']='y'
        with self.assertRaisesRegex(ValueError,'binding'):s.describe(f,o)
        o['sha256']='x';o['errors']=['failed']
        with self.assertRaisesRegex(ValueError,'ocr_errors'):s.describe(f,o)

    def test_no_title_is_not_context(self):
        f,o=self.fixture();o['text']=o['text'][1:];a=s.describe(f,o)
        self.assertFalse(s.correspond(a,a)['sameTitle'])


class ComparisonTests(unittest.TestCase):
    def fixture(self):
        before=[dict(id='b',bounds=[10,20,100,30],state='unfocused')]
        after=[dict(id='a',bounds=[10,20,100,30],state='focused')]
        p=[dict(id='b',tracking=dict(status='matched',afterBounds=[10,20,100,30]),
                decision='arrival',brightness='arrival',growth='unavailable',illuminationWarning=False)]
        matches=[dict(before='b',after='a',text='row',reason='unique_row_text')]
        return p,before,after,matches

    def test_all_arms_same_membership_and_after_truth_not_prediction(self):
        p,b,a,m=self.fixture();original=copy.deepcopy(p);r=c.compare(p,b,a,m)[0]
        self.assertEqual(r['expected'],'arrival');self.assertTrue(r['arms']['brightness']['correct'])
        self.assertFalse(r['arms']['growth']['correct']);self.assertEqual(original,p)
        a[0]['state']='unfocused';q=c.compare(p,b,a,m)[0]
        self.assertEqual(q['expected'],'unchanged');self.assertFalse(q['arms']['brightness']['correct'])
        self.assertEqual(original,p)

    def test_tracking_failure_counts_as_abstention_not_exclusion(self):
        p,b,a,m=self.fixture();p[0]['tracking']=dict(status='unavailable',reason='ambiguous_texture')
        r=c.compare(p,b,a,m)[0]['arms']['brightness']
        self.assertTrue(r['scorable']);self.assertEqual(r['decision'],'unavailable')
        summary=c.evaluate.summarize([r]);self.assertEqual(summary['abstained'],1)
        self.assertEqual(summary['correctnessIncludingAbstentions'],0)

    def test_wrong_spatial_target_rejected_despite_matching_text(self):
        p,b,a,m=self.fixture();p[0]['tracking']['afterBounds']=[200,200,100,30]
        r=c.compare(p,b,a,m)[0]
        self.assertFalse(r['trackingAgreesWithSemanticTarget'])
        self.assertEqual(r['arms']['combined']['rawDecision'],'arrival')
        self.assertEqual(r['arms']['combined']['decision'],'unavailable')

    def test_illumination_gates_every_arm_and_identical_unchanged(self):
        p,_,_,_=self.fixture();p[0]['illuminationWarning']=True
        self.assertTrue(all(c.decision(p[0],arm)=='unknown' for arm in c.ARMS))
        p[0]['tracking']['status']='identical'
        self.assertTrue(all(c.decision(p[0],arm)=='unchanged' for arm in c.ARMS))

    def test_reused_after_identity_and_missing_prediction_rejected(self):
        p,b,a,m=self.fixture();b.append(dict(b[0],id='b2'));p.append(dict(p[0],id='b2'));m.append(dict(m[0],before='b2'))
        with self.assertRaisesRegex(ValueError,'after_membership'):c.compare(p,b,a,m)
        with self.assertRaisesRegex(ValueError,'comparison_membership'):c.compare(p[:1],b,a,m)


if __name__=='__main__':unittest.main()
