"""Native measured-body assembly and encoding plan. No model imports or execution."""
import argparse
from collections import Counter, defaultdict
import math
import re

import human_annotation_review as h
import fixture_batch_review as native
from focus_corpus_planner import verified_inventory
from focus_dataset_contract import image
from focus_runtime import RUNTIME_PREPROCESSING
from human_corpus_inventory import metadata_hashes

INPUT_VERSION = 'focus-native-body-input-v1'
VERSION = 'focus-native-body-assembly-v1'
ARM = 'native-body-dry-run'
BASE_SEAL = '1140910f741a048cefe155b4146087c6f5831ff55860c514416367e773097543'
SOURCE_GROUP = 'fixture_procedural_renderer_v1'
ASSEMBLY_MAX_BYTES = 32 * 1024 * 1024


def annotation_conflicts(frames):
    """Generation is provenance, not a changed visual annotation. Keep originals."""
    groups = defaultdict(list)
    for frame in frames:
        proposals = []
        for c in frame['proposals']:
            normalized = dict(c)
            if 'renderedBodyGeometry' in c:
                normalized['renderedBodyGeometry'] = {k:v for k,v in c['renderedBodyGeometry'].items() if k!='generation'}
            proposals.append(normalized)
        groups[frame['pixelSHA256']].append((frame['id'],h.digest(proposals)))
    return {fid for group in groups.values() if len({sig for _,sig in group})>1 for fid,_ in group}


def candidates(entries, protected):
    """Existing bracket validator remains authoritative; reuse verified crop receipts."""
    h.require(entries and len(entries) <= 32, 'source_count')
    h.require(len({e['batch']['path'] for e in entries}) == len(entries), 'duplicate_batch')
    rows, accounting, links = [], [], []
    for entry in sorted(entries, key=lambda e:e['batch']['path']):
        path = h.checked(h.ROOT, entry['batch'])
        raw = h.read(path)
        h.require(raw.get('version') == native.BODY_VERSION, 'measured_body_batch_required')
        raw = h.sealed(path,native.BODY_VERSION)
        h.require(h.ref(h.CATEGORY)==raw['categoryMap'], 'taxonomy_changed')
        roots=[s['root'] for s in raw['sources']]
        h.require(len(set(roots))==len(roots) and all(f['sourceRoot'] in roots for f in raw['frames']), 'source_membership')
        protected_here = protected | metadata_hashes(h.read(h.checked(h.ROOT,raw['protectedMetadata'])))
        safe_sources, contracts = [], []
        # Quarantine whole source bundles on known protected identities before any
        # image decode. Other independent bundles in the same review can continue.
        for source in raw['sources']:
            frames=[f for f in raw['frames'] if f['sourceRoot']==source['root']]
            if metadata_hashes([source,frames]) & protected_here:
                accounting.append(dict(batchID=raw['id'],sourceRoot=source['root'],
                    disposition='excluded_source_before_decode',reason='protected_reference_before_decode',
                    frameIDs=[f['id'] for f in frames],
                    controlIDs=[f['id']+':'+c['id'] for f in frames for c in f['proposals']]))
                continue
            expected,contract=native.source_record(h.local(h.ROOT/source['root']),protected_here,source.get('pairIDs'))
            h.require(expected==source,'source_binding_changed')
            safe_sources.append(source);contracts.append(contract)
        projection=native.project(safe_sources,contracts,body_geometry=True,
                                 visibility_policy=raw.get('visibilityPolicy'))
        original={f['id']:f for f in raw['frames']}
        h.require(len(original)==len(raw['frames']), 'duplicate_frame')
        # Only presentation numbering and cross-source duplicate/review summaries
        # may differ after quarantining a source. Geometry, labels and refs cannot.
        stable=lambda f:{k:v for k,v in f.items() if k not in ('number','editorStem','duplicateOf','reviewFindings')}
        safe_roots={s['root'] for s in safe_sources}
        h.require({f['id'] for f in projection['frames']}=={f['id'] for f in raw['frames'] if f['sourceRoot'] in safe_roots},
                  'safe_frame_membership')
        h.require(all(stable(f)==stable(original[f['id']]) for f in projection['frames']), 'native_review_projection_changed')
        batch=dict(raw,**projection)
        conflicts=annotation_conflicts(batch['frames'])
        qa = h.sealed(h.checked(h.ROOT, entry['crops']), 'human-review-crop-qa-v1')
        h.require(qa['batch'] == entry['batch'] and qa['revision'] is None
                  and qa['preprocessing'] == RUNTIME_PREPROCESSING, 'crop_batch_or_protocol_mismatch')
        crops = {r['id']:r for r in qa['crops']}
        expected = {f['id']+':'+c['id'] for f in raw['frames'] if f['disposition']=='imported' for c in f['proposals']}
        h.require(len(crops) == len(qa['crops']) == qa['expected'] == qa['completed'] == len(expected)
                  and set(crops) == expected, 'crop_membership')
        accounting.extend(dict(r, batchID=batch['id']) for r in batch['records'])
        links.extend(dict(p, batchID=batch['id']) for p in batch['pairs'])
        for frame in batch['frames']:
            if frame['disposition'] != 'imported':
                continue
            h.require(h.pixel_digest(h.ROOT, frame['image']) == frame['pixelSHA256'], 'frame_pixels_changed')
            for c in frame['proposals']:
                ref = crops[frame['id']+':'+c['id']]['crop']
                h.require(not metadata_hashes(ref) & protected_here, 'protected_crop_before_decode')
                h.checked(h.ROOT, ref); image(h.ROOT, ref, (256,256))
                px = h.pixel_digest(h.ROOT, ref)
                h.require(c['geometryRole']=='rendered_control_body' and c['state'] in ('focused','unfocused'),
                          'unknown_geometry_or_focus')
                reasons = ['protected_or_evaluation_overlap'] if px in protected_here else []
                reasons.extend(frame.get('admissionBlockers',[]))
                if frame['nativeUnresolved']: reasons.append('incomplete_body_inventory')
                if c['renderedBodyGeometry'].get('clipping'): reasons.append('clipping_requires_separate_acceptance')
                if frame['id'] in conflicts:
                    reasons.append('conflicting_native_proposals')
                rows.append(dict(id='native-body:'+batch['id']+':'+frame['id']+':'+c['id'],
                    batchID=batch['id'], frameID=frame['id'], controlID=c['id'],
                    sourceElementID=c['sourceElementID'], sourcePairID=frame['sourcePairID'],
                    sourceID=frame['sourceRoot'], sourceKind='tvos_native_generator',
                    relatedGroup=SOURCE_GROUP, intrinsicGroup=SOURCE_GROUP,
                    recipe=frame['recipe'], recipeSeed=frame['recipe'].get('seed'),
                    scene=frame['recipe']['archetype'], style=frame['recipe']['theme'], control=c['class'],
                    label=int(c['state']=='focused'), labelSource=c.get('labelSource','observed_native_bracket'),
                    bounds=c['bounds'], geometryRole=c['geometryRole'],
                    nativeRecord=frame['nativeRecord'], batch=entry['batch'], cropQA=entry['crops'],
                    generationOnlyConflictResolved=(frame['id'] not in conflicts and
                        'same_pixels_conflicting_native_proposals' in frame['reviewFindings']),
                    frame=dict(frame['image'], pixelSHA256=frame['pixelSHA256']),
                    crop=dict(ref, pixelSHA256=px), originSplit='development',
                    split='development', use='native-body-candidate', pairedTransitionEligible=False,
                    reasons=reasons, trainingEligible=False))
    h.require(len({r['id'] for r in rows}) == len(rows), 'duplicate_control_identity')
    return sorted(rows,key=lambda r:r['id']), accounting, links


def classify(rows, baseline, forbidden):
    """All evidence retained; no first-seen label wins a contradictory pixel group."""
    forbidden = set(forbidden)
    baseline_pixels, labels = set(), defaultdict(set)
    evaluation_groups, evaluation_seeds = set(), set()
    for r in baseline:
        crop = r.get('pixelSHA256',r['crop'].get('pixelSHA256'))
        labels[crop].add(r['label'])
        baseline_pixels.add(crop)
        if r['split'] != 'train':
            forbidden.add(crop)
            frame = r.get('frame',r.get('image',{}))
            forbidden.update(metadata_hashes(frame))
            evaluation_groups.update(filter(None,(r.get('relatedGroup'),r.get('intrinsicGroup'))))
            if r.get('recipeSeed') is not None: evaluation_seeds.add(r['recipeSeed'])
    for r in rows:
        h.require(type(r['label']) is int and r['label'] in (0,1), 'invalid_native_label')
        labels[r['crop']['pixelSHA256']].add(r['label'])
    owners, result = {}, []
    for r in sorted(rows,key=lambda r:r['id']):
        reasons = list(r['reasons']); px = r['crop']['pixelSHA256']
        if (metadata_hashes(r['frame']) | metadata_hashes(r['crop'])) & forbidden:
            reasons.append('protected_or_evaluation_overlap')
        if r['relatedGroup'] in evaluation_groups or r['intrinsicGroup'] in evaluation_groups or r['recipeSeed'] in evaluation_seeds:
            reasons.append('evaluation_lineage_overlap')
        if len(labels[px]) != 1: reasons.append('conflicting_crop_labels')
        if px in baseline_pixels: reasons.append('baseline_duplicate_crop')
        representative = None
        if not reasons:
            representative = owners.get(px)
            if representative: reasons.append('duplicate_crop')
            else: owners[px] = r['id']
        result.append(dict(r,reasons=sorted(set(reasons)),duplicateOf=representative,
                           disposition='blocked' if reasons else 'awaiting_admission'))
    return result


def admit(rows, decision, spec, baseline):
    """Explicit sample/recipe-scope acceptance, not mandatory per-box human drawing."""
    h.require(decision.get('version')=='focus-native-body-admission-v1' and decision.get('approved') is True
              and decision.get('reviewer') and decision.get('authorizationReference'), 'explicit_admission_required')
    h.checked(h.ROOT,decision['authorizationReference'])
    h.require(decision['inputs']=={k:spec[k] for k in ('inventory','sources')}, 'stale_admission_inputs')
    review=decision['sourceReview']; h.checked(h.ROOT,review['evidence'])
    h.require(review['relationshipsKnown'] is True and review['protectedRolesUnchanged'] is True
              and review['group']==SOURCE_GROUP and review['role']=='training-candidate'
              and review['independentEvaluationClaim'] is False, 'source_review_required')
    qa=decision['geometryAcceptance'];h.checked(h.ROOT,qa['evidence'])
    h.require(qa['accepted'] is True and qa['batches']==[e['batch'] for e in spec['sources']], 'geometry_acceptance_scope')
    selected,excluded=decision['selectedIDs'],decision['excluded']
    indexed={r['id']:r for r in rows}
    h.require(selected and len(set(selected))==len(selected) and not set(selected)&set(excluded)
              and set(selected)|set(excluded)==set(indexed)
              and all(isinstance(v,str) and v.strip() for v in excluded.values()), 'admission_membership')
    h.require(all(not indexed[s]['reasons'] for s in selected), 'blocked_candidate_selected')
    h.require(not set(selected)&{r['id'] for r in baseline}, 'baseline_id_collision')
    return [dict(indexed[s],split='train',use='train-candidate',disposition='admitted-for-assembly')
            for s in sorted(selected)]


CONTINUITY_POLICY = 'baseline-fixture-budget-v1'


def continuous_weights(base, additions):
    """Preserve non-fixture members exactly; share each fixture label budget.

    This is an explicit experimental policy, not a reinterpretation of v1 runs.
    No-addition identity also preserves historical within-fixture differences.
    """
    from focus_appearance_experiment import FIXTURE_KINDS
    train = [r for r in base['samples'] if r['split'] == 'train']
    old = base['fullFit']['weights']
    h.require(len({r['id'] for r in train+additions}) == len(train+additions), 'duplicate_weight_member')
    h.require(set(old) == {r['id'] for r in train} and
              all(type(w) in (int,float) and math.isfinite(w) and w > 0 for w in old.values())
              and math.isclose(sum(old.values()),1), 'invalid_baseline_weights')
    h.require(all(type(r['label']) is int and r['label'] in (0,1) for r in train+additions), 'invalid_weight_label')
    fixture = [r for r in train if r['use'] == 'train-candidate' and r['sourceKind'] in FIXTURE_KINDS]
    h.require(all(r['split'] == 'train' and r['use'] == 'train-candidate'
                  and r['sourceKind'] in FIXTURE_KINDS for r in additions), 'nonfixture_weight_addition')
    if not additions:
        return dict(old)
    result = dict(old)
    for label in (0,1):
        original = [r for r in fixture if r['label'] == label]
        members = [r for r in fixture+additions if r['label'] == label]
        h.require(original and members, 'missing_fixture_label_budget')
        mass = math.fsum(old[r['id']] for r in original)
        result.update({r['id']:mass/len(members) for r in members})
    h.require(math.isclose(math.fsum(result.values()),1), 'invalid_weight_mass')
    return result


def weighting(base, additions, policy=None):
    h.require(policy in (None, CONTINUITY_POLICY), 'unsupported_weight_policy')
    if policy == CONTINUITY_POLICY:
        return continuous_weights(base, additions)
    if not additions: return dict(base['fullFit']['weights'])
    from focus_appearance_experiment import weights
    native_rows=[r for r in base['samples'] if r['split']=='train' and r['use']=='train-candidate']+additions
    result={sid:.8*w for sid,w in weights(native_rows)['weights'].items()}
    human=[r for r in base['samples'] if r['split']=='train' and r['use']=='human-static-auxiliary']
    result.update({r['id']:base['fullFit']['weights'][r['id']] for r in human})
    h.require(set(result)=={r['id'] for r in native_rows+human} and
              all(math.isfinite(w) and w>0 for w in result.values()) and
              math.isclose(sum(result.values()),1), 'invalid_weight_mass')
    for members,mass in ((native_rows,.8),(human,.2)):
        for label in (0,1):
            h.require(math.isclose(sum(result[r['id']] for r in members if r['label']==label),mass/2),
                      'unbalanced_source_label_mass')
    return result


def assemble(spec):
    h.require(spec.get('version')==INPUT_VERSION, 'unsupported_native_body_input')
    inventory,base,audit,protected,_=verified_inventory(h.checked(h.ROOT,spec['inventory']))
    h.require(base['protocolSHA256']==BASE_SEAL, 'wrong_baseline')
    # Include preserved evaluation frame pixels from the verified inventory, even
    # when historical human rows omit pixel hashes on their image references.
    protected |= {r[k] for r in audit['records'] if r['role']!='training' for k in ('framePixels','cropPixels')}
    admission=h.read(h.checked(h.ROOT,inventory['admission']))
    reserved=h.read(h.checked(h.ROOT,admission['reservedPixels']))
    h.require(reserved.get('seal')==h.digest({k:v for k,v in reserved.items() if k!='seal'}), 'changed_reservation')
    protected |= metadata_hashes(reserved)
    protected |= {r['framePixelSHA256'] for r in reserved['samples']}
    rows,accounting,links=candidates(spec['sources'],protected)
    rows=classify(rows,base['samples'],protected)
    additions=[];blockers=[]
    if spec.get('admission'):
        additions=admit(rows,h.read(h.checked(h.ROOT,spec['admission'])),spec,base['samples'])
    else: blockers.append('missing_explicit_native_admission_and_source_review')
    if not additions: blockers.append('no_admitted_native_controls')
    baseline_train=[r for r in base['samples'] if r['split']=='train']
    evaluation=[r for r in base['samples'] if r['split']!='train']
    weights=weighting(base,additions,spec.get('weightPolicy'))
    # Existing caches remain byte-bound; do not deserialize them in a dry run.
    cache_refs=[base['baseCachedInputs'][k] for k in ('cache','receipt','preflight')]
    cache_refs += list(base['inputs']['newFeatures'].values())
    for ref in cache_refs: h.checked(h.ROOT,ref)
    receipt=h.read(h.checked(h.ROOT,base['baseCachedInputs']['receipt']))
    plan=dict(version='focus-native-body-encoding-plan-v1',executionAuthorized=False,
        representation=base['representation'],featureStateSHA256=receipt['featureStateSHA256'],
        baseline=inventory['protocol'],baselineCaches=cache_refs,
        reuseTrainingIDs=[r['id'] for r in baseline_train],reuseEvaluationIDs=[r['id'] for r in evaluation],
        members=[dict(id=r['id'],label=r['label'],crop=r['crop']) for r in additions],
        featureWidth=576,preprocessing=RUNTIME_PREPROCESSING,
        blockers=['encoding_budget_and_approval_required','changed_data_experiment_contract_required'])
    doc=dict(version=VERSION,inputs=spec,baseline=inventory['protocol'],
        samples=baseline_train+additions+evaluation,candidates=rows,nativeAccounting=accounting,
        nativePairRelationships=links,encodingPlan=plan,fullFit=dict(base['fullFit'],weights=weights),
        configuration=dict(base['configuration'],batch=len(baseline_train)+len(additions)),
        selection=base['selection'],representation=base['representation'],
        evaluationMembershipSHA256=h.digest(evaluation),baselineEvaluationMembershipSHA256=h.digest(evaluation),
        counts=dict(baselineTraining=len(baseline_train),added=len(additions),training=len(baseline_train)+len(additions),
                    evaluation=len(evaluation),candidates=len(rows),dispositions=dict(Counter(r['disposition'] for r in rows))),
        weightDelta={r['id']:weights[r['id']]-base['fullFit']['weights'][r['id']] for r in baseline_train},
        blockers=blockers+plan['blockers'],trainingEligible=False,releaseEligible=False,modelGatePassed='not_assessed')
    doc['protocolSHA256']=h.digest(doc)
    return doc


def load_protocol(path,arm,run_name,approval_path=None):
    doc=h.read(h.local(path),limit=ASSEMBLY_MAX_BYTES); seal=doc.get('protocolSHA256')
    h.require(doc.get('version')==VERSION and seal==h.digest({k:v for k,v in doc.items() if k!='protocolSHA256'}), 'changed_native_assembly')
    h.require(doc==assemble(doc['inputs']), 'changed_native_assembly_inputs')
    h.require(arm==ARM and isinstance(run_name,str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',run_name), 'dry_run_arm_required')
    h.require(approval_path is None, 'assembly_is_not_execution_approval')
    rows=[dict(r,path=h.checked(h.ROOT,r['crop'])) for r in doc['samples']]
    return dict(formatVersion='focus-representative-preflight-v1',protocolVersion=VERSION,
                configurationValid=True,launchEligible=False,executionAuthorized=False,releaseEligible=False,
                blockers=doc['blockers'],counts=doc['counts'],configuration=doc['configuration'],
                protocolSHA256=seal,encodingPlan=doc['encodingPlan']),rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inventory',required=True);p.add_argument('--source',nargs=2,action='append',required=True,metavar=('BATCH','CROPS'))
    p.add_argument('--admission');p.add_argument('--output',required=True)
    p.add_argument('--weight-policy',choices=[CONTINUITY_POLICY],
                   help='Explicit experimental continuity policy; omitted preserves legacy behavior')
    args=p.parse_args();out=h.fresh(args.output)
    spec=dict(version=INPUT_VERSION,inventory=h.ref(h.local(args.inventory)),
              sources=[dict(batch=h.ref(h.local(b)),crops=h.ref(h.local(c))) for b,c in args.source])
    if args.admission:spec['admission']=h.ref(h.local(args.admission))
    if args.weight_policy:spec['weightPolicy']=args.weight_policy
    try:
        doc=assemble(spec);out.mkdir(parents=True)
        h.write(out/'focus_dataset_manifest.json',doc)
        h.write(out/'input.json',spec);h.write(out/'encoding-plan.json',doc['encodingPlan'])
        h.write(out/'admission-draft.json',dict(version='focus-native-body-admission-v1',approved=False,
            inputs={k:spec[k] for k in ('inventory','sources')},reviewer='',authorizationReference=None,
            selectedIDs=[],excluded={},sourceReview=None,geometryAcceptance=None))
        (out/'review.md').write_text('# Native-body assembly dry run\n\n'+
            f"Candidates: {doc['counts']['candidates']}; admitted additions: {doc['counts']['added']}.\n\n"+
            'Every candidate, exclusion and native record is in focus_dataset_manifest.json.\n\n'+
            'Blockers:\n\n'+''.join('- '+x+'\n' for x in doc['blockers']))
        print(doc['counts']);return 0
    except (ValueError,OSError,KeyError,TypeError) as error:
        print('Assembly rejected: '+str(error));return 2


if __name__=='__main__':raise SystemExit(main())
