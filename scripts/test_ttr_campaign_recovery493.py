"""Qualify recovery with software fixtures. Never contact TTR."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import research_queue as q
import ttr_campaign_recovery493 as adapter

OUT=None


def queue_qualification():
    """Exercise the recovery adapter through an isolated queue with no TTR calls."""
    spec=q.load(OUT.parents[2]/'spec.json')
    config=q.load(q.ROOT/spec['inputs'][0]['path'])
    software=OUT/'software';software.mkdir()
    client=Client(config,OUT,corrupt=spec['id'].endswith('fail'))
    with patch.object(q,'ROOT',software), patch.object(adapter,'retained_restart',return_value={'verified':True}), \
         patch.object(adapter,'fixture_binding',return_value={'verified':True}):
        adapter.execute(config,client,OUT)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path='recovery-complete.json',sha256=q.digest(OUT/'recovery-complete.json'))]))


class Client:
    def __init__(self, config, output, failure=None, corrupt=False):
        self.config=config; self.output=output; self.failure=failure
        self.calls=[]; self.resumed=False; self.corrupt=corrupt
    def call(self,*args,**kwargs):
        self.calls.append(args)
        if args[:2]==self.failure: raise RuntimeError('injected_failure')
        if args[0]=='simulator': return dict(can_run=True,ownership=[dict(state='clear')])
        if args[0]=='status': return dict(commandActive=False,observationActive=False,queuedCommandCount=0)
        if args[0]=='fixture': return dict(isSettled=True,elementCount=7)
        if args[:2]==('campaign','resume'): self.resumed=True; return {}
        if args[:2]==('campaign','status'):
            result=copy.deepcopy(self.config['before'])
            if self.resumed:
                result.update(state='completed_with_failures',completed_cases=7,unattempted_cases=0,elapsed_seconds=500)
                for row in result['cases']:
                    row['state']='failed' if row['state'] in ('cleanup_unknown','failed') else 'completed'
                result['completed_cases']=sum(r['state']=='completed' for r in result['cases'])
                if self.corrupt: result['cases'][0]['duration_seconds']=123
            return result
        if args[:2]==('campaign','export'):
            folder=self.output/'corpus'; folder.mkdir()
            Image.new('RGB',(2,2)).save(folder/'test.png')
            return dict(export_path=str(folder))
        return {}


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        receipt=q.load(q.ROOT/'reports/work/ADRSPIKES493/campaign-owner-review/call-001.json')
        before=json.loads(receipt['stdout'])['data']['campaign']['_0']
        self.config=dict(version='campaign-recovery493-v1',campaign=adapter.CAMPAIGN,
                         manifestSHA256=adapter.MANIFEST,before=before)
        parent=q.ROOT/'.build/adr493-tests'; parent.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=parent); self.root=Path(self.temp.name)
        self.output=self.root/'out'; self.output.mkdir()
        self.root_patch=patch.object(q,'ROOT',self.root); self.root_patch.start()
    def tearDown(self):
        self.root_patch.stop(); self.temp.cleanup()
    def test_success_preserves_failed_case_and_refuses_duplicate(self):
        client=Client(self.config,self.output)
        adapter.execute(self.config,client,self.output)
        result=q.load(self.output/'recovery-complete.json')
        self.assertTrue(result['failedEvidencePreserved'])
        self.assertEqual(result['report']['completed_cases'],7)
        # The live checkpoint has changed. A second dispatch must fail before restart.
        with self.assertRaisesRegex(ValueError,'checkpoint_changed'):
            adapter.execute(self.config,client,self.output)
        self.assertEqual(sum(c[:2]==('campaign','resume') for c in client.calls),1)
    def test_restart_failure_never_resumes(self):
        client=Client(self.config,self.output,('simulator','restart'))
        with self.assertRaisesRegex(RuntimeError,'injected'): adapter.execute(self.config,client,self.output)
        self.assertFalse(client.resumed)
        self.assertTrue((self.root/'.build/campaign493-recovery-dispatch.json').exists())
    def test_lost_resume_cancels_only_this_campaign(self):
        client=Client(self.config,self.output,('campaign','resume'))
        with self.assertRaisesRegex(RuntimeError,'injected'): adapter.execute(self.config,client,self.output)
        self.assertIn(('campaign','cancel',adapter.CAMPAIGN),client.calls)
    def test_failed_case_change_blocks_release(self):
        client=Client(self.config,self.output,corrupt=True)
        with self.assertRaisesRegex(ValueError,'failed_case_replayed'): adapter.execute(self.config,client,self.output)
        self.assertFalse((self.output/'recovery-complete.json').exists())
    def test_export_failure_never_repeats_capture(self):
        client=Client(self.config,self.output,('campaign','export'))
        with self.assertRaisesRegex(RuntimeError,'injected'): adapter.execute(self.config,client,self.output)
        self.assertEqual(sum(c[:2]==('campaign','resume') for c in client.calls),1)
        self.assertFalse((self.output/'recovery-complete.json').exists())
    def test_budget_and_membership_fail_closed(self):
        for field,value in [('budget_remaining_seconds',600),('unattempted_cases',8)]:
            config=copy.deepcopy(self.config); config['before'][field]=value
            with self.assertRaises(ValueError): adapter.validate_config(config)

    def retained_config(self):
        from experiment_templates import pin
        folder=self.root/'proof';folder.mkdir()
        q.save(folder/'report.json',dict(cleanup_unknown_all=False,cleanup_unknown_targets=[],ownership=[],
            checks=[dict(code='restart_completed',state='ready')],
            inventory=[dict(id=adapter.TARGET,state='Booted')]))
        members=[]
        for name in ('report.json','shutdown-verification.stdout','boot.stdout','shutdown.stdout'):
            path=folder/name
            if name!='report.json': path.write_bytes(b'')
            members.append(dict(name=name,state='collected',size=path.stat().st_size,sha256=q.digest(path)))
        members.append(dict(name='prior-recovery-marker.json',state='absent',size=None,sha256=None))
        q.save(folder/'manifest.json',dict(operation='b838426c-3f16-40bc-8064-f73b584c8d00',reportAvailable=True,members=members))
        return dict(self.config,version='campaign-recovery493-v2',retainedRestart=pin(folder/'manifest.json'))

    def test_retained_proof_does_not_restart_or_repeat_failed_case(self):
        config=self.retained_config();client=Client(config,self.output)
        adapter.execute(config,client,self.output)
        self.assertFalse(any(c[:2]==('simulator','restart') for c in client.calls))
        self.assertEqual(sum(c[:2]==('campaign','resume') for c in client.calls),1)
        self.assertTrue(q.load(self.output/'recovery-complete.json')['failedEvidencePreserved'])

    def test_altered_retained_proof_prevents_all_calls(self):
        config=self.retained_config();client=Client(config,self.output)
        (self.root/'proof/report.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'export_bytes'): adapter.execute(config,client,self.output)
        self.assertEqual(client.calls,[])

    def six_config(self):
        config=self.retained_config()
        config.update(version='campaign-recovery493-v3',callerExport={'test':True},fixtureBinaries={'test':True})
        before=config['before']=copy.deepcopy(config['before'])
        before.update(state='completed_with_failures',failed_cases=2,unattempted_cases=6)
        before['cases'][0]['state']='failed'
        before['cases'][1].update(state='failed',duration_seconds=.03,failure={'code':'serviceUnavailable'})
        return config

    def test_six_success_preserves_both_failed_cases_without_restart(self):
        config=self.six_config();client=Client(config,self.output)
        with patch.object(adapter,'fixture_binding',return_value={'verified':True}):
            adapter.execute(config,client,self.output)
        report=q.load(self.output/'recovery-complete.json')['report']
        self.assertEqual(report['completed_cases'],6)
        self.assertEqual(report['cases'][:2],config['before']['cases'][:2])
        self.assertFalse(any(c[:2]==('simulator','restart') for c in client.calls))

    def test_six_changed_failed_evidence_blocks_release(self):
        config=self.six_config();client=Client(config,self.output,corrupt=True)
        with patch.object(adapter,'fixture_binding',return_value={'verified':True}):
            with self.assertRaisesRegex(ValueError,'failed_case_replayed'):
                adapter.execute(config,client,self.output)
        self.assertFalse((self.output/'recovery-complete.json').exists())

    def test_six_launch_failure_prevents_dispatch(self):
        config=self.six_config();client=Client(config,self.output)
        with patch.object(adapter,'fixture_binding',side_effect=ValueError('campaign_fixture_changed')):
            with self.assertRaisesRegex(ValueError,'fixture_changed'):
                adapter.execute(config,client,self.output)
        self.assertEqual(client.calls,[])


if __name__=='__main__': unittest.main()
