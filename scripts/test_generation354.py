import copy
import unittest
from pathlib import Path
from unittest.mock import patch
import dataset351 as d
import register_generation354 as r
import audit_generation354 as audit


class Tests(unittest.TestCase):
    def source(self):
        return {'appearance':{'composition':{'version':5,
            'regions':[{'frame':[100+i*400,100,200,200]} for i in range(4)],
            'definitions':{'poster':{'width':80,'height':80}},
            'styles':{'image':{'background':123}}}}}

    def test_factors_preserve_source(self):
        original=self.source(); saved=copy.deepcopy(original)
        for factor in ('size','growth','shadow','position','background'):
            pair=r.cases(original,factor)
            self.assertEqual(len(pair),2)
            self.assertEqual(pair[0]['sourceFocus'],'item-2')
            self.assertEqual(pair[1]['targetFocus'],'item-3')
            self.assertNotEqual(pair[0]['recipe'],pair[1]['recipe'])
            self.assertEqual(original,saved)

    @patch('dataset351.n.identity',return_value='same')
    @patch('dataset351.n.signature',return_value='verified')
    def test_reload_waits_for_observed_focus(self,*_):
        from unittest.mock import Mock
        fixture=Mock();fixture.snapshot.return_value={'scene':{'is_settled':True,
            'focus_observation':{'verified':True,'generation':1}, 'observation_generation':1,
            'observation_diagnostics':{'sampledGeneration':1,'reason':'ready','sampleAgeMilliseconds':2}}}
        self.assertEqual(d.wait_loaded(fixture,{},Path('.'),1),fixture.snapshot.return_value)
        fixture.request.assert_not_called()

    @patch('dataset351.n.identity',side_effect=['new','old'])
    def test_reload_rejects_changed_identity(self,*_):
        from unittest.mock import Mock
        with self.assertRaisesRegex(ValueError,'reload_identity_changed'):
            d.wait_loaded(Mock(),{},Path('.'),1)

    @patch('dataset351.q.save')
    @patch('dataset351.time.monotonic',side_effect=[0,11])
    def test_reload_timeout_preserves_reason(self,clock,save):
        from unittest.mock import Mock
        with self.assertRaisesRegex(ValueError,'reload_not_ready'):
            d.wait_loaded(Mock(),{},Path('.'),1)
        self.assertEqual(save.call_args.args[1]['reason'],'no_observation')

    def test_pixel_difference_and_dimension_check(self):
        import tempfile
        from PIL import Image
        import research_queue as q
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as folder:
            a=Path(folder)/'a.png';b=Path(folder)/'b.png'
            Image.new('RGB',(2,2),(0,0,0)).save(a)
            Image.new('RGB',(2,2),(1,0,0)).save(b)
            self.assertEqual(audit.difference(a,a)['changedPixels'],0)
            self.assertEqual(audit.difference(a,b)['changedPixels'],4)
            Image.new('RGB',(3,2)).save(b)
            with self.assertRaisesRegex(ValueError,'dimension_mismatch'):audit.difference(a,b)
