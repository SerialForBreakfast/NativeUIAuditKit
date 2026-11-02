"""RC561-01: measure SDK label accuracy per app from SDK drafts and the maintainer's validate-and-flag review.

A draft object has provenance `sdk-draft:<sdk id>`. The reviewed label keeps it (maybe moved or reclassified), deletes it, or the
reviewer adds an object the SDK missed (provenance `reviewer`). Classes compare as ROLES559 roles.
Gates (REALCORPUS561): coverage ≥ 0.95; median IoU ≥ 0.90 and ≥ 95% at IoU ≥ 0.75; role agreement ≥ 0.98;
no false registrations above 2%; focus agreement on every frame; at least 10 frames from 4 flows.
Stability needs a repeated capture and stays `not measured` without `--repeats`.
Usage: sdk_qualification561.py --drafts DIR --labels DIR --out NEW_JSON [--app PREFIX]
"""
import argparse
import collections
import json
import statistics
from pathlib import Path
from perception_benchmark import _iou
from roles559 import role

GATES = dict(coverage=.95, medianIoU=.90, shareIoU75=.95, roleAgreement=.98, falseRegistrations=.02, frames=10, flows=4)


def load(path):
    return json.loads(Path(path).read_text())


def frame_result(draft, label):
    drafts = {o['id']: o for o in draft['objects'] if o['provenance'].startswith('sdk-draft:')}
    final = {o['id']: o for o in label['objects']}
    # Validate-and-flag reviews flag errors instead of editing: `not-control` counts as deleted, `wrong-box` as IoU 0, `wrong-class` as a role error.
    kept = [i for i in drafts if i in final and final[i].get('flag') != 'not-control']
    added = [o for o in label['objects'] if not o['provenance'].startswith('sdk-draft:')]
    ious = [0.0 if final[i].get('flag') == 'wrong-box' else _iou(drafts[i]['box'], final[i]['box']) for i in kept]
    roles = [final[i].get('flag') != 'wrong-class' and role(drafts[i]['class']) == role(final[i]['class']) for i in kept]
    dfocus, ffocus = draft.get('focus', {}), label.get('focus', {})
    if ffocus.get('state') == 'focused':
        focus = dfocus.get('state') == 'focused' and _iou(dfocus['box'], ffocus['box']) >= .5
    else:
        focus = dfocus.get('state') == ffocus.get('state')
    return dict(drafts=len(drafts), kept=len(kept), deleted=len(drafts) - len(kept), added=len(added), ious=ious, roles=roles,
                focusAgrees=focus, draftFocus=dfocus.get('state'), reviewedFocus=ffocus.get('state'),
                addedClasses=[str(role(o['class']) or o['class']) for o in added])


def app_of(name):
    return name.split('-')[0]


def flow_of(name):
    parts = name.split('-')
    return '-'.join(parts[:3]) if len(parts) > 2 else name


def qualify(drafts_dir, labels_dir, prefix=None):
    apps = collections.defaultdict(list)
    for label_path in sorted(Path(labels_dir).glob('*.json')):
        name = label_path.stem
        if prefix and not name.startswith(prefix):
            continue
        draft_path = Path(drafts_dir)/label_path.name
        label = load(label_path)
        if 'objects' not in label or not draft_path.is_file():
            continue
        apps[app_of(name)].append((name, frame_result(load(draft_path), label)))
    out = {}
    for app, frames in apps.items():
        ious = [v for _, f in frames for v in f['ious']]; roles = [v for _, f in frames for v in f['roles']]
        kept = sum(f['kept'] for _, f in frames); added = sum(f['added'] for _, f in frames); drafts = sum(f['drafts'] for _, f in frames)
        deleted = sum(f['deleted'] for _, f in frames)
        m = dict(frames=len(frames), flows=len({flow_of(n) for n, _ in frames}), sdkBoxes=drafts, kept=kept, deleted=deleted, missed=added,
                 coverage=round(kept/(kept+added), 4) if kept + added else None,
                 medianIoU=round(statistics.median(ious), 4) if ious else None,
                 shareIoU75=round(sum(v >= .75 for v in ious)/len(ious), 4) if ious else None,
                 roleAgreement=round(sum(roles)/len(roles), 4) if roles else None,
                 falseRegistrations=round(deleted/drafts, 4) if drafts else None,
                 focusAgreement=f"{sum(f['focusAgrees'] for _, f in frames)}/{len(frames)}",
                 focusStates=dict(collections.Counter(f"{f['draftFocus']}->{f['reviewedFocus']}" for _, f in frames).most_common()),
                 missedRoles=dict(collections.Counter(c for _, f in frames for c in f['addedClasses'])),
                 stability='not measured')
        checks = dict(coverage=m['coverage'] is not None and m['coverage'] >= GATES['coverage'],
                      geometry=m['medianIoU'] is not None and m['medianIoU'] >= GATES['medianIoU'] and m['shareIoU75'] >= GATES['shareIoU75'],
                      role=m['roleAgreement'] is not None and m['roleAgreement'] >= GATES['roleAgreement'],
                      falseRegistrations=m['falseRegistrations'] is not None and m['falseRegistrations'] <= GATES['falseRegistrations'],
                      focus=all(f['focusAgrees'] for _, f in frames),
                      sample=m['frames'] >= GATES['frames'] and m['flows'] >= GATES['flows'])
        m['checks'] = checks
        m['qualified'] = all(checks.values())
        m['failures'] = [k for k, v in checks.items() if not v]
        out[app] = m
    return dict(version='sdk-qualification561-v1', gates=GATES, apps=out)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--drafts', type=Path, required=True); parser.add_argument('--labels', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True); parser.add_argument('--app')
    args = parser.parse_args()
    result = qualify(args.drafts, args.labels, args.app)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    for app, m in result['apps'].items():
        print(app, 'qualified' if m['qualified'] else 'not qualified', m['failures'],
              {k: m[k] for k in ('frames', 'flows', 'kept', 'missed', 'deleted', 'coverage', 'medianIoU', 'roleAgreement', 'focusAgreement')})


if __name__ == '__main__':
    main()
