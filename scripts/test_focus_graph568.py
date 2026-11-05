import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import torch
from PIL import Image
import research_queue as q
from template_inputs398 import pin
from focus_dataset_contract import digest,pixel_digest
from focus_corpus568 import replay_members,partitions,assert_isolation,validate_native
from focus_replay568 import schedule

class FocusGraphTests(unittest.TestCase):
    def test_reserved_samples_are_not_read_or_admitted(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='roles568-') as temp:
            image=Path(temp)/'crop.png';Image.new('RGB',(256,256),'red').save(image)
            px=pixel_digest(q.ROOT,pin(image))
            samples=[dict(id=str(i),role='train',crop=pin(image),pixelSHA256=px,label=i%2,group='train') for i in range(96)]
            samples += [dict(id='reserved'+str(i),role='reserved',group='reserved') for i in range(16)]
            replay=[dict(id='legacy'+str(i),crop=pin(image),pixelSHA256=px,label=i%2,pairID=str(i//2)) for i in range(56)]
            legacy=Path(temp)/'legacy.json';q.save(legacy,dict(pairs=[dict(pair_id=str(i),split='train',focused_crop='crop.png',unfocused_crop='crop.png') for i in range(28)]))
            doc=dict(samples=samples,replay=replay,replayManifest=pin(legacy));doc['protocolSHA256']=digest(doc)
            rows=replay_members(doc);self.assertEqual(len(rows),152)
            self.assertFalse(any('reserved' in r['id'] for r in rows))
            doc['samples'][0]['role']='reserved';doc.pop('protocolSHA256');doc['protocolSHA256']=digest(doc)
            with self.assertRaisesRegex(ValueError,'replay_membership'):replay_members(doc)

    def test_duplicate_pixels_connect_split_groups(self):
        rows=[dict(group=g,pixelSHA256=p) for g,p in [('a','x'),('b','x'),('c','y'),('d','z')]]
        result=partitions(rows);self.assertEqual(result[0]['role'],result[1]['role'])
        with self.assertRaisesRegex(ValueError,'cross_partition_crop'):
            assert_isolation([dict(pixelSHA256='x',label=1,role='train'),dict(pixelSHA256='x',label=1,role='validation')],set())
        with self.assertRaisesRegex(ValueError,'protected_crop_overlap'):
            assert_isolation([dict(pixelSHA256='x',label=1,role='train')],{'x'})

    def test_schedules_match_updates_and_exclude_validation(self):
        rows=[dict(id=s+str(i),role='train',source=s,label=i%2,group=s) for s in ('native-replay','focus556-native') for i in range(4)]
        rows.append(dict(id='v',role='validation',source='focus556-native',label=1,group='validation'))
        corpus=dict(version='native-focus-corpus568-v1',trainingAdmitted=True,rows=rows)
        for arm in ('control','native','boost'):
            selected=schedule(corpus,arm);self.assertEqual(len(selected),8);self.assertNotIn('v',[r['id'] for r in selected])
            self.assertEqual(sum(r['label'] for r in selected),4)
        self.assertTrue(all(r['source']=='native-replay' for r in schedule(corpus,'control')))

    def test_existing_training_loop_consumes_explicit_samples(self):
        from train_focus556 import train_model
        class Toy(torch.nn.Module):
            def __init__(self):super().__init__();self.classifier=torch.nn.Linear(3,1)
            def forward(self,x):return self.classifier(x.mean((2,3)))
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='train568-') as temp:
            root=Path(temp);model=Toy();torch.save(dict(state_dict=model.state_dict()),root/'base.pt')
            samples=[]
            for label in (0,1):
                path=root/(str(label)+'.png');Image.new('RGB',(256,256),(label*200,0,0)).save(path)
                samples.append(dict(path=str(path),label=float(label)))
            history=[]
            with patch('train_focus556.load_mobilenetv4',side_effect=Toy),patch('torch.backends.mps.is_available',return_value=False),patch('train_focus556.build_samples',side_effect=AssertionError('implicit dataset read')):
                checkpoint=train_model('toy',root/'out',epochs=2,batch_size=2,samples=samples,initialization=root/'base.pt',epoch_callback=lambda n,l:history.append(n))
            self.assertTrue(checkpoint.is_file());self.assertEqual(history,[1,2])

    def test_retained_native_brackets_validate(self):
        root=q.ROOT/'dataset/tvos_captures/focus556/out-4k';row=q.load(root/'manifest.json')[0]
        meta=q.load(root/row['metadata']['metadataPath']);result=validate_native(row,meta,root)
        self.assertEqual([r['label'] for r in result],[1,0])
        meta=copy.deepcopy(meta);meta['focused_capture']['frame_png_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'frame_hash'):validate_native(row,meta,root)

    def test_matched_report_rejects_lost_success_and_incomplete_anchors(self):
        from focus_replay568 import compare_reports
        reference=dict(suiteSHA256='fixed',threshold=.85,outcomes=[dict(id=str(i),correct=False,wrong=False) for i in range(21)],legacyLabels=[1]*270,legacyProbabilities=[.99]*270)
        control=dict(reference,arm='control',anchors=[dict(id=scope+'-'+str(i),label=1,before=.99,after=.99) for scope,n in [('reserved',16),('calibration',8)] for i in range(n)],
            development=dict(D1=0,D2=0,D3=0),retention=dict(tp=270,tn=0),ancillary={})
        native=copy.deepcopy(control);native['arm']='native';native['development']=dict(D1=21,D2=0,D3=21)
        for row in native['outcomes']:row['correct']=True
        self.assertEqual(compare_reports(reference,control,native)['outcome'],'supported')
        native['legacyProbabilities'][0]=.1
        self.assertEqual(compare_reports(reference,control,native)['outcome'],'contradicted')
        native['legacyProbabilities'][0]=.99
        control['anchors'][0]['before']=native['anchors'][0]['before']=.1
        native['anchors'][0]['after']=.1
        self.assertEqual(compare_reports(reference,control,native)['outcome'],'contradicted')
        native['anchors'].pop()
        with self.assertRaisesRegex(ValueError,'anchor_count|anchor_membership'):compare_reports(reference,control,native)

    def test_native_pixel_conflict_quarantines_whole_pair(self):
        from focus_corpus568 import quarantine_native
        native=[dict(id='a-focused',label=1,pixelSHA256='same',image={}),dict(id='a-unfocused',label=0,pixelSHA256='same',image={}),dict(id='b-focused',label=1,pixelSHA256='b1',image={}),dict(id='b-unfocused',label=0,pixelSHA256='b0',image={})]
        kept,excluded=quarantine_native([],native,set())
        self.assertEqual(len(kept),2);self.assertEqual(len(excluded),2)
        self.assertTrue(all(r['id'].startswith('b-') for r in kept))

    def test_production_swift_crop_path(self):
        import focus_runtime as runtime
        import base64,io
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='crop568-') as temp:
            path=Path(temp)/'image.png';Image.new('RGB',(128,128),'red').save(path)
            reply=runtime.invoke([dict(id='fractional',path=str(path),sha256=q.digest(path),bounds=[30.5,32.25,40.25,20.5])])
            with Image.open(io.BytesIO(base64.b64decode(reply['results'][0]['png']))) as image:
                self.assertEqual(image.size,(256,256));self.assertEqual(image.convert('RGB').getpixel((128,128)),(255,0,0))

    def test_compiler_reuses_two_descriptions_and_queue_comparison(self):
        import focus_graph568 as compiler
        import research_approval as approval
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='graph568-') as temp:
            root=Path(temp);request=q.load(q.ROOT/'reports/work/FOCUS568/request.json')
            for ident in ('unit568','reuse568'):
                value=dict(request,id=ident);q.save(root/(ident+'.json'),value)
                manifest=compiler.compile_request(root/(ident+'.json'),root/ident)
                self.assertEqual(len(manifest['jobs']),9)
            reference=dict(suiteSHA256='fixed',threshold=.85,outcomes=[dict(id=str(i),correct=False,wrong=False) for i in range(21)],legacyLabels=[1]*270,legacyProbabilities=[.99]*270)
            control=dict(reference,arm='control',anchors=[dict(id=scope+'-'+str(i),label=1,before=.99,after=.99) for scope,n in [('reserved',16),('calibration',8)] for i in range(n)],development=dict(D1=0,D2=0,D3=0),retention=dict(tp=270,tn=0),ancillary={})
            native=copy.deepcopy(control);native['arm']='native'
            refs={}
            for name,value in [('reference',reference),('control',control),('native',native)]:
                path=root/(name+'.json');q.save(path,value);refs[name]=pin(path)
            spec=q.load(root/'unit568/unit568-compare.json');spec['dependencies']=[]
            spec['template']['inputs']=refs;spec['inputs']=[pin(q.MODULES/'focus_replay568.py')]+list(refs.values())
            spec['evidence']['reads']=[v['path'] for v in refs.values()]
            q.save(root/'queue-spec.json',spec);queue=root/'queue';q.submit(root/'queue-spec.json',queue)
            approval.approve(queue,spec['id'],'test','Synthetic software qualification only.')
            self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[spec['id']]),[(spec['id'],'complete')])
            report=q.load(queue/'jobs'/spec['id']/'attempts/1/out/benchmark_summary.json')
            self.assertFalse(report['modelAccepted']);self.assertEqual(report['metricsStatus'],'provisional')
