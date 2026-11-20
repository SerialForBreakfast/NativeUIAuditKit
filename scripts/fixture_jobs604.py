"""RESET604 T2.1: capture Fixture recipes locally through TTR app-managed jobs (prepare, run-job, job-status, export-job).

Use this when the running TTR app is in app-managed mode: `fixture batch` then refuses an output directory outside its own storage.
Each recipe becomes 1 job on 1 exact Simulator. A failed job is recorded and not retried. Exports go to a new directory per recipe.
The sandboxed helper cannot write outside TTR storage (`export-job` gives access_denied), so this tool reads each file in chunks
(`fixture read-job`) and checks its size and SHA-256 against the job manifest.
The caller must check Simulator ownership, idle state and system alerts first (tvtestrig skill). Data role comes from --split.
Usage: fixture_jobs604.py --aatv HELPER --recipes DIR --out NEW_DIR --simulator-udid UUID [--fixture-url URL] [--split training] [--limit N]
"""
import argparse
import base64
import hashlib
import json
import subprocess
import time
from pathlib import Path

TERMINAL = ('completed', 'failed', 'cancelled', 'interrupted')


def call(aatv, *args, timeout=60):
    p = subprocess.run([str(aatv), '--json', '--timeout-ms', '30000', *args], capture_output=True, text=True, timeout=timeout)
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        return dict(success=False, error=dict(code='unparsed', message=p.stdout[:300]))


def job(doc):
    return (doc.get('data') or {}).get('fixtureJob', {}).get('_0', {})


def export(aatv, uid, dest):
    """Copy every manifest file of 1 completed job into `dest`. Return (files, bytes). Raise on any size or hash mismatch."""
    files = job(call(aatv, 'fixture', 'job-manifest', uid)).get('files', [])
    dest.mkdir(parents=True, exist_ok=False); total = 0
    for f in files:
        name = f['path']
        if name != Path(name).name or name in ('.', '..'):
            raise ValueError('unsafe_job_path:' + name)
        data = bytearray()
        while len(data) < f['bytes']:
            chunk = (call(aatv, 'fixture', 'read-job', uid, '--path', name, '--offset', str(len(data))).get('data') or {}).get('fixtureJobChunk', {}).get('_0')
            part = base64.b64decode(chunk['data']) if chunk else b''
            if not part:
                raise ValueError('job_chunk_unavailable:' + name)
            data += part
        if len(data) != f['bytes'] or hashlib.sha256(data).hexdigest() != f['sha256']:
            raise ValueError('job_file_mismatch:' + name)
        (dest/name).write_bytes(data); total += len(data)
    return len(files), total


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--aatv', type=Path, required=True); parser.add_argument('--recipes', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True); parser.add_argument('--simulator-udid', required=True)
    parser.add_argument('--fixture-url', default='http://127.0.0.1:8080'); parser.add_argument('--split', default='training')
    parser.add_argument('--limit', type=int, default=0); parser.add_argument('--wait', type=int, default=300)
    parser.add_argument('--skip', type=int, default=0)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False); rows = []; start = time.time()
    recipes = sorted(args.recipes.glob('*.json'))[args.skip:][:args.limit or None]
    for recipe in recipes:
        t0 = time.time(); row = dict(recipe=recipe.name)
        doc = call(args.aatv, 'fixture', 'prepare', '--recipe-json', json.dumps(json.loads(recipe.read_text())), '--split', args.split)
        uid = job(doc).get('jobID')
        if not uid:
            row.update(state='prepare_failed', error=doc.get('error')); rows.append(row); continue
        call(args.aatv, 'fixture', 'run-job', uid, '--simulator-udid', args.simulator_udid, '--fixture-url', args.fixture_url)
        state = {}
        while time.time() - t0 < args.wait:
            state = job(call(args.aatv, 'fixture', 'job-status', uid))
            if state.get('state') in TERMINAL:
                break
            time.sleep(2)
        row.update(job=uid, state=state.get('state'), failure=state.get('failure'), files=len(state.get('files', [])))
        if state.get('state') == 'completed':
            dest = args.out/recipe.stem
            row['captureSeconds'] = round(time.time() - t0, 1)
            try:
                count, size = export(args.aatv, uid, dest)
                row.update(exported=True, exportedFiles=count, exportedBytes=size, images=len(list(dest.glob('*.png'))))
            except (ValueError, KeyError, OSError) as error:
                row.update(exported=False, exportError=str(error))
        row['seconds'] = round(time.time() - t0, 1); rows.append(row)
        print(json.dumps(row)[:300], flush=True)
    summary = dict(version='fixture-jobs604-v1', simulatorUDID=args.simulator_udid, split=args.split, recipes=len(recipes),
                   completed=sum(r.get('state') == 'completed' for r in rows), images=sum(r.get('images', 0) for r in rows),
                   seconds=round(time.time() - start, 1), rows=rows)
    (args.out/'session.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: v for k, v in summary.items() if k != 'rows'}))


if __name__ == '__main__':
    main()
