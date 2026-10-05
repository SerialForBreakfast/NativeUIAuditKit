import copy
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
import numpy as np
import torch
import worker_candidate151 as w
from native_page150_audit import ink_bounds


class WorkerIntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=w.t.ROOT/'.build');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def archive(self,bad_hash=False,link=False,kind='cuda145'):
        data=b'data';manifest=dict(version='cuda145-worker-return-v1',request_id='nuiak-20261004-joe-big-dog-cuda145',
            files=[dict(path='model.pt',bytes=4,sha256=('0'*64 if bad_hash else hashlib.sha256(data).hexdigest()))])
        if kind=='robust153':
            manifest['version']='robust153-return-v1';manifest['request_id']='nuiak-20261004-worker-robust153'
            manifest['files'][0]['file']=manifest['files'][0].pop('path')
        raw=json.dumps(manifest).encode();p=self.root/'test.tar.gz'
        with tarfile.open(p,'w:gz') as tar:
            for name,value in [('manifest.json',raw),('model.pt',data)]:
                info=tarfile.TarInfo(name);info.size=len(value)
                if link and name=='model.pt':info.type=tarfile.SYMTYPE;info.linkname='/outside'
                tar.addfile(info,io.BytesIO(value))
        expected=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
            members=2,expanded_bytes=len(raw)+4,manifest_sha256=hashlib.sha256(raw).hexdigest())
        return p,expected

    def test_real_extraction_and_collision(self):
        p,e=self.archive();out=self.root/'out'
        self.assertTrue(w.extract(p,out,e)['allHashesVerified']);self.assertEqual((out/'model.pt').read_bytes(),b'data')
        with self.assertRaisesRegex(ValueError,'output_collision'):w.extract(p,out,e)

    def test_scoped_robust153_version(self):
        p,e=self.archive(kind='robust153');out=self.root/'out'
        with self.assertRaisesRegex(ValueError,'manifest_identity'):w.extract(p,out,e)
        self.assertFalse(out.exists())
        self.assertTrue(w.extract(p,out,e,'robust153')['allHashesVerified'])

    def test_bad_member_hash_before_output(self):
        p,e=self.archive(bad_hash=True);out=self.root/'out'
        with self.assertRaisesRegex(ValueError,'member_hash'):w.extract(p,out,e)
        self.assertFalse(out.exists())

    def test_link_rejected(self):
        p,e=self.archive(link=True)
        with self.assertRaises(ValueError):w.extract(p,self.root/'out',e)

    def test_wrong_manifest_and_size(self):
        p,e=self.archive();e['manifest_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'manifest_hash'):w.extract(p,self.root/'out',e)
        e['expanded_bytes']+=1
        with self.assertRaisesRegex(ValueError,'archive_scope'):w.extract(p,self.root/'out',e)

    def test_state_validation(self):
        net=torch.nn.Linear(2,1);cfg=dict(run_id='DTM044',epochs=600,selection='fixed-last',thresholds=dict(changed_min=.85,unchanged_max=.15))
        saved=dict(version='cuda145-checkpoint-v1',epoch=600,steps=21600,pins=dict(configuration=cfg),model=net.state_dict())
        self.assertIs(w.checked_state(torch,net,saved,'DTM044',dict(configuration=cfg)),net)
        bad=copy.deepcopy(saved);bad['model']['weight'][0,0]=float('nan')
        with self.assertRaisesRegex(ValueError,'checkpoint_tensor'):w.checked_state(torch,net,bad,'DTM044',dict(configuration=cfg))
        bad=copy.deepcopy(saved);bad['epoch']=599
        with self.assertRaisesRegex(ValueError,'completion'):w.checked_state(torch,net,bad,'DTM044',dict(configuration=cfg))

    def test_scores_keep_abstentions_separate(self):
        self.assertEqual(w.summary([.9,.1,.5,.9,.1],[1,0,1,0,1]),dict(count=5,correct=2,falseChange=1,missedChange=1,abstentions=1))
        with self.assertRaises(ValueError):w.summary([float('nan')],[1])

    def test_probe_measurement(self):
        im=np.full((20,30,3),255,np.uint8);im[4:8,5:19]=0
        self.assertEqual(ink_bounds(im,False),[5,4,14,4])
        self.assertEqual(ink_bounds(255-im,True),[5,4,14,4])
        with self.assertRaisesRegex(ValueError,'empty'):ink_bounds(np.zeros_like(im),True)


if __name__=='__main__':unittest.main()
