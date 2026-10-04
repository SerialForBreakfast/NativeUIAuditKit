import unittest
from unittest.mock import patch
import focus_direct_transition as d
from focus_translation_training import schedule


class ExposureTests(unittest.TestCase):
    def test_negative_evidence_and_connected_support(self):
        import evaluate_retained_negatives64 as e
        raw=dict(specification=dict(condition='boundary_unchanged'),cleanup='verified')
        with patch.object(e,'observed_scroll',return_value=(False,'observed')):
            e.validate_negative(raw,dict(focus='a'),dict(focus='a'))
            with self.assertRaises(ValueError):e.validate_negative(raw,dict(focus='a'),dict(focus='b'))
        with patch.object(e,'observed_scroll',return_value=(None,'unknown')):
            with self.assertRaises(ValueError):e.validate_negative(raw,dict(focus='a'),dict(focus='a'))
        rows=[dict(id='a',decodedPixelHashes=['1','2']),dict(id='b',decodedPixelHashes=['3','4']),
              dict(id='c',decodedPixelHashes=['2','3'])]
        self.assertEqual(e.connected_components(rows),[['a','b','c']])

    def test_only_epochs_differ(self):
        self.assertEqual(dict(d.TRANSLATION_CONFIG,epochs=600),d.EXPOSURE_CONFIG)
        self.assertTrue(d.valid_configuration(d.EXPOSURE_CONFIG))
        self.assertFalse(d.valid_configuration(dict(d.EXPOSURE_CONFIG,epochs=601)))
        t=d.torch_runtime();t.manual_seed(42);a=d.model(d.TRANSLATION_CONFIG)
        t.manual_seed(42);b=d.model(d.EXPOSURE_CONFIG)
        self.assertTrue(all(t.equal(v,b.state_dict()[k]) for k,v in a.state_dict().items()))

    def test_schedule_prefix_and_exposure(self):
        options=[list(range(i*5,i*5+5)) for i in range(24)]
        a=schedule(options,120,42);b=schedule(options,600,42)
        self.assertEqual(a,b[:120]);self.assertEqual(sum(map(len,b)),14400)


if __name__=='__main__':unittest.main()
