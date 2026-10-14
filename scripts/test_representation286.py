"""Check local residual inputs without changing the shared model definition."""
import unittest
import torch
import representation286 as r


class RepresentationTests(unittest.TestCase):
    def test_constant_change(self):
        x=torch.zeros(2,6,16,24);x[:,3:]=.5
        result=r.change_inputs(None,x)
        self.assertTrue(torch.equal(result[:,:3],torch.zeros_like(result[:,:3])))
        self.assertTrue(torch.equal(result[:,3:],x))

    def test_edges_and_frame_order(self):
        x=torch.zeros(1,6,16,24);x[:,3:,5:10,5:10]=1
        a=r.change_inputs(None,x)
        b=r.change_inputs(None,torch.cat((x[:,3:],x[:,:3]),1))
        self.assertGreater(float(a[:,:3].sum()),0)
        self.assertTrue(torch.equal(a[:,:3],b[:,:3]))
        self.assertTrue(((a>=0)&(a<=1)).all())

    def test_no_parameter_change(self):
        model=r.base.worker.make_model(torch,paired_context=True)
        before={k:v.clone() for k,v in model.state_dict().items()}
        r.treatment(model)
        self.assertTrue(all(torch.equal(v,model.state_dict()[k]) for k,v in before.items()))


if __name__=='__main__':unittest.main()
