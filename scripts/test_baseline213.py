import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import baseline213 as b

class BaselineTests(unittest.TestCase):
    def setUp(self):
        root=b.a.ROOT/'.build/debug-output';root.mkdir(parents=True,exist_ok=True)
        self.work=Path(tempfile.mkdtemp(dir=root,prefix='baseline213-'))
    def tearDown(self):shutil.rmtree(self.work)
    def test_collision_before_input_work(self):
        with patch.object(b,'OUT',self.work),patch.object(b.a,'checked_requests') as check:
            with self.assertRaises(ValueError):b.run()
            check.assert_not_called()
    def test_changed_checkpoint_stops_before_inference(self):
        with patch.object(b,'OUT',self.work/'output'),patch.object(b.a,'checked_requests',return_value={}),patch.object(b.a,'sha',return_value='changed'),patch.object(b.subprocess,'run') as launch:
            with self.assertRaises(ValueError):b.run()
            launch.assert_not_called();self.assertFalse((self.work/'output').exists())
    def test_timeout_preserves_failure_without_retry(self):
        fake=SimpleNamespace(backends=SimpleNamespace(mps=SimpleNamespace(is_available=lambda:True)))
        with patch.object(b,'OUT',self.work/'output'),patch.object(b.a,'checked_requests',return_value={'native':SimpleNamespace(content_sha256='test-only')}),patch.object(b.a,'sha',return_value=b.PIN),patch.dict('sys.modules',torch=fake),patch.object(b.subprocess,'run',side_effect=subprocess.TimeoutExpired('test',120)) as launch:
            with self.assertRaises(subprocess.TimeoutExpired):b.run()
            self.assertEqual(launch.call_count,1)
            self.assertTrue((self.work/'output/failure.json').is_file())
            self.assertFalse((self.work/'output/report.json').exists())

if __name__=='__main__':unittest.main()
