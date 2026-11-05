"""Test detector proposal coverage with unchanged focus weights and independent focus references."""
import copy
import os
import math
import research_queue as q
from template_adapters395 import resolve_inputs, document
from template_inputs398 import checked
from perception_benchmark import _iou

OUT=None


def replace_candidates(plan, predictions):
    result=copy.deepcopy(plan)
    for frame in result['frames']:
        rows=predictions[frame['image']['path']]
        frame['candidates']=[dict(id='r5-'+str(i),bounds=row['box']) for i,row in enumerate(rows) if row['cls']!='text']
    return result


def proposals():
    import roles559_evaluate as e
    os.environ.setdefault('YOLO_CONFIG_DIR',str(q.ROOT/'NativeUITrainer/.ultralytics'))
    os.environ.setdefault('MPLCONFIGDIR',str(q.ROOT/'NativeUITrainer/.mplconfig'))
    os.environ['YOLO_OFFLINE']='true'
    refs=resolve_inputs(q.load(OUT.parents[2]/'spec.json')['template'],OUT)
    plan=document(refs['plan']);model=checked(refs['model'])
    images=[checked(frame['image']) for frame in plan['frames']]
    old=e.SQUARE;e.SQUARE=True
    try: raw=e.predict(model,images,.5)
    finally:e.SQUARE=old
    predictions={q.relative(path):rows for path,rows in raw.items()}
    from PIL import Image
    rejected=[]
    cropped_predictions={}
    for frame in plan['frames']:
        with Image.open(checked(frame['image'])) as image:width,height=image.size
        valid=[]
        for row in predictions[frame['image']['path']]:
            x,y,w,h=row['box']
            q.require(all(math.isfinite(v) for v in (x,y,w,h)) and w>0 and h>0,'invalid_detector_geometry')
            x1,y1,x2,y2=max(0.,x),max(0.,y),min(float(width),x+w),min(float(height),y+h)
            if x2<=x1 or y2<=y1:
                rejected.append(dict(frame=frame['id'],proposal=row,reason='outside_visible_image'));continue
            valid.append(dict(row,box=[x1,y1,x2-x1,y2-y1]))
        cropped_predictions[frame['image']['path']]=valid
    result=replace_candidates(plan,cropped_predictions)
    coverage=[]
    for frame in result['frames']:
        label=document(frame['label'])
        coverage.append(dict(id=frame['id'],covered=any(_iou(c['bounds'],label['focus']['box'])>=.5 for c in frame['candidates'])))
    q.save(OUT/'plan.json',result)
    q.save(OUT/'proposals.json',dict(model=refs['model'],confidence=.5,nmsIoU=.45,square640=True,
         predictions=predictions,rejectedProposals=rejected,geometryPolicy='visible-intersection',coverage=coverage,metricsStatus='provisional',modelAccepted=False))
    receipt(['plan.json','proposals.json'])


def compare_reports(baseline,candidate):
    q.require(baseline['model']==candidate['model'],'focus_weights_changed')
    q.require(baseline['threshold']==candidate['threshold']==.85,'focus_threshold_changed')
    left={r['id']:r for r in baseline['outcomes']};right={r['id']:r for r in candidate['outcomes']}
    q.require(left.keys()==right.keys(),'comparison_membership')
    q.require(baseline['legacyLabels']==candidate['legacyLabels'] and baseline['legacyProbabilities']==candidate['legacyProbabilities'],'legacy_changed')
    q.require({k:v for k,v in baseline['scores'].items() if k.endswith('|truth')}==
              {k:v for k,v in candidate['scores'].items() if k.endswith('|truth')},'reference_crop_or_score_changed')
    gained=[k for k in left if not left[k]['correct'] and right[k]['correct']]
    lost=[k for k in left if left[k]['correct'] and not right[k]['correct']]
    wrong=[k for k in left if not left[k]['wrong'] and right[k]['wrong']]
    outcome='contradicted' if lost or wrong else 'supported' if gained else 'inconclusive'
    return dict(version='proposal-correction564-v1',outcome=outcome,recovered=gained,lost=lost,newWrong=wrong,
                baseline=baseline['development'],candidate=candidate['development'],metricsStatus='provisional',modelAccepted=False,
                nextAction='If coverage is adequate but selections still fail, diagnose focus feature discrimination. Never tune thresholds on these frames.',
                limitation='Retained-proposal diagnostic with PyTorch R5; not full-screen TTR acceptance or independent qualification.')


def compare():
    refs=resolve_inputs(q.load(OUT.parents[2]/'spec.json')['template'],OUT)
    result=compare_reports(document(refs['baseline']),document(refs['candidate']))
    q.save(OUT/'benchmark_summary.json',result);receipt(['benchmark_summary.json'])


def receipt(names):
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path=n,sha256=q.digest(OUT/n)) for n in names]))
