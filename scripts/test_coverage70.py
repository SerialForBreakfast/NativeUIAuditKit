import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
import focus_direct_transition as d
from focus_pair_translation import transform,DEFAULT_POLICY,BROAD_POLICY,COMPRESSED_POLICY
from focus_translation_training import banks,schedule


class CoverageTests(unittest.TestCase):
    def test_exact_rounded_affine_and_pair_alignment(self):
        a=Image.new('RGB',(101,80),'white');boxes=[[20,20,60,4]]*2
        pair,truth=transform([a,a],boxes,'right',COMPRESSED_POLICY)
        np.testing.assert_allclose(truth,[[20*50/101+50,20,60*50/101,4]]*2,rtol=0,atol=1e-12)
        self.assertEqual(truth[0],truth[1])
        self.assertEqual(pair[0].tobytes(),pair[1].tobytes())
        self.assertEqual(pair[0].size,a.size)
        self.assertEqual(transform([a,a],boxes,'right',BROAD_POLICY),(None,None))
        self.assertEqual(transform([a,a],boxes,'baseline',COMPRESSED_POLICY)[1],boxes)
        with self.assertRaises(ValueError):transform([a,a],boxes,'left','unknown')

    def test_joint_preparation_decodes_each_pair_once_and_keeps_roles(self):
        row=dict(id='a',split='train',images=[{},{}],size=[100,80],boxes=[[20,20,60,4]]*2,changed=False)
        with patch.object(d,'pixels',return_value=Image.new('RGB',(100,80),'white')) as pixels:
            result=banks([row],[BROAD_POLICY,COMPRESSED_POLICY])
        self.assertEqual(pixels.call_count,2)
        self.assertEqual(len(result[BROAD_POLICY][3]),3);self.assertEqual(len(result[COMPRESSED_POLICY][3]),5)
        self.assertEqual(result[BROAD_POLICY][1][:,-1].tolist(),[0]*3)
        self.assertEqual(schedule(result[BROAD_POLICY][2],600,42),schedule(result[BROAD_POLICY][2],600,42))
        with self.assertRaises(ValueError):banks([dict(row,split='development')],[BROAD_POLICY])

    def test_configs_change_only_augmentation_and_preserve_initial_weights(self):
        t=d.torch_runtime();t.manual_seed(42);old=d.model(d.TEMPORAL_CONFIG).state_dict()
        for config in d.COVERAGE_CONFIGURATIONS:
            self.assertEqual(dict(config,augmentation=DEFAULT_POLICY),d.TEMPORAL_CONFIG)
            t.manual_seed(42);new=d.model(config).state_dict()
            self.assertTrue(all(t.equal(v,new[k]) for k,v in old.items()))


if __name__=='__main__':unittest.main()
