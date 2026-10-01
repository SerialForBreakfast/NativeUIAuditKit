"""Offline generated context/authority tests; no retained model execution."""
import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from unittest.mock import Mock

import focus_context_experiment as c
import train_focus_ring_detector as trainer
from test_focus_native_body_experiment import NativeExecutionTests
import test_focus_growth_inputs as inputs


class TensorTests(unittest.TestCase):
    def setUp(self):
        import torch
        self.t=torch

    def test_pool_uses_target_not_global_or_labels(self):
        t=self.t;features=t.tensor([[[[1.,2.],[3.,8.]]]])
        self.assertEqual(c.pooled(features,t.tensor([[[[0.,0.],[0.,1.]]]])).item(),8)
        self.assertEqual(c.pooled(features,t.ones(1,1,2,2)).item(),3.5)
        with self.assertRaisesRegex(ValueError,'empty_context_pool'):c.pooled(features,t.zeros(1,1,2,2))

    def test_pool_nondivisible_scene_dimensions(self):
        t=self.t
        result=c.pooled(t.ones(1,576,14,24),t.ones(1,1,432,768))
        self.assertEqual(result.shape,(1,576));self.assertTrue(t.equal(result,t.ones_like(result)))

    def test_ablations_and_identical_initial_predictions(self):
        t=self.t;t.manual_seed(17);local=t.randn(4,576);extra=t.randn(4,1160)
        outputs=[]
        for arm in c.ARMS:
            x=c.fuse(local,extra,arm);self.assertTrue(t.equal(x[:,:576],local))
            if arm=='context-local':self.assertEqual(x[:,576:].abs().sum(),0)
            if arm=='context-geometry':
                self.assertEqual(x[:,576:1728].abs().sum(),0)
                self.assertTrue(t.equal(x[:,1728:],extra[:,1152:]))
            head=c.make_head('cpu');outputs.append(head(x))
        for output in outputs[1:]:self.assertTrue(t.equal(output,outputs[0]))
        self.assertTrue(t.equal(extra,c.fuse(local,extra,'context-scene')[:,576:]))

    def test_geometry_can_learn_without_mutating_local_branch_input(self):
        t=self.t;head=c.make_head('cpu');local=t.ones(2,576);extra=t.zeros(2,1160)
        extra[1,-8]=1;x=c.fuse(local,extra,'context-geometry')
        loss=t.nn.functional.binary_cross_entropy_with_logits(head(x),t.tensor([[0.],[1.]]))
        loss.backward();self.assertGreater(head[0].weight.grad[:,1728:].abs().sum(),0)
        with self.assertRaises(ValueError):c.fuse(local,extra,'guess')


class AuthorityTests(unittest.TestCase):
    def setUp(self):
        parent=c.h.ROOT/'.build/context-tests';parent.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=parent);self.root=Path(self.temp.name)
        auth=self.root/'authority.md';auth.write_text('Generated test only')
        self.e=dict(version='focus-context-tranche-v1',approved=True,runs=dict(c.ARMS),
                    scope='local-context-comparison-no-export',authorizationReference=c.h.ref(auth),
                    limits=dict(maxRuns=3,trainingSeconds=300,encodingSeconds=300,wallSeconds=1800,
                                outputBytes=2*1024**3,cacheBytes=64*1024**2))
        self.path=self.root/'envelope.json'

    def tearDown(self):self.temp.cleanup()

    def ref(self):self.path.write_text(json.dumps(self.e));return c.h.ref(self.path)

    def test_authority_is_exact_not_blanket(self):
        self.assertEqual(c.envelope(self.ref()),self.e)
        original=copy.deepcopy(self.e)
        for mode in ('unapproved','fourth','budget','scope','authority'):
            self.e=copy.deepcopy(original)
            if mode=='unapproved':self.e['approved']=False
            if mode=='fourth':self.e['runs']['context-fourth']='fdr027'
            if mode=='budget':self.e['limits']['trainingSeconds']=301
            if mode=='scope':self.e['scope']='export'
            if mode=='authority':self.e['authorizationReference']['sha256']='0'*64
            with self.assertRaises(ValueError):c.envelope(self.ref())

    def test_real_trainer_dispatch_rejects_missing_approval_before_torch(self):
        doc=dict(version=c.VERSION,inputs={},samples=[],blockers=[],configuration=dict(epochs=1000,batch=1,lr=.01,model='context_mlp_64'),
                 selection={},representation={},fullFit={},counts={},runtime={},baseCachedInputs={},reviewedExtension={},
                 baselineTraining=1,nativeExtension={},warmCheckpoint=None,unmetQualificationBlockers=[])
        doc['inputs']['contextFeatures']=None;doc['inputs']['envelope']=self.ref()
        doc['protocolSHA256']=c.h.digest(doc)
        path=self.root/'protocol.json';c.h.write(path,doc)
        # Do not depend on the real approved run directory remaining absent after
        # execution. This generated missing-approval test must never load a model.
        test_run='generated-context-'+self.root.name
        with patch.dict(c.ARMS,{'context-local':test_run}),\
             patch.object(c,'prepare',return_value=doc),patch.dict('sys.modules',{'torch':None}),\
             patch('sys.argv',['trainer','--experiment-protocol',str(path),'--experiment-arm','context-local',
                               '--name',test_run,'--execute']),redirect_stdout(io.StringIO()) as out:
            self.assertEqual(trainer.main(),2)
        self.assertEqual(json.loads(out.getvalue())['blockers'],['missing_tranche_approval'])
        with patch.object(c,'prepare',return_value=doc):
            with self.assertRaisesRegex(ValueError,'arm_binding'):c.load_protocol(path,'context-scene','other')


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.fixture=NativeExecutionTests();self.fixture.setUp()
    def tearDown(self):self.fixture.tearDown()

    def test_existing_cache_join_and_fusion_membership(self):
        f=self.fixture;t=f.t;doc,ref,approval=f.prepared()
        import focus_native_body_experiment as native
        report,rows=native.load_protocol(f.path(ref),native.ARM,'generated-native-test',f.path(approval))
        x=t.arange(8*1160,dtype=t.float32).reshape(8,1160)/1000
        receipt=dict(ids=[r['id'] for r in rows],featureSHA256=c.tensor_digest(x))
        cp=f.root/'context.pt';t.save(dict(receipt=receipt,features=x),cp)
        rp=f.save('context-receipt.json',receipt)
        report.update(arm='context-geometry',contextFeatures=dict(cache=c.h.ref(cp),receipt=rp))
        out=f.root/'fusion';out.mkdir()
        head,train,val=c.prepare_features(report,rows[:6],rows[6:],t.device('cpu'),out)
        self.assertEqual(train.tensors[0].shape,(6,c.WIDTH));self.assertEqual(val.tensors[0].shape,(2,c.WIDTH))
        self.assertTrue(t.equal(train.tensors[0][:,:576],f.x[:6]))
        self.assertTrue(t.equal(train.tensors[0][:,-8:],x[:6,-8:]))
        self.assertEqual(train.tensors[0][:,576:1728].abs().sum(),0)
        self.assertEqual(head(train.tensors[0]).shape,(6,1))

    def test_context_dispatch_reaches_existing_full_fit_loop(self):
        f=self.fixture;t=f.t;doc,ref,old_approval=f.prepared()
        import focus_native_body_experiment as native
        report,rows=native.load_protocol(f.path(ref),native.ARM,'generated-native-test',f.path(old_approval))
        report.update(protocolVersion=c.VERSION,arm='context-local',approval=None,
                      configuration=dict(report['configuration'],model='context_mlp_64'))
        research=f.root/'Research';research.mkdir()
        (research/'ExperimentLog.md').write_text('## Run GENERATED software fixture\n'+
                        doc['protocolSHA256']+' context-local '+c.ARMS['context-local']+'\n')
        argv=['trainer','--experiment-protocol',str(f.path(ref)),'--experiment-arm','context-local',
              '--name',c.ARMS['context-local'],'--execute','--experiment-id','GENERATED']
        model=Mock()
        with patch('sys.argv',argv),patch('focus_learning_experiment.load_protocol',return_value=(report,rows)),\
             patch.object(trainer,'PROJECT_ROOT',f.root),patch.object(trainer,'RUNS',f.root/'runs'),\
             patch.object(trainer,'os_env_defaults',{}),patch.object(trainer,'load_mobilenetv4_conv_small'),\
             patch.object(t,'device',return_value=SimpleNamespace(type='mps')),\
             patch.object(c,'prepare_features',return_value=(model,'train','val')) as join,\
             patch.object(native.reviewed.full,'run',return_value=0) as run,redirect_stdout(io.StringIO()):
            self.assertEqual(trainer.main(),0)
        join.assert_called_once();run.assert_called_once()
        self.assertEqual(run.call_args.args[1:3],('train','val'))


class ContextBindingTests(unittest.TestCase):
    def setUp(self):
        self.f=inputs.CLITests();self.f.setUp();self.f.save()
        self.path=self.f.root/'context'
        self.doc=c.context.build(self.f.protocol,self.path)
        self.base=c.h.read(self.f.protocol)
    def tearDown(self):self.f.tearDown()

    def check(self,doc):
        p=self.f.root/'edited.json';p.write_text(json.dumps(doc))
        return c.verified_context(c.h.ref(p),self.base)

    def test_source_geometry_mask_and_membership_are_bound(self):
        self.assertEqual(self.check(self.doc),self.doc)
        for mode in ('bounds','crop','scene','extra','missing','blocked'):
            d=copy.deepcopy(self.doc)
            if mode=='bounds':d['members'][0]['geometry']['normalizedBounds'][0]+=.1
            if mode=='crop':d['members'][0]['localCrop']['sha256']='0'*64
            if mode=='scene':d['members'][0]['sceneKey']='unknown'
            if mode=='extra':d['members'].append(copy.deepcopy(d['members'][0]))
            if mode=='missing':d['members']=[]
            if mode=='blocked':d['blocked']=[{'id':'a'}]
            with self.subTest(mode=mode),self.assertRaises((ValueError,KeyError)):
                self.check(d)
        from PIL import Image
        mask=c.h.ROOT/self.doc['members'][0]['mask']['path']
        Image.new('L',c.context.SIZE,255).save(mask)
        d=copy.deepcopy(self.doc);d['members'][0]['mask']=c.h.ref(mask)
        with self.assertRaisesRegex(ValueError,'mask_changed'):self.check(d)


if __name__=='__main__':unittest.main()
