"""Coverage audit of an existing focus protocol; no models, capture or admission.

Preserves the executable protocol byte-for-byte. A coverage report is not a new
trainer protocol, and cannot promote diagnostic manifests or protected members.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

import human_annotation_review as h
from focus_dataset_contract import digest, image, pixel_digest, validate_manifest
from focus_representative_validation import stratum
from focus_ring_readiness import MIN
from human_corpus_inventory import metadata_hashes

VERSION = 'focus-corpus-inventory-v1'
ROLES = {'train-candidate', 'human-static-auxiliary', 'representative-selection', 'retention-validation'}
LANES = ('buttons', 'tabs', 'artwork', 'rows', 'keyboard', 'other')


def refresh_runtime(original):
    from focus_review_continuation import assemble
    current = assemble(original['inputs'])
    allowed = {'runtime', 'protocolSHA256'}
    h.require(set(current) == set(original) and all(current[k] == original[k] for k in original if k not in allowed),
              'reassembly_changed_data_or_policy')
    return current


def recipe_coverage(rows, producer):
    """Join producer recipe roles by exact retained sidecar bytes, never by names."""
    known = {r['metadata_sha256']: r for r in producer['pairs']}
    result = {}
    for row in rows:
        if not row.get('pairID') or not row.get('frame'):
            continue
        # Optional retained-sidecar join; absence does not fabricate recipe semantics.
        pair = row['pairID']
        h.require(Path(pair).name == pair, 'unsafe_pair_identity')
        candidate = h.local(h.ROOT / row['frame']['path']).parent / (pair + '_metadata.json')
        if not candidate.is_file():
            continue
        ref = h.ref(candidate)
        evidence = known.get(ref['sha256'])
        if evidence:
            result.setdefault(ref['sha256'], dict(reference=ref, presentation=evidence['presentation'],
                              focusTreatment=evidence['focus_treatment'], sampleIDs=[]))['sampleIDs'].append(row['id'])
    return [result[k] for k in sorted(result)]


def sealed(path, key):
    value = h.read(path)
    h.require(value.get(key) == digest({k: v for k, v in value.items() if k != key}), 'changed_seal')
    return value


def role(row):
    h.require(row.get('use') in ROLES, 'unsupported_or_protected_role')
    expected = 'train' if row['use'] in ('train-candidate', 'human-static-auxiliary') else 'validation'
    h.require(row.get('split') == expected, 'changed_role_split')
    return 'training' if expected == 'train' else 'retention' if row['use'] == 'retention-validation' else 'development'


def audit_rows(rows, protected, check):
    """Account for failures per member; never silently shrink an executable corpus."""
    h.require(rows and len({r['id'] for r in rows}) == len(rows), 'empty_or_duplicate_membership')
    records, pixel_groups, relationships = [], defaultdict(list), defaultdict(list)
    for row in rows:
        record = dict(id=row['id'], disposition='accepted', reasons=[])
        try:
            record['role'] = role(row)
            h.require(type(row.get('label')) is int and row['label'] in (0, 1), 'invalid_label')
            lane = stratum(row)
            h.require(lane in LANES, 'unsupported_stratum')
            record.update(stratum=lane, label=row['label'])
            frame = row.get('frame', row.get('image'))
            h.require(isinstance(frame, dict), 'missing_frame')
            for ref, size in ((frame, None), (row['crop'], (256, 256))):
                observed = check(ref, size)
                h.require(observed not in protected and ref['sha256'] not in protected, 'protected_overlap')
                expected = ref.get('pixelSHA256')
                if ref is row['crop']:
                    expected = row.get('pixelSHA256', expected)
                h.require(expected is None or expected == observed, 'changed_pixels')
                record['framePixels' if ref is frame else 'cropPixels'] = observed
            pixel_groups[record['cropPixels']].append(record)
            group_keys = [('frame', record['framePixels'])]
            # Sessions and source families are relationships, not independence proof.
            for key in ('relatedGroup', 'sourceSessionID', 'family'):
                if row.get(key) not in (None, '', 'unknown'):
                    group_keys.append((key, row[key]))
            for key in group_keys:
                relationships[key].append(record)
            record.update(source=row.get('sourceID', row.get('sourceSessionID', 'unknown')),
                          family=row.get('family', row.get('scene', 'unknown')),
                          control=row['control'], pairID=row.get('pairID'),
                          labelSource=row.get('labelSource', 'human-review-reference'))
        except (OSError, ValueError, KeyError, TypeError) as error:
            record.update(disposition='blocked', reasons=[str(error)])
        records.append(record)
    for group in pixel_groups.values():
        reasons = []
        if len({r['label'] for r in group}) > 1:
            reasons.append('conflicting_pixel_labels')
        if 'training' in {r['role'] for r in group} and len({r['role'] for r in group}) > 1:
            reasons.append('training_evaluation_pixel_overlap')
        for r in group:
            if reasons:
                r['disposition'] = 'blocked'; r['reasons'] += reasons
    overlaps = []
    for (kind, group), members in sorted(relationships.items()):
        roles = sorted({r['role'] for r in members})
        if 'training' in roles and len(roles) > 1:
            overlaps.append(dict(kind=kind, group=group, roles=roles, ids=sorted(r['id'] for r in members),
                                 meaning='development-exposed; not independent qualification'))
            if kind == 'frame':
                for record in members:
                    record['disposition'] = 'blocked'
                    record['reasons'].append('training_evaluation_frame_overlap')
    return dict(records=records, dispositions=dict(Counter(r['disposition'] for r in records)),
                duplicateCropGroups=[sorted(r['id'] for r in g) for g in pixel_groups.values() if len(g) > 1],
                crossRoleRelationships=overlaps)


def coverage(records):
    result = []
    for population in ('training', 'development', 'retention'):
        for lane in LANES:
            rows = [r for r in records if r.get('role') == population and r.get('stratum') == lane
                    and r['disposition'] == 'accepted']
            result.append(dict(role=population, stratum=lane, status='present' if rows else 'absent',
                               focused=sum(r['label'] for r in rows), unfocused=sum(1-r['label'] for r in rows),
                               distinctCrops=len({r['cropPixels'] for r in rows}),
                               knownSourceIDs=len({r['source'] for r in rows if r['source'] != 'unknown'}),
                               unknownSourceSamples=sum(r['source'] == 'unknown' for r in rows)))
    return result


def artwork_decisions(report):
    h.require(report.get('policy') == 'retained_geometry_coverage_v1', 'unsupported_geometry_report')
    decisions = []
    seen = set()
    for row in report['recapture_matrix']:
        h.require(row['recipe_hash'] not in seen, 'duplicate_recipe')
        seen.add(row['recipe_hash'])
        treatment = row['focus_treatment']
        decision = ('artwork-not-applicable-use-control-wrapper' if treatment == ['native_button'] else
                    'review-retained-artwork-crops' if treatment == ['native_image'] and not row['sidecars_with_missing_role'] else
                    'measured-artwork-evidence-needed-for-body-specific-use' if treatment == ['native_image'] else
                    'unknown-treatment-blocked')
        decisions.append(dict(recipeHash=row['recipe_hash'], pairs=row['sidecars'], decision=decision,
                              newTrainingAdmission=False, automaticRecapture=False))
    h.require(sum(r['pairs'] for r in decisions) == report['unique_sidecars'], 'geometry_count_mismatch')
    return decisions


def run(protocol_path, admission_path, qa_path, geometry_path, output):
    out = h.fresh(output)
    protocol = sealed(protocol_path, 'protocolSHA256')
    h.require(protocol['version'] == 'focus-reviewed-full-fit-v1', 'incompatible_protocol')
    admission = sealed(admission_path, 'assemblySHA256')
    protected_ref = admission['protectedMetadata']
    protected = metadata_hashes(h.read(h.checked(h.ROOT, protected_ref)))
    cache = {}
    def check(ref, size):
        key = (ref['path'], ref['sha256'], size)
        if key not in cache:
            image(h.ROOT, ref, size)
            cache[key] = pixel_digest(h.ROOT, ref)
        return cache[key]
    audit = audit_rows(protocol['samples'], protected, check)
    diagnostic = []
    qa = h.read(qa_path)
    for entry in qa['results']:
        path = h.local(entry['manifest'])
        doc = h.read(path)
        result = dict(manifest=h.ref(path), claimedPairs=len(doc.get('pairs', [])), trainingAdmission=False)
        try:
            h.require(doc.get('evidenceKind') == 'test-only' and doc.get('purpose') == 'development-pilot',
                      'changed_diagnostic_role')
            validated = validate_manifest(doc, path.parent)
            result.update(disposition='accepted-diagnostic-only', validatedPairs=len(validated),
                          targetCoverage=doc.get('targetCoverage'))
        except (OSError, ValueError, KeyError, TypeError) as error:
            result.update(disposition='blocked', reason=str(error))
        diagnostic.append(result)
    train = [r for r in protocol['samples'] if r['use'] == 'train-candidate']
    pairs = defaultdict(list)
    for r in train:
        pairs[r['sourceID'], r['pairID']].append(r)
    incomplete = [list(k) for k, v in pairs.items() if len(v) != 2 or {r['label'] for r in v} != {0, 1}]
    scene_counts = Counter(v[0]['scene'] for v in pairs.values() if len(v) == 2 and {r['label'] for r in v} == {0, 1})
    geometry = h.read(geometry_path)
    report = dict(version=VERSION, protocol=h.ref(protocol_path), admission=h.ref(admission_path),
                  protectedMetadata=protected_ref, protectedPixelsOpened=False, **audit,
                  coverage=coverage(audit['records']), diagnostic=diagnostic,
                  nativePairs=len(pairs), incompletePairs=incomplete,
                  productionSceneSupport=[dict(scene=k, retainedPairs=scene_counts[k], requiredPairs=v,
                                               shortfall=max(0, v-scene_counts[k])) for k, v in MIN.items()],
                  unmappedControls=dict(Counter(r['control'] for r in protocol['samples'] if stratum(r) == 'other')),
                  selectedUnfocusedParentSupport='unknown: not an explicit field in baseline rows',
                  hardNegativeSupport='appearance strata require recipe-linked evidence; not inferred from label=0',
                  artworkRoleDecisions=artwork_decisions(geometry),
                  retainedRecipeCoverage=recipe_coverage(protocol['samples'], geometry),
                  heldPairs=len(admission.get('heldMembers', [])),
                  excludedSelection=len(admission.get('excludedSelection', [])),
                  qualificationBlockers=protocol['unmetQualificationBlockers'],
                  executionAuthorized=False, newTrainingAdmission=False, releaseEligible=False)
    out.mkdir(parents=True)
    # Preserve the original and rebind only runtime identity through the real assembler.
    with (out/'protocol.json').open('xb') as f:
        f.write(h.local(protocol_path).read_bytes())
    current = refresh_runtime(protocol)
    h.write(out/'current-runtime-protocol.json', current)
    report['runtimeReassembly'] = dict(originalProtocolSHA256=protocol['protocolSHA256'],
                                     currentProtocolSHA256=current['protocolSHA256'],
                                     changedFields=sorted(k for k in current if current[k] != protocol[k]),
                                     dataAndPolicyUnchanged=True)
    h.write(out/'inventory.json', report)
    h.write(out/'input-index.json', [h.ref(p) for p in (protocol_path, admission_path, qa_path, geometry_path)]
            + [protected_ref] + [r['manifest'] for r in diagnostic])
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('protocol', 'admission', 'diagnostic-qa', 'geometry', 'output'):
        p.add_argument('--'+name, required=True)
    args = p.parse_args()
    report = run(args.protocol, args.admission, args.diagnostic_qa, args.geometry, args.output)
    print(json.dumps({k: report[k] for k in ('dispositions', 'nativePairs', 'incompletePairs', 'newTrainingAdmission')}))
    return 2 if report['dispositions'].get('blocked') or report['incompletePairs'] or any(
        r['disposition'] == 'blocked' for r in report['diagnostic']) else 0


if __name__ == '__main__':
    raise SystemExit(main())
