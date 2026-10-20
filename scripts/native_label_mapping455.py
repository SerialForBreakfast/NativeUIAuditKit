"""Map verified native inventories to scoped canonical detector targets.

Keep control presentation bounds. Exclude their nested text and images.
This does not qualify unobserved classes or change any source annotation.
"""
import argparse
import copy
from collections import Counter
from pathlib import Path
import research_queue as q
from template_inputs398 import checked, pin
from annotation_inventory454 import inventory
import focusable_detector_labels422 as existing


def map_scene(scene, row):
    records = inventory(scene, row)
    index = {r['id']: r for r in records}
    controls = existing.controls(scene, row)
    control_ids = {r['id'] for r in controls}
    targets = copy.deepcopy(controls)
    excluded = []
    for record in records:
        ident, role = record['id'], record['role']
        ancestors, parent = set(), record['parent']
        while parent:
            q.require(parent not in ancestors and parent != ident, 'mapping_parent_cycle')
            ancestors.add(parent)
            parent = index[parent]['parent']
        if role == 'control_wrapper':
            q.require(ident in control_ids, 'mapping_control_missing')
            continue
        if role in ('layout_region', 'decorative_background'):
            q.require(record['declaredTaxonomy'] is None, 'mapping_region_taxonomy')
            reason = 'decorative-layout-not-canonical-target'
        elif role in ('label_view', 'image_view'):
            native, canonical = ('UILabel', 'label') if role == 'label_view' else ('UIImageView', 'imageView')
            q.require(record['nativeClass'] == native and record['declaredTaxonomy'] in (None, canonical),
                      'mapping_native_class')
            if ancestors & control_ids:
                reason = 'content-inside-interactive-control'
            else:
                targets.append(dict(id=ident, **{'class': canonical}, bounds=record['bounds']))
                continue
        else:
            raise ValueError('mapping_unsupported_role:' + role)
        excluded.append(dict(id=ident, role=role, reason=reason))
    q.require(len(targets) + len(excluded) == len(records), 'mapping_inventory_accounting')
    return dict(targets=targets, excluded=excluded)


def prepare(admission_ref, frame_refs):
    # Reuse all existing image, ancestry, duplicate, source, and role checks.
    result = existing.prepare(admission_ref, set(), frame_refs)
    admission = q.load(checked(admission_ref))
    scenes = {}
    for ref in admission['sources']:
        artifact = q.load(checked(ref))
        for frame in q.load(artifact['path'])['frames']:
            scenes[(frame['case'], frame['profile'], frame['id'])] = frame['before']['scene']
    source = {r['id']: r for r in admission['rows'] if r['role'] == 'train'}
    exclusions = []
    for row in result['rows']:
        original = source[row['id']]
        mapped = map_scene(scenes[(original['case'], original['profile'], original['sourceFrame'])], original)
        row['controls'] = mapped['targets']
        exclusions.append(dict(id=row['id'], image=row['image'], exclusions=mapped['excluded']))
    result['names'] = sorted({c['class'] for r in result['rows'] for c in r['controls']})
    result['targetScope'] = 'Declared Fixture controls and standalone UILabel/UIImageView targets; decorative regions and nested control content excluded.'
    result['mappingVersion'] = 'native-canonical-targets-v1'
    result['generalUILabelsComplete'] = False
    result['limitation'] += ' Mapping support does not establish coverage of unobserved canonical classes.'
    return result, dict(version='native-mapping-review-v1', exclusions=exclusions,
        classes=dict(Counter(c['class'] for r in result['rows'] for c in r['controls'])),
        exclusionReasons=dict(Counter(e['reason'] for r in exclusions for e in r['exclusions'])),
        modelAccepted=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--admission', type=Path, required=True)
    parser.add_argument('--frames', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = q.local_path(q.ROOT, str(args.output))
    q.require(not out.exists(), 'mapping_output_exists')
    data, review = prepare(pin(args.admission), [pin(p) for p in args.frames])
    out.mkdir(parents=True)
    q.save(out/'membership.json', data)
    q.save(out/'review.json', review)
    print(out)


if __name__ == '__main__':
    main()
