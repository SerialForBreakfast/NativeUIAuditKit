import unittest
from consumer_crop_comparison import records,summarize

class ConsumerTests(unittest.TestCase):
    def fixture(self):
        frames=[dict(id='f',cohort='c',path='a.png',sha256='a'*64)]
        truth=[dict(id='f-x',frame='f',focused=True,profile='Standard',source='native_body_presentation_layer',
                    geometry_role='rendered_control_body',family='test',bounds=[0,0,10,10])]
        observed=dict(results=[dict(id='f-x',probability=.9,modelInputRGBSHA256='b'*64)])
        return frames,{'c':(truth,observed,[dict(id='f',focus_id='x',profile='Standard')])}
    def test_valid(self):
        rows=records(*self.fixture()); out=summarize(rows,[.9])
        self.assertEqual(out['counts'],{'tp':1}); self.assertEqual(out['rows'][0]['outcome'],'correct')
    def test_conflicting_focus(self):
        f,c=self.fixture(); c['c'][0][0]['focused']=False
        with self.assertRaisesRegex(ValueError,'consumer_focus_conflict'): records(f,c)
    def test_missing_score(self):
        f,c=self.fixture(); c['c'][1]['results']=[]
        with self.assertRaisesRegex(ValueError,'consumer_scores'): records(f,c)
    def test_thresholds(self):
        rows=records(*self.fixture())
        self.assertEqual(summarize(rows,[.7])['counts'],{'abstention':1})
        self.assertEqual(summarize(rows,[.69])['counts'],{'fn':1})
        with self.assertRaises(ValueError): summarize(rows,[float('nan')])
