"""RA557-01: compare 4K and 1080p input for the NewsTV pilot frames on the same runtime.

Downscales each 4K frame to 1920 x 1080 (Lanczos), replays it through `aatv visual replay`,
scales the boxes back to 4K pixels, and scores both with the REAL543 matching and official COCO code.
The 4K pilot results stay unchanged. Downscaled inputs and exports stay in the TTR work folder and the project.
Usage: real_app_resolution557.py --out NEW_DIR
"""
import argparse
import json
from pathlib import Path
from PIL import Image
import research_queue as q
import real_app_session554 as s
import real_app_benchmark543 as b

R = q.ROOT/'reports/work/REALAPP554'


def detections(export, scale):
    provider = q.load(export/'result.json')['receipt']['provider']
    return [{'class': e['role'], 'box': [v*scale for v in e['pixels']], 'score': e['confidence']} for e in provider['elements']]


def score(rows, classes):
    out = []
    for row in rows:
        above = [d for d in row['detections'] if d['score'] >= .5]
        known, found, extra, wrong, loc = b.match(row['label'], above, .5)
        out.append(dict(id=row['id'], status='ok', complete=row['label']['complete'], unresolved=len(row['label']['objects'])-len(known),
                        objects=known, allDetections=row['detections'], found=len(found), known=len(known), wrong=wrong, loc=loc))
    coco = b.official_ap(out, classes)
    return dict(recall=f"{sum(r['found'] for r in out)}/{sum(r['known'] for r in out)}", wrongClass=sum(r['wrong'] for r in out),
                localization=sum(r['loc'] for r in out), coco=coco.get('metrics'))


def build(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=False)
    manifest = q.load(R/'pilot-v2/manifest.json')
    classes = manifest['classes']
    replays = q.load(R/'replays/replays.json')
    export = {c: q.ROOT/f['export'] for f in replays['frames'] for c in f['cases']}
    work = s.LOCAL/'realapp557-1080p'; work.mkdir(parents=True, exist_ok=False)
    cases = [c for c in manifest['cases'] if c['status'] == 'captured']
    code, before = s.aatv('features', 'status', out=out, name='features-before')
    enabled = next(iter(before['data'].values()))['_0']['enabled']
    code, status = s.aatv('status', out=out, name='status-before')
    q.require(next(iter(status['data'].values()))['_0'].get('commandActive') is False, 'ttr_busy')
    rows4k, rows1080 = [], []
    try:
        if not enabled:
            code, reply = s.aatv('features', 'set', 'nuiak', 'on', out=out, name='features-enabled')
            q.require(code == 0 and reply.get('success'), 'feature_enable_failed')
        for case in cases:
            label = q.load(q.ROOT/case['labels']['path'])
            rows4k.append(dict(id=case['id'], label=label, detections=detections(export[case['id']], 1)))
            small = work/f"{case['id']}.png"
            with Image.open(q.ROOT/case['image']['path']) as im:
                im.convert('RGB').resize((1920, 1080), Image.Resampling.LANCZOS).save(small)
            sha = q.digest(small)
            manifest_path = work/f"{case['id']}-input.json"; manifest_path.write_text(json.dumps(dict(source_sha256=sha)))
            target = work/f"{case['id']}-replay"
            code, reply = s.aatv('visual', 'replay', '--source', str(small.relative_to(s.TTR)), '--manifest', str(manifest_path.relative_to(s.TTR)),
                                 '--output', str(target.relative_to(s.TTR)), out=out, name=f"{case['id']}-response")
            q.require(code == 0 and reply.get('success'), 'replay_failed:'+case['id'])
            import shutil
            shutil.copytree(target, out/'replays'/case['id'])
            rows1080.append(dict(id=case['id'], label=label, detections=detections(out/'replays'/case['id'], 2)))
    finally:
        restored = None
        if not enabled:
            code, reply = s.aatv('features', 'set', 'nuiak', 'off', out=out, name='features-restored')
            restored = code == 0 and reply.get('success')
    doc = dict(version='realapp557-resolution-v1', frames=len(cases), featureRestored=restored,
               input4k=score(rows4k, classes), input1080p=score(rows1080, classes),
               note='1080p input is a Lanczos downscale of the 4K capture, not a native 1080p render. Boxes are scaled by 2 before scoring.')
    q.save(out/'resolution.json', doc)
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, required=True)
    doc = build(parser.parse_args().out)
    print(json.dumps({k: doc[k] for k in ('frames', 'featureRestored', 'input4k', 'input1080p')}, indent=1))


if __name__ == '__main__':
    main()
