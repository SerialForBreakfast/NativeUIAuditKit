"""Exercise admission with synthetic receipts. Never contact a Simulator."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import research_queue as q
import research_approval as approval
import recovery_capture_gate437 as gate
from experiment_templates import pin
from test_native_capture_recovery import restored


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=q.ROOT/'.build', prefix='gate437-test-')
        self.root = Path(self.temp.name)
        self.queue = self.root/'queue'; self.queue.mkdir()
        self.recovery = self.queue/'jobs'/'recovery'
        self.attempt = self.recovery/'attempts'/'1'
        self.out = self.attempt/'out'; self.out.mkdir(parents=True)
        (self.out/'qualification').mkdir()
        self.entries = []
        for family in ('button', 'row', 'tab'):
            for position in ('top', 'bottom'):
                path = self.root/(family+'-'+position+'.json')
                case = gate.native_coverage402.controls_case(family, path.stem, path.stem, 7433+len(self.entries))
                q.save(path, dict(version='native-controls-t45-v1', role='study-pending', trainingEligible=False,
                    profiles=['standard','hcf'], repeats=1, expectedFrames=8, captureBudgetBytes=100_000_000,
                    group=path.stem, shard=path.stem, cases=[case], helperSHA256='a'*64,
                    binding=dict(simulatorUDID=gate.native343.TARGET, endpoint='http://127.0.0.1:8080'),
                    qualification=dict(complete=False,restoration='pending')))
                self.entries.append(dict(id='capture-'+path.stem, draft=pin(path)))
        draft = q.load(self.root/'button-top.json')
        stage = self.root/'stage.json'; q.save(stage, dict(version='test-only'))
        self.recovery_plan = self.root/'recovery-plan.json'
        q.save(self.out/'previous-marker.json', dict(job='old', pid=1))
        original = self.root/'original-marker.json'
        original.write_text('{"pid":1,"job":"old"}')
        self.original = original
        self.rplan = dict(version='native-capture-recovery-v2', binding=draft['binding'],
            helperSHA256=draft['helperSHA256'], markerSHA256=q.digest(original),
            failedJob='old', staging=pin(stage))
        q.save(self.recovery_plan, self.rplan)
        # Retained synthetic scene checks the same signature function as native recovery.
        snapshot = dict(device=dict(simulator_udid=gate.native343.TARGET, fixture_instance_id='test', fixture_run_id='test'),
            startedAt=1, finishedAt=2, scene=dict(recipe={}, focused_element_id=None, is_settled=True,
                observation_generation=1, timestamp=1, scene_width=1920, scene_height=1080, elements=[],
                focus_observation=dict(verified=True, source='uikit_focus_system', observedID=None, generation=1, plannedFocusIDs=[]),
                observation_diagnostics=dict(nativeFocusResolved=True, reason='ready', nativeProbe=dict(referenceFocused=True),
                    sampledGeneration=1, sampleAgeMilliseconds=0, stableMilliseconds=150)))
        for name in ('fixture-before.json', 'fixture-after.json'):q.save(self.out/name, snapshot)
        q.save(self.out/'qualification/qualification.json', restored())
        Image.new('RGB', (2,2)).save(self.out/'restored-fixture.png')
        q.save(self.out/'capture-evidence.json', dict(version='research-capture-evidence-v1', cleanup=True,
            images=[dict(path='restored-fixture.png', sha256=q.digest(self.out/'restored-fixture.png'))]))
        q.save(self.out/'recovery.json', dict(complete=True, trainingEligible=False, target=gate.native343.TARGET,
            qualification=pin(self.out/'qualification/qualification.json'), fixture=pin(self.out/'fixture-after.json'),
            previousMarker=pin(self.out/'previous-marker.json')))
        self.producer = dict(id='recovery', capture=dict(plan=pin(self.recovery_plan), target=gate.native343.TARGET))
        q.save(self.recovery/'spec.json', self.producer)
        self.publish_result()
        self.plan = dict(version='recovery-capture-admission-v2',
            recovery=dict(job='recovery', specSHA256=q.text_digest(self.producer)), captures=self.entries, staging=pin(stage), originalMarker=pin(original))
        self.plan_path = self.root/'admission-plan.json'; q.save(self.plan_path, self.plan)
        self.spec = gate.specification('gate-test', self.plan_path)
        self.output = self.root/'prepared'; self.output.mkdir()

    def tearDown(self):self.temp.cleanup()

    def publish_result(self, status='complete'):
        q.save(self.attempt/'result.json', dict(status=status, specSHA256=q.text_digest(self.producer),
            outputs=[dict(path=str(p.relative_to(self.out)), sha256=q.digest(p))
                for p in sorted(self.out.rglob('*')) if p.is_file()]), replace=True)

    def prepare(self):return gate.prepare(self.spec, self.queue, self.plan, self.output)[0]

    def test_positive_preserves_every_nonqualification_field(self):
        children=self.prepare()
        for child, entry in zip(children,self.entries):
            recipe=q.load(q.ROOT/child['capture']['plan']['path'])
            original=q.load(q.ROOT/entry['draft']['path'])
            recipe['qualification']=original['qualification']
            self.assertEqual(recipe,original)
            self.assertEqual(child['limits']['maxAttempts'],1)
            self.assertEqual(child['conditions'][0]['outcome'],'supported')
        self.assertEqual(children,self.prepare())

    def test_incomplete_recovery(self):
        self.publish_result('failed')
        with self.assertRaisesRegex(ValueError,'dependency_incomplete'):self.prepare()
        self.assertFalse((self.output/'gate.json').exists())

    def test_original_bytes_and_saved_identity_are_independent_checks(self):
        self.assertNotEqual(q.digest(self.original), q.digest(self.out/'previous-marker.json'))
        self.assertEqual(len(self.prepare()), 6)
        path = self.out/'previous-marker.json'
        q.save(path, dict(job='other', pid=1), replace=True)
        receipt = q.load(self.out/'recovery.json')
        receipt['previousMarker'] = pin(path)
        q.save(self.out/'recovery.json', receipt, replace=True)
        self.publish_result()
        with self.assertRaisesRegex(ValueError, 'gate_old_marker'):
            self.prepare()

    def test_changed_original_bytes_fail_before_admission(self):
        self.original.write_text('{"job":"old","pid":1}')
        with self.assertRaisesRegex(ValueError, 'input_changed'):
            self.prepare()

    def test_failed_restoration_and_missing_ownership(self):
        for key in ('restoration','ownership','empty'):
            report=restored()
            if key=='restoration':report['route']['hcf']['restoration']='pending'
            elif key=='ownership':report['postflight']['ownership']=[dict(state='busy')]
            else:report['postflight']['ownership']=[]
            path=self.out/'qualification/qualification.json';q.save(path,report,replace=True)
            receipt=q.load(self.out/'recovery.json');receipt['qualification']=pin(path)
            q.save(self.out/'recovery.json',receipt,replace=True);self.publish_result()
            with self.assertRaises(ValueError):self.prepare()

    def test_changed_recovery_bytes(self):
        q.save(self.out/'fixture-after.json',{},replace=True)
        with self.assertRaisesRegex(ValueError,'dependency_output_changed'):self.prepare()

    def test_changed_draft(self):
        q.save(q.ROOT/self.entries[0]['draft']['path'],{},replace=True)
        with self.assertRaisesRegex(ValueError,'input_changed'):self.prepare()

    def test_wrong_fixture_after_restore(self):
        path=self.out/'fixture-after.json';doc=q.load(path);doc['device']['fixture_run_id']='other'
        q.save(path,doc,replace=True)
        receipt=q.load(self.out/'recovery.json');receipt['fixture']=pin(path)
        q.save(self.out/'recovery.json',receipt,replace=True);self.publish_result()
        with self.assertRaisesRegex(ValueError,'runtime_or_recipe_changed'):self.prepare()

    def test_missing_output_and_wrong_producer(self):
        self.spec['dependencies'][0]['specSHA256']='0'*64
        with self.assertRaisesRegex(ValueError,'dependency_spec_changed'):self.prepare()
        self.spec['dependencies'][0]['specSHA256']=q.text_digest(self.producer)
        (self.out/'restored-fixture.png').unlink()
        self.publish_result()
        with self.assertRaisesRegex(ValueError,'dependency_output_missing'):self.prepare()

    def test_conflicting_child_prevents_any_admission(self):
        children=self.prepare()
        target=self.queue/'jobs'/children[-1]['id'];target.mkdir()
        q.save(target/'spec.json',dict(id='conflict'))
        with self.assertRaisesRegex(ValueError,'gate_child_conflict'):gate.admit(children,self.queue,self.output)
        self.assertFalse(approval.path(self.queue).exists())

    def test_disk_failure_does_not_approve_children(self):
        children=self.prepare()
        with patch.object(gate,'retain',side_effect=OSError('disk_full')):
            with self.assertRaisesRegex(OSError,'disk_full'):gate.admit(children,self.queue,self.output)
        self.assertFalse(approval.path(self.queue).exists())

    def test_negative_restoration_through_actual_queue(self):
        path=self.out/'qualification/qualification.json';report=restored()
        report['route']['hcf']['restoration']='required_unverified';q.save(path,report,replace=True)
        receipt=q.load(self.out/'recovery.json');receipt['qualification']=pin(path)
        q.save(self.out/'recovery.json',receipt,replace=True);self.publish_result()
        self.spec['adapter']=dict(type='python-callable',steps=['test_recovery_capture_gate437.queue_gate'],
                                 outputAttributes=['test_recovery_capture_gate437.OUT'])
        spec_path=self.root/'spec.json';q.save(spec_path,self.spec);q.submit(spec_path,self.queue)
        approval.approve(self.queue,self.spec['id'],'test','isolated negative restoration test')
        self.assertEqual(q.run(self.queue,job_ids=[self.spec['id']],lock=self.root/'runner.lock'),[('gate-test','failed')])
        for entry in self.entries:self.assertFalse((self.queue/'jobs'/entry['id']).exists())

    def test_partial_admission_resumes_and_revocation_is_respected(self):
        children=self.prepare()
        original=approval.approve
        calls=[]
        def fail_once(*args,**kwargs):
            calls.append(args[1])
            if len(calls)==3:raise OSError('planned_interruption')
            return original(*args,**kwargs)
        with patch.object(approval,'capture_ownership',return_value={'softwareOnly':True}):
            with patch.object(approval,'approve',side_effect=fail_once):
                with self.assertRaisesRegex(OSError,'planned_interruption'):gate.admit(children,self.queue,self.output)
            gate.admit(children,self.queue,self.output)
            events=copy.deepcopy(approval.load(self.queue)['events'])
            gate.admit(children,self.queue,self.output)
            self.assertEqual(events,approval.load(self.queue)['events'])
            self.assertEqual(len(events),6)
            approval.revoke(self.queue,children[0]['id'],'test','intentional test revocation')
            with self.assertRaisesRegex(ValueError,'gate_child_revoked'):gate.admit(children,self.queue,self.output)

    def test_real_queue_gate_and_duplicate_dispatch(self):
        # This diagnostic wrapper mocks only live preflight and ownership. It never runs capture jobs.
        self.spec['adapter']=dict(type='python-callable',steps=['test_recovery_capture_gate437.queue_gate'],
                                 outputAttributes=['test_recovery_capture_gate437.OUT'])
        path=self.root/'spec.json';q.save(path,self.spec);q.submit(path,self.queue)
        approval.approve(self.queue,self.spec['id'],'test','isolated software admission test')
        run=lambda:q.run(self.queue,job_ids=[self.spec['id']],lock=self.root/'runner.lock')
        result=run()
        if result != [('gate-test','complete')]:
            attempt=self.queue/'jobs/gate-test/attempts/1'
            self.fail(str(result)+' '+(attempt/'result.json').read_text()+' '+(attempt/'stderr.log').read_text())
        self.assertEqual(run(),[])
        for entry in self.entries:
            child=q.load(self.queue/'jobs'/entry['id']/'spec.json')
            self.assertEqual(len(q.dependency_inputs(child,self.queue)),1)
            self.assertEqual(q.attempts_of(self.queue/'jobs'/entry['id']),[])


OUT=None


def queue_gate():
    q.require(OUT.parents[4] != q.QUEUE, 'software_test_on_live_queue')
    with patch.object(gate,'preflight'), patch.object(approval,'capture_ownership',return_value={'softwareOnly':True}):
        gate.OUT=OUT;gate.run()


if __name__=='__main__':unittest.main()
