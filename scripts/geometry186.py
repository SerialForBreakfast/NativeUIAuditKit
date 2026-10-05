"""One box-loss comparison through unchanged replay trainer/evaluator."""
import argparse
from pathlib import Path
import replay179 as r
h,p,e=r.h,r.p,r.e
BASE=h.ROOT/'reports/work/IOS-GEOMETRY-186/attempt02/artifacts'
CANONICAL=h.ROOT/'reports/work/IOS-DIAG-185/artifacts/proposal.json'
CONTROL=h.ROOT/'reports/work/IOS-REPLAY-184/artifacts/experiment'
RUN=h.ROOT/'NativeUITrainer/yolo_runs/geometry186-r023'


def compatible(proposal,control):
    h.require(proposal['version']=='geometry185-proposal-v1','proposal_version')
    h.require(proposal['rows']==control['rows'] and len(control['rows'])==432,'changed_membership')
    h.require(proposal['initializer']==control['initializer'] and proposal['membership']==control['membership'],'changed_inputs')
    h.require(proposal['schedule']==control['schedule']==r.schedule(54,10,.25),'changed_schedule')
    h.require(control['args']['box']==7.5 and proposal['config']==dict(control['args'],box=15.),'not_single_treatment')


def bind():
    r.OUT=BASE/'experiment';r.RUN=RUN;r.PROPOSAL=BASE/'launch-proposal.json'


def prepare():
    h.require(not BASE.exists() and not RUN.exists(),'output_collision')
    proposal=p.sealed(CANONICAL);control=p.sealed(CONTROL/'protocol.json')
    for key in ('diagnosis','referenceProtocol','referenceEvaluation','source'):h.checked(h.ROOT,proposal[key],256*1024**2)
    compatible(proposal,control)
    for row in proposal['rows']:
        for key in ('image','annotation','label'):h.checked(h.ROOT,row[key])
    old=p.sealed(r.PROPOSAL)
    bridge=dict(fitIDs=[row['id'] for row in proposal['rows'][:216]],replayRows=proposal['rows'][216:],membership=proposal['membership'],omittedFitTrainSupport=old['omittedFitTrainSupport'])
    BASE.mkdir(parents=True);h.write(BASE/'launch-proposal.json',bridge,sealed=True)
    bind();r.OUT=BASE/'prepared';r.prepare()
    prepared=p.sealed(r.OUT/'protocol.json');input_doc=h.read(r.OUT/'input.json')
    input_doc['corpusID']='geometry186-training-only'
    bind();r.OUT.mkdir();(r.OUT/'dataset').symlink_to(BASE/'prepared/dataset',target_is_directory=True)
    h.write(r.OUT/'input.json',input_doc);e.load_request(r.OUT/'input.json',41)
    args=dict(prepared['args'],box=15.)
    expected=dict(control['args'],box=15.,data=args['data'],name=RUN.name,project=str(RUN.parent))
    h.require(args==expected and prepared['rows']==proposal['rows'],'resolved_config_differs')
    protocol=dict(prepared);protocol.pop('seal')
    protocol.update(args=args,input=h.ref(r.OUT/'input.json'),epochScheduleIdenticalTo022=True,
        sources=prepared['sources']+[h.ref(__file__),h.ref(CANONICAL),h.ref(CONTROL/'protocol.json'),h.ref(BASE/'prepared/protocol.json')])
    h.write(r.OUT/'protocol.json',protocol,sealed=True)
    print('186prepared:432unchanged train members; box7.5→15 only',flush=True)


def verify():
    bind();doc=r.inputs();proposal=p.sealed(CANONICAL);control=p.sealed(CONTROL/'protocol.json');compatible(proposal,control)
    for row in proposal['rows']:h.checked(h.ROOT,row['annotation'])
    return doc


def main(mode):
    if mode=='prepare':prepare();return
    verify();getattr(r,mode)()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','train','infer','report']);main(parser.parse_args().mode)
