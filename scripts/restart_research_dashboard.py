#!/usr/bin/env python3
"""Safely stop the research dashboard server and start it again with the project interpreter.

Order of operations:
1. Check the project interpreter and that the new server code imports. A broken edit stops the restart here.
2. Find dashboard servers on the port. Refuse if another program holds the port.
3. Refuse if a job holds an active lease (unless --wait or --cancel-running).
   Ask the server to stop after its current job, so it starts no new job.
4. Interrupt the server process, so that it closes cleanly. Use SIGTERM and SIGKILL only if it does not exit.
5. Start a detached server, write its PID and log under .build/dashboard/, and check that it answers.

Examples:
  .venv-yolo/bin/python scripts/restart_research_dashboard.py --priority-task TEMPLATE395
  .venv-yolo/bin/python scripts/restart_research_dashboard.py --wait 3600   # wait for the running job
  .venv-yolo/bin/python scripts/restart_research_dashboard.py --stop        # stop only
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / 'scripts/research_dashboard_server.py'
PYTHON = ROOT / '.venv-yolo/bin/python'
QUEUE = ROOT / 'reports/work/research-queue'
STATE = ROOT / '.build/dashboard'
MARKER = 'research_dashboard_server'
DEFAULT_PORT = 8765


class Refused(Exception):
    """A safety check failed. Nothing more is changed."""


def say(text):
    print(time.strftime('%H:%M:%S'), text, flush=True)


# --- Process discovery -------------------------------------------------------

def processes():
    """Return [(pid, command)] for this user's processes."""
    out = subprocess.run(['ps', '-x', '-o', 'pid=,uid=,command='], capture_output=True, text=True, check=True).stdout
    rows = []
    for line in out.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) == 3 and parts[0].isdigit() and parts[1] == str(os.getuid()):
            rows.append((int(parts[0]), parts[2]))
    return rows


def port_of(command):
    match = re.search(r'--port[= ](\d+)', command)
    return int(match.group(1)) if match else DEFAULT_PORT


def ancestors():
    """Return this process and its parents. A shell that started this script is never a target."""
    parents = {pid: ppid for pid, ppid in (map(int, line.split()) for line in subprocess.run(
        ['ps', '-x', '-o', 'pid=,ppid='], capture_output=True, text=True, check=True).stdout.splitlines() if line.strip())}
    chain, pid = set(), os.getpid()
    while pid and pid not in chain:
        chain.add(pid)
        pid = parents.get(pid)
    return chain


def dashboards(port):
    """Dashboard server processes for this port."""
    skip = ancestors()
    return [(pid, cmd) for pid, cmd in processes() if pid not in skip and is_server(cmd) and port_of(cmd) == port]


def is_server(command):
    """Match only a Python interpreter whose script argument is the server file.

    A shell, editor, or log viewer whose command text names the file does not match.
    """
    words = command.split()
    if not words or not re.fullmatch(r'python[0-9.]*', Path(words[0]).name, re.IGNORECASE):
        return False
    script = next((word for word in words[1:] if not word.startswith('-')), '')
    return Path(script).name == MARKER + '.py'


def listeners(port):
    out = subprocess.run(['lsof', '-nP', f'-iTCP:{port}', '-sTCP:LISTEN', '-t'], capture_output=True, text=True).stdout
    return sorted({int(p) for p in out.split() if p.isdigit()})


def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


# --- Server API --------------------------------------------------------------

CONTROL = STATE / 'control.json'


class Api:
    """Use the server's own loopback controls.

    Newer servers write their token to a private control file. For an older server, the token comes from its page.
    That page builds a full queue snapshot, which can take minutes on a busy server.
    """

    def __init__(self, port, pid, page_timeout, allow_page=True):
        self.origin = f'http://127.0.0.1:{port}'
        self.token = None
        try:
            control = json.loads(CONTROL.read_text())
            if control.get('pid') == pid and control.get('port') == port:
                self.token = control['token']
        except (OSError, ValueError, KeyError):
            pass
        if self.token is None and not allow_page:
            raise Refused('The control file is not ready.')
        if self.token is None:
            say(f'Reading the control token from the server page. This can take up to {page_timeout} s.')
            page = self._open(urllib.request.Request(self.origin + '/'), page_timeout).decode()
            match = re.search(r'const TOKEN=("[^"\n]*");', page)
            if not match or not json.loads(match.group(1)):
                raise Refused('The server page has no control token. Is it a dashboard server?')
            self.token = json.loads(match.group(1))

    @staticmethod
    def _open(request, timeout):
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()

    def health(self):
        """Return the light runner state, or None if the server is older than /api/health."""
        request = urllib.request.Request(self.origin + '/api/health', headers={'Authorization': 'Bearer ' + self.token})
        try:
            return json.loads(self._open(request, 30))
        except urllib.error.HTTPError as error:
            if error.code == 403:
                return None
            raise

    def post(self, name):
        request = urllib.request.Request(self.origin + '/api/' + name, data=b'{}', method='POST', headers={
            'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json', 'Origin': self.origin})
        try:
            return json.loads(self._open(request, 60))
        except urllib.error.HTTPError as error:
            raise Refused(f'The server refused /api/{name}: {error.read().decode()[:300]}')


def locked_attempts():
    """Return jobs whose attempt holds an active lease. This check does not use the server."""
    found = []
    for lock in QUEUE.glob('jobs/*/attempts/*/active.lock'):
        if (lock.parent / 'result.json').exists():
            continue
        with lock.open('a+') as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(f, fcntl.LOCK_UN)
            except BlockingIOError:
                found.append(lock.parent.parent.parent.name)
    return found


# --- Steps -------------------------------------------------------------------

def preflight(args):
    if not ROOT.is_dir() or not SERVER.is_file():
        raise Refused(f'The project is not available at {ROOT}. Is the training drive mounted?')
    if not args.stop:
        if not os.access(PYTHON, os.X_OK):
            raise Refused(f'The project interpreter is missing: {PYTHON}')
        # Import the new code before teardown. A syntax or import error keeps the old server running.
        check = subprocess.run([str(PYTHON), '-B', '-c', 'import research_dashboard_server'], cwd=ROOT,
                               env=dict(os.environ, PYTHONPATH=str(ROOT / 'scripts')),
                               capture_output=True, text=True, timeout=120)
        if check.returncode != 0:
            raise Refused('The new server code does not import. The old server stays running.\n' + check.stderr[-2000:])
        say('Preflight passed: the interpreter and the server code import.')


def drain(port, pid, args):
    """Stop the runner after its current job. Refuse to interrupt a running job unless told to."""
    jobs = locked_attempts()
    if jobs and not (args.wait or args.cancel_running):
        raise Refused(f'Job {", ".join(jobs)} is running. Nothing changed. Use --wait SECONDS to restart after it '
                      'ends, or --cancel-running to cancel it.')
    try:
        api = Api(port, pid, args.page_timeout)
    except (urllib.error.URLError, OSError, ValueError) as error:
        if jobs:
            raise Refused(f'The server does not answer ({error}) while {", ".join(jobs)} runs. Nothing changed.')
        say(f'WARNING: the server does not answer ({error}). No job runs now, so the restart continues. '
            'A job that starts in the next moment is cancelled by the shutdown.')
        return
    api.post('stop')
    say('Asked the runner to stop after the current job. It starts no new job.')
    if jobs and args.cancel_running:
        api.post('cancel')
        say(f'Cancelled {", ".join(jobs)}. The attempt records the cancellation.')
    deadline = time.monotonic() + max(args.wait, 60)
    last = time.monotonic()
    while time.monotonic() < deadline:
        jobs = locked_attempts()
        state = api.health() if not jobs else None
        if not jobs and (state is None or not state.get('busy')):
            if state is None:
                time.sleep(6)  # An older server has no /api/health. Its idle loop checks the stop flag every 5 s.
            say('The runner stopped.')
            return
        if time.monotonic() - last > 60:
            say(f'Waiting for {", ".join(jobs) or "the runner"} to finish.')
            last = time.monotonic()
        time.sleep(3)
    raise Refused('The runner is still busy after the wait. It stays in the stopping state and starts no new job. '
                  'Run this script again later, or use --cancel-running.')


def terminate(pid):
    """Interrupt first, so that the server closes cleanly. Escalate only if it does not exit."""
    for sig, seconds in ((signal.SIGINT, 20), (signal.SIGTERM, 10), (signal.SIGKILL, 5)):
        if not alive(pid):
            return
        say(f'Sending {sig.name} to {pid}.')
        try:
            os.kill(pid, sig)
        except ProcessLookupError:
            return
        end = time.monotonic() + seconds
        while time.monotonic() < end and alive(pid):
            time.sleep(0.2)
    if alive(pid):
        raise Refused(f'Process {pid} does not exit after SIGKILL.')


def teardown(port, args):
    servers = dashboards(port)
    holders = listeners(port)
    strangers = [pid for pid in holders if pid not in {p for p, _ in servers}]
    if strangers:
        raise Refused(f'Port {port} belongs to a process that is not a dashboard server: {strangers}. Nothing changed.')
    if not servers:
        say(f'No dashboard server runs on port {port}.')
        return
    for pid, cmd in servers:
        say(f'Found dashboard server {pid}: {cmd}')
    if args.dry_run:
        return
    if len(holders) == 1:
        drain(port, holders[0], args)
    elif locked_attempts() and not args.cancel_running:
        raise Refused('A job holds a lease, and the server cannot be asked to stop. Nothing changed.')
    for pid, _ in servers:
        terminate(pid)
    end = time.monotonic() + 15
    while listeners(port) and time.monotonic() < end:
        time.sleep(0.2)
    if listeners(port):
        raise Refused(f'Port {port} is still in use after teardown.')
    say('Teardown complete.')


def launch(port, args):
    command = [str(PYTHON), '-B', str(SERVER.relative_to(ROOT)), '--port', str(port)]
    if not args.no_resume:
        command.append('--resume-approved')
    for task in args.priority_task:
        command += ['--priority-task', task]
    if args.dry_run:
        say('Would start: ' + ' '.join(command))
        return
    STATE.mkdir(parents=True, exist_ok=True)
    log = STATE / 'server.log'
    with log.open('a') as out:
        out.write(f'\n=== {time.strftime("%Y-%m-%d %H:%M:%S")} start: {" ".join(command)}\n')
        out.flush()
        process = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT,
                                   start_new_session=True)
    (STATE / 'server.pid').write_text(f'{process.pid}\n')
    say(f'Started server {process.pid}. Log: {log.relative_to(ROOT)}')
    deadline = time.monotonic() + args.start_timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            tail = log.read_text().splitlines()[-30:]
            raise Refused(f'The new server exited with code {process.returncode}.\n' + '\n'.join(tail))
        try:
            state = Api(port, process.pid, 0, allow_page=False).health()
        except (urllib.error.URLError, OSError, ValueError, Refused):
            time.sleep(1)
            continue
        if state is None:
            raise Refused('The new server has no /api/health endpoint. Check the server code.')
        say(f'Server answers at http://127.0.0.1:{port}/ — runner {"active" if state.get("busy") else "idle"}.')
        if state.get('error'):
            say('Runner error: ' + state['error'])
        return
    raise Refused(f'The new server ({process.pid}) does not answer after {args.start_timeout} s. '
                  f'It is still running. Check {log.relative_to(ROOT)}.')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--port', type=int, default=DEFAULT_PORT)
    parser.add_argument('--priority-task', action='append', default=[], help='Passed to the server. Repeat as needed.')
    parser.add_argument('--no-resume', action='store_true', help='Start without --resume-approved. The runner stays idle.')
    parser.add_argument('--wait', type=int, default=0, metavar='SECONDS',
                        help='If a job runs, stop the runner after it and wait up to SECONDS.')
    parser.add_argument('--cancel-running', action='store_true', help='Cancel a running job. Its work is lost.')
    parser.add_argument('--stop', action='store_true', help='Stop the server only. Do not start a new one.')
    parser.add_argument('--dry-run', action='store_true', help='Show what would happen. Change nothing.')
    parser.add_argument('--start-timeout', type=int, default=120, metavar='SECONDS')
    parser.add_argument('--page-timeout', type=int, default=600, metavar='SECONDS',
                        help='Time limit to read the token from an older server page.')
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535 or args.wait < 0:
        parser.error('Use a port from 1024 to 65535 and a wait of 0 or more seconds.')
    try:
        preflight(args)
        teardown(args.port, args)
        if args.stop:
            if not args.dry_run:
                (STATE / 'server.pid').unlink(missing_ok=True)
        else:
            launch(args.port, args)
    except Refused as error:
        say('REFUSED: ' + str(error))
        return 2
    except KeyboardInterrupt:
        say('Interrupted. Check the server state before you run this script again.')
        return 130
    except (OSError, subprocess.SubprocessError) as error:
        say(f'FAILED: {type(error).__name__}: {error}')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
