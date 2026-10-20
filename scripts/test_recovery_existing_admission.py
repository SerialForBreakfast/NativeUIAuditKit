"""Reuse the established gate fixtures for precompiled capture successors."""
from unittest.mock import patch
import unittest
import research_queue as q
import recovery_existing_admission as existing
from experiment_templates import pin
from test_recovery_capture_gate437 import GateTests


class ExistingTests(GateTests):
    def children_plan(self):
        children = self.prepare()[:2]
        refs = []
        for child in children:
            child['dependencies'].append(dict(**self.plan['recovery'], outputs=['recovery.json']))
            path = self.root/(child['id']+'-existing.json')
            q.save(path, child)
            refs.append(pin(path))
        return dict(self.plan, version='existing-capture-recovery-admission-v1', captures=refs)

    def test_existing_successors_reuse_recovery_evidence(self):
        children, recovery = existing.prepare(self.spec, self.queue, self.children_plan())
        self.assertEqual(len(children), 2)
        self.assertEqual(recovery, self.rplan)

    def test_existing_duplicate_rejected(self):
        plan = self.children_plan(); plan['captures'][1] = plan['captures'][0]
        with self.assertRaisesRegex(ValueError, 'existing_gate_duplicates'):
            existing.prepare(self.spec, self.queue, plan)

    def test_existing_started_rejected(self):
        plan = self.children_plan()
        with patch.object(q, 'attempts_of', return_value=[self.attempt]):
            with self.assertRaisesRegex(ValueError, 'existing_gate_started'):
                existing.prepare(self.spec, self.queue, plan)

    def test_serial_retention_dependency_is_anchored(self):
        plan = self.children_plan()
        first = q.load(q.ROOT/plan['captures'][0]['path'])
        path = q.ROOT/plan['captures'][1]['path']
        second = q.load(path)
        second['conditions'] = []
        second['dependencies'] = [dict(job=first['id'],specSHA256=q.text_digest(first),outputs=['retention/compaction.json'])]
        q.save(path,second,replace=True);plan['captures'][1]=pin(path)
        self.assertEqual(len(existing.prepare(self.spec,self.queue,plan)[0]),2)
        second['dependencies'][0]['specSHA256']='0'*64
        q.save(path,second,replace=True);plan['captures'][1]=pin(path)
        with self.assertRaisesRegex(ValueError,'existing_gate_parent_changed'):
            existing.prepare(self.spec,self.queue,plan)


if __name__ == '__main__':
    unittest.main()
