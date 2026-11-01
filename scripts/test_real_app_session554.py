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


if __name__ == '__main__':
    unittest.main()
