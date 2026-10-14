"""Check effect measurements and retention of original training views."""
import copy
import unittest
import numpy as np
import torch
import effect312 as e
import native_adapt152 as n
from test_native_adapt152 import Toy


class EffectTests(unittest.TestCase):
    def test_two_windows_and_identical(self):
        import proposal312 as p
        x=np.zeros((6,128,192),np.float32)
        self.assertTrue(p.measure(x)['identical'])
        x[3:,20:24,20:24]=1;x[3:,90:94,150:154]=1
        result=p.measure(x)
        self.assertEqual(result['energyFraction'],1.)
        self.assertEqual(result,p.measure(np.concatenate((x[3:],x[:3]))))

    def test_zero_and_reverse(self):
        x=np.zeros((6,128,192),np.float32)
        self.assertIsNone(e.metrics(x,[])['windowEnergyFraction'])
        x[3:,50:55,100:104]=.5
        a=e.metrics(x,[]);b=e.metrics(np.concatenate((x[3:],x[:3])),[])
        self.assertEqual(a,b);self.assertEqual(a['areaAbove8'],20)

    def test_geometry_transform_and_missing(self):
        item=dict(status='measured',sourceSize=[100,80],visibleBody=[20,10,10,20])
        self.assertEqual(e.scaled_endpoints([item],(.5,.5))[0]['visibleBody'],[35.,25.,5.,10.])
        with self.assertRaisesRegex(ValueError,'missing_body'):
            e.scaled_endpoints([dict(status='missing_body')],(.5,.5))

    def test_auxiliary_keeps_original_step(self):
        torch.manual_seed(7);net=Toy();manual=copy.deepcopy(net)
        x=torch.zeros(2,6,128,192);aux=torch.ones_like(x);y=torch.tensor([0.,1.])
        weights=torch.tensor([.5,1.5]);before=x.clone()
        cfg=dict(n.CONFIG,epochs=1,batch=2)
        trained,history=n.fit(net,x,y,cfg,weights=weights,auxiliary_inputs=aux,auxiliary_weight=.25)
        opt=torch.optim.Adam(manual.change.parameters(),lr=cfg['lr'])
        loss=torch.nn.functional.binary_cross_entropy_with_logits(manual.change(manual.change_inputs(x)).flatten(),y,weight=weights)
        loss+=.25*torch.nn.functional.binary_cross_entropy_with_logits(manual.change(manual.change_inputs(aux)).flatten(),y,weight=weights)
        loss.backward();opt.step()
        for k,v in manual.state_dict().items():torch.testing.assert_close(v,trained.state_dict()[k])
        self.assertTrue(torch.equal(before,x));self.assertEqual(history[0]['updates'],1)
        self.assertEqual(history[0]['originalExamples'],2)

    def test_reject_bad_auxiliary(self):
        x=torch.zeros(2,6,128,192);y=torch.tensor([0.,1.]);cfg=dict(n.CONFIG,epochs=1)
        for kwargs in (dict(auxiliary_weight=.25),dict(auxiliary_inputs=x,auxiliary_weight=0),
                       dict(auxiliary_inputs=x[:1],auxiliary_weight=.25),
                       dict(auxiliary_inputs=x,auxiliary_weight=.25,alternate_inputs=x)):
            with self.assertRaises(ValueError):n.fit(Toy(),x,y,cfg,**kwargs)


if __name__=='__main__':unittest.main()
