"""Check added inputs, unchanged starting scores, and trainable new weights."""
import unittest
import tempfile
from pathlib import Path
import torch
import representation287 as r


class AddedInputsTests(unittest.TestCase):
    def test_initial_parity_and_gradient(self):
        torch.manual_seed(42);torch.set_num_threads(2)
        net=r.base.worker.make_model(torch,paired_context=True).eval()
        x=torch.rand(2,6,128,192)
        before=net.change(net.change_inputs(x)).detach()
        weights=net.change[0].weight.detach().clone()
        r.extend(net)
        after=net.change(net.change_inputs(x))
        self.assertTrue(torch.allclose(before,after,atol=1e-6,rtol=0))
        self.assertTrue(torch.equal(net.change[0].weight[:,:9],weights))
        self.assertEqual(float(net.change[0].weight[:,9:].detach().abs().sum()),0)
        after.sum().backward()
        self.assertGreater(float(net.change[0].weight.grad[:,9:].abs().sum()),0)

    def test_channel_order(self):
        x=torch.rand(1,6,16,24)
        y=r.change_inputs(None,x)
        self.assertEqual(y.shape,(1,12,16,24))
        self.assertTrue(torch.equal(y[:,:3],(x[:,3:]-x[:,:3]).abs()))
        self.assertTrue(torch.equal(y[:,3:9],x))
        self.assertTrue(torch.equal(y[:,9:],r.previous.change_inputs(None,x)[:,:3]))

    def test_double_extension_rejected(self):
        net=r.extend(r.base.worker.make_model(torch,paired_context=True))
        with self.assertRaisesRegex(ValueError,'input_architecture'):r.extend(net)

    def test_checkpoint_representation_and_roundtrip(self):
        net=r.extend(r.base.worker.make_model(torch,paired_context=True)).eval()
        with tempfile.TemporaryDirectory(dir=r.base.ROOT/'.build') as directory:
            path=Path(directory)/'candidate.pt'
            torch.save(dict(state=net.state_dict(),representation=r.REPRESENTATION),path)
            restored=r.load_candidate(path)
            self.assertTrue(all(torch.equal(v,restored.state_dict()[k]) for k,v in net.state_dict().items()))
            torch.save(dict(state=net.state_dict(),representation='wrong'),path)
            with self.assertRaisesRegex(ValueError,'representation_identity'):r.load_candidate(path)


if __name__=='__main__':unittest.main()
