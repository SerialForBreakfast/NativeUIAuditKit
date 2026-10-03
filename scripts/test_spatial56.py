import unittest
import numpy as np
import focus_direct_transition as d
import focus_spatial_transition as s
import prepare_spatial56 as p


class SpatialTests(unittest.TestCase):
    def test_targets_cell_geometry(self):
        t=d.torch_runtime();boxes=t.tensor([[.25,.375,.2,.1,.75,.625,.1,.2]])
        ids,geo=s.targets(t,boxes)
        self.assertEqual(ids.tolist(),[[6*24+6,10*24+18]])
        np.testing.assert_allclose(geo[0,:,:2],0)
        np.testing.assert_allclose(geo[0,:,2:],[[.2,.1],[.1,.2]])

    def test_spatial_gradients_shapes_and_state_reload(self):
        t=d.torch_runtime();t.manual_seed(42);net=d.model(d.SPATIAL_CONFIG)
        images=t.rand(2,6,64,96);labels=t.tensor([[.25,.375,.2,.1,.75,.625,.1,.2,1.],
                                                    [.2,.2,.1,.1,.2,.2,.1,.1,0.]])
        loss=s.loss(t,net,images,labels);loss.backward()
        for layer in (net.cells,net.geometry):
            self.assertTrue(bool(t.isfinite(layer.weight.grad).all()))
            self.assertGreater(float(layer.weight.grad.abs().sum()),0)
        out=net(images);self.assertEqual(tuple(out.shape),(2,9))
        restored=d.model(d.SPATIAL_DIAGNOSTIC);restored.load_state_dict(net.state_dict())
        np.testing.assert_allclose(out.detach(),restored(images).detach(),rtol=0,atol=0)
        with self.assertRaises(ValueError):d.model(dict(d.SPATIAL_CONFIG,width=192))

    def test_diagnostic_selection_is_train_only_and_candidate_gate_strict(self):
        rows=[dict(id=str(i),changed=bool(i%2),split='train') for i in range(6)]
        picked=d.training_rows(rows,d.SPATIAL_DIAGNOSTIC)
        self.assertEqual([r['id'] for r in picked],['0','2','1','3'])
        scores=[dict(id=r['id'],split='train',boxIoUs=[.6,.7],rawChangeCorrect=True) for r in picked]
        self.assertEqual(len(p.candidate_gate(dict(results=scores),rows)),4)
        scores[0]['boxIoUs'][1]=.49
        with self.assertRaisesRegex(ValueError,'memorization_gate'):p.candidate_gate(dict(results=scores),rows)
        rows[0]['split']='development'
        with self.assertRaises(ValueError):d.training_rows(rows,d.SPATIAL_DIAGNOSTIC)


if __name__=='__main__':unittest.main()
