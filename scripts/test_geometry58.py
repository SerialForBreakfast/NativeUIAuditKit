import unittest
from unittest.mock import patch
import numpy as np
import focus_direct_transition as d
import focus_spatial_transition as s
from inventory_transition_sources import observed_scroll
import prepare_context57 as preparation


class GeometryTests(unittest.TestCase):
    def test_candidate_gate_binds_geometry_diagnostic(self):
        rows=[dict(id=str(i),changed=bool(i%2),split='train') for i in range(4)]
        evidence=dict(source={},model={},results=[dict(id=r['id'],split='train',boxIoUs=[.7,.8],rawChangeCorrect=True) for r in rows])
        result=dict(protocol={},model={},trainingIDs=['0','1','2','3'])
        protocol=dict(configuration=d.GEOMETRY_DIAGNOSTIC,corpusSHA256='same',pins={})
        with patch.object(d.h,'checked'),patch.object(d.h,'sealed',return_value=evidence),patch.object(d,'pins',return_value={}):
            with patch.object(d.h,'read',side_effect=[result,protocol]):
                self.assertEqual(preparation.verify_gate({},dict(corpusSHA256='same'),rows,d.GEOMETRY_DIAGNOSTIC),['0','1','2','3'])
            with patch.object(d.h,'read',side_effect=[result,dict(protocol,configuration=d.CONTEXT_DIAGNOSTIC)]):
                with self.assertRaisesRegex(ValueError,'diagnostic_gate_binding'):
                    preparation.verify_gate({},dict(corpusSHA256='same'),rows,d.GEOMETRY_DIAGNOSTIC)
            evidence['results'][0]['boxIoUs']=[.1,.8]
            with patch.object(d.h,'read',side_effect=[result,protocol]):
                with self.assertRaisesRegex(ValueError,'memorization_gate_failed'):
                    preparation.verify_gate({},dict(corpusSHA256='same'),rows,d.GEOMETRY_DIAGNOSTIC)

    def test_native_scroll_is_observed_not_requested(self):
        def scene(y):return dict(semantic_inventory=dict(elements=[dict(scroll_container_id='list',scroll_offset_points=[0,y])]))
        def endpoint(role,y):return dict(role=role,capture_endpoint=dict(before_scene=scene(y),after_scene=scene(y)))
        raw=dict(endpoints=[endpoint('before',0),endpoint('after',10)],specification=dict(offset=[0,0]))
        self.assertTrue(observed_scroll(raw)[0])
        raw['endpoints'][1]=endpoint('after',0);self.assertFalse(observed_scroll(raw)[0])
        raw['endpoints'][1]['capture_endpoint']['after_scene']=scene(20)
        self.assertIsNone(observed_scroll(raw)[0])
        self.assertIsNone(observed_scroll(dict(specification=dict(offset=[0,20])))[0])

    def test_saturated_logit_has_correcting_gradient(self):
        t=d.torch_runtime()
        for value,target in [(-100.,.06328125),(100.,.2),(-100.,1.),(100.,0.)]:
            logit=t.tensor([value],requires_grad=True);truth=t.tensor([target])
            s.geometry_loss(t,logit,truth,True).backward()
            self.assertTrue(bool(t.isfinite(logit.grad).all()))
            self.assertGreater(abs(float(logit.grad)),.01)
            self.assertEqual(float(logit.grad)>0,value>0)
        logit=t.tensor([-100.],requires_grad=True)
        s.geometry_loss(t,logit,t.tensor([.06328125]),False).backward()
        self.assertLess(abs(float(logit.grad)),1e-20)

    def test_unchanged_architecture_and_serialization(self):
        t=d.torch_runtime();t.manual_seed(42);old=d.model(d.CONTEXT_DIAGNOSTIC)
        t.manual_seed(42);new=d.model(d.GEOMETRY_DIAGNOSTIC)
        for name,value in old.state_dict().items():self.assertTrue(t.equal(value,new.state_dict()[name]))
        x=t.rand(2,6,64,96);y=t.tensor([[.5,.4,.8,.06,.5,.6,.8,.06,1.],[.2,.3,.1,.1,.2,.3,.1,.1,0.]])
        loss=s.loss(t,new,x,y,True);loss.backward()
        self.assertTrue(all(bool(t.isfinite(p.grad).all()) for p in new.parameters()))
        restored=d.model(d.GEOMETRY_CONFIG);restored.load_state_dict(new.state_dict())
        np.testing.assert_allclose(new(x).detach(),restored(x).detach(),atol=0,rtol=0)
        with self.assertRaises(ValueError):d.model(dict(d.GEOMETRY_CONFIG,lr=.01))

    def test_selection_unchanged(self):
        rows=[dict(id=str(i),changed=bool(i%2),split='train') for i in range(8)]
        self.assertEqual(d.training_rows(rows,d.GEOMETRY_DIAGNOSTIC),d.training_rows(rows,d.CONTEXT_DIAGNOSTIC))


if __name__=='__main__':unittest.main()
