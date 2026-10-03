import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from PIL import Image
import train_fullscreen_focus as f


class RunnerTests(unittest.TestCase):
    def setUp(self):
        base=f.h.ROOT/'.build/debug-output';base.mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(prefix='bounded-focus-',dir=base))
        frames=[]
        for i,split in enumerate(('train','development')):
            image=self.root/f'{i}.png';Image.new('RGB',(20,10),('black','white')[i]).save(image)
            ann=self.root/f'{i}.json';f.h.write(ann,dict(version='fullscreen-focus-annotation-v1',
                image=f.h.ref(image),completeFocus=True,profile='ordinary',
                controls=[dict(id='target',bounds=[2,2,10,5],state='focused')]))
            frames.append(dict(id=str(i),split=split,group='family-'+str(i),image=f.h.ref(image),annotation=f.h.ref(ann)))
        weights=self.root/'model.pt';weights.write_bytes(b'unit-test-only checkpoint')
        self.doc=dict(version='fullscreen-focus-run-v1',frames=frames,checkpoint=f.h.ref(weights),
            budget=dict(seconds=2,bytes=128*1024*1024),epochs=1,batch=1,imgsz=640,seed=42,runtime=f.runtime_identity())
        self.refresh()

    def refresh(self):
        admission=self.root/'admission.json'
        admission.write_text(json.dumps(dict(version='fullscreen-focus-admission-v1',approved=True,
            purpose='full-screen-focus-training',approvedBy='unit test, not real admission',
            membershipSHA256=f.h.digest(self.doc['frames']))))
        self.doc['admission']=f.h.ref(admission)
        self.contract=self.root/'contract.json';self.contract.write_text(json.dumps(self.doc))

    def tearDown(self):shutil.rmtree(self.root)

    def test_validation_and_staging(self):
        doc,checked=f.validate(self.contract);out=self.root/'stage';out.mkdir();f.stage(doc,checked,out)
        self.assertEqual((out/'dataset/train/labels/000000.txt').read_text(),'0 0.350000000 0.450000000 0.500000000 0.500000000\n')
        self.assertEqual(json.loads((out/'dataset.yaml').read_text())['names'],['focusedControl'])

    def test_validation_cli_does_not_train_or_write(self):
        before=set(self.root.rglob('*'))
        p=subprocess.run([sys.executable,f.__file__,'--contract',str(self.contract)],capture_output=True,text=True,
            env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},timeout=10)
        self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads(p.stdout)['mode'],'validation-only')
        self.assertEqual(before,set(self.root.rglob('*')))

    def test_group_overlap_rejected(self):
        self.doc['frames'][1]['group']=self.doc['frames'][0]['group'];self.refresh()
        with self.assertRaisesRegex(ValueError,'cross_split_source_group'):f.validate(self.contract)

    def test_pixel_duplicates_rejected(self):
        second=self.doc['frames'][1];first=self.doc['frames'][0]
        second['image']=first['image'];second['annotation']=first['annotation'];self.refresh()
        with self.assertRaisesRegex(ValueError,'cross_split_pixel_duplicate'):f.validate(self.contract)

    def test_admission_and_missing_local_weights(self):
        self.doc['frames'][0]['group']='changed';self.contract.write_text(json.dumps(self.doc))
        with self.assertRaisesRegex(ValueError,'membership_not_admitted'):f.validate(self.contract)
        self.refresh();(self.root/'model.pt').unlink()
        with self.assertRaises(ValueError):f.validate(self.contract)

    def test_incomplete_and_unknown_labels(self):
        ann=self.root/'0.json';value=json.loads(ann.read_text());value['completeFocus']=False
        ann.write_text(json.dumps(value));self.doc['frames'][0]['annotation']=f.h.ref(ann);self.refresh()
        with self.assertRaisesRegex(ValueError,'incomplete_or_assisted'):f.validate(self.contract)
        value['completeFocus']=True;value['controls'][0]['state']='unknown';ann.write_text(json.dumps(value))
        self.doc['frames'][0]['annotation']=f.h.ref(ann);self.refresh()
        with self.assertRaisesRegex(ValueError,'unknown_focus'):f.validate(self.contract)

    def launch(self,code,seconds=2,limit=1024*1024):
        out=self.root/('child-'+str(len(list(self.root.glob('child-*')))));out.mkdir()
        return f.supervise([sys.executable,'-c',code],out,seconds,limit)

    def test_success_and_child_error(self):
        self.assertEqual(self.launch('print("ok")')['outcome'],'completed')
        self.assertEqual(self.launch('raise RuntimeError("test")')['outcome'],'child_failed')

    def test_timeout_stops_owned_process(self):
        r=self.launch('import time; time.sleep(5)',seconds=.1)
        self.assertEqual(r['outcome'],'wall_time_limit');self.assertLess(r['wallSeconds'],3)

    def test_size_limit_retains_artifact(self):
        r=self.launch('print("x"*20000)',limit=1000)
        self.assertEqual(r['outcome'],'output_limit');self.assertGreater(r['outputOvershootBytes'],0)

    def test_direct_child_rejected(self):
        p=subprocess.run([sys.executable,f.__file__,'--child',str(self.root)],capture_output=True,text=True,
            env={k:v for k,v in os.environ.items() if k!='NUIAK_SUPERVISOR_PID'},timeout=10)
        self.assertNotEqual(p.returncode,0);self.assertIn('supervised_child_required',p.stderr)

    def test_child_wires_validated_membership_to_shared_recipe(self):
        doc,checked=f.validate(self.contract);out=self.root/'stage';out.mkdir();f.stage(doc,checked,out)
        code='''import sys,types,json
import train_fullscreen_focus as f
class Model:
 def __init__(self,path): self.path=path
 def train(self,**kwargs): print(json.dumps(kwargs))
sys.modules['ultralytics']=types.SimpleNamespace(YOLO=Model)
f.child(f.h.local(sys.argv[1]))
'''
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(f.h.ROOT/'scripts'),
             'NUIAK_SUPERVISOR_PID':str(os.getpid())}
        for k in ('YOLO_CONFIG_DIR','MPLCONFIGDIR','TORCH_HOME'):env[k]=str(self.root/k)
        p=subprocess.run([sys.executable,'-c',code,str(out)],capture_output=True,text=True,env=env,timeout=10)
        self.assertEqual(p.returncode,0,p.stderr);v=json.loads(p.stdout)
        self.assertEqual(v['data'],str(out/'dataset.yaml'));self.assertEqual(v['workers'],0)
        self.assertFalse(v['plots']);self.assertEqual(v['hsv_v'],0);self.assertFalse(v['resume'])

    def test_runtime_change_rejected(self):
        self.doc['runtime']={};self.refresh()
        with self.assertRaisesRegex(ValueError,'runtime_identity_changed'):f.validate(self.contract)

    def test_shared_recipe_preserves_old_defaults(self):
        from train_tvos_model import training_options
        from types import SimpleNamespace
        a=SimpleNamespace(dry_run=False,epochs=100,batch=8,imgsz=640,patience=15,workers=4,output_dir='local',name='test')
        r=training_options(a,'dataset.yaml')
        self.assertEqual((r['epochs'],r['warmup_epochs'],r['mosaic'],r['device']),(100,3,1,'mps'))
        a.dry_run=True;r=training_options(a,'dataset.yaml')
        self.assertEqual((r['epochs'],r['fraction'],r['warmup_epochs'],r['name']),(2,.05,0,'test_dryrun'))


if __name__=='__main__':unittest.main()
