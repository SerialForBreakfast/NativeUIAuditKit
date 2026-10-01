"""Generated protocol/cache tests. No retained-data encoding or training."""
import copy
from contextlib import redirect_stdout
import hashlib
import io
import json
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch, Mock

import focus_native_body_experiment as e
import train_focus_ring_detector as trainer


class NativeExecutionTests(unittest.TestCase):
    def setUp(self):
        import torch
        from PIL import Image
        self.t = torch
        parent=e.h.ROOT/'.build/native-execution-tests';parent.mkdir(parents=True,exist_ok=True)
        from pathlib import Path
        self.root=Path(tempfile.mkdtemp(dir=parent))
        self.evidence=self.save('authority.json',dict(softwareFixtureOnly=True))
        self.rows=[]
        for i in range(8):
            p=self.root/f'{i}.png';Image.new('RGB',(256,256),(i*20,0,100)).save(p)
            self.rows.append(dict(id=f'r{i}',label=i%2,crop=e.h.ref(p),split='validation' if i>=6 else 'train'))
        self.old=self.rows[:2];self.human=self.rows[2:4];self.new=self.rows[4:6];self.val=self.rows[6:]
        self.x=torch.arange(8*576,dtype=torch.float32).reshape(8,576)
        self.y=torch.tensor([[r['label']] for r in self.rows],dtype=torch.float32)
        original=dict(trainCount=2,validationCount=2,trainFeatureSHA256=self.digest(self.x[:2]),
                      validationFeatureSHA256=self.digest(self.x[6:]),featureStateSHA256='encoder')
        old_ref=self.cache('old',original,(self.x[:2],self.y[:2]),(self.x[6:],self.y[6:]))
        old_ref['base']=self.save('old-base.json',dict(samples=self.old+self.val))
        extra=dict(featureSHA256=self.digest(self.x[2:4]),featureStateSHA256='encoder',members=self.members(self.human))
        human_ref=self.cache('human',extra,(self.x[2:4],self.y[2:4]))
        self.base=dict(version=e.reviewed.VERSION,protocolSHA256=e.assembly.BASE_SEAL,
                       baseCachedInputs=old_ref,inputs=dict(newFeatures=human_ref),
                       counts=dict(development=2,retention=0),unmetQualificationBlockers=['fixture-only'])
        self.base_ref=self.save('baseline.json',self.base)
        self.native=dict(samples=self.rows,baseline=self.base_ref,counts=dict(added=2,baselineTraining=4,training=6,evaluation=2),
             encodingPlan=dict(members=self.members(self.new),reuseTrainingIDs=[r['id'] for r in self.rows[:4]],
                               reuseEvaluationIDs=[r['id'] for r in self.val],featureStateSHA256='encoder'),
             configuration=dict(epochs=1000,batch=6,lr=.01,model='mobilenet_v3_small_frozen',maxSeconds=300),
             selection={'preserved':True},representation={'frozen':True},fullFit={'weights':{r['id']:1/6 for r in self.rows[:6]}},
             evaluationMembershipSHA256=e.h.digest(self.val),blockers=['encoding_budget_and_approval_required','changed_data_experiment_contract_required'])
        self.assembly_ref=self.save('assembly.json',self.native)
        self.spec=dict(version=e.INPUT_VERSION,assembly=self.assembly_ref,
                       encodingBudget=dict(maxSeconds=300,maxControls=8,batchSize=32,maxOutputBytes=1000000))
        # Only full historical/native intake is substituted; existing intake tests
        # cover it. Protocol, approvals, all three caches and trainer dispatch are real.
        self.patcher=patch.object(e,'verified_assembly',side_effect=lambda ref:copy.deepcopy(self.native))
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop();shutil.rmtree(self.root)

    @staticmethod
    def digest(t):return hashlib.sha256(t.contiguous().numpy().tobytes()).hexdigest()
    @staticmethod
    def members(rows):return [dict(id=r['id'],label=r['label'],crop=r['crop']) for r in rows]
    def save(self,name,doc):
        p=self.root/name;e.h.write(p,doc);return e.h.ref(p)
    def path(self,ref):return e.h.checked(e.h.ROOT,ref)
    def cache(self,name,receipt,train,validation=None):
        data=dict(receipt=receipt,train=train)
        if validation is not None:data['validation']=validation
        p=self.root/(name+'.pt');self.t.save(data,p)
        return dict(cache=e.h.ref(p),receipt=self.save(name+'-receipt.json',receipt))
    def encoding_approval(self,doc):
        return dict(version=e.ENCODING_APPROVAL,approved=True,protocolSHA256=doc['protocolSHA256'],
                    scope='encode-admitted-native-only-no-training',output=str((self.root/'encoded').relative_to(e.h.ROOT)),
                    budget=self.spec['encodingBudget'],authorizationReference=self.evidence)
    def prepared(self):
        before=e.make_protocol(self.spec);pref=self.save('pre-cache.json',before)
        approval=self.encoding_approval(before);ar=self.save('encode-approval.json',approval)
        receipt=dict(version=e.FEATURES,members=self.members(self.new),representation=before['representation'],
                     featureStateSHA256='encoder',backboneUnchanged=True,featureSHA256=self.digest(self.x[4:6]),
                     assembly=self.assembly_ref,budget=self.spec['encodingBudget'],encodingProtocol=pref,approval=ar,
                     output=approval['output'])
        refs=self.cache('native',receipt,(self.x[4:6],self.y[4:6]))
        spec=dict(self.spec,newFeatures=refs);doc=e.make_protocol(spec)
        protocol=self.save('ready.json',doc)
        run=dict(version=e.RUN_APPROVAL,approved=True,protocolSHA256=doc['protocolSHA256'],arm=e.ARM,
                 runName='generated-native-test',scope='one-run-no-export-no-promotion',authorizationReference=self.evidence)
        return doc,protocol,self.save('run-approval.json',run)

    def test_blocked_cli_has_no_model_import_or_output(self):
        doc=e.make_protocol(self.spec);ref=self.save('blocked.json',doc)
        argv=['trainer','--experiment-protocol',str(self.path(ref)),'--experiment-arm',e.ARM,'--name','generated-native-test','--execute']
        with patch.object(sys,'argv',argv),patch.dict(sys.modules,{'torch':None,'torchvision':None}),redirect_stdout(io.StringIO()) as out:
            self.assertEqual(trainer.main(),2)
        self.assertEqual(json.loads(out.getvalue())['blockers'],['missing_native_feature_cache','missing_run_approval'])
        self.assertFalse((trainer.RUNS/'generated-native-test').exists())
        with self.assertRaisesRegex(ValueError,'arm_or_name'):e.load_protocol(self.path(ref),'full-corpus-fit','foo')

    def test_empty_or_unadmitted_data_cannot_encode(self):
        self.native['counts']['added']=0
        self.native['samples']=self.rows[:4]+self.val;self.native['encodingPlan']['members']=[]
        self.native['blockers']=['no_admitted_native_controls']
        doc=e.make_protocol(self.spec)
        with self.assertRaisesRegex(ValueError,'data_not_ready'):
            e.check_encoding_approval(doc,self.encoding_approval(doc),self.root/'encoded')

    def test_budget_and_encoding_approval_exactness(self):
        for key,value in [('maxSeconds',301),('maxControls',1),('batchSize',64),('maxOutputBytes',1),('maxSeconds',True)]:
            bad=copy.deepcopy(self.spec);bad['encodingBudget'][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):e.make_protocol(bad)
        doc=e.make_protocol(self.spec);good=self.encoding_approval(doc)
        e.check_encoding_approval(doc,good,self.root/'encoded')
        for key,value in [('approved',False),('protocolSHA256','stale'),('output','reports/work/wrong'),('budget',{}),('version',e.RUN_APPROVAL)]:
            with self.subTest(key=key),self.assertRaises(ValueError):
                e.check_encoding_approval(doc,dict(good,**{key:value}),self.root/'encoded')
        ref=self.save('encoding-blocked.json',doc);bad=self.save('encoding-denied.json',dict(good,approved=False))
        with patch.dict(sys.modules,{'torch':None,'torchvision':None}),self.assertRaises(ValueError):
            e.encode_new(self.path(ref),self.path(bad),self.root/'encoded')
        self.assertFalse((self.root/'encoded').exists())

    def test_cache_join_preserves_all_three_sources_and_eval(self):
        doc,protocol,approval=self.prepared()
        report,rows=e.load_protocol(self.path(protocol),e.ARM,'generated-native-test',self.path(approval))
        self.assertTrue(report['launchEligible']);self.assertFalse(report['executionAuthorized'])
        out=self.root/'joined';out.mkdir()
        head,train,val=e.prepare_features(report,rows[:6],rows[6:],self.t.device('cpu'),out)
        self.assertEqual(sum(p.numel() for p in head.parameters()),577)
        self.assertTrue(self.t.equal(train.tensors[0],self.x[:6]));self.assertTrue(self.t.equal(train.tensors[1],self.y[:6]))
        self.assertTrue(self.t.equal(val.tensors[0],self.x[6:]))
        self.assertEqual(doc['selection'],self.native['selection']);self.assertEqual(doc['fullFit'],self.native['fullFit'])
        self.assertFalse(e.h.read(out/'native-feature-receipt.json')['encoderLoaded'])
        out2=self.root/'wrong-order';out2.mkdir()
        with self.assertRaises(ValueError):e.prepare_features(report,list(reversed(rows[:6])),rows[6:],self.t.device('cpu'),out2)

    def test_corrupt_tensor_receipt_order_labels_and_hash(self):
        self.prepared();receipt=e.h.read(self.root/'native-receipt.json')
        for mode in ('nan','width','dtype','label','feature-hash','receipt','order'):
            x=self.x[4:6].clone();y=self.y[4:6].clone();r=copy.deepcopy(receipt)
            if mode=='nan':x[0,0]=float('nan')
            if mode=='width':x=x[:,:4]
            if mode=='dtype':x=x.double()
            if mode=='label':y[0,0]=1
            if mode=='feature-hash':x[0,0]+=1
            if mode=='receipt':r['featureStateSHA256']='wrong'
            if mode=='order':x=x.flip(0)
            with self.subTest(mode=mode),self.assertRaises(ValueError):
                e.validate_tensors(dict(receipt=r,train=(x,y)),receipt,self.members(self.new))

    def test_changed_protocol_cache_and_receipt_rejected(self):
        doc,protocol,approval=self.prepared()
        for key in ('members','representation','featureStateSHA256','backboneUnchanged','assembly','budget','encodingProtocol'):
            receipt=e.h.read(self.root/'native-receipt.json');receipt[key]=None
            with self.subTest(key=key),self.assertRaises((ValueError,TypeError,KeyError)):
                e.receipt_check(receipt,doc)
        doc['samples'][-1]['label']=0;doc.pop('protocolSHA256');doc['protocolSHA256']=e.h.digest(doc)
        bad=self.save('tamper.json',doc)
        with self.assertRaisesRegex(ValueError,'protocol_inputs'):e.load_document(self.path(bad))
        (self.root/'native.pt').write_bytes(b'corrupted')
        with self.assertRaisesRegex(ValueError,'changed_hash'):e.load_document(self.path(protocol))

    def test_run_approval_not_encoding_approval_and_ordinary_loader_rejects(self):
        doc,protocol,approval=self.prepared()
        with self.assertRaises(ValueError):e.load_protocol(self.path(protocol),e.ARM,'other-run',self.path(approval))
        with self.assertRaises(ValueError):e.load_protocol(self.path(protocol),e.ARM,'generated-native-test',self.root/'encode-approval.json')
        dataset=self.root/'dataset';dataset.mkdir();e.h.write(dataset/'focus_dataset_manifest.json',doc)
        from focus_training_preflight import preflight
        self.assertIn('native_body_requires_explicit_experiment_mode',preflight(dataset,'generated-native-test')['blockers'])
        with self.assertRaises(ValueError):trainer.load_samples(dataset,'train')

    def test_actual_trainer_execution_dispatch_without_model_work(self):
        doc,protocol,approval=self.prepared()
        research=self.root/'Research';research.mkdir()
        (research/'ExperimentLog.md').write_text('## Run GENERATED software fixture\n'+doc['protocolSHA256']+' '+e.ARM+' generated-native-test\n')
        argv=['trainer','--experiment-protocol',str(self.path(protocol)),'--experiment-arm',e.ARM,
              '--name','generated-native-test','--experiment-approval',str(self.path(approval)),
              '--execute','--experiment-id','GENERATED']
        model=Mock()
        with patch.object(sys,'argv',argv),patch.object(trainer,'PROJECT_ROOT',self.root),patch.object(trainer,'RUNS',self.root/'runs'),\
             patch.object(trainer,'os_env_defaults',{}),patch.object(trainer,'load_mobilenetv4_conv_small'),\
             patch.object(self.t,'device',return_value=SimpleNamespace(type='mps')),\
             patch.object(e,'prepare_features',return_value=(model,'train-tensors','val-tensors')) as join,\
             patch.object(e.reviewed.full,'run',return_value=0) as run,redirect_stdout(io.StringIO()):
            self.assertEqual(trainer.main(),0)
        join.assert_called_once();run.assert_called_once()
        self.assertEqual(run.call_args.args[1:3],('train-tensors','val-tensors'))
        self.assertEqual([r['id'] for r in run.call_args.args[4]], [r['id'] for r in self.rows[:6]])

    def fake_encoder_context(self):
        """Exercise orchestration with generated tensors, never run a backbone."""
        from contextlib import ExitStack
        import focus_pretrained_experiment as encoder
        stack=ExitStack()
        weights=self.root/'weights.pt';self.t.save({},weights)
        self.native['representation']['weights']=e.h.ref(weights)
        network=Mock();features=Mock()
        factory=Mock(return_value=network)
        stack.enter_context(patch.dict(sys.modules,{'torchvision.models':SimpleNamespace(mobilenet_v3_small=factory)}))
        stack.enter_context(patch.object(encoder,'WEIGHTS_SHA',e.h.sha(weights)))
        stack.enter_context(patch.object(encoder,'state_digest',return_value='encoder'))
        stack.enter_context(patch.object(self.t.backends.mps,'is_available',return_value=True))
        sequence=stack.enter_context(patch.object(self.t.nn,'Sequential',return_value=features))
        features.to.return_value=features
        def encoded(feature,dataset,device,deadline):
            self.assertEqual(len(dataset),2)
            for i in range(2):
                x,y=dataset[i];self.assertEqual(x.shape,(3,256,256));self.assertEqual(y.item(),self.new[i]['label'])
            return self.t.utils.data.TensorDataset(self.x[4:6],self.y[4:6]),'encoder'
        stack.enter_context(patch.object(encoder,'encode',side_effect=encoded))
        stack.enter_context(patch.object(self.t.mps,'current_allocated_memory',return_value=0))
        stack.enter_context(patch.object(self.t.mps,'driver_allocated_memory',return_value=0))
        return stack,factory

    def test_encoder_orchestration_receipt_and_protocol_roundtrip(self):
        stack,factory=self.fake_encoder_context()
        with stack:
            doc=e.make_protocol(self.spec);protocol=self.save('encoding-protocol.json',doc)
            approval=self.save('encoding-approval.json',self.encoding_approval(doc))
            result=e.encode_new(self.path(protocol),self.path(approval),self.root/'encoded')
            factory.assert_called_once_with(weights=None)
            refs=e.h.read(result);final=e.make_protocol(dict(self.spec,newFeatures=refs))
            self.assertEqual(final['blockers'],[])
            report=e.h.read(self.path(refs['receipt']))
            self.assertEqual(report['members'],self.members(self.new))
            self.assertEqual(report['budget'],self.spec['encodingBudget'])
            with self.assertRaisesRegex(ValueError,'output_collision'):
                e.encode_new(self.path(protocol),self.path(approval),self.root/'encoded')

    def test_encoder_time_and_output_limits_leave_no_success_cache(self):
        import focus_pretrained_experiment as encoder
        stack,_=self.fake_encoder_context()
        with stack:
            doc=e.make_protocol(self.spec);protocol=self.save('encoding-protocol.json',doc)
            approval=self.save('encoding-approval.json',self.encoding_approval(doc))
            with patch.object(e.time,'monotonic',side_effect=[0,301]),self.assertRaisesRegex(ValueError,'time_cap'):
                e.encode_new(self.path(protocol),self.path(approval),self.root/'encoded')
            self.assertFalse((self.root/'encoded').exists())
            with patch.object(self.t,'save',side_effect=lambda data,stream:stream.write(b'x'*1000001)),\
                 self.assertRaisesRegex(ValueError,'output_cap'):
                e.encode_new(self.path(protocol),self.path(approval),self.root/'encoded')
            self.assertFalse((self.root/'encoded').exists())
            with patch.object(encoder,'state_digest',return_value='wrong'),self.assertRaisesRegex(ValueError,'wrong_encoder_state'):
                e.encode_new(self.path(protocol),self.path(approval),self.root/'encoded')


if __name__=='__main__':unittest.main()
