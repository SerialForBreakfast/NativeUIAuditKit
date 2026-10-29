"""Authenticity rules for research jobs (RCA-20261013-01).

A `research-spec-v2` job declares its kind, its plain-language question, and the evidence it must produce.
The child records Python file opens. Native loaders need explicit instrumentation.
A job that never reads its pinned data or model fails as `evidence_not_read`, whatever its exit code.
These checks replace the RCA's 5 s rule: fast aggregation jobs remain valid when they read real producer outputs.
Opening a file does not prove its use. These checks do not contain malicious code.
"""
import builtins
import io
import os
import math
import re
from pathlib import Path

import research_queue as q

SPEC_V2 = 'research-spec-v2'
JOB_KINDS = {'capture', 'training', 'evaluation', 'aggregation', 'analytic', 'artifact'}
OWNER = re.compile(r'[A-Za-z0-9][A-Za-z0-9-]{1,63}-(?:NUIAK|TTR)')
TEXT_FIELDS = ('question', 'controlledComparison', 'decisionRule')
READS_FILE = 'reads.json'
READS_LIMIT = 20000

_reads = set()
_reads_total = 0


def text(value):
    return isinstance(value, str) and len(value.strip()) >= 12


def validate_v2(spec):
    """Validate the v2 description and evidence contract."""
    q.require(isinstance(spec.get('owner'), str) and OWNER.fullmatch(spec['owner']), 'owner_not_machine_project')
    for key in TEXT_FIELDS:
        q.require(text(spec.get(key)), f'{key}_missing')
    outcomes = spec.get('nextActionByOutcome')
    q.require(isinstance(outcomes, dict) and len(outcomes) >= 2 and all(text(v) for v in outcomes.values()),
              'next_action_by_outcome_missing')
    kind = spec.get('jobKind')
    q.require(kind in JOB_KINDS, 'job_kind_unknown')
    evidence = spec.get('evidence', {})
    q.require(isinstance(evidence, dict) and set(evidence) <= {'reads', 'weights', 'predictions', 'membershipCount',
              'history', 'trainingReport', 'captureReceipt', 'citations', 'model', 'artifactReceipt'},
              'evidence_fields')
    reads = evidence.get('reads', [])
    q.require(isinstance(reads, list) and len(set(reads)) == len(reads), 'evidence_reads')
    pinned = {p['path'] for p in spec.get('inputs', [])} | {s['from']['path'] for s in spec.get('stage', [])}
    if spec['authority'] == 'training':
        pinned |= {p['path'] for p in spec['training']['membership']} | {spec['training']['initialization']['path']}
    for path in reads:
        q.require(path in pinned, 'evidence_read_not_pinned:' + str(path))
    if kind == 'artifact':
        q.require(reads or spec.get('dependencies'), 'artifact_inputs_missing')
        q.check_name(evidence.get('artifactReceipt'))
    elif kind == 'capture':
        q.require(spec['authority'] == 'capture', 'capture_kind_authority')
        q.check_name(evidence.get('captureReceipt'))
    elif kind == 'training':
        q.require(spec['authority'] == 'training', 'training_kind_authority')
        q.check_name(evidence.get('weights'))
        q.check_name(evidence.get('history'))
        q.check_name(evidence.get('trainingReport'))
        required = {p['path'] for p in spec['training']['membership']} | {spec['training']['initialization']['path']}
        q.require(required <= set(reads), 'training_reads_incomplete')
    elif kind == 'evaluation':
        q.require(reads or spec.get('dependencies'), 'evaluation_reads_missing')
        dependency_model = any('model.json' in d['outputs'] for d in spec.get('dependencies', []))
        q.require(evidence.get('model') in reads or dependency_model, 'evaluation_model_missing')
        q.check_name(evidence.get('predictions'))
        count = evidence.get('membershipCount')
        q.require(type(count) is int and count > 0, 'evaluation_membership_count')
    elif kind == 'aggregation':
        q.require(spec.get('dependencies'), 'aggregation_dependencies_missing')
        q.check_name(evidence.get('citations'))
    q.require(spec['authority'] != 'training' or kind == 'training', 'training_authority_kind')
    q.require(spec['authority'] != 'capture' or kind == 'capture', 'capture_authority_kind')
    q.require(kind != 'analytic' or not evidence, 'analytic_declares_no_evidence')
    for item in spec.get('stage', []):
        path = q.ROOT / item['from']['path']
        if path.suffix == '.json' and path.is_file() and path.stat().st_size <= 5_000_000:
            empty = sorted(k for k, v in empty_lists(q.load(path)))
            q.require(not empty, 'empty_membership_list:' + ','.join(empty))
    if kind != 'training':
        q.require('weights' not in evidence, 'weights_only_for_training')
    if kind != 'evaluation':
        q.require('predictions' not in evidence and 'membershipCount' not in evidence, 'predictions_only_for_evaluation')
    q.require(kind == 'artifact' or 'artifactReceipt' not in evidence, 'artifact_receipt_kind')


MEMBERSHIP_KEYS = {'sources', 'rows', 'members', 'cases', 'items', 'jobs'}


def empty_lists(value, prefix=''):
    """Yield membership-like keys whose list is empty. An empty shard silently changes what a job computes."""
    if isinstance(value, dict):
        for key, item in value.items():
            name = f'{prefix}.{key}' if prefix else key
            if key in MEMBERSHIP_KEYS and isinstance(item, list) and not item:
                yield name, item
            else:
                yield from empty_lists(item, name)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from empty_lists(item, f'{prefix}[{index}]')


def _note(path, mode='r'):
    global _reads_total
    if any(flag in mode for flag in ('w', 'a', 'x')) and '+' not in mode:
        return
    try:
        resolved = os.path.realpath(os.fspath(path))
    except TypeError:
        return
    _reads_total += 1
    if len(_reads) < READS_LIMIT and os.path.isfile(resolved):
        _reads.add(resolved)


def note_read(path):
    """Record a read made by a native loader that bypasses Python file APIs, such as Core ML."""
    _note(path)


def install_read_trace():
    """Wrap Python file opening in this child process. PIL, NumPy, and PyTorch file loads pass through it."""
    original_open, original_os_open = builtins.open, os.open

    def traced_open(file, mode='r', *args, **kwargs):
        stream = original_open(file, mode, *args, **kwargs)
        if isinstance(file, (str, bytes, os.PathLike)):
            _note(file, mode if isinstance(mode, str) else 'r')
        return stream

    def traced_os_open(path, flags, *args, **kwargs):
        descriptor = original_os_open(path, flags, *args, **kwargs)
        if flags & os.O_ACCMODE != os.O_WRONLY:
            _note(path)
        return descriptor

    builtins.open = traced_open
    io.open = traced_open
    os.open = traced_os_open


def write_reads(attempt):
    paths = sorted(_reads)
    q.save(Path(attempt) / READS_FILE, dict(version='research-reads-v1', total=_reads_total,
           truncated=len(paths) >= READS_LIMIT, files=paths), replace=True)


def check_training_report(out, evidence, max_epochs):
    """Check the training history and report fields. Template schema tests call this without a training run."""
    history_path, report_path = (Path(out) / evidence[key] for key in ('history', 'trainingReport'))
    if not history_path.is_file() or not report_path.is_file():
        return 'training_history_missing'
    history, report = q.load(history_path), q.load(report_path)
    epochs = report.get('epochs') if isinstance(report, dict) else None
    if (type(epochs) is not int or not 0 < epochs <= max_epochs
            or not isinstance(history, list) or len(history) != epochs
            or any(not isinstance(row, dict) or row.get('epoch') != index
                   for index, row in enumerate(history, 1))):
        return 'training_history_epoch_mismatch'
    if any(not isinstance(row.get('trainLoss'), (int, float))
           or not math.isfinite(row['trainLoss']) for row in history):
        return 'training_history_loss_invalid'
    return None


def check_evidence(spec, attempt, out):
    """Return None when the declared evidence exists, or the reason it does not."""
    if spec.get('version') != SPEC_V2:
        return None
    reads_path = Path(attempt) / READS_FILE
    if not reads_path.is_file():
        return 'reads_record_missing'
    record = q.load(reads_path)
    if (record.get('version') != 'research-reads-v1' or record.get('truncated') is not False
            or not isinstance(record.get('files'), list)
            or not all(isinstance(p, str) for p in record['files'])):
        return 'reads_record_invalid_or_truncated'
    reads = set(record['files'])
    kind, evidence = spec['jobKind'], spec.get('evidence', {})
    required = [str((q.ROOT / p).resolve()) for p in evidence.get('reads', [])]
    deps = Path(out) / 'dependencies.json'
    if spec.get('dependencies') and not deps.is_file():
        return 'dependencies_record_missing'
    for dep in q.load(deps) if deps.is_file() else []:
        if 'failure' in dep:
            required.append(str((q.ROOT / dep['result']['path']).resolve()))
        for output in dep['outputs']:
            required.append(str((q.ROOT / output['path']).resolve()))
            if kind == 'evaluation' and output['path'].endswith('/model.json'):
                model = q.load(q.ROOT / output['path'])
                required.append(os.path.realpath(model['path']))
    for path in required:
        if path not in reads:
            return 'evidence_not_read:' + os.path.relpath(path, q.ROOT)
    if kind == 'artifact':
        receipt = Path(out) / evidence['artifactReceipt']
        if not receipt.is_file(): return 'artifact_receipt_missing'
        document = q.load(receipt)
        if document.get('version') != 'research-artifact-v1' or not document.get('outputs'):
            return 'artifact_receipt_invalid'
        seen = set()
        for item in document['outputs']:
            q.check_pin(item)
            path = q.local_path(Path(out), item['path'])
            if item['path'] in seen or not path.is_file() or q.digest(path) != item['sha256']:
                return 'artifact_output_changed'
            seen.add(item['path'])
    elif kind == 'capture':
        if not any(p.suffix.lower() == '.png' for p in Path(out).rglob('*')):
            return 'capture_without_images'
        receipt = Path(out) / evidence['captureReceipt']
        if not receipt.is_file():
            return 'capture_receipt_missing'
        document = q.load(receipt)
        if document.get('version') != 'research-capture-evidence-v1' or not document.get('images'):
            return 'capture_receipt_invalid'
        for item in document['images']:
            path = q.local_path(Path(out), item['path'])
            if path.suffix.lower() != '.png' or not path.is_file() or q.digest(path) != item['sha256']:
                return 'capture_receipt_image_changed'
    elif kind == 'training':
        weights = Path(out) / evidence['weights']
        if not weights.is_file():
            return 'training_weights_missing'
        if q.digest(weights) == spec['training']['initialization']['sha256']:
            return 'training_weights_unchanged'
        problem = check_training_report(out, evidence, spec['training']['epochs'])
        if problem:
            return problem
    elif kind == 'evaluation':
        path = Path(out) / evidence['predictions']
        if not path.is_file():
            return 'evaluation_predictions_missing'
        doc = q.load(path)
        rows = doc if isinstance(doc, list) else doc.get('predictions', doc.get('rows')) if isinstance(doc, dict) else None
        if not isinstance(rows, list) or len(rows) != evidence['membershipCount']:
            return 'evaluation_prediction_count'
        if not all(isinstance(row, dict) and isinstance(row.get('id'), (str, int)) for row in rows):
            return 'evaluation_prediction_ids_missing'
        if len({row['id'] for row in rows}) != len(rows):
            return 'evaluation_prediction_ids_duplicate'
    elif kind == 'aggregation':
        path = Path(out) / evidence['citations']
        if not path.is_file():
            return 'aggregation_citations_missing'
        expected = [item for dep in q.load(deps) for item in dep['outputs']]
        if q.load(path) != expected:
            return 'aggregation_citations_mismatch'
    return None


def drift(job, attempt=None, display_cache=False):
    """Return step modules whose current hash differs from the hash recorded at run time.

    display_cache=True reuses stat-keyed hashes for dashboard labels only.
    """
    spec = q.load(job / 'spec.json')
    if attempt is None:
        attempt = next((a for a in q.attempts_of(job) if (a / 'result.json').exists()
                        and q.load(a / 'result.json').get('status') == 'complete'), None)
    closure_path = attempt / 'closure.json' if attempt else None
    if not closure_path or not closure_path.is_file():
        return []
    recorded = {m['path']: m['sha256'] for m in q.load(closure_path)['modules']}
    changed = []
    for step in spec['adapter']['steps']:
        name = '/' + step.split('.')[0] + '.py'
        for path in [p for p in recorded if ('/' + p).endswith(name)]:
            current = q.ROOT / path
            if not current.is_file() or (q.display_digest if display_cache else q.digest)(current) != recorded[path]:
                changed.append(path)
    return sorted(set(changed))
