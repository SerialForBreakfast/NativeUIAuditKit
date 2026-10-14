import unittest
from unittest.mock import patch
from pathlib import Path
from hcf_settings368 import Client, page


class SettingsTests(unittest.TestCase):
    def test_page_requires_one_known_title(self):
        def report(names):
            return {'frames':[{'features':{'text':[{'text':n,'confidence':.9,'bounds':{'x':.2}} for n in names]}}]}
        self.assertEqual(page(report(['Display'])),'Display')
        for names in ([],['Display','Settings']):
            with self.assertRaisesRegex(ValueError,'uncertain'):page(report(names))

    def test_back_only_and_verified_parent(self):
        client=Client(Path('.'))
        with patch.object(client,'observe_page',side_effect=['Display','Display','Accessibility','Accessibility','Accessibility']), \
             patch('hcf_settings368.BaseClient.call',return_value={'state':'delivered'}) as call, \
             patch('hcf_settings368.time.sleep'):
            client.normalize('session')
            self.assertEqual(call.call_count,1)
            self.assertEqual(call.call_args.args[-2:],('--button','back'))

    def test_changed_page_sends_no_input(self):
        client=Client(Path('.'))
        with patch.object(client,'observe_page',side_effect=['Display','Focus Style']), \
             patch('hcf_settings368.BaseClient.call') as call,patch('hcf_settings368.time.sleep'):
            with self.assertRaisesRegex(ValueError,'page_changed'):client.normalize('session')
            call.assert_not_called()

    def test_wrong_parent_stops(self):
        client=Client(Path('.'))
        with patch.object(client,'observe_page',side_effect=['Display','Display','Settings']), \
             patch('hcf_settings368.BaseClient.call',return_value={'state':'delivered'}) as call, \
             patch('hcf_settings368.time.sleep'):
            with self.assertRaisesRegex(ValueError,'parent_unverified'):client.normalize('session')
            self.assertEqual(call.call_count,1)


if __name__=='__main__':unittest.main()
