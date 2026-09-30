"""Offline supervisor/input guards; never import Torch or execute training."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch
from PIL import Image
import mps_training_diagnostic as d


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=d.ROOT/'.build/debug-output')
        self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)

    def test_pixels_labels_and_changed_hash(self):
        image=self.root/'a.png';label=self.root/'a.txt'
        Image.new('RGB',(10,20),'red').save(image)
        label.write_text('0 0.5 0.5 0.2 0.2\n')
        record=d.pin(image);self.assertEqual(d.verified(record),image)
        self.assertEqual(len(d.validate_member(image,label,41)),64)
        for text in ('42 .5 .5 .2 .2','0 .5 .5 nan .2','0 .5 .5 0 .2','1.5 .5 .5 .2 .2','0 1.1 .5 .2 .2'):
            label.write_text(text)
            with self.assertRaises(ValueError):d.validate_member(image,label,41)
        image.write_bytes(b'corrupt')
        with self.assertRaises(ValueError):d.verified(record)
        with self.assertRaises(Exception):d.validate_member(image,label,41)

    def test_limits(self):
        good=dict(available_bytes=9*2**30,free_disk_bytes=11*2**30)
        self.assertIsNone(d.resource_block(good))
        self.assertEqual(d.resource_block(dict(good,available_bytes=7*2**30)),'insufficient_available_memory')
        self.assertIsNone(d.resource_block(dict(good,available_bytes=7*2**30),False))
        self.assertEqual(d.resource_block(dict(good,available_bytes=2*2**30),False),'insufficient_available_memory')
        self.assertEqual(d.resource_block(dict(good,free_disk_bytes=9*2**30)),'insufficient_disk')
        self.assertEqual(d.resource_block(good,size=3*2**30),'output_budget_exceeded')

    def test_blocked_preflight_never_spawns_or_stages(self):
        out=self.root/'run';low=dict(available_bytes=1,total_bytes=24*2**30,free_disk_bytes=50*2**30)
        with patch.object(d,'load_plan',return_value={}),patch.object(d,'resources',return_value=low), \
             patch.object(d,'stage') as stage,patch.object(d,'supervise') as run:
            result=d.execute(self.root/'unused','hash',out)
        self.assertEqual(result['outcome'],'blocked');stage.assert_not_called();run.assert_not_called()
        self.assertFalse(json.loads((out/'preflight.json').read_text())['model_loaded'])
        with self.assertRaisesRegex(ValueError,'collision'):d.execute('unused','hash',out)

    def test_owned_child_success_and_failure(self):
        good=lambda _:dict(available_bytes=9*2**30,free_disk_bytes=20*2**30)
        for exitcode in (0,3):
            out=self.root/str(exitcode);out.mkdir()
            result=d.supervise([sys.executable,'-c',f'raise SystemExit({exitcode})'],out,dict(os.environ),sample=good)
            self.assertEqual(result['returncode'],exitcode)
            self.assertEqual(result['outcome'],'completed' if exitcode==0 else 'failed')

    def test_deadline_terminates_only_owned_child(self):
        now=iter([0,1801,1802,1803]).__next__
        result=d.supervise([sys.executable,'-c','import time;time.sleep(30)'],self.root,dict(os.environ),clock=now,
             sample=lambda _:dict(available_bytes=9*2**30,free_disk_bytes=20*2**30))
        self.assertEqual(result['reason'],'deadline_exceeded')
        self.assertNotEqual(result['returncode'],0)

    def test_resource_sampler_failure_also_stops_owned_child(self):
        def fail(_):raise OSError('unavailable')
        result=d.supervise([sys.executable,'-c','import time;time.sleep(30)'],self.root,dict(os.environ),sample=fail)
        self.assertEqual(result['reason'],'supervisor_error: OSError')
        self.assertNotEqual(result['returncode'],0)

    def test_plan_seal_and_boundary(self):
        p=self.root/'plan.json';p.write_text('{}')
        with self.assertRaisesRegex(ValueError,'changed_plan'):d.load_plan(p,'bad')
        with self.assertRaisesRegex(ValueError,'incompatible_plan'):d.load_plan(p,d.digest(p))
        with self.assertRaisesRegex(ValueError,'outside_project'):d.local(d.ROOT.parent/'outside')

    def test_actual_stage_and_worker_entrypoint_with_fake_model_runtime(self):
        import yaml
        image=self.root/'a.png';label=self.root/'a.txt';taxonomy=self.root/'original.yaml'
        Image.new('RGB',(10,10),'blue').save(image);label.write_text('0 .5 .5 .1 .1')
        taxonomy.write_text(yaml.safe_dump(dict(names={i:str(i) for i in range(41)})))
        weights=self.root/'fake.pt';weights.write_bytes(b'not a model')
        row=dict(split='train',image=d.pin(image),label=d.pin(label))
        plan=dict(members=[row],taxonomy=d.pin(taxonomy),weights=d.pin(weights),settings=dict(batch=8))
        before={p:d.digest(p) for p in (image,label,taxonomy,weights)}
        output=self.root/'run';output.mkdir()
        staged=d.stage(plan,output)
        self.assertEqual(d.digest(staged/'train/images/0000.png'),d.digest(image))
        self.assertFalse((staged/'test').exists())
        d.write(output/'preflight.json',{})
        fake=torch=NS(backends=NS(mps=NS(is_available=lambda:True)))
        captured=[]
        module=NS(main=lambda:captured.append(list(sys.argv)))
        good=dict(available_bytes=10*2**30,free_disk_bytes=20*2**30)
        with patch.object(d,'load_plan',return_value=plan),patch.object(d,'resources',return_value=good), \
             patch.dict(sys.modules,{'torch':fake,'train_ios_model':module}),patch.object(sys,'addaudithook'), \
             patch.object(sys,'argv',[]):
            d.worker(self.root/'plan','hash',output)
            self.assertEqual(captured[0][captured[0].index('--epochs')+1],'2')
            self.assertEqual(captured[0][captured[0].index('--batch')+1],'8')
            self.assertIn('--timing',captured[0]);self.assertNotIn('--resume',captured[0])
            plan['settings']['batch']=16
            d.worker(self.root/'plan','hash',output)
            self.assertEqual(captured[1][captured[1].index('--batch')+1],'16')
            (staged/'train/labels/0000.txt').write_text('changed')
            with self.assertRaisesRegex(ValueError,'changed_staged_member'):d.worker('plan','hash',output)
        self.assertEqual({p:d.digest(p) for p in before},before)

    def test_protected_and_duplicate_plan_members_rejected(self):
        base=dict(schema='mps-host-diagnostic-v1',limits=d.LIMITS,
                  settings=dict(device='mps',batch=8,imgsz=640,epochs=2,workers=0,seed=42),quality_eligible=False)
        rows=[dict(split='train' if i<512 else 'val',image=dict(path=str(i))) for i in range(576)]
        for kind in ('protected','duplicate'):
            plan=dict(base,members=json.loads(json.dumps(rows)))
            if kind=='protected':plan['members'][-1]['split']='test'
            else:plan['members'][-1]['image']['path']='0'
            path=self.root/(kind+'.json');d.write(path,plan)
            with self.assertRaisesRegex(ValueError,'protected|duplicate'):d.load_plan(path,d.digest(path))


if __name__=='__main__':unittest.main()
