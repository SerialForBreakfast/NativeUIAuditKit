"""Frozen ranking/change diagnostics; no training or threshold selection."""
import argparse
import time
import numpy as np
import focus_candidate_ranker as r
import focus_change_adaptation as c


def rank_summary(diagnostics):
    rows=[v for v in diagnostics if v['split']=='development']
    wrong=[v for v in rows if v['bestPositiveRank']>1]
    return dict(endpoints=len(rows),wrong=len(wrong),
        wrongWithPositiveSecond=sum(v['bestPositiveRank']==2 for v in wrong),
        wrongSmallSelection=sum(max(v['selected']['candidate']['bounds'][2:])<100 for v in wrong),
        limitation='Exposed development; size is descriptive, not an exclusion threshold.')


def combine(rows, probabilities, boxes, new_ids):
    r.d.h.require(len(rows)==len(probabilities) and len({v['id'] for v in rows})==len(rows) and
        set(boxes)=={v['id'] for v in rows} and new_ids<=set(boxes),'native88_prediction_membership')
    r.d.h.require(all(np.isfinite(p) and 0<=p<=1 for p in probabilities),'native88_probabilities')
    out=[]
    for row,p in zip(rows,probabilities):
        known=max(float(p),1-float(p))>=r.d.CONFIG['confidence']
        correct=(float(p)>=.5)==row['changed']
        out.append(dict(id=row['id'],group='exposedSettings' if row['split']=='development' else
            'addedNativeTrain' if row['id'] in new_ids else 'originalTrain',
            probability=float(p),correct=correct,abstained=not known,
            joint=bool(known and correct and boxes[row['id']]['bothBoxesCorrect'])))
    summary={}
    for group in ('originalTrain','addedNativeTrain','exposedSettings'):
        vals=[v for v in out if v['group']==group]
        summary[group]=dict(pairs=len(vals),correct=sum(v['correct'] for v in vals),
            abstentions=sum(v['abstained'] for v in vals),joint=sum(v['joint'] for v in vals))
    return out,summary


def run(output):
    start=time.monotonic();h=r.d.h;out=h.fresh(output)
    root=h.ROOT/'reports/work/NATIVE-87'
    corpus=h.read(root/'admitted/corpus.json');rows=r.d.admitted(corpus,h.read(root/'admitted/admission.json'))
    replay=r.sealed(root/'replay.json','rank75-replay-v1')
    ranker=r.sealed(h.checked(h.ROOT,replay['result']),r.VERSION);h.checked(h.ROOT,ranker['model'])
    frozen=r.sealed(h.ROOT/'NativeUITrainer/focus_ring_runs/change80-dtm018/result.json',c.VERSION)
    protocol=h.read(h.checked(h.ROOT,frozen['protocol']))
    prior=h.read(h.checked(h.ROOT,protocol['corpus']));old_rows=r.d.admitted(prior,h.read(h.checked(h.ROOT,protocol['admission'])))
    old_x=np.load(h.checked(h.ROOT,protocol['x']),allow_pickle=False)
    h.require(protocol['rowIDs']==[v['id'] for v in old_rows] and old_x.shape==(49,6,64,96),'native88_old_membership')
    old_by={v['id']:(v,x) for v,x in zip(old_rows,old_x)};encoded=[];new_ids=set()
    for row in rows:
        for ref in row['images']:h.checked(h.ROOT,ref)
        if row['id'] in old_by:
            prior_row,x=old_by[row['id']];h.require(row==prior_row,'native88_old_record_changed')
        else:
            x=r.d.encode(*(r.d.pixels(ref) for ref in row['images']));new_ids.add(row['id'])
        encoded.append(x)
    h.require(len(rows)==73 and len(new_ids)==24,'native88_new_membership')
    torch=r.d.torch_runtime();torch.set_num_threads(2)
    state=torch.load(h.checked(h.ROOT,frozen['model']),map_location='cpu',weights_only=True)
    h.require(state['configuration']==r.d.TEMPORAL_CONFIG and state['adaptation']==c.CONFIG,'native88_model_configuration')
    net=r.d.model(state['configuration']);net.load_state_dict(state['state'],strict=True);net.eval()
    tx=torch.from_numpy(np.stack(encoded))
    before=time.monotonic()
    with torch.inference_mode():probabilities=net.change((tx[:,3:]-tx[:,:3]).abs()).sigmoid().flatten().numpy()
    seconds=time.monotonic()-before
    expected={v['id']:v['after'] for v in frozen['results']}
    h.require(all(abs(float(p)-expected[row['id']])<=1e-6 for row,p in zip(rows,probabilities) if row['id'] in expected),'native88_old_prediction_parity')
    boxes={v['id']:v for v in ranker['results']};h.require(set(boxes)=={v['id'] for v in rows},'native88_rank_membership')
    values,summary=combine(rows,probabilities,boxes,new_ids)
    report=dict(version='native88-frozen-diagnostic-v1',**h.FLAGS,changeModel=frozen['model'],rankModel=ranker['model'],
        corpus=h.ref(root/'admitted/corpus.json'),replay=h.ref(root/'replay.json'),
        ranking=rank_summary(replay['diagnostics']),summary=summary,results=values,
        oldPredictionParity=True,reusedEncodings=49,newEncodings=24,
        changeInferenceSeconds=seconds,elapsedSeconds=time.monotonic()-start,trainingLaunched=False,
        limitation='Frozen DTM018+DTM020 diagnostic composition, not the primary DTM020 control or independent evaluation.')
    h.checked(h.ROOT,frozen['model']);h.checked(h.ROOT,ranker['model'])
    out.mkdir(parents=True);h.write(out/'diagnostic.json',report,sealed=True)
    print(report['ranking']);print(summary);print('seconds',report['elapsedSeconds'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    run(p.parse_args().output)
