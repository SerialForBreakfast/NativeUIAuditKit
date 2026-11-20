import json
import subprocess
import unittest
from unittest import mock
import real_app_session554 as s


def line(scene, reasons, timestamp='2026-11-01 10:00:00.000000-0700'):
    return json.dumps(dict(timestamp=timestamp, eventMessage=f"[{scene}] Setting deactivation reasons to: '{reasons}' for reason: test."))


FINISHED = '{"count":2,"finished":1}'


class AlertCheckTests(unittest.TestCase):
    def test_latest_reason_per_scene_wins(self):
        latest = s.deactivation([line('app-default', 'systemModalAlert'), line('app-default', '(none)', '2026-11-01 10:00:01'), FINISHED])
        self.assertEqual(latest['app-default']['reasons'], [])
        self.assertEqual(s.alert_state(latest)['status'], 'clear')

    def test_alert_present(self):
        latest = s.deactivation([line('app-default', 'systemAnimation, systemModalAlert'), line('other', 'occluded'), FINISHED])
        state = s.alert_state(latest)
        self.assertEqual(state['status'], 'alert')
        self.assertEqual(state['alertScenes'], ['app-default'])

    def test_alert_absent(self):
        self.assertEqual(s.alert_state(s.deactivation([line('app-default', 'occluded'), FINISHED]))['status'], 'clear')

    def test_unrelated_lines_ignored(self):
        self.assertEqual(s.deactivation(['Filtering the log data', json.dumps(dict(eventMessage='Now tracking: x')), FINISHED]), {})

    def test_log_unavailable_is_not_clear(self):
        failed = subprocess.CompletedProcess([], 1, '', 'error')
        with mock.patch.object(s.subprocess, 'run', return_value=failed):
            result = s.alert_check('62DA0048-BB6A-4726-9CCC-F842DF7BE985')
        self.assertEqual(result['status'], 'unavailable')

    def test_truncated_log_is_not_clear(self):
        partial = subprocess.CompletedProcess([], 0, line('app-default', '(none)')+'\n', '')
        with mock.patch.object(s.subprocess, 'run', return_value=partial):
            self.assertEqual(s.alert_check('62DA0048-BB6A-4726-9CCC-F842DF7BE985')['status'], 'unavailable')

    def test_capture_case_flags_transitional_drift_and_focus_known(self):
        import tempfile
        from pathlib import Path
        from PIL import Image
        with tempfile.TemporaryDirectory(dir=s.q.ROOT / '.build', prefix='sess554-') as tmp:
            root = Path(tmp)
            out = root / 'out'
            out.mkdir()
            plan = dict(settleSeconds=0.0, udid='SIM-UDID', bundle='com.example.App')
            case = dict(id='c0', flow='f1', group='g1', expectedScreen='home', inputs=[], expectedSDK=['b0'])
            launched = dict(identity=dict(endpoint='127.0.0.1:1'), enrollment='tok', lines=[])
            base_sdk = dict(
                returnCode=0, success=True, state='active', focusKnown=True, focusID='b0', generation=1,
                truncated=False, captureGeometry=dict(displayScale=2.0, screenBounds=dict(width=1920, height=1080)),
                layout=dict(actualFocusKnown=True, actualFocus='b0'), accessibilityDrafts=None, issues=[],
                elements=[('b0', '{"height": 40, "width": 100, "x": 10, "y": 10}', False)],
                richElements=[dict(id='b0', role='primaryButton', bounds=dict(x=10, y=10, width=100, height=40), hidden=False, focused=True)],
                file='c0.stdout',
            )
            drift_sdk = dict(base_sdk, focusID='b1', generation=2)

            def fake_shot(cmd, **kw):
                Image.new('RGB', (3840, 2160), (0, 0, 0)).save(cmd[-1])
                return subprocess.CompletedProcess(cmd, 0, '', '')

            with mock.patch.object(s, 'LOCAL', root / 'local'), \
                 mock.patch.object(s, 'DATA', root / 'data'), \
                 mock.patch.object(s.subprocess, 'run', side_effect=fake_shot), \
                 mock.patch.object(s, 'alert_check', return_value=dict(status='clear', scenes={'com.example.App-default': dict(reasons=[])})), \
                 mock.patch.object(s, 'sdk_rows', side_effect=[base_sdk, drift_sdk]):
                rec_drift = s.capture_case(plan, launched, out, case, '2026-11-11 00:00:00')
            self.assertEqual(rec_drift['status'], 'transitional')
            self.assertTrue(rec_drift['transitional'])

            no_focus_sdk = dict(base_sdk, focusID=None, richElements=[dict(id='b0', role='primaryButton', bounds=dict(x=10, y=10, width=100, height=40), hidden=False, focused=False)])
            with mock.patch.object(s, 'LOCAL', root / 'local'), \
                 mock.patch.object(s, 'DATA', root / 'data'), \
                 mock.patch.object(s.subprocess, 'run', side_effect=fake_shot), \
                 mock.patch.object(s, 'alert_check', return_value=dict(status='clear', scenes={'com.example.App-default': dict(reasons=[])})), \
                 mock.patch.object(s, 'sdk_rows', side_effect=[no_focus_sdk, dict(no_focus_sdk)]):
                rec_nofocus = s.capture_case(plan, launched, out, case, '2026-11-11 00:00:00')
            self.assertEqual(rec_nofocus['status'], 'captured')
            self.assertTrue(rec_nofocus['focusKnown'])
            self.assertEqual(rec_nofocus['focus'], 'no_focus')
            self.assertIsNone(rec_nofocus['focusID'])


if __name__ == '__main__':
    unittest.main()
