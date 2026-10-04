import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import focus_candidate_ranker as r
from geometry109 import truth_by_frame


class GeometryTests(unittest.TestCase):
    def test_target_conflict_hidden_by_binary_labels(self):
        frame=dict(id='a',split='train',candidates=[dict(id='p',bounds=[0,0,10,10])])
        rows=[dict(split='train',images=[dict(sha256='a')]*2,boxes=[[0,0,10,10],[0,0,11,10]])]
        self.assertEqual(len(truth_by_frame(rows)['a']),2)
        with self.assertRaisesRegex(ValueError,'geometry_truth_conflict'):
            r.geometry_targets(dict(frames=[frame]),rows)

    def test_targets_no_development_and_complete_training(self):
        frames=[dict(id=k,split=role,candidates=[dict(id='p',bounds=[0,0,10,10])]) for k,role in [('a','train'),('b','development')]]
        rows=[dict(split=role,images=[dict(sha256=k)]*2,boxes=[[0,0,10,10]]*2) for k,role in [('a','train'),('b','development')]]
        self.assertEqual(r.geometry_targets(dict(frames=frames),rows),{'a':[1.]})
        with self.assertRaisesRegex(ValueError,'geometry_training_membership'):
            r.geometry_targets(dict(frames=frames),rows[1:])

    def test_loss_prefers_better_extent_and_permutation(self):
        torch=r.d.torch_runtime()
        scores=torch.zeros(3,requires_grad=True); quality=torch.tensor([.9,.6,.1])
        loss=r.geometry_frame_loss(torch,scores,[0,1],quality); loss.backward()
        self.assertLess(scores.grad[0],scores.grad[1])
        order=[2,0,1]
        self.assertAlmostEqual(float(loss.detach()),float(r.geometry_frame_loss(torch,scores.detach()[order],[1,2],quality[order])))
        self.assertGreater(float(loss.detach()),float(r.frame_loss(torch,scores,[0,1]).detach()))

    def test_loss_ties_and_invalid_quality(self):
        torch=r.d.torch_runtime(); scores=torch.zeros(2,requires_grad=True)
        value=r.geometry_frame_loss(torch,scores,[0,1],torch.ones(2))
        self.assertEqual(float(value.detach()),0);value.backward()
        for quality in (torch.tensor([float('nan'),.5]),torch.tensor([1.,2.]),torch.tensor([1.])):
            with self.assertRaises(ValueError):r.geometry_frame_loss(torch,scores,[0],quality)
        with self.assertRaisesRegex(ValueError,'geometry_positive_binding'):
            r.geometry_frame_loss(torch,scores,[0],torch.ones(2))

    def test_real_trainer_path_and_conflict_fails_before_output(self):
        torch=r.d.torch_runtime();torch.set_num_threads(2)
        with tempfile.TemporaryDirectory(dir=r.d.h.ROOT/'.build') as tmp:
            root=Path(tmp); out=root/'run'; net=r.model(torch,r.ACTION_CONFIG)
            torch.save(dict(version=r.VERSION,configuration=r.ACTION_CONFIG,state=net.state_dict()),root/'initial.pt')
            r.d.h.write(root/'protocol.json',dict(initializer=r.d.h.ref(root/'initial.pt')))
            r.d.h.write(root/'approval.json',dict(testOnly=True))
            frames=[dict(id=str(i),split='train' if i<178 else 'development',size=[100,100],
                         candidates=[dict(id='p',bounds=[0,0,20,20]),dict(id='n',bounds=[40,40,20,20])]) for i in range(179)]
            rows=[dict(id=f['id'],split=f['split'],changed=True,images=[dict(sha256=f['id'])]*2,boxes=[[0,0,20,20]]*2) for f in frames]
            controls=[dict(id=v['id'],prediction=dict(changeProbability=.9)) for v in rows]
            data=np.zeros((358,768),dtype=np.float32);data[::2]=1
            payload=(dict(frames=frames),data,{f['id']:{'p'} for f in frames},rows,controls)
            report=dict(configuration=r.GEOMETRY_CONFIG,output=str(out.relative_to(r.d.h.ROOT)),
                protocolFile=r.d.h.ref(root/'protocol.json'),approval=r.d.h.ref(root/'approval.json'),launchEligible=True)
            with patch.object(r,'load_protocol',return_value=(report,payload)),patch.object(r.d.old,'fresh_run',return_value=out):
                self.assertEqual(r.run(report,'SYNTHETIC-UNIT-TEST'),0)
            result=r.sealed(out/'result.json',r.VERSION)
            self.assertEqual(len(result['trainingFrameIDs']),178)
            self.assertNotIn('178',result['trainingFrameIDs'])
            self.assertTrue(result['checkpointReplay'])
            rows[0]['boxes']=[[0,0,20,20],[0,0,21,20]]
            blocked=root/'blocked';report['output']=str(blocked.relative_to(r.d.h.ROOT))
            with patch.object(r,'load_protocol',return_value=(report,payload)),patch.object(r.d.old,'fresh_run',return_value=blocked):
                with self.assertRaisesRegex(ValueError,'geometry_truth_conflict'):r.run(report,'SYNTHETIC-UNIT-TEST')
            self.assertFalse(blocked.exists())


if __name__=='__main__':unittest.main()
