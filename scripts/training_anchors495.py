"""Select unchanged training anchors from an explicit retained source manifest."""
from pathlib import Path
import research_queue as q

OUT = None
FIELDS = ('path', 'sha256', 'role', 'label', 'group', 'profile')


def select(membership, original, excluded):
    source = {r['id']: r for r in original['rows']}
    q.require(len(source) == len(original['rows']), 'anchor_source_duplicate')
    rows = membership['rows']
    q.require(len({r['id'] for r in rows}) == len(rows), 'anchor_membership_duplicate')
    anchors = []
    for row in rows:
        if row['role'] != 'train': continue
        origin = source.get(row.get('sourceID', row['id']))
        if origin is None: continue
        q.require(all(row.get(k) == origin.get(k) for k in FIELDS), 'anchor_source_mismatch')
        q.require(row['group'] not in excluded, 'anchor_evaluation_overlap')
        q.require(q.digest(Path(row['path'])) == row['sha256'], 'anchor_crop_changed')
        anchors.append(row)
    q.require(anchors and {r['label'] for r in anchors} == {0, 1}, 'anchor_class_support')
    return dict(version='teacher-anchors-v1', rows=anchors)


def run():
    from template_adapters395 import resolve_inputs, document
    cfg = q.load(OUT.parents[2]/'spec.json')['template']
    refs = resolve_inputs(cfg, OUT)
    result = select(document(refs['membership']), document(refs['original']),
                    document(refs['suite'])['excludedGroups'])
    q.save(OUT/'anchors.json', result)
    q.save(OUT/'summary.json', dict(anchorRows=len(result['rows']),
        groups=len({r['group'] for r in result['rows']}), trainingOnly=True, modelAccepted=False))
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=name, sha256=q.digest(OUT/name)) for name in ('anchors.json', 'summary.json')]))
