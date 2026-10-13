"""Test the research queue with small synthetic modules; no FOCUS code runs."""
import copy
import json
import shutil
import sys
import textwrap
import unittest
import uuid
from unittest import mock

import research_queue as q

FIXTURE = textwrap.dedent('''
    import json, time
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[{depth}]
    OUT = ROOT / "never-written"
    def produce():
        source = json.loads((ROOT / "{input_rel}").read_text())
        (OUT / "result.json").write_text(json.dumps(dict(value=source["value"] * 2, seconds=time.time(),
            self=str((OUT / "result.json").relative_to(ROOT)))))
    def produce_other():
        (OUT / "result.json").write_text(json.dumps(dict(value=999, seconds=0)))
    def fail():
        raise RuntimeError("planned failure")
    def slow():
        time.sleep(30)
    def brief():
        time.sleep(0.3)
        produce()
    def oversized():
        (OUT / 'large.bin').write_bytes(b'x' * 20000)
        time.sleep(30)
    def produce_nested():
        (OUT / "run").mkdir()
        history = [dict(epoch=1, seconds=time.time()), dict(epoch=2, seconds=time.time())]
        (OUT / "run" / "fit.json").write_text(json.dumps(dict(loss=0.5 + 1e-9, history=history, folder=OUT.name)))
        (OUT / "weights.bin").write_bytes(b"abc")
''')


class QueueTests(unittest.TestCase):
    def test_live_size_tolerates_removed_temporary(self):
        vanished = mock.Mock()
        vanished.lstat.side_effect = FileNotFoundError('atomic rename')
        present = mock.Mock()
        present.lstat.return_value = mock.Mock(st_mode=q.stat.S_IFREG, st_size=321)
        folder = mock.Mock()
        folder.rglob.return_value = [vanished, present]
        self.assertEqual(q.live_output_bytes(folder), 321)

    def test_live_size_rejects_links_and_permission_errors(self):
        path = mock.Mock()
        folder = mock.Mock()
        folder.rglob.return_value = [path]
        path.lstat.return_value = mock.Mock(st_mode=q.stat.S_IFLNK, st_size=10)
        with self.assertRaisesRegex(ValueError, 'symlink_in_outputs'):
            q.live_output_bytes(folder)
        path.lstat.side_effect = PermissionError('denied')
        with self.assertRaises(PermissionError):
            q.live_output_bytes(folder)

    def setUp(self):
        self.base = q.ROOT / '.build' / f'test-research-queue-{uuid.uuid4().hex}'
        self.modules = self.base / 'modules'
        self.queue = self.base / 'queue'
        self.recorded = self.base / 'recorded'
        for folder in (self.modules, self.queue, self.recorded):
            folder.mkdir(parents=True)
        self.input = self.base / 'input.json'
        self.input.write_text(json.dumps(dict(value=21)))
        depth = len(self.modules.relative_to(q.ROOT).parts)
        (self.modules / 'rq_fixture.py').write_text(FIXTURE.format(depth=depth, input_rel=q.relative(self.input)))
        self.lock = self.base / 'lock'

    def tearDown(self):
        shutil.rmtree(self.base, ignore_errors=True)

    def spec(self, **changes):
        spec = dict(version=q.SPEC_VERSION, id='job-a', task='TEST338', owner='test', kind='screen',
                    hypothesis='doubling works', decisionRule='value equals 42', authority='diagnostic',
                    adapter=dict(type='python-callable', steps=['rq_fixture.produce'], outputAttributes=['rq_fixture.OUT']),
                    inputs=[dict(path=q.relative(self.input), sha256=q.digest(self.input))],
                    limits=dict(timeoutSeconds=20, maxOutputBytes=100000, maxAttempts=2))
        spec.update(changes)
        return spec

    def write_spec(self, spec, name='spec.json'):
        path = self.base / name
        path.write_text(json.dumps(spec))
        return path

    def submit(self, spec):
        return q.submit(self.write_spec(spec), self.queue, self.modules)

    def run_queue(self, max_jobs=5, retry=False):
        return q.run(self.queue, self.modules, max_jobs, sys.executable, self.lock, retry=retry)

    def attempt(self, number=1, job='job-a'):
        return self.queue / 'jobs' / job / 'attempts' / str(number)

    def test_validation_errors(self):
        cases = [
            (dict(version='v0'), 'spec_version'),
            (dict(id='../x'), 'id_format'),
            (dict(authority='unknown'), 'authority_unknown'),
            (dict(authority='training'), 'training_fields'),
            (dict(training=dict()), 'training_only_for_training_jobs'),
            (dict(authority='capture'), 'capture_contract'),
            (dict(kind='replay'), 'replay_missing'),
            (dict(inputs=[dict(path='/etc/passwd', sha256='0' * 64)]), 'unsafe_path'),
            (dict(inputs=[dict(path='a/../b', sha256='0' * 64)]), 'unsafe_path'),
            (dict(inputs=[dict(path='a', sha256='xyz')]), 'pin_hash_format'),
            (dict(limits=dict(timeoutSeconds=0, maxOutputBytes=1, maxAttempts=1)), 'limits_timeout'),
        ]
        for change, reason in cases:
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, reason):
                q.validate(self.spec(**change), self.modules)
        for step, reason in [('os.system', 'module_not_allowlisted'), ('rq_fixture', 'target_format'),
                             ('rq_fixture.a-b', 'target_format')]:
            adapter = dict(type='python-callable', steps=[step], outputAttributes=['rq_fixture.OUT'])
            with self.subTest(step=step), self.assertRaisesRegex(ValueError, reason):
                q.validate(self.spec(adapter=adapter), self.modules)

    def test_submit_checks_inputs_and_identity(self):
        self.assertEqual(self.submit(self.spec()), 'submitted')
        self.assertEqual(self.submit(self.spec()), 'already_submitted')
        with self.assertRaisesRegex(ValueError, 'job_exists'):
            self.submit(self.spec(hypothesis='changed'))
        bad = self.spec(id='job-b', inputs=[dict(path=q.relative(self.input), sha256='0' * 64)])
        with self.assertRaisesRegex(ValueError, 'input_changed'):
            self.submit(bad)

    def test_producer_dependency_runs_and_rejects_changed_bytes(self):
        producer = self.spec()
        consumer = self.spec(id='job-b', dependencies=[dict(job='job-a',
            specSHA256=q.text_digest(producer), outputs=['result.json'])])
        self.submit(consumer)
        self.assertEqual(q.state(self.queue / 'jobs/job-b')[0], 'blocked')
        self.submit(producer)
        self.assertEqual(self.run_queue(), [('job-a', 'complete'), ('job-b', 'complete')])
        resolved = q.load(self.attempt(job='job-b') / 'out/dependencies.json')
        self.assertEqual(resolved[0]['outputs'][0]['sha256'], q.digest(self.attempt() / 'out/result.json'))
        (self.attempt() / 'out/result.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'dependency_output_changed'):
            q.dependency_inputs(consumer, self.queue)

    def test_failed_producer_blocks_consumer(self):
        producer = self.spec(adapter=dict(type='python-callable', steps=['rq_fixture.fail'], outputAttributes=[]))
        self.submit(producer)
        self.submit(self.spec(id='job-b', dependencies=[dict(job='job-a',
            specSHA256=q.text_digest(producer), outputs=['result.json'])]))
        self.assertEqual(self.run_queue(), [('job-a', 'failed')])
        self.assertEqual(q.state(self.queue / 'jobs/job-b')[0], 'blocked')

    def test_dependency_cycle_is_rejected(self):
        a = self.spec(dependencies=[dict(job='job-b', specSHA256='0'*64, outputs=['result.json'])])
        self.submit(a)
        b = self.spec(id='job-b', dependencies=[dict(job='job-a', specSHA256=q.text_digest(a), outputs=['result.json'])])
        with self.assertRaisesRegex(ValueError, 'dependency_cycle'):
            self.submit(b)

    def test_dependency_paths_and_staging_are_rejected(self):
        dep = dict(job='job-b', specSHA256='0'*64, outputs=['../result.json'])
        with self.assertRaisesRegex(ValueError, 'replay_name'):
            q.validate(self.spec(dependencies=[dep]), self.modules)
        dep['outputs'] = ['result.json']
        stage = [{'from':dict(path=q.relative(self.input), sha256=q.digest(self.input)), 'to':'dependencies.json'}]
        with self.assertRaisesRegex(ValueError, 'reserved_dependency_output'):
            q.validate(self.spec(dependencies=[dep], stage=stage), self.modules)

    def test_run_records_result_and_closure_then_skips(self):
        self.submit(self.spec())
        self.assertEqual(self.run_queue(), [('job-a', 'complete')])
        result = q.load(self.attempt() / 'result.json')
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(json.loads((self.attempt() / 'out/result.json').read_text())['value'], 42)
        fixture = q.relative(self.modules / 'rq_fixture.py')
        self.assertIn(dict(path=fixture, sha256=q.digest(self.modules / 'rq_fixture.py')), result['closure']['modules'])
        self.assertEqual([s['step'] for s in result['steps']], ['rq_fixture.produce'])
        self.assertEqual(self.run_queue(), [])
        self.assertFalse(self.attempt(2).exists())

    def test_changed_output_reopens_job(self):
        self.submit(self.spec())
        self.run_queue()
        (self.attempt() / 'out/result.json').write_text('{}')
        self.assertEqual(q.state(self.queue / 'jobs/job-a')[0], 'failed')

    def test_interrupted_attempt_is_recorded_then_retried(self):
        self.submit(self.spec())
        self.attempt().mkdir(parents=True)
        q.save(self.attempt() / 'attempt.json', dict(version=q.ATTEMPT_VERSION))
        self.assertEqual(q.state(self.queue / 'jobs/job-a')[0], 'interrupted')
        self.assertEqual(self.run_queue(), [])
        self.assertEqual(self.run_queue(retry=True), [('job-a', 'complete')])
        self.assertEqual(q.load(self.attempt() / 'result.json')['status'], 'interrupted')
        self.assertEqual(q.load(self.attempt(2) / 'result.json')['status'], 'complete')

    def test_failure_keeps_logs_and_stops_at_attempt_limit(self):
        adapter = dict(type='python-callable', steps=['rq_fixture.fail'], outputAttributes=['rq_fixture.OUT'])
        self.submit(self.spec(adapter=adapter))
        self.assertEqual(self.run_queue(), [('job-a', 'failed')])
        self.assertIn('planned failure', (self.attempt() / 'stderr.log').read_text())
        self.assertEqual(self.run_queue(), [])
        self.assertEqual(self.run_queue(retry=True), [('job-a', 'failed')])
        self.assertEqual(self.run_queue(), [])
        self.assertEqual(q.state(self.queue / 'jobs/job-a')[0], 'exhausted')

    def test_timeout_stops_the_process(self):
        adapter = dict(type='python-callable', steps=['rq_fixture.slow'], outputAttributes=['rq_fixture.OUT'])
        self.submit(self.spec(adapter=adapter, limits=dict(timeoutSeconds=1, maxOutputBytes=1000, maxAttempts=1)))
        self.run_queue()
        result = q.load(self.attempt() / 'result.json')
        self.assertEqual((result['status'], result['reason']), ('failed', 'timeout'))
        self.assertLess(result['wallSeconds'], 15)

    def test_input_change_after_submit_blocks_execution(self):
        self.submit(self.spec())
        self.input.write_text(json.dumps(dict(value=1)))
        self.run_queue()
        result = q.load(self.attempt() / 'result.json')
        self.assertEqual((result['status'], result['reason']), ('failed', 'input_changed'))
        self.assertFalse((self.attempt() / 'out').exists())

    def test_lock_prevents_second_runner(self):
        self.submit(self.spec())
        with q.host_lock(self.lock), self.assertRaisesRegex(ValueError, 'resource_busy'):
            self.run_queue()

    def replay_spec(self, recorded, ignore):
        (self.recorded / 'result.json').write_text(json.dumps(recorded))
        return self.spec(kind='replay', replay=dict(recordedDirectory=q.relative(self.recorded), files=[
            dict(name='result.json', sha256=q.digest(self.recorded / 'result.json'), ignore=ignore)]))

    def test_replay_matches_with_declared_fields_and_mapped_paths(self):
        recorded = dict(value=42, seconds=1.0, self=q.relative(self.recorded / 'result.json'))
        self.submit(self.replay_spec(recorded, [dict(path='seconds', reason='wall time')]))
        self.run_queue()
        replay = q.load(self.attempt() / 'result.json')['replay']
        self.assertTrue(replay['matched'], replay)
        self.assertEqual(replay['files'][0]['ignored'], [dict(path='seconds', recordedFields=1, replayedFields=1)])

    def test_replay_reports_exact_differences(self):
        recorded = dict(value=41, seconds=1.0, self=q.relative(self.recorded / 'result.json'))
        self.submit(self.replay_spec(recorded, [dict(path='seconds', reason='wall time')]))
        self.run_queue()
        result = q.load(self.attempt() / 'result.json')
        self.assertEqual(result['status'], 'complete')
        file = result['replay']['files'][0]
        self.assertFalse(file['matched'])
        self.assertEqual(file['differencePaths'], ['value'])
        self.assertEqual(file['maxNumericDiff'], 1)

    def test_replay_without_declared_field_fails(self):
        recorded = dict(value=42, seconds=1.0, self=q.relative(self.recorded / 'result.json'))
        self.submit(self.replay_spec(recorded, []))
        self.run_queue()
        self.assertEqual(q.load(self.attempt() / 'result.json')['replay']['files'][0]['differencePaths'], ['seconds'])

    def test_ignore_requires_reason(self):
        spec = self.replay_spec(dict(value=1), [dict(path='seconds', reason=' ')])
        with self.assertRaisesRegex(ValueError, 'ignore_reason'):
            q.validate(spec, self.modules)

    def nested_spec(self, tolerance):
        (self.recorded / 'run').mkdir()
        fit = self.recorded / 'run/fit.json'
        fit.write_text(json.dumps(dict(loss=0.5, history=[dict(epoch=1, seconds=1.0), dict(epoch=2, seconds=2.0)],
                                       folder='FOCUS-X')))
        (self.recorded / 'weights.bin').write_bytes(b'abc')
        adapter = dict(type='python-callable', steps=['rq_fixture.produce_nested'], outputAttributes=['rq_fixture.OUT'],
                       outputFolderName='FOCUS-X')
        return self.spec(kind='replay', adapter=adapter, replay=dict(recordedDirectory=q.relative(self.recorded), files=[
            dict(name='run/fit.json', sha256=q.digest(fit), tolerance=tolerance,
                 ignore=[dict(path='history[].seconds', reason='wall time')]),
            dict(name='weights.bin', sha256=q.digest(self.recorded / 'weights.bin'), compare='sha256')]))

    def test_replay_nested_files_wildcards_tolerance_and_hash_compare(self):
        self.submit(self.nested_spec(1e-6))
        self.run_queue()
        self.assertTrue((self.attempt() / 'out/FOCUS-X/run/fit.json').is_file())
        replay = q.load(self.attempt() / 'result.json')['replay']
        self.assertTrue(replay['matched'], replay)
        fit, weights = replay['files']
        self.assertEqual(fit['ignored'], [dict(path='history[].seconds', recordedFields=2, replayedFields=2)])
        self.assertEqual((fit['exactlyEqual'], fit['withinToleranceCount']), (False, 1))
        self.assertAlmostEqual(fit['maxNumericDiff'], 1e-9)
        self.assertEqual((weights['compare'], weights['matched']), ('sha256', True))

    def test_replay_without_tolerance_reports_small_difference(self):
        self.submit(self.nested_spec(0))
        self.run_queue()
        fit = q.load(self.attempt() / 'result.json')['replay']['files'][0]
        self.assertFalse(fit['matched'])
        self.assertEqual(fit['differencePaths'], ['loss'])

    def test_replay_field_rules(self):
        spec = self.nested_spec(1e-6)
        cases = [(('ignore', [dict(path='history[]', reason='x')]), 'ignore_path'),
                 (('ignore', [dict(path='a b', reason='x')]), 'ignore_path'),
                 (('tolerance', 2), 'replay_tolerance'),
                 (('name', 'run/../x.json'), 'replay_name'),
                 (('compare', 'pixels'), 'replay_compare')]
        for (key, value), reason in cases:
            changed = copy.deepcopy(spec)
            changed['replay']['files'][0][key] = value
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, reason):
                q.validate(changed, self.modules)
        changed = copy.deepcopy(spec)
        changed['replay']['files'][1]['tolerance'] = 0.1
        with self.assertRaisesRegex(ValueError, 'replay_compare'):
            q.validate(changed, self.modules)

    def training_spec(self, **changes):
        training = dict(experimentLogRunId='TEST-R1', membership=[dict(path=q.relative(self.input), sha256=q.digest(self.input))],
                        initialization=dict(path=q.relative(self.input), sha256=q.digest(self.input)), epochs=2,
                        storageBudgetBytes=200000, acceptanceEvidence='value equals 42', resume='restart')
        training.update(changes)
        return self.spec(authority='training', training=training)

    def test_training_fields(self):
        cases = [(dict(resume='epoch'), 'training_resume'), (dict(epochs=0), 'training_epochs'),
                 (dict(storageBudgetBytes=10), 'training_storage'), (dict(membership=[]), 'training_membership'),
                 (dict(acceptanceEvidence=' '), 'training_acceptance'), (dict(experimentLogRunId='a b'), 'training_log_id')]
        for change, reason in cases:
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, reason):
                q.validate(self.training_spec(**change), self.modules)
        spec = self.training_spec()
        del spec['training']['resume']
        with self.assertRaisesRegex(ValueError, 'training_fields'):
            q.validate(spec, self.modules)

    def test_training_needs_log_entry_and_storage(self):
        log = self.base / 'ExperimentLog.md'
        log.write_text('## TEST-R10 other run\n')
        with mock.patch.object(q, 'EXPERIMENT_LOG', log):
            with self.assertRaisesRegex(ValueError, 'experiment_log_missing'):
                self.submit(self.training_spec())
            log.write_text('## TEST-R1 registered before the run\n')
            with mock.patch.object(q.shutil, 'disk_usage', return_value=mock.Mock(free=q.STORAGE_MARGIN)):
                with self.assertRaisesRegex(ValueError, 'storage_insufficient'):
                    self.submit(self.training_spec())
            self.assertEqual(self.submit(self.training_spec()), 'submitted')
            self.assertEqual(self.run_queue(), [('job-a', 'complete')])
        result = q.load(self.attempt() / 'result.json')
        self.assertEqual(result['training'], dict(experimentLogRunId='TEST-R1', epochs=2, resume='restart',
                                                  storageBudgetBytes=200000))
        self.assertEqual(q.summarize(self.queue)['jobs'][0]['experimentLogRunId'], 'TEST-R1')

    def test_training_pin_change_blocks_execution(self):
        log = self.base / 'ExperimentLog.md'
        log.write_text('TEST-R1\n')
        member = self.base / 'member.json'
        member.write_text('{}')
        with mock.patch.object(q, 'EXPERIMENT_LOG', log):
            self.submit(self.training_spec(membership=[dict(path=q.relative(member), sha256=q.digest(member))]))
            member.write_text('{"changed": true}')
            self.run_queue()
        result = q.load(self.attempt() / 'result.json')
        self.assertEqual((result['status'], result['reason']), ('failed', 'input_changed'))

    def test_summary_reports_each_job(self):
        self.submit(self.spec())
        failing = dict(type='python-callable', steps=['rq_fixture.fail'], outputAttributes=['rq_fixture.OUT'])
        self.submit(self.spec(id='job-b', adapter=failing, limits=dict(timeoutSeconds=20, maxOutputBytes=1000, maxAttempts=1)))
        self.run_queue()
        rows = {r['job']: r for r in q.summarize(self.queue)['jobs']}
        self.assertEqual((rows['job-a']['state'], rows['job-a']['status']), ('complete', 'complete'))
        self.assertEqual((rows['job-b']['state'], rows['job-b']['reason']), ('exhausted', 'process_failed'))
        self.assertTrue((self.queue / 'summary.json').exists())

    def test_summary_extracts_screening_metrics_and_ranks(self):
        self.submit(self.spec(id='job-screen-1'))
        self.submit(self.spec(id='job-screen-2'))
        self.run_queue()

        # Write mock benchmark summaries
        (self.attempt(1, 'job-screen-1') / 'out/benchmark_summary.json').write_text(
            json.dumps({'metrics': {'accuracy': 0.94, 'sample_count': 10}})
        )
        (self.attempt(1, 'job-screen-2') / 'out/benchmark_summary.json').write_text(
            json.dumps({'metrics': {'accuracy': 0.98, 'sample_count': 12}})
        )

        rows = {r['job']: r for r in q.summarize(self.queue)['jobs']}
        self.assertNotIn('screening', rows['job-screen-1'])
        self.assertNotIn('screening', rows['job-screen-2'])
        self.assertEqual(rows['job-screen-2']['evidenceKind'], 'unverified')


if __name__ == '__main__':
    unittest.main()
