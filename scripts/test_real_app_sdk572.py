import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import real_app_sdk572 as sdk
import research_queue as q


class SDKMetadataTests(unittest.TestCase):
    def test_launch_identity_uses_bounded_console_protocol(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='sdk572-test-') as temp:
            p=subprocess.Popen([sys.executable,'-c','import json; print("REAL543_SDK " + json.dumps({"appID":"demo","runID":"run"}), flush=True)'],stdout=subprocess.PIPE)
            try:
                with (Path(temp)/'console.log').open('wb') as log:
                    self.assertEqual(sdk.identity(p,log,seconds=3)['appID'],'demo')
            finally:p.wait(timeout=5);p.stdout.close()

    def test_native_sample_identity_uses_its_own_prefix(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='sdk572-native-') as temp:
            p=subprocess.Popen([sys.executable,'-c','print(\'TTR_SAMPLE_READY {"appID":"native","runID":"run"}\', flush=True)'],stdout=subprocess.PIPE)
            try:
                with (Path(temp)/'console.log').open('wb') as log:
                    self.assertEqual(sdk.identity(p,log,seconds=3,prefix=b'TTR_SAMPLE_READY ')['appID'],'native')
            finally:p.wait(timeout=5);p.stdout.close()

    def test_helper_change_fails_before_external_call(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='sdk572-test-') as temp:
            helper=Path(temp)/'aatv';helper.write_text('changed')
            with patch.object(sdk.subprocess,'run') as run:
                with self.assertRaisesRegex(ValueError,'helper_changed'):
                    sdk.cli(dict(helper=str(helper),helperSHA256='0'*64),['status'],'read')
                run.assert_not_called()

    def test_unapproved_target_and_bundle_fail_before_installation(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='sdk572-test-') as temp:
            root=Path(temp);sdk.OUT=root/'job/attempts/1/out';sdk.OUT.mkdir(parents=True)
            config=root/'config.json'
            q.save(sdk.OUT.parents[2]/'spec.json',dict(template=dict(inputs=dict(configuration=dict(path=q.relative(config),sha256='0'*64)))))
            for target,bundle in [('other',next(iter(sdk.BUNDLES))),(sdk.TARGET,'com.apple.Preferences')]:
                with patch.object(sdk,'checked',return_value=config),patch.object(sdk.q,'load',side_effect=[dict(template=dict(inputs=dict(configuration={}))),dict(target=target,bundle=bundle)]),patch.object(sdk.subprocess,'run') as run:
                    with self.assertRaisesRegex(ValueError,'sdk572_scope'):sdk.run()
                    run.assert_not_called()


if __name__=='__main__':unittest.main()
