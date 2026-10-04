import unittest
import numpy as np
import joint_replay138 as j


class JointTests(unittest.TestCase):
    def test_zero_slack_can_collapse_radial_learning(self):
        # Diagnostic regression: this preserves the observed limitation, not a fix.
        torch=j.d.a.r.d.torch_runtime()
        x=np.zeros((1,1153),np.float32);x[0,0]=1.75;x[0,1]=1
        net=j.a.t.retention.constrained_model(x,np.ones(1,np.float32))
        net.change.linear.weight.data[0,0]=-1
        loss=net.change(torch.from_numpy(x)).sum();loss.backward()
        self.assertEqual(float(net.change.effective()[1].detach()),0)
        self.assertEqual(float(net.change.linear.weight.grad.norm()),0)

    def test_exact_five_family_weighting(self):
        cache={k:np.full((433,1153),i,np.float32) for i,k in enumerate(('original','contrast_0','contrast_1'))}
        cache['peer']=np.tile(np.arange(11,dtype=np.float32)[:,None],(1,1153))
        families=dict(within_screen=list(range(5)),screen_transition=[5,6],identical_control=[7,8])
        labels=np.arange(433)%2;x,y=j.bank(cache,labels,families)
        self.assertEqual(x.shape,(21650,1153))
        for k,ids in enumerate(families.values()):
            counts=[np.sum(x[k*4330:(k+1)*4330,0]==i) for i in ids]
            self.assertEqual(sum(counts),4330);self.assertEqual(len(set(counts)),1)
        np.testing.assert_array_equal(y[12990:17320],np.tile(labels,10))
        families['within_screen']=[0]*5
        with self.assertRaises(ValueError):j.bank(cache,labels,families)

    def test_only_confident_correct_contrast_constrains(self):
        cache={k:np.zeros((433,1153),np.float32) for k in ('original','contrast_0','contrast_1')}
        labels=np.zeros(433,np.float32);ref={k:np.full(433,.5,np.float32) for k in ('contrast_0','contrast_1')}
        ref['contrast_0'][1]=.01;ref['contrast_1'][2]=.99
        z,y,ids=j.protected(cache,labels,ref)
        self.assertEqual(len(z),208);self.assertEqual(ids,dict(contrast_0=[1],contrast_1=[]))
        self.assertNotIn('global8',ids)


if __name__=='__main__':unittest.main()
