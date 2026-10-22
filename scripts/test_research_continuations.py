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


    # RECOVERY488: chained chunks and reservation releases.
    def chain_record(self, first, ident='resume-chain'):
        spec = self.spec(id=ident)
        checkpoint = dict(job=first['job'], output='last.pt')
        proof = self.base/(ident+'-qualification.json')
        q.save(proof, dict(q.load(c.checked(first['qualification'])), checkpoint=checkpoint))
        proof_pin = dict(path=q.relative(proof), sha256=q.digest(proof))
        spec['inputs'] += [first['checkpoint'], proof_pin]
        spec['dependencies'] = [dict(job=first['job'], specSHA256=first['specSHA256'], outputs=['last.pt'])]
        self.submit(spec)
        return dict(first, version=c.CHAIN_VERSION, job=ident, specSHA256=q.text_digest(spec),
                    previous=first['job'], checkpoint=checkpoint, qualification=proof_pin)

    def test_chain_reserves_against_original_parent(self):
        first = self.prepare(); c.register(first, self.queue)
        second = self.chain_record(first)
        c.register(second, self.queue)
        self.assertEqual(c.records(self.queue)['resume-chain']['previous'], 'resume-a')
        bad = dict(second, checkpoint=dict(job='other', output='last.pt'))
        with self.assertRaisesRegex(ValueError, 'previous_checkpoint'):
            c.validate(bad, self.queue)
        with self.assertRaisesRegex(ValueError, 'continuation_previous'):
            c.validate(dict(second, previous='missing'), self.queue)

    def test_chain_budget_includes_every_chunk(self):
        first = self.prepare(); c.register(first, self.queue)
        for index in range(3):
            c.register(self.chain_record(first, 'chain-' + str(index)), self.queue)
        with self.assertRaisesRegex(ValueError, 'budget_exhausted'):
            c.register(self.chain_record(first, 'chain-extra'), self.queue)

    def test_release_frees_unstarted_revoked_reservation(self):
        for index in range(4):
            c.register(self.prepare('resume-' + str(index)), self.queue)
        with self.assertRaisesRegex(ValueError, 'budget_exhausted'):
            c.register(self.prepare('resume-extra'), self.queue)
        doc = dict(version=c.RELEASE_VERSION, job='resume-0', reason='Revoked before execution after a source-pin conflict.',
                   specSHA256=c.records(self.queue)['resume-0']['specSHA256'])
        with self.assertRaisesRegex(ValueError, 'still_approved'):
            c.release(doc, self.queue)
        approval.revoke(self.queue, 'resume-0', 'test', 'software revocation')
        c.release(doc, self.queue)
        self.assertIn('resume-0', c.released(self.queue))
        c.register(self.prepare('resume-extra2'), self.queue)
        self.assertIn('resume-0', c.records(self.queue))

    def test_release_refuses_started_job(self):
        record = self.prepare(); c.register(record, self.queue)
        approval.revoke(self.queue, 'resume-a', 'test', 'software revocation')
        (self.queue/'jobs/resume-a/attempts/1').mkdir(parents=True)
        doc = dict(version=c.RELEASE_VERSION, job='resume-a', reason='Revoked before execution after a source-pin conflict.',
                   specSHA256=record['specSHA256'])
        with self.assertRaisesRegex(ValueError, 'release_started'):
            c.release(doc, self.queue)


    def test_finished_sibling_counts_measured_usage(self):
        for index in range(4):
            c.register(self.prepare('resume-' + str(index)), self.queue)
        with self.assertRaisesRegex(ValueError, 'budget_exhausted'):
            c.register(self.prepare('resume-extra'), self.queue)
        # A finished attempt frees the rest of its 20 s reservation. An unfinished attempt does not.
        attempt = self.queue/'jobs/resume-0/attempts/1'
        (attempt/'out').mkdir(parents=True)
        spec = q.load(self.queue/'jobs/resume-0/spec.json')
        self.assertEqual(c.sibling_usage(self.queue/'jobs/resume-0', spec), (20, spec['limits']['maxOutputBytes']))
        q.save(attempt/'result.json', dict(status='failed', reason='evidence_not_read:x', wallSeconds=0.0, outputs=[]))
        self.assertEqual(c.sibling_usage(self.queue/'jobs/resume-0', spec), (0.0, 0))
        c.register(self.prepare('resume-extra2'), self.queue)


if __name__ == '__main__':
    unittest.main()
