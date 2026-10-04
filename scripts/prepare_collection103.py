"""Prepare immutable derivatives or explicitly admit approved collection pairs; never train."""
import argparse
from collections import Counter
from pathlib import Path
import time
import numpy as np
import focus_candidate_ranker as r
import evaluate_collection102 as c
from diagnose_signal95 import encoded

h=r.d.h
VERSION='collection103-preparation-v1'


def source_records(path):
    proposal=h.sealed(path,c.VERSION);c.validate_proposal(proposal)
    rows=c.verified_records()
    h.require(proposal['members']==[dict(v,requestedRole='train') for v in rows],
        'collection103_source_changed')
    return rows


def build_admission(old,previous,proposal,decision,source,corpus):
    c.validate_proposal(proposal)
    h.require(decision.get('version')=='collection103-role-decision-v1' and
        decision.get('approved') is True and decision.get('reviewer') and
        decision.get('decisionReference') and decision.get('memberSHA256')==proposal['memberSHA256'],
        'collection103_explicit_role_decision')
    h.require(Counter(v['split'] for v in r.d.admitted(old,previous))=={'train':68,'development':5},
        'collection103_old_roles')
    additions=[dict({k:v for k,v in row.items() if k!='requestedRole'},id=source['sha256']+':'+row['id'])
               for row in proposal['members']]
    h.require(corpus['records']==old['records']+additions and corpus['excluded']==old['excluded'] and
        corpus['sources']==dict(old['sources'],nativeCollection=source), 'collection103_preserve_records')
    h.require(corpus==r.d.corpus_document(corpus['sources'],corpus['records'],corpus['excluded']),
        'collection103_corpus_seal')
    result=dict(version='focus-direct-admission-v1',approved=True,reviewer=decision['reviewer'],
        decisionReference=decision['decisionReference'],corpusSHA256=corpus['corpusSHA256'],
        assignments={**previous['assignments'],**{v['id']:'train' for v in additions}},
        limitation='108real training pairs/5exposed development; no independent final evaluation or promotion.')
    h.require(Counter(v['split'] for v in r.d.admitted(corpus,result))=={'train':108,'development':5},
        'collection103_result_roles')
    return result


def admit(proposal_path,decision_path,output):
    out=h.fresh(output);path=h.local(proposal_path)
    proposal=h.sealed(path,c.VERSION);c.validate_proposal(proposal)
    decision=h.read(h.local(decision_path))
    h.require(decision.get('version')=='collection103-role-decision-v1' and
        decision.get('approved') is True and decision.get('memberSHA256')==proposal['memberSHA256'] and
        decision.get('reviewer') and decision.get('decisionReference'),'collection103_explicit_role_decision')
    old=h.read(h.checked(h.ROOT,proposal['existingCorpus']))
    previous=h.read(h.checked(h.ROOT,proposal['existingAdmission']))
    source=h.ref(path);corpus=r.d.collect(dict(old['sources'],nativeCollection=source))
    result=build_admission(old,previous,proposal,decision,source,corpus)
    out.mkdir(parents=True);h.write(out/'corpus.json',corpus);h.write(out/'admission.json',result)
    h.write(out/'receipt.json',dict(version='collection103-admission-receipt-v1',proposal=source,
        decision=h.ref(h.local(decision_path)),corpus=h.ref(out/'corpus.json'),
        admission=h.ref(out/'admission.json'),trainingLaunched=False),sealed=True)
    return result


def validate_training_binding(doc,rows,x=None):
    """Training admission is distinct from the retained calibration preparation."""
    prep=h.sealed(h.checked(h.ROOT,doc['preparation']),VERSION)
    receipt=r.sealed(h.checked(h.ROOT,doc['admissionReceipt']),'collection103-admission-receipt-v1')
    decision=h.read(h.checked(h.ROOT,receipt['decision']))
    h.require(decision.get('approved') is True and decision.get('memberSHA256')==prep['memberSHA256'] and
        receipt['proposal']==prep['proposal'],'collection104_role_binding')
    corpus=h.read(h.checked(h.ROOT,receipt['corpus']))
    admission=h.read(h.checked(h.ROOT,receipt['admission']))
    h.require(rows==r.d.admitted(corpus,admission) and len(rows)==113 and
        prep['rowIDs']==[v['id'] for v in rows] and
        prep['rowRoles']==[v['split'] for v in rows[:73]]+['calibration']*40,
        'collection104_prepared_membership')
    old=h.read(h.checked(h.ROOT,prep['oldCorpus']))
    previous=h.read(h.checked(h.ROOT,prep['oldAdmission']))
    proposal=h.sealed(h.checked(h.ROOT,prep['proposal']),c.VERSION)
    h.require(admission==build_admission(old,previous,proposal,decision,prep['proposal'],corpus),
        'collection104_admission_changed')
    # Only this unchanged encoder generates the new40 entries. The original73
    # tensor is independently pinned to the historical model protocol below.
    encoder=next(v for v in prep['implementation'] if v['path'].endswith('/diagnose_signal95.py'))
    h.checked(h.ROOT,encoder)
    if x is not None:
        h.require(doc['x']==prep['x'] and x.shape==(113,6,128,192),'collection104_tensor_binding')


def original_negatives(doc,rows,x):
    import focus_change_adaptation as change
    parent=h.read(h.checked(h.ROOT,doc['originalProtocol']))
    h.require(parent['configuration']==change.REPAIR_CONFIG and
        parent['protocolSHA256']==h.digest({k:v for k,v in parent.items() if k!='protocolSHA256'}),
        'collection104_original_protocol')
    old=r.d.admitted(h.read(h.checked(h.ROOT,parent['corpus'])),h.read(h.checked(h.ROOT,parent['admission'])))
    old_x=np.load(h.checked(h.ROOT,parent['x'],64*1024**2),allow_pickle=False)
    h.require(rows[:73]==old and np.array_equal(x[:73],old_x),'collection104_old_inputs_changed')
    derived=change.self_pair_proposal(old,old_x)
    approved=h.read(h.checked(h.ROOT,parent['derivedProposal']))
    h.require(approved['seal']==h.digest({k:v for k,v in approved.items() if k!='seal'}) and
        all(approved.get(k)==v for k,v in derived.items()) and len(derived['entries'])==122,
        'collection104_original_negatives')
    return derived['entries']


def ready(admission_root,preparation_path,output):
    """Bind admitted data/cached inputs to the two existing trainer entrypoints."""
    import focus_change_adaptation as change
    from prepare_transition_inputs import references
    start=time.monotonic();out=h.fresh(output);root=h.local(admission_root)
    prep_path=h.local(preparation_path);prep=h.sealed(prep_path,VERSION)
    corpus=h.read(root/'corpus.json');admission=h.read(root/'admission.json')
    rows=r.d.admitted(corpus,admission)
    common=dict(preparation=h.ref(prep_path),admissionReceipt=h.ref(root/'receipt.json'))
    x=np.load(h.checked(h.ROOT,prep['x'],64*1024**2),allow_pickle=False)
    validate_training_binding(dict(common,x=prep['x']),rows,x)
    for ref in references(corpus):h.checked(h.ROOT,ref)
    deriv_path=h.checked(h.ROOT,prep['derivatives'])
    deriv=r.sealed(deriv_path,'ranking-inspection-derivatives-v1')
    h.require(deriv['identity']==r.derivative_identity() and deriv['inputs']==prep['candidates'],
        'collection104_derivative_binding')
    inspection=r.sealed(h.checked(h.ROOT,deriv['inputs']),'calibration-proposals-v1')
    frames=inspection['frames'];r.validate_frames(frames)
    from prepare_proposal74 import unique_frames
    roles=unique_frames(rows)
    h.require(set(roles)=={f['id'] for f in frames} and len(frames)==187,'collection104_frames')
    bound=[dict(f,split=roles[f['id']]['split'],source=deriv['inputs']) for f in frames]
    inputs=dict(version='transition-candidate-inputs-v2',frames=bound,
        pairs=[dict(id=v['id'],split=v['split'],group=v['group'],frames=[i['sha256'] for i in v['images']]) for v in rows])
    by={f['id']:f for f in frames}
    labels=[dict(pairID=v['id'],endpoint=e,frameID=im['sha256'],split=v['split'],
        **r.targets(by[im['sha256']]['candidates'],box)) for v in rows
        for e,im,box in zip(('before','after'),v['images'],v['boxes'])]
    r.supervision(inputs,labels,rows)
    out.mkdir(parents=True);h.write(out/'inputs.json',inputs,sealed=True)
    h.write(out/'supervision.json',dict(version='transition-candidate-supervision-v1',inputs=h.ref(out/'inputs.json'),
        corpus=h.ref(root/'corpus.json'),admission=h.ref(root/'admission.json'),labels=labels),sealed=True)
    h.write(out/'bank.json',dict(version='ranking-encodings-v1',inputs=h.ref(out/'inputs.json'),
        tensor=deriv['tensor'],runtime=deriv['identity']['runtime'],encoding=r.CONFIG['encoding'],
        encodingDependencies=deriv['identity']['dependencies'],derivativeIdentity=deriv['identity'],
        items=deriv['items'],cropPNGHashes=deriv['cropPNGHashes'],invocations=0,reusedInspection=h.ref(deriv_path)),sealed=True)
    _,_,data=r.bank(out/'bank.json')
    frozen=r.sealed(h.ROOT/'NativeUITrainer/focus_ring_runs/repair100-dtm024/result.json',change.VERSION)
    ranked=r.sealed(h.ROOT/'NativeUITrainer/focus_ring_runs/native87-dtm020/result.json',r.VERSION)
    torch=r.d.torch_runtime();torch.set_num_threads(2)
    state=torch.load(h.checked(h.ROOT,frozen['model']),map_location='cpu',weights_only=True)
    net,_=change.initialize(state,change.COLLECTION_CONFIG)
    rs=torch.load(h.checked(h.ROOT,ranked['model']),map_location='cpu',weights_only=True)
    h.require(rs['configuration']==r.ACTION_CONFIG,'collection104_rank_initializer')
    rank=r.model(torch,rs['configuration']);rank.load_state_dict(rs['state'],strict=True);rank.eval()
    with torch.inference_mode():
        probabilities=change.score_change(net,torch.from_numpy(x),change.COLLECTION_CONFIG).tolist()
        scores=rank(torch.from_numpy(r.features(data,inputs,r.ACTION_CONFIG))).flatten().tolist()
    h.require(all(abs(p-v['after'])<=1e-6 for p,v in zip(probabilities[:73],frozen['results'])),
        'collection104_change_retention_parity')
    selections={};cursor=0
    for f in frames:
        n=len(f['candidates']);selections[f['id']]=r.choose(f['candidates'],scores[cursor:cursor+n]);cursor+=n
    results=[]
    for v in rows:
        chosen=[selections[i['sha256']] for i in v['images']]
        overlaps=[r.iou(p['bounds'],b) for p,b in zip(chosen,v['boxes'])]
        results.append(dict(id=v['id'],split=v['split'],selected=chosen,boxIoUs=overlaps,bothBoxesCorrect=min(overlaps)>=.5))
    h.require(all(v['selected']==old['selected'] for v,old in zip(results[:73],ranked['results'])),
        'collection104_rank_retention_parity')
    h.write(out/'reference.json',dict(version='native-ranking-reference-v1',model=ranked['model'],
        inputs=h.ref(out/'inputs.json'),results=results),sealed=True)
    h.write(out/'change-control.json',dict(version='native88-frozen-diagnostic-v1',corpus=h.ref(root/'corpus.json'),
        changeModel=frozen['model'],rankModel=ranked['model'],
        results=[dict(id=v['id'],probability=p) for v,p in zip(rows,probabilities)]),sealed=True)
    h.write(out/'rank-control.json',dict(version='collection104-frozen-change-v1',**h.FLAGS,corpusSHA256=corpus['corpusSHA256'],
        models={'DTM024':frozen['model']},results=[dict(id=v['id'],model='DTM024',condition='baseline',
        prediction=dict(changeProbability=p)) for v,p in zip(rows,probabilities)]),sealed=True)
    cd=dict(version=change.VERSION,configuration=change.COLLECTION_CONFIG,pins=change.pins(),**common,
        corpus=h.ref(root/'corpus.json'),admission=h.ref(root/'admission.json'),x=prep['x'],
        rowIDs=[v['id'] for v in rows],sourceReferences=references(corpus),originalProtocol=frozen['protocol'],
        initializer=frozen['model'],control=h.ref(out/'change-control.json'),ranker=h.ref(out/'reference.json'))
    original_negatives(cd,rows,x)
    rd=dict(version=r.VERSION,configuration=r.COLLECTION_CONFIG,pins=r.pins(),**common,
        bank=h.ref(out/'bank.json'),supervision=h.ref(out/'supervision.json'),control=h.ref(out/'rank-control.json'),
        reference=h.ref(out/'reference.json'),initializer=ranked['model'])
    for name,doc,arm,approval_version,run in [('change',cd,change.ARM,'change-adaptation-approval-v1','collection104-dtm025'),
            ('rank',rd,r.ARM,'ranking-approval-v1','collection104-dtm026')]:
        doc['protocolSHA256']=h.digest(doc);h.write(out/(name+'-protocol.json'),doc)
        h.write(out/(name+'-approval.json'),dict(version=approval_version,approved=True,protocolSHA256=doc['protocolSHA256'],
            arm=arm,runName=run,decisionReference='Maintainer Yea continue: exact40 admission and two600epoch comparisons, standing local training approval; no capture/export/promotion.'))
    h.write(out/'preparation-report.json',dict(version='collection104-ready-v1',elapsedSeconds=time.monotonic()-start,
        trainingLaunched=False,nativeCropInvocations=0,realTrain=108,development=5,trainingFrames=178,
        changeProtocol=cd['protocolSHA256'],rankProtocol=rd['protocolSHA256']),sealed=True)
    print(cd['protocolSHA256'],rd['protocolSHA256'])


def prepare(proposal_path,output):
    start=time.monotonic();out=h.fresh(output);path=h.local(proposal_path)
    proposal=h.sealed(path,c.VERSION);c.validate_proposal(proposal);new=source_records(path)
    old=h.read(h.checked(h.ROOT,proposal['existingCorpus']))
    previous=h.read(h.checked(h.ROOT,proposal['existingAdmission']))
    h.require(old==r.d.collect(old['sources']),'collection103_existing_source_changed')
    rows=r.d.admitted(old,previous)
    h.require(Counter(v['split'] for v in rows)=={'train':68,'development':5},'collection103_old_roles')
    # Pending examples have explicit calibration roles, not speculative assignments.
    additions=[dict(v,id=h.ref(path)['sha256']+':'+v['id'],split='calibration') for v in new]
    combined=rows+additions
    prior=h.read(h.ROOT/'reports/work/REPAIR-100/ready/protocol.json')
    h.require(prior['protocolSHA256']==h.digest({k:v for k,v in prior.items() if k!='protocolSHA256'}) and
        prior['corpus']==proposal['existingCorpus'] and prior['admission']==proposal['existingAdmission'] and
        prior['rowIDs']==[v['id'] for v in rows], 'collection103_prior_binding')
    x=np.load(h.checked(h.ROOT,prior['x'],64*1024**2),allow_pickle=False)
    h.require(x.shape==(73,6,128,192) and x.dtype==np.float32 and np.isfinite(x).all(),
        'collection103_prior_tensor')
    encode_start=time.monotonic()
    new_x=np.stack([encoded(*(r.d.pixels(image) for image in v['images']),size=(192,128))[0] for v in new])
    combined_x=np.concatenate((x,new_x));encode_seconds=time.monotonic()-encode_start
    result=r.sealed(h.ROOT/'NativeUITrainer/focus_ring_runs/native87-dtm020/result.json',r.VERSION)
    protocol=h.read(h.checked(h.ROOT,result['protocol']))
    bank=r.sealed(h.checked(h.ROOT,protocol['bank']),'ranking-encodings-v1')
    old_inputs=r.load_inputs(h.checked(h.ROOT,bank['inputs']))
    new_path=h.ROOT/'reports/work/CALIBRATION-102/candidates/inputs.json'
    new_inputs=r.sealed(new_path,'calibration-proposals-v1')
    h.require(new_inputs['source']==h.ref(path),'collection103_candidate_binding')
    frames=[{k:v[k] for k in ('id','image','size','candidates')} for v in old_inputs['frames']+new_inputs['frames']]
    expected={image['sha256'] for v in combined for image in v['images']}
    h.require(len(frames)==187 and len({v['id'] for v in frames})==187 and
        {v['id'] for v in frames}==expected, 'collection103_frame_membership')
    for v in combined:
        for image in v['images']:h.checked(h.ROOT,image)
    out.mkdir(parents=True)
    h.write(out/'inputs.json',dict(version='calibration-proposals-v1',**h.FLAGS,frames=frames,
        sourceRoles='68train/5development unchanged;40calibration pending',
        sources=[h.ref(h.checked(h.ROOT,bank['inputs'])),h.ref(new_path)]),sealed=True)
    with (out/'x.npy').open('xb') as stream:np.save(stream,combined_x,allow_pickle=False)
    deriv=r.prepare_derivatives(out/'derivatives',out/'inputs.json',h.ROOT/'.build/batch79-derivatives')
    report=dict(version=VERSION,**h.FLAGS,executionEligible=False,approved=False,trainingLaunched=False,
        proposal=h.ref(path),memberSHA256=proposal['memberSHA256'],oldCorpus=proposal['existingCorpus'],
        oldAdmission=proposal['existingAdmission'],rowIDs=[v['id'] for v in combined],
        rowRoles=[v['split'] for v in combined],x=h.ref(out/'x.npy'),inputSize=[192,128],
        reusedPairs=73,newPairs=40,tensorBytes=combined_x.nbytes,encodingSeconds=encode_seconds,
        candidates=h.ref(out/'inputs.json'),derivatives=h.ref(out/'derivatives/derivatives.json'),
        cacheStatistics=deriv['statistics'],elapsedSeconds=time.monotonic()-start,
        implementation=[h.ref(h.ROOT/'scripts'/p) for p in
            ('prepare_collection103.py','evaluate_collection102.py','diagnose_signal95.py','focus_direct_transition.py')],
        limitation='Preparation is not admission or a training protocol. Explicit exact role decision remains required.')
    h.write(out/'preparation.json',report,sealed=True)
    h.write(out/'decision-template.json',dict(version='collection103-role-decision-v1',approved=False,
        memberSHA256=proposal['memberSHA256'],reviewer=None,decisionReference=None))
    print({k:report[k] for k in ('reusedPairs','newPairs','tensorBytes','cacheStatistics','elapsedSeconds')})
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--proposal',required=True)
    p.add_argument('--output',required=True);p.add_argument('--decision')
    p.add_argument('--admission-root');p.add_argument('--preparation');a=p.parse_args()
    if a.admission_root or a.preparation:
        if not (a.admission_root and a.preparation) or a.decision:p.error('ready requires admission-root and preparation, no decision')
        ready(a.admission_root,a.preparation,a.output)
    elif a.decision:admit(a.proposal,a.decision,a.output)
    else:prepare(a.proposal,a.output)
