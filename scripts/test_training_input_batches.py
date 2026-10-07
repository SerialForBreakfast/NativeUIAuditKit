"""Check bounded validation and exact fitting parity on authored tensors."""
import copy
import inspect
import unittest
from unittest.mock import patch
import torch
import native_adapt152 as n


class ValidationBatchTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(2);torch.manual_seed(7)
        self.x=torch.rand(9,6,128,192);self.y=torch.arange(9).remainder(2).float()
        self.net=n.make_model(torch,paired_context=True)
        self.config=dict(n.CONFIG,epochs=1,batch=3)

    def test_exact_fit_parity(self):
        source=inspect.getsource(n.fit)
        chunk="    # Bound validation masks without changing sample order or optimization.\n    for part in x.split(8):\n        h.require(torch.isfinite(part).all() and ((part>=0)&(part<=1)).all(),'training_inputs')\n"
        self.assertIn(chunk,source)
        namespace=dict(n.__dict__)
        exec(source.replace(chunk,"    h.require(torch.isfinite(x).all() and ((x>=0)&(x<=1)).all(),'training_inputs')\n"),namespace)
        old,oh=namespace['fit'](copy.deepcopy(self.net),self.x,self.y,self.config)
        new,nh=n.fit(copy.deepcopy(self.net),self.x,self.y,self.config)
        self.assertEqual(oh[0]['loss'],nh[0]['loss'])
        for name,value in old.state_dict().items():self.assertTrue(torch.equal(value,new.state_dict()[name]),name)

    def test_validation_masks_are_bounded(self):
        sizes=[];original=torch.isfinite
        def record(value):
            if value.ndim==4 and value.shape[1:]==(6,128,192):sizes.append(len(value))
            return original(value)
        with patch.object(torch,'isfinite',side_effect=record):n.fit(self.net,self.x,self.y,self.config)
        self.assertEqual(sizes,[8,1])

    def test_last_batch_invalid_values_stop_before_optimizer(self):
        for value in [float('nan'),float('inf'),-.01,1.01]:
            x=self.x.clone();x[-1,0,0,0]=value
            with self.subTest(value=value),patch.object(torch.optim,'Adam') as optimizer:
                with self.assertRaisesRegex(ValueError,'training_inputs'):n.fit(self.net,x,self.y,self.config)
                optimizer.assert_not_called()


if __name__=='__main__':unittest.main()
