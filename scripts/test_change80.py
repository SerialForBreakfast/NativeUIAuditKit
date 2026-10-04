import copy
from pathlib import Path
import tempfile
import unittest
import focus_direct_transition as d
import focus_change_adaptation as a
import focus_recorded_semantics as semantics
from unittest.mock import patch


class ChangeAdaptationTests(unittest.TestCase):
    def test_self_pair_diagnostic_rejects_unbound_result_and_collision(self):
        with tempfile.TemporaryDirectory(dir=d.h.ROOT/'.build') as tmp:
            root=Path(tmp);d.h.write(root/'protocol.json',{})
            d.h.write(root/'result.json',dict(protocol={'path':'wrong','sha256':'wrong'}),sealed=True)
            with self.assertRaisesRegex(ValueError,'self_pair_result_binding'):
                a.evaluate_self_pairs(root/'protocol.json',root/'result.json',root/'out')
            self.assertFalse((root/'out').exists())
            (root/'out').mkdir()
            with self.assertRaisesRegex(ValueError,'output_collision'):
                a.evaluate_self_pairs(root/'protocol.json',root/'result.json',root/'out')

    def test_high_resolution_change_is_separate_from_geometry(self):
        torch=d.torch_runtime();torch.set_num_threads(2);torch.manual_seed(42)
        old=d.model(d.TEMPORAL_CONFIG).eval();state=dict(configuration=d.TEMPORAL_CONFIG,state=old.state_dict())
        net,configuration=a.initialize(state,a.RESOLUTION_CONFIG)
        images=torch.rand((2,6,128,192))
        with torch.inference_mode():
            self.assertTrue(torch.allclose(a.score_change(old,images,a.RESOLUTION_CONFIG),
                a.score_change(net,images,a.RESOLUTION_CONFIG),atol=1e-6,rtol=0))
        for tensor,config in [(images,a.CONTEXT_CONFIG),(images[:,:,:64,:96],a.RESOLUTION_CONFIG)]:
            with self.assertRaisesRegex(ValueError,'score_shape'):a.score_change(net,tensor,config)
        net,_=d.fit_change_head(net,images,torch.tensor([0.,1.]),dict(a.RESOLUTION_CONFIG,epochs=2))
        self.assertTrue(all(torch.equal(v,net.state_dict()[k]) for k,v in state['state'].items() if not k.startswith('change.')))
        replay=d.model(configuration);replay.load_state_dict(net.state_dict());replay.eval()
        with torch.inference_mode():self.assertTrue(torch.equal(a.score_change(net,images,a.RESOLUTION_CONFIG),a.score_change(replay,images,a.RESOLUTION_CONFIG)))

    def test_context_initial_parity_training_and_reload(self):
        torch=d.torch_runtime();torch.set_num_threads(2);torch.manual_seed(42)
        old=d.model(d.TEMPORAL_CONFIG).eval()
        state=dict(configuration=d.TEMPORAL_CONFIG,state=old.state_dict())
        net,config=a.initialize(state,a.CONTEXT_CONFIG)
        x=torch.rand((4,6,64,96));labels=torch.tensor([0.,1.,0.,1.])
        self.assertEqual(config,d.PAIRED_TEMPORAL_CONFIG)
        self.assertTrue(torch.equal(net.change[0].weight[:,3:],torch.zeros_like(net.change[0].weight[:,3:])))
        self.assertTrue(torch.equal(net.change_inputs(x)[:,3:],x))
        with torch.inference_mode():self.assertTrue(torch.allclose(old(x),net(x),atol=1e-6,rtol=0))
        trained,_=d.fit_change_head(net,x,labels,dict(a.CONTEXT_CONFIG,epochs=2))
        self.assertTrue(any(torch.count_nonzero(trained.change[0].weight[:,3:]).flatten()))
        self.assertTrue(all(torch.equal(v,trained.state_dict()[k]) for k,v in state['state'].items() if not k.startswith('change.')))
        replay=d.model(config);replay.load_state_dict(trained.state_dict());replay.eval()
        with torch.inference_mode():self.assertTrue(torch.equal(trained(x),replay(x)))
        bad=dict(state,state=dict(state['state']));bad['state']['change.0.weight']=torch.zeros((8,4,3,3))
        with self.assertRaisesRegex(ValueError,'initializer_shape'):a.initialize(bad,a.CONTEXT_CONFIG)

    def test_native_control_binding(self):
        doc=dict(configuration=a.NATIVE_CONFIG,corpus={'sha256':'corpus'},initializer={'sha256':'model'})
        control=dict(version='native88-frozen-diagnostic-v1',corpus=doc['corpus'],changeModel=doc['initializer'],
            results=[dict(id='pair',probability=.25)])
        control['seal']=d.h.digest(control)
        self.assertEqual(a.control_scores(control,doc,{}),[dict(id='pair',prediction=dict(changeProbability=.25))])
        for field in ('corpus','changeModel'):
            bad=copy.deepcopy(control);bad[field]={'sha256':'wrong'}
            bad['seal']=d.h.digest({k:v for k,v in bad.items() if k!='seal'})
            with self.assertRaisesRegex(ValueError,'change_control_binding'):a.control_scores(bad,doc,{})
        bad=copy.deepcopy(control);bad['results'][0]['probability']=.8
        with self.assertRaisesRegex(ValueError,'change_control_binding'):a.control_scores(bad,doc,{})

    def test_semantics_reuses_reviewed_frames_once(self):
        audit=dict(actions=[dict(metadataReady=True,annotationsComplete=True,endpoints={'before':dict(sha256='a'),'after':dict(sha256='b')})])
        truth={'a':{'test':1},'b':{'test':2}}
        with patch.object(semantics.readiness,'run_with_frames',return_value=(audit,truth)) as run, \
             patch.object(semantics.readiness.baseline_reader,'baseline',side_effect=AssertionError('duplicate traversal')):
            result=semantics.inputs('batch','baseline','pending','revision','completeness')
            self.assertIs(result[0],audit);self.assertIs(result[1],truth);self.assertEqual(result[3],['a','b'])
            run.assert_called_once_with('batch','baseline','pending','revision','completeness')

    def test_only_change_weights_update_and_reload(self):
        torch=d.torch_runtime();torch.set_num_threads(2);torch.manual_seed(42)
        net=d.model(d.TEMPORAL_CONFIG);before={k:v.clone() for k,v in net.state_dict().items()}
        x=torch.rand((4,6,64,96));labels=torch.tensor([0.,1.,0.,1.])
        fitted,history=d.fit_change_head(net,x,labels,dict(a.CONFIG,epochs=2))
        self.assertEqual(len(history),2)
        self.assertTrue(all(torch.equal(v,fitted.state_dict()[k]) for k,v in before.items() if not k.startswith('change.')))
        self.assertTrue(any(not torch.equal(v,fitted.state_dict()[k]) for k,v in before.items() if k.startswith('change.')))
        self.assertTrue(all(p.grad is None for k,p in fitted.named_parameters() if not k.startswith('change.')))
        other=d.model(d.TEMPORAL_CONFIG);other.load_state_dict(fitted.state_dict());other.eval()
        with torch.inference_mode():self.assertTrue(torch.equal(fitted(x),other(x)))

    def test_invalid_shape_range_labels_and_nan(self):
        torch=d.torch_runtime();net=d.model(d.TEMPORAL_CONFIG)
        x=torch.zeros((2,6,64,96));labels=torch.tensor([0.,1.])
        cases=[(x[:,:,:,:95],labels),(x+2,labels),(x,torch.tensor([0.,.5])),(x*float('nan'),labels),(x,labels[:1])]
        for data,target in cases:
            with self.assertRaisesRegex(ValueError,'adaptation_inputs'):
                d.fit_change_head(net,data,target,dict(a.CONFIG,epochs=1))


if __name__=='__main__':unittest.main()
