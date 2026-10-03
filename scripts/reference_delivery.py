"""Import the pinned rich-reference36 delivery into diagnostic annotation review."""
import copy
from collections import Counter
import human_annotation_review as h
from audit_reference43 import accepted_cases, verify_files
from fixture_owned_pairs import member
from harvest_bundle_validation import validate_bundle
from focus_corrected_transition_audit import validate_case


def source_record(root, protected):
    verify_files(root)
    refs = [h.ref(root/'artifact-manifest.json')]
    for item in h.read(root/'artifact-manifest.json')['files']:
        path = member(root, item['path'])
        h.require(path.stat().st_size <= 32 * 1024**2, 'reference_member_size')
        ref = h.ref(path)
        h.require(ref['sha256'] not in protected, 'protected_reference_bytes')
        refs.append(ref)
    rows = []
    for entry in accepted_cases(root):
        base = member(root, entry['path'])
        campaign = h.read(root/'campaigns'/entry['campaign']/'campaign-manifest.json')
        case = next(c for c in campaign['cases'] if c['case_id'] == entry['case_id'])
        h.require(case['split_group'] == 'validation' and case['recipe']['recipe_hash'] == entry['recipe_hash'],
                  'reference_case_role_recipe')
        pack = case['recipe']['appearance']['referencePack']
        h.require(case['independence_group'] == 'reference_' + pack['screen'] + '_v1',
                  'reference_case_ancestry')
        if entry['kind'] == 'appearance':
            contract = validate_bundle(base, max_total_bytes=512 * 1024**2)
            h.require(len(contract['usableRows']) == contract['acceptedRowCount'] == 1,
                      'reference_appearance_membership')
            row = copy.deepcopy(contract['usableRows'][0])
            h.require(row['split'] == 'calibration' and row['recipe']['recipe_hash'] == entry['recipe_hash'],
                      'reference_appearance_role')
            for key in ('unfocusedPath', 'focusedPath', 'metadataPath'):
                row[key] = str((base/row[key]).relative_to(root))
        else:
            evidence, before, after = validate_case(root, base/'transition-case.json', case)
            h.require(entry['kind'] == evidence['specification']['condition'] and
                      (before['focus'] != after['focus']) == (entry['kind'] == 'scroll_moved'),
                      'reference_transition_relation')
            row = dict(recipe=before['scene']['recipe'], split='calibration', sidecarVersion=None,
                       unfocusedPath=str((base/'before.png').relative_to(root)),
                       focusedPath=str((base/'after.png').relative_to(root)),
                       metadataPath=str((base/'transition-case.json').relative_to(root)),
                       observationBinding=dict(baselineScene=before['scene'], focusedScene=after['scene']))
        row.update(id=entry['case_id'], sourceRole='calibration', eligibleForTraining=False,
                   evidenceKind=entry['kind'], labelSource='observed_native_bracket',
                   sourceAncestry=dict(renderer='fixture_procedural_renderer_v1',
                                      screenFamily=case['independence_group']),
                   admissionBlockers=['calibration_role_requires_explicit_admission', 'sampled_review_pending'])
        row['observationBinding']['correlation'] = 'validated_capture_bracket'
        rows.append(row)
    coverage = dict(acceptedCases=len(rows), kinds=dict(Counter(r['evidenceKind'] for r in rows)))
    return dict(root=str(root.relative_to(h.ROOT)), files=refs, targetCoverage=coverage), dict(
                    usableRows=rows, acceptedRowCount=len(rows), eligibleForTraining=False, targetCoverage=coverage)
