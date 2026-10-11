"""Test the research queue with small synthetic modules; no FOCUS code runs."""
import copy
import json
import shutil
import sys
import textwrap
import unittest
import uuid

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
''')


class QueueTests(unittest.TestCase):
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

    def run_queue(self, max_jobs=5):
        return q.run(self.queue, self.modules, max_jobs, sys.executable, self.lock)

    def attempt(self, number=1, job='job-a'):
        return self.queue / 'jobs' / job / 'attempts' / str(number)

    def test_validation_errors(self):
        cases = [
            (dict(version='v0'), 'spec_version'),
            (dict(id='../x'), 'id_format'),
            (dict(authority='unknown'), 'authority_unknown'),
            (dict(authority='training'), 'authority_not_permitted'),
            (dict(authority='capture'), 'authority_not_permitted'),
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
        self.assertEqual(q.state(self.queue / 'jobs/job-a')[0], 'pending')

    def test_interrupted_attempt_is_recorded_then_retried(self):
        self.submit(self.spec())
        self.attempt().mkdir(parents=True)
        q.save(self.attempt() / 'attempt.json', dict(version=q.ATTEMPT_VERSION))
        self.assertEqual(q.state(self.queue / 'jobs/job-a')[0], 'interrupted')
        self.assertEqual(self.run_queue(), [('job-a', 'complete')])
        self.assertEqual(q.load(self.attempt() / 'result.json')['status'], 'interrupted')
        self.assertEqual(q.load(self.attempt(2) / 'result.json')['status'], 'complete')

    def test_failure_keeps_logs_and_stops_at_attempt_limit(self):
        adapter = dict(type='python-callable', steps=['rq_fixture.fail'], outputAttributes=['rq_fixture.OUT'])
        self.submit(self.spec(adapter=adapter))
        self.assertEqual(self.run_queue(), [('job-a', 'failed')])
        self.assertIn('planned failure', (self.attempt() / 'stderr.log').read_text())
        self.assertEqual(self.run_queue(), [('job-a', 'failed')])
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
        self.assertEqual(replay['files'][0]['ignored'], ['seconds'])

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

    def test_summary_reports_each_job(self):
        self.submit(self.spec())
        failing = dict(type='python-callable', steps=['rq_fixture.fail'], outputAttributes=['rq_fixture.OUT'])
        self.submit(self.spec(id='job-b', adapter=failing, limits=dict(timeoutSeconds=20, maxOutputBytes=1000, maxAttempts=1)))
        self.run_queue()
        rows = {r['job']: r for r in q.summarize(self.queue)['jobs']}
        self.assertEqual((rows['job-a']['state'], rows['job-a']['status']), ('complete', 'complete'))
        self.assertEqual((rows['job-b']['state'], rows['job-b']['reason']), ('exhausted', 'process_failed'))
        self.assertTrue((self.queue / 'summary.json').exists())


if __name__ == '__main__':
    unittest.main()
