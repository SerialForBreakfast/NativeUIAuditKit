"""Materialize an explicitly approved data-role change; never launch training."""
import argparse
from collections import Counter
import focus_direct_transition as d
import human_annotation_review as h
from propose_negative_admission65 import validate_proposal


def read_proposal(path):
    doc=h.read(path)
    h.require(doc.get('seal')==h.digest({k:v for k,v in doc.items() if k!='seal'}),
        'proposal_seal_changed')
    return validate_proposal(doc)


def build_admission(old, corpus, previous, proposal, decision):
    validate_proposal(proposal)
    h.require(decision.get('version')=='focus-negative-role-decision-v1' and
        decision.get('approved') is True and decision.get('reviewer') and
        decision.get('decisionReference'),'missing_role_decision')
    h.require(decision['memberSHA256']==proposal['memberSHA256']==h.digest(proposal['members']),
        'approved_membership_changed')
    old_rows=d.admitted(old,previous)
    h.require(Counter(r['split'] for r in old_rows)==dict(train=24,development=5),'original_roles')
    h.require(corpus['records'][:29]==old['records'] and corpus['excluded']==old['excluded'],
        'original_records_changed')
    expected=[dict({k:v for k,v in r.items() if k!='requestedRole'},
        id=proposal['source']['sha256']+':'+r['id']) for r in proposal['members']]
    h.require(corpus['records'][29:]==expected,'new_records_changed')
    result=dict(version='focus-direct-admission-v1',approved=True,reviewer=decision['reviewer'],
        decisionReference=decision['decisionReference'],corpusSHA256=corpus['corpusSHA256'],
        assignments={**previous['assignments'],**{r['id']:'train' for r in expected}},
        limitation='32 training / 5 exposed development; no independent evaluation. Data role only, no run authorization.')
    rows=d.admitted(corpus,result)
    h.require(Counter(r['split'] for r in rows)==dict(train=32,development=5),'new_roles')
    return result


def run(base,proposal_path,decision_path,output):
    out=h.fresh(output)
    protocol=h.read(h.local(base));proposal=read_proposal(h.local(proposal_path))
    decision=h.read(h.local(decision_path));previous=h.read(h.checked(h.ROOT,protocol['admission']))
    old=d.collect(protocol['sources'])
    h.require(old['corpusSHA256']==protocol['corpusSHA256'],'original_corpus_changed')
    corpus=d.collect(dict(protocol['sources'],negatives=proposal['source']))
    admission=build_admission(old,corpus,previous,proposal,decision)
    out.mkdir(parents=True)
    h.write(out/'corpus.json',corpus)
    h.write(out/'admission.json',admission)
    # Re-read the published artifacts and exercise the actual admission entrypoint.
    rows=d.admitted(h.read(out/'corpus.json'),h.read(out/'admission.json'))
    h.write(out/'receipt.json',dict(version='focus-negative-admission-receipt-v1',
        decision=h.ref(h.local(decision_path)),proposal=h.ref(h.local(proposal_path)),
        corpus=h.ref(out/'corpus.json'),admission=h.ref(out/'admission.json'),
        originalCorpusSHA256=old['corpusSHA256'],counts=dict(Counter(r['split'] for r in rows)),
        originalRecordsUnchanged=True,independentEvaluation=0,trainingLaunched=False),sealed=True)
    print(corpus['corpusSHA256'],dict(Counter(r['split'] for r in rows)))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('base','proposal','decision','output'):p.add_argument('--'+name,required=True)
    a=p.parse_args();run(a.base,a.proposal,a.decision,a.output)
