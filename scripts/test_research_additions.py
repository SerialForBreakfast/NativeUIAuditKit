"""Verify explicit queue additions and read-only readiness."""
import unittest
from test_research_queue import QueueTests
from research_dashboard_server import Controller
import research_readiness as r
import research_queue as q
from unittest import mock


class AdditionsTests(QueueTests):
    def test_priority_does_not_run_lower_tasks_first(self):
        self.submit(self.spec(id='a-diagnostic'))
        self.submit(self.spec(id='z-hcf', task='HCF371'))
        c=self.control();c.priority_tasks=('HCF371',)
        self.assertEqual(c.next_batch(['a-diagnostic','z-hcf']),['z-hcf'])
        self.assertEqual(c.next_batch(['a-diagnostic']),['a-diagnostic'])

    def test_resume_uses_only_persisted_approvals(self):
        approved = self.spec(); self.submit(approved)
        self.submit(self.spec(id='withdrawn-job'))
        c = self.control()
        c.add([dict(id=approved['id'], sha256=q.text_digest(approved))])
        with mock.patch('research_dashboard_server.threading.Thread') as thread:
            c.start_all(approved_only=True)
            self.assertEqual(thread.call_args.kwargs['args'], (['job-a'],))
            thread.return_value.start.assert_called_once()
        self.assertFalse(c.cancel.is_set())

    def test_resume_rejects_changed_approval_before_start(self):
        spec = self.spec(); self.submit(spec)
        c = self.control(); c.add([dict(id=spec['id'], sha256=q.text_digest(spec))])
        spec['hypothesis'] = 'Changed question'
        q.save(self.queue/'jobs/job-a/spec.json', spec, replace=True)
        with mock.patch('research_dashboard_server.threading.Thread') as thread:
            with self.assertRaisesRegex(ValueError, 'approved_spec_changed'):
                c.start_all(approved_only=True)
            thread.assert_not_called()

    def control(self):
        return Controller(self.queue, self.modules, self.lock)

    def test_add_persists_without_start(self):
        spec = self.spec(); self.submit(spec)
        c = self.control(); c.stop.set()
        c.add([dict(id=spec['id'], sha256=q.text_digest(spec))])
        self.assertFalse(c.busy); self.assertTrue(c.stop.is_set())
        self.assertEqual(self.control().approved(), {spec['id']: q.text_digest(spec)})
        c.add([dict(id=spec['id'], sha256=q.text_digest(spec))])

    def test_bad_hash_and_paths(self):
        spec = self.spec(); self.submit(spec)
        for ident, digest in [('job-a', '0'*64), ('../job-a', q.text_digest(spec))]:
            with self.assertRaises(ValueError):
                self.control().add([dict(id=ident, sha256=digest)])
        self.assertFalse((self.queue/'approved-additions.json').exists())

    def test_readiness_and_incomplete_report(self):
        self.submit(self.spec())
        self.assertTrue(r.check('job-a', self.queue, self.modules)['ready'])
        report = r.report(['job-a'], self.queue, self.modules)
        self.assertFalse(report['executionComplete']); self.assertFalse(report['modelAccepted'])
        self.input.write_text('changed')
        result = r.check('job-a', self.queue, self.modules)
        self.assertFalse(result['ready']); self.assertTrue(result['blockers'][0]['owner'])

    def test_duplicate_report(self):
        with self.assertRaisesRegex(ValueError, 'report_membership'):
            r.report(['job-a', 'job-a'], self.queue, self.modules)

    def test_wrong_production_interpreter(self):
        self.submit(self.spec())
        with mock.patch.object(q, 'QUEUE', self.queue), mock.patch.object(r.sys, 'prefix', '/wrong'):
            result = r.check('job-a', self.queue, self.modules)
        self.assertFalse(result['ready'])
        self.assertIn('runtime_interpreter:use_project_venv', [v['requirement'] for v in result['blockers']])


if __name__ == '__main__':
    unittest.main()
