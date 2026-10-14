"""Test native adapter dispatch and failures with explicit stubs. No device or training claims."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import research_queue as q
import template_bridge395 as bridge
from experiment_templates import pin


class NativeBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='native-template395-')
        self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)

    def prepare(self,ident,inputs=None):
        out=self.root/ident/'attempts/1/out';out.mkdir(parents=True)
        q.save(out.parents[2]/'spec.json',dict(template=dict(id=ident,inputs=inputs or {},parameters={})))
        q.save(out/'dependencies.json',[])
        return out

    def test_admission_dispatch_positive_and_failure(self):
        import hcf_study371
        out=self.prepare('T04')
        with patch.object(bridge,'OUT',out),patch.object(hcf_study371,'admit') as operation:
            bridge.native();operation.assert_called_once()
        self.assertEqual(q.load(out/'template-result.json')['execution'],'complete')
        failed=self.prepare('T04-failure')
        q.save(failed.parents[2]/'spec.json',dict(template=dict(id='T04',inputs={},parameters={})),replace=True)
        with patch.object(bridge,'OUT',failed),patch.object(hcf_study371,'admit',side_effect=ValueError('observed_focus_missing')):
            with self.assertRaisesRegex(ValueError,'observed_focus_missing'):bridge.native()
        self.assertEqual(q.load(failed/'template-result.json')['execution'],'failed')

    def test_crop_dispatch_positive_and_failure(self):
        import hcf_study371
        out=self.prepare('T05')
        with patch.object(bridge,'OUT',out),patch.object(hcf_study371,'prepare_crops') as operation:
            bridge.native();operation.assert_called_once()
        failed=self.prepare('T05-failure')
        q.save(failed.parents[2]/'spec.json',dict(template=dict(id='T05',inputs={},parameters={})),replace=True)
        with patch.object(bridge,'OUT',failed),patch.object(hcf_study371,'prepare_crops',side_effect=ValueError('crop_source_changed')):
            with self.assertRaisesRegex(ValueError,'crop_source_changed'):bridge.native()

    def test_training_dispatch_and_membership_failure(self):
        import hcf_study371,hcf_factor_train376
        membership=dict(rows=[dict(id='software-test',role='train',label=1)])
        path=self.root/'membership.json';q.save(path,membership)
        out=self.prepare('T06',dict(membership=pin(path)))
        with patch.object(bridge,'OUT',out),patch.object(hcf_study371,'dependency',return_value=[membership]),patch.object(hcf_factor_train376,'train') as operation:
            bridge.native();operation.assert_called_once()
        failed=self.prepare('T06-failure',dict(membership=pin(path)))
        q.save(failed.parents[2]/'spec.json',dict(template=dict(id='T06',inputs=dict(membership=pin(path)),parameters={})),replace=True)
        with patch.object(bridge,'OUT',failed),patch.object(hcf_study371,'dependency',return_value=[dict(rows=[])]),patch.object(hcf_factor_train376,'train') as operation:
            with self.assertRaisesRegex(ValueError,'membership_mismatch'):bridge.native()
            operation.assert_not_called()

    def capture(self,out,cleanup):
        from PIL import Image
        source=out/'source';source.mkdir()
        image=source/'frame.png';Image.new('RGB',(8,8)).save(image)
        receipt=source/'capture.json';q.save(receipt,dict(complete=True,cleanup=cleanup,frames=[dict(path='frame.png',sha256=q.digest(image))]))
        q.save(out/'artifact.json',dict(path=str(receipt),sha256=q.digest(receipt)))

    def test_capture_positive_and_cleanup_failure(self):
        import generation352
        out=self.prepare('T03')
        with patch.object(bridge,'OUT',out),patch.object(generation352,'run',side_effect=lambda:self.capture(out,True)):
            bridge.capture()
        self.assertEqual(len(q.load(out/'capture-evidence.json')['images']),1)
        failed=self.prepare('T03-failure')
        with patch.object(bridge,'OUT',failed),patch.object(generation352,'run',side_effect=lambda:self.capture(failed,False)):
            with self.assertRaisesRegex(ValueError,'capture_incomplete'):bridge.capture()
        self.assertFalse((failed/'capture-evidence.json').exists())


if __name__=='__main__':unittest.main()
