"""Exact runtime exceptions approved by the maintainer. No scope expansion."""
import json
from pathlib import Path

# USB386 preserves the approved HCF375D recipe and its 2 h detector limit.
TRAINING_EXCEPTIONS = {
    '6dec71bd728b7e5c5fc2a8000dd5b20490a5731779139fd11feb6144fbb16d6c': 7200,
    # HCF388 resolves early stopping while retaining the approved 30-epoch study.
    'f7ae94240dc3193471a1e2d31e1ff3efe19f00f788c8a5368a674c528df94608': 7200,
}
# EXTENSION408: maintainer limit overrides for exact successor specifications.
OVERRIDES = 'execution-limits.json'
OVERRIDE_VERSION = 'research-execution-limits-v1'
LIVE_QUEUE = Path(__file__).resolve().parents[1] / 'reports/work/research-queue'


def override(queue, spec_hash):
    """Return the maintainer override for 1 exact specification hash, or None."""
    path = queue / OVERRIDES if queue is not None else None
    if path is None or not path.is_file():
        return None
    doc = json.loads(path.read_text())
    if doc.get('version') != OVERRIDE_VERSION:
        raise ValueError('execution_limits_version')
    record = doc.get('specs', {}).get(spec_hash)
    if record is None:
        return None
    # The test approver cannot act on the live queue.
    if record.get('by') != 'maintainer' and not (record.get('by') == 'test' and queue.resolve() != LIVE_QUEUE):
        raise ValueError('execution_limits_approver')
    return record


def seconds(spec_hash, authority, diagnostic_seconds, queue=None):
    if authority == 'export':
        default = 1800
    elif authority == 'training':
        default = TRAINING_EXCEPTIONS.get(spec_hash, 1800)
    else:
        default = diagnostic_seconds
    # Capture limits stay fixed. The spec validator also enforces them.
    record = override(queue, spec_hash) if authority != 'capture' else None
    return max(default, record['timeoutSeconds']) if record else default


def output_bytes(spec_hash, authority, diagnostic_bytes, queue=None):
    default = 2 << 30 if authority in ('training', 'export') else diagnostic_bytes
    record = override(queue, spec_hash) if authority != 'capture' else None
    return max(default, record['maxOutputBytes']) if record else default
