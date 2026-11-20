"""TRAIN666 W1: build the 10-class D1 baseline membership from an existing legacy-label membership.

Source rows keep their images, groups, roles and boxes. Classes are re-ordered to the contract class order
(`framework_projection604.tvos_classes()`). A row that holds a control of a removed role (`adjustable`,
`container`) is dropped whole: an unlabelled visible control would train as background.
Labels stay legacy (ID-prefix generator and Fixture `taxonomy_class`). This membership is a baseline, not a release input.
Usage: d1_membership666.py [--source .../v3-d1/membership.json] [--out reports/work/TRAIN666/membership/d1-10class]
"""
import argparse
import json
from collections import Counter
from pathlib import Path

import framework_projection604 as fp
import research_queue as q
from template_inputs398 import pin

DEFAULT_SOURCE = q.ROOT / 'reports/work/RESET604/membership/v3-d1/membership.json'
DEFAULT_OUT = q.ROOT / 'reports/work/TRAIN666/membership/d1-10class'


def build(source=DEFAULT_SOURCE, out=DEFAULT_OUT):
    source, out = Path(source), Path(out)
    doc = q.load(source)
    names = fp.tvos_classes()
    removed = set(doc['names']) - set(names)
    q.require(set(names) >= set(doc['names']) - removed and removed <= {'adjustable', 'container'}, 'd1_membership666_unexpected_classes')
    rows, dropped = [], Counter()
    for row in doc['rows']:
        hit = {c['class'] for c in row['controls']} & removed
        if hit:
            dropped[(row['role'], '+'.join(sorted(hit)))] += 1
            continue
        rows.append(row)
    counts = Counter(c['class'] for r in rows for c in r['controls'])
    new = dict(doc, names=names, rows=rows, membershipVersion='train666-d1-10class-v1', mode='d1',
               calibrationGroups=sorted({r['group'] for r in rows if r['role'] == 'calibration'}),
               targetScope='TRAIN666 W1 baseline: 10 tvOS contract classes, legacy labels.',
               limitation=doc.get('limitation', '') + ' Legacy labels (not framework-qualified). Rows with adjustable/container controls dropped.',
               source=pin(source), contractSha256=fp.load_contract()[1])
    path = out / 'membership.json'
    q.require(not path.exists(), f'd1_membership666_immutable_target_exists:{path}')
    out.mkdir(parents=True, exist_ok=True)
    q.save(path, new)
    audit = dict(version='d1-membership666-audit-v1', source=pin(source), membership=pin(path), names=names,
                 rows=len(rows), roles=dict(Counter(r['role'] for r in rows)), sourceRoles=dict(Counter(r.get('sourceRole') for r in rows)),
                 droppedRows={f'{k[0]}:{k[1]}': v for k, v in dropped.items()}, classCounts=dict(counts),
                 unsupportedClasses=[n for n in names if counts[n] == 0],
                 focusStates=dict(Counter(r.get('focusState') for r in rows)))
    q.save(out / 'audit.json', audit)
    return audit


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--source', type=Path, default=DEFAULT_SOURCE)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.out), indent=2))
