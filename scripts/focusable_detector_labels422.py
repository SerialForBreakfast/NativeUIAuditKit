"""Qualify exhaustive labels for three Fixture control kinds, not general UI labels.

Preparation only. Reuse T89 for training after this manifest passes qualification.
"""
import argparse
from pathlib import Path
from collections import Counter
import research_queue as q
from template_inputs398 import checked, pin
from native_control_admission import validate_partition
from detector_native_inputs import bounds

CLASSES = {'button': 'primaryButton', 'row': 'listRow', 'tab': 'menuButton'}


def controls(scene, row):
    composition = scene['recipe']['appearance']['composition']
    items = [i for r in composition['regions'] for i in r['items']]
    ids = [i['id'] for i in items]
    elements = scene['elements']
    q.require(len(ids) == len(set(ids)) and len(elements) == len(ids), 'labels_inventory_count')
    by_id = {e['id']: e for e in elements}
    q.require(set(ids) == set(by_id) == set(row['boxes']) ==
              set(scene['focus_observation']['plannedFocusIDs']), 'labels_inventory_missing')
    q.require(scene['focus_observation']['verified'] is True and
              scene['focus_observation']['observedID'] == row['focus'], 'labels_unknown_focus')
    labels = []
    for item in items:
        definition = composition['definitions'][item['component']]
        kind = definition['kind']
        q.require(kind in CLASSES, 'labels_unsupported_component')
        element = by_id[item['id']]
        q.require(element['is_hidden'] is False and element['taxonomy_class'] == CLASSES[kind], 'labels_class_or_visibility')
        g = element['rendered_body_geometry']
        q.require(g['availability'] == 'measured' and g['coordinate_space'] == 'image_top_left_pixels'
                  and g['source'] == 'native_body_presentation_layer', 'labels_geometry_source')
        box = bounds(g['full_pixel_bounds'], row['width'], row['height'])
        q.require(box == row['boxes'][item['id']], 'labels_geometry_changed')
        labels.append(dict(id=item['id'], **{'class': CLASSES[kind]}, bounds=box))
    return labels


def prepare(admission_ref, calibration_groups, frame_refs):
    admission = q.load(checked(admission_ref))
    q.require(admission.get('trainingAdmitted') is True, 'labels_not_admitted')
    validate_partition(admission['rows'])
    train = [r for r in admission['rows'] if r['role'] == 'train']
    train_groups = {r['group'] for r in train}
    q.require(not calibration_groups or calibration_groups < train_groups, 'labels_calibration_groups')
    identities={}
    for r in train:
        role='calibration' if r['group'] in calibration_groups else 'train'
        for field in ('decodedSHA256','layoutSHA256'):
            q.require(identities.setdefault((field,r[field]),role)==role, 'labels_ancestry_leak')
    images={}
    for ref in frame_refs:
        staged=q.load(checked(ref))
        q.require(staged['role']=='train', 'labels_staged_role')
        for f in staged['frames']:
            checked(f['image'])
            q.require(f['role']=='train', 'labels_staged_role')
            images[f['sha256']]=f
    scenes = {}
    for ref in admission['sources']:
        artifact = q.load(checked(ref))
        from hcf_study371 import verify_storage
        root=verify_storage(artifact['storage'])
        capture_path=Path(artifact['path'])
        q.require(capture_path.resolve().is_relative_to(root) and q.digest(capture_path)==artifact['sha256'], 'labels_capture_changed')
        capture = q.load(capture_path)
        q.require(capture['complete'] is True and capture['cleanup'] is True, 'labels_capture_incomplete')
        for frame in capture['frames']:
            # Capture event IDs, not pixel hashes, select the exact scene observation.
            key = (frame['case'], frame['profile'], frame['id'])
            q.require(key not in scenes, 'labels_duplicate_event')
            scenes[key] = frame['before']['scene']
    rows = []
    for row in train:
        scene = scenes[(row['case'], row['profile'], row['sourceFrame'])]
        staged=images[row['sha256']]
        q.require(staged['group']==row['group'] and staged['boxes']==row['boxes'], 'labels_staged_identity')
        image = staged['image']
        q.require(q.digest(Path(row['path']))==row['sha256'], 'labels_original_changed')
        q.require(image['sha256'] == row['sha256'], 'labels_image_changed')
        role = 'calibration' if row['group'] in calibration_groups else 'train'
        rows.append(dict(id=row['id'], role=role, sourceRole='train', group=row['group'],
            trainingEligible=role == 'train', image=image, width=row['width'], height=row['height'],
            labelsComplete=True, controls=controls(scene, row)))
    q.require({c['class'] for r in rows if r['role']=='train' for c in r['controls']} == set(CLASSES.values()),
              'labels_training_class_missing')
    return dict(version='detector-training-membership-v1' if calibration_groups else 'detector-training-membership-v2', trainingAdmitted=True,
        names=sorted(CLASSES.values()), rows=rows, admission=admission_ref, frameSources=frame_refs,
        targetScope='Fixture button, row, and tab bodies only; text and containers are not targets.',
        generalUILabelsComplete=False, calibrationGroups=sorted(calibration_groups),
        calibrationPolicy='separate-groups' if calibration_groups else 'none-fixed-last-training-diagnostics',
        selection='fixed-last', modelAccepted=False,
        limitation=('Calibration is reserved from prior training groups. It is not an untouched final audit.' if calibration_groups else
                    'No calibration partition exists. Trainer validation metrics are training diagnostics, not held-out accuracy.') +
                    ' No development group enters training.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--admission',type=Path,required=True)
    p.add_argument('--calibration-group',action='append',default=[])
    p.add_argument('--frames',type=Path,action='append',required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    out=q.local_path(q.ROOT,str(args.output));q.require(not out.exists(),'labels_output_exists')
    result=prepare(pin(args.admission),set(args.calibration_group),[pin(f) for f in args.frames])
    out.mkdir(parents=True)
    q.save(out/'membership.json',result)
    q.save(out/'summary.json',dict(frames=dict(Counter(r['role'] for r in result['rows'])),
        uniqueFrames={role:len({r['image']['sha256'] for r in result['rows'] if r['role']==role}) for role in ('train','calibration')},
        groups={role:len({r['group'] for r in result['rows'] if r['role']==role}) for role in ('train','calibration')},
        targetScope=result['targetScope'],generalUILabelsComplete=False,modelAccepted=False))
    print(out/'membership.json')


if __name__=='__main__':main()
