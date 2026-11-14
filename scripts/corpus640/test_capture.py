"""Test capture preflight without operating a Simulator."""
import json
from unittest import TestCase,main
from unittest.mock import Mock,patch
import capture

class PreflightTests(TestCase):
    def test_paths_stay_inside_project(self):
        with self.assertRaises(ValueError):capture.inside('../outside')
        self.assertTrue(capture.inside('reports/work/example').is_relative_to(capture.ROOT))
    def test_existing_app_stops_install(self):
        with patch.object(capture,'sim',return_value=json.dumps({capture.BUNDLE:{}})):
            with self.assertRaisesRegex(ValueError,'already installed'):capture.assert_not_installed('test')
    def test_openstep_inventory_rejects_installed_app(self):
        raw='{ "'+capture.BUNDLE+'" = { CFBundleName = Study; }; }'
        with patch.object(capture,'sim',return_value=raw):
            with self.assertRaisesRegex(ValueError,'already installed'):capture.assert_not_installed('test')
    def test_invalid_inventory_fails_closed(self):
        with patch.object(capture,'sim',return_value='not a plist'):
            with self.assertRaisesRegex(ValueError,'Cannot parse'):capture.assert_not_installed('test')
    def test_missing_app_passes_inventory(self):
        with patch.object(capture,'sim',return_value='{}'):
            capture.assert_not_installed('test')
    def test_alert_stops_capture(self):
        event={'eventMessage':"[scene] Setting deactivation reasons to: 'systemModalAlert'"}
        data=json.dumps(event)+'\n'+json.dumps({'finished':1},separators=(',',':'))
        with patch.object(capture,'sim',return_value=data):
            with self.assertRaisesRegex(ValueError,'alert is active'):capture.assert_clear('test')
    def test_success_removes_only_owned_app(self):
        proc=Mock()
        with patch.object(capture,'sim',return_value='{}') as sim:
            result=capture.cleanup_owned('target',True,proc,True)
        self.assertTrue(result['terminated'] and result['uninstalled'])
        self.assertEqual([call.args[0] for call in sim.call_args_list],['terminate','uninstall','listapps'])
        proc.wait.assert_called_once_with(timeout=10)
    def test_failure_keeps_owned_installation(self):
        with patch.object(capture,'sim',return_value='') as sim:
            result=capture.cleanup_owned('target',True,Mock(),False)
        self.assertTrue(result['terminated'])
        self.assertFalse(result['uninstalled'])
        self.assertEqual([call.args[0] for call in sim.call_args_list],['terminate'])
    def test_missing_alert_log_fails_closed(self):
        with patch.object(capture,'sim',return_value=''):
            with self.assertRaisesRegex(ValueError,'unavailable'):capture.assert_clear('test')

if __name__=='__main__':main()
