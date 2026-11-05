import unittest
import torch
from torch import nn
from role_head_projection import initialize_pair

class Head(nn.Module):
    def __init__(self):
        super().__init__();self.cv3=nn.ModuleList([nn.Sequential(nn.Conv2d(2,3,1)) for _ in range(3)])
        self.reg_max=4;self.nc=3;self.no=19
class Model(nn.Module):
    def __init__(self):
        super().__init__();self.model=nn.ModuleList([nn.Conv2d(1,2,1),Head()]);self.names={0:'a',1:'b',2:'c'}

class ProjectionTests(unittest.TestCase):
    def test_pair_preserves_non_output_and_missing_roles(self):
        src=Model().eval();r,p,receipt=initialize_pair(src,src.names,['button','text','absent'],{'a':'button','b':'button','c':'text'})
        for k,v in src.model[0].state_dict().items():self.assertTrue(torch.equal(v,r.model[0].state_dict()[k]))
        for i in range(3):
            a,b,c=src.model[-1].cv3[i][-1],r.model[-1].cv3[i][-1],p.model[-1].cv3[i][-1]
            torch.testing.assert_close(c.weight[0],a.weight[:2].mean(dim=0))
            self.assertTrue(torch.equal(b.weight[2],c.weight[2]));self.assertTrue(torch.equal(b.bias[2],c.bias[2]))
            self.assertFalse(c.training)
        self.assertEqual(receipt['randomFallbackRoles'],['absent'])
        self.assertFalse(receipt['modelAccepted'])
    def test_mean_is_not_probability_pooling(self):
        logits=torch.tensor([4.,-4.]);self.assertNotEqual(float(logits.mean().sigmoid()),float(logits.sigmoid().max()))
    def test_invalid_taxonomy_refused(self):
        src=Model()
        with self.assertRaises(ValueError):initialize_pair(src,{1:'a'},['button'],{'a':'button'})

if __name__=='__main__':unittest.main()
