"""Fixed existing raster proposer comparison; no truth enters proposal generation."""
import argparse
import time
from PIL import Image
import focus_direct_transition as d
from prepare_proposal74 import load_inputs,targets
from human_auto_boxes import detect
from compare_annotation_proposals import validate_boxes


def publish_union(comparison,output):
    path=d.h.local(comparison);report=d.h.sealed(path,'proposal74-source-comparison-v1')
    base=load_inputs(d.h.checked(d.h.ROOT,report['inputs']));old=d.h.read(d.h.checked(d.h.ROOT,report['supervision']))
    d.h.require(set(report['pools'])=={f['id'] for f in base['frames']},'union_frame_membership')
    out=d.h.fresh(output);out.mkdir(parents=True)
    frames=[dict(f,candidates=report['pools'][f['id']]['union'],source='automatic-Vision-plus-raster') for f in base['frames']]
    inputs=dict(version='transition-candidate-inputs-v2',frames=frames,pairs=base['pairs'],
        sourceKind='automatic-Vision-plus-raster',sourceComparison=d.h.ref(path),executionAuthorized=False)
    d.h.write(out/'inputs.json',inputs,sealed=True);load_inputs(out/'inputs.json')
    labels=[dict(pairID=r['pairID'],endpoint=r['endpoint'],frameID=r['frameID'],split=r['split'],**r['results']['union']) for r in report['results']]
    d.h.require({(r['pairID'],r['endpoint']) for r in labels}=={(r['pairID'],r['endpoint']) for r in old['labels']} and len(labels)==len(old['labels']),'union_label_membership')
    d.h.write(out/'supervision.json',dict(version='transition-candidate-supervision-v1',inputs=d.h.ref(out/'inputs.json'),
        corpus=old['corpus'],admission=old['admission'],labels=labels,trainingLaunched=False),sealed=True)
    print('union bank',len(frames),'frames',len(labels),'endpoint labels; training not launched')


def run(bank,output,reuse_training=None):
    out=d.h.fresh(output);start=time.monotonic();bank=d.h.local(bank)
    inputs=load_inputs(bank/'inputs.json');supervision=d.h.read(bank/'supervision.json')
    corpus=d.h.read(d.h.checked(d.h.ROOT,supervision['corpus']))
    truth={(r['id'],k):box for r in corpus['records'] for k,box in zip(('before','after'),r['boxes'])}
    pools={};times=[];reused=None
    if reuse_training:
        reused=d.h.ref(d.h.local(reuse_training));old=d.h.sealed(d.h.checked(d.h.ROOT,reused),'proposal74-source-comparison-v1')
        d.h.require(old['inputs']==d.h.ref(bank/'inputs.json') and old['supervision']==d.h.ref(bank/'supervision.json'),'reuse_bank_binding')
        d.h.require(old['implementation'][0]==d.h.ref(d.h.ROOT/'scripts/human_auto_boxes.py'),'raster_implementation_changed')
        d.h.require(set(old['pools'])=={f['id'] for f in inputs['frames'] if f['split']=='train'},'reuse_training_membership')
        pools.update(old['pools'])
    for frame in inputs['frames']:
        if frame['id'] in pools:continue
        before=time.monotonic()
        with Image.open(d.h.checked(d.h.ROOT,frame['image'])) as image:
            corners=detect(image)  # no existing boxes or focus labels
        boxes=[[x,y,r-x,b-y] for (x,y),(r,b) in corners];validate_boxes(boxes,*frame['size'])
        raster=[dict(id=f'raster-{i}',bounds=b) for i,b in enumerate(boxes)]
        vision=[dict(id='vision-'+c['id'],bounds=c['bounds']) for c in frame['candidates']]
        pools[frame['id']]=dict(vision=vision,raster=raster,union=vision+raster)
        times.append(time.monotonic()-before)
    scores=[]
    for label in supervision['labels']:
        box=truth[label['pairID'],label['endpoint']]
        scores.append(dict(pairID=label['pairID'],endpoint=label['endpoint'],frameID=label['frameID'],split=label['split'],
            results={method:targets(pool,box) for method,pool in pools[label['frameID']].items()}))
    summary={split:{method:dict(endpoints=len(items),covered=sum(not r['results'][method]['missingPositive'] for r in items),
        ambiguous=sum(r['results'][method]['ambiguousPositive'] for r in items)) for method in ('vision','raster','union')}
        for split in ('train','development') for items in ([r for r in scores if r['split']==split],)}
    report=dict(version='proposal74-source-comparison-v1',**d.h.FLAGS,inputs=d.h.ref(bank/'inputs.json'),
        supervision=d.h.ref(bank/'supervision.json'),summary=summary,results=scores,pools=pools,
        uniqueImages=len(pools),newlyProcessedImages=len(times),reusedTraining=reused,proposalSeconds=sum(times),elapsedSeconds=time.monotonic()-start,
        implementation=[d.h.ref(d.h.ROOT/'scripts'/n) for n in ('human_auto_boxes.py','compare_proposal74_sources.py')],
        limitation='Fixed geometry coverage only; union retains overlapping proposals, no semantic precision or focus-ranking claim. No new admission.')
    out.parent.mkdir(parents=True,exist_ok=True);d.h.write(out,report,sealed=True);print(summary);return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bank');p.add_argument('--output',required=True);p.add_argument('--reuse-training');p.add_argument('--publish-union')
    a=p.parse_args()
    if a.publish_union:publish_union(a.publish_union,a.output)
    else:run(a.bank,a.output,a.reuse_training)
