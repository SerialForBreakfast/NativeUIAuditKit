"""Startup failures never reach annotation loading or QApplication in the parent."""
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import human_review_startup as s
import human_review_editor as editor


class StartupTests(unittest.TestCase):
    def setUp(self):
        parent=s.ROOT/'.build/review-startup-tests';parent.mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(dir=parent))
    def tearDown(self):shutil.rmtree(self.root)

    def fake_result(self,receipt,code):
        def run(command,**kwargs):
            self.assertEqual(command[0],sys.executable)
            self.assertEqual(kwargs['timeout'],20)
            self.assertEqual(kwargs['cwd'],s.ROOT)
            kwargs['stdout'].write(s.PREFIX+json.dumps(receipt)+'\n');kwargs['stdout'].flush()
            return SimpleNamespace(returncode=code)
        return run

    def test_success_checked_each_time_and_receipts_preserved(self):
        with patch.object(s.subprocess,'run',side_effect=self.fake_result(dict(version=s.VERSION,passed=True,platform='cocoa'),0)) as run:
            a=s.preflight(self.root);b=s.preflight(self.root)
        self.assertEqual(run.call_count,2);self.assertNotEqual(a['receipt'],b['receipt'])
        self.assertTrue(a['passed']);self.assertEqual(json.loads(Path(a['receipt']).read_text()),a)

    def test_abort_malformed_and_inconsistent_child_fail_closed(self):
        for receipt,code in [(dict(version=s.VERSION,passed=True),-6),([],0),({},0),(dict(version=s.VERSION,passed=False),0)]:
            with self.subTest(receipt=receipt,code=code),patch.object(s.subprocess,'run',side_effect=self.fake_result(receipt,code)):
                result=s.preflight(self.root)
            self.assertFalse(result['passed']);self.assertTrue(Path(result['stderr']).is_file())

    def test_timeout_and_spawn_error_recorded_without_retry(self):
        for exc,category in [(subprocess.TimeoutExpired('probe',20),'timeout'),(OSError('unavailable'),'spawn')]:
            with self.subTest(category=category),patch.object(s.subprocess,'run',side_effect=exc) as run:
                result=s.preflight(self.root)
            self.assertEqual(run.call_count,1);self.assertEqual(result['category'],category);self.assertFalse(result['passed'])

    def test_failed_normal_launch_never_loads_review_or_qt(self):
        failure=dict(passed=False,receipt='generated receipt')
        with patch.object(sys,'argv',['editor','unread-batch.json','--runtime',str(self.root)]),\
             patch.object(s,'preflight',return_value=failure),\
             patch.object(editor,'configure',side_effect=AssertionError('must not import Qt')),\
             patch.object(editor,'window',side_effect=AssertionError('must not load review')),\
             redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
            self.assertEqual(editor.main(),2)

    def test_doctor_without_batch_never_opens_annotation(self):
        with patch.object(sys,'argv',['editor','--doctor','--runtime',str(self.root)]),\
             patch.object(s,'preflight',return_value=dict(passed=True)),\
             patch.object(editor,'window',side_effect=AssertionError('must not open editor')),redirect_stdout(io.StringIO()):
            self.assertEqual(editor.main(),0)

    def test_doctor_rejects_annotation_arguments_before_probe(self):
        with patch.object(sys,'argv',['editor','--doctor','a-batch']),patch.object(s,'preflight') as probe,redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):editor.main()
        probe.assert_not_called()

    def test_failure_categories_are_actionable(self):
        for message,expected in [('Library not loaded: @rpath/QtDBus','framework_lookup'),
                                 ('unsupported_explicit_qt_platform:bad','platform_configuration'),
                                 ('changed_qt_plugin_cache','cache_integrity'),
                                 ('unsupported_editor_version','environment'),('unknown error','qt_initialization')]:
            category,action=s.diagnose(message);self.assertEqual(category,expected);self.assertTrue(action)


if __name__=='__main__':unittest.main()
