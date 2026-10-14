"""Test USB output guards without model training or external writes."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import usb_training386 as u


class USBTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=u.q.ROOT / '.build/debug-output')
        self.root = Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()
    def test_checked_copy(self):
        src=self.root/'a';src.write_bytes(b'model')
        dst=self.root/'b';u.copy_checked(src,dst)
        self.assertEqual(dst.read_bytes(),b'model')
        with self.assertRaisesRegex(ValueError,'usb_copy_input'):u.copy_checked(src,dst)
    def test_links_refused(self):
        src=self.root/'a';src.write_bytes(b'1');(self.root/'link').symlink_to(src)
        with self.assertRaisesRegex(ValueError,'usb_output_symlink'):u.bounded_bytes(self.root)
    def test_missing_volume(self):
        with patch.object(u,'VOLUME',self.root):
            with self.assertRaisesRegex(ValueError,'usb_unmounted'):u.verify_volume()
    def volume_check(self, **changes):
        import plistlib
        from collections import namedtuple
        Usage=namedtuple('Usage','total used free')
        info=dict(VolumeUUID=u.UUID,FilesystemType='apfs',Internal=False,
                  Writable=True,MountPoint=str(self.root))
        info.update(changes)
        with patch.object(u,'VOLUME',self.root),patch.object(u.q,'ROOT',self.root), \
             patch.object(Path,'is_mount',return_value=True), \
             patch.object(u.subprocess,'check_output',return_value=plistlib.dumps(info)), \
             patch.object(u,'bounded_bytes',return_value=0), \
             patch.object(u.shutil,'disk_usage',return_value=Usage(100*1024**3,0,100*1024**3)):
            return u.verify_volume()
    def test_project_can_use_verified_usb(self):
        self.assertEqual(self.volume_check(),self.root.stat().st_dev)
    def test_wrong_volume_identity(self):
        with self.assertRaisesRegex(ValueError,'usb_identity'):
            self.volume_check(VolumeUUID='wrong')
    def test_wrong_mountpoint(self):
        with self.assertRaisesRegex(ValueError,'usb_identity'):
            self.volume_check(MountPoint='/different-volume')
    def test_internal_volume_refused(self):
        with self.assertRaisesRegex(ValueError,'usb_identity'):
            self.volume_check(Internal=True)
    def test_budget_and_reserve(self):
        from collections import namedtuple
        Usage=namedtuple('Usage','total used free')
        with patch.object(Path,'is_mount',return_value=True),patch.object(u,'VOLUME',self.root),patch.object(u.shutil,'disk_usage',return_value=Usage(1000,100,900)):
            with patch.object(u,'bounded_bytes',return_value=u.TOTAL_LIMIT):
                with self.assertRaisesRegex(ValueError,'usb_local_limit'):u.check_budget(self.root,self.root,self.root.stat().st_dev)
            with patch.object(u,'bounded_bytes',return_value=0):
                with self.assertRaisesRegex(ValueError,'usb_disconnected'):u.check_budget(self.root,self.root,-1)
            with patch.object(u.shutil,'disk_usage',return_value=Usage(1000,900,100)):
                with self.assertRaisesRegex(ValueError,'usb_reserve'):u.check_budget(self.root,self.root,self.root.stat().st_dev)
    def test_adapter_keeps_small_verified_outputs(self):
        local=self.root/'test-job/attempts/1/out';local.mkdir(parents=True)
        u.q.save(local/'usb.json',dict(mode='crop',job='test-job',totalBytes=u.TOTAL_LIMIT,localBytes=u.LOCAL_LIMIT))
        u.q.save(local/'config.json',{'seed':371});u.q.save(local/'dependencies.json',[])
        def fake_train():
            out=u.hcf_factor_train376.OUT
            for name,value in [('fit.json',{'epochs':30}),('history.json',[{'epoch':1}])]:u.q.save(out/name,value)
            (out/'final.pt').write_bytes(b'new-model')
            u.q.save(out/'model.json',dict(path=str(out/'final.pt'),sha256=u.q.digest(out/'final.pt')))
        with patch.object(u,'OUT',local),patch.object(u,'BASE',self.root/'usb'),patch.object(u,'verify_volume',return_value=1),patch.object(u,'check_budget'),patch.object(u.hcf_factor_train376,'train',side_effect=fake_train):
            u.train()
            receipt=u.q.load(local/'usb-manifest.json')
            self.assertFalse(receipt['backup'])
            self.assertEqual((local/'final.pt').read_bytes(),b'new-model')
            self.assertTrue(Path(u.q.load(local/'model.json')['path']).is_file())
            with self.assertRaisesRegex(ValueError,'usb_attempt_collision'):u.train()

if __name__=='__main__':unittest.main()
