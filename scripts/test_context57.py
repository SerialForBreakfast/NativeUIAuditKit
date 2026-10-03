import unittest
import tempfile
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch
import numpy as np
import focus_direct_transition as d
import focus_spatial_transition as s
import transition_intake_coverage as c


class ContextTests(unittest.TestCase):
    def test_intake_cli_evidence_and_collision(self):
        with tempfile.TemporaryDirectory(dir=d.h.ROOT/'.build',prefix='context57-test-') as directory:
            root=Path(directory);evidence=root/'observation.json';d.h.write(evidence,dict(testOnly=True))
            ref=d.h.ref(evidence)
            row=dict(id='fixture-only',partition='development',journeyGroup='test',
                focusChanged=False,scrolled=False,labelSource='human-reviewed',
                decodedFrameHashes=['b'*64,'c'*64],
                **{k:ref for k in ('beforeObservation','afterObservation','actionReceipt','cleanupReceipt')})
            source=root/'input.json';output=root/'output.json'
            d.h.write(source,dict(version='transition-intake-coverage-v1',records=[row]))
            command=[sys.executable,str(d.h.ROOT/'scripts/transition_intake_coverage.py'),
                '--input',str(source),'--output',str(output)]
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertFalse(d.h.read(output)['trainingEligible'])
            self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)
            evidence.write_text('{}')
            command[-1]=str(root/'changed.json')
            self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)

    def test_global_receptive_field_and_reload(self):
        t=d.torch_runtime();t.manual_seed(42);net=d.model(d.CONTEXT_DIAGNOSTIC)
        x=t.rand(1,6,64,96,requires_grad=True)
        cells,geometry,_=net.fields(x)
        for output in (cells[0,0,0,0],geometry[0,0,0,0,0]):
            grad=t.autograd.grad(output,x,retain_graph=True)[0]
            self.assertGreater(float(grad[:,:,-8:,-8:].abs().sum()),0)
        y=t.tensor([[.5,.4,.2,.1,.5,.6,.2,.1,1.]])
        s.loss(t,net,x,y).backward()
        self.assertTrue(all(bool(t.isfinite(p.grad).all()) for p in net.parameters()))
        restored=d.model(d.CONTEXT_CONFIG);restored.load_state_dict(net.state_dict())
        np.testing.assert_allclose(net(x).detach(),restored(x).detach(),atol=0,rtol=0)
        with self.assertRaises(ValueError):d.model(dict(d.CONTEXT_CONFIG,epochs=31))

    def test_local_model_has_no_remote_context(self):
        t=d.torch_runtime();net=d.model(d.SPATIAL_CONFIG)
        x=t.rand(1,6,64,96,requires_grad=True)
        grad=t.autograd.grad(net.fields(x)[0][0,0,0,0],x)[0]
        self.assertEqual(float(grad[:,:,-8:,-8:].abs().sum()),0)

    def test_intake_no_inferred_scroll_or_admission(self):
        ref=dict(path='test.json',sha256='a'*64)
        row=dict(id='a',partition='train',journeyGroup='j',focusChanged=False,scrolled=False,
            labelSource='fixture-observed',decodedFrameHashes=['b'*64,'c'*64],
            **{k:ref for k in ('beforeObservation','afterObservation','actionReceipt','cleanupReceipt')})
        doc=dict(version='transition-intake-coverage-v1',records=[row])
        with patch.object(c.h,'checked'):
            report=c.validate(doc);self.assertFalse(report['trainingEligible']);self.assertEqual(len(report['gaps']),11)
            for change,error in [({'scrolled':None},'observed_scrolled'),({'labelSource':'model'},'label_source')]:
                with self.assertRaisesRegex(ValueError,error):c.validate(dict(doc,records=[dict(row,**change)]))
            with self.assertRaisesRegex(ValueError,'journey_leakage'):
                c.validate(dict(doc,records=[row,dict(row,id='b',partition='evaluation')]))
            with self.assertRaisesRegex(ValueError,'pixel_leakage'):
                c.validate(dict(doc,records=[row,dict(row,id='b',journeyGroup='other',partition='evaluation')]))
        with patch.object(c.h,'checked',side_effect=ValueError('hash_changed')):
            with self.assertRaisesRegex(ValueError,'hash_changed'):c.validate(doc)


if __name__=='__main__':unittest.main()
