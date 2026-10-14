"""The groomer reports only. It never creates, approves, moves, or deletes jobs."""
import json
import unittest

import backlog_groomer as bg
import research_queue as q
from test_research_queue import QueueTests


class BacklogGroomerTests(QueueTests):
    def snapshot(self):
        return sorted(str(p.relative_to(self.queue)) for p in self.queue.rglob('*'))

    def test_report_changes_nothing(self):
        self.submit(self.spec(), approve=False)
        before = self.snapshot()
        report = bg.queue_report(self.queue, self.modules)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.queue / 'approved-additions.json').exists())
        # An unapproved job is pending, not ready.
        self.assertEqual((report['readyJobs'], report['counts']), ([], {'pending': 1}))
        self.assertTrue(report['starvation'])

    def test_empty_queue_reports_starvation(self):
        report = bg.queue_report(self.queue, self.modules)
        self.assertTrue(report['starvation'])
        self.assertEqual(report['counts'], {})
        self.assertFalse((self.queue / 'jobs').exists())

    def test_is_proposal_detection(self):
        self.assertTrue(bg.is_proposal({"planningOnly": True}))
        self.assertTrue(bg.is_proposal({"requirements": ["Remote-TTR: test requirement"]}))
        self.assertTrue(bg.is_proposal({"requirements": [{"owner": "external producer"}]}))
        self.assertFalse(bg.is_proposal({"requirements": []}))
        self.assertFalse(bg.is_proposal({}))

    def test_no_write_or_approval_api(self):
        for name in ('sync_approvals', 'groom_backlog', 'quarantine_superseded', 'segregate_proposals'):
            self.assertFalse(hasattr(bg, name), name)


if __name__ == "__main__":
    unittest.main()
