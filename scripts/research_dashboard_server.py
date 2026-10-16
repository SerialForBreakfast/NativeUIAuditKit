"""Serve authenticated loopback controls for the existing research queue."""
import argparse
import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import secrets
import signal
import threading
import time
from urllib.parse import parse_qs, urlsplit

import research_queue as q
import research_approval
from generate_research_dashboard import render_html
from research_dashboard_states import annotate


class Controller:
    def __init__(self, queue=q.QUEUE, modules=q.MODULES, lock=None):
        self.queue, self.modules, self.lock = queue, modules, lock
        self.stop = threading.Event()
        self.cancel = threading.Event()
        self.guard = threading.Lock()
        self.current = None
        self.thread = None
        self.error = None
        self.continuous = False
        self.waiting = None
        self.skipped = {}
        self.approvals = self.queue / 'approved-additions.json'
        self.priority_tasks = ()
        # Shared snapshot cache: 1 build at a time, reused by every request until it is stale.
        self.cache = None
        self.cache_ready = threading.Condition()
        self.building = False
        self.invalidated = 0.0
        self.snapshot_id = 0

    def next_batch(self, ready):
        """Recheck priority at each completed job, including continuation chunks."""
        from research_continuations import select
        return select(ready, self.queue, self.priority_tasks)

    def approved(self):
        return research_approval.approved_map(self.queue)

    def add(self, jobs):
        """Approve exact specifications as the maintainer, through the same checks as agent approvals."""
        q.require(isinstance(jobs, list) and len(jobs) == 1, 'one_job_approval_required')
        seen = set()
        for item in jobs:
            q.require(isinstance(item, dict) and set(item) <= {'id', 'sha256', 'reason'} and {'id', 'sha256'} <= set(item),
                      'addition_fields')
            ident = item['id']
            q.require(isinstance(ident, str) and q.ID.fullmatch(ident) and ident not in seen, 'job_id')
            seen.add(ident)
            spec = q.validate(q.load(self.queue / 'jobs' / ident / 'spec.json'), self.modules)
            q.require(q.text_digest(spec) == item['sha256'], 'addition_hash')
        with self.guard:
            for item in jobs:
                research_approval.approve(self.queue, item['id'], 'maintainer',
                                          item.get('reason') or 'Maintainer approval from the dashboard.', self.modules)

    def extend(self, data):
        """Save 1 restart with new limits as the maintainer (EXTENSION408). This does not start the runner."""
        q.require(isinstance(data, dict) and set(data) == {'job', 'timeoutSeconds', 'maxOutputBytes', 'reason'},
                  'extension_fields')
        from research_extensions import save
        with self.guard:
            return save(self.queue, data['job'], data['timeoutSeconds'], data['maxOutputBytes'], data['reason'],
                        'maintainer', self.modules)

    @property
    def busy(self):
        return self.thread is not None and self.thread.is_alive()

    def start(self, ids, retry=False):
        q.require(isinstance(ids, list) and 1 <= len(ids) <= 10 and len(set(ids)) == len(ids), 'batch_size')
        q.require(type(retry) is bool, 'retry_type')
        with self.guard:
            q.require(not self.busy, 'batch_running')
            for id in ids:
                q.require(isinstance(id, str) and q.ID.fullmatch(id), 'job_id')
                job = q.local_path(self.queue, 'jobs/' + id)
                q.require((job / 'spec.json').is_file(), 'unknown_job')
                spec = q.validate(q.load(job / 'spec.json'), self.modules)
                current, attempts = q.state(job)
                q.require(current == 'pending' or retry and current in ('failed', 'cancelled', 'interrupted'), 'job_not_ready')
                q.require(not spec.get('requirements') and 'benchmark_evaluator.run' not in spec['adapter']['steps'], 'job_blocked')
                q.require(self.approved().get(id) == q.text_digest(spec), 'job_not_approved')
                q.verify_pins(spec)
            self.stop.clear()
            self.cancel.clear()
            self.error = None
            self.continuous = False
            self.thread = threading.Thread(target=self._run, args=(ids, retry), daemon=False)
            self.thread.start()

    def start_all(self):
        """Run approved jobs only, until the user stops it. Unapproved jobs never run."""
        with self.guard:
            q.require(not self.busy, 'batch_running')
            ids = sorted(self.approved())
            for ident, digest in self.approved().items():
                q.require(q.text_digest(q.load(self.queue / 'jobs' / ident / 'spec.json')) == digest,
                          'approved_spec_changed')
            self.stop.clear(); self.cancel.clear(); self.error = None
            self.continuous = True; self.skipped = {}
            self.thread = threading.Thread(target=self._continuous, args=(ids,), daemon=False)
            self.thread.start()

    def _continuous(self, ids):
        try:
            initial = {ident: q.text_digest(q.load(self.queue / 'jobs' / ident / 'spec.json')) for ident in ids}
            while not self.stop.is_set():
                ready = []
                with self.guard:
                    selected = dict(initial)
                    for ident, digest in self.approved().items():
                        q.require(ident not in selected or selected[ident] == digest, 'approval_changed')
                        selected[ident] = digest
                for id, digest in selected.items():
                    job = self.queue / 'jobs' / id
                    try:
                        spec = q.validate(q.load(job / 'spec.json'), self.modules)
                        q.require(q.text_digest(spec) == digest, 'approved_spec_changed')
                        state, _ = q.state(job)
                        if state != 'pending':
                            continue
                        from research_readiness import check
                        readiness = check(id, self.queue, self.modules)
                        if not readiness['ready']:
                            self.skipped[id] = readiness['blockers']
                            continue
                        self.skipped.pop(id, None)
                        ready.append(id)
                    except (ValueError, OSError, KeyError) as error:
                        self.skipped[id] = str(error)[:200]
                if ready:
                    self.waiting = None
                    batch = self.next_batch(ready)
                    if not batch:
                        self.waiting = 'Continuation requires valid approval, resume evidence, or remaining budget.'
                        self.stop.wait(5)
                        continue
                    try:
                        q.run(self.queue, self.modules, 5, lock=self.lock, job_ids=batch, control=self)
                        from research_readiness import write_campaign
                        for task in {q.load(self.queue / 'jobs' / ident / 'spec.json')['task'] for ident in batch}:
                            try:
                                write_campaign(task, self.queue, self.modules)
                            except (ValueError, OSError, KeyError, TypeError) as error:
                                self.skipped['report:' + task] = str(error)[:200]
                    except ValueError as error:
                        if str(error) != 'resource_busy':
                            self.error = str(error)[:500]
                            break
                        self.waiting = 'Waiting for the existing runner. Its current job continues.'
                else:
                    self.waiting = 'Runner active — waiting for approved work that passes readiness checks.'
                self.stop.wait(5)
        except Exception as error:
            self.error = str(error)[:500]
        finally:
            self.current = None
            self.waiting = None
            self.continuous = False

    def _run(self, ids, retry):
        try:
            q.run(self.queue, self.modules, len(ids), lock=self.lock, job_ids=ids, retry=retry, control=self)
        except Exception as error:
            self.error = str(error)[:500]
        finally:
            self.current = None

    def invalidate(self):
        """Make the next state request build a fresh snapshot."""
        self.invalidated = time.monotonic()

    def live(self):
        """Runner fields that change often. They are cheap, so every reply reads them again."""
        return dict(busy=self.busy, current=self.current, stopping=self.stop.is_set() and self.busy,
                    error=self.error, continuous=self.continuous, waiting=self.waiting, skipped=dict(self.skipped))

    def fresh(self, cache, key):
        return (cache and cache['started'] >= self.invalidated and cache['key'] == key and
                time.monotonic() - cache['started'] < max(5.0, 2 * cache['seconds']))

    def cached_snapshot(self):
        """Return a shared snapshot record. Rebuild it when it is old, invalidated, or the running job changed.

        A build takes from seconds to minutes on the live queue. Only the first request waits for a build.
        Later requests get the previous snapshot at once, marked stale, while 1 background thread rebuilds it.
        """
        key = (self.busy, self.current)
        with self.cache_ready:
            # An action invalidates the cache; its caller must see the result, so it waits for a new build.
            if self.cache and not self.fresh(self.cache, key) and self.cache['started'] >= self.invalidated:
                if not self.building:
                    self.building = True
                    threading.Thread(target=self.build, args=(key,), daemon=True).start()
                return dict(self.cache, stale=True)
            while True:
                cache = self.cache
                if self.fresh(cache, key):
                    return cache
                if not self.building:
                    self.building = True
                    break
                self.cache_ready.wait(timeout=5)
        return self.build(key)

    def build(self, key):
        """Build 1 snapshot. The caller has set `building`."""
        started = time.monotonic()
        try:
            value = self.snapshot()
        finally:
            with self.cache_ready:
                self.building = False
                self.cache_ready.notify_all()
        with self.cache_ready:
            self.snapshot_id += 1
            self.cache = dict(id=self.snapshot_id, value=value, started=started, key=key,
                              seconds=time.monotonic() - started)
            return self.cache

    def state_reply(self, since=None):
        cache = self.cached_snapshot()
        head = dict(self.live(), snapshotId=cache['id'], buildSeconds=round(cache['seconds'], 2),
                    stale=cache.get('stale', False))
        if since == cache['id']:
            return dict(head, unchanged=True)
        return dict(cache['value'], **head)

    def snapshot(self):
        value = q.summarize(self.queue, write=False)
        from research_continuations import records, eligible, review
        continuations = records(self.queue)
        histories = {}
        keys = {}
        for row in value['jobs']:
            spec = q.load(self.queue / 'jobs' / row['job'] / 'spec.json')
            if row['job'] in continuations:
                blocker = eligible(row['job'], continuations[row['job']], self.queue)
                row['continuation'] = dict(state='resumable' if blocker is None else 'blocked',
                    reason=blocker or 'Runs only after ordinary ready work. Yields after this bounded job.')
            elif row.get('reason') == 'timeout':
                try:
                    decision = review(row['job'], self.queue)
                    row['continuation'] = dict(state='superseded' if decision else 'needs-qualification',
                        reason=decision['reason'] if decision else 'Resume support, unchanged controls, and budget need verification.')
                except (ValueError, OSError, KeyError, TypeError) as error:
                    row['continuation'] = dict(state='blocked', reason=str(error))
            row['specSHA256'] = q.text_digest(spec)
            key = q.text_digest({k: spec.get(k) for k in ('adapter', 'inputs', 'stage', 'authority', 'training')})
            keys[row['job']] = key
            if row['state'] == 'complete' and row['evidenceKind'] != 'placeholder' and row.get('wallSeconds'):
                histories.setdefault(key, []).append(row['wallSeconds'])
        from research_extensions import records as restarts, describe
        saved = restarts(self.queue)
        for row in value['jobs']:
            # Different IDs are comparable only when executable inputs and settings match.
            history = histories.get(keys[row['job']], [])
            if row['job'] in saved:
                record = saved[row['job']]
                row['extendedFrom'] = dict(parent=record['parent'], reason=record['reason'],
                                           queuedAt=record['queuedAt'], estimate=record['estimate'])
            if row['state'] == 'exhausted':
                try:
                    row['extension'] = describe(row['job'], self.queue)
                except (ValueError, OSError, KeyError, TypeError) as error:
                    row['extension'] = dict(blocker=str(error)[:200])
            if row['state'] != 'running' or not row.get('startedAt'):
                continue
            elapsed = time.time() - row['startedAt']
            if len(history) >= 3:
                row['eta'] = dict(low=max(0, min(history)-elapsed), high=max(0, max(history)-elapsed),
                                  samples=len(history), basis='history')
            elif (left := progress_remaining(row.get('progress'), row['startedAt'])) is not None:
                row['eta'] = dict(low=left, high=left, samples=0, basis='progress')
            elif row.get('extendedFrom', {}).get('estimate', {}).get('available'):
                left = max(0, row['extendedFrom']['estimate']['restartSeconds'] - elapsed)
                row['eta'] = dict(low=left, high=left, samples=0, basis='parent-progress')
        value.update(busy=self.busy, current=self.current, stopping=self.stop.is_set() and self.busy, error=self.error,
                     continuous=self.continuous, waiting=self.waiting, skipped=self.skipped)
        return annotate(value, self.queue, self.modules)


def progress_remaining(progress, started, now=None):
    """Extrapolate the remaining seconds linearly from recorded progress units, or return None."""
    if not isinstance(progress, dict):
        return None
    done, total, at = progress.get('completed'), progress.get('total'), progress.get('updatedAt')
    if not all(type(v) in (int, float) for v in (done, total, at)) or done <= 0 or total <= done or at <= started:
        return None
    now = time.time() if now is None else now
    return max(0.0, (at - started) / done * (total - done) - max(0.0, now - at))


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port=0, controller=None):
        self.controller = controller or Controller()
        self.token = secrets.token_urlsafe(32)
        super().__init__(('127.0.0.1', port), Handler)
        self.origin = 'http://127.0.0.1:' + str(self.server_port)

    def server_close(self):
        self.controller.stop.set()
        self.controller.cancel.set()
        if self.controller.thread:
            self.controller.thread.join(timeout=5)
        super().server_close()


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, *args):
        pass  # Do not log authentication headers or tokens.

    def reply(self, status, value, content_type='application/json'):
        body = value.encode() if isinstance(value, str) else json.dumps(value, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type + '; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def valid_host(self):
        host = self.headers.get('Host', '')
        port = str(self.server.server_port)
        return host in (f'127.0.0.1:{port}', f'localhost:{port}')

    def authenticated(self):
        return secrets.compare_digest(self.headers.get('Authorization', ''), 'Bearer ' + self.server.token)

    def do_GET(self):
        if not self.valid_host():
            return self.reply(403, {'error': 'host_refused'})
        url = urlsplit(self.path)
        if self.path == '/':
            return self.reply(200, render_html(self.server.controller.state_reply(), self.server.token), 'text/html')
        if url.path == '/api/state' and self.authenticated():
            since = parse_qs(url.query).get('since', [''])[0]
            return self.reply(200, self.server.controller.state_reply(int(since) if since.isdigit() else None))
        if self.path == '/api/health' and self.authenticated():
            # A light check for scripts. It does not build a queue snapshot.
            c = self.server.controller
            return self.reply(200, dict(pid=os.getpid(), busy=c.busy, current=c.current, continuous=c.continuous,
                                        stopping=c.stop.is_set() and c.busy, waiting=c.waiting, error=c.error))
        self.reply(403, {'error': 'request_refused'})

    def do_POST(self):
        if not self.valid_host() or not self.authenticated() or self.headers.get('Origin') != self.server.origin:
            return self.reply(403, {'error': 'request_refused'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            q.require(0 < size <= 8192, 'request_size')
            q.require(self.headers.get('Content-Type') == 'application/json', 'content_type')
            data = json.loads(self.rfile.read(size))
            q.require(isinstance(data, dict), 'request_object')
            if self.path == '/api/start':
                q.require(set(data) <= {'jobs', 'retry'}, 'request_fields')
                self.server.controller.start(data.get('jobs'), data.get('retry', False))
            elif self.path == '/api/add' and set(data) == {'jobs'}:
                self.server.controller.add(data['jobs'])
            elif self.path == '/api/extend':
                result = self.server.controller.extend(data)
                self.server.controller.invalidate()
                return self.reply(200, {'accepted': True, 'result': result})
            elif self.path == '/api/start-all' and not data:
                self.server.controller.start_all()
            elif self.path == '/api/stop' and not data:
                self.server.controller.stop.set()
            elif self.path == '/api/cancel' and not data:
                q.require(self.server.controller.current is not None, 'no_owned_job')
                self.server.controller.stop.set()
                self.server.controller.cancel.set()
            else:
                raise ValueError('request_refused')
            self.server.controller.invalidate()
            self.reply(200, {'accepted': True})
        except (ValueError, KeyError, TypeError, OSError) as error:
            self.reply(400, {'error': str(error)[:500]})


def interrupt(*_):
    raise KeyboardInterrupt


CONTROL = Path(__file__).resolve().parents[1] / '.build/dashboard/control.json'


def write_control(server):
    """Give local restart scripts the token without a full page render. Only this user can read the file."""
    CONTROL.parent.mkdir(parents=True, exist_ok=True)
    partial = CONTROL.with_name(f'.control.{os.getpid()}.partial')
    fd = os.open(partial, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump(dict(pid=os.getpid(), port=server.server_port, origin=server.origin, token=server.token), f)
    os.replace(partial, CONTROL)


def remove_control():
    try:
        if json.loads(CONTROL.read_text()).get('pid') == os.getpid():
            CONTROL.unlink()
    except (OSError, ValueError):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--resume-approved', action='store_true',
                        help='Resume only persisted approvals. Do not retry failed jobs.')
    parser.add_argument('--priority-task', action='append', default=[],
                        help='Run ready jobs for this task before other ready work.')
    args = parser.parse_args()
    # A background start can inherit an ignored SIGINT. Restore it, and close cleanly on SIGTERM too.
    signal.signal(signal.SIGINT, signal.default_int_handler)
    signal.signal(signal.SIGTERM, interrupt)
    with Server(args.port) as server:
        server.controller.priority_tasks = tuple(args.priority_task)
        if args.resume_approved:
            server.controller.start_all()
        write_control(server)
        print(server.origin, flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            remove_control()


if __name__ == '__main__':
    main()
