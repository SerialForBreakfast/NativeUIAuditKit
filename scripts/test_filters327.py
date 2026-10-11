"""Check indexed training, detail learning, and frozen parameters."""
import copy
import unittest
import torch
import filters327 as f


class FilterTests(unittest.TestCase):
    def setUp(self):torch.set_num_threads(2);torch.manual_seed(42)

    def model(self):return f.r.extend(f.r.s.c.model.extend(f.b.worker.make_model(torch,paired_context=True)),2)

    def test_indexed_matches_expanded(self):
        net=self.model();other=copy.deepcopy(net)
        x=torch.rand(4,6,128,192);detail=torch.rand(4,12,128,192);y=torch.tensor([0.,1.,0.,1.])
        aux=torch.rand(2,6,128,192);ad=torch.rand(2,12,128,192);ids=torch.tensor([0,1,0,1])
        config=dict(epochs=1,lr=.001,batch=2,seed=42,threads=2,detailOnly=True)
        before={k:v.clone() for k,v in net.state_dict().items()}
        f.b.trainer.fit(net,x,y,config,detail_inputs=detail,auxiliary_inputs=aux,
            auxiliary_detail=ad,auxiliary_weight=.25,auxiliary_indices=ids)
        f.b.trainer.fit(other,x,y,config,detail_inputs=detail,auxiliary_inputs=aux[ids],
            auxiliary_detail=ad[ids],auxiliary_weight=.25)
        changed=[]
        for key,value in net.state_dict().items():
            torch.testing.assert_close(value,other.state_dict()[key],rtol=0,atol=0)
            if not torch.equal(value,before[key]):changed.append(key)
        self.assertTrue(any(k.startswith('change.detail.0.') for k in changed))
        self.assertTrue(all(k.startswith(('change.detail.','change.correction.')) for k in changed))

    def test_invalid_indices(self):
        x=torch.zeros(4,6,128,192);y=torch.tensor([0.,1.,0.,1.])
        config=dict(epochs=1,lr=.001,batch=2,seed=42,threads=2)
        for ids in (torch.tensor([0,1]),torch.tensor([0.,1.,0.,1.]),torch.tensor([0,1,-1,0]),torch.tensor([0,1,4,0])):
            with self.assertRaises(ValueError):
                f.b.trainer.fit(self.model(),x,y,config,auxiliary_inputs=x,auxiliary_weight=.25,auxiliary_indices=ids)
        with self.assertRaises(ValueError):f.b.trainer.fit(self.model(),x,y,config,auxiliary_indices=torch.arange(4))


if __name__=='__main__':unittest.main()
