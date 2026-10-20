import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import research_queue as q
from experiment_templates import pin
import retention_recovery461 as worker


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=q.ROOT/'.build')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.out = self.root/'attempts/1/out'; self.out.mkdir(parents=True)
        (self.out/'image.png').write_bytes(b'original')
        digest = q.digest(self.out/'image.png')
        q.save(self.out/'capture.json', dict(complete=True, cleanup=True, frames=[dict(path='image.png',sha256=digest)]))
        q.save(self.out/'artifact.json',pin(self.out/'capture.json'))
        q.save(self.out/'capture-evidence.json',dict(cleanup=True,images=[dict(path='image.png',sha256=digest)]))
        q.save(self.out/'template-result.json',dict(execution='failed',code='compaction_input_budget'))
        q.save(self.root/'spec.json',dict(id='failed-capture'))
        self.plan=dict(spec=pin(self.root/'spec.json'))
        self.seal()

    def seal(self):
        q.save(self.out.parent/'result.json',dict(status='failed',reason='process_failed',job='failed-capture',
            specSHA256=q.text_digest(q.load(self.root/'spec.json')), outputs=[dict(path=p.name,bytes=p.stat().st_size,sha256=q.digest(p)) for p in self.out.iterdir()]), replace=True)
        self.plan['result']=pin(self.out.parent/'result.json')

    def test_completed_capture_is_reusable(self):
        source,evidence=worker.verify(self.plan)
        self.assertEqual(source,self.out);self.assertTrue(evidence['cleanup'])

    def test_changed_image_is_rejected(self):
        (self.out/'image.png').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'output_changed'):worker.verify(self.plan)

    def test_capture_failure_is_not_retention_failure(self):
        q.save(self.out/'template-result.json',dict(execution='failed',code='capture_timeout'), replace=True);self.seal()
        with self.assertRaisesRegex(ValueError,'failure_cause'):worker.verify(self.plan)

    def test_missing_cleanup_is_rejected(self):
        q.save(self.out/'capture-evidence.json',dict(cleanup=False,images=[]), replace=True);self.seal()
        with self.assertRaisesRegex(ValueError,'retention_cleanup'):worker.verify(self.plan)

    def test_retention_failure_never_publishes_capture(self):
        new=self.root/'new/attempts/1/out';new.mkdir(parents=True)
        q.save(self.root/'plan.json',self.plan)
        q.save(new.parents[2]/'spec.json',dict(retentionRecovery=pin(self.root/'plan.json')))
        worker.OUT=new
        with patch.object(worker.storage,'local_compact',side_effect=ValueError('busy')):
            with self.assertRaisesRegex(ValueError,'busy'):worker.run()
        self.assertFalse((new/'artifact.json').exists())

    def test_retention_success_copies_exact_evidence(self):
        new=self.root/'new/attempts/1/out';new.mkdir(parents=True)
        q.save(self.root/'plan.json',self.plan)
        q.save(new.parents[2]/'spec.json',dict(retentionRecovery=pin(self.root/'plan.json')))
        worker.OUT=new
        with patch.object(worker.storage,'local_compact') as retain:worker.run()
        retain.assert_called_once()
        self.assertEqual((new/'image.png').read_bytes(),b'original')
        self.assertFalse(q.load(new/'recovery.json')['captureRepeated'])

if __name__=='__main__':unittest.main()
