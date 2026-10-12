"""Queued, resumable research jobs with standard results (ADR-0026).

Commands: submit SPEC, run [--max-jobs N], status, summarize.
The queue is not a service. Each `run` executes a bounded number of jobs, then stops.
"""
import argparse
import contextlib
import fcntl
import hashlib
import importlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / 'reports/work/research-queue'
MODULES = ROOT / 'scripts'
SPEC_VERSION = 'research-spec-v1'
ATTEMPT_VERSION = 'research-attempt-v1'
RESULT_VERSION = 'research-result-v1'
SUMMARY_VERSION = 'research-summary-v1'
KINDS = {'replay', 'screen', 'confirm'}
AUTHORITIES = {'diagnostic', 'training', 'capture', 'export', 'promotion'}
PERMITTED = {'diagnostic', 'training'}
TRAINING_FIELDS = {'experimentLogRunId', 'membership', 'initialization', 'epochs', 'storageBudgetBytes',
                   'acceptanceEvidence', 'resume'}
EXPERIMENT_LOG = ROOT / 'Research/ExperimentLog.md'
STORAGE_MARGIN = 1 << 30
ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}')
NAME = re.compile(r'[A-Za-z_][A-Za-z0-9_]{0,63}')
FILE = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}')
HASH = re.compile(r'[0-9a-f]{64}')
FIELD = re.compile(r'[A-Za-z0-9_]{1,64}(\[\])?')


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def text_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def save(path, value, replace=False):
    """Write JSON atomically. Refuse to replace unless asked."""
    path = Path(path)
    require(replace or not path.exists(), 'output_collision')
    tmp = path.with_name(f'.{path.name}.{uuid.uuid4().hex}.partial')
    with tmp.open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    if replace:
        os.replace(tmp, path)
    else:
        os.link(tmp, path)
        tmp.unlink()


def load(path):
    return json.loads(Path(path).read_text())


def local_path(root, rel):
    require(isinstance(rel, str) and rel and not rel.startswith('/') and '\\' not in rel, 'unsafe_path')
    require('..' not in Path(rel).parts, 'unsafe_path')
    path = root / rel
    current = path
    while current != root and root in current.parents:
        require(not current.is_symlink(), 'symlink_refused')
        current = current.parent
    return path


def check_pin(pin):
    require(isinstance(pin, dict) and set(pin) == {'path', 'sha256'}, 'pin_fields')
    require(isinstance(pin['sha256'], str) and HASH.fullmatch(pin['sha256']), 'pin_hash_format')
    return pin


def split_target(value, module_dir):
    require(isinstance(value, str) and value.count('.') == 1, 'target_format')
    module, name = value.split('.')
    require(NAME.fullmatch(module) and NAME.fullmatch(name), 'target_format')
    require((module_dir / f'{module}.py').is_file(), 'module_not_allowlisted')
    return module, name


def check_name(value):
    """Accept a relative output name, such as `run/fit.json`."""
    require(isinstance(value, str) and value and all(FILE.fullmatch(p) for p in value.split('/')), 'replay_name')
    require('..' not in value.split('/'), 'replay_name')
    return value


def check_ignore(path):
    parts = path.split('.') if isinstance(path, str) else []
    require(parts and all(FIELD.fullmatch(p) for p in parts) and not parts[-1].endswith('[]'), 'ignore_path')


def validate_training(spec):
    """Require the standing-approval fields for training jobs."""
    if spec['authority'] != 'training':
        require('training' not in spec, 'training_only_for_training_jobs')
        return
    training = spec.get('training')
    require(isinstance(training, dict) and set(training) == TRAINING_FIELDS, 'training_fields')
    require(isinstance(training['experimentLogRunId'], str) and ID.fullmatch(training['experimentLogRunId']),
            'training_log_id')
    require(isinstance(training['membership'], list) and training['membership'], 'training_membership')
    for pin in training['membership']:
        local_path(ROOT, check_pin(pin)['path'])
    local_path(ROOT, check_pin(training['initialization'])['path'])
    require(type(training['epochs']) is int and 1 <= training['epochs'] <= 1000, 'training_epochs')
    budget = training['storageBudgetBytes']
    require(type(budget) is int and 0 < budget <= 1 << 40, 'training_storage')
    require(spec['limits']['maxOutputBytes'] <= budget, 'training_storage')
    require(isinstance(training['acceptanceEvidence'], str) and training['acceptanceEvidence'].strip(),
            'training_acceptance')
    # The trainers save weights only at the end, so an interrupted run restarts from epoch 0.
    require(training['resume'] == 'restart', 'training_resume')


def check_training(spec, queue):
    """Check the run-time training conditions: a prior log entry and free storage."""
    if spec['authority'] != 'training':
        return
    training = spec['training']
    text = EXPERIMENT_LOG.read_text() if EXPERIMENT_LOG.is_file() else ''
    pattern = r'(?<![\w-])' + re.escape(training['experimentLogRunId']) + r'(?![\w-])'
    require(re.search(pattern, text), 'experiment_log_missing')
    queue.mkdir(parents=True, exist_ok=True)
    require(shutil.disk_usage(queue).free >= training['storageBudgetBytes'] + STORAGE_MARGIN, 'storage_insufficient')


def output_dir(spec, attempt):
    name = spec['adapter'].get('outputFolderName')
    return attempt / 'out' / name if name else attempt / 'out'


def validate(spec, module_dir=MODULES):
    require(isinstance(spec, dict) and spec.get('version') == SPEC_VERSION, 'spec_version')
    for key in ('id', 'task'):
        require(isinstance(spec.get(key), str) and ID.fullmatch(spec[key]), f'{key}_format')
    for key in ('owner', 'hypothesis', 'decisionRule'):
        require(isinstance(spec.get(key), str) and spec[key].strip(), f'{key}_missing')
    require(spec.get('kind') in KINDS, 'kind_unknown')
    require(spec.get('authority') in AUTHORITIES, 'authority_unknown')
    require(spec['authority'] in PERMITTED, 'authority_not_permitted')
    adapter = spec.get('adapter')
    require(isinstance(adapter, dict) and adapter.get('type') == 'python-callable', 'adapter_unknown')
    require(isinstance(adapter.get('steps'), list) and adapter['steps'], 'steps_missing')
    for step in adapter['steps']:
        split_target(step, module_dir)
    require(isinstance(adapter.get('outputAttributes'), list), 'output_attributes_missing')
    for attribute in adapter['outputAttributes']:
        split_target(attribute, module_dir)
    require(set(adapter) <= {'type', 'steps', 'outputAttributes', 'outputFolderName'}, 'adapter_fields')
    if 'outputFolderName' in adapter:
        require(isinstance(adapter['outputFolderName'], str) and FILE.fullmatch(adapter['outputFolderName']),
                'output_folder_name')
    for pin in spec.get('inputs', []):
        local_path(ROOT, check_pin(pin)['path'])
    for item in spec.get('stage', []):
        require(isinstance(item, dict) and set(item) == {'from', 'to'}, 'stage_fields')
        local_path(ROOT, check_pin(item['from'])['path'])
        require(isinstance(item['to'], str) and FILE.fullmatch(item['to']), 'stage_name')
    limits = spec.get('limits')
    require(isinstance(limits, dict) and set(limits) == {'timeoutSeconds', 'maxOutputBytes', 'maxAttempts'}, 'limits_fields')
    require(type(limits['timeoutSeconds']) in (int, float) and 0 < limits['timeoutSeconds'] <= 86400, 'limits_timeout')
    require(type(limits['maxOutputBytes']) is int and 0 < limits['maxOutputBytes'] <= 1 << 34, 'limits_bytes')
    require(type(limits['maxAttempts']) is int and 1 <= limits['maxAttempts'] <= 5, 'limits_attempts')
    validate_training(spec)
    if spec['kind'] == 'replay':
        replay = spec.get('replay')
        require(isinstance(replay, dict) and isinstance(replay.get('files'), list) and replay['files'], 'replay_missing')
        local_path(ROOT, replay.get('recordedDirectory'))
        for item in replay['files']:
            require(isinstance(item, dict) and set(item) <= {'name', 'sha256', 'compare', 'tolerance', 'ignore'},
                    'replay_fields')
            check_name(item.get('name'))
            require(isinstance(item.get('sha256'), str) and HASH.fullmatch(item['sha256']), 'replay_hash_format')
            require(item.get('compare', 'json') in ('json', 'sha256'), 'replay_compare')
            if item.get('compare') == 'sha256':
                require('ignore' not in item and 'tolerance' not in item, 'replay_compare')
            tolerance = item.get('tolerance', 0)
            require(type(tolerance) in (int, float) and 0 <= tolerance <= 1, 'replay_tolerance')
            for ignore in item.get('ignore', []):
                check_ignore(ignore.get('path'))
                require(isinstance(ignore.get('reason'), str) and ignore['reason'].strip(), 'ignore_reason')
    else:
        require('replay' not in spec, 'replay_only_for_replay_jobs')
    return spec


def verify_pins(spec):
    pins = list(spec.get('inputs', [])) + [item['from'] for item in spec.get('stage', [])]
    if spec['authority'] == 'training':
        pins += spec['training']['membership'] + [spec['training']['initialization']]
    for pin in pins:
        path = local_path(ROOT, pin['path'])
        require(path.is_file() and digest(path) == pin['sha256'], 'input_changed')
    if spec['kind'] == 'replay':
        recorded = local_path(ROOT, spec['replay']['recordedDirectory'])
        for item in spec['replay']['files']:
            path = recorded / item['name']
            require(path.is_file() and digest(path) == item['sha256'], 'recorded_output_changed')


def submit(spec_path, queue=QUEUE, module_dir=MODULES):
    spec = validate(load(spec_path), module_dir)
    verify_pins(spec)
    check_training(spec, queue)
    job = queue / 'jobs' / spec['id']
    target = job / 'spec.json'
    if target.exists():
        require(load(target) == spec, 'job_exists')
        return 'already_submitted'
    job.mkdir(parents=True, exist_ok=True)
    save(target, spec)
    return 'submitted'


@contextlib.contextmanager
def host_lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+') as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('resource_busy')
        yield


def inventory(folder, limit):
    files, total = [], 0
    for path in sorted(folder.rglob('*')):
        require(not path.is_symlink(), 'symlink_in_outputs')
        if path.is_file():
            size = path.stat().st_size
            total += size
            files.append(dict(path=str(path.relative_to(folder)), bytes=size, sha256=digest(path)))
    return files, total <= limit


def attempts_of(job):
    folder = job / 'attempts'
    return sorted((p for p in folder.iterdir() if p.is_dir() and p.name.isdigit()), key=lambda p: int(p.name)) \
        if folder.exists() else []


def outputs_intact(attempt, result):
    out = attempt / 'out'
    return all((out / f['path']).is_file() and digest(out / f['path']) == f['sha256'] for f in result['outputs'])


def state(job):
    """Return the job state from recorded files only."""
    spec = load(job / 'spec.json')
    attempts = attempts_of(job)
    results = [load(a / 'result.json') if (a / 'result.json').exists() else None for a in attempts]
    for attempt, result in zip(attempts, results):
        if result and result['status'] == 'complete' and outputs_intact(attempt, result):
            return 'complete', attempts
    if attempts and results[-1] is None:
        return 'interrupted', attempts
    if len(attempts) >= spec['limits']['maxAttempts']:
        return 'exhausted', attempts
    return 'pending', attempts


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT))


def remove_path(doc, parts):
    """Remove a dotted field. `key[]` applies the rest of the path to each list entry."""
    head, rest = parts[0], parts[1:]
    if head.endswith('[]'):
        items = doc.get(head[:-2]) if isinstance(doc, dict) else None
        return sum(remove_path(item, rest) for item in items) if isinstance(items, list) else 0
    if not isinstance(doc, dict) or head not in doc:
        return 0
    if not rest:
        del doc[head]
        return 1
    return remove_path(doc[head], rest)


def map_paths(value, old_prefix, new_prefix):
    if isinstance(value, dict):
        return {k: map_paths(v, old_prefix, new_prefix) for k, v in value.items()}
    if isinstance(value, list):
        return [map_paths(v, old_prefix, new_prefix) for v in value]
    if isinstance(value, str) and value.startswith(old_prefix):
        return new_prefix + value[len(old_prefix):]
    return value


def differences(a, b, tolerance=0, path='', found=None, limit=20):
    """Count differing fields. Numeric differences within the tolerance are counted separately."""
    found = found if found is not None else dict(paths=[], count=0, withinTolerance=0, maxNumericDiff=0.0)
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            sub = f'{path}.{key}' if path else key
            if key not in a or key not in b:
                found['count'] += 1
                if len(found['paths']) < limit:
                    found['paths'].append(sub)
            else:
                differences(a[key], b[key], tolerance, sub, found, limit)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            differences(x, y, tolerance, f'{path}[{i}]', found, limit)
    elif a != b or type(a) is not type(b):
        numeric = type(a) in (int, float) and type(b) in (int, float)
        if numeric:
            found['maxNumericDiff'] = max(found['maxNumericDiff'], abs(a - b))
        if numeric and abs(a - b) <= tolerance:
            found['withinTolerance'] += 1
        else:
            found['count'] += 1
            if len(found['paths']) < limit:
                found['paths'].append(path or '$')
    return found


def compare_replay(spec, out):
    replay = spec['replay']
    recorded = local_path(ROOT, replay['recordedDirectory'])
    old_prefix = relative(out) + '/'
    new_prefix = replay['recordedDirectory'].rstrip('/') + '/'
    files = []
    for item in replay['files']:
        produced = out / item['name']
        if not produced.is_file():
            files.append(dict(name=item['name'], matched=False, reason='missing_output'))
            continue
        same = digest(produced) == item['sha256']
        if item.get('compare') == 'sha256':
            files.append(dict(name=item['name'], compare='sha256', matched=same, bytesIdentical=same))
            continue
        original = load(recorded / item['name'])
        replayed = map_paths(load(produced), old_prefix, new_prefix)
        ignored = []
        for ignore in item.get('ignore', []):
            parts = ignore['path'].split('.')
            removed = [remove_path(doc, parts) for doc in (original, replayed)]
            ignored.append(dict(path=ignore['path'], recordedFields=removed[0], replayedFields=removed[1]))
        diff = differences(original, replayed, item.get('tolerance', 0))
        files.append(dict(name=item['name'], compare='json', matched=diff['count'] == 0,
                          exactlyEqual=diff['count'] == 0 and diff['withinTolerance'] == 0, bytesIdentical=same,
                          tolerance=item.get('tolerance', 0), ignored=ignored, differenceCount=diff['count'],
                          withinToleranceCount=diff['withinTolerance'], differencePaths=diff['paths'],
                          maxNumericDiff=diff['maxNumericDiff']))
    return dict(matched=all(f['matched'] for f in files), files=files)


def execute(spec, attempt, module_dir, python):
    out = output_dir(spec, attempt)
    out.mkdir(parents=True)
    for item in spec.get('stage', []):
        source = local_path(ROOT, item['from']['path'])
        shutil.copyfile(source, out / item['to'])
        require(digest(out / item['to']) == item['from']['sha256'], 'stage_copy_hash')
    env = dict(os.environ, PYTHONPATH=str(module_dir), PYTHONDONTWRITEBYTECODE='1')
    with (attempt / 'stdout.log').open('w') as stdout, (attempt / 'stderr.log').open('w') as stderr:
        process = subprocess.Popen([python, str(Path(__file__).resolve()), '_execute', str(attempt), str(module_dir)],
                                   cwd=ROOT, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            return process.wait(timeout=spec['limits']['timeoutSeconds']), False
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            return process.returncode, True


def run_attempt(job, spec, number, module_dir, python):
    attempt = job / 'attempts' / str(number)
    attempt.mkdir(parents=True)
    started = time.time()
    save(attempt / 'attempt.json', dict(version=ATTEMPT_VERSION, job=spec['id'], number=number,
         specSHA256=text_digest(spec), startedAt=started, python=python, platform=platform.platform()))
    result = dict(version=RESULT_VERSION, job=spec['id'], task=spec['task'], kind=spec['kind'],
                  authority=spec['authority'], attempt=number, specSHA256=text_digest(spec))
    if spec['authority'] == 'training':
        training = spec['training']
        result['training'] = dict(experimentLogRunId=training['experimentLogRunId'], epochs=training['epochs'],
                                  resume=training['resume'], storageBudgetBytes=training['storageBudgetBytes'])
    try:
        verify_pins(spec)
        check_training(spec, job.parents[1])
    except ValueError as error:
        result.update(status='failed', reason=str(error), wallSeconds=0.0, outputs=[])
        save(attempt / 'result.json', result)
        return result
    code, timed_out = execute(spec, attempt, module_dir, python)
    outputs, within = inventory(attempt / 'out', spec['limits']['maxOutputBytes'])
    result.update(returnCode=code, wallSeconds=time.time() - started, outputs=outputs,
                  steps=load(attempt / 'steps.json') if (attempt / 'steps.json').exists() else None,
                  closure=load(attempt / 'closure.json') if (attempt / 'closure.json').exists() else None)
    if timed_out:
        result.update(status='failed', reason='timeout')
    elif code != 0:
        result.update(status='failed', reason='process_failed')
    elif not within:
        result.update(status='failed', reason='output_limit')
    else:
        result.update(status='complete')
        if spec['kind'] == 'replay':
            result['replay'] = compare_replay(spec, output_dir(spec, attempt))
    save(attempt / 'result.json', result)
    return result


def run(queue=QUEUE, module_dir=MODULES, max_jobs=1, python=sys.executable, lock=None):
    lock = lock or ROOT / '.build/research-queue.lock'
    report = []
    with host_lock(lock):
        jobs = sorted((queue / 'jobs').iterdir()) if (queue / 'jobs').exists() else []
        for job in jobs:
            if len(report) >= max_jobs:
                break
            spec = validate(load(job / 'spec.json'), module_dir)
            current, attempts = state(job)
            if current == 'interrupted':
                save(attempts[-1] / 'result.json', dict(version=RESULT_VERSION, job=spec['id'], task=spec['task'],
                     kind=spec['kind'], authority=spec['authority'], attempt=int(attempts[-1].name),
                     specSHA256=text_digest(spec), status='interrupted', outputs=[], wallSeconds=None))
                current, attempts = state(job)
            if current != 'pending':
                continue
            result = run_attempt(job, spec, len(attempts) + 1, module_dir, python)
            report.append((spec['id'], result['status']))
    return report


def child(attempt, module_dir):
    """Run inside the job process. Import steps, redirect outputs, record the module closure."""
    attempt = Path(attempt)
    spec = load(attempt.parents[1] / 'spec.json')
    out = output_dir(spec, attempt).resolve()
    adapter = spec['adapter']
    modules = {}
    for target in adapter['outputAttributes'] + adapter['steps']:
        name = split_target(target, Path(module_dir))[0]
        modules[name] = importlib.import_module(name)
    for target in adapter['outputAttributes']:
        name, attribute = target.split('.')
        require(hasattr(modules[name], attribute), 'output_attribute_missing')
        setattr(modules[name], attribute, out)
    steps = []
    for target in adapter['steps']:
        name, function = target.split('.')
        call = getattr(modules[name], function, None)
        require(callable(call), 'step_not_callable')
        start = time.monotonic()
        call()
        steps.append(dict(step=target, seconds=time.monotonic() - start))
    save(attempt / 'steps.json', steps)
    closure = []
    for module in list(sys.modules.values()):
        file = getattr(module, '__file__', None)
        if not file or not os.path.isfile(file):
            continue
        path = Path(file).resolve()
        if ROOT in path.parents and '.venv' not in '/'.join(path.parts):
            closure.append(dict(path=relative(path), sha256=digest(path)))
    packages = {name: getattr(sys.modules[name], '__version__', None) for name in ('numpy', 'torch', 'PIL') if name in sys.modules}
    save(attempt / 'closure.json', dict(modules=sorted(closure, key=lambda v: v['path']), packages=packages,
                                        python=sys.version.split()[0]))


def summarize(queue=QUEUE):
    rows = []
    for job in sorted((queue / 'jobs').iterdir()) if (queue / 'jobs').exists() else []:
        spec = load(job / 'spec.json')
        current, attempts = state(job)
        last = load(attempts[-1] / 'result.json') if attempts and (attempts[-1] / 'result.json').exists() else {}
        replay = last.get('replay')
        row = dict(job=spec['id'], task=spec['task'], kind=spec['kind'], authority=spec['authority'],
                   hypothesis=spec['hypothesis'], decisionRule=spec['decisionRule'], state=current,
                   attempts=len(attempts), status=last.get('status'), reason=last.get('reason'),
                   wallSeconds=last.get('wallSeconds'),
                   closureModules=len(last['closure']['modules']) if last.get('closure') else None,
                   experimentLogRunId=spec['training']['experimentLogRunId'] if 'training' in spec else None,
                   replayMatched=replay['matched'] if replay else None,
                   replayExact=all(f.get('exactlyEqual', f.get('bytesIdentical')) for f in replay['files'])
                   if replay else None,
                   replayDifferences=sum(f.get('differenceCount', 0) for f in replay['files']) if replay else None)
        
        # Extract screening metrics if available
        if attempts and (attempts[-1] / 'out/benchmark_summary.json').exists():
            try:
                bm = load(attempts[-1] / 'out/benchmark_summary.json')
                metrics = bm.get('metrics', {})
                eff = metrics.get('accuracy', 0.0)
                samples = metrics.get('sample_count', bm.get('evaluated_cases', 0))
                cost = last.get('wallSeconds') or 0.0
                row['screening'] = dict(effect=eff, sampleCount=samples, costSeconds=cost)
            except Exception:
                pass
        rows.append(row)

    # Rank completed jobs with screening metrics by effect descending, then cost ascending
    ranked = sorted(
        [r for r in rows if r.get('screening') and r.get('status') == 'complete'],
        key=lambda r: (r['screening']['effect'], -r['screening']['costSeconds']),
        reverse=True
    )
    for rank_idx, r in enumerate(ranked, 1):
        r['screening']['rank'] = rank_idx

    summary = dict(version=SUMMARY_VERSION, generatedAt=time.time(), jobs=rows)
    queue.mkdir(parents=True, exist_ok=True)
    save(queue / 'summary.json', summary, replace=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--queue', type=Path, default=QUEUE)
    parser.add_argument('--module-dir', type=Path, default=MODULES)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('submit').add_argument('spec', type=Path)
    run_parser = sub.add_parser('run')
    run_parser.add_argument('--max-jobs', type=int, default=1)
    sub.add_parser('status')
    sub.add_parser('summarize')
    execute_parser = sub.add_parser('_execute')
    execute_parser.add_argument('attempt')
    execute_parser.add_argument('child_module_dir')
    args = parser.parse_args()
    if args.command == '_execute':
        child(args.attempt, args.child_module_dir)
    elif args.command == 'submit':
        print(submit(args.spec, args.queue.resolve(), args.module_dir.resolve()))
    elif args.command == 'run':
        require(1 <= args.max_jobs <= 100, 'max_jobs')
        for job, status in run(args.queue.resolve(), args.module_dir.resolve(), args.max_jobs):
            print(job, status, flush=True)
    else:
        summary = summarize(args.queue.resolve())
        for row in summary['jobs']:
            extra = ""
            if row.get('screening'):
                sc = row['screening']
                rank = sc.get('rank', '-')
                extra = f" effect={sc['effect']:.4f} rank={rank} cost={sc['costSeconds']:.2f}s"
            print(f"{row['job']:<32} {row['state']:<12} attempts={row['attempts']} status={row['status']} "
                  f"replayMatched={row['replayMatched']} differences={row['replayDifferences']}{extra}")


if __name__ == '__main__':
    main()
