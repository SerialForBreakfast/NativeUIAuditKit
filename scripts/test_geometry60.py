import unittest
import focus_direct_transition as d
import focus_spatial_transition as s


class LogitTests(unittest.TestCase):
    def test_collapsed_extent_gradient_and_boundary_targets(self):
        t=d.torch_runtime()
        grads=[]
        for mode in ('bce','logit'):
            x=t.tensor([-7.],requires_grad=True)
            loss=s.geometry_loss(t,x,t.tensor([.06328]),mode=='bce',mode=='logit')
            loss.backward();grads.append(float(x.grad))
        self.assertLess(grads[1],grads[0]);self.assertLess(grads[0],0)
        self.assertGreater(abs(grads[1]),10*abs(grads[0]))
        x=t.zeros(2,requires_grad=True)
        s.geometry_loss(t,x,t.tensor([0.,1.]),logit_regression=True).backward()
        self.assertTrue(bool(t.isfinite(x.grad).all()))
        self.assertGreater(float(x.grad[0]),0);self.assertLess(float(x.grad[1]),0)

    def test_fixed_architecture_and_finite_objective(self):
        t=d.torch_runtime();t.manual_seed(42);old=d.model(d.OVERLAP_DIAGNOSTIC)
        t.manual_seed(42);net=d.model(d.LOGIT_DIAGNOSTIC)
        self.assertTrue(all(t.equal(v,net.state_dict()[k]) for k,v in old.state_dict().items()))
        x=t.rand(2,6,64,96);y=t.tensor([[.5,.4,.8,.06,.5,.6,.8,.06,1.],[.3,.3,.1,.2,.3,.3,.1,.2,0.]])
        s.loss(t,net,x,y,overlap=True,logit_regression=True).backward()
        self.assertTrue(all(bool(t.isfinite(p.grad).all()) for p in net.parameters()))
        restored=d.model(d.LOGIT_CONFIG);restored.load_state_dict(net.state_dict())
        t.testing.assert_close(restored(x),net(x),rtol=0,atol=0)


if __name__=='__main__':unittest.main()
