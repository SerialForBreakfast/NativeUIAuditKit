"""Export a browsable snapshot of local experiment receipts."""
import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / 'reports/work/research-queue/jobs'
DEST = ROOT / 'reports/work/experiment-map/index.html'
LIB = ROOT / 'scripts/vendor/cytoscape-3.33.1/cytoscape.min.js'


def load(path, limit):
    if path.is_symlink() or path.stat().st_size > limit:
        raise ValueError('Unsupported file')
    return json.loads(path.read_bytes())


def experiment(folder):
    spec = load(folder / 'spec.json', 2_000_000)
    ident = spec['id']
    if ident != folder.name:
        raise ValueError('Unexpected job identity')
    deps = [d if isinstance(d, str) else d['job'] for d in spec.get('dependencies', [])]
    row = dict(id=ident, group=spec.get('task') or 'Unassigned', deps=deps,
               question=spec.get('question') or spec.get('hypothesis') or ident,
               rule=spec.get('decisionRule'), status='No result receipt', findings={}, files=[])
    receipts = sorted((folder/'attempts').glob('*/result.json'),
                      key=lambda p: int(p.parent.name) if p.parent.name.isdigit() else -1)
    if not receipts:
        return row
    receipt = receipts[-1]
    result = load(receipt, 4_000_000)
    digest = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()
    if result.get('job') != ident or result.get('specSHA256') != digest:
        row['status'] = 'Receipt identity mismatch'
        return row
    row['status'] = result.get('status') or 'Unknown status'
    row['files'].append(['Execution receipt', '../research-queue/jobs/' + str(receipt.relative_to(QUEUE))])
    outputs = {o.get('path'): o for o in result.get('outputs', [])}
    for name in ('decision.json', 'benchmark_summary.json', 'report.md'):
        if name not in outputs:
            continue
        p = receipt.parent/'out'/name
        if not p.is_file() or p.is_symlink() or p.stat().st_size > 8_000_000:
            continue
        raw = p.read_bytes()
        if hashlib.sha256(raw).hexdigest() != outputs[name].get('sha256'):
            continue
        row['files'].append([name, '../research-queue/jobs/' + str(p.relative_to(QUEUE))])
        if name.endswith('.json'):
            doc = json.loads(raw)
            if isinstance(doc, dict):
                for k in ('outcome','decision','reason','metrics','gains','lostPriorSuccesses','nextAction','limitation'):
                    v = doc.get(k)
                    if isinstance(v, list) and k in ('gains','lostPriorSuccesses'):
                        v = len(v)
                    if isinstance(v, dict):
                        v = {key:n for key,n in v.items() if type(n) in (int,float)}
                    if v is not None and len(str(v)) <= 1500:
                        row['findings'].setdefault(k,v)
    return row


def main():
    rows = []
    skipped = 0
    for folder in sorted(QUEUE.iterdir()):
        if not folder.is_dir() or folder.is_symlink():
            continue
        try:
            rows.append(experiment(folder))
        except (OSError, ValueError, TypeError, KeyError):
            skipped += 1
    asset = LIB.read_bytes()
    if hashlib.sha256(asset).hexdigest() != 'f55947f3daa3bae53209d4b885c195c157f595c225e508a6b382598d9452d6e2':
        raise ValueError('Unexpected graph library')
    page = Path(__file__).with_suffix('.html').read_text()
    data = json.dumps(rows, separators=(',', ':'), allow_nan=False).replace('<', r'\u003c')
    page = page.replace('__STAMP__', html.escape(datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')))
    page = page.replace('__SKIPPED__', str(skipped)).replace('__LIB__',asset.decode()).replace('__ROWS__',data)
    DEST.parent.mkdir(parents=True, exist_ok=True)
    temp = DEST.with_suffix('.partial')
    temp.write_text(page)
    temp.replace(DEST)
    print(len(rows), 'jobs;', skipped, 'unreadable;', DEST)


if __name__ == '__main__':
    main()
