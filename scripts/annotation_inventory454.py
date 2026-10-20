"""Audit retained native inventories without inventing detector class labels."""
from collections import Counter
from pathlib import Path
import research_queue as q
from template_inputs398 import checked
from detector_native_inputs import bounds


def inventory(scene, row):
    value = scene.get('semantic_inventory')
    q.require(isinstance(value, dict) and value.get('version') == 1, 'inventory_missing')
    q.require(value.get('coverage') == 'complete_declared_composition'
              and value.get('truncated') is False and value.get('exclusions') == {}
              and value.get('control_exclusions') == {}, 'inventory_incomplete')
    q.require((value['width'], value['height']) == (row['width'], row['height']), 'inventory_dimensions')
    q.require(value.get('generation') == scene['observation_generation'], 'inventory_generation')
    q.require(value.get('focus_known') is True and value.get('focused_id') == row['focus'], 'inventory_focus')
    elements = value['elements']
    ids = [e['id'] for e in elements]
    q.require(elements and len(ids) == len(set(ids)), 'inventory_duplicate')
    expected = set(row['boxes'])
    q.require(set(value['expected_control_ids']) == set(value['visible_control_ids']) == expected,
              'inventory_control_membership')
    q.require({e['id'] for e in elements if e['role'] == 'control_wrapper'} == expected,
              'inventory_control_membership')
    result = []
    for element in elements:
        q.require(element.get('source') == 'uikit_post_layout_view', 'inventory_source')
        q.require(element.get('is_hidden') is False and element.get('effective_alpha', 0) > 0,
                  'inventory_visibility')
        box = bounds(element['visible_pixel_bounds'], row['width'], row['height'])
        q.require(not element.get('parent_id') or element['parent_id'] in ids, 'inventory_parent')
        # Native view bounds are not glyph bounds or presentation-layer control bounds.
        result.append(dict(id=element['id'], role=element['role'], bounds=box,
            nativeClass=element['native_class'], parent=element.get('parent_id'),
            declaredTaxonomy=element.get('declared_taxonomy')))
    return result


def audit(admission_ref):
    admission = q.load(checked(admission_ref))
    from native_control_admission import validate_partition
    validate_partition(admission['rows'])
    scenes = {}
    for ref in admission['sources']:
        artifact = q.load(checked(ref))
        from hcf_study371 import verify_storage
        root = verify_storage(artifact['storage'])
        path = Path(artifact['path'])
        q.require(path.resolve().is_relative_to(root) and q.digest(path) == artifact['sha256'], 'inventory_capture_changed')
        capture = q.load(path)
        q.require(capture['complete'] is True and capture['cleanup'] is True, 'inventory_capture_incomplete')
        for frame in capture['frames']:
            key = (frame['case'], frame['profile'], frame['id'])
            q.require(key not in scenes, 'inventory_duplicate_capture')
            scenes[key] = frame['before']['scene']
    rows = []
    for row in admission['rows']:
        if row['role'] != 'train':
            continue
        q.require(q.digest(Path(row['path'])) == row['sha256'], 'inventory_image_changed')
        records = inventory(scenes[(row['case'], row['profile'], row['sourceFrame'])], row)
        rows.append(dict(id=row['id'], group=row['group'], profile=row['profile'], sha256=row['sha256'],
                         role='train', records=records))
    q.require(rows, 'inventory_empty')
    return dict(version='native-inventory-review-v1', source=admission_ref, rows=rows,
        frames=len(rows), uniqueImages=len({r['sha256'] for r in rows}), groups=len({r['group'] for r in rows}),
        roleCounts=dict(Counter(e['role'] for r in rows for e in r['records'])),
        generalUILabelsComplete=False, modelAccepted=False,
        decision='Reuse measured inventory. Qualify target taxonomy and geometry before general detector training.',
        limitation='Counts describe capture events, not independent examples. Nested text is not automatically a standalone label. Layout regions are not detector classes.')
