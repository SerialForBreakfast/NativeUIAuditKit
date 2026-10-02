"""Prepare a non-executable structural data comparison from completed campaign QA."""
import argparse
from collections import Counter
import json

import human_annotation_review as h
import human_intake_audit as audit
import fixture_campaign_intake as campaign
import focus_artwork_readiness as ready
import focus_native_body_assembly as native
from fixture_offline_pipeline import tree_refs
from human_corpus_inventory import metadata_hashes


def prepare(completion, baseline):
    completion,baseline=map(h.local,(completion,baseline))
    record=h.sealed(completion,'fixture-campaign-completion-v1')
    queue=h.checked(h.ROOT,record['reviewQueue']);attempt=queue.parents[1]
    h.require(attempt.parent==completion.parent,'completion_root')
    h.require(tree_refs(attempt)==record['files'],'changed_campaign_outputs')
    audit.validate_queue(queue)
    identity=h.read(completion.parent/'identity.json')
    for ref in identity['implementation']:h.checked(h.ROOT,ref)
    evidence=campaign.coverage(h.checked(h.ROOT,identity['plan']),
        [h.ROOT/s['root'] for s in identity['sources']],h.checked(h.ROOT,identity['protected']))
    h.require(evidence==record['summary']['coverage'],'changed_campaign_coverage')
    base=ready.baseline(baseline)
    protected=metadata_hashes(h.read(h.checked(h.ROOT,identity['protected'])))
    for r in base['samples']:
        if r['split']!='train':protected|=metadata_hashes([r.get(k,{}) for k in ('crop','frame','image')])
    entry=dict(batch=h.ref(attempt/'native-review/batch.json'),crops=h.ref(attempt/'crops/crop-qa.json'))
    rows,accounting,links=native.candidates([entry],protected)
    raw_rows=rows;rows=native.classify(raw_rows,base['samples'],protected)
    global_reasons={r['id']:[x for x in r['reasons'] if x!='duplicate_crop'] for r in rows}
    # Choose alias ownership among targets, but never drop conflicts discovered
    # against competitors or other non-target controls in the same corpus.
    target_rows=native.classify([dict(r,reasons=global_reasons[r['id']]) for r in raw_rows
                                if r['sourceElementID']==evidence['target']],base['samples'],protected)
    by={(r['frameID'],r['controlID']):r for r in target_rows}
    by_id={r['id']:r for r in target_rows};pairs=[];selected=[];seen=set();pixel_pairs=set()
    for link in links:
        if (link['frames'][0],link['controlID']) not in by:continue
        members=[by[(f,link['controlID'])] for f in link['frames']]
        h.require(len(members)==2 and [r['label'] for r in members]==[1,0],'target_pair_labels')
        reasons=sorted({reason for r in members for reason in r['reasons'] if reason!='duplicate_crop'})
        if not reasons:
            pixel_pairs.add(tuple(r['crop']['pixelSHA256'] for r in members))
            for r in members:
                r=by_id[r['duplicateOf']] if r['duplicateOf'] else r
                h.require(not r['reasons'],'blocked_duplicate_representative')
                if r['id'] not in seen:seen.add(r['id']);selected.append(r)
        pairs.append(dict(id=link['id'],members=[r['id'] for r in members],
                          aliases={r['id']:r['duplicateOf'] for r in members if r['duplicateOf']},reasons=reasons))
    h.require(len(pairs)==evidence['cases'],'planned_target_pair_membership')
    proposed=ready.comparison(base,selected) if selected else None
    # Preserve the original source role and ancestry; a plan is not admission.
    compact=[{k:v for k,v in r.items() if k!='recipe'} for r in rows]
    return dict(version='focus-structural-readiness-v1',**h.FLAGS,
        inputs=dict(completion=h.ref(completion),baseline=h.ref(baseline)),
        implementation=[h.ref(h.ROOT/'scripts'/name) for name in
                        ('focus_structural_readiness.py','focus_native_body_assembly.py','focus_artwork_readiness.py')],
        coverage=evidence,counts=dict(candidates=len(rows),targetPairs=len(pairs),
            proposedControls=len(selected),uniqueTargetPixelPairs=len(pixel_pairs),
            blockedPairs=sum(bool(p['reasons']) for p in pairs)),
        pairs=pairs,candidates=compact,nativeAccounting=accounting,comparison=proposed,
        exclusions=dict(Counter(x for r in rows for x in r['reasons'])),
        sourceRole='validation as declared by producer plan; not reassigned',
        ancestry=native.SOURCE_GROUP,independentTest=False,launchEligible=False,
        blockers=['human_sample_acceptance_pending','source_role_decision_pending',
                  'exact_admission_pending','encoding_and_execution_scope_pending']+
                 ([] if selected else ['no_complete_eligible_target_pairs']),
        recommendedExperiment='Matched partial-detail control versus approved structural additions only; fixed evaluation, model and source-label mass.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--completion',required=True);p.add_argument('--baseline',required=True);p.add_argument('--output',required=True)
    a=p.parse_args()
    try:
        output=h.fresh(a.output);r=prepare(a.completion,a.baseline);h.write(output,r,sealed=True)
        print(json.dumps(dict(counts=r['counts'],blockers=r['blockers'],launchEligible=False)));return 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        print('Structural preparation blocked: '+str(e));return 2


if __name__=='__main__':raise SystemExit(main())
