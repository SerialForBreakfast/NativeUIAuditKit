"""Exercise isolated approval transactions with the resident approval checks."""
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import research_queue as q
import research_approval as approval
import workflow_transaction441 as transaction
from test_research_trust import TrustTests


class TransactionTests(unittest.TestCase):
    setUp = TrustTests.setUp
    pin = TrustTests.pin
    spec = TrustTests.spec

    def entries(self, count=5):
        rows=[]
        for i in range(count):
            spec=self.spec('real_eval', id=f'job-{i}')
            folder=self.queue/'jobs'/spec['id'];folder.mkdir(parents=True)
            q.save(folder/'spec.json',spec)
            rows.append(dict(job=spec['id'],sha256=q.text_digest(spec),approver='test',reason='Qualify exact isolated job approval.'))
        return rows

    def test_five_and_ten_jobs_use_one_write_and_retry_is_noop(self):
        rows=self.entries(10)
        for subset in (rows[:5],rows):
            result=transaction.qualify(self.queue,subset,self.modules)
            self.assertEqual(result['storeWrites'],1)
        before=approval.path(self.queue).read_bytes()
        self.assertEqual(transaction.qualify(self.queue,rows,self.modules)['storeWrites'],0)
        self.assertEqual(before,approval.path(self.queue).read_bytes())
        self.assertEqual(len(approval.load(self.queue)['events']),10)

    def test_matches_individual_checks(self):
        rows=self.entries()
        expected={r['job']:approval.checks(self.queue,r['job'],self.modules,'test')[1] for r in rows}
        result=transaction.qualify(self.queue,rows,self.modules)
        for row in rows:self.assertEqual(result['records'][row['job']]['checks'],expected[row['job']])

    def test_invalid_last_job_leaves_no_partial_approval(self):
        rows=self.entries();rows[-1]['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'transaction_spec_changed'):transaction.qualify(self.queue,rows,self.modules)
        self.assertFalse(approval.path(self.queue).exists())

    def test_failed_publication_then_retry(self):
        rows=self.entries()
        with patch.object(q,'save',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):transaction.qualify(self.queue,rows,self.modules)
        self.assertFalse(approval.path(self.queue).exists())
        transaction.qualify(self.queue,rows,self.modules)
        self.assertEqual(len(approval.load(self.queue)['events']),5)

    def test_revoked_job_never_reapproved(self):
        rows=self.entries();transaction.qualify(self.queue,rows,self.modules)
        approval.revoke(self.queue,rows[0]['job'],'test','preserve revocation')
        before=approval.path(self.queue).read_bytes()
        with self.assertRaisesRegex(ValueError,'transaction_revoked'):transaction.qualify(self.queue,rows,self.modules)
        self.assertEqual(before,approval.path(self.queue).read_bytes())

    def test_duplicates_and_live_queue_rejected(self):
        rows=self.entries()
        with self.assertRaisesRegex(ValueError,'transaction_duplicate_id'):transaction.qualify(self.queue,[rows[0]]*2,self.modules)
        with self.assertRaisesRegex(ValueError,'transaction_live_disabled'):transaction.qualify(q.QUEUE,rows,self.modules)

    def test_storage_failure_preserves_empty_store(self):
        rows=self.entries()
        with patch.object(approval.shutil,'disk_usage',return_value=SimpleNamespace(free=0)):
            with self.assertRaisesRegex(ValueError,'approval_storage_insufficient'):transaction.qualify(self.queue,rows,self.modules)
        self.assertFalse(approval.path(self.queue).exists())

    def test_opt_in_does_not_allow_test_actor_on_live_queue(self):
        rows=self.entries()
        # Rebind the live identity to this disposable queue; never access the real live store.
        with patch.object(q,'QUEUE',self.queue):
            with self.assertRaisesRegex(ValueError,'test_approver_on_live_queue'):
                transaction.qualify(self.queue,rows,self.modules,allow_live=True)
        self.assertFalse(approval.path(self.queue).exists())

    def test_source_change_during_checks_rejects_all(self):
        rows=self.entries();checks=approval.checks;calls=[]
        def change(*args,**kwargs):
            result=checks(*args,**kwargs);calls.append(1)
            if len(calls)==len(rows):
                path=self.modules/'trust_fixture.py';path.write_text(path.read_text()+'\n# changed source\n')
            return result
        with patch.object(approval,'checks',side_effect=change):
            with self.assertRaisesRegex(ValueError,'approval_checks_changed'):transaction.qualify(self.queue,rows,self.modules)
        self.assertFalse(approval.path(self.queue).exists())

    def test_concurrent_duplicate_transactions(self):
        rows=self.entries();errors=[]
        def run():
            try:transaction.qualify(self.queue,rows,self.modules)
            except Exception as error:errors.append(error)
        threads=[threading.Thread(target=run) for _ in range(2)]
        for thread in threads:thread.start()
        for thread in threads:thread.join(35)
        self.assertFalse(any(t.is_alive() for t in threads));self.assertEqual(errors,[])
        self.assertEqual(len(approval.load(self.queue)['events']),5)

    def test_atomic_replace_failure_preserves_existing_store(self):
        rows=self.entries()
        approval.approve(self.queue,rows[0]['job'],'test',rows[0]['reason'],self.modules)
        before=approval.path(self.queue).read_bytes()
        with patch.object(q.os,'replace',side_effect=OSError('replace interrupted')):
            with self.assertRaises(OSError):transaction.qualify(self.queue,rows,self.modules)
        self.assertEqual(before,approval.path(self.queue).read_bytes())
        transaction.qualify(self.queue,rows,self.modules)
        self.assertEqual(len(approval.load(self.queue)['events']),5)

    def test_lost_receipt_after_commit_is_idempotent(self):
        rows=self.entries();save=q.save
        def lost(*args,**kwargs):
            save(*args,**kwargs)
            raise OSError('receipt lost after commit')
        with patch.object(q,'save',side_effect=lost):
            with self.assertRaises(OSError):transaction.qualify(self.queue,rows,self.modules)
        self.assertEqual(transaction.qualify(self.queue,rows,self.modules)['storeWrites'],0)
        self.assertEqual(len(approval.load(self.queue)['events']),5)

    def test_concurrent_revocation_is_not_lost(self):
        rows=self.entries();entered=threading.Event();release=threading.Event();errors=[]
        original=approval.checks
        def held(*args,**kwargs):
            entered.set();self.assertTrue(release.wait(10));return original(*args,**kwargs)
        def run():
            try:transaction.qualify(self.queue,rows,self.modules)
            except Exception as error:errors.append(error)
        with patch.object(approval,'checks',side_effect=held):
            worker=threading.Thread(target=run);worker.start()
            self.assertTrue(entered.wait(10))
            def revoke():
                try:approval.revoke(self.queue,rows[0]['job'],'test','concurrent revocation')
                except Exception as error:errors.append(error)
            revoker=threading.Thread(target=revoke);revoker.start();release.set()
            worker.join(35);revoker.join(35)
        self.assertFalse(worker.is_alive() or revoker.is_alive());self.assertEqual(errors,[])
        doc=approval.load(self.queue)
        self.assertNotIn(rows[0]['job'],doc['jobs'])
        self.assertEqual(doc['events'][-1]['action'],'revoke')

    def test_benchmark_identical_specs(self):
        rows=self.entries(10);samples=[]
        for count in (5,10):
            for mode in ('individual','transaction'):
                # Only this disposable test store is reset. Specifications stay identical.
                if approval.path(self.queue).exists():approval.path(self.queue).unlink()
                started=time.monotonic()
                if mode=='individual':
                    for row in rows[:count]:approval.approve(self.queue,row['job'],'test',row['reason'],self.modules)
                else:transaction.qualify(self.queue,rows[:count],self.modules)
                samples.append(dict(jobs=count,mode=mode,seconds=time.monotonic()-started))
                self.assertEqual(len(approval.load(self.queue)['events']),count)
        print('Isolated small-store benchmark:',samples)


if __name__=='__main__':unittest.main()
