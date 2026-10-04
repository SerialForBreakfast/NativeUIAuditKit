import unittest
import focus_direct_transition as d
import focus_spatial_transition as s
import plan_stationary_transitions as planner


class OverlapTests(unittest.TestCase):
    def test_stationary_matrix_is_development_only(self):
        plan=planner.validate(planner.catalog())
        self.assertEqual(len(plan['cases']),24)
        self.assertEqual(sum(c['expectedFocusChanged'] for c in plan['cases']),12)
        self.assertTrue(all(not c['expectedScrolled'] and c['partition']=='development' for c in plan['cases']))
        self.assertFalse(plan['executionEligible'])
        plan['cases'][0]['partition']='evaluation'
        with self.assertRaises(ValueError):planner.validate(plan)

    def test_identity_decode_and_loss(self):
        t=d.torch_runtime();truth=t.tensor([[.5,.4,.8,.06,.3,.7,.1,.2]])
        indices,values=s.targets(t,truth)
        decoded=s.decode_geometry(t,indices,values,16,24)
        t.testing.assert_close(decoded.reshape(1,8),truth)
        self.assertLess(abs(float(s.giou_loss(t,decoded,truth))),1e-6)

    def test_oversized_thin_box_correcting_gradient(self):
        t=d.torch_runtime();pred=t.tensor([[[.5,.4,.8,.14]]],requires_grad=True)
        truth=t.tensor([[[.5,.4,.8,.06]]])
        loss=s.giou_loss(t,pred,truth);loss.backward()
        self.assertGreater(float(pred.grad[0,0,3]),0)
        self.assertTrue(bool(t.isfinite(pred.grad).all()))

    def test_model_and_objective(self):
        t=d.torch_runtime();t.manual_seed(42);old=d.model(d.GEOMETRY_DIAGNOSTIC)
        t.manual_seed(42);net=d.model(d.OVERLAP_DIAGNOSTIC)
        self.assertTrue(all(t.equal(v,net.state_dict()[k]) for k,v in old.state_dict().items()))
        x=t.rand(2,6,64,96);y=t.tensor([[.5,.4,.8,.06,.5,.6,.8,.06,1.],[.3,.3,.1,.2,.3,.3,.1,.2,0.]])
        loss=s.loss(t,net,x,y,True,True);loss.backward()
        self.assertTrue(all(bool(t.isfinite(p.grad).all()) for p in net.parameters()))
        with self.assertRaises(ValueError):d.model(dict(d.OVERLAP_CONFIG,width=192))


if __name__=='__main__':unittest.main()
