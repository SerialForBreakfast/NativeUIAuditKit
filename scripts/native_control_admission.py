"""Admit native controls with observed focus and explicit group roles.

This variant does not require a visual difference between accessibility profiles.
It preserves the artwork admission rules in hcf_study371.
"""
from pathlib import Path
import hashlib
import json

from PIL import Image
import research_queue as q
import native343
import native_coverage402 as coverage
import hcf_study371 as study
from hcf_spatial_audit import body_bounds

OUT = None
VERSION = 'native-control-admission-v1'


def layout_identity(case):
    comp = case['recipe']['appearance']['composition']
    return q.text_digest(dict(family=case['family'], definitions=comp['definitions'],
        regions=[dict(frame=r['frame'], axis=r['axis'], gap=r['gap'],
                      components=[i['component'] for i in r['items']]) for r in comp['regions']]))


def admit_artifact(artifact, roles, root, source_id):
    """Validate a complete capture before applying a separate role overlay."""
    path = Path(artifact['path'])
    q.require(path.resolve().is_relative_to(root.resolve()), 'native_capture_scope')
    q.require(q.digest(path) == artifact['sha256'], 'native_capture_changed')
    plan = artifact['plan']
    coverage.validate_controls(plan)
    doc = q.load(path)
    q.require(doc.get('version') == coverage.CONTROLS_VERSION and doc.get('complete') is True
              and doc.get('cleanup') is True, 'native_capture_incomplete')
    cases = {c['id']: c for c in plan['cases']}
    q.require(set(roles) == {c['group'] for c in cases.values()}, 'native_role_membership')
    q.require(set(roles.values()) <= {'train', 'development'}, 'native_role_invalid')
    expected = {(c['id'], p, t) for c in cases.values() for p in plan['profiles'] for t in c['targets']}
    seen, rows = set(), []
    for frame in doc['frames']:
        key = (frame['case'], frame['profile'], frame['focus'])
        q.require(key in expected and key not in seen and frame['repeat'] == 0, 'native_frame_membership')
        seen.add(key)
        case = cases[frame['case']]
        before, after = frame['before'], frame['after']
        import dataset351
        q.require(dataset351.clean(before['scene']['recipe']) == case['recipe'], 'native_recipe_changed')
        q.require(before['device']['simulator_udid'] == plan['binding']['simulatorUDID'], 'native_target_changed')
        q.require(native343.signature(before, before, frame['focus']) ==
                  native343.signature(after, before, frame['focus']), 'native_interval_changed')
        q.require(before['finishedAt'] <= frame['start'] <= frame['end'] <= after['startedAt'],
                  'native_capture_interval')
        import hcf_capture362
        hcf_capture362.verified_profile(frame['profileReceipt']['receipt'], frame['profile'])
        boxes = body_bounds(frame)
        planned = before['scene']['focus_observation']['plannedFocusIDs']
        boxes = {k: v for k, v in boxes.items() if k in planned}
        q.require(set(boxes) == set(planned) and frame['focus'] in boxes, 'native_controls_missing')
        image = q.local_path(path.parent, frame['path'])
        q.require(q.digest(image) == frame['sha256'], 'native_image_changed')
        with Image.open(image) as im:
            rgb = im.convert('RGB')
            width, height = rgb.size
            pixels = hashlib.sha256(rgb.tobytes()).hexdigest()
        q.require([width, height] == [before['scene']['scene_width'], before['scene']['scene_height']],
                  'native_image_size')
        for x, y, w, h in boxes.values():
            q.require(0 <= x and 0 <= y and w > 0 and h > 0 and x+w <= width+.1 and y+h <= height+.1,
                      'native_body_bounds')
        # Prefix frame identities across independently published captures.
        rows.append(dict(id=source_id+'-'+frame['id'], sourceFrame=frame['id'], path=str(image),
            sha256=frame['sha256'], decodedSHA256=pixels, width=width, height=height,
            boxes=boxes, focus=frame['focus'], profile=frame['profile'], role=roles[case['group']],
            group=case['group'], family=case['family'], theme=case['theme'], case=case['id'],
            layoutSHA256=layout_identity(case)))
    q.require(seen == expected and len(rows) == plan['expectedFrames'], 'native_capture_membership')
    return rows


def validate_partition(rows):
    """Identical profile pixels are valid only with identical labels and one role."""
    q.require(bool(rows), 'native_empty_membership')
    groups, pixels, layouts = {}, {}, {}
    q.require(len({r['id'] for r in rows}) == len(rows), 'native_duplicate_id')
    for row in rows:
        role = row['role']
        q.require(role in ('train', 'development'), 'native_role_invalid')
        q.require(groups.setdefault(row['group'], role) == role, 'native_group_leak')
        if 'layoutSHA256' in row:
            q.require(layouts.setdefault(row['layoutSHA256'], role) == role, 'native_layout_leak')
        label = (row['focus'], q.text_digest(row['boxes']))
        previous = pixels.setdefault(row['decodedSHA256'], (role, label))
        q.require(previous[0] == role, 'native_pixel_leak')
        q.require(previous[1] == label, 'native_pixel_label_conflict')
    return dict(groups={role: len({r['group'] for r in rows if r['role'] == role})
                        for role in ('train', 'development')}, uniqueFrames=len(pixels))


def run():
    from template_adapters395 import resolve_inputs, document
    cfg = q.load(OUT.parents[2]/'spec.json')['template']
    refs = resolve_inputs(cfg, OUT)
    config = document(refs['configuration'])
    decision = document(refs['decision'])
    q.require(config.get('version') == VERSION, 'native_admission_version')
    q.require(set(config) == {'version', 'sources'} and bool(config['sources']), 'native_admission_fields')
    q.require(len({s['id'] for s in config['sources']}) == len(config['sources']), 'native_source_duplicate')
    q.require(decision.get('approvedDerivedRole') == 'train', 'native_training_authority')
    allowed = set(decision['sourceGroups'])
    rows, sources = [], []
    for source in config['sources']:
        ref = source['artifact']
        path = q.local_path(q.ROOT, ref['path'])
        q.require(q.digest(path) == ref['sha256'], 'native_artifact_changed')
        artifact = q.load(path)
        root = study.verify_storage(artifact['storage'])
        roles = source['roles']
        if 'train' in roles.values():
            q.require(source['id'] in decision['sourceJobs'], 'native_unapproved_source')
            q.require(ref['sha256'] == decision['sourceArtifactSHA256'][source['id']], 'native_authority_source_changed')
        q.require({g for g, r in roles.items() if r == 'train'} <= allowed, 'native_unapproved_training_group')
        q.require(not {g for g, r in roles.items() if r == 'development'} & allowed,
                  'native_training_source_in_development')
        rows.extend(admit_artifact(artifact, roles, root, source['id']))
        sources.append(ref)
    summary = validate_partition(rows)
    q.save(OUT/'admission.json', dict(version=VERSION, rows=rows, storage=artifact['storage'],
        sources=sources, trainingAdmitted=True, roleDecisionSHA256=q.text_digest(decision),
        limitation='Native-control source admission. Separate development layouts and crop duplicate checks remain required.'))
    q.save(OUT/'summary.json', dict(**summary, frames=len(rows), modelAccepted=False))
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=n, sha256=q.digest(OUT/n)) for n in ('admission.json', 'summary.json')]))
