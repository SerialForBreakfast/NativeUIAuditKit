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
    a=p.parse_args();run(a.root,a.output)
