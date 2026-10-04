import unittest
import numpy as np
import diagnose_region113 as m


class SignalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t=m.d.torch_runtime();cls.t.set_num_threads(2)
        cls.net=m.d.model(m.d.PAIRED_TEMPORAL_CONFIG)

    def test_letterbox_window(self):
        self.assertEqual(m.window(),(104,89,186,102))

    def test_channel_masks_do_not_mutate_inputs(self):
        x=self.t.rand(2,6,128,192);saved=x.clone();base=self.net.change_inputs(x)
        y=m.intervention(self.net,x,'difference_only')
        self.assertTrue(self.t.equal(y[:,:3],base[:,:3]));self.assertEqual(y[:,3:].abs().sum(),0)
        y=m.intervention(self.net,x,'context_only')
        self.assertTrue(self.t.equal(y[:,3:],base[:,3:]));self.assertEqual(y[:,:3].abs().sum(),0)
        self.assertTrue(self.t.equal(x,saved))

    def test_complementary_spatial_masks(self):
        x=self.t.rand(2,6,128,192);a=m.intervention(self.net,x,'focus_difference_only');b=m.intervention(self.net,x,'outside_difference_only')
        original=self.net.change_inputs(x)
        self.assertTrue(self.t.equal(a[:,:3]+b[:,:3],original[:,:3]))
        self.assertTrue(self.t.equal(a[:,3:],original[:,3:]))

    def test_reversal_preserves_difference(self):
        x=self.t.rand(2,6,128,192);a=m.intervention(self.net,x,'reversed');b=self.net.change_inputs(x)
        self.assertTrue(self.t.equal(a[:,:3],b[:,:3]));self.assertTrue(self.t.equal(a[:,3:6],x[:,3:]))

    def test_unsupported_and_wrong_shape(self):
        with self.assertRaises(ValueError):m.intervention(self.net,self.t.zeros(1,6,64,96),'baseline')
        with self.assertRaises(ValueError):m.intervention(self.net,self.t.zeros(1,6,128,192),'other')

    def test_summary_reports_intervention_decisions_not_accuracy(self):
        r=m.summarize(np.array([.1,.5,.9]),np.array([.1,.1,.1]),[0,1,2])
        self.assertEqual(r['confidentChanged'],1);self.assertEqual(r['uncertain'],1);self.assertNotIn('accuracy',r)
        self.assertEqual(r['decisionChanges'],2)


if __name__=='__main__':unittest.main()
