"""Check the optional gradient projection and unchanged trainer behavior."""
import copy
import unittest
from unittest.mock import patch
import torch
import native_adapt152 as trainer


class ConflictTests(unittest.TestCase):
    def test_opposing(self):
        a=torch.tensor([1.,0.]); b=torch.tensor([-1.,1.])
        pa,pb,used=trainer.project_conflicting_gradients(a,b)
        self.assertTrue(used)
        torch.testing.assert_close(pa,torch.tensor([.5,.5]))
        torch.testing.assert_close(pb,torch.tensor([0.,1.]))
        self.assertEqual(float(pa@b),0.)
        self.assertEqual(float(pb@a),0.)
        torch.testing.assert_close(a,torch.tensor([1.,0.]))

    def test_identity_and_zero(self):
        for a,b in [(torch.tensor([1.,2.]),torch.tensor([2.,1.])),
                    (torch.zeros(2),torch.ones(2))]:
            pa,pb,used=trainer.project_conflicting_gradients(a,b)
            self.assertFalse(used); self.assertIs(pa,a); self.assertIs(pb,b)

    def test_nonfinite(self):
        with self.assertRaisesRegex(ValueError,'projection_inputs'):
            trainer.project_conflicting_gradients(torch.tensor([float('nan')]),torch.ones(1))

    def test_antiparallel_and_small_norm(self):
        for scale in (1.,1e-25):
            a=torch.tensor([scale,0.]); b=-2*a
            pa,pb,used=trainer.project_conflicting_gradients(a,b)
            self.assertTrue(used)
            self.assertTrue(torch.equal(pa,torch.zeros_like(a)))
            self.assertTrue(torch.equal(pb,torch.zeros_like(b)))

    def test_weighted_remainder_is_preserved(self):
        class Model(torch.nn.Module):
            def __init__(self):
                super().__init__(); self.change=torch.nn.Linear(6,1)
            def change_inputs(self,x): return x.mean((2,3))
        torch.manual_seed(3)
        net=Model(); x=torch.rand(3,6,128,192)
        y=torch.tensor([0.,1.,1.]); weights=torch.tensor([2.,3.,4.])
        params=list(net.parameters())
        losses=torch.nn.functional.binary_cross_entropy_with_logits(
            net.change(net.change_inputs(x)).flatten(),y,weight=weights,reduction='none')
        gradients=[torch.cat([v.flatten() for v in torch.autograd.grad(losses[i]/3,params,retain_graph=True)])
                   for i in range(3)]
        a,b,_=trainer.project_conflicting_gradients(*gradients[:2])
        expected=a+b+gradients[2]; observed=[]
        def capture(optimizer,*args,**kwargs):
            observed.append(torch.cat([p.grad.flatten() for g in optimizer.param_groups for p in g['params']]))
        with patch.object(torch.optim.Adam,'step',capture):
            trainer.fit(net,x,y,dict(trainer.CONFIG,epochs=1,batch=3),weights=weights,
                        conflict_groups=torch.tensor([0,1,-1]))
        torch.testing.assert_close(observed[0],expected,atol=1e-7,rtol=1e-5)

    def test_trainer_parity_and_determinism(self):
        torch.manual_seed(9); torch.set_num_threads(2)
        x=torch.rand(4,6,128,192); y=torch.tensor([0.,1.,0.,1.])
        model=trainer.make_model(torch,paired_context=True)
        config=dict(trainer.CONFIG,epochs=2,batch=4)
        first,_=trainer.fit(copy.deepcopy(model),x,y,config)
        absent,_=trainer.fit(copy.deepcopy(model),x,y,config,conflict_groups=torch.full((4,),-1))
        for key,value in first.state_dict().items():
            self.assertTrue(torch.equal(value,absent.state_dict()[key]),key)
        groups=y.long(); weights=torch.tensor([1.,2.,3.,4.])
        second,h=trainer.fit(copy.deepcopy(model),x,y,config,weights=weights,conflict_groups=groups)
        repeat,rh=trainer.fit(copy.deepcopy(model),x,y,config,weights=weights,conflict_groups=groups)
        self.assertEqual([v['loss'] for v in h],[v['loss'] for v in rh])
        self.assertEqual(sum(v['pairedBatches'] for v in h),2)
        for key,value in second.state_dict().items():
            self.assertTrue(torch.equal(value,repeat.state_dict()[key]),key)
            if not key.startswith('change.'):
                self.assertTrue(torch.equal(value,model.state_dict()[key]),key)
        with self.assertRaisesRegex(ValueError,'conflict_labels'):
            trainer.fit(copy.deepcopy(model),x,y,config,conflict_groups=1-groups)


if __name__=='__main__': unittest.main()
