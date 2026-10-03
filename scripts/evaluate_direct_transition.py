"""Pinned checkpoint reload, fit/transfer diagnosis and bounded latency; no training."""
import argparse
import statistics
import time
import numpy as np
import focus_direct_transition as d
from focus_recorded_transition_eval import iou


def parity(expected,actual):
    d.h.require(len(expected['boxes'])==len(actual['boxes'])==2,'checkpoint_box_count')
    d.h.require(expected['decision']==actual['decision'] and
        abs(expected['changeProbability']-actual['changeProbability'])<=1e-6,'checkpoint_prediction_changed')
    for a,b in zip(expected['boxes'],actual['boxes']):
        d.h.require((a is None)==(b is None),'checkpoint_box_changed')
        if a is not None:d.h.require(np.allclose(a,b,rtol=0,atol=1e-4),'checkpoint_box_changed')


def localization(predicted,targets,size):
    """Per-endpoint errors in viewport units; invalid predictions remain failures."""
    rows=[]
    for name,p,t in zip(('before','after'),predicted,targets):
        row=dict(endpoint=name,valid=p is not None,iou=iou(p,t) if p else 0)
        if p is not None:
            row['centerError']=[abs(p[k]+p[k+2]/2-t[k]-t[k+2]/2)/size[k] for k in (0,1)]
            row['sizeError']=[abs(p[k+2]-t[k+2])/size[k] for k in (0,1)]
        rows.append(row)
    return rows


def endpoint_summary(rows):
    result={}
    for name in ('before','after'):
        values=[next(v for v in r['localization'] if v['endpoint']==name) for r in rows]
        valid=[v for v in values if v['valid']]
        result[name]=dict(count=len(values),invalid=len(values)-len(valid),
            meanIoU=statistics.mean(v['iou'] for v in values),
            localized=sum(v['iou']>=.5 for v in values),
            meanCenterError=np.mean([v['centerError'] for v in valid],axis=0).tolist() if valid else None,
            meanSizeError=np.mean([v['sizeError'] for v in valid],axis=0).tolist() if valid else None)
    return result


def run(result_path,output):
    path=d.h.local(result_path);out=d.h.fresh(output);result=d.h.read(path)
    d.h.require(result['version']=='focus-direct-result-v1','result_version')
    protocol=d.h.read(d.h.checked(d.h.ROOT,result['protocol']))
    d.h.require(protocol['pins']==d.pins(),'direct_dependency_or_code_changed')
    corpus=d.collect(protocol['sources']);d.h.require(corpus['corpusSHA256']==protocol['corpusSHA256'],'corpus_changed')
    rows=d.admitted(corpus,d.h.read(d.h.checked(d.h.ROOT,protocol['admission'])))
    expected={r['id']:r for r in result['results']}
    d.h.require(set(expected)=={r['id'] for r in rows if r['split']=='development'},'development_membership_changed')
    start=time.monotonic();torch=d.torch_runtime();torch.set_num_threads(2)
    checkpoint=d.h.checked(d.h.ROOT,result['model']);state=torch.load(checkpoint,map_location='cpu',weights_only=True)
    d.h.require(state['version']==d.VERSION and d.valid_configuration(state['configuration']) and
                state['configuration']==protocol['configuration'],'checkpoint_contract')
    net=d.model();net.load_state_dict(state['state'],strict=True);net.eval();load_seconds=time.monotonic()-start
    scores=[];first=None;warm=[]
    for r in rows:
        before,after=[d.pixels(i) for i in r['images']]
        p=d.infer(net,before,after)
        if first is None:first=p['elapsedSeconds']
        if r['split']=='development':
            parity(expected[r['id']]['prediction'],p)
            for _ in range(4):warm.append(d.infer(net,before,after)['elapsedSeconds'])
        overlaps=[iou(box,target) if box else 0 for box,target in zip(p['boxes'],r['boxes'])]
        scores.append(dict(id=r['id'],split=r['split'],prediction=p,expectedChange=r['changed'],boxIoUs=overlaps,
            localization=localization(p['boxes'],r['boxes'],r['size']),
            rawChangeCorrect=(p['changeProbability']>=.5)==r['changed'],bothBoxesCorrect=min(overlaps)>=.5,baseline=r['baseline']))
    report=dict(version='direct-checkpoint-evaluation-v1',**d.h.FLAGS,source=d.h.ref(path),model=result['model'],
        summary={split:d.summarize([r for r in scores if r['split']==split]) for split in ('train','development')},
        results=scores,checkpointParityPassed=True,
        localization={split:endpoint_summary([r for r in scores if r['split']==split]) for split in ('train','development')},
        timing=dict(loadSeconds=load_seconds,firstPairSeconds=first,warmSamples=len(warm),
            warmMedianSeconds=statistics.median(warm),warmP95Seconds=float(np.quantile(warm,.95)),
            scope='CPU2threads, resize+forward+decode boxes; PNG loading excluded; first pair not process cold startup'),
        outputBytes=sum(p.stat().st_size for p in checkpoint.parent.iterdir()),
        implementation=d.h.ref(d.h.ROOT/'scripts/evaluate_direct_transition.py'))
    d.h.checked(d.h.ROOT,result['model']);d.h.checked(d.h.ROOT,result['protocol'])
    d.h.write(out,report,sealed=True);print(report['summary']);print(report['timing']);return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--result',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.result,a.output)
