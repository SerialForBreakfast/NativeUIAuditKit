import copy
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import focus_pretrained_experiment as p


class ProtocolTests(unittest.TestCase):
    def test_venv_interpreter_identity_is_not_dataset_admission(self):
        import focus_retention_experiment as retention
        executable = str(p.ROOT/'.venv-yolo/bin/python')
        with patch.object(retention.sys, 'executable', executable), \
             patch.object(retention.importlib.metadata, 'version', return_value='test'), \
             patch.object(retention, 'local', side_effect=AssertionError('dataset-only check')):
            self.assertEqual(retention.runtime_identity()['executable'], executable)

    def test_wrong_weight_identity_and_changed_baseline(self):
        base=dict(samples=[dict(id='one')],runtime={},protocolSHA256='old')
        spec=dict(version=p.INPUT,base={},weights=dict(sha256='wrong'))
        with patch.object(p.sampler.rep.appearance,'sealed',return_value=base), \
             patch.object(p.sampler,'assemble',return_value=base):
            base['inputs']={}
            with self.assertRaisesRegex(ValueError,'wrong_pretrained_weights'):p.assemble(spec)
        bad={**base,'samples':[]}
        with patch.object(p.sampler.rep.appearance,'sealed',return_value=base), \
             patch.object(p.sampler,'assemble',return_value=bad):
            with self.assertRaisesRegex(ValueError,'changed_pretrained_baseline'):p.assemble(spec)

    def test_actual_dispatch_approval_and_ordinary_rejection(self):
        from focus_learning_experiment import load_protocol
        from focus_training_preflight import preflight
        root=p.ROOT/'.build/debug-output/pretrained-tests';root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            d=Path(tmp);crop=d/'crop.png';crop.write_bytes(b'test')
            ref=p.sampler.rep.a.reference(crop)
            fields=dict(configuration={},selection={},sampling=dict(weights={'one':1}),counts={},
                        warmCheckpoint=None,runtime={},unmetQualificationBlockers=[],representation=p.REPRESENTATION)
            doc=dict(version=p.VERSION,inputs={},samples=[dict(id='one',crop=ref)],**fields)
            doc['protocolSHA256']=p.digest(doc)
            path=d/'protocol.json';path.write_text(json.dumps(doc))
            approval=d/'approval.json'
            data=dict(version='focus-pretrained-approval-v1',approved=True,protocolSHA256=doc['protocolSHA256'],
                      arm='pretrained-stretch',runName='unit-pretrained',reviewer='test',reviewReference='test')
            approval.write_text(json.dumps(data))
            with patch.object(p,'assemble',return_value=doc):
                report,rows=load_protocol(path,'pretrained-stretch','unit-pretrained',approval)
                self.assertTrue(report['launchEligible']);self.assertEqual(rows[0]['samplingWeight'],1)
                self.assertFalse(load_protocol(path,'pretrained-stretch','unit-pretrained')[0]['launchEligible'])
                with self.assertRaisesRegex(ValueError,'invalid_pretrained_arm'):load_protocol(path,'warm-stretch','unit-pretrained',approval)
                data['protocolSHA256']='bad';approval.write_text(json.dumps(data))
                with self.assertRaisesRegex(ValueError,'stale_pretrained_approval'):load_protocol(path,'pretrained-stretch','unit-pretrained',approval)
            (d/'focus_dataset_manifest.json').write_text(json.dumps(doc))
            result=preflight(d,'ordinary',30,64,.0003,'mobilenetv4_conv_small')
            self.assertFalse(result['launchEligible'])


class TensorMechanismTests(unittest.TestCase):
    def setUp(self):
        try:
            import torch
        except ImportError: self.skipTest('run tensor tests with the approved model interpreter')
        self.torch=torch

    def test_frozen_bn_parameters_order_and_normalization(self):
        torch=self.torch
        torch.set_num_threads(2)
        class Features(torch.nn.Module):
            def __init__(self):
                super().__init__();self.bn=torch.nn.BatchNorm2d(3);self.pool=torch.nn.AdaptiveAvgPool2d(1)
            def forward(self,x):
                self.observed=x.detach().clone();return self.pool(self.bn(x))
        net=Features();before=p.state_digest(net)
        images=torch.ones(4,3,8,8);labels=torch.tensor([[0.],[1.],[0.],[1.]])
        ds=torch.utils.data.TensorDataset(images,labels)
        encoded,sha=p.encode(net,ds,torch.device('cpu'),time.monotonic()+10,expected_features=3)
        self.assertEqual(sha,before);self.assertEqual(p.state_digest(net),before)
        self.assertFalse(net.training);self.assertFalse(any(x.requires_grad for x in net.parameters()))
        self.assertTrue(torch.equal(encoded.tensors[1],labels))
        expected=(torch.ones(3)-torch.tensor([.485,.456,.406]))/torch.tensor([.229,.224,.225])
        self.assertTrue(torch.allclose(net.observed[0,:,0,0],expected))
        head=torch.nn.Linear(3,1);opt=torch.optim.AdamW(head.parameters(),lr=.0003)
        original=head.weight.detach().clone()
        loss=torch.nn.functional.binary_cross_entropy_with_logits(head(encoded.tensors[0]),labels)
        loss.backward();opt.step()
        self.assertFalse(torch.equal(head.weight,original));self.assertEqual(p.state_digest(net),before)
        with self.assertRaisesRegex(ValueError,'pretrained_feature_deadline'):
            p.encode(net,ds,torch.device('cpu'),0,expected_features=3)


if __name__ == '__main__':unittest.main()
