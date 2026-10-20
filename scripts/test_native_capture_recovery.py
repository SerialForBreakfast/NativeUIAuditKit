"""Test recovery evidence and guard retention without contacting a Simulator."""
import copy
import tempfile
import unittest
import io
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import patch
from PIL import Image

import research_queue as q
import research_trust as trust
import native_capture_recovery as recovery


def restored():
    return dict(complete=True, route=dict(hcf=dict(status='completed', desiredVerified=True,
        original='standard', observed='standard', restoration='verified')),
        disconnect=dict(state='closed'), postflight=dict(can_run=True, ownership=[dict(state='clear')]))


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=q.ROOT/'.build', prefix='recovery-test-')
        self.root = Path(self.temp.name)
        self.output = self.root/'out'; self.output.mkdir()
        self.marker = self.root/'marker.json'
        q.save(self.marker, dict(job='failed', pid=1))
        self.digest = q.digest(self.marker)
        q.save(self.output/'previous-marker.json', q.load(self.marker))
        (self.output/'qualification').mkdir()
        q.save(self.output/'qualification/qualification.json', restored())

    def tearDown(self):
        self.temp.cleanup()

    def finish(self, report=None, screenshot_error=False, mutate=False):
        def screenshot(target, path, timeout):
            if screenshot_error: raise RuntimeError('writer_failed')
            Image.new('RGB', (2,2)).save(path)
            if mutate: q.save(self.marker, dict(job='another'), replace=True)
        with patch.object(recovery, 'lock', nullcontext), patch.object(recovery.runtime.d, 'Fixture'), patch.object(recovery.native343, 'settle', return_value={'verified':True}), \
                patch.object(recovery.runtime.d, 'capture_screenshot', side_effect=screenshot):
            recovery.finish(self.output, self.marker, self.digest, report or restored(),
                            dict(scene=dict(focused_element_id='item')), 'http://127.0.0.1:8080')

    def test_success_retains_evidence_before_release(self):
        self.finish()
        self.assertFalse(self.marker.exists())
        evidence=q.load(self.output/'capture-evidence.json')
        self.assertTrue(evidence['cleanup'])
        self.assertEqual(evidence['images'][0]['sha256'],q.digest(self.output/'restored-fixture.png'))
        self.assertFalse(evidence['modelAccepted'])

    def test_unverified_restore_keeps_guard(self):
        r=restored();r['route']['hcf']['restoration']='required_unverified'
        with self.assertRaisesRegex(ValueError,'standard_restoration_unverified'):self.finish(r)
        self.assertTrue(self.marker.exists())

    def test_incomplete_and_busy_keep_guard(self):
        for field in ('complete','ownership','session','profile'):
            r=restored()
            if field=='complete':r['complete']=False
            elif field=='ownership':r['postflight']['ownership'][0]['state']='busy'
            elif field=='session':r['disconnect']['state']='uncertain'
            else:r['route']['hcf']['observed']='hcf'
            with self.assertRaises(ValueError):self.finish(r)
            self.assertTrue(self.marker.exists())

    def test_writer_failure_keeps_guard(self):
        with self.assertRaisesRegex(RuntimeError,'writer_failed'):self.finish(screenshot_error=True)
        self.assertTrue(self.marker.exists())

    def test_changed_guard_is_not_removed(self):
        with self.assertRaisesRegex(ValueError,'recovery_marker_changed'):self.finish(mutate=True)
        self.assertEqual(q.load(self.marker)['job'],'another')

    def test_receipt_failure_keeps_guard(self):
        original=q.save
        def save(path, value, **kwargs):
            if Path(path).name=='capture-evidence.json':raise OSError('disk_full')
            return original(path,value,**kwargs)
        with patch.object(q,'save',side_effect=save):
            with self.assertRaisesRegex(OSError,'disk_full'):self.finish()
        self.assertTrue(self.marker.exists())

    def test_specification_uses_current_contract(self):
        plan=self.root/'plan.json';q.save(plan,dict(version='native-capture-recovery-v2'))
        spec=recovery.specification('recovery-test',plan)
        q.validate(spec,q.MODULES)
        self.assertEqual(spec['version'],trust.SPEC_V2)
        self.assertEqual(spec['limits']['maxAttempts'],1)

    def test_evidence_gate_checks_receipt_and_image(self):
        self.finish()
        q.save(self.root/'reads.json',dict(version='research-reads-v1',truncated=False,files=[]))
        spec=dict(version=trust.SPEC_V2,jobKind='capture',evidence=dict(reads=[],captureReceipt='capture-evidence.json'))
        self.assertIsNone(trust.check_evidence(spec,self.root,self.output))
        (self.output/'restored-fixture.png').write_bytes(b'changed')
        self.assertEqual(trust.check_evidence(spec,self.root,self.output),'capture_receipt_image_changed')

    def qualify(self, initial='hcf', invalid=False, uncertain=False):
        calls = []
        def call(name, *args, **kwargs):
            calls.append((name, args))
            if name in ('readiness', 'postflight'):
                return dict(can_run=True, ownership=[dict(state='clear')])
            if name == 'ensure-standard':
                if uncertain:
                    raise RuntimeError('uncertain_input')
                return dict(hcf=dict(status='completed', desiredVerified=not invalid,
                    original=initial, observed='hcf' if invalid else 'standard', inputsAttempted=int(initial=='hcf')))
            if name == 'hcf-roundtrip':
                return restored()['route']
            raise AssertionError(name)
        import hcf_settings368
        with patch.object(recovery.runtime, 'lock', nullcontext), \
                patch.object(hcf_settings368, 'Client') as client, \
                patch.object(recovery.runtime.d, 'Fixture') as fixture, \
                patch.object(recovery.runtime.d, 'run', return_value='fixture'):
            client.return_value.call.side_effect = call
            client.return_value.remote.side_effect = [dict(operationID='owned', state='ready'), dict(state='closed')]
            client.return_value.terminal.side_effect = lambda receipt, desired: receipt
            fixture.return_value.snapshot.return_value = dict(device=dict(simulator_udid='test'))
            report = recovery.runtime.run(self.root/'sequence', normalize=True, ensure_standard=True)
        return report, calls

    def test_standard_preparation_precedes_roundtrip_in_same_session_and_journal(self):
        report, calls = self.qualify()
        self.assertTrue(report['complete'])
        routes = [args for name,args in calls if name in ('ensure-standard','hcf-roundtrip')]
        self.assertEqual([args[args.index('--mode')+1] for args in routes], ['ensure','roundtrip'])
        self.assertEqual([args[args.index('--desired')+1] for args in routes], ['standard','hcf'])
        for option in ('--map-dir','--session','--simulator-udid'):
            self.assertEqual(routes[0][routes[0].index(option)+1],routes[1][routes[1].index(option)+1])
        self.assertTrue(report['settingChanged'])

    def test_invalid_preparation_stops_roundtrip_and_retains_cleanup(self):
        report, calls = self.qualify(invalid=True)
        self.assertFalse(report['complete'])
        self.assertEqual(report['error'], 'standard_preparation_unverified')
        self.assertNotIn('hcf-roundtrip', [name for name,args in calls])
        self.assertEqual(report['disconnect']['state'],'closed')

    def test_uncertain_preparation_is_not_retried(self):
        report, calls = self.qualify(uncertain=True)
        self.assertFalse(report['complete'])
        self.assertEqual([name for name,args in calls].count('ensure-standard'),1)
        self.assertNotIn('hcf-roundtrip',[name for name,args in calls])


if __name__=='__main__':unittest.main()


OUT = None


def queue_check():
    """Run software-only recovery checks through an isolated diagnostic queue."""
    spec=q.load(OUT.parents[2]/'spec.json')
    config=q.load(q.ROOT/spec['inputs'][0]['path'])
    q.require(config.get('version')=='recovery-software-check-v1','recovery_check_version')
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream).run(unittest.defaultTestLoader.loadTestsFromTestCase(RecoveryTests))
    (OUT/'checks.txt').write_text(stream.getvalue())
    q.require(result.wasSuccessful(),'recovery_software_checks_failed')
    q.save(OUT/'checks.json',dict(tests=result.testsRun,softwareOnly=True,nativeRecoveryVerified=False))
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path='checks.json',sha256=q.digest(OUT/'checks.json'))]))
