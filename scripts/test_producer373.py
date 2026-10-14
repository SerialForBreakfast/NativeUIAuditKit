"""Check offline planning receipts without contacting TTR."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import producer373 as p
import research_queue as q


class ProducerTests(unittest.TestCase):
    def test_plan_failure_is_not_capture_or_admission(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='test-plan373-') as folder:
            out=Path(folder);(out/'inputs').mkdir();request=out/'inputs/request.json';helper=Path(__file__)
            q.save(request,dict(source_role='calibration',target={'simulator_udid':'original'}))
            q.save(out/'config.json',dict(helperSHA256=q.digest(helper),requests=[dict(path=q.relative(request),sha256=q.digest(request))]))
            def run(args,stdout,stderr,timeout):
                self.assertIn('plan',args);self.assertNotIn('generate',args)
                self.assertEqual(json.loads(args[-1])['target']['simulator_udid'],'original')
                stdout.write(json.dumps({'success':False,'error':'unsupported'}))
                return type('Result',(),{'returncode':1})()
            with patch.object(p,'OUT',out),patch.object(p,'CLI',helper),patch.object(p.subprocess,'run',side_effect=run):p.run()
            report=q.load(out/'summary.json')
            self.assertEqual(report['accepted'],0)
            self.assertFalse(report['captureStarted'])
            self.assertFalse(report['trainingAdmitted'])

    def test_helper_hash_change_fails_before_call(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='test-plan373-') as folder:
            out=Path(folder);q.save(out/'config.json',dict(helperSHA256='0'*64,requests=[]))
            with patch.object(p,'OUT',out),patch.object(p,'CLI',Path(__file__)),patch.object(p.subprocess,'run') as run:
                with self.assertRaisesRegex(ValueError,'helper_changed'):p.run()
                run.assert_not_called()
