"""Read queue evidence into a durable outbox. Remote transport is not configured."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sqlite3
import time

VERSION = 'research-report-event-v1'
IDENT = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$')
STATES = {'pending', 'blocked', 'running', 'stopping', 'cancelled', 'interrupted',
          'failed', 'complete', 'drifted', 'exhausted', 'unknown'}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def identifier(value):
    if not isinstance(value, str) or not IDENT.fullmatch(value):
        raise ValueError('invalid_identifier')
    return value


def public_text(value):
    """Remove paths and credential-like text from bounded display metadata."""
    if not isinstance(value, str):
        return None
    if re.search(r'(?i)(bearer\s|private.key|password\s*[:=]|token\s*[:=]|secret\s*[:=])', value):
        return '[private metadata omitted]'
    value = re.sub(r'(?:https?://|file://|/Users/|/Volumes/|/private/|~/)\S+', '[location omitted]', value)
    return ''.join(c for c in value if c >= ' ' and c != '\x7f')[:600]


def progress(value):
    value = value if isinstance(value, dict) else {}
    result = {'step': public_text(value.get('step')), 'completed': None, 'total': None}
    for key in ('completed', 'total'):
        n = value.get(key)
        if type(n) is int and 0 <= n <= 10**12:
            result[key] = n
    if result['total'] is not None and result['completed'] is not None and result['completed'] > result['total']:
        raise ValueError('invalid_progress')
    return result


def observation(row, spec_hash, attempt, result_hash=None):
    """Whitelist metadata. Do not export paths, logs, predictions, or weights."""
    if not re.fullmatch('[a-f0-9]{64}', spec_hash):
        raise ValueError('invalid_spec_hash')
    state = row.get('state', 'unknown')
    if state not in STATES:
        raise ValueError('unknown_state')
    if type(attempt) is not int or attempt < 0:
        raise ValueError('invalid_attempt')
    if result_hash is not None and not re.fullmatch('[a-f0-9]{64}', result_hash):
        raise ValueError('invalid_result_hash')
    elapsed = row.get('wallSeconds')
    elapsed = elapsed if type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed >= 0 else None
    return dict(job=identifier(row['job']), task=identifier(row['task']), specSHA256=spec_hash,
                attempt=attempt, state=state, approved=row.get('approved') is True,
                question=public_text(row.get('question') or row.get('hypothesis')),
                decision=public_text(row.get('decisionRule')), progress=progress(row.get('progress')),
                blockers=[public_text(str(x)) for x in row.get('requirements', [])[:20]],
                reason=public_text(row.get('reason')), evidence=public_text(row.get('evidenceKind')),
                verification='not-assessed', modelAcceptance='not-assessed', resultSHA256=result_hash,
                dependencies=[identifier(x['job']) for x in row.get('dependencies', [])],
                elapsedSeconds=elapsed, exitCode=row.get('returnCode') if type(row.get('returnCode')) is int else None,
                sourceRevision=None, priority=None, eta=None)


class Outbox:
    """One durable reporting store. It never writes to the execution queue."""
    def __init__(self, path, producer, queue, max_bytes=100_000_000):
        self.producer, self.queue = identifier(producer), identifier(queue)
        self.max_bytes = max_bytes
        path = Path(path)
        if path.is_symlink():
            raise ValueError('linked_store')
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, timeout=5)
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS identity (id INTEGER PRIMARY KEY CHECK(id=1), producer TEXT, queue TEXT);
          CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT UNIQUE,
            payload TEXT NOT NULL, sha256 TEXT NOT NULL, receipt TEXT, delivery TEXT NOT NULL DEFAULT 'pending');
          CREATE TABLE IF NOT EXISTS latest (job TEXT, attempt INTEGER, digest TEXT, PRIMARY KEY(job,attempt));
          CREATE TABLE IF NOT EXISTS heartbeats (id INTEGER PRIMARY KEY CHECK(id=1), observed REAL);
        ''')
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO identity VALUES (1,?,?)', (producer, queue))
        if self.db.execute('SELECT producer,queue FROM identity').fetchone() != (producer, queue):
            self.db.close()
            raise ValueError('store_identity_changed')

    def close(self):
        self.db.close()

    def record(self, rows, now=None):
        now = time.time() if now is None else now
        if not math.isfinite(now) or now < 0:
            raise ValueError('invalid_time')
        created = []
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            used = self.db.execute('SELECT COALESCE(SUM(length(CAST(payload AS BLOB))),0) FROM events').fetchone()[0]
            for row in rows:
                fingerprint = digest(row)
                key = (identifier(row['job']), row['attempt'])
                previous = self.db.execute('SELECT digest FROM latest WHERE job=? AND attempt=?', key).fetchone()
                if previous == (fingerprint,):
                    continue
                seq = self.db.execute('SELECT COALESCE(MAX(seq),0)+1 FROM events').fetchone()[0]
                eid = hashlib.sha256(f'{self.producer}:{self.queue}:{seq}'.encode()).hexdigest()
                event = dict(version=VERSION, producer=self.producer, queue=self.queue, sequence=seq,
                             eventID=eid, observedAt=now, observation=row)
                payload = canonical(event)
                size = len(payload.encode())
                if size > 16_384 or used + size > self.max_bytes:
                    raise ValueError('reporting_capacity_exhausted')
                self.db.execute('INSERT INTO events(seq,event_id,payload,sha256) VALUES (?,?,?,?)',
                                (seq, eid, payload, digest(event)))
                self.db.execute('INSERT OR REPLACE INTO latest VALUES (?,?,?)', (*key, fingerprint))
                created.append(eid)
                used += size
            self.db.execute('INSERT OR REPLACE INTO heartbeats VALUES (1,?)', (now,))
        return created

    def pending(self, limit=100):
        if not 1 <= limit <= 100:
            raise ValueError('invalid_limit')
        return [dict(event=json.loads(p), sha256=h, delivery=d) for p,h,d in self.db.execute(
            'SELECT payload,sha256,delivery FROM events WHERE receipt IS NULL ORDER BY seq LIMIT ?', (limit,))]

    def uncertain(self, event_id):
        with self.db:
            self.db.execute("UPDATE events SET delivery='uncertain' WHERE event_id=? AND receipt IS NULL", (event_id,))

    def acknowledge(self, receipt):
        if set(receipt) != {'eventID', 'sha256', 'durable', 'receiver'} or receipt['durable'] is not True:
            raise ValueError('invalid_receipt')
        identifier(receipt['receiver'])
        with self.db:
            row = self.db.execute('SELECT sha256,receipt FROM events WHERE event_id=?', (receipt['eventID'],)).fetchone()
            if not row or row[0] != receipt['sha256']:
                raise ValueError('receipt_identity_mismatch')
            encoded = canonical(receipt)
            if row[1] is not None and row[1] != encoded:
                raise ValueError('conflicting_receipt')
            self.db.execute("UPDATE events SET receipt=?,delivery='stored' WHERE event_id=?", (encoded, receipt['eventID']))

    def status(self, now=None):
        now = time.time() if now is None else now
        h = self.db.execute('SELECT observed FROM heartbeats WHERE id=1').fetchone()
        return dict(total=self.db.execute('SELECT COUNT(*) FROM events').fetchone()[0],
                    pending=self.db.execute('SELECT COUNT(*) FROM events WHERE receipt IS NULL').fetchone()[0],
                    lastObservedAt=h[0] if h else None, stale=not h or now-h[0] > 30,
                    remoteConfigured=False)


def deliver_once(box, transport):
    """Injected transport only. A lost receipt requires status reconciliation."""
    for item in box.pending():
        eid = item['event']['eventID']
        if item['delivery'] == 'uncertain':
            receipt = transport.status(eid)
            if receipt is None:
                return 'unresolved'
        else:
            box.uncertain(eid)
            try:
                receipt = transport.send(item['event'], item['sha256'])
            except (OSError, TimeoutError):
                return 'uncertain'
        box.acknowledge(receipt)
    return 'stored'


def collect(queue, selected):
    # The existing summary checks evidence and dependencies without writing a summary.
    import research_queue as q
    by_id = {r['job']: r for r in q.summarize(queue, write=False)['jobs']}
    rows = []
    for ident in selected:
        identifier(ident)
        row = by_id[ident]
        job = queue/'jobs'/ident
        spec = q.load(job/'spec.json')
        attempts = q.attempts_of(job)
        if not attempts:
            rows.append(observation(row, q.text_digest(spec), 0))
        for attempt in attempts:
            doc = q.load(attempt/'attempt.json')
            copy = dict(row)
            result_path = attempt/'result.json'
            if result_path.exists():
                result = q.load(result_path)
                copy['state'] = ('drifted' if attempt == attempts[-1] and row['state'] == 'drifted'
                                 else result['status'])
                copy['reason'] = result.get('reason')
                copy['wallSeconds'] = result.get('wallSeconds')
                copy['returnCode'] = result.get('returnCode')
            elif attempt != attempts[-1]:
                copy['state'] = 'interrupted'
            if (attempt/'progress.json').exists():
                copy['progress'] = q.load(attempt/'progress.json')
            else:
                copy.pop('progress', None)
            rows.append(observation(copy, doc['specSHA256'], doc['number'],
                                    q.digest(result_path) if result_path.exists() else None))
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--queue', type=Path, required=True)
    p.add_argument('--store', type=Path, required=True)
    p.add_argument('--job', action='append', required=True)
    p.add_argument('--producer', default='research-host-NUIAK')
    p.add_argument('--queue-id', default='nuiak-research')
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    if not a.store.resolve().is_relative_to(root/'reports/work'):
        p.error('store must stay under reports/work')
    box = Outbox(a.store, a.producer, a.queue_id)
    try:
        created = box.record(collect(a.queue.resolve(), a.job))
        print(canonical(dict(created=len(created), **box.status())))
    finally:
        box.close()


if __name__ == '__main__':
    main()
