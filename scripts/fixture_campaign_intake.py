"""Complete a planned native appearance campaign into one prefilled human review.

Offline only: no capture, inference, automatic annotation approval or admission.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path

import human_annotation_review as h
import fixture_batch_review as batch
import human_intake_audit as audit
from fixture_offline_pipeline import tree_refs
from fixture_composition import resolve
from harvest_sidecar_v2 import recipe_hash
from human_corpus_inventory import metadata_hashes


def coverage(plan_path, bundles, protected_path):
    envelope=h.read(plan_path)
    if 'data' in envelope:
        h.require(envelope.get('success') is True and envelope.get('command')=='campaign plan','planner_failed')
        plan=envelope['data']['campaign']['_0']['coverage_plan']
    else: plan=envelope
    h.require(plan.get('version')==1 and plan.get('compiler')=='structural-appearance-v1','unsupported_plan')
    manifest=plan['manifest']; cases=manifest['cases']
    h.require(isinstance(cases,list) and 1<=len(cases)<=128,'campaign_review_limit')
    # Coverage compiler uses JSONEncoder.withoutEscapingSlashes (unlike recipe
    # artwork digests). Do not reuse that different serialization contract.
    encoded=json.dumps(manifest,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
    expected_digest=hashlib.sha256(plan['compiler'].encode()+encoded).hexdigest()
    h.require(plan['plan_sha256']==expected_digest,'plan_digest_mismatch')
    h.require(plan['requested_pairs']==plan['attainable_pairs']==len(cases),'plan_count')
    expected={}; families=Counter(); targets=set()
    for case in cases:
        recipe=case['recipe']; digest=recipe_hash(recipe)
        h.require(digest==recipe.get('recipe_hash') and digest not in expected,'duplicate_or_invalid_planned_recipe')
        h.require(case.get('split_group')=='validation' and
                  case.get('independence_group')=='fixture_procedural_renderer_v1','unsupported_source_role')
        ids=case['target_element_ids'];h.require(isinstance(ids,list) and len(ids)==1,'one_target_per_case')
        controls,_=resolve(recipe['appearance']['composition'],recipe,h.require)
        controls={i['id']:i for i in controls if i['focusable']}
        h.require(ids[0] in controls and len(controls)>1,'missing_target_or_competitor')
        expected[digest]=case;families[controls[ids[0]]['kind']]+=1;targets.add(ids[0])
    h.require(len({c['case_id'] for c in cases})==len(cases),'duplicate_case_id')
    h.require(len(targets)==1,'mixed_review_target_ids')
    protected=metadata_hashes(h.read(protected_path)); seen={};sources=[];contracts=[]
    for root in bundles:batch.preflight(root,protected)
    for root in bundles:
        source,contract=batch.source_record(root,protected)
        sources.append(source);contracts.append(contract)
        for row in contract['usableRows']:
            digest=recipe_hash(row['recipe'])
            h.require(digest in expected,'unexpected_captured_recipe')
            h.require(digest not in seen,'duplicate_captured_case')
            scene=row['observationBinding']['focusedScene']
            h.require(scene['focused_element_id']==expected[digest]['target_element_ids'][0],'captured_target_mismatch')
            seen[digest]=dict(caseID=expected[digest]['case_id'],sourceRoot=source['root'],pairID=row['id'])
    h.require(set(seen)==set(expected),'missing_captured_cases')
    # Validate body/visibility projection before any output or expensive cropping.
    projected=batch.project(sources,contracts,body_geometry=True,visibility_policy=batch.VISIBILITY_POLICY)
    h.require(all(f['disposition']=='imported' and not f['nativeUnresolved'] for f in projected['frames']),
              'unresolved_campaign_body_or_visibility')
    return dict(planSHA256=plan['plan_sha256'],cases=len(cases),familyCounts=dict(families),
                target=next(iter(targets)),sources=sources,members=[seen[k] for k in sorted(seen)],
                frames=len(projected['frames']),trainingEligible=False)


def run(plan_path, bundles, protected_path, output, *, seed=42, count=8, exception_limit=0):
    plan_path,protected_path,output=map(h.local,(plan_path,protected_path,output))
    roots=sorted(map(h.local,bundles))
    h.require(roots and len(roots)<=128 and len(set(roots))==len(roots),'bundle_membership')
    h.require(not any(output.is_relative_to(r) or r.is_relative_to(output) for r in roots),'output_source_overlap')
    h.require(not plan_path.is_relative_to(output) and not protected_path.is_relative_to(output),'output_input_overlap')
    h.require(type(seed)is int and type(count)is int and 1<=count<=256 and
              type(exception_limit)is int and 0<=exception_limit<=256,'sampling_limits')
    evidence=coverage(plan_path,roots,protected_path)
    h.require(count>=2*len(evidence['familyCounts']),'sample_count_below_family_focus_strata')
    dependencies=['fixture_campaign_intake.py','fixture_batch_review.py','human_intake_audit.py',
        'human_annotation_review.py','fixture_offline_pipeline.py','fixture_composition.py',
        'fixture_semantic_inventory.py','fixture_rendered_body.py','harvest_bundle_validation.py',
        'harvest_sidecar_v2.py','harvest_artwork.py','focus_runtime.py','photos_focus_pilot.py']
    identity=dict(plan=h.ref(plan_path),protected=h.ref(protected_path),sources=evidence['sources'],
        categoryMap=h.ref(h.CATEGORY),seed=seed,count=count,exceptionLimit=exception_limit,
        implementation=[h.ref(h.ROOT/'scripts'/p) for p in dependencies])
    output.mkdir(parents=True,exist_ok=True);lock=output/'active.lock'
    try:fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    except FileExistsError:raise ValueError('campaign_intake_locked')
    os.close(fd)
    try:
        pin=output/'identity.json';done=output/'completed.json'
        if pin.exists():h.require(h.read(pin)==identity,'changed_campaign_inputs_or_implementation')
        else:
            h.require(set(output.iterdir())=={lock},'unrecognized_output')
            h.write(pin,identity)
        if done.exists():
            record=h.sealed(done,'fixture-campaign-completion-v1')
            for ref in record['files']:h.checked(h.ROOT,ref)
            attempt=h.checked(h.ROOT,record['reviewQueue']).parents[1]
            h.require(attempt.parent==output and tree_refs(attempt)==record['files'],'changed_output_membership')
            audit.validate_queue(h.checked(h.ROOT,record['reviewQueue']))
            return record['summary']
        attempts=sorted(output.glob('attempt-*'));h.require(len(attempts)<10,'attempt_limit')
        attempt=output/f'attempt-{len(attempts)+1:03d}'
        try:
            result=batch.prepare(roots,attempt,protected_path,seed=seed,count=count,
                exception_limit=exception_limit,body_geometry=True,family_focus_element=evidence['target'])
            h.require(not result['counts'].get('rejected'),'campaign_bundle_rejected')
            review=audit.validate_plan(attempt/'audit/plan.json')
            h.require(coverage(plan_path,roots,protected_path)==evidence,'campaign_changed_during_intake')
            h.require(h.ref(plan_path)==identity['plan'] and h.ref(protected_path)==identity['protected'],
                      'campaign_input_changed')
            summary=dict(version='fixture-campaign-intake-v1',**h.FLAGS,coverage=evidence,
                crops=result['crops'],review=review['counts'],sampling=review['sampling'],
                reviewQueue=h.ref(attempt/'audit/combined-queue.json'))
            h.write(attempt/'campaign.json',summary,sealed=True)
            lines=['# Campaign review','',f"{evidence['cases']} planned cases verified; {result['crops']['completed']} production crops checked.",
                f"One prefilled review: {review['counts']['uniqueReview']} frames; {len(review['sampling']['strata'])} family/focus strata.",
                '', '**Diagnostic only. Review confirms annotation quality, not training admission.**','',
                'Selected frames use measured solid-body bounds, excluding shadow/glow. Check growth, focus, clipping and missing controls.',
                'Mark uncertain frames for correction; do not approve by appearance alone. No manual redraw unless a proposal is wrong.','',
                '| Stratum | Eligible frames | Sample | Inclusion probability |','|---|---:|---:|---:|']
            for key,stratum in sorted(review['sampling']['strata'].items()):
                lines.append(f"| {key} | {stratum['denominator']} | {len(stratum['selected'])} | {stratum['inclusionProbability']:.3f} |")
            lines+=['','Related screens are not independent source groups. Targeted exceptions are not a random defect-rate estimate.',
                '',f"[All-frame geometry previews]({attempt}/review.md)",f"[Annotation queue]({attempt}/audit/combined-queue.json)"]
            (attempt/'campaign-review.md').write_text('\n'.join(lines)+'\n')
            record=dict(version='fixture-campaign-completion-v1',**h.FLAGS,
                        summary=summary,reviewQueue=summary['reviewQueue'],files=tree_refs(attempt))
            pending=output/f'completed-{attempt.name}.pending.json'
            h.write(pending,record,sealed=True);pending.replace(done)
            return summary
        except (ValueError,OSError,KeyError,TypeError) as error:
            attempt.mkdir(parents=True,exist_ok=True)
            h.write(attempt/'failure.json',dict(complete=False,error=str(error)))
            raise
    finally:lock.unlink()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',required=True);parser.add_argument('--bundle',action='append',required=True)
    parser.add_argument('--protected',required=True);parser.add_argument('--output',required=True)
    parser.add_argument('--seed',type=int,default=42);parser.add_argument('--count',type=int,default=8)
    parser.add_argument('--exception-limit',type=int,default=0)
    args=parser.parse_args()
    try:
        result=run(args.plan,args.bundle,args.protected,args.output,seed=args.seed,count=args.count,
                   exception_limit=args.exception_limit)
        print(json.dumps(dict(cases=result['coverage']['cases'],crops=result['crops'],review=result['review'],
                              queue=result['reviewQueue'],trainingEligible=False)));return 0
    except (ValueError,OSError,KeyError,TypeError) as error:
        print('Campaign intake blocked: '+str(error));return 2


if __name__=='__main__':raise SystemExit(main())
