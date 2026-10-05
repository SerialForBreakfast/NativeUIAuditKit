import unittest
import torch
import pool167 as p

class PoolTests(unittest.TestCase):
    def test_pool_contract_and_reload(self):
        net=p.n.make_model(torch,paired_context=True);before=set(net.state_dict());count=sum(x.numel() for x in net.parameters())
        p.pooled(net,torch);self.assertEqual(before,set(net.state_dict()));self.assertEqual(count,sum(x.numel() for x in net.parameters()))
        x=torch.randn(2,24,8,12,requires_grad=True);out=net.change[6](x)
        self.assertEqual(tuple(out.shape),(2,24,4,6))
        self.assertTrue(torch.allclose(out,net.change[6](x.flip(-1)),atol=1e-6))
        out.sum().backward();self.assertTrue(torch.isfinite(x.grad).all())
        state=dict(version='pool167-v1',pooling='global-broadcast-4x6',state=net.state_dict())
        other=p.load(torch,state);self.assertTrue(torch.equal(net.change[6](x),other.change[6](x)))
        with self.assertRaisesRegex(ValueError,'checkpoint_architecture'):p.load(torch,dict(state,pooling='legacy'))

if __name__=='__main__':unittest.main()
