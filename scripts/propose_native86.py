"""Exact retained action-pair proposal; no admission or training authority."""
import argparse
from collections import Counter
import focus_direct_transition as d
from intake_native76 import verify_selection, collection_selection
from focus_corrected_transition_audit import validate_case
from inventory_transition_sources import observed_scroll


def verified_records():
    roots=[d.h.ROOT/'reports/work/NATIVE-INTAKE-76/received/ttr-native-rich24-20261003-r1',
        d.h.ROOT/'reports/work/NATIVE-INTAKE-83/received/ttr-native-collection-36-20261003']
    rows=[]
    for root in roots:
        selection=d.h.read(root/'qualified-cases.json') if (root/'qualified-cases.json').exists() else collection_selection(root)
        for entry,bundle,case in verify_selection(root,selection,expected_pairs=selection['pairs']):
            evidence=bundle/'transition-case.json'
            if not evidence.exists():continue
            raw,b,a=validate_case(root,evidence,case,directional=True)
            rows.append(dict(d.record(case['case_id'],'fixture-procedural-renderer-v1','calibration',b,a,True,
                [d.h.ref(evidence),d.h.ref(root/entry['source_receipt'])],None),
                recipe=case['recipe'],observedScroll=observed_scroll(raw)[0]))
    d.h.require(len(rows)==24 and len({r['id'] for r in rows})==24,'native86_membership')
    return rows


def validate_proposal(p):
    d.h.require(p.get('version')=='native86-role-proposal-v1' and p.get('approved') is False and
        p.get('executionEligible') is False,'native86_not_approval')
    rows=p['members']
    d.h.require(len(rows)==24 and len({r['id'] for r in rows})==24 and p['memberSHA256']==d.h.digest(rows),'native86_members')
    d.h.require(all(r['sourceRole']=='calibration' and r['requestedRole']=='train' and
        r['group']=='fixture-procedural-renderer-v1' and r['changed'] is True for r in rows),'native86_roles')
    return p


def source_records(path):
    proposal=d.h.sealed(path,'native86-role-proposal-v1');validate_proposal(proposal)
    rows=verified_records()
    d.h.require([dict(r,requestedRole='train') for r in rows]==proposal['members'],'native86_source_changed')
    return rows


def build_admission(old, previous, proposal, decision, source, corpus):
    validate_proposal(proposal)
    d.h.require(decision.get('version')=='native86-role-decision-v1' and decision.get('approved') is True and
        decision.get('reviewer') and decision.get('decisionReference') and
        decision.get('memberSHA256')==proposal['memberSHA256'],'native86_explicit_role_decision')
    d.h.require(Counter(r['split'] for r in d.admitted(old,previous))=={'train':44,'development':5},'native86_previous_roles')
    additions=[dict({k:v for k,v in r.items() if k!='requestedRole'},id=source['sha256']+':'+r['id']) for r in proposal['members']]
    d.h.require(corpus['records']==old['records']+additions and corpus['excluded']==old['excluded'] and
        corpus['sources']==dict(old['sources'],nativeActions=source),'native86_records_changed')
    d.h.require(d.corpus_document(corpus['sources'],corpus['records'],corpus['excluded'])==corpus,'native86_corpus_digest')
    result=dict(version='focus-direct-admission-v1',approved=True,reviewer=decision['reviewer'],
        decisionReference=decision['decisionReference'],corpusSHA256=corpus['corpusSHA256'],
        assignments={**previous['assignments'],**{r['id']:'train' for r in additions}},
        limitation='68train/5exposed development; no independent final evaluation or promotion.')
    d.h.require(Counter(r['split'] for r in d.admitted(corpus,result))=={'train':68,'development':5},'native86_result_roles')
    return result


def admit(proposal_path,decision_path,output):
    out=d.h.fresh(output);path=d.h.local(proposal_path)
    proposal=d.h.sealed(path,'native86-role-proposal-v1');validate_proposal(proposal)
    decision=d.h.read(d.h.local(decision_path))
    # Check approval before expensive source reconstruction or creating an output tree.
    d.h.require(decision.get('approved') is True,'native86_explicit_role_decision')
    old=d.h.read(d.h.checked(d.h.ROOT,proposal['existingCorpus']))
    previous=d.h.read(d.h.checked(d.h.ROOT,proposal['existingAdmission']))
    source=d.h.ref(path);corpus=d.collect(dict(old['sources'],nativeActions=source))
    admission=build_admission(old,previous,proposal,decision,source,corpus)
    out.mkdir(parents=True);d.h.write(out/'corpus.json',corpus);d.h.write(out/'admission.json',admission)
    d.h.write(out/'receipt.json',dict(version='native86-admission-receipt-v1',proposal=source,
        decision=d.h.ref(d.h.local(decision_path)),corpus=d.h.ref(out/'corpus.json'),
        admission=d.h.ref(out/'admission.json'),trainingLaunched=False),sealed=True)
    return admission


def prepare(output):
    out=d.h.fresh(output);rows=verified_records()
    base=d.h.ROOT/'reports/work/NATIVE-ADMISSION-77/admitted'
    corpus=d.h.read(base/'corpus.json');admission=d.h.read(base/'admission.json')
    old=d.admitted(corpus,admission)
    d.h.require(Counter(r['split'] for r in old)=={'train':44,'development':5},'native86_existing_roles')
    # Recheck old source bytes before comparing retained RGBA hashes; never reseal them.
    for r in old:
        for ref in r['images']:d.h.checked(d.h.ROOT,ref)
    members=[dict(r,requestedRole='train') for r in rows]
    newpixels={v for r in rows for v in r['decodedPixelHashes']}
    overlap={s:sorted(newpixels & {v for r in old if r['split']==s for v in r['decodedPixelHashes']}) for s in ('train','development')}
    d.h.require(not overlap['development'],'native86_development_overlap')
    p=dict(version='native86-role-proposal-v1',**d.h.FLAGS,approved=False,executionEligible=False,
        members=members,memberSHA256=d.h.digest(members),overlap=overlap,
        existingCorpus=d.h.ref(base/'corpus.json'),existingAdmission=d.h.ref(base/'admission.json'),
        prospectiveCounts=dict(train=68,development=5,independentEvaluation=0),
        scrollStates=dict(Counter(str(r['observedScroll']) for r in rows)),
        themeCounts=dict(Counter(r['recipe']['theme'] for r in rows)),
        excludedAppearancePairs=36,
        limitation='Proposal only. Shared Fixture ancestry excluded from final evaluation; Settings remains exposed development.')
    validate_proposal(p);out.mkdir(parents=True);d.h.write(out/'proposal.json',p,sealed=True)
    d.h.write(out/'decision-template.json',dict(version='native86-role-decision-v1',approved=False,
        memberSHA256=p['memberSHA256'],reviewer=None,decisionReference=None))
    print({k:p[k] for k in ('memberSHA256','prospectiveCounts','scrollStates','themeCounts','overlap')})


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    p.add_argument('--proposal');p.add_argument('--decision');a=p.parse_args()
    if bool(a.proposal)!=bool(a.decision):p.error('--proposal and --decision are required together')
    if a.proposal:admit(a.proposal,a.decision,a.output)
    else:prepare(a.output)
