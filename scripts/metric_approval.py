"""Simple records of explicit user decisions. These records are not cryptographic authentication."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = Path('reports/work/user-approvals')


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):h.update(block)
    return h.hexdigest()


def read_record(path, root=ROOT):
    path=Path(path)
    if path.is_absolute() or '..' in path.parts:raise ValueError('approval_path')
    full=root/path
    if not full.is_file() or full.resolve()!=full.absolute():raise ValueError('approval_missing')
    record=json.loads(full.read_text())
    if record.get('version')!='user-review-v1' or record.get('decision')!='approved':raise ValueError('approval_decision')
    if not record.get('userMessage') or not record.get('chatReference'):raise ValueError('explicit_user_review_required')
    return record


def require_promotion(entry, root=ROOT):
    record=read_record(entry['approvalReference'],root)
    if record.get('action')!='promotion':raise ValueError('promotion_approval_required')
    expected=hashlib.sha256(json.dumps({k:v for k,v in entry.items() if k!='approvalReference'},sort_keys=True).encode()).hexdigest()
    if record.get('releaseEntrySHA256')!=expected:raise ValueError('approved_release_changed')
    return record


def report_status(report, root=ROOT):
    result=dict(metricsStatus='provisional',modelAcceptance='requires-user-approval',promotionStatus='not-approved')
    report=Path(report)
    if not report.is_absolute():report=root/report
    if not report.is_file():return result
    for path in (root/LEDGER).glob('*.json'):
        try:
            record=read_record(path.relative_to(root),root)
            if record.get('action')=='publish-metrics' and record.get('reportSHA256')==digest(report):
                result.update(metricsStatus='user-approved',approvedScope=record.get('scope','User-reviewed report'))
        except (ValueError,OSError,TypeError):continue
    return result


def decorate_jobs(rows, root=ROOT):
    for row in rows:
        row.update(metricsStatus='provisional',modelAcceptance='requires-user-approval',promotionStatus='not-approved')
        if row.get('attempts'):
            report=root/'reports/work/research-queue/jobs'/row['job']/'attempts'/str(row['attempts'])/'out/benchmark_summary.json'
            row.update(report_status(report,root))
