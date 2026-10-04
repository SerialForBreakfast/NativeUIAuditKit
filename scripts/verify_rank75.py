"""Frozen ranker replay and latency; inference inputs contain no focus labels."""
import argparse
import time
import numpy as np
import focus_candidate_ranker as r


def run(result_path,output):
    start=time.monotonic();result=r.sealed(r.d.h.local(result_path),r.VERSION)
    doc=r.d.h.read(r.d.h.checked(r.d.h.ROOT,result['protocol']))
    r.d.h.require(doc['pins']==r.pins(),'ranking_code_changed')
    manifest,inputs,x=r.bank(r.d.h.checked(r.d.h.ROOT,doc['bank']))
    torch=r.d.torch_runtime();torch.set_num_threads(2)
    state=torch.load(r.d.h.checked(r.d.h.ROOT,result['model']),map_location='cpu',weights_only=True)
    r.d.h.require(state['version']==r.VERSION and state['configuration']==doc['configuration'] and
        state['configuration'] in (r.CONFIG,r.NATIVE_CONFIG,r.SIZE_CONFIG,r.ACTION_CONFIG),'ranking_checkpoint_configuration')
    x=r.features(x,inputs,state['configuration'])
    net=r.model(torch,state['configuration']);net.load_state_dict(state['state'],strict=True);net.eval()
    offset=0;predictions={};timings=[];ranked={}
    for f in inputs['frames']:
        n=len(f['candidates']);frame=torch.from_numpy(x[offset:offset+n]);offset+=n
        begin=time.perf_counter()
        with torch.inference_mode():scores=net(frame).flatten().numpy()
        timings.append(time.perf_counter()-begin)
        predictions[f['id']]=r.choose(f['candidates'],scores)
        ranked[f['id']]=sorted([dict(candidate=c,score=float(s)) for c,s in zip(f['candidates'],scores)],
            key=lambda v:(-v['score'],v['candidate']['id']))
        # Reordering inference candidates cannot change the result, including ties.
        r.d.h.require(r.choose(f['candidates'][::-1],scores[::-1])==predictions[f['id']],'ranking_order_dependence')
    by_pair={p['id']:p for p in inputs['pairs']}
    r.d.h.require(len(result['results'])==len(by_pair),'ranking_result_membership')
    for row in result['results']:
        r.d.h.require(row['selected']==[predictions[k] for k in by_pair[row['id']]['frames']], 'ranking_checkpoint_replay')
    # Only after prediction, read supervision to diagnose rank positions.
    labels=r.sealed(r.d.h.checked(r.d.h.ROOT,doc['supervision']),'transition-candidate-supervision-v1')['labels']
    diagnostics=[]
    for label in labels:
        ordered=ranked[label['frameID']]
        diagnostics.append(dict(pairID=label['pairID'],endpoint=label['endpoint'],split=label['split'],
            bestPositiveRank=min(i+1 for i,v in enumerate(ordered) if v['candidate']['id'] in label['positiveIDs']),
            selected=ordered[0],positiveScores=[v for v in ordered if v['candidate']['id'] in label['positiveIDs']]))
    evidence=dict(version='rank75-replay-v1',result=r.d.h.ref(r.d.h.local(result_path)),
        verifier=r.d.h.ref(r.d.h.ROOT/'scripts/verify_rank75.py'),model=result['model'],
        checkpointReplay=True,candidateOrderParity=True,diagnostics=diagnostics,
        frameRankingColdSeconds=timings[0],frameRankingWarmMedianSeconds=float(np.median(timings[1:])),
        frameRankingWarmP95Seconds=float(np.percentile(timings[1:],95)),
        latencyScope='Resident CPU ranker only; excludes proposal generation, crop, encoding, DTM013 change inference and application routing.',
        elapsedSeconds=time.monotonic()-start,releaseEligible=False)
    if doc.get('reference'):
        reference=r.sealed(r.d.h.checked(r.d.h.ROOT,doc['reference']),'native-ranking-reference-v1')
        r.d.h.require(reference['inputs']==manifest['inputs'],'ranking_comparison_inputs')
        r.d.h.checked(r.d.h.ROOT,reference['model'])
        previous={v['id']:v for v in reference['results']}
        r.d.h.require(set(previous)==set(by_pair),'ranking_comparison_membership')
        comparison={}
        for group in ('originalTrain','addedNativeTrain','exposedSettings'):
            values=[v for v in result['results'] if
                ('exposedSettings' if v['split']=='development' else
                 'addedNativeTrain' if previous[v['id']]['newNative'] else 'originalTrain')==group]
            comparison[group]=dict(pairs=len(values),
                referenceEndpoints=sum(x>=.5 for v in values for x in previous[v['id']]['boxIoUs']),
                candidateEndpoints=sum(x>=.5 for v in values for x in v['boxIoUs']),
                referencePaired=sum(min(previous[v['id']]['boxIoUs'])>=.5 for v in values),
                candidatePaired=sum(v['bothBoxesCorrect'] for v in values),
                candidateJoint=sum(v['bothBoxesCorrect'] and v['rawChangeCorrect'] for v in values),
                candidateAbstentions=sum(v['decision']=='unknown' for v in values))
        evidence['matchedComparison']=comparison
        evidence['reference']=doc['reference']
    r.d.h.write(r.d.h.fresh(output),evidence,sealed=True)
    print({k:v for k,v in evidence.items() if k not in ('diagnostics','result','verifier','model')})


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--result',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.result,a.output)
