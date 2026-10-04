"""Expanded-data gate and one tranche-authorized experiment; no launch here."""
from collections import Counter
from pathlib import Path
import focus_direct_transition as d
from admit_negatives65 import build_admission,read_proposal
from prepare_robustness63 import verify_gate as original_gate

BASE=d.h.ROOT/'reports/work/DATA-67'


def original_corpus(corpus,protocol):
    rows=corpus['records'][:29]
    old=dict(version=corpus['version'],sources=protocol['sources'],records=rows,
        excluded=corpus['excluded'],groups={g:dict(Counter('changed' if r['changed'] else 'unchanged'
            for r in rows if r['group']==g)) for g in sorted({r['group'] for r in rows})},trainingEligible=False)
    old['corpusSHA256']=d.digest(old)
    d.h.require(old['corpusSHA256']==protocol['corpusSHA256'],'expanded_original_changed')
    d.h.require({k:v for k,v in corpus['sources'].items() if k!='negatives'}==protocol['sources'],
        'expanded_sources_changed')
    return old


def verify_gate(reference,corpus,rows,admission):
    doc=d.h.read(d.h.checked(d.h.ROOT,reference))
    d.h.require(doc.get('version')=='expanded-direct-gate-v1','expanded_gate_version')
    protocol=d.h.read(d.h.checked(d.h.ROOT,doc['originalProtocol']))
    old=original_corpus(corpus,protocol)
    previous=d.h.read(d.h.checked(d.h.ROOT,protocol['admission']))
    old_rows=d.admitted(old,previous);original_gate(doc['fitEvidence'],old,old_rows)
    proposal=read_proposal(d.h.checked(d.h.ROOT,doc['proposal']))
    decision=d.h.read(d.h.checked(d.h.ROOT,doc['decision']))
    expected=build_admission(old,corpus,previous,proposal,decision)
    d.h.require(corpus['sources']['negatives']==proposal['source'] and
        d.h.read(d.h.checked(d.h.ROOT,admission))==expected and d.admitted(corpus,expected)==rows,
        'expanded_admission_changed')
    return [r['id'] for r in old_rows if r['split']=='train']


def prepare():
    from prepare_transition_inputs import prepare as prepare_inputs,manifest
    base=d.h.fresh(BASE/'ready');base.mkdir(parents=True)
    source=d.h.ROOT/'reports/work/GENERALIZATION-65'
    prepare_inputs(source/'admission/corpus.json',source/'admission/admission.json',d.h.ROOT/'.build/data67-bank')
    prepared=d.h.ROOT/'.build/data67-bank/manifest.json';inputs,corpus,rows=manifest(prepared)
    gate=dict(version='expanded-direct-gate-v1',originalProtocol=d.h.ref(d.h.ROOT/'reports/work/FIT-61/ready/protocol.json'),
        fitEvidence=d.h.ref(d.h.ROOT/'reports/work/FIT-61/evaluation.json'),
        proposal=d.h.ref(source/'negative-admission-proposal-verified.json'),decision=d.h.ref(source/'data-role-decision.json'))
    d.h.write(base/'gate.json',gate);gate_ref=d.h.ref(base/'gate.json')
    verify_gate(gate_ref,corpus,rows,inputs['admission'])
    protocol=dict(version=d.VERSION,sources=corpus['sources'],corpusSHA256=corpus['corpusSHA256'],
        admission=inputs['admission'],configuration=d.EXPOSURE_CONFIG,implementation=d.h.ref(Path(d.__file__)),
        pins=d.pins(),expandedGate=gate_ref,preparedInputs=d.h.ref(prepared))
    protocol['protocolSHA256']=d.digest(protocol);d.h.write(base/'protocol.json',protocol)
    d.h.write(base/'approval.json',dict(version='focus-direct-approval-v1',approved=True,
        protocolSHA256=protocol['protocolSHA256'],arm=d.ARM,runName='data67-dtm012',
        decisionReference='2026-10-03 active goal and standing local experiment tranche envelope: DATA-67 one600epoch DTM011-config comparison on explicitly approved32/5roles;2GiB/no wall-time cap. No capture/export/promotion.'))
    print(protocol['protocolSHA256'])


if __name__=='__main__':prepare()
