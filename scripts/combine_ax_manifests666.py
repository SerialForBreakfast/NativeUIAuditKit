"""TRAIN666: combine frozen AX development snapshots into 1 tvbench manifest. Source snapshots stay unchanged.

Checks: same version, classes, baseline and split; none sealed or training-eligible; unique case IDs and pixels;
every case has an independent-layout ID; each label file still matches its pinned hash.
Usage: combine_ax_manifests666.py --manifest A.json B.json ... --out NEW.json
"""
import argparse
from pathlib import Path
import research_queue as q
from template_inputs398 import pin


def combine(paths, out):
    out = Path(out)
    q.require(not out.exists(), 'combined_out_exists')
    docs = [q.load(p) for p in paths]
    first = docs[0]
    for d in docs:
        q.require(d['version'] == first['version'] and d['classes'] == first['classes'] and d['baseline'] == first['baseline']
                  and d['split'] == 'development' and d['sealed'] is False and d['trainingEligible'] is False, 'combined_source_mismatch')
    cases, ids, pixels, apps = [], set(), set(), {}
    for d in docs:
        for c in d['cases']:
            q.require(c['id'] not in ids and c['pixelSHA256'] not in pixels, 'combined_duplicate_case')
            q.require(isinstance(c.get('independentLayoutId'), str) and c['independentLayoutId'], 'combined_missing_layout_id')
            q.require(q.digest(q.ROOT/c['labels']['path']) == c['labels']['sha256'], 'combined_label_changed')
            ids.add(c['id']); pixels.add(c['pixelSHA256']); cases.append(c)
        for a in d['apps']:
            apps[a['id']] = a
    doc = dict(version=first['version'], split='development', sealed=False, trainingEligible=False, pending=0,
               classes=first['classes'], baseline=first['baseline'], apps=sorted(apps.values(), key=lambda a: a['id']),
               sources=[pin(Path(p)) for p in paths], cases=cases,
               limitation='Development frames reviewed by Joe; not a sealed test. Results stay provisional until Joe reviews them.')
    q.save(out, doc)
    return dict(path=str(out), sha256=q.digest(out), cases=len(cases), layouts=len({(c['app'], c['independentLayoutId']) for c in cases}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--manifest', nargs='+', required=True); parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(combine(args.manifest, args.out))
