"""Offline rectangular batching and real trainer entrypoint timing tests."""
import copy
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace as NS, ModuleType
import unittest
from unittest.mock import Mock, patch

from ohem_callback import OHEMCallback, rectangular_keys, sync_dataset_lists
from training_timing import TrainingTiming
import train_ios_model as entry

ROOT = Path(__file__).resolve().parent.parent


def trainer():
    ds = NS(im_files=list("abcde"), labels=[{"im_file": f, "box": [i]} for i, f in enumerate("abcde")],
            rect=True, batch_size=2, batch=[0, 0, 1, 1, 2],
            batch_shapes=[[320, 640], [640, 320], [640, 320]], buffer=[0, 2])
    return NS(train_loader=NS(dataset=ds, reset=Mock()), preprocess_batch=lambda b: b)


class BatchTests(unittest.TestCase):
    def test_rect_partial_batch_alignment_and_noncompounding(self):
        t = trainer(); ds = t.train_loader.dataset; cb = OHEMCallback(fraction=1)
        cb.on_pretrain_routine_end(t)
        for hard in ("e", "b", "e"):
            cb._epoch_loss[hard].append(8)
            cb.on_train_epoch_end(t)
            self.assertEqual(ds.im_files.count(hard), 2)
            self.assertEqual([l['im_file'] for l in ds.labels], ds.im_files)
            self.assertEqual(ds.ni, 5)
            self.assertEqual(ds.buffer, [])
            self.assertEqual(ds.ims, [None]*5)
            for i, f in enumerate(ds.im_files):
                self.assertEqual(cb._keys[i], cb._keys["abcde".index(f)])
        self.assertEqual(t.train_loader.reset.call_count, 3)
        ds.labels[2]['box'].append(999)
        self.assertNotIn(999, ds.labels[4]['box'])  # duplicate labels are independent

    def test_unfulfilled_and_no_cross_shape_fallback(self):
        t = trainer(); cb = OHEMCallback(fraction=1, factor=4)
        cb.on_pretrain_routine_end(t); cb._epoch_loss['a'].append(1)
        cb.on_train_epoch_end(t)
        self.assertEqual(t.train_loader.dataset.im_files, list('aacde'))
        self.assertEqual(cb.last_replacements, dict(requested=3, replaced=1, unfulfilled=2))

    def test_geometry_membership_labels_and_loader_drift_fail_before_mutation(self):
        for change in ('shape', 'batch', 'membership', 'labels', 'identity', 'reset'):
            t=trainer(); cb=OHEMCallback(); cb.on_pretrain_routine_end(t)
            ds=t.train_loader.dataset
            if change=='shape': ds.batch_shapes[0]=[640,640]
            if change=='batch': ds.batch[0]=1
            if change=='membership': ds.im_files[0]='z'
            if change=='labels': ds.labels[0]['im_file']='z'
            if change=='identity': t.train_loader.dataset=copy.deepcopy(ds)
            if change=='reset': t.train_loader.reset=None
            before=copy.deepcopy(vars(t.train_loader.dataset))
            with self.assertRaises(ValueError): cb.on_train_epoch_end(t)
            self.assertEqual(vars(t.train_loader.dataset), before)

    def test_malformed_metadata_and_duplicate_originals(self):
        for shape in ([0,640], [float('nan'),640], [1.5,640], [640]):
            t=trainer();t.train_loader.dataset.batch_shapes[0]=shape
            with self.assertRaises(ValueError): OHEMCallback().on_pretrain_routine_end(t)
        t=trainer();t.train_loader.dataset.im_files[0]='b'
        with self.assertRaises(ValueError): OHEMCallback().on_pretrain_routine_end(t)
        ds=NS()
        with self.assertRaises(ValueError): sync_dataset_lists(ds,['a'],[])
        self.assertEqual(vars(ds),{})

    def test_rebuilt_loader_rejected_before_forward(self):
        t=trainer();cb=OHEMCallback();cb.on_pretrain_routine_end(t)
        t.train_loader.dataset=copy.deepcopy(t.train_loader.dataset)
        with self.assertRaisesRegex(ValueError,'rebuilt'): t.preprocess_batch({})

    def test_nonfinite_loss_rejected_missing_loss_not_invented(self):
        t=trainer();cb=OHEMCallback();cb.on_pretrain_routine_end(t)
        t.preprocess_batch({'im_file':['a']});cb.on_train_batch_end(t)
        self.assertEqual(dict(cb._epoch_loss),{})
        t.loss=NS(detach=lambda: NS(cpu=lambda: float('nan')))
        with self.assertRaises(ValueError): cb.on_train_batch_end(t)


class TimingTests(unittest.TestCase):
    def setUp(self):
        (ROOT/'.build/debug-output').mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'.build/debug-output')
        self.addCleanup(self.tmp.cleanup); self.d=Path(self.tmp.name)

    def test_clock_wrapping_partial_evidence_and_boundary(self):
        timer=TrainingTiming(ROOT, clock=iter([1,4,5,9]).__next__)
        self.assertEqual(timer.measured('ok',lambda: 7)(),7)
        with self.assertRaisesRegex(RuntimeError,'original'):
            timer.measured('bad',lambda: (_ for _ in ()).throw(RuntimeError('original')))()
        self.assertEqual(timer.stats['ok']['seconds'],3)
        self.assertEqual(timer.stats['bad'],dict(calls=1,seconds=4,errors=1))
        with self.assertRaisesRegex(ValueError,'inside project'):
            timer.setup(NS(save_dir=ROOT.parent))

    def test_real_entrypoint_with_fake_runtime_enabled_disabled_and_failure(self):
        for enabled, fail, no_ohem in ((False,False,False),(True,False,False),(True,True,False),(True,False,True)):
            callbacks={}; state={}
            class FakeModel:
                def __init__(self, weights): pass
                def add_callback(self,event,fn): callbacks.setdefault(event,[]).append(fn)
                def train(self,**kwargs):
                    state['kwargs']=kwargs
                    t=trainer();self.trainer=t
                    t.save_dir=Path(kwargs['project'])/kwargs['name'];t.save_dir.mkdir(parents=True)
                    t.device='mps';t.args=NS(workers=0);t.batch_size=2;t.epoch=0
                    t.last=t.save_dir/'absent.pt'
                    for name in ('optimizer_step','validate','save_model'):setattr(t,name,lambda: 7)
                    def event(name):
                        for fn in callbacks.get(name,[]):fn(t)
                    event('on_pretrain_routine_end'); event('on_train_epoch_start')
                    event('on_train_batch_start'); t.preprocess_batch({'im_file':['a','b']})
                    t.loss=NS(detach=lambda: NS(cpu=lambda: 4))
                    t.optimizer_step();event('on_train_batch_end')
                    if fail: raise RuntimeError('training failed')
                    event('on_train_epoch_end');t.validate();t.save_model();event('on_model_save')
                    event('on_fit_epoch_end');event('on_fit_epoch_end')
                    return 'fake-result'
            ultra=ModuleType('ultralytics');ultra.YOLO=FakeModel
            utils=ModuleType('ultralytics.utils');utils.SETTINGS={}
            run=f'run-{enabled}-{fail}-{no_ohem}'
            (self.d/'dataset.yaml').write_text('names: []\n')
            argv=['trainer','--dataset',str(self.d),'--output-dir',str(self.d),
                  '--name',run,'--initial-weights',str(self.d/'fake.pt')]+(['--timing'] if enabled else [])+(['--no-ohem'] if no_ohem else [])
            old=os.getcwd()
            try:
                with patch.dict('sys.modules',{'ultralytics':ultra,'ultralytics.utils':utils}), \
                     patch('sys.argv',argv), patch.object(entry,'WEIGHTS_DIR',self.d/'weights'), \
                     patch.object(entry,'os_env_defaults',{}):
                    if fail:
                        with self.assertRaisesRegex(RuntimeError,'training failed'):entry.main()
                    else:self.assertEqual(entry.main(),'fake-result')
            finally:os.chdir(old)
            self.assertEqual(state['kwargs']['device'],'mps')
            logs=list((self.d/run).glob('host-timing-*.jsonl'))
            self.assertEqual(len(logs),int(enabled))
            if enabled:
                records=[json.loads(line) for line in logs[0].read_text().splitlines()]
                self.assertEqual(records[0]['device_sync'],False)
                self.assertEqual(records[-1]['kind'],'terminal')
                self.assertEqual(records[-1]['outcome'],'failed' if fail else 'completed')
                self.assertEqual(sum(r['kind']=='epoch' for r in records),int(not fail))
                metrics=records[1]['intervals']
                for key in ('preprocess_batch','optimizer_step','batch_interval'):
                    self.assertEqual(metrics[key]['calls'],1)
                self.assertEqual('ohem_on_train_batch_end' in metrics,not no_ohem)
                if not fail:
                    for key in ('validate','save_model','checkpoint_mirror'):
                        self.assertEqual(metrics[key]['calls'],1)
                    self.assertEqual('ohem_on_train_epoch_end' in metrics,not no_ohem)

    def test_exact_intervals_and_final_eval_not_duplicate_epoch(self):
        timer=TrainingTiming(ROOT,clock=iter([0,2,5,8,12,20]).__next__)
        timer.path=self.d/'timing.jsonl';timer.path.touch()
        t=NS(epoch=0)
        timer.epoch_begin(t);timer.batch_begin(t);timer.batch_end(t)
        timer.batch_begin(t);timer.batch_end(t);timer.epoch_end(t)
        timer.epoch_end(t)
        rows=[json.loads(line) for line in timer.path.read_text().splitlines()]
        self.assertEqual(len(rows),1)
        stats=rows[0]['intervals']
        self.assertEqual(stats['epoch_total']['seconds'],20)
        self.assertEqual(stats['batch_interval']['seconds'],7)
        self.assertEqual(stats['inter_batch_gap']['seconds'],5)

    def test_terminal_io_failure_does_not_replace_training_error(self):
        timer=TrainingTiming(ROOT);timer.path=self.d/'missing'/'timing.jsonl'
        with self.assertWarns(RuntimeWarning): timer.terminal(NS(), 'failed')


if __name__=='__main__': unittest.main()
