"""TRAIN666 H3 arm F: build the D1 membership plus 1 `focused` class (11 classes).

Source rows are the D1 10-class rows, unchanged. Each D1 row with `focusState == 'focused'` gets the single
`focused` box of the same row (same id and image hash) from `v3-focus-supervision`. `no_focus` rows keep no
`focused` box. Rows with `unknown` or `ambiguous` focus are dropped: without a `focused` box they would train
"no control is focused", and missing focus is unknown, never no focus. Joe approved this 5,063-row set in chat
on 2026-11-22 ("Approve both, start"). Plan: Research/Plans/H3Focus666.md.
Usage: h3_focused_membership666.py [--out reports/work/TRAIN666/membership/d1-focused-11class]
"""
import argparse
import json
from collections import Counter
from pathlib import Path

import research_queue as q
from template_inputs398 import pin

D1 = q.ROOT / 'reports/work/TRAIN666/membership/d1-10class/membership.json'
FOCUS = q.ROOT / 'reports/work/RESET604/membership/v3-focus-supervision/membership.json'
DEFAULT_OUT = q.ROOT / 'reports/work/TRAIN666/membership/d1-focused-11class'
KEEP = {'focused', 'no_focus'}


def focused_rows(d1, focus):
    """Return (rows, dropped) for the 11-class membership. Pure; raises on any mismatch."""
    index = {r['id']: r for r in focus['rows']}
    rows, dropped = [], Counter()
    for row in d1['rows']:
        state = row.get('focusState')
        if state not in KEEP:
            dropped[f"{row['role']}:{state}"] += 1
            continue
        source = index.get(row['id'])
        q.require(source is not None and source['image']['sha256'] == row['image']['sha256']
                  and source.get('focusState') == state, f"h3_focus_source_mismatch:{row['id']}")
        boxes = [c for c in source['controls'] if c['class'] == 'focused']
        if state == 'focused':
            q.require(len(boxes) == 1, f"h3_focus_box_count:{row['id']}:{len(boxes)}")
            controls = row['controls'] + [dict(boxes[0], id='focused')]
        else:
            q.require(not boxes, f"h3_no_focus_has_box:{row['id']}")
            controls = list(row['controls'])
        rows.append(dict(row, controls=controls))
    return rows, dropped


def build(out=DEFAULT_OUT, d1_path=D1, focus_path=FOCUS):
    out = Path(out)
    d1, focus = q.load(d1_path), q.load(focus_path)
    q.require('focused' not in d1['names'], 'h3_d1_has_focused')
    rows, dropped = focused_rows(d1, focus)
    names = d1['names'] + ['focused']
    new = dict(d1, names=names, rows=rows, membershipVersion='train666-d1-focused-11class-v1', mode='d1-focused',
               calibrationGroups=sorted({r['group'] for r in rows if r['role'] == 'calibration'}),
               targetScope='TRAIN666 H3 arm F: D1 10 tvOS contract classes plus 1 focused-control box, legacy labels.',
               limitation=d1.get('limitation', '') + ' Rows with unknown or ambiguous focus dropped.',
               source=dict(d1=pin(Path(d1_path)), focus=pin(Path(focus_path))))
    path = out / 'membership.json'
    q.require(not path.exists(), f'h3_membership_immutable_target_exists:{path}')
    out.mkdir(parents=True, exist_ok=True)
    q.save(path, new)
    counts = Counter(c['class'] for r in rows for c in r['controls'])
    audit = dict(version='h3-focused-membership666-audit-v1', membership=pin(path), source=new['source'], names=names,
                 rows=len(rows), roles=dict(Counter(r['role'] for r in rows)),
                 focusStates={f'{k[0]}:{k[1]}': v for k, v in Counter((r['role'], r['focusState']) for r in rows).items()},
                 droppedRows=dict(dropped), classCounts=dict(counts),
                 unsupportedClasses=[n for n in names if counts[n] == 0])
    q.save(out / 'audit.json', audit)
    return audit


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    print(json.dumps(build(parser.parse_args().out), indent=2))
