"""Check rotating coverage and training-only preservation requirements."""
import copy
import unittest
import numpy as np
import torch
import balance342 as b
import native_adapt152 as n
from test_native_adapt152 import Toy


class BalanceTests(unittest.TestCase):
    def test_equal_budget_and_complete_coverage(self):
        rows=[dict(role='train',changed=i%2) for i in range(16)]
        y=np.array([0,1]*8);idx=np.arange(16)
        result=b.schedule(y,rows,idx,3,4)
        self.assertEqual(result.shape,(4,16))
        self.assertEqual(set(result[result<16].flatten()),set(range(16)))
        for epoch in result:
            self.assertEqual(int(sum(epoch>=16)),4)
            self.assertTrue(np.array_equal(epoch[y==1],idx[y==1]))
        self.assertTrue(np.array_equal(result,b.schedule(y,rows,idx,3,4)))

    def test_role_and_label_rejection(self):
        with self.assertRaisesRegex(ValueError,'training_roles'):
            b.schedule([0,1],[dict(role='test',changed=0),dict(role='train',changed=1)],[0,1],2,2)
        with self.assertRaisesRegex(ValueError,'schedule_alignment'):
            b.schedule([0,1],[dict(role='train',changed=1),dict(role='train',changed=0)],[0,1],2,2)

    def test_rotating_trainer_and_preservation(self):
        torch.manual_seed(1);net=Toy();x=torch.rand(4,6,128,192);y=torch.tensor([0.,1.,0.,1.])
        aux=x.clone();indices=torch.tensor([[0,1,2,3],[2,1,0,3]])
        cfg=dict(n.CONFIG,epochs=2,batch=2)
        trained,history=n.fit(net,x,y,cfg,auxiliary_inputs=aux,auxiliary_weight=.25,auxiliary_indices=indices,
             preservation_logits=torch.tensor([-3.,3.,-3.,3.]),
             auxiliary_preservation_logits=torch.tensor([-3.,3.,0.,0.]),preservation_weight=1.)
        self.assertEqual(len(history),2)
        self.assertTrue(all(torch.isfinite(v).all() for v in trained.parameters()))

    def test_invalid_preservation_rejected(self):
        x=torch.zeros(2,6,128,192);y=torch.tensor([0.,1.]);cfg=dict(n.CONFIG,epochs=1)
        for reference in (torch.zeros(3),torch.tensor([0.,float('nan')])):
            with self.assertRaisesRegex(ValueError,'preservation_reference'):
                n.fit(Toy(),x,y,cfg,preservation_logits=reference,preservation_weight=1.)
        with self.assertRaisesRegex(ValueError,'preservation_missing'):
            n.fit(Toy(),x,y,cfg,preservation_weight=1.)

    def test_zero_weight_keeps_previous_behavior(self):
        torch.manual_seed(5);net=Toy();other=copy.deepcopy(net)
        x=torch.rand(2,6,128,192);y=torch.tensor([0.,1.]);cfg=dict(n.CONFIG,epochs=2,batch=2)
        first,_=n.fit(net,x,y,cfg);second,_=n.fit(other,x,y,cfg,preservation_weight=0.)
        for key,value in first.state_dict().items():self.assertTrue(torch.equal(value,second.state_dict()[key]))

    def test_preservation_penalty_uses_only_correct_confident_targets(self):
        x=torch.zeros(2,6,128,192);y=torch.tensor([0.,1.]);cfg=dict(n.CONFIG,epochs=1,batch=2)
        def loss(reference):
            net=Toy()
            with torch.no_grad():net.change.weight.zero_();net.change.bias.zero_()
            _,history=n.fit(net,x,y,cfg,preservation_logits=reference,preservation_weight=1.)
            return history[0]['loss']
        base=loss(torch.zeros(2))
        self.assertAlmostEqual(loss(torch.tensor([3.,-3.])),base,places=6)
        self.assertAlmostEqual(loss(torch.tensor([-6.,6.])),base+9.,places=5)
        self.assertAlmostEqual(loss(torch.tensor([-3.,3.])),base+9.,places=5)


if __name__=='__main__':unittest.main()
