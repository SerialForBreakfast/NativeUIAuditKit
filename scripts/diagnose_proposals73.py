"""Retained prediction/candidate coverage audit; no model execution or source edits."""
import argparse
import math
from collections import Counter
import human_annotation_review as h
import focus_direct_transition as d
import focus_recorded_semantics as semantic
from focus_recorded_transition_eval import iou


def valid(box):
    return isinstance(box,(list,tuple)) and len(box)==4 and all(type(v) in (int,float) and math.isfinite(v) for v in box) and box[0]>=0 and box[1]>=0 and box[2]>0 and box[3]>0


def select(prediction,candidates,method):
    """Geometry-only input. No focus state/label is accepted by this interface."""
    h.require(method in ('center','iou'),'selection_method')
    h.require(all(set(c)=={'id','bounds'} and valid(c['bounds']) for c in candidates),'candidate_geometry_only')
    h.require(len({c['id'] for c in candidates})==len(candidates),'duplicate_candidate')
    if prediction is None or not candidates:return None
    h.require(valid(prediction),'invalid_prediction')
    def cost(c):
        b=c['bounds']
        return (-iou(prediction,b) if method=='iou' else
            (prediction[0]+prediction[2]/2-b[0]-b[2]/2)**2+(prediction[1]+prediction[3]/2-b[1]-b[3]/2)**2,c['id'])
    return min(candidates,key=cost)


def vision_candidates(record,ref,size):
    h.require(record is not None and record['sha256']==ref['sha256'] and not record['errors'] and
        [record['width'],record['height']]==size,'vision_frame_binding')
    rectangles=record['rectangles'];h.require(len(rectangles)<=40,'vision_count')
    h.require(all(valid(r['bounds']) and r['bounds'][0]+r['bounds'][2]<=size[0] and
        r['bounds'][1]+r['bounds'][3]<=size[1] and type(r['confidence']) in (int,float) and
        0<=r['confidence']<=1 for r in rectangles),'invalid_vision_rectangle')
    return [dict(id=str(i),bounds=r['bounds']) for i,r in enumerate(rectangles)]


def run(output):
    out=h.fresh(output)
    corpus_path=h.ROOT/'reports/work/GENERALIZATION-65/admission/corpus.json'
    corpus=h.read(corpus_path);h.require(corpus['corpusSHA256']==h.digest({k:v for k,v in corpus.items() if k!='corpusSHA256'}),'corpus_hash')
    admission=h.read(h.ROOT/'reports/work/GENERALIZATION-65/admission/admission.json')
    rows=[r for r in d.admitted(corpus,admission) if r['split']=='development'];h.require(len(rows)==5,'development_membership')
    settings=h.read(h.checked(h.ROOT,corpus['sources']['settings']))
    comparison=h.read(h.checked(h.ROOT,settings['baseline']));semref=comparison['semantics']
    sem=h.sealed(h.checked(h.ROOT,semref),'focus-recorded-semantics-v1')
    args={k:str(h.checked(h.ROOT,v)) for k,v in sem['inputs'].items() if k!='events'}
    _,truth,_,_=semantic.inputs(**args)
    native=h.read(h.checked(h.ROOT,sem['raw']))
    vision={r['sha256']:r for r in native['results']}
    h.require(len(vision)==len(native['results']),'duplicate_vision_frame')
    proposals={}
    for name in ('batch','pending'):
        batch=h.validate_batch(h.checked(h.ROOT,sem['inputs'][name]))
        for frame in batch['frames']:
            key=frame['image']['sha256'];pool=frame['proposals']
            if key in proposals:h.require(proposals[key]==pool,'conflicting_proposal_pool')
            proposals[key]=pool
    result_path=h.ROOT/'reports/work/COVERAGE-70/comparison.json'
    report=h.sealed(result_path,'data67-batched-comparison-v1')
    h.require(report['corpusSHA256']==corpus['corpusSHA256'],'prediction_corpus')
    for ref in report['models'].values():h.checked(h.ROOT,ref)
    scores=[r for r in report['results'] if r['condition']=='baseline' and r['group']=='development']
    h.require(len(scores)==len(rows)*len(report['models']) and
        {(r['model'],r['id']) for r in scores}=={(m,r['id']) for m in report['models'] for r in rows},'prediction_membership')
    by_id={r['id']:r for r in rows};details=[];coverage=[]
    for row in rows:
        for endpoint,ref,box in zip(('before','after'),row['images'],row['boxes']):
            h.checked(h.ROOT,ref);frame=truth[ref['sha256']]
            focused=[c for c in frame['controls'] if c['state']=='focused']
            h.require(len(focused)==1 and focused[0]['bounds']==box,'truth_binding')
            pool=proposals.get(ref['sha256'])
            vr=vision.get(ref['sha256'])
            rectangles=vision_candidates(vr,ref,row['size'])
            # Saved proposal schemas are not assumed interchangeable with model detections.
            h.require(pool is None or pool==[],'unreviewed_nonempty_proposal_schema')
            coverage.append(dict(id=row['id'],endpoint=endpoint,image=ref,reviewedControls=len(frame['controls']),
                proposalState='missing' if pool is None else 'empty',proposalCount=None if pool is None else 0,
                measuredDetectorRecall=None,source='original saved annotation proposals; detector execution not established',
                retainedVisionRectangleCount=len(rectangles),visionBestFocusIoU=max((iou(r['bounds'],box) for r in rectangles),default=0)))
    for score in scores:
        row=by_id[score['id']]
        for endpoint,ref,box,prediction in zip(('before','after'),row['images'],row['boxes'],score['prediction']['boxes']):
            candidates=[dict(id=c['id'],bounds=c['bounds']) for c in truth[ref['sha256']]['controls']]
            selected={method:select(prediction,candidates,method) for method in ('center','iou')}
            actual=vision_candidates(vision[ref['sha256']],ref,row['size'])
            automatic={method:select(prediction,actual,method) for method in ('center','iou')}
            details.append(dict(id=row['id'],model=score['model'],endpoint=endpoint,predictedBox=prediction,
                rawCorrect=prediction is not None and iou(prediction,box)>=.5,
                oraclePoolCount=len(candidates),selected=selected,
                oraclePoolCorrect={k:v is not None and iou(v['bounds'],box)>=.5 for k,v in selected.items()},
                visionPoolCorrect={k:v is not None and iou(v['bounds'],box)>=.5 for k,v in automatic.items()}))
    summaries={}
    for model in report['models']:
        ms=[r for r in details if r['model']==model]
        summaries[model]=dict(endpoints=len(ms),invalid=sum(r['predictedBox'] is None for r in ms),
            rawCorrect=sum(r['rawCorrect'] for r in ms),
            oraclePoolEndpoints={k:sum(r['oraclePoolCorrect'][k] for r in ms) for k in ('center','iou')},
            visionPoolEndpoints={k:sum(r['visionPoolCorrect'][k] for r in ms) for k in ('center','iou')},
            visionPoolPairs={k:sum(all(r['visionPoolCorrect'][k] for r in ms if r['id']==row['id']) for row in rows) for k in ('center','iou')},
            oraclePoolPairs={k:sum(all(r['oraclePoolCorrect'][k] for r in ms if r['id']==row['id']) for row in rows) for k in ('center','iou')})
    doc=dict(version='proposal73-diagnostic-v1',**h.FLAGS,corpus=h.ref(corpus_path),semantics=semref,
        predictions=h.ref(result_path),models=report['models'],coverage=coverage,
        coverageStates=dict(Counter(r['proposalState'] for r in coverage)),details=details,summary=summaries,
        uniqueImages=len({r['image']['sha256'] for r in coverage}),
        visionSource=sem['raw'],visionFocusBoxRecallAtHalfIoU=sum(r['visionBestFocusIoU']>=.5 for r in coverage),
        limitation='Human geometry is an oracle pool, not an automatic proposal source. Exposed development data only. No classifier trained or detector run.',
        implementation=h.ref(h.ROOT/'scripts/diagnose_proposals73.py'))
    out.parent.mkdir(parents=True,exist_ok=True);h.write(out,doc,sealed=True)
    print(doc['coverageStates'],summaries);return doc


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    run(p.parse_args().output)
