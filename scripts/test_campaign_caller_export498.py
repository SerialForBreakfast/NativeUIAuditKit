"""Verify the caller exporter without contacting TTR or making captures."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import research_queue as q
from ttr_campaign_queue493 import Client


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build')
        self.root=Path(self.temp.name); self.out=self.root/'out'; self.out.mkdir()
        self.pins={}
        for key,name in [('script','export-campaign.rb'),('dependency','export-fixture-job.rb'),('helper','tvtestrig-mcp')]:
            path=self.root/name;path.write_text('test')
            self.pins[key]=dict(path=str(path),sha256=q.digest(path))
        self.client=Client(dict(callerExport=self.pins),self.out)

    def tearDown(self): self.temp.cleanup()

    def response(self, bad=False):
        def run(args,**kwargs):
            folder=Path(args[-1]);folder.mkdir();p=folder/'manifest.json';p.write_text('{}')
            result=dict(campaign=dict(campaign_id='retained'),exported_path=str(folder),
                files=[dict(path=p.name,bytes=2,sha256='0'*64 if bad else q.digest(p))])
            return SimpleNamespace(returncode=0,stdout=json.dumps(result),stderr='')
        return run

    def test_success_uses_caller_and_verifies_bytes(self):
        with patch('ttr_campaign_queue493.subprocess.run',side_effect=self.response()) as run:
            result=self.client.call('campaign','export','retained','--output-dir',str(self.out/'corpus'))
        self.assertEqual(result['export_path'],str(self.out/'corpus'))
        self.assertEqual(run.call_args.args[0][0],'/usr/bin/ruby')

    def test_bad_export_has_no_receipt(self):
        with patch('ttr_campaign_queue493.subprocess.run',side_effect=self.response(True)):
            with self.assertRaisesRegex(ValueError,'export_bytes'):
                self.client.call('campaign','export','retained','--output-dir',str(self.out/'corpus'))
        self.assertFalse((self.out/'export-receipt.json').exists())

    def test_changed_dependency_blocks_before_execution(self):
        Path(self.pins['dependency']['path']).write_text('changed')
        with patch('ttr_campaign_queue493.subprocess.run') as run:
            with self.assertRaisesRegex(ValueError,'export_source_changed'):
                Client(dict(callerExport=self.pins),self.out)
        run.assert_not_called()

    def test_existing_destination_prevents_export(self):
        (self.out/'corpus').mkdir()
        with patch('ttr_campaign_queue493.subprocess.run') as run:
            with self.assertRaisesRegex(ValueError,'export_destination'):
                self.client.export('retained',self.out/'corpus',30)
        run.assert_not_called()
