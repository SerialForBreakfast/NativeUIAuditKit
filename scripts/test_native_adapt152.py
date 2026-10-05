import copy
import unittest
import torch
import native_adapt152 as n


class Toy(torch.nn.Module):
    def __init__(self):
        super().__init__();self.geometry=torch.nn.Linear(1,1);self.change=torch.nn.Linear(6,1)
    def change_inputs(self,x):return x.mean((2,3))


class NativeAdaptTests(unittest.TestCase):
    def test_linear_only_real_architecture_preserves_features(self):
        torch.manual_seed(17);net=n.make_model(torch,paired_context=True)
        before={k:v.clone() for k,v in net.state_dict().items()}
        x=torch.rand(2,6,128,192);y=torch.tensor([0.,1.])
        net,_=n.fit(net,x,y,dict(n.CONFIG,epochs=2,batch=2,linearOnly=True))
        changed=[]
        for key,value in net.state_dict().items():
            if not torch.equal(value,before[key]):changed.append(key)
        self.assertTrue(changed)
        self.assertTrue(all(k.startswith(('change.8.','change.10.')) for k in changed))
        with self.assertRaisesRegex(ValueError,'linear_scope_architecture'):
            n.fit(Toy(),x,y,dict(n.CONFIG,epochs=1,linearOnly=True))
        with self.assertRaisesRegex(ValueError,'training_scope'):
            n.fit(Toy(),x,y,dict(n.CONFIG,epochs=1,linearOnly='yes'))

    def test_deterministic_fit_and_frozen_geometry(self):
        torch.manual_seed(9);net=Toy();other=copy.deepcopy(net)
        before={k:v.clone() for k,v in net.geometry.state_dict().items()}
        x=torch.rand(3,6,128,192);y=torch.tensor([0.,1.,1.]);cfg=dict(n.CONFIG,epochs=3,batch=2)
        a,h=n.fit(net,x,y,cfg);b,j=n.fit(other,x,y,cfg)
        self.assertEqual([v['loss'] for v in h],[v['loss'] for v in j])
        for key,value in a.state_dict().items():self.assertTrue(torch.equal(value,b.state_dict()[key]))
        for key,value in before.items():self.assertTrue(torch.equal(value,a.geometry.state_dict()[key]))
        self.assertEqual(len(h),3)

    def test_invalid_inputs_and_configuration(self):
        x=torch.zeros(2,6,128,192);y=torch.tensor([0.,1.]);net=Toy()
        for bad in (torch.tensor([0.,2.]),torch.tensor([0.,float('nan')])):
            with self.assertRaises(ValueError):n.fit(net,x,bad,n.CONFIG)
        for cfg in (dict(n.CONFIG,epochs=0),dict(n.CONFIG,batch=0),dict(n.CONFIG,lr=float('nan'))):
            with self.assertRaises(ValueError):n.fit(net,x,y,cfg)

    def test_nonfinite_model_stops(self):
        net=Toy();net.change.bias.data.fill_(float('nan'))
        with self.assertRaisesRegex(ValueError,'nonfinite_loss'):
            n.fit(net,torch.zeros(2,6,128,192),torch.zeros(2),dict(n.CONFIG,epochs=1))


if __name__=='__main__':unittest.main()
