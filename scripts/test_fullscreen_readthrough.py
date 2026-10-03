import json
import os
import unittest
from unittest.mock import patch
import test_train_fullscreen_focus as baseline
import train_fullscreen_focus as f
import fullscreen_readthrough as r


class ReadThroughTests(baseline.RunnerTests):
    def v2(self):
        self.doc.update(version='fullscreen-focus-run-v2',storage='read-through',evaluationPolicy='terminal-last-checkpoint')
        self.doc['frames'][1]['split']='evaluation';self.refresh()
        return f.validate(self.contract)

    def test_direct_stage_no_image_copies(self):
        doc,checked=self.v2();out=self.root/'direct';out.mkdir();f.stage(doc,checked,out)
        self.assertEqual(checked['stagingBytes'],0)
        self.assertEqual({p.name for p in out.iterdir()},{'configuration.json','validated.json'})

    def test_unlimited_time_requires_explicit_authority(self):
        self.v2();self.doc['budget']['seconds']=None;self.refresh()
        with self.assertRaisesRegex(ValueError,'missing_time_limit_authority'):f.validate(self.contract)
        authority=self.root/'time.json';f.h.write(authority,dict(version='local-training-time-override-v1',
            approved=True,wallTimeLimit=None,approvedBy='unit-test-only'))
        self.doc['timeLimitOverride']=f.h.ref(authority);self.refresh();f.validate(self.contract)
        self.assertEqual(self.launch('print("completed")',seconds=None)['outcome'],'completed')

    def test_diagnostic_check_does_not_admit(self):
        self.v2();p=self.root/'admission.json';a=json.loads(p.read_text());a['approved']=False
        p.write_text(json.dumps(a));self.doc['admission']=f.h.ref(p);self.contract.write_text(json.dumps(self.doc))
        f.validate(self.contract,inputs_only=True)
        with self.assertRaisesRegex(ValueError,'membership_not_admitted'):f.validate(self.contract)

    def test_actual_dataset_ignores_adjacent_cache(self):
        from ultralytics.cfg import get_cfg
        _,checked=self.v2();frame=checked['frames'][0]
        cache=self.root/'0.npy';cache.write_bytes(b'corrupt, must not be read or removed')
        before=cache.read_bytes()
        dataset=r.dataset_type()([frame],data={'names':{0:'focusedControl'},'channels':3},
            imgsz=640,batch_size=1,augment=False,hyp=get_cfg(),rect=False,stride=32)
        sample=dataset[0]
        self.assertEqual(tuple(sample['img'].shape),(3,640,640))
        self.assertEqual(len(sample['cls']),1);self.assertEqual(cache.read_bytes(),before)
        self.assertFalse(any(self.root.glob('*.cache')))

    def test_terminal_trainer_no_evaluation_loader_or_validator(self):
        _,checked=self.v2();Trainer=r.trainer_type(checked['frames']);trainer=object.__new__(Trainer)
        self.assertEqual(trainer.get_dataset()['val'],'train')
        with self.assertRaisesRegex(ValueError,'evaluation_access'):trainer.build_dataset('evaluation')
        trainer.validator=lambda *_:self.fail('evaluation ran inside training')
        self.assertEqual(trainer.validate(),({},0.));trainer.final_eval()

    def test_outside_source_and_changed_hash_rejected(self):
        with self.assertRaises(ValueError):f.source_image({'path':'/etc/hosts','sha256':'0'*64})
        ref=dict(self.doc['frames'][0]['image'],sha256='0'*64)
        with self.assertRaises(ValueError):f.source_image(ref)

    def test_verified_pixels_reused_only_with_unchanged_bytes(self):
        _,checked=self.v2()
        _,again=f.validate(self.contract,_verified_frames=checked['frames'])
        self.assertEqual(again,checked)
        (self.root/'0.png').write_bytes(b'changed')
        with self.assertRaises(ValueError):f.validate(self.contract,_verified_frames=checked['frames'])

    def test_supervised_v2_child_requires_parent_seal(self):
        doc,checked=self.v2();out=self.root/'sealed';out.mkdir();f.stage(doc,checked,out)
        with patch.dict(os.environ,{'NUIAK_SUPERVISOR_PID':str(os.getppid()),'NUIAK_VALIDATED_SHA256':'bad'}):
            with self.assertRaisesRegex(ValueError,'changed_parent_validation'):f.child(out)
        with patch.dict(os.environ,{'NUIAK_SUPERVISOR_PID':str(os.getppid()),
                'NUIAK_VALIDATED_SHA256':f.h.sha(out/'validated.json')}),patch.object(r,'train_terminal') as train:
            f.child(out)
            self.assertEqual(train.call_args.args,(doc,checked,out))

    def test_evaluation_only_rejects_incomplete_fit(self):
        import evaluate_completed_fullscreen as evaluation
        doc,checked=self.v2();out=self.root/'incomplete';out.mkdir();f.stage(doc,checked,out)
        f.h.write(out/'training-complete.json',dict(epochs=0,selection='fixed-last-epoch',checkpoint=doc['checkpoint']))
        with self.assertRaisesRegex(ValueError,'incomplete_fit'):evaluation.execute(out,self.root/'forbidden-output')
        self.assertFalse((self.root/'forbidden-output').exists())

    def test_evaluation_only_child_uses_bound_checkpoint(self):
        import evaluate_completed_fullscreen as evaluation
        doc,checked=self.v2();out=self.root/'eval-only';out.mkdir()
        fit=self.root/'fit.json';f.h.write(fit,dict(epochs=1,selection='fixed-last-epoch',checkpoint=doc['checkpoint']))
        f.h.write(out/'fit.json',dict(receipt=f.h.ref(fit)));f.h.write(out/'validated.json',checked)
        with patch.dict(os.environ,{'NUIAK_SUPERVISOR_PID':str(os.getppid()),
                'NUIAK_VALIDATED_SHA256':f.h.sha(out/'validated.json')}),patch('sys.addaudithook'),\
                patch.object(r,'evaluate_terminal') as score:
            evaluation.child(out)
            self.assertEqual(score.call_args.args,(doc,checked,self.root/'model.pt',out))

    def test_scoring_duplicates_and_misses(self):
        self.assertEqual(r.score_boxes([[0,0,10,10]]*2,[[0,0,10,10],[20,20,30,30]]),dict(tp=1,fp=1,fn=1))

    def test_terminal_caller_uses_last_and_only_scores_evaluation(self):
        from types import SimpleNamespace
        import torch
        doc,checked=self.v2();out=self.root/'terminal';out.mkdir()
        doc['augmentation']=dict(version=1,translate=.05,scale=.2)
        calls=[]
        class Model:
            def __init__(model,path):calls.append(('load',path))
            def train(model,**kwargs):
                calls.append(('train',kwargs))
                last=out/'last.pt';last.write_bytes(b'test-double-only')
                model.trainer=SimpleNamespace(epoch=0,last=last)
            def predict(model,**kwargs):
                calls.append(('predict',kwargs))
                return [SimpleNamespace(boxes=SimpleNamespace(conf=torch.tensor([.9]),
                    xyxy=torch.tensor([[2.,2.,12.,7.]])))]
        with patch('ultralytics.YOLO',Model),patch('sys.addaudithook'):
            r.train_terminal(doc,checked,out)
        predictions=[v for k,v in calls if k=='predict']
        self.assertEqual([v['source'] for v in predictions],[checked['frames'][1]['absoluteImage']])
        self.assertEqual([v for k,v in calls if k=='load'][-1],str(out/'last.pt'))
        self.assertFalse([v for k,v in calls if k=='train'][0]['val'])
        options=[v for k,v in calls if k=='train'][0]
        self.assertEqual((options['translate'],options['scale']),(.05,.2))
        result=json.loads((out/'terminal-evaluation.json').read_text())
        self.assertEqual(result['totals'],dict(tp=1,fp=0,fn=0))


if __name__=='__main__':unittest.main()
