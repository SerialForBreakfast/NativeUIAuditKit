"""RESET604 T2.1: Bounded, fault-tolerant local Fixture batch runner for recipes-v1.

Runs `aatv fixture batch` in bounded chunks inside TVTestRig project mode, bisects single-recipe
`sceneNotSettled` failures so bad recipes are skipped and logged instead of aborting the batch,
copies accepted rows to NUIAK with SHA-256 verification, and preserves `held-out` family splits.
"""
import os
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import research_queue as q

DEFAULT_AATV = Path(os.environ.get('NUIAK_TTR_ROOT', Path.home() / 'Developer/TVTestRig')) / '.local-work/artparity595/DerivedData/Build/Products/Debug/TVTestRig.app/Contents/Helpers/aatv'
DEFAULT_PROJECT = Path(os.environ.get('NUIAK_TTR_ROOT', Path.home() / 'Developer/TVTestRig'))
DEFAULT_RECIPES = q.ROOT / 'reports/work/RESET604/recipes-v1'
DEFAULT_OUT = q.ROOT / 'dataset/tvos_captures/reset604/batch-v1'
DEFAULT_UDID = '9026ECA9-77DB-4AE6-8FE6-BB239E9571FA'
DEFAULT_URL = 'http://127.0.0.1:8080'


def parse_cli_json(stdout_text):
    """Extract the JSON payload emitted by `aatv` after diagnostic log lines."""
    lines = stdout_text.splitlines()
    for i, line in enumerate(lines):
        if line.lstrip().startswith('{'):
            return json.loads('\n'.join(lines[i:]))
    raise ValueError('fixture_runner_no_json_output')


def copy_verified_chunk(src_dir, dst_dir, row_lookup):
    """Copy accepted rows from TVTestRig output to NUIAK and verify PNG SHA-256 digests."""
    src_dir, dst_dir = Path(src_dir), Path(dst_dir)
    dst_dir.mkdir(parents=True, exist_ok=True)
    raw_manifest = json.loads((src_dir / 'manifest.json').read_text())
    entries = []
    mismatches = 0
    for item in raw_manifest:
        meta_rel = (item.get('metadata') or {}).get('metadataPath')
        if not meta_rel or not (src_dir / meta_rel).is_file():
            continue
        meta = json.loads((src_dir / meta_rel).read_text())
        if not meta.get('is_settled', False):
            continue
        rec_file = (item.get('metadata') or {}).get('recipeFile')
        rec_info = row_lookup.get(rec_file, {})
        fam = rec_info.get('family', 'unknown')
        split = 'test' if rec_info.get('role') == 'held-out' else item.get('split', 'training')

        shutil.copy2(src_dir / meta_rel, dst_dir / meta_rel)
        for png_key, sha_key in (('focused_png', 'focused_sha256'), ('unfocused_png', 'unfocused_sha256')):
            png_name = meta.get(png_key)
            if not png_name or not (src_dir / png_name).is_file():
                continue
            dst_png = dst_dir / png_name
            shutil.copy2(src_dir / png_name, dst_png)
            expected = meta.get(sha_key)
            if expected and q.digest(dst_png) != expected:
                mismatches += 1
        q.require(mismatches == 0, f'fixture_runner_copy_mismatch:{dst_dir.name}')
        entries.append(dict(item, category=fam.split(':', 1)[-1], family=fam, split=split))
    q.save(dst_dir / 'manifest.json', entries, replace=True)
    return entries


def invoke_aatv_batch(aatv, project, recipes_dir, out_dir, fixture_url, udid, timeout=900):
    cmd = [
        str(aatv),
        'fixture', 'batch',
        '--project', str(project),
        '--recipes-dir', str(recipes_dir),
        '--output-dir', str(out_dir),
        '--fixture-url', str(fixture_url),
        '--simulator-udid', str(udid),
        '--json',
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if res.returncode != 0:
        try:
            payload = parse_cli_json(res.stdout)
            # Keep TTR's structured failure (code/cause/stage); the log tail alone loses it.
            return False, payload.get('failure') or payload
        except Exception:
            return False, res.stdout + '\n' + res.stderr
    try:
        payload = parse_cli_json(res.stdout)
        return bool(payload.get('success')), payload
    except Exception as exc:
        return False, f'{exc}: {res.stdout[-400:]}'


def run_chunk_with_bisect(recipes, recipes_root, work_root, dst_chunk, row_lookup, aatv, project, fixture_url, udid, runner=invoke_aatv_batch):
    """Run a chunk of recipes; if it fails (`sceneNotSettled`), bisect down to isolate rejecting recipes."""
    stage_dir = work_root / dst_chunk.name
    rec_stage = stage_dir / 'recipes'
    if rec_stage.exists():
        shutil.rmtree(rec_stage)
    rec_stage.mkdir(parents=True)
    for rname in recipes:
        shutil.copy2(recipes_root / rname, rec_stage / rname)

    abs_out = project / '.local-work/reset604/batches' / dst_chunk.name / 'out'
    if abs_out.exists():
        shutil.rmtree(abs_out)

    ok, detail = runner(aatv, project, rec_stage, abs_out, fixture_url, udid)
    if ok:
        accepted = copy_verified_chunk(abs_out, dst_chunk, row_lookup)
        return accepted, []
    if len(recipes) == 1:
        return [], [dict(recipe=recipes[0], error=(json.dumps(detail, sort_keys=True) if isinstance(detail, dict) else str(detail))[-400:])]

    mid = len(recipes) // 2
    a1, rej1 = run_chunk_with_bisect(recipes[:mid], recipes_root, work_root, dst_chunk.with_name(dst_chunk.name + '_a'), row_lookup, aatv, project, fixture_url, udid, runner=runner)
    a2, rej2 = run_chunk_with_bisect(recipes[mid:], recipes_root, work_root, dst_chunk.with_name(dst_chunk.name + '_b'), row_lookup, aatv, project, fixture_url, udid, runner=runner)
    return a1 + a2, rej1 + rej2


def run_batches(recipes_dir=DEFAULT_RECIPES, out_dir=DEFAULT_OUT, batch_size=15, start=0, count=15,
                skip_families=None, aatv=DEFAULT_AATV, project=DEFAULT_PROJECT, fixture_url=DEFAULT_URL, udid=DEFAULT_UDID):
    recipes_dir, out_dir = Path(recipes_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    index = q.load(recipes_dir / 'index.json')
    row_lookup = {r['recipe']: r for r in index['rows']}
    skip_set = set(skip_families or ())
    target_rows = index['rows'][start:start + count] if count > 0 else index['rows'][start:]
    work_root = project / '.local-work/reset604/batches'
    work_root.mkdir(parents=True, exist_ok=True)

    state_path = out_dir / 'runner-state.json'
    state = q.load(state_path) if state_path.is_file() else dict(completedChunks={}, rejected=[], totalAcceptedRows=0)

    all_accepted, all_rejected = [], list(state.get('rejected', []))
    for offset in range(0, len(target_rows), batch_size):
        slice_rows = target_rows[offset:offset + batch_size]
        chunk_rows = [r for r in slice_rows if r.get('family') not in skip_set]
        skipped_rows = [r for r in slice_rows if r.get('family') in skip_set]
        chunk_base = f'c{start + offset:04d}'
        spec_payload = dict(
            chunk=chunk_base,
            recipes=[r['recipe'] for r in chunk_rows],
            skipped=[r['recipe'] for r in skipped_rows],
            skipFamilies=sorted(skip_set),
        )
        chunk_hash = hashlib.sha256(json.dumps(spec_payload, sort_keys=True).encode()).hexdigest()[:12]
        chunk_key = f'{chunk_base}-{chunk_hash}'
        dst_chunk = out_dir / chunk_key
        if chunk_key in state['completedChunks']:
            continue
        if not chunk_rows:
            state['completedChunks'][chunk_key] = dict(
                chunk=chunk_base,
                specHash=chunk_hash,
                recipes=0,
                acceptedRows=0,
                rejectedRecipes=[],
                skippedRecipes=[r['recipe'] for r in skipped_rows],
            )
            q.save(state_path, state, replace=True)
            continue
        recipes = [r['recipe'] for r in chunk_rows]
        acc, rej = run_chunk_with_bisect(recipes, recipes_dir, work_root, dst_chunk, row_lookup, aatv, project, fixture_url, udid)
        all_accepted.extend(acc)
        all_rejected.extend(rej)
        state['completedChunks'][chunk_key] = dict(
            chunk=chunk_base,
            specHash=chunk_hash,
            recipes=len(recipes),
            acceptedRows=len(acc),
            rejectedRecipes=[x['recipe'] for x in rej],
            skippedRecipes=[r['recipe'] for r in skipped_rows],
        )
        state['rejected'] = all_rejected
        state['totalAcceptedRows'] = state.get('totalAcceptedRows', 0) + len(acc)
        q.save(state_path, state, replace=True)

    return dict(
        outDir=str(out_dir),
        processedRecipes=len(target_rows),
        newAcceptedRows=len(all_accepted),
        totalAcceptedRows=state['totalAcceptedRows'],
        rejectedCount=len(all_rejected),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recipes-dir', type=Path, default=DEFAULT_RECIPES)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    parser.add_argument('--batch-size', type=int, default=15)
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--count', type=int, default=15, help='Number of recipes to process (0 = all)')
    parser.add_argument('--skip-families', nargs='*', default=[], help='Families to skip (e.g. plain:grid_matrix plain:settings_list)')
    args = parser.parse_args()
    print(json.dumps(run_batches(
        args.recipes_dir, args.out, args.batch_size, args.start, args.count, skip_families=args.skip_families,
    ), indent=2))


if __name__ == '__main__':
    main()
