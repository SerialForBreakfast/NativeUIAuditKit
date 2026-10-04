import unittest
import focus_identity_residual as r


class ResidualTests(unittest.TestCase):
    def setUp(self):
        self.t=r.d.torch_runtime();self.t.set_num_threads(2);self.t.manual_seed(42)
        self.base=r.d.model(r.d.PAIRED_TEMPORAL_CONFIG).eval()
        self.net=r.model(self.base)
        self.x=self.t.rand(4,6,128,192)
        self.x[2:,3:]=self.x[2:,:3]

    def test_zero_initialization(self):
        with self.t.no_grad():
            a=r.c.score_change(self.base,self.x,r.CONFIG)
            b=r.c.score_change(self.net,self.x,r.CONFIG)
        self.assertTrue(self.t.equal(a,b))

    def test_identity_cancels_after_nonzero_weights(self):
        z=self.net.change_inputs(self.x)
        self.assertTrue(self.t.equal(z[2:,1:],self.t.zeros_like(z[2:,1:])))
        with self.t.no_grad():self.net.change.linear.weight.normal_()
        self.assertTrue(self.t.equal(self.net.change(z)[2:],z[2:,:1]))

    def test_fit_freezes_baseline_and_replays(self):
        frozen={k:v.clone() for k,v in self.net.state_dict().items() if not k.startswith('change.')}
        cfg=dict(r.CONFIG,epochs=2,originalGroupCount=2,derivedGroupCount=2)
        net,_=r.d.fit_change_head(self.net,self.x,self.t.tensor([1.,0.,0.,0.]),cfg)
        self.assertTrue(all(self.t.equal(v,net.state_dict()[k]) for k,v in frozen.items()))
        replay=r.model(self.base);replay.load_state_dict(net.state_dict())
        self.assertTrue(self.t.equal(r.c.score_change(net,self.x,cfg),r.c.score_change(replay,self.x,cfg)))
        self.assertEqual(sum(v.numel() for v in net.parameters() if v.requires_grad),576)

    def test_bad_inputs(self):
        for x in (self.x[:,:3],self.x*2,self.x*float('nan')):
            with self.assertRaises(ValueError):self.net.change_inputs(x)


if __name__=='__main__':unittest.main()
