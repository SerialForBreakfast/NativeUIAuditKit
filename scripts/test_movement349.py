import unittest
import numpy as np
import movement349 as m


class MovementTests(unittest.TestCase):
    def test_normalized_class_emphasis(self):
        y=np.array([0.,0.,1.],np.float32);w=np.array([1.,2.,3.],np.float32)
        factors=m.class_weights(y,w)
        self.assertAlmostEqual(float(factors[1]/factors[0]),2.)
        self.assertAlmostEqual(float((w*factors[y.astype(int)]).sum()),float(w.sum()))

    def test_missing_class(self):
        with self.assertRaisesRegex(ValueError,'class_support'):
            m.class_weights(np.zeros(2),np.ones(2))

    def test_fit_scope_and_optional_weights(self):
        t=m.t;t.set_num_threads(2);t.manual_seed(42)
        class Change(t.nn.Module):
            def __init__(self):
                super().__init__();self.whole=t.nn.Linear(6,1);self.detail=t.nn.Linear(12,1);self.correction=t.nn.Linear(1,1)
            def forward(self,x):
                v=x.mean((2,3));return self.whole(v[:,:6])+self.correction(self.detail(v[:,6:]))
        class Net(t.nn.Module):
            def __init__(self):super().__init__();self.change=Change()
            def change_inputs(self,x):return x
        net=Net()
        x=t.rand(2,6,128,192);d=t.rand(2,12,128,192);y=t.tensor([0.,1.]);before=x.clone()
        initial={k:v.clone() for k,v in net.state_dict().items()}
        settings=dict(epochs=1,lr=.0001,batch=2,seed=42,threads=2,detailOnly=True)
        net,_=m.a.b.trainer.fit(net,x,y,settings,detail_inputs=d,auxiliary_inputs=x.clone(),
            auxiliary_detail=d.clone(),auxiliary_weight=.25,auxiliary_class_weights=t.tensor([2/3,4/3]))
        self.assertTrue(t.equal(x,before))
        changed=[k for k,v in net.state_dict().items() if not t.equal(v,initial[k])]
        self.assertTrue(changed)
        self.assertTrue(all(k.startswith(('change.detail.','change.correction.')) for k in changed))
        with self.assertRaisesRegex(ValueError,'auxiliary_class_weights'):
            m.a.b.trainer.fit(net,x,y,settings,detail_inputs=d,auxiliary_inputs=x,
                auxiliary_detail=d,auxiliary_weight=.25,auxiliary_class_weights=t.tensor([0.,1.]))
        import copy
        left=copy.deepcopy(net);right=copy.deepcopy(net)
        kwargs=dict(detail_inputs=d,auxiliary_inputs=x,auxiliary_detail=d,auxiliary_weight=.25)
        left,_=m.a.b.trainer.fit(left,x,y,settings,**kwargs)
        right,_=m.a.b.trainer.fit(right,x,y,settings,auxiliary_class_weights=t.ones(2),**kwargs)
        self.assertTrue(all(t.equal(v,right.state_dict()[k]) for k,v in left.state_dict().items()))


if __name__=='__main__':unittest.main()
