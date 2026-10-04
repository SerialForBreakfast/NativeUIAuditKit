import copy
import unittest
import focus_direct_transition as d
import focus_change_adaptation as a


class ChangeAdaptationTests(unittest.TestCase):
    def test_only_change_weights_update_and_reload(self):
        torch=d.torch_runtime();torch.set_num_threads(2);torch.manual_seed(42)
        net=d.model(d.TEMPORAL_CONFIG);before={k:v.clone() for k,v in net.state_dict().items()}
        x=torch.rand((4,6,64,96));labels=torch.tensor([0.,1.,0.,1.])
        fitted,history=d.fit_change_head(net,x,labels,dict(a.CONFIG,epochs=2))
        self.assertEqual(len(history),2)
        self.assertTrue(all(torch.equal(v,fitted.state_dict()[k]) for k,v in before.items() if not k.startswith('change.')))
        self.assertTrue(any(not torch.equal(v,fitted.state_dict()[k]) for k,v in before.items() if k.startswith('change.')))
        self.assertTrue(all(p.grad is None for k,p in fitted.named_parameters() if not k.startswith('change.')))
        other=d.model(d.TEMPORAL_CONFIG);other.load_state_dict(fitted.state_dict());other.eval()
        with torch.inference_mode():self.assertTrue(torch.equal(fitted(x),other(x)))

    def test_invalid_shape_range_labels_and_nan(self):
        torch=d.torch_runtime();net=d.model(d.TEMPORAL_CONFIG)
        x=torch.zeros((2,6,64,96));labels=torch.tensor([0.,1.])
        cases=[(x[:,:,:,:95],labels),(x+2,labels),(x,torch.tensor([0.,.5])),(x*float('nan'),labels),(x,labels[:1])]
        for data,target in cases:
            with self.assertRaisesRegex(ValueError,'adaptation_inputs'):
                d.fit_change_head(net,data,target,dict(a.CONFIG,epochs=1))


if __name__=='__main__':unittest.main()
