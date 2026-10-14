import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import subprocess
from prepare_standard392 import prepare


class PreparationTests(unittest.TestCase):
    def test_matched_contract_and_no_capture(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/'.build') as folder:
            root = Path(folder)
            sources = root/'docs/experiment-graph-v1-requests'
            sources.mkdir(parents=True)
            for name, condition in [('a-directional', 'directional'), ('b-content-only', 'content_only')]:
                (sources/('NX02-'+name+'.json')).write_text(json.dumps(dict(version=17, source_role='calibration',
                    budget={}, condition=condition, target={'simulator_udid':'test'})))
            helper = root/'helper'
            helper.write_text('test')
            alias = root/'aatv'
            alias.symlink_to(helper)
            with patch('prepare_standard392.subprocess.run', return_value=subprocess.CompletedProcess(
                    [], 0, '{"success":true}', '')) as call:
                prepare(root, alias, root/'output')
            self.assertEqual(call.call_count, 2)
            for args in call.call_args_list:
                self.assertEqual(args.args[0][0], str(alias))
                self.assertEqual(args.args[0][2:4], ['campaign', 'plan'])
            a = json.loads((root/'output/movement-request.json').read_text())
            b = json.loads((root/'output/content-request.json').read_text())
            for key in ('seeds', 'positions', 'backgrounds', 'artwork_styles', 'source_role', 'budget'):
                self.assertEqual(a[key], b[key])
            with self.assertRaises(ValueError):
                prepare(root, helper, root/'output')


if __name__ == '__main__':
    unittest.main()
