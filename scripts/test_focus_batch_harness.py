"""Check batch limits, recovery, and owned process cleanup."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys
import focus_batch_harness as b


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=b.h.ROOT/'.build')
        self.root=Path(self.tmp.name)
        self.source=self.root/'render-headless-screen.swift';self.source.write_text('// fixture')
        self.assets=self.root/'assets';self.assets.mkdir()
        self.jobs=[dict(id='one',layout='grid',focusID=None),dict(id='two',layout='shelf',focusID=None)]
        self.plan=self.root/'plan.json'
        b.plan(self.source,self.assets,self.jobs,self.plan)
        self.campaign=b.initialize(self.plan,self.root/'campaign')

    def tearDown(self):self.tmp.cleanup()

    def test_pin_change(self):
        self.source.write_text('// changed')
        with self.assertRaises(ValueError):b.verify_plan(self.plan)

    def test_output_collision(self):
        with self.assertRaises(ValueError):b.initialize(self.plan,self.campaign)

    def test_role_and_jobs(self):
        d=json.loads(self.plan.read_text());d['jobs'][0]['layout']='native_hcf'
        self.plan.write_text(json.dumps(d))
        with self.assertRaises(ValueError):b.verify_plan(self.plan)

    def test_resource_defer(self):
        with patch.object(b.os,'getloadavg',return_value=(999,999,999)):
            self.assertEqual(b.run(self.campaign)['state'],'deferred_resources')

    def test_exclusive_lock(self):
        with b.lock():
            with self.assertRaisesRegex(ValueError,'resource_busy'):
                with b.lock():pass

    def test_cancel(self):
        (self.campaign/'STOP').touch()
        self.assertEqual(b.run(self.campaign)['state'],'cancelled')

    def test_interrupted(self):
        s=b.state(self.campaign);s['jobs']['one']=dict(state='running',folder='missing')
        b.save(self.campaign/'state.json',s)
        self.assertEqual(b.run(self.campaign)['state'],'needs_reconciliation')
        self.assertEqual(b.reconcile(self.campaign)['jobs']['one']['state'],'interrupted')

    def test_receipt_change(self):
        p=self.assets/'a';p.write_text('first');receipt=dict(files=b.inventory(self.assets))
        p.write_text('second')
        with self.assertRaises(ValueError):b.check_result(self.assets,receipt)

    def test_timeout_owned_child(self):
        (self.campaign/'tmp').mkdir()
        with b.lock() as fd:
            with self.assertRaisesRegex(ValueError,'operation_timeout'):
                b.execute([sys.executable,'-c','import time; time.sleep(10)'],self.campaign,
                          self.campaign/'timeout.log',.1,1000000,fd)

    def test_unknown_version(self):
        d=json.loads(self.plan.read_text());d['version']='future'
        self.plan.write_text(json.dumps(d))
        with self.assertRaises(ValueError):b.verify_plan(self.plan)

    def test_png_and_geometry_validation(self):
        folder=self.root/'render';folder.mkdir()
        before=folder/'grid_unfocused.png';after=folder/'grid_focused_cell.png'
        b.Image.new('RGB',(1920,1080),'black').save(before)
        b.Image.new('RGB',(1920,1080),'white').save(after)
        d=dict(schemaVersion='contract-v1-headless-focus',layoutType='grid',canvasWidth=1920,
               canvasHeight=1080,focusedNodeID='cell',nodes=[dict(id='cell',isFocused=True,
               unfocusedBounds=[10,10,100,100],focusedBounds=[5,5,110,110])],
               unfocusedImageSHA256=b.sha(before),focusedImageSHA256=b.sha(after))
        sidecar=folder/'grid_annotations.json';sidecar.write_text(json.dumps(d))
        result=b.validate_output(folder,self.jobs[0])
        self.assertFalse(result['nativeHCF'])
        before.write_bytes(b'corrupt')
        with self.assertRaises(ValueError):b.validate_output(folder,self.jobs[0])
        before.unlink()
        with self.assertRaises(OSError):b.validate_output(folder,self.jobs[0])

    def test_resume_skips_complete_job(self):
        s=b.state(self.campaign)
        folder=self.campaign/'done';folder.mkdir();(folder/'evidence').write_text('retained')
        s['jobs']['one']=dict(state='complete',folder='done',receipt=dict(files=b.inventory(folder)))
        s['binaryPath']='binary';binary=self.campaign/'binary';binary.write_text('pinned')
        s['binarySHA256']=b.sha(binary);b.save(self.campaign/'state.json',s)
        calls=[]
        def execute(command,*args):
            calls.append(command)
            Path(command[command.index('--output-dir')+1]).mkdir()
        with patch.object(b,'execute',side_effect=execute),patch.object(b,'validate_output',return_value={}),\
             patch.object(b.os,'getloadavg',return_value=(0,0,0)):
            result=b.run(self.campaign)
        self.assertEqual(result['state'],'complete')
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0][2],'shelf')


if __name__=='__main__':unittest.main()
