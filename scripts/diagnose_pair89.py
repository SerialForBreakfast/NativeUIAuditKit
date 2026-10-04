"""Fixed paired-logit diagnostic; automatic geometry only, no training."""
import argparse
import numpy as np
import focus_candidate_ranker as r
from focus_recorded_transition_eval import iou


def select_pair(current, other, current_scores, other_scores):
    r.d.h.require(len(current)==len(current_scores) and len(other)==len(other_scores),'pair89_score_count')
    r.d.h.require(all(set(c)=={'id','bounds'} for c in current+other),'pair89_truth_input')
    scored=[]
    for c,score in zip(current,current_scores):
        matches=[(iou(c['bounds'],o['bounds']),o,float(s)) for o,s in zip(other,other_scores)]
        matches=[v for v in matches if v[0]>=.5]
        if not matches:continue
        overlap,o,opposite=min(matches,key=lambda v:(-v[0],v[1]['id']))
        scored.append(dict(candidate=c,opposite=o['id'],overlap=overlap,delta=float(score)-opposite))
    return min(scored,key=lambda v:(-v['delta'],v['candidate']['id'])) if scored else None


def run(output):
    h=r.d.h;out=h.fresh(output)
    result=r.sealed(h.ROOT/'NativeUITrainer/focus_ring_runs/native87-dtm020/result.json',r.VERSION)
    doc=h.read(h.checked(h.ROOT,result['protocol']))
    _,inputs,data=r.bank(h.checked(h.ROOT,doc['bank']))
    torch=r.d.torch_runtime();torch.set_num_threads(2)
    state=torch.load(h.checked(h.ROOT,result['model']),map_location='cpu',weights_only=True)
    h.require(state['configuration']==r.ACTION_CONFIG,'pair89_configuration')
    net=r.model(torch,state['configuration']);net.load_state_dict(state['state']);net.eval()
    with torch.inference_mode():scores=net(torch.from_numpy(r.features(data,inputs,state['configuration']))).flatten().numpy()
    by={};offset=0
    for f in inputs['frames']:
        n=len(f['candidates']);by[f['id']]=(f['candidates'],scores[offset:offset+n]);offset+=n
    change=r.sealed(h.ROOT/'reports/work/NATIVE-88/diagnostic-r2/diagnostic.json','native88-frozen-diagnostic-v1')
    h.checked(h.ROOT,change['changeModel']);h.require(change['rankModel']==result['model'],'pair89_rank_binding')
    changes={v['id']:v for v in change['results']}
    labels=r.sealed(h.checked(h.ROOT,doc['supervision']),'transition-candidate-supervision-v1')
    corpus=h.read(h.checked(h.ROOT,labels['corpus']));rows=r.d.admitted(corpus,h.read(h.checked(h.ROOT,labels['admission'])))
    baseline={v['id']:v for v in result['results']};values=[]
    h.require(set(baseline)==set(changes)=={v['id'] for v in rows},'pair89_membership')
    for row in rows:
        c=changes[row['id']];a,b=[by[f['sha256']] for f in row['images']]
        # Predictions use only candidate geometry, frozen scores and predicted change.
        if c['abstained']:picks=[None,None];mode='unknown-change'
        elif c['probability']<.5:picks=baseline[row['id']]['selected'];mode='static-no-change'
        else:
            matched=[select_pair(a[0],b[0],a[1],b[1]),select_pair(b[0],a[0],b[1],a[1])]
            picks=[v['candidate'] if v else None for v in matched];mode='paired-delta'
        overlaps=[iou(p['bounds'],truth) if p else 0 for p,truth in zip(picks,row['boxes'])]
        values.append(dict(id=row['id'],group=c['group'],mode=mode,selected=picks,boxIoUs=overlaps,
            staticIoUs=baseline[row['id']]['boxIoUs'],abstained=any(p is None for p in picks),
            observedScroll=row.get('observedScroll'),both=min(overlaps)>=.5,
            joint=bool(min(overlaps)>=.5 and c['correct'] and not c['abstained'])))
    summary={g:dict(pairs=len(vs),staticEndpoints=sum(x>=.5 for v in vs for x in v['staticIoUs']),
        pairedEndpoints=sum(x>=.5 for v in vs for x in v['boxIoUs']),pairedBoxes=sum(v['both'] for v in vs),
        joint=sum(v['joint'] for v in vs),abstentions=sum(v['abstained'] for v in vs))
        for g in ('originalTrain','addedNativeTrain','exposedSettings') for vs in ([v for v in values if v['group']==g],)}
    out.mkdir(parents=True);h.write(out/'diagnostic.json',dict(version='pair89-frozen-diagnostic-v1',**h.FLAGS,
        rankModel=result['model'],changeModel=change['changeModel'],protocol=result['protocol'],results=values,
        summary=summary,trainingLaunched=False,limitation='Fixed geometry matching can fail under scroll/layout changes; exposed diagnostic, not promotion.'),sealed=True)
    print(summary)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    run(p.parse_args().output)
