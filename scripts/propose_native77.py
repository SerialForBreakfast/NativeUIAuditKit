"""Source-backed native-table data-role proposal; no automatic admission or training."""
import argparse
from collections import Counter
from pathlib import Path
import focus_direct_transition as d
from focus_corrected_transition_audit import validate_case
from inventory_transition_sources import observed_scroll


def verified_records(source):
    report=d.h.sealed(source,'native76-intake-v1')
    chosen=[r for r in report['results'] if r['lane']=='table12']
    d.h.require(len(chosen)==12 and all(r['consumer']=='passed-inspection-only' for r in chosen),'native77_inspection')
    rows=[]
    for row in chosen:
        bundle=d.h.local(d.h.ROOT/row['bundle']);root=bundle.parents[2]
        manifest=root/'campaign-manifest.json';case_doc=d.h.read(manifest)
        matches=[c for c in case_doc['cases'] if c['case_id']==row['caseID']]
        d.h.require(len(matches)==1,'native77_source_case')
        evidence=bundle/'transition-case.json';raw,b,a=validate_case(root,evidence,matches[0],directional=True)
        d.h.require([b['image'],a['image']]==[{k:v for k,v in image.items() if k in ('path','sha256')} for image in row['images']], 'native77_image_binding')
        result=d.record(row['caseID'],'fixture-procedural-renderer-v1','calibration',b,a,True,
            [d.h.ref(evidence),d.h.ref(manifest)],None)
        # record() recomputes the existing corpus's RGBA hash convention. Intake76
        # used RGB plus a separator; compare source-byte refs above, not unlike hashes.
        rows.append(dict(result,recipe=matches[0]['recipe'],condition=raw['specification']['condition'],
            observedScroll=observed_scroll(raw)[0]))
    return rows


def validate_proposal(proposal):
    d.h.require(proposal.get('version')=='native77-role-proposal-v1' and proposal.get('approved') is False and
        proposal.get('executionEligible') is False,'native77_not_approval')
    rows=proposal['members']
    d.h.require(len(rows)==12 and len({r['id'] for r in rows})==12 and
        proposal['memberSHA256']==d.h.digest(rows),'native77_membership')
    d.h.require(all(r['sourceRole']=='calibration' and r['requestedRole']=='train' and
        r['group']=='fixture-procedural-renderer-v1' and r['changed'] is True for r in rows),'native77_roles')
    return proposal


def build_admission(old,corpus,previous,proposal,decision):
    validate_proposal(proposal)
    d.h.require(decision.get('version')=='native77-role-decision-v1' and decision.get('approved') is True and
        decision.get('reviewer') and decision.get('decisionReference') and
        decision.get('memberSHA256')==proposal['memberSHA256'],'native77_explicit_role_decision')
    old_rows=d.admitted(old,previous)
    d.h.require(Counter(r['split'] for r in old_rows)=={'train':32,'development':5},'native77_old_roles')
    d.h.require(proposal['originalCorpusSHA256']==old['corpusSHA256'] and
        proposal['originalAdmission']==previous,'native77_original_binding')
    expected=[dict({k:v for k,v in row.items() if k!='requestedRole'},id=proposal['source']['sha256']+':'+row['id']) for row in proposal['members']]
    d.h.require(corpus['records']==old['records']+expected and corpus['excluded']==old['excluded'], 'native77_original_or_added_records_changed')
    result=dict(version='focus-direct-admission-v1',approved=True,reviewer=decision['reviewer'],
        decisionReference=decision['decisionReference'],corpusSHA256=corpus['corpusSHA256'],
        assignments={**previous['assignments'],**{row['id']:'train' for row in expected}},
        limitation='44train/5exposed development; no independent evaluation or training launch approval.')
    d.h.require(Counter(r['split'] for r in d.admitted(corpus,result))=={'train':44,'development':5},'native77_new_roles')
    return result


def prepare(output):
    out=d.h.fresh(output);source=d.h.ROOT/'reports/work/NATIVE-INTAKE-76/intake-r3/intake.json'
    base=d.h.ROOT/'reports/work/GENERALIZATION-65/admission'
    old=d.h.read(base/'corpus.json');previous=d.h.read(base/'admission.json')
    d.h.require(old==d.collect(old['sources']),'native77_existing_source_changed')
    existing=d.admitted(old,previous);new=verified_records(source)
    reference=d.h.ref(source)
    combined=d.corpus_document(dict(old['sources'],nativeTable=reference),old['records']+
        [dict(r,id=reference['sha256']+':'+r['id']) for r in new],old['excluded'])
    rows=[dict(r,requestedRole='train') for r in new]
    proposed=dict(version='native77-role-proposal-v1',approved=False,executionEligible=False,
        source=d.h.ref(source),originalCorpusSHA256=old['corpusSHA256'],originalAdmission=previous,
        members=rows,memberSHA256=d.h.digest(rows),counts=dict(train=44,development=5,independentEvaluation=0),
        conditionCounts=dict(Counter(r['condition'] for r in rows)),recipeThemeCounts=dict(Counter(r['recipe']['theme'] for r in rows)),
        scrollStates=dict(Counter(str(r['observedScroll']) for r in rows)),
        overlap={split:sorted({v for r in existing if r['split']==split for v in r['decodedPixelHashes']} &
            {v for r in rows for v in r['decodedPixelHashes']}) for split in ('train','development')},
        limitations=['All new pairs are focus changes; scroll unknown, not no-scroll positives.',
            'Shared Fixture ancestry excludes these and related variants from final evaluation.',
            'Settings5remain exposed development; no independent validation or production gate.',
            'Rich24remain excluded; no renderer-v2metadata is silently downgraded.'])
    validate_proposal(proposed)
    # Exercise existing leakage checks in memory only; never publish an approval.
    trial=dict(version='native77-role-decision-v1',approved=True,reviewer='test-only',decisionReference='in-memory proposal consistency only',memberSHA256=proposed['memberSHA256'])
    build_admission(old,combined,previous,proposed,trial)
    out.mkdir(parents=True);d.h.write(out/'proposal.json',proposed,sealed=True)
    d.h.write(out/'prospective-corpus.json',combined)
    d.h.write(out/'decision-template.json',dict(version='native77-role-decision-v1',approved=False,reviewer=None,
        decisionReference=None,memberSHA256=proposed['memberSHA256']))
    print({k:proposed[k] for k in ('memberSHA256','counts','recipeThemeCounts','scrollStates','overlap')})


def admit(output, decision_path):
    """Materialize exact approved membership after fresh source reconstruction."""
    import time
    start=time.monotonic();out=d.h.fresh(output)
    root=d.h.ROOT/'reports/work/NATIVE-ADMISSION-77/proposal'
    proposal=d.h.read(root/'proposal.json');decision=d.h.read(d.h.local(decision_path))
    corpus=d.h.read(root/'prospective-corpus.json')
    old=d.h.read(d.h.ROOT/'reports/work/GENERALIZATION-65/admission/corpus.json')
    admission=build_admission(old,corpus,proposal['originalAdmission'],proposal,decision)
    d.h.require(corpus==d.collect(corpus['sources']), 'native77_source_changed_before_admission')
    rows=d.admitted(corpus,admission)
    out.mkdir(parents=True);d.h.write(out/'corpus.json',corpus);d.h.write(out/'admission.json',admission)
    d.h.write(out/'receipt.json',dict(version='native77-admission-receipt-v1',proposal=d.h.ref(root/'proposal.json'),
        decision=d.h.ref(d.h.local(decision_path)),corpus=d.h.ref(out/'corpus.json'),admission=d.h.ref(out/'admission.json'),
        roles=dict(Counter(r['split'] for r in rows)),originalRolesPreserved=True,
        elapsedSeconds=time.monotonic()-start),sealed=True)
    print('admitted44train/5development; model execution separate')
    return out,rows


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);p.add_argument('--decision')
    args=p.parse_args()
    if args.decision:admit(args.output,args.decision)
    else:prepare(args.output)
