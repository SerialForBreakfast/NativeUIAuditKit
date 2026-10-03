"""Offline corrected campaign-v1 intake; fixed pixel comparisons, no model admission."""
import argparse
import copy
import time
from collections import Counter
from PIL import Image
import human_annotation_review as h
from fixture_owned_pairs import member
from synth05_intake import verify_package
import focus_structural_transition_audit as legacy


def endpoint(root, evidence, record, role):
    h.require(record['role']==role and record['image']==role+'.png','endpoint_role')
    h.require(h.read(evidence.parent/(role+'.json'))==record,'endpoint_sidecar_binding')
    capture=copy.deepcopy(record['capture_endpoint'])
    h.require(capture['correlation']=='validated_capture_bracket','endpoint_correlation')
    image=member(root,str((evidence.parent/record['image']).relative_to(root)))
    with Image.open(image) as im:
        h.require(im.size==(capture['frame_width'],capture['frame_height']),'endpoint_dimensions')
    capture.update(image=record['image'],sha256=capture['frame_png_sha256'],action_capture_receipt=record['receipt'])
    result=legacy.endpoint(root,evidence,capture,str(image.relative_to(root)),transition_visibility=True)
    inventory=result['scene'].get('semantic_inventory') or {}
    result['exclusions']=inventory.get('control_exclusions',{})
    return result


def validate_case(root,evidence,case):
    d=h.read(evidence)
    reference = (case['recipe'].get('appearance') or {}).get('referencePack')
    ancestry = case['independence_group']
    if reference:
        from fixture_reference import resolve
        resolve(case['recipe'], h.require)
        h.require(ancestry == 'reference_' + reference['screen'] + '_v1', 'reference_ancestry')
    else:
        h.require(ancestry == 'fixture_procedural_renderer_v1', 'case_ancestry')
    h.require(d['version']==1 and d['case_id']==case['case_id'] and
              d['specification']==case['transition'] and d['recipe_hash']==case['recipe']['recipe_hash'] and
              d['ancestry_exclusion']=='fixture_procedural_renderer_v1' and
              d['evidence_kind']=='controlled_transition_not_direct_focus_pair','case_contract')
    h.require(len(d['endpoints'])==2,'endpoint_count')
    b,a=[endpoint(root,evidence,r,k) for r,k in zip(d['endpoints'],('before','after'))]
    h.require(b['ticks'][-1]<=a['ticks'][0],'pair_time_order')
    recipe={k:v for k,v in case['recipe'].items() if k!='evidence_requirements'}
    h.require(b['scene']['recipe']==recipe and a['scene']['recipe']==recipe,'case_recipe_binding')
    h.require(all(e['scene'].get('fixture_run_id')==d['run_id'] and
                  e['receipt']['simulatorID']==d['simulator_id'] for e in (b,a)), 'case_runtime_binding')
    receipts=[b['receipt']]+([d['action_receipt']] if 'action_receipt' in d else [])+[a['receipt']]
    h.require(all(r['state']=='delivered' for r in receipts) and
              len({r['operationID'] for r in receipts})==len({r['simulatorID'] for r in receipts})==1,
              'case_action_session')
    seq=[r['sequence'] for r in receipts]
    h.require(all(type(n)is int and n>0 for n in seq) and seq==sorted(set(seq)),'case_action_sequence')
    condition=d['specification']['condition']
    h.require(condition in ('boundary_unchanged','content_only','scroll_unchanged','scroll_moved'),'case_condition')
    if condition!='boundary_unchanged':
        m=d['mutation_receipt'];c=m['command']
        h.require(m['state']=='observed' and c['run_id']==d['run_id'] and c['event_id']==d['event_id'] and
                  c['generation']==b['scene']['focus_observation']['generation'] and
                  b['ticks'][-1]<=m['requested_at_ns']<=m['observed_at_ns']<=a['ticks'][0], 'mutation_binding')
        h.require(c['action']==('replace_content' if condition=='content_only' else 'scroll') and
                  c['target_id']==d['specification']['mutation_target'], 'mutation_action')
        field='replacement_seed' if condition=='content_only' else 'offset'
        observed='observed_content_seed' if condition=='content_only' else 'observed_offset'
        h.require(c[field]==d['specification'][field]==m[observed],'mutation_result')
    else:h.require('action_receipt' in d,'missing_boundary_action')
    return d,b,a


def score_pair(before, after,*,tracker='template'):
    """Predict from before proposals only; native after truth is scoring-only."""
    import focus_recorded_transition_eval as evaluate
    import focus_recorded_comparison as comparison
    import settings_focus_stability as stability
    proposals=[dict(id=c['id'],bounds=c['bounds']) for c in before['controls']]
    options={} if tracker=='template' else dict(tracker=tracker)
    predictions,runtime=evaluate.predict(before['image'],after['image'],proposals,**options)
    metrics,crop_runtime=stability.crop_metrics(before['image'],after['image'],proposals,predictions)
    h.require(runtime is None or runtime==crop_runtime,'transition_runtime_changed')
    matches=[dict(before=c['id'],after=c['id'] if c['id'] in {a['id'] for a in after['controls']} else None,
                  text=c['id'],reason='native_control_excluded_after') for c in before['controls']]
    # Persist prediction-only measurements, not the guarded decision or after truth.
    for p in predictions:p['stability']=dict(metrics=metrics.get(p['id']))
    scored=comparison.compare(predictions,before['controls'],after['controls'],matches)
    guarded=copy.deepcopy(predictions)
    for p in guarded:
        p['decision']=stability.guard(stability.extend(p,metrics.get(p['id']),settings_context=True),metrics.get(p['id']))['decision']
    guardrows=comparison.compare(guarded,before['controls'],after['controls'],matches)
    for row,guard in zip(scored,guardrows):
        row['arms']['guardedStability']=guard['arms']['combined']
        for arm in row['arms'].values():
            if arm['scorable']:arm['scoreReason']='native_identity_correspondence'
    return scored,runtime or crop_runtime


def reference_run(root,output,*,tracker='template'):
    """Replay delivered reference actions; appearance captures are not actions."""
    from audit_reference43 import accepted_cases,verify_files
    import focus_recorded_transition_eval as evaluate
    import focus_recorded_comparison as comparison
    import focus_transition_verifier as visual
    policy=visual.tracker_policy(tracker)
    root,output=h.local(root),h.fresh(output)
    start=time.monotonic();file_count=verify_files(root)
    manifest=h.ref(root/'artifact-manifest.json');entries=accepted_cases(root)
    h.require(Counter(e['kind'] for e in entries)==dict(appearance=12,scroll_moved=12,scroll_unchanged=12),
              'reference_condition_membership')
    pairs=[];excluded=[];runtimes=[];total=0
    for entry in entries:
        if entry['kind']=='appearance':
            excluded.append(dict(id=entry['case_id'],reason='direct_focus_capture_not_action'));continue
        h.require(time.monotonic()-start<600,'reference_replay_deadline')
        base=member(root,entry['path'])
        campaign_path=member(root,f"campaigns/{entry['campaign']}/campaign-manifest.json")
        campaign=h.read(campaign_path)
        cases=[c for c in campaign['cases'] if c['case_id']==entry['case_id']]
        h.require(len(cases)==1,'reference_case_membership');case=cases[0]
        row=dict(id=entry['case_id'],condition=entry['kind'],status='blocked');pairs.append(row)
        try:
            h.require(case['split_group']=='validation' and case['recipe']['recipe_hash']==entry['recipe_hash'],
                      'reference_case_role_recipe')
            evidence,b,a=validate_case(root,base/'transition-case.json',case)
            h.require(evidence.get('cleanup')=='verified','reference_cleanup_unverified')
            h.require(entry['kind']==evidence['specification']['condition'] and
                      (b['focus']!=a['focus'])==(entry['kind']=='scroll_moved'),'reference_transition_relation')
            controls,runtime=score_pair(b,a,tracker=tracker)
            total+=len(controls);h.require(total<=512,'reference_control_budget')
            if runtime not in runtimes:runtimes.append(runtime)
            row.update(status='diagnostic',controls=controls,beforeFocus=b['focus'],afterFocus=a['focus'],
                family=case['recipe']['appearance']['referencePack']['screen'],
                sourceAncestry=dict(renderer=evidence['ancestry_exclusion'],screenFamily=case['independence_group']),
                sourceRole='calibration',completeEndpoints=False,
                inputs=[b['image'],a['image'],h.ref(base/'transition-case.json'),h.ref(campaign_path)],
                exclusions=dict(before=b['exclusions'],after=a['exclusions']),
                observedSwitch=b['focus']!=a['focus'])
        except (ValueError,KeyError,TypeError,OSError) as error:row['reason']=str(error)
    h.require(len(runtimes)<=1 and verify_files(root)==file_count and h.ref(root/'artifact-manifest.json')==manifest,
              'reference_source_or_runtime_changed')
    report=dict(version='reference-transition-audit-v1',**h.FLAGS,manifest=manifest,pairs=pairs,
        tracker=tracker,trackerPolicy=policy,
        excluded=excluded,filesVerified=file_count,elapsedSeconds=time.monotonic()-start,runtime=runtimes,
        counts=dict(Counter(p['status'] for p in pairs)),
        summaries={arm:evaluate.summarize([r['arms'][arm] for p in pairs for r in p.get('controls',[])])
                   for arm in (*comparison.ARMS,'guardedStability')},
        limitations=['calibration only; no training admission','shared Fixture renderer ancestry',
                     'partial visible/control inventories; no full-screen navigation qualification',
                     'guarded Settings rule is cross-domain diagnostic, not qualified reference UI logic'],
        implementation=[h.ref(h.ROOT/'scripts'/s) for s in ('focus_corrected_transition_audit.py',
            'focus_recorded_transition_eval.py','focus_recorded_comparison.py','settings_focus_stability.py',
            'harvest_sidecar_v2.py','fixture_reference.py','focus_transition_verifier.py')])
    output.mkdir(parents=True);h.write(output/'audit.json',report,sealed=True)
    print(report['counts']);print(report['summaries']);return report


def run(root,output):
    # Validation is also used by the annotation environment, which needs no cv2.
    import focus_recorded_transition_eval as evaluate
    import focus_recorded_comparison as comparison
    import settings_focus_stability as stability
    root=h.local(root);output=h.fresh(output);start=time.monotonic()
    manifest=verify_package(root/'file-manifest.json');campaign=h.read(root/'campaign-manifest.json')
    cases=campaign['cases'];h.require(len(cases)==len({c['case_id'] for c in cases})==16,'case_membership')
    files=list(root.glob('splits/*/*/transition-case.json'))
    h.require(len(files)==16 and {p.parent.name for p in files}=={c['case_id'] for c in cases},'case_files')
    rows=[];runtimes=[];total=0
    for case in cases:
        h.require(time.monotonic()-start<600,'diagnostic_deadline')
        evidence=member(root,f"splits/{case['split_group']}/{case['case_id']}/transition-case.json")
        row=dict(id=case['case_id'],condition=case['transition']['condition'],status='blocked');rows.append(row)
        try:
            raw=h.read(evidence)
            row['sourceObservations']=[dict(role=e['role'],**legacy.contract_observations(e['capture_endpoint']['after_scene']),
                settled=e['capture_endpoint']['after_scene']['is_settled'],
                focusObservation=e['capture_endpoint']['after_scene']['focus_observation'],
                readiness=e['capture_endpoint']['after_scene']['observation_diagnostics']['reason']) for e in raw['endpoints']]
            d,b,a=validate_case(root,evidence,case)
            predictions,runtime=evaluate.predict(b['image'],a['image'],[dict(id=c['id'],bounds=c['bounds']) for c in b['controls']])
            if runtime and runtime not in runtimes:runtimes.append(runtime)
            total+=len(predictions);h.require(total<=256,'control_budget')
            matches=[dict(before=c['id'],after=c['id'] if c['id'] in {x['id'] for x in a['controls']} else None,
                          text=c['id'],reason='native_control_excluded_after') for c in b['controls']]
            scored=comparison.compare(predictions,b['controls'],a['controls'],matches)
            metrics,_=stability.crop_metrics(b['image'],a['image'],b['controls'],predictions)
            guarded=copy.deepcopy(predictions)
            for p in guarded:
                # Cross-domain diagnostic only; this is not a Settings-context qualification.
                p['decision']=stability.guard(stability.extend(p,metrics.get(p['id']),settings_context=True),metrics.get(p['id']))['decision']
            guardrows=comparison.compare(guarded,b['controls'],a['controls'],matches)
            for r,g in zip(scored,guardrows):
                r['arms']['guardedStability']=g['arms']['combined']
                for arm in r['arms'].values():
                    if arm['scorable']:arm['scoreReason']='native_identity_correspondence'
            row.update(status='diagnostic',controls=scored,inputs=[b['image'],a['image'],h.ref(evidence)],
                       beforeFocus=b['focus'],afterFocus=a['focus'],
                       intentMatched=(b['focus']==case['transition']['initial_focus'] and a['focus']==case['transition']['expected_focus']),
                       exclusions=dict(before=b['exclusions'],after=a['exclusions']))
        except (ValueError,KeyError,TypeError,OSError) as error:row['reason']=str(error)
    h.require(len(runtimes)<=1 and verify_package(root/'file-manifest.json')==manifest,'runtime_or_source_changed')
    result=dict(version='corrected-transition-audit-v1',**h.FLAGS,manifest=manifest,pairs=rows,
                counts=dict(Counter(r['status'] for r in rows)),elapsedSeconds=time.monotonic()-start,runtime=runtimes,
                summaries={arm:evaluate.summarize([r['arms'][arm] for p in rows for r in p.get('controls',[])])
                           for arm in (*comparison.ARMS,'guardedStability')},
                limitations=['same renderer ancestry; calibration diagnostic only',
                             'guardedStability is cross-domain stress testing, not runtime Settings applicability',
                             'capture hash plus host brackets; not authenticated pixel-focus attestation'])
    result['implementation']=[h.ref(h.ROOT/'scripts'/name) for name in (
        'focus_corrected_transition_audit.py','focus_structural_transition_audit.py','fixture_semantic_inventory.py',
        'harvest_sidecar_v2.py','harvest_artwork.py','fixture_composition.py','settings_focus_stability.py',
        'focus_recorded_comparison.py','focus_recorded_transition_eval.py')]
    output.mkdir(parents=True);h.write(output/'audit.json',result,sealed=True)
    print(result['counts']);print(result['summaries']);print(Counter(r.get('reason') for r in rows if r['status']=='blocked'))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True);p.add_argument('--output',required=True)
    p.add_argument('--reference-delivery',action='store_true',help='Explicit rich-reference36 replay; no legacy count override')
    p.add_argument('--tracker',choices=('template','wide-template-v1','feature-consensus-v1'),default='template')
    a=p.parse_args()
    h.require(a.reference_delivery or a.tracker=='template','tracker_requires_reference_delivery')
    if a.reference_delivery:reference_run(a.root,a.output,tracker=a.tracker)
    else:run(a.root,a.output)
