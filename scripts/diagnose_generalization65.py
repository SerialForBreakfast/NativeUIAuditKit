"""Frozen unseen-shift and zero-difference probes; not genuine action evidence."""
import argparse
from collections import Counter
import time
import focus_direct_transition as d
from focus_pair_translation import translate
from evaluate_direct_transition import parity
from focus_recorded_transition_eval import iou

MODELS={'fit61-dtm009':'FIT-61','robustness63-dtm010':'ROBUSTNESS-63','exposure64-dtm011':'EXPOSURE-64'}


def conditions():
    result=[('baseline',0,0)]
    for magnitude in (.02,.06):
        for name,x,y in (('left',-1,0),('right',1,0),('up',0,-1),('down',0,1)):
            result.append((f'{name}-{int(magnitude*100)}pct',x*magnitude,y*magnitude))
    for x in (-1,1):
        for y in (-1,1):result.append((f'diagonal-{x}-{y}',x*.04,y*.04))
    return result


def counterfactual_summary(rows):
    return dict(pairs=len(rows),decisions=dict(Counter(r['prediction']['decision'] for r in rows)),
        rawChangePredictions=sum(r['prediction']['changeProbability']>=.5 for r in rows),
        boxConsistencyAtHalfIoU=sum(r['predictedBoxOverlap']>=.5 for r in rows),
        semanticAccuracy=None)


def run(output):
    out=d.h.fresh(output);start=time.monotonic()
    protocol=d.h.read(d.h.ROOT/'reports/work/EXPOSURE-64/ready/protocol.json')
    corpus=d.collect(protocol['sources']);d.h.require(corpus['corpusSHA256']==protocol['corpusSHA256'],'corpus_changed')
    rows=d.admitted(corpus,d.h.read(d.h.checked(d.h.ROOT,protocol['admission'])))
    d.h.require(len(rows)==29,'probe_membership')
    torch=d.torch_runtime();torch.set_num_threads(2);models={};sources=[]
    for name,packet in MODELS.items():
        evaluation=d.h.sealed(d.h.ROOT/f'reports/work/{packet}/evaluation.json','direct-checkpoint-evaluation-v1')
        result=d.h.read(d.h.checked(d.h.ROOT,evaluation['source']))
        d.h.require(evaluation['model']==result['model'],'model_binding')
        state=torch.load(d.h.checked(d.h.ROOT,result['model']),map_location='cpu',weights_only=True)
        d.h.require(state['version']==d.VERSION and state['configuration'] in (d.FULL_FIT_CONFIG,*d.TRANSLATION_CONFIGURATIONS),'model_configuration')
        net=d.model(state['configuration']);net.load_state_dict(state['state'],strict=True);net.eval()
        expected={r['id']:r for r in evaluation['results']}
        d.h.require(set(expected)=={r['id'] for r in rows},'baseline_membership')
        models[name]=(net,expected);sources.append(dict(name=name,model=result['model'],evaluation=d.h.ref(d.h.ROOT/f'reports/work/{packet}/evaluation.json')))
    scores=[];counterfactuals=[];rejected=[]
    for row in rows:
        images=[d.pixels(ref) for ref in row['images']]
        for condition,x,y in conditions():
            dx,dy=round(images[0].width*x),round(images[0].height*y)
            pair,truth=translate(images,row['boxes'],dx,dy)
            if pair is None:
                rejected.append(dict(id=row['id'],split=row['split'],condition=condition,reason='target_outside_frame'));continue
            for name,(net,expected) in models.items():
                p=d.infer(net,*pair)
                if condition=='baseline':parity(expected[row['id']]['prediction'],p)
                overlaps=[iou(b,t) if b else 0 for b,t in zip(p['boxes'],truth)]
                scores.append(dict(id=row['id'],split=row['split'],model=name,condition=condition,translationPixels=[dx,dy],
                    prediction=p,boxIoUs=overlaps,bothBoxesCorrect=min(overlaps)>=.5,expectedChange=row['changed'],
                    rawChangeCorrect=(p['changeProbability']>=.5)==row['changed'],baseline=None))
        for endpoint,image in zip(('before','after'),images):
            for name,(net,_) in models.items():
                p=d.infer(net,image,image);a,b=p['boxes']
                counterfactuals.append(dict(id=row['id'],split=row['split'],model=name,duplicatedEndpoint=endpoint,
                    prediction=p,predictedBoxOverlap=iou(a,b) if a and b else 0,synthetic=True,
                    semanticLabel=None,zeroVisualDifference=True))
    summaries=[]
    for name in models:
        for split in ('train','development'):
            summary={c:d.summarize([r for r in scores if r['model']==name and r['split']==split and r['condition']==c])
                for c,_,_ in conditions()}
            summaries.append(dict(model=name,split=split,conditions=summary,
                counterfactual=counterfactual_summary([r for r in counterfactuals if r['model']==name and r['split']==split])))
    d.h.require(len(scores)<=1131 and len(counterfactuals)==174,'probe_budget')
    for source in sources:d.h.checked(d.h.ROOT,source['model'])
    report=dict(version='generalization65-probes-v1',**d.h.FLAGS,sources=sources,corpusSHA256=corpus['corpusSHA256'],
        results=scores,counterfactuals=counterfactuals,rejected=rejected,summary=summaries,
        baselineParityPassed=True,elapsedSeconds=time.monotonic()-start,
        implementation=[d.h.ref(d.h.ROOT/'scripts'/s) for s in ('diagnose_generalization65.py','focus_pair_translation.py','focus_direct_transition.py','focus_spatial_transition.py')],
        limitations=['Unseen transforms of seen scenes, not independent evaluation.',
            'Duplicated inputs are synthetic zero-visual-difference probes, not genuine no-op action labels.',
            'Black fill introduces domain changes; no causal proof or threshold/model selection.'])
    out.parent.mkdir(parents=True,exist_ok=True);d.h.write(out,report,sealed=True)
    print('shift evaluations',len(scores),'rejected',len(rejected),'counterfactuals',len(counterfactuals))
    for summary in summaries:print(summary['model'],summary['split'],summary['counterfactual'])
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    run(p.parse_args().output)
