"""Qualify native retained membership without inference."""
import unittest
from unittest.mock import patch
import research_queue as q
import retained_temporal506 as a
from experiment_templates import pin

class RetainedTests(unittest.TestCase):
    def request(self):
        return dict(version='retained-temporal-request-v1',id='temporal506-check',
            fixtureRequest=pin(q.ROOT/'reports/work/SDK501/sdk501-geometry.json'),
            model=pin(q.QUEUE/'jobs/b405-126-r2-notification-42/attempts/1/out/final.pt'))

    def test_preserves_calibration_and_observed_changes(self):
        rows=a.prepare(self.request())
        self.assertEqual(len(rows),4);self.assertEqual(sum(r['changed'] for r in rows),2)
        self.assertEqual({r['role'] for r in rows},{'calibration'})
        self.assertEqual(len({r['group'] for r in rows}),1)

    def test_rejects_role_change(self):
        original=a.audit
        def changed(r):
            d=original(r);d['frames'][0]['role']='train';return d
        with patch.object(a,'audit',side_effect=changed),self.assertRaisesRegex(ValueError,'retained_temporal_role'):
            a.prepare(self.request())
