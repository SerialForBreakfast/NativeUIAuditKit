import copy
import io
import json
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, Mock

from PIL import Image
import focus_visual_experiment as v
import focus_full_fit_experiment as fit


class InputTests(unittest.TestCase):
    def test_scale_is_not_candidate_normalized(self):
        a=v.window([100,100,100,80],(1920,1080));b=v.window([90,92,120,96],(1920,1080))
        self.assertEqual(a,b)
        self.assertAlmostEqual((120*256/b[2])/(100*256/a[2]),1.2)

    def test_edges_pad_not_rescale(self):
        image=Image.new('RGB',(200,100),'white')
        result=v.context_image(image,[0,0,20,20])
        self.assertEqual(result.size,(256,256));self.assertEqual(result.getpixel((0,0)),(0,0,0))
        self.assertEqual(result.getpixel((128,128)),(255,255,255))
        with self.assertRaises(ValueError):v.window([0,0,float('nan'),20],(200,100))

    def test_roles_duplicates_and_labels(self):
        row=dict(id='a',split='train',use='train-candidate',label=1)
        v.protected([row])
        for rows in ([row,row],[dict(row,use='final-challenge')],[dict(row,label=2)]):
            with self.assertRaises(ValueError):v.protected(rows)

    def test_mask_is_target_bound_and_keeps_growth(self):
        a=v.context_mask(dict(contextSide=600,bounds=[0,0,100,60]))
        b=v.context_mask(dict(contextSide=600,bounds=[0,0,120,72]))
        self.assertAlmostEqual(float(b.sum()/a.sum()),1.44,places=5)
        self.assertGreater(a[7:9,7:9].sum(),0);self.assertEqual(a[0,0],0)
        tiny=v.context_mask(dict(contextSide=2000,bounds=[0,0,1,1]))
        self.assertGreater(tiny.sum(),0)

    def test_changed_reference_rejected(self):
        parent=v.h.ROOT/'.build/visual-tests';parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as tmp:
            p=Path(tmp)/'generated.json';p.write_text('{}');ref=v.h.ref(p)
            p.write_text('{"changed":true}')
            with self.assertRaises(ValueError):v.previous.read(ref)

    def test_input_counts_allow_bound_source_metadata_not_missing_members(self):
        rows=[dict(id=str(i),split='train' if i<1550 else 'validation',
                   use='train-candidate' if i<1550 else 'representative-selection',label=i%2) for i in range(1883)]
        records=[dict(id=r['id'],bounds=[0,0,10,10],sourceSize=[100,100],contextSide=60,local={},context={}) for r in rows]
        doc=dict(version='focus-visual-input-v1',sourceSamples=rows,records=records,
                 counts=dict(training=1550,development=315,retention=18,evaluation=333,added=564))
        with patch.object(v.h,'checked'):
            v.validate_inputs(doc)
            doc['records']=records[:-1]
            with self.assertRaises(ValueError):v.validate_inputs(doc)


class LearningTests(unittest.TestCase):
    def setUp(self):
        import torch
        self.t=torch

    def network(self,rep):
        t=self.t;t.manual_seed(1)
        return SimpleNamespace(features=t.nn.Sequential(*[t.nn.Identity() for _ in range(9)],
            t.nn.Conv2d(96,576,1),t.nn.BatchNorm2d(576),t.nn.ReLU()))

    def test_tail_gradients_and_frozen_bn(self):
        t=self.t;x=t.randn(2,2,97,2,2);x[:,:,-1]=1
        outputs=[]
        for arm in v.ARMS:
            with patch.object(v,'make_network',side_effect=self.network):m=v.make_model({},arm,'cpu')
            m.train();outputs.append(m(x).detach())
            before={k:p.detach().clone() for k,p in m.tail.state_dict().items()}
            opt=t.optim.AdamW(m.optimizer_groups(.01,.001))
            m(x).sum().backward()
            if arm.endswith('partial'):self.assertGreater(m.tail[0].weight.grad.abs().sum(),0)
            else:self.assertIsNone(m.tail[0].weight.grad)
            opt.step()
            self.assertTrue(t.equal(before['10.running_mean'],m.tail[1].running_mean))
            self.assertTrue(t.equal(before['10.weight'],m.tail[1].weight))
            self.assertEqual(t.equal(before['9.weight'],m.tail[0].weight),arm.endswith('frozen'))
        for o in outputs[1:]:self.assertTrue(t.equal(outputs[0],o))

    def test_accumulation_equivalence_and_abort(self):
        t=self.t;t.manual_seed(2);a=t.nn.Linear(3,1);b=copy.deepcopy(a)
        x=t.randn(7,3);y=t.tensor([[0.],[1.],[1.],[0.],[1.],[0.],[1.]])
        w=t.arange(1,8,dtype=t.float32).reshape(-1,1)/28
        la=fit.weighted_backward(a,x,y,w,7,time.monotonic()+10)
        lb=fit.weighted_backward(b,x,y,w,3,time.monotonic()+10)
        self.assertAlmostEqual(la,lb,places=6)
        for p,q in zip(a.parameters(),b.parameters()):self.assertTrue(t.allclose(p.grad,q.grad,atol=1e-7))
        self.assertIsNone(fit.weighted_backward(a,x,y,w,3,0))
        self.assertTrue(all(p.grad is None for p in a.parameters()))

    def test_visual_run_does_not_stop_at_training_fit(self):
        t=self.t
        parent=v.h.ROOT/'.build/visual-tests';parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as tmp:
            out=Path(tmp);(out/'weights').mkdir()
            with patch.object(v,'make_network',side_effect=self.network):m=v.make_model({},'visual-local-frozen','cpu')
            rows=[dict(id=str(i),split='train',use='human-static-auxiliary' if i else 'train-candidate',label=i) for i in range(2)]
            x=t.randn(2,2,97,2,2);x[:,:,-1]=1
            data=t.utils.data.TensorDataset(x,t.tensor([[0.],[1.]]))
            from focus_pretrained_experiment import state_digest
            report=dict(visualTraining=True,arm='visual-local-frozen',features={},representation={},
                configuration=dict(epochs=12,lr=.01,model='generated'),protocolSHA256='generated',
                selection={},fullFit=dict(weights={'0':.5,'1':.5},weightDecay=.01,tailLR=.0001,microbatch=1,validationEvery=5),
                initialTailSHA256=state_digest(m.tail),initialBNSHA256=state_digest(t.nn.ModuleList([m.tail[1]])))
            check=fit.require
            def guard(ok,msg):
                if msg!='full_fit_requires_mps':check(ok,msg)
            score=dict(checkpointEligible=True,selectionLoss=.1)
            start=time.monotonic()
            with patch.object(fit,'require',side_effect=guard),patch.object(fit.s.rep,'selection_metrics',return_value=score),\
                 patch.object(fit,'training_metrics',return_value=dict(fitPass=True,groups={'overall':{'weightedBCE':0.,'confidentCorrect':2}})):
                fit.run(m,data,data,report,rows,rows,'cpu',out,start,start+30,'generated')
            result=json.loads((out/'experiment-result.json').read_text())
            self.assertEqual(len(result['history']),12);self.assertEqual(result['stopReason'],'update_cap')
            self.assertEqual([r['update'] for r in result['history'] if r['validation']], [5,10,12])
            self.assertFalse(result['visualState']['tailChanged'])
            checkpoint=t.load(out/'weights/best.pt',weights_only=True)
            self.assertEqual(checkpoint['checkpointKind'],'visual-partial-candidate-v1')


class CallerTests(unittest.TestCase):
    def test_adapter_report_and_real_positive_cli_dispatch(self):
        import torch
        import train_focus_ring_detector as trainer
        parent=v.h.ROOT/'.build/visual-tests';parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as tmp:
            root=Path(tmp);name='generated-'+root.name;arm='visual-local-frozen'
            rows=[dict(id=str(i),split='train' if i==0 else 'validation',label=i,
                       use='train-candidate' if i==0 else 'representative-selection',crop={'path':'generated.png'}) for i in range(2)]
            source=dict(sourceSamples=rows,sourceConfiguration=dict(lr=.01,batch=1550,maxSeconds=300),
                        fullFit=dict(weights={'0':1.},weightDecay=.01),selection={})
            with patch.dict(v.ARMS,{arm:name}):
                doc=dict(version=v.VERSION,arms=dict(v.ARMS),samples=rows,inputs={'path':'generated-input'},
                    features=dict(cache={'path':'generated-cache'},receipt={'path':'generated-receipt'}),authority={'path':'generated-authority'},
                    configuration=dict(source['sourceConfiguration'],model='mobilenet_v3_small_partial_visual',
                                       initialization='imagenet-prefix-tail-fresh-mlp',epochs=100),
                    fullFit=dict(source['fullFit'],microbatch=32,tailLR=.0001,validationEvery=10,stopOnFit=False),
                    selection={},counts={},representation={},unmetQualificationBlockers=[],
                    runtime=dict(code=[v.h.ref(v.h.ROOT/'scripts'/n) for n in v.CODE],packages=v.packages()),
                    limits=dict(runs=4,secondsPerRun=300,wallSeconds=1800,outputBytes=2*1024**3))
                doc['protocolSHA256']=v.h.digest(doc);path=root/'protocol.json';path.write_text(json.dumps(doc))
                ap=root/'approval.json';ap.write_text(json.dumps(v.approval(doc)))
                def read(ref):
                    if ref['path']==v.h.ref(path)['path']:return doc
                    if ref['path']=='generated-input':return source
                    if ref['path']=='generated-receipt':return dict(inputs=doc['inputs'],ids=['0','1'])
                    return json.loads(ap.read_text())
                with patch.object(v.previous,'read',side_effect=read),patch.object(v.h,'checked'):
                    report,actual_rows=v.load_protocol(path,arm,name,ap)
                self.assertIsNone(report['warmCheckpoint']);self.assertTrue(report['launchEligible'])
                (root/'Research').mkdir();(root/'Research/ExperimentLog.md').write_text(
                    '## Run GENERATED software fixture\n'+doc['protocolSHA256']+' '+arm+' '+name)
                report['approval']=None
                with patch('sys.argv',['trainer','--experiment-protocol',str(path),'--experiment-arm',arm,
                            '--name',name,'--execute','--experiment-id','GENERATED']),\
                     patch('focus_learning_experiment.load_protocol',return_value=(report,actual_rows)),\
                     patch.object(trainer,'PROJECT_ROOT',root),patch.object(trainer,'RUNS',root/'runs'),\
                     patch.object(trainer,'os_env_defaults',{}),patch.object(trainer,'load_mobilenetv4_conv_small'),\
                     patch.object(torch,'device',return_value=SimpleNamespace(type='mps')),\
                     patch.object(v,'prepare_features',return_value=(Mock(),'train','val')) as join,\
                     patch.object(fit,'run',return_value=0) as execute,redirect_stdout(io.StringIO()):
                    self.assertEqual(trainer.main(),0)
                join.assert_called_once();execute.assert_called_once()

    def test_actual_cli_rejects_missing_approval_before_torch(self):
        import train_focus_ring_detector as trainer
        report=dict(configuration=dict(epochs=100,batch=1550,lr=.01,model='generated'),
                    launchEligible=False,blockers=['missing_visual_approval'])
        with patch('focus_learning_experiment.load_protocol',return_value=(report,[])),\
             patch.dict('sys.modules',{'torch':None}),\
             patch('sys.argv',['trainer','--experiment-protocol','generated.json','--experiment-arm',
                               'visual-local-frozen','--name','generated','--execute']),redirect_stdout(io.StringIO()) as out:
            self.assertEqual(trainer.main(),2)
        self.assertEqual(json.loads(out.getvalue())['blockers'],['missing_visual_approval'])


if __name__=='__main__':unittest.main()
