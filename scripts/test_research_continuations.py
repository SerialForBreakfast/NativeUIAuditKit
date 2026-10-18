"""Continuation software tests. Synthetic checkpoints are not model evidence."""
import copy
import sys
import unittest
from unittest import mock
import research_queue as q
import research_approval as approval
import research_continuations as c
from research_dashboard_server import Controller
from test_research_queue import QueueTests


class ContinuationTests(unittest.TestCase):
    setUp = QueueTests.setUp
    tearDown = QueueTests.tearDown
    spec = QueueTests.spec
    write_spec = QueueTests.write_spec
    submit = QueueTests.submit

    def prepare(self, ident='resume-a'):
        parent = self.spec(id='parent')
        if not (self.queue/'jobs/parent').exists():
            self.submit(parent)
        attempt = self.queue/'jobs/parent/attempts/1'
        if not attempt.exists():
            (attempt/'out').mkdir(parents=True)
            q.save(attempt/'out/checkpoint.json', {'completedStep': 1})
            q.save(attempt/'result.json', dict(status='failed', reason='timeout', wallSeconds=20,
                specSHA256=q.text_digest(parent), outputs=[]))
        pin = lambda p: dict(path=q.relative(p), sha256=q.digest(p))
        budget = dict(totalSeconds=100, totalOutputBytes=1_000_000, maxChunkSeconds=20)
        spec = self.spec(id=ident)
        checkpoint = pin(attempt/'out/checkpoint.json')
        parent_result = pin(attempt/'result.json')
        proof = self.base/(ident+'-qualification.json')
        q.save(proof, dict(version='resume-qualification-v1', passed=True, checkpoint=checkpoint,
            adapter=spec['adapter'], preservesControls=True, budget=budget, parentResult=parent_result))
        spec['inputs'] += [checkpoint, pin(proof)]
        self.submit(spec)
        return dict(version=c.VERSION, job=ident, specSHA256=q.text_digest(spec), parent='parent', parentAttempt=1,
            parentResult=parent_result, checkpoint=checkpoint, qualification=pin(proof),
            reason='Continue the remaining software fixture steps.', budget=budget)

    def test_priority_and_real_execution_once(self):
        record = self.prepare(); c.register(record, self.queue)
        self.submit(self.spec(id='new-work'))
        control = Controller(self.queue, self.modules, self.lock)
        self.assertEqual(control.next_batch(['resume-a', 'new-work']), ['new-work'])
        before = q.digest(c.checked(record['checkpoint']))
        for ident in ('new-work', 'resume-a'):
            self.assertEqual(q.run(self.queue, self.modules, 1, sys.executable, self.lock,
                job_ids=control.next_batch([ident])), [(ident, 'complete')])
        self.assertEqual(control.next_batch(['resume-a']), [])
        self.assertEqual(q.digest(c.checked(record['checkpoint'])), before)
        self.assertEqual(len(q.attempts_of(self.queue/'jobs/resume-a')), 1)

    def test_new_priority_between_chunks(self):
        c.register(self.prepare(), self.queue)
        c.register(self.prepare('resume-b'), self.queue)
        control = Controller(self.queue, self.modules, self.lock)
        self.assertEqual(control.next_batch(['resume-a', 'resume-b']), ['resume-a'])
        self.submit(self.spec(id='urgent', task='URGENT'))
        control.priority_tasks = ('URGENT',)
        self.assertEqual(control.next_batch(['resume-b', 'urgent']), ['urgent'])

    def test_restart_and_duplicate_registration(self):
        record=self.prepare(); c.register(record,self.queue); c.register(record,self.queue)
        self.assertEqual(Controller(self.queue,self.modules,self.lock).next_batch(['resume-a']), ['resume-a'])
        self.assertEqual(len(c.records(self.queue)),1)

    def test_revocation_blocks(self):
        record=self.prepare(); c.register(record,self.queue)
        approval.revoke(self.queue,'resume-a','test','software revocation')
        self.assertEqual(c.select(['resume-a'],self.queue),[])

    def test_checkpoint_mutation_blocks(self):
        record=self.prepare(); c.register(record,self.queue)
        c.checked(record['checkpoint']).write_text('changed')
        self.assertEqual(c.select(['resume-a'],self.queue),[])

    def test_budget_expansion_rejected(self):
        record=self.prepare(); record['budget']['totalSeconds']=200
        with self.assertRaisesRegex(ValueError,'budget_not_pinned'):c.register(record,self.queue)

    def test_siblings_reserve_worst_case(self):
        for index in range(4):c.register(self.prepare('resume-'+str(index)),self.queue)
        with self.assertRaisesRegex(ValueError,'budget_exhausted'):
            c.register(self.prepare('resume-extra'),self.queue)

    def test_invalid_parent_is_not_resumable(self):
        record=self.prepare()
        path=c.checked(record['parentResult']); result=q.load(path); result['reason']='process_failed'
        q.save(path,result,replace=True)
        record['parentResult']['sha256']=q.digest(path)
        with self.assertRaisesRegex(ValueError,'not_exhausted'):c.register(record,self.queue)
        self.assertEqual(c.inventory(self.queue)['jobs'][0]['state'],'not-resumable')

    def test_immutable_registration(self):
        record=self.prepare(); c.register(record,self.queue)
        changed=copy.deepcopy(record); changed['reason']='A changed explanation for the same continuation.'
        with self.assertRaisesRegex(ValueError,'immutable'):c.register(changed,self.queue)

    def test_missing_proof_and_unknown_version(self):
        record=self.prepare(); record['version']='unknown'
        with self.assertRaisesRegex(ValueError,'version'):c.register(record,self.queue)
        record['version']=c.VERSION; c.checked(record['qualification']).unlink()
        self.assertEqual(c.eligible('resume-a',record,self.queue),'continuation_input_changed')


if __name__ == '__main__':
    unittest.main()
