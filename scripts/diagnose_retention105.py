"""Frozen ranker replay and per-frame drift diagnosis, no fitting or capture."""
import argparse
from collections import Counter
from pathlib import Path
import time
import numpy as np
import focus_candidate_ranker as r

h=r.d.h
READY=h.ROOT/'reports/work/COLLECTION-104/ready'


def load():
    protocol=h.read(READY/'rank-protocol.json')
    h.require(protocol['protocolSHA256']==h.digest({k:v for k,v in protocol.items() if k!='protocolSHA256'}), 'retention_protocol')
    bank,inputs,data=r.bank(h.checked(h.ROOT,protocol['bank']))
    labels=r.sealed(h.checked(h.ROOT,protocol['supervision']),'transition-candidate-supervision-v1')
    rows=r.d.admitted(h.read(h.checked(h.ROOT,labels['corpus'])),h.read(h.checked(h.ROOT,labels['admission'])))
    positives=r.supervision(inputs,labels['labels'],rows)
    from prepare_collection103 import validate_training_binding
    validate_training_binding(protocol,rows)
    return protocol,bank,inputs,data,rows,positives


def groups(inputs):
    cursor=0;result=[]
    for frame in inputs['frames']:
        end=cursor+len(frame['candidates']);result.append((frame,cursor,end));cursor=end
    return result


def candidate_summary(frame,scores,positive_ids):
    h.require(len(scores)==len(frame['candidates']) and np.isfinite(scores).all(), 'retention_scores')
    ids=[c['id'] for c in frame['candidates']]
    positive=np.array([v in positive_ids for v in ids]);h.require(positive.any() and (~positive).any(),'retention_support')
    selected=r.choose(frame['candidates'],scores)
    return dict(selected=selected,correct=selected['id'] in positive_ids,
        positiveMargin=float(scores[positive].max()-scores[~positive].max()),
        positiveCandidateCount=int(positive.sum()))


def diagnose(output):
    start=time.monotonic();out=h.fresh(output)
    protocol,bank,inputs,data,rows,positives=load()
    torch=r.d.torch_runtime();torch.set_num_threads(2)
    refs=dict(DTM020=protocol['initializer'],DTM026=r.sealed(h.ROOT/'NativeUITrainer/focus_ring_runs/collection104-dtm026/result.json',r.VERSION)['model'])
    networks={};states={};logits={};activations={}
    x=torch.from_numpy(r.features(data,inputs,r.COLLECTION_CONFIG))
    for name,ref in refs.items():
        state=torch.load(h.checked(h.ROOT,ref),map_location='cpu',weights_only=True)
        net=r.model(torch,state['configuration']);net.load_state_dict(state['state'],strict=True);net.eval()
        with torch.inference_mode():
            logits[name]=net(x).flatten().numpy();activations[name]=net[:2](x).numpy()
        networks[name]=net;states[name]=state
    oldids={im['sha256'] for row in rows[:73] if row['split']=='train' for im in row['images']}
    reports=[];selected={k:{} for k in refs}
    for f,a,b in groups(inputs):
        summaries={k:candidate_summary(f,logits[k][a:b],positives[f['id']]) for k in refs}
        for k in refs:selected[k][f['id']]=summaries[k]['selected']
        candidates=[]
        for i,c in enumerate(f['candidates']):
            candidates.append(dict(**c,positive=c['id'] in positives[f['id']],normalizedSize=(x[a+i,-2:].numpy()).tolist(),
                scores={k:float(logits[k][a+i]) for k in refs}))
        candidates.sort(key=lambda v:(-v['scores']['DTM026'],v['id']))
        reports.append(dict(id=f['id'],group='settingsDevelopment' if f['split']=='development' else 'oldTrain' if f['id'] in oldids else 'newTrain',
            candidateCount=b-a,models=summaries,candidates=candidates,
            hiddenActivationMeanAbsDrift=float(np.abs(activations['DTM026'][a:b]-activations['DTM020'][a:b]).mean())))
    # Tie the replay to historical decisions, not merely freshly computed metrics.
    prior=r.sealed(h.checked(h.ROOT,protocol['reference']),'native-ranking-reference-v1')
    later=r.sealed(h.ROOT/'NativeUITrainer/focus_ring_runs/collection104-dtm026/result.json',r.VERSION)
    for name,doc in [('DTM020',prior),('DTM026',later)]:
        h.require([v['id'] for v in doc['results']]==[v['id'] for v in rows],'retention_replay_membership')
        h.require(all([selected[name][im['sha256']] for im in row['images']]==value['selected'] for row,value in zip(rows,doc['results'])), 'retention_replay_selection')
    summary={}
    for group in ('oldTrain','newTrain','settingsDevelopment'):
        subset=[v for v in reports if v['group']==group]
        summary[group]=dict(uniqueFrames=len(subset),proposalCovered=len(subset),
            correct={k:sum(v['models'][k]['correct'] for v in subset) for k in refs},
            meanMargin={k:float(np.mean([v['models'][k]['positiveMargin'] for v in subset])) for k in refs},
            selectionChanges=sum(v['models']['DTM020']['selected']!=v['models']['DTM026']['selected'] for v in subset))
    weights={k:dict(oldNorm=float(v.norm()),changeNorm=float((states['DTM026']['state'][k]-v).norm())) for k,v in states['DTM020']['state'].items()}
    hybrids={}
    for name,hidden,readout in [('oldHidden_newReadout','DTM020','DTM026'),('newHidden_oldReadout','DTM026','DTM020')]:
        net=r.model(torch,r.COLLECTION_CONFIG)
        net.load_state_dict({k:states[hidden if k.startswith('0.') else readout]['state'][k] for k in states['DTM020']['state']},strict=True)
        with torch.inference_mode(): scores=net(x).flatten().numpy()
        counts=Counter()
        for (frame,a,b),detail in zip(groups(inputs),reports):
            counts[detail['group']]+=candidate_summary(frame,scores[a:b],positives[frame['id']])['correct']
        hybrids[name]=dict(counts)
    out.mkdir(parents=True)
    report=dict(version='rank-retention105-diagnosis-v1',**h.FLAGS,models=refs,bank=protocol['bank'],supervision=protocol['supervision'],
        summary=summary,frames=reports,weightDrift=weights,diagnosticHybrids=hybrids,replaySelectionsExact=True,
        nativeCropInvocations=0,elapsedSeconds=time.monotonic()-start,implementation=h.ref(Path(__file__)))
    h.write(out/'diagnosis.json',report,sealed=True)
    print(summary)
    print('weightDrift',weights)
    print('diagnosticHybrids',hybrids)
    for f in reports:
        if f['group']=='settingsDevelopment':print('settings',f['id'][:12], {k:(v['correct'],round(v['positiveMargin'],3),v['selected']['bounds']) for k,v in f['models'].items()})
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();diagnose(a.output)
