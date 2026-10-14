"""Test additive edge channels and the existing training path."""
import copy
import io
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import ExitStack
import numpy as np
import torch
import edge329 as e


class EdgeTests(unittest.TestCase):
    def setUp(self):torch.manual_seed(42);torch.set_num_threads(2)

    def model(self):
        return e.r.extend(e.r.s.c.model.extend(e.b.worker.make_model(torch,paired_context=True)),2)

    def test_initial_predictions_and_raw_weights(self):
        original=self.model().eval();new=e.extend(copy.deepcopy(original)).eval()
        self.assertTrue(torch.equal(new.change.detail[0].weight[:,:12],original.change.detail[0].weight))
        self.assertEqual(int(torch.count_nonzero(new.change.detail[0].weight[:,12:])),0)
        # Make the correction active so parity tests the changed convolution path.
        with torch.no_grad():
            original.change.correction.weight.fill_(.1);new.change.correction.weight.fill_(.1)
        x=torch.rand(2,18,128,192)
        with torch.inference_mode():torch.testing.assert_close(original.change(x),new.change(x),atol=1e-6,rtol=0)

    def test_edge_map_and_reversal(self):
        x=torch.zeros(1,6,128,192);x[:,:,:64]=.5
        g=e.gradient_channels(x)
        self.assertGreater(float(g.sum()),0);self.assertEqual(float(g[:,:,20:40].sum()),0)
        reverse=lambda v:torch.cat((v[:,3:],v[:,:3]),1)
        self.assertTrue(torch.equal(reverse(g),e.gradient_channels(reverse(x))))
        self.assertEqual(int(torch.count_nonzero(e.gradient_channels(torch.ones_like(x)))),0)
        x[0,0,0,0]=float('nan')
        with self.assertRaises(ValueError):e.gradient_channels(x)

    def test_actual_trainer_updates_only_detail_and_correction(self):
        net=e.extend(self.model());x=torch.rand(2,6,128,192);d=torch.rand(2,12,128,192)
        before={k:v.clone() for k,v in net.state_dict().items()}
        e.b.trainer.fit(net,x,torch.tensor([0.,1.]),dict(epochs=2,lr=.001,batch=2,seed=42,threads=2,detailOnly=True),detail_inputs=d)
        changed=[k for k,v in net.state_dict().items() if not torch.equal(v,before[k])]
        self.assertTrue(all(k.startswith(('change.detail.','change.correction.')) for k in changed))
        self.assertGreater(int(torch.count_nonzero(net.change.detail[0].weight[:,12:])),0)

    def test_checkpoint_and_invalid_version(self):
        net=e.extend(self.model()).eval();data=io.BytesIO()
        torch.save(dict(state=net.state_dict(),representation=e.VERSION,windows=2),data);data.seek(0)
        restored=e.load_candidate(data);x=torch.rand(2,18,128,192)
        with torch.inference_mode():torch.testing.assert_close(net.change(x),restored.change(x),atol=0,rtol=0)
        data=io.BytesIO();torch.save(dict(representation='wrong',windows=2),data);data.seek(0)
        with self.assertRaises(ValueError):e.load_candidate(data)

    def test_ablation_entrypoint_writes_report_and_restores_function(self):
        import ablate_edge329 as report
        keys=('native.npy','reverse_replay.npy','center8.npy')
        evaluation={'conditions':{k:{'probabilities':[.1,.9]} for k in keys}}
        membership={'rows':[{'changed':0},{'changed':1}],'replayLabels':[0,1]}
        emitted=[];original=e.gradient_channels
        def ref(path):
            self.assertIsInstance(path,Path)
            return {'path':str(path),'sha256':'test'}
        with ExitStack() as stack:
            stack.enter_context(patch.object(report,'OUT',e.b.ROOT/'.build/unused-edge329-test'))
            stack.enter_context(patch.object(report.e,'load_candidate',return_value=object()))
            stack.enter_context(patch.object(report.b,'read',side_effect=lambda p:membership if p.name=='membership.json' else evaluation))
            stack.enter_context(patch.object(report.np,'load',return_value=np.zeros((2,6,128,192),np.float32)))
            stack.enter_context(patch.object(report.r,'prepare',return_value=(np.zeros((2,12,128,192),np.float32),[])))
            stack.enter_context(patch.object(report.b.worker,'score',return_value=np.array([.1,.9])))
            stack.enter_context(patch.object(report.b,'ref',side_effect=ref))
            stack.enter_context(patch.object(report.b,'write',side_effect=lambda p,d:emitted.append(d)))
            report.main()
        self.assertIs(e.gradient_channels,original)
        self.assertEqual(set(emitted[0]['results']),set(keys))
        self.assertFalse(emitted[0]['trainingStarted'])


if __name__=='__main__':unittest.main()
