"""Offline reporting tests. These do not qualify a remote service."""
import copy
import json
from pathlib import Path
import tempfile
import sqlite3
import unittest

import research_reporting as r


class Receiver:
    def __init__(self):
        self.events = {}
        self.drop = False
        self.sends = 0

    def send(self, event, sha):
        self.sends += 1
        if event['version'] != r.VERSION or r.digest(event) != sha:
            raise ValueError('invalid_event')
        previous = self.events.get(event['eventID'])
        if previous and previous['sha256'] != sha:
            raise ValueError('conflict')
        receipt = dict(eventID=event['eventID'], sha256=sha, durable=True, receiver='test-receiver')
        self.events[event['eventID']] = receipt
        if self.drop:
            self.drop = False
            raise TimeoutError('receipt lost')
        return receipt

    def status(self, ident):
        return self.events.get(ident)


class ReportingTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]/'.build/debug-output'
        root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.path = Path(self.temp.name)/'outbox.sqlite'
        self.box = r.Outbox(self.path, 'test-producer', 'test-queue')
        self.row = r.observation(dict(job='test-job', task='TEST', state='running',
                                     progress={'step':'score','completed':2}), 'a'*64, 1)

    def tearDown(self):
        self.box.close()
        self.temp.cleanup()

    def test_restart_and_repeat_snapshot(self):
        ids = self.box.record([self.row], 100)
        self.box.close()
        self.box = r.Outbox(self.path, 'test-producer', 'test-queue')
        self.assertEqual(self.box.record([self.row], 101), [])
        self.assertEqual(self.box.pending()[0]['event']['eventID'], ids[0])

    def test_changed_progress_appends(self):
        self.box.record([self.row], 100)
        other = copy.deepcopy(self.row)
        other['progress']['completed'] = 3
        self.box.record([other], 101)
        self.assertEqual([p['event']['sequence'] for p in self.box.pending()], [1,2])

    def test_lost_receipt_restart_reconciles(self):
        self.box.record([self.row], 100)
        remote = Receiver(); remote.drop = True
        self.assertEqual(r.deliver_once(self.box, remote), 'uncertain')
        self.box.close(); self.box = r.Outbox(self.path, 'test-producer', 'test-queue')
        self.assertEqual(r.deliver_once(self.box, remote), 'stored')
        self.assertEqual(remote.sends, 1)
        self.assertEqual(self.box.status(100)['pending'], 0)

    def test_unknown_delivery_does_not_resend(self):
        self.box.record([self.row], 100)
        self.box.uncertain(self.box.pending()[0]['event']['eventID'])
        remote = Receiver()
        self.assertEqual(r.deliver_once(self.box, remote), 'unresolved')
        self.assertEqual(remote.sends, 0)

    def test_bad_receipt_keeps_event(self):
        self.box.record([self.row], 100)
        item = self.box.pending()[0]
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            self.box.acknowledge(dict(eventID=item['event']['eventID'], sha256='b'*64,
                                      durable=True, receiver='test-receiver'))
        self.assertEqual(self.box.status(100)['pending'], 1)

    def test_nondurable_receipt_rejected(self):
        with self.assertRaisesRegex(ValueError, 'invalid_receipt'):
            self.box.acknowledge(dict(eventID='x',sha256='a'*64,durable=False,receiver='test'))

    def test_capacity_rolls_back_whole_snapshot(self):
        self.box.max_bytes = 1
        with self.assertRaisesRegex(ValueError, 'capacity'):
            self.box.record([self.row], 100)
        self.assertEqual(self.box.status(100)['total'], 0)
        self.assertTrue(self.box.status(100)['stale'])

    def test_identity_change_rejected(self):
        with self.assertRaisesRegex(ValueError, 'identity_changed'):
            r.Outbox(self.path, 'other-producer', 'test-queue')

    def test_stale_is_not_completion(self):
        self.box.record([self.row], 100)
        self.assertTrue(self.box.status(131)['stale'])
        self.assertEqual(self.box.pending()[0]['event']['observation']['state'], 'running')

    def test_unknown_total_no_eta(self):
        self.assertIsNone(self.row['progress']['total'])
        self.assertIsNone(self.row['eta'])

    def test_invalid_progress(self):
        with self.assertRaisesRegex(ValueError, 'invalid_progress'):
            r.progress({'completed':4,'total':3})

    def test_completion_does_not_accept_model(self):
        self.row['state'] = 'complete'
        self.box.record([self.row], 100)
        row = self.box.pending()[0]['event']['observation']
        self.assertEqual(row['modelAcceptance'], 'not-assessed')

    def test_private_metadata_removed(self):
        self.assertEqual(r.public_text('token=secret'), '[private metadata omitted]')
        self.assertNotIn('/Users/', r.public_text('source /Users/test/private/path'))

    def test_hostile_text_remains_data(self):
        self.row['question'] = '<script>alert(1)</script>'
        self.box.record([self.row], 100)
        self.assertEqual(self.box.pending()[0]['event']['observation']['question'], self.row['question'])

    def test_duplicate_receipt_is_idempotent(self):
        self.box.record([self.row], 100)
        item = self.box.pending()[0]
        receipt = Receiver().send(item['event'], item['sha256'])
        self.box.acknowledge(receipt); self.box.acknowledge(receipt)
        self.assertEqual(self.box.status(100)['total'], 1)

    def test_conflicting_duplicate_receiver(self):
        self.box.record([self.row], 100)
        item = self.box.pending()[0]; remote = Receiver()
        remote.send(item['event'], item['sha256'])
        changed = copy.deepcopy(item['event']); changed['observedAt'] += 1
        with self.assertRaisesRegex(ValueError, 'conflict'):
            remote.send(changed, r.digest(changed))

    def test_new_attempt_stays_separate(self):
        self.box.record([self.row], 100)
        row = dict(self.row, attempt=2)
        self.box.record([row], 101)
        self.assertEqual(len(self.box.pending()), 2)

    def test_unknown_state_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unknown_state'):
            r.observation(dict(job='j',task='t',state='invented'), 'a'*64, 1)

    def test_receiver_restart_keeps_duplicate_identity(self):
        # This is a local test double, not the worker host receiver.
        path = Path(self.temp.name)/'receiver.sqlite'
        self.box.record([self.row], 100)
        item = self.box.pending()[0]
        db = sqlite3.connect(path)
        db.execute('CREATE TABLE receipts (id TEXT PRIMARY KEY, hash TEXT)')
        db.execute('INSERT INTO receipts VALUES (?,?)', (item['event']['eventID'],item['sha256']))
        db.commit(); db.close()
        db = sqlite3.connect(path)
        self.assertEqual(db.execute('SELECT hash FROM receipts WHERE id=?', (item['event']['eventID'],)).fetchone(),
                         (item['sha256'],))
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute('INSERT INTO receipts VALUES (?,?)', (item['event']['eventID'],item['sha256']))
        db.close()

    def test_snapshot_transaction_survives_crash(self):
        import subprocess, sys
        code = """import os,sqlite3,sys
db=sqlite3.connect(sys.argv[1]);db.execute('BEGIN IMMEDIATE')
db.execute("INSERT INTO latest VALUES ('unfinished',1,'bad')")
os._exit(1)
"""
        run = subprocess.run([sys.executable,'-c',code,str(self.path)], check=False)
        self.assertEqual(run.returncode, 1)
        self.assertIsNone(self.box.db.execute("SELECT * FROM latest WHERE job='unfinished'").fetchone())

    def test_read_only_queue_collection(self):
        from unittest.mock import patch
        import research_queue as q
        queue = Path(self.temp.name)/'queue'
        job = queue/'jobs'/'test-job'; job.mkdir(parents=True)
        spec = {'id':'test-job'}
        (job/'spec.json').write_text(json.dumps(spec))
        source = {p:p.read_bytes() for p in queue.rglob('*') if p.is_file()}
        row = dict(job='test-job', task='TEST', state='pending')
        with patch.object(q,'summarize',return_value={'jobs':[row]}) as summary:
            items = r.collect(queue,['test-job'])
        summary.assert_called_once_with(queue,write=False)
        self.assertEqual(items[0]['attempt'],0)
        self.assertEqual(source,{p:p.read_bytes() for p in queue.rglob('*') if p.is_file()})


if __name__ == '__main__':
    unittest.main()
