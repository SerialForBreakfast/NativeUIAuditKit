import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import focus_change_adaptation as a


class DerivedProposalTests(unittest.TestCase):
    def test_equal_group_training_and_frozen_geometry(self):
        torch=a.d.torch_runtime();torch.manual_seed(42);torch.set_num_threads(2)
        base=a.d.model(a.d.TEMPORAL_CONFIG)
        state=dict(configuration=a.d.TEMPORAL_CONFIG,state=base.state_dict())
        net,_=a.initialize(state,a.REPAIR_CONFIG)
        x=torch.rand((3,6,128,192));x[2,3:]=x[2,:3]
        labels=torch.tensor([1.,0.,0.]);config=dict(a.REPAIR_CONFIG,epochs=1,originalGroupCount=2,derivedGroupCount=1)
        with torch.no_grad():
            logits=net.change(net.change_inputs(x)).flatten()
            loss=torch.nn.functional.binary_cross_entropy_with_logits(logits,labels,reduction='none')
            expected=.5*(loss[:2].mean()+loss[2:].mean())
        net,history=a.d.fit_change_head(net,x,labels,config)
        self.assertAlmostEqual(history[0]['loss'],expected.item(),places=6)
        self.assertTrue(all(torch.equal(v,net.state_dict()[k]) for k,v in state['state'].items() if not k.startswith('change.')))
        for invalid in (dict(config,derivedGroupCount=2),dict(config,lossWeighting='pooled')):
            with self.assertRaisesRegex(ValueError,'change_derived_group'):a.d.fit_change_head(net,x,labels,invalid)

    def fixture(self):
        rows=[]
        for i,split in enumerate(('train','development')):
            rows.append(dict(id=str(i),split=split,group=split,
                images=[dict(path=f'{i}-{j}.png',sha256=str(i*2+j+1)*64) for j in range(2)],
                decodedPixelHashes=[str(i*2+j+5)*64 for j in range(2)]))
        return rows,np.zeros((2,6,128,192),dtype=np.float32)

    def test_deterministic_train_only_and_no_authority(self):
        rows,x=self.fixture();p=a.self_pair_proposal(rows,x)
        self.assertEqual(p,a.self_pair_proposal(rows,x));self.assertEqual(len(p['entries']),2)
        self.assertEqual(p['excludedDevelopmentFrames'],2)
        self.assertFalse(p['trainingEligible']);self.assertFalse(p['launchEligible'])
        self.assertTrue(all(e['changed'] is False for e in p['entries']))
        self.assertTrue(all(o['rowIndex']==0 for e in p['entries'] for o in e['origins']))

    def test_duplicate_pixels_deduplicated_preserve_origins(self):
        rows,x=self.fixture();rows[0]['decodedPixelHashes'][1]=rows[0]['decodedPixelHashes'][0]
        p=a.self_pair_proposal(rows,x);self.assertEqual(len(p['entries']),1)
        self.assertEqual(len(p['entries'][0]['origins']),2)

    def test_cross_split_even_different_bytes_rejected(self):
        rows,x=self.fixture();rows[1]['decodedPixelHashes'][0]=rows[0]['decodedPixelHashes'][0]
        with self.assertRaisesRegex(ValueError,'derived_cross_split'):a.self_pair_proposal(rows,x)

    def test_byte_identity_and_tensor_conflicts(self):
        rows,x=self.fixture();rows[1]['images'][0]['sha256']=rows[0]['images'][0]['sha256']
        with self.assertRaisesRegex(ValueError,'derived_byte_conflict'):a.self_pair_proposal(rows,x)
        rows,x=self.fixture();rows[0]['decodedPixelHashes'][1]=rows[0]['decodedPixelHashes'][0];x[0,3:]=1
        with self.assertRaisesRegex(ValueError,'derived_tensor_conflict'):a.self_pair_proposal(rows,x)

    def test_malformed_inputs(self):
        for change in ('nan','range','shape','dtype','duplicate','hash','role'):
            rows,x=self.fixture()
            if change=='nan':x[0,0,0,0]=np.nan
            if change=='range':x[0,0,0,0]=2
            if change=='shape':x=x[:,:,:64]
            if change=='dtype':x=x.astype(np.float64)
            if change=='duplicate':rows[1]['id']=rows[0]['id']
            if change=='hash':rows[0]['decodedPixelHashes'][0]='not-a-hash'
            if change=='role':rows[0]['split']='final'
            with self.subTest(change=change),self.assertRaises(ValueError):a.self_pair_proposal(rows,x)

    def test_proposal_rejected_by_training_dispatcher(self):
        rows,x=self.fixture()
        with tempfile.TemporaryDirectory(dir=a.d.h.ROOT/'.build') as tmp:
            p=Path(tmp)/'proposal.json';a.d.h.write(p,a.self_pair_proposal(rows,x),sealed=True)
            with self.assertRaisesRegex(ValueError,'change_configuration'):
                a.load_protocol(p,a.ARM,'never-launched')

    def test_collision_and_changed_parent_fail_without_output(self):
        with tempfile.TemporaryDirectory(dir=a.d.h.ROOT/'.build') as tmp:
            root=Path(tmp);p=root/'parent.json';a.d.h.write(p,{})
            with self.assertRaisesRegex(ValueError,'derived_protocol'):a.prepare_self_pairs(p,root/'out')
            self.assertFalse((root/'out').exists());(root/'out').mkdir()
            with self.assertRaisesRegex(ValueError,'output_collision'):a.prepare_self_pairs(p,root/'out')

    def test_changed_source_prevents_publication(self):
        with tempfile.TemporaryDirectory(dir=a.d.h.ROOT/'.build') as tmp:
            root=Path(tmp);corpus=root/'corpus.json';a.d.h.write(corpus,dict(sources={}))
            doc=dict(version=a.VERSION,configuration=a.RESOLUTION_CONFIG,corpus=a.d.h.ref(corpus))
            doc['protocolSHA256']=a.d.h.digest(doc);p=root/'parent.json';a.d.h.write(p,doc)
            with patch.object(a.d,'collect',return_value={'changed':True}), \
                 self.assertRaisesRegex(ValueError,'derived_source_changed'):
                a.prepare_self_pairs(p,root/'out')
            self.assertFalse((root/'out').exists())


if __name__=='__main__':unittest.main()
