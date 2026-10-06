import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import fullframe_replay_baseline as b


class BaselineTests(unittest.TestCase):
    def test_prepare_collision_and_changed_source(self):
        with patch.object(b,'OUT',Path(__file__).parent),patch.object(b.a,'sha') as digest:
            with self.assertRaises(ValueError):b.prepare()
            digest.assert_not_called()
        with patch.object(b.a,'sha',return_value='changed'),patch.object(b.a,'fresh'):
            with self.assertRaisesRegex(ValueError,'source_changed'):b.prepare()

    def test_timeout_preserved_no_retry(self):
        base=b.a.ROOT/'.build/debug-output';base.mkdir(parents=True,exist_ok=True)
        pre=dict(poolSHA256=b.POOL_PIN,inputContentSHA256='inputs',sourceSHA256='source')
        fake=SimpleNamespace(backends=SimpleNamespace(mps=SimpleNamespace(is_available=lambda:True)))
        def digest(path):return b.POOL_PIN if path==b.POOL else b.PIN if path==b.CHECKPOINT else 'source'
        with tempfile.TemporaryDirectory(dir=base) as directory,patch.object(b,'OUT',Path(directory)), \
             patch.object(b.a,'document',return_value=pre),patch.object(b.a,'sha',side_effect=digest), \
             patch.object(b.a.artifact,'load_request',return_value=SimpleNamespace(content_sha256='inputs')), \
             patch.dict('sys.modules',torch=fake), \
             patch.object(b.subprocess,'run',side_effect=subprocess.TimeoutExpired('test',300)) as launch:
            with self.assertRaises(subprocess.TimeoutExpired):b.infer()
            self.assertEqual(launch.call_count,1)
            self.assertTrue((b.OUT/'failure.json').exists())
            self.assertFalse((b.OUT/'report.json').exists())
            with self.assertRaisesRegex(ValueError,'output_collision'):b.infer()
            self.assertEqual(launch.call_count,1)


if __name__=='__main__':unittest.main()
