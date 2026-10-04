"""Deterministic tests for retention-only ranker adaptation; no private fixtures."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import focus_candidate_ranker as r
from diagnose_retention105 import candidate_summary,groups


class RetentionTests(unittest.TestCase):
    def test_hidden_only_optimizer_preserves_readout(self):
        torch=r.d.torch_runtime();torch.set_num_threads(2);torch.manual_seed(42)
        net=r.model(torch,r.RETENTION_CONFIG)
        before={k:v.clone() for k,v in net.state_dict().items()}
        parameters=r.trainable_parameters(net,r.RETENTION_CONFIG)
        self.assertEqual([k for k,p in net.named_parameters() if p.requires_grad],['0.weight','0.bias'])
        opt=torch.optim.Adam(parameters,lr=.001)
        x=torch.rand(8,770)
        for _ in range(5):
            opt.zero_grad();r.frame_loss(torch,net(x).flatten(),[0]).backward();opt.step()
        self.assertTrue(all(torch.equal(net.state_dict()[k],v) for k,v in before.items() if k.startswith('2.')))
        self.assertFalse(torch.equal(before['0.weight'],net.state_dict()['0.weight']))
        self.assertTrue(all(p.grad is None for k,p in net.named_parameters() if k.startswith('2.')))

    def test_old_training_mode_keeps_all_parameters(self):
        torch=r.d.torch_runtime();net=r.model(torch,r.COLLECTION_CONFIG)
        self.assertEqual(len(r.trainable_parameters(net,r.COLLECTION_CONFIG)),4)
        self.assertTrue(all(p.requires_grad for p in net.parameters()))
        with self.assertRaisesRegex(ValueError,'trainable_configuration'):
            r.trainable_parameters(net,dict(r.RETENTION_CONFIG,epochs=1))

    def test_retention_features_and_initial_predictions_identical(self):
        torch=r.d.torch_runtime();torch.manual_seed(42)
        base=r.model(torch,r.ACTION_CONFIG);candidate=r.model(torch,r.RETENTION_CONFIG)
        candidate.load_state_dict(base.state_dict(),strict=True)
        frames=dict(frames=[dict(size=[100,80],candidates=[dict(bounds=[1,2,30,40])])])
        data=np.full((1,768),.25,dtype=np.float32)
        a=r.features(data,frames,r.ACTION_CONFIG);b=r.features(data,frames,r.RETENTION_CONFIG)
        np.testing.assert_array_equal(a,b)
        with torch.no_grad():self.assertTrue(torch.equal(base(torch.from_numpy(a)),candidate(torch.from_numpy(b))))

    def test_diagnosis_distinguishes_proposal_and_rank(self):
        f=dict(id='frame',candidates=[dict(id='a',bounds=[0,0,20,10]),dict(id='b',bounds=[0,0,50,50])])
        v=candidate_summary(f,np.array([1.,2.]),{'a'})
        self.assertFalse(v['correct']);self.assertEqual(v['positiveCandidateCount'],1)
        self.assertEqual(v['positiveMargin'],-1.)
        self.assertEqual(candidate_summary(f,np.array([1.,1.]),{'a'})['selected']['id'],'a')
        for scores in (np.array([1.]),np.array([1.,np.nan])):
            with self.assertRaises(ValueError):candidate_summary(f,scores,{'a'})
        with self.assertRaises(ValueError):candidate_summary(f,np.array([1.,2.]),set())

    def test_group_offsets_do_not_duplicate_frames(self):
        frames=[dict(id='one',candidates=[{},{}]),dict(id='two',candidates=[{}])]
        self.assertEqual([(f['id'],a,b) for f,a,b in groups(dict(frames=frames))],[('one',0,2),('two',2,3)])

    def test_actual_run_receipt_keeps_parameter_names_and_training_roles(self):
        torch=r.d.torch_runtime();torch.set_num_threads(2)
        with tempfile.TemporaryDirectory(dir=r.d.h.ROOT/'.build',prefix='retention105-test-') as tmp:
            root=Path(tmp);initial=root/'initial.pt';out=root/'run'
            net=r.model(torch,r.ACTION_CONFIG)
            torch.save(dict(version=r.VERSION,configuration=r.ACTION_CONFIG,state=net.state_dict()),initial)
            r.d.h.write(root/'protocol.json',dict(initializer=r.d.h.ref(initial)))
            r.d.h.write(root/'approval.json',dict(testOnly=True))
            frames=[dict(id=str(i),split='train' if i<178 else 'development',size=[100,100],
                candidates=[dict(id='positive',bounds=[0,0,20,20]),dict(id='negative',bounds=[40,40,20,20])]) for i in range(179)]
            rows=[dict(id='training',split='train',changed=True,images=[dict(sha256='0')]*2,boxes=[[0,0,20,20]]*2),
                  dict(id='development',split='development',changed=True,images=[dict(sha256='178')]*2,boxes=[[0,0,20,20]]*2)]
            control=[dict(id=v['id'],prediction=dict(changeProbability=.9)) for v in rows]
            inputs=dict(frames=frames);data=np.zeros((358,768),dtype=np.float32);data[::2]=1
            report=dict(configuration=r.RETENTION_CONFIG,output=str(out.relative_to(r.d.h.ROOT)),
                protocolFile=r.d.h.ref(root/'protocol.json'),approval=r.d.h.ref(root/'approval.json'),launchEligible=True)
            payload=(inputs,data,{f['id']:{'positive'} for f in frames},rows,control)
            with patch.object(r,'load_protocol',return_value=(report,payload)),patch.object(r.d.old,'fresh_run',return_value=out):
                self.assertEqual(r.run(report,'SYNTHETIC-UNIT-TEST'),0)
            result=r.sealed(out/'result.json',r.VERSION)
            self.assertEqual(result['frozenParameterNames'],['2.bias','2.weight'])
            self.assertEqual(set(result['trainingFrameIDs']),{str(i) for i in range(178)})
            saved=torch.load(out/'last.pt',weights_only=True)
            for k in ('2.weight','2.bias'):self.assertTrue(torch.equal(saved['state'][k],net.state_dict()[k]))


if __name__=='__main__': unittest.main()
