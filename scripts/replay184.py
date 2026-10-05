"""Isolated positive-context comparison through the qualified replay179 workflow."""
import argparse
from pathlib import Path
import replay179 as r
h,p=r.h,r.p
BASE=h.ROOT/'reports/work/IOS-REPLAY-184/artifacts'
CANONICAL=h.ROOT/'reports/work/IOS-REPLAY-181/artifacts/proposal.json'
CONTROL=r.OUT
OLD_PROPOSAL=r.PROPOSAL
RUN=h.ROOT/'NativeUITrainer/yolo_runs/replay184-r022'


def bind():
    r.OUT=BASE/'experiment';r.RUN=RUN;r.PROPOSAL=BASE/'launch-proposal.json'


def compatible(doc,original):
    h.require(doc['version']=='replay181-proposal-v1' and len(doc['rows'])==432,'proposal_version_or_count')
    h.require(len(doc['addedIDs'])==80 and len(doc['removedIDs'])==80,'replacement_count')
    h.require(doc['schedule']==r.schedule(54,10,.25),'changed_schedule')
    h.require(doc['initializer']==original['initializer'],'changed_initializer')
    ids=[x['id'] for x in doc['rows']]
    h.require(ids[:216]==[x['id'] for x in original['rows'][:216]],'changed_fit')
    h.require(set(ids)-{x['id'] for x in original['rows']}==set(doc['addedIDs']) and
        {x['id'] for x in original['rows']}-set(ids)==set(doc['removedIDs']),'replacement_identity')
    return dict(fitIDs=ids[:216],replayRows=doc['rows'][216:],membership=doc['membership'])


def prepare():
    h.require(not BASE.exists() and not RUN.exists(),'output_collision')
    original=r.inputs();doc=p.sealed(CANONICAL)
    for ref in doc['sources']+[doc['diagnosis'],doc['referenceProtocol']]:h.checked(h.ROOT,ref,256*1024**2)
    bridge=compatible(doc,original)
    for row in doc['rows']:
        for key in ('image','annotation','label'):h.checked(h.ROOT,row[key])
    bridge['omittedFitTrainSupport']=p.sealed(OLD_PROPOSAL)['omittedFitTrainSupport']
    BASE.mkdir(parents=True);h.write(BASE/'launch-proposal.json',bridge,sealed=True)
    bind();r.prepare()
    protocol=p.sealed(r.OUT/'protocol.json')
    expected=dict(original['args'],data=protocol['args']['data'],name=RUN.name,project=str(RUN.parent))
    h.require(protocol['args']==expected,'settings_differ_from_control')
    h.require(protocol['rows']==doc['rows'],'membership_differ')
    h.write(BASE/'binding.json',dict(source=h.ref(__file__),canonical=h.ref(CANONICAL),
        controlProtocol=h.ref(CONTROL/'protocol.json'),protocol=h.ref(r.OUT/'protocol.json'),
        epochScheduleIdenticalTo021=True,trainingRole='existing train only'),sealed=True)
    print('184binding complete:432members; only composition/data/output changed',flush=True)


def verify():
    bind();doc=p.sealed(BASE/'binding.json')
    for key in ('source','canonical','controlProtocol','protocol'):h.checked(h.ROOT,doc[key],256*1024**2)
    proposal=p.sealed(CANONICAL)
    for row in proposal['rows']:h.checked(h.ROOT,row['annotation'])
    return r.inputs()


def main(mode):
    if mode=='prepare':prepare();return
    verify();getattr(r,mode)()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','train','infer','report'])
    main(parser.parse_args().mode)
