import copy
import unittest
import torch
import dual130 as d


class DualTests(unittest.TestCase):
    def test_strided_cache_column_replays_contiguous_sigmoid(self):
        z=torch.linspace(-20,20,433*3).reshape(433,3)
        actual=d.probabilities(z[:,0]);v=z[:,0].contiguous()
        expected=torch.cat([v[:424].sigmoid(),v[424:].sigmoid()]).numpy()
        self.assertTrue((actual==expected).all())

    def test_zero_correction_and_identity_anchor(self):
        net=d.model();z=torch.zeros(3,1153);z[:,0]=torch.tensor([-3.,0.,3.])
        torch.testing.assert_close(net.change(z).flatten(),z[:,0],rtol=0,atol=0)
        with torch.no_grad():net.change.linear.weight.fill_(2.)
        torch.testing.assert_close(net.change(z).flatten(),z[:,0],rtol=0,atol=0)

    def test_factored_trainer_matches_pixel_entrypoint(self):
        class Net(torch.nn.Module):
            def __init__(self):
                super().__init__();self.change=torch.nn.Linear(2,1);self.frozen=torch.nn.Parameter(torch.tensor(4.))
            def change_inputs(self,x):
                return torch.stack([(x[:,:3]-x[:,3:]).abs().mean((1,2,3)),x.mean((1,2,3))],1).detach()
        torch.manual_seed(3);x=torch.rand(4,6,64,96);x[2:,3:]=x[2:,:3]
        y=torch.tensor([1.,0.,0.,0.]);net=Net();other=copy.deepcopy(net)
        config=dict(threads=2,seed=42,epochs=5,lr=.01,originalGroupCount=2,derivedGroupCount=2,lossWeighting='equal-group-means')
        z=other.change_inputs(x)
        trained,h1=d.a.r.d.fit_change_head(net,x,y,config)
        matched,h2=d.a.r.d.fit_change_features(other,z,y,config)
        self.assertEqual(h1,h2)
        for key,value in trained.state_dict().items():torch.testing.assert_close(value,matched.state_dict()[key],rtol=0,atol=0)
        self.assertEqual(float(trained.frozen),4.)

    def test_feature_validation(self):
        net=d.model();config=dict(threads=2,seed=42,epochs=1,lr=.01)
        with self.assertRaises(ValueError):d.a.r.d.fit_change_features(net,torch.full((1,1153),float('nan')),torch.zeros(1),config)
        with self.assertRaises(ValueError):d.a.r.d.fit_change_features(net,torch.zeros(1,1153,requires_grad=True),torch.zeros(1),config)


if __name__=='__main__':unittest.main()
