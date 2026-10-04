import copy
import unittest
import numpy as np
import focus_candidate_ranker as r


class SizeFeatureTests(unittest.TestCase):
    def fixture(self):
        return dict(frames=[dict(id='a',size=[200,100],candidates=[dict(id='c',bounds=[10,20,40,30])])])

    def test_only_size_and_scale_invariance(self):
        inputs=self.fixture();x=np.zeros((1,768),dtype=np.float32)
        result=r.features(x,inputs,r.SIZE_CONFIG)
        np.testing.assert_array_equal(result[:,:768],x)
        np.testing.assert_allclose(result[:,-2:],[[.2,.3]])
        moved=copy.deepcopy(inputs);moved['frames'][0]['candidates'][0]['bounds'][:2]=[80,40]
        moved['frames'][0].update(id='different',split='development',truth='ignored')
        np.testing.assert_array_equal(result,r.features(x,moved,r.SIZE_CONFIG))
        doubled=copy.deepcopy(inputs);doubled['frames'][0]['size']=[400,200]
        doubled['frames'][0]['candidates'][0]['bounds']=[20,40,80,60]
        np.testing.assert_array_equal(result,r.features(x,doubled,r.SIZE_CONFIG))
        self.assertIs(r.features(x,inputs,r.NATIVE_CONFIG),x)

    def test_bad_sizes_and_shape(self):
        for size,bounds in [([0,100],[0,0,20,20]),([200,100],[0,0,-1,20]),([200,100],[0,0,201,20]),([200,100],[0,0,float('nan'),20])]:
            inputs=self.fixture();inputs['frames'][0].update(size=size)
            inputs['frames'][0]['candidates'][0]['bounds']=bounds
            with self.assertRaises(ValueError):r.features(np.zeros((1,768),dtype=np.float32),inputs,r.SIZE_CONFIG)
        with self.assertRaises(ValueError):r.features(np.zeros((2,768),dtype=np.float32),self.fixture(),r.SIZE_CONFIG)

    def test_matched_visual_initialization_and_checkpoint(self):
        torch=r.d.torch_runtime();torch.set_num_threads(2)
        torch.manual_seed(42);old=r.model(torch,r.NATIVE_CONFIG)
        torch.manual_seed(42);new=r.model(torch,r.SIZE_CONFIG)
        self.assertTrue(torch.equal(old[0].weight,new[0].weight[:,:768]))
        self.assertTrue(torch.equal(old[0].bias,new[0].bias))
        self.assertTrue(torch.equal(old[2].weight,new[2].weight))
        self.assertTrue(torch.equal(old[2].bias,new[2].bias))
        self.assertTrue(torch.count_nonzero(new[0].weight[:,768:])==0)
        x=torch.rand((3,768));sizes=torch.rand((3,2));aug=torch.cat((x,sizes),1)
        with torch.inference_mode():self.assertTrue(torch.allclose(old(x),new(aug),atol=1e-6,rtol=0))
        other=r.model(torch,r.SIZE_CONFIG);other.load_state_dict(new.state_dict())
        with torch.inference_mode():self.assertTrue(torch.equal(new(aug),other(aug)))
        with self.assertRaises(RuntimeError):old.load_state_dict(new.state_dict())


if __name__=='__main__':unittest.main()
