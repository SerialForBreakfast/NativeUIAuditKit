"""Offline regression checks for the admitted cached-input comparison lane."""
import copy
import unittest
from unittest.mock import patch
import numpy as np
import focus_change_adaptation as a
import focus_candidate_ranker as r
import prepare_collection103 as p


class CollectionTrainingTests(unittest.TestCase):
    def test_joint_requires_confident_correct_change_and_both_boxes(self):
        from evaluate_collection104 import score,summary
        row=dict(id='synthetic',split='train',changed=True,boxes=[[0,0,10,10]]*2)
        boxes=[dict(bounds=[0,0,10,10])]*2
        self.assertTrue(score(row,.85,boxes,'oldTrain')['joint'])
        self.assertFalse(score(row,.84,boxes,'oldTrain')['joint'])
        self.assertFalse(score(row,.1,boxes,'oldTrain')['joint'])
        self.assertFalse(score(row,.9,[None,boxes[0]],'oldTrain')['joint'])
        self.assertEqual(summary([score(row,.84,boxes,'oldTrain')])['abstentions'],1)
        for p in (float('nan'),float('inf'),-1,2):
            with self.assertRaisesRegex(ValueError,'score_probability'):score(row,p,boxes,'oldTrain')

    def test_paired_initializer_preserves_all_weights(self):
        torch=a.d.torch_runtime();torch.set_num_threads(2);torch.manual_seed(42)
        original=a.d.model(a.d.PAIRED_TEMPORAL_CONFIG).eval()
        state=dict(configuration=a.d.PAIRED_TEMPORAL_CONFIG,adaptation=a.REPAIR_CONFIG,state=original.state_dict())
        net,config=a.initialize(state,a.COLLECTION_CONFIG)
        self.assertEqual(config,a.d.PAIRED_TEMPORAL_CONFIG)
        self.assertTrue(all(torch.equal(v,net.state_dict()[k]) for k,v in state['state'].items()))
        x=torch.rand((2,6,128,192))
        with torch.no_grad():self.assertTrue(torch.equal(a.score_change(original,x,a.REPAIR_CONFIG),a.score_change(net,x,a.COLLECTION_CONFIG)))
        with self.assertRaisesRegex(ValueError,'collection_change_initializer'):
            a.initialize(dict(state,adaptation=a.CONFIG),a.COLLECTION_CONFIG)

    def test_rank_features_and_checkpoint_are_compatible(self):
        torch=a.d.torch_runtime();torch.manual_seed(42)
        before=r.model(torch,r.ACTION_CONFIG);after=r.model(torch,r.COLLECTION_CONFIG)
        after.load_state_dict(before.state_dict(),strict=True)
        frames=dict(frames=[dict(size=[100,100],candidates=[dict(bounds=[1,2,30,40])])])
        data=np.zeros((1,768),dtype=np.float32)
        old=r.features(data,frames,r.ACTION_CONFIG);new=r.features(data,frames,r.COLLECTION_CONFIG)
        np.testing.assert_array_equal(old,new)
        with torch.no_grad():self.assertTrue(torch.equal(before(torch.from_numpy(old)),after(torch.from_numpy(new))))

    def test_binding_rejects_false_role_before_loading_corpus(self):
        prep=dict(memberSHA256='member',proposal='proposal')
        receipt=dict(decision='decision',proposal='proposal')
        with patch.object(p.h,'checked',side_effect=lambda root,ref:ref),patch.object(p.h,'sealed',return_value=prep),\
             patch.object(p.r,'sealed',return_value=receipt),patch.object(p.h,'read',return_value=dict(approved=False,memberSHA256='member')) as read:
            with self.assertRaisesRegex(ValueError,'collection104_role_binding'):
                p.validate_training_binding(dict(preparation='prep',admissionReceipt='receipt'),[])
            self.assertEqual(read.call_count,1)

    def test_new_examples_do_not_expand_derived_negative_group(self):
        self.assertEqual(a.COLLECTION_CONFIG['originalGroupCount'],108)
        self.assertEqual(a.COLLECTION_CONFIG['derivedGroupCount'],122)
        self.assertEqual(a.COLLECTION_CONFIG['epochs'],600)
        self.assertEqual(r.COLLECTION_CONFIG['batch'],178)


if __name__=='__main__':unittest.main()
