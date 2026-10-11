"""Compare cached production outputs with saved HCF proposals, not ground truth."""
import argparse
import math
from collections import Counter
from pathlib import Path
import accessibility_review as a
import human_annotation_review as h
import report_hcf333


def iou(x,y):
    for b in (x,y):
        h.require(isinstance(b,dict) and set(b)=={'x','y','width','height'} and
            all(type(v) in (int,float) and math.isfinite(v) for v in b.values()) and
            b['width']>0 and b['height']>0,'invalid_comparison_box')
    area=max(0,min(x['x']+x['width'],y['x']+y['width'])-max(x['x'],y['x']))*max(
        0,min(x['y']+x['height'],y['y']+y['height'])-max(x['y'],y['y']))
    return area/(x['width']*x['height']+y['width']*y['height']-area)


def compare(elements,candidates):
    focused=[e for e in elements if e.get('state',{}).get('isFocused') is True]
    rules=[c['bounds'] for c in candidates]
    overlap=lambda values: max((iou(b,e['boundingBoxPixels']) for b in rules for e in values),default=0)
    nearest=max(elements,key=lambda e:overlap([e])) if rules and elements else None
    decision=('multiple_model_focus' if len(focused)>1 else
              'ambiguous_rules' if len(rules)>1 else
              'agree' if focused and rules and overlap(focused)>=.5 else
              'disagree' if focused and rules else
              'model_only' if focused else 'rule_only' if rules else 'both_abstain')
    return dict(decision=decision,modelFocusCount=len(focused),ruleCount=len(rules),
        bestDetectorOverlap=overlap(elements) if rules else None,
        focusedOverlap=overlap(focused) if rules else None,
        bestRuleMatch=(dict(type=nearest['elementType'],box=nearest['boundingBoxPixels'],
                           state=nearest.get('state',{})) if nearest else None),
        focused=[dict(type=e['elementType'],box=e['boundingBoxPixels'],score=e['state'].get('focusScore')) for e in focused])


def validate_scans(doc,manifest,root):
    h.require(doc.get('schemaVersion')==1 and doc.get('failed')==0 and doc.get('degraded')==0,'scan_health')
    rows=doc.get('results',[])
    h.require(doc.get('count')==len(rows)==len(manifest['frames']),'scan_count')
    by={}
    for row in rows:
        path=Path(row['input']).resolve()
        h.require(path not in by,'duplicate_scan')
        h.require(row.get('configuration')==dict(minConfidence=.25,ocr=False,platform='tvOS',strict=False),
                  'scan_configuration')
        receipt=row['runtime']['result']['focusExecution']
        h.require(receipt.get('backend')=='coreML' and receipt.get('modelScoringComplete') is True and
                  receipt.get('failedPredictions')==0,'focus_execution')
        by[path]=row
    for frame in manifest['frames']:
        path=(root/frame['file']).resolve();h.require(path in by,'missing_scan')
        row=by[path]
        h.require(row.get('inputSHA256')==frame['sha256'] and
                  (row.get('width'),row.get('height'))==(frame['width'],frame['height']),'scan_image_mismatch')
    return by


def run(root,scan):
    root=h.local(root);audit=report_hcf333.run(root);manifest=h.read(root/'manifest.json')
    doc=h.read(h.local(scan));by=validate_scans(doc,manifest,root)
    frames={f['frame']:f for f in manifest['frames']};rows=[]
    for pair in manifest['pairs']:
        side=root/'analysis'/(pair['id']+'.json')
        for role in ('before','after'):
            frame=frames[pair[role]];image=root/frame['file'];r=by[image.resolve()]
            report=a.perception(dict(perceptionReport=h.ref(side),perceptionImage=h.ref(image),perceptionFrameRole=role))
            candidates=[]
            for c in report['focusRules']['candidates']:
                b=c['bounds'];candidates.append(dict(bounds=dict(x=b['x']*frame['width'],y=b['y']*frame['height'],
                    width=b['width']*frame['width'],height=b['height']*frame['height'])))
            result=compare(r['runtime']['result']['elements'],candidates)
            rows.append(dict(frame=frame['frame'],sha256=frame['sha256'],profile=frame['profile'],**result))
    identities={(r['runtime']['detector']['treeSHA256'],r['runtime']['result']['focusExecution']['modelDigest']) for r in doc['results']}
    h.require(len(identities)==1,'changed_model_identity')
    detector,focus=next(iter(identities))
    return dict(version='hcf-model-rule-comparison-v1',scan=h.ref(h.local(scan)),manifest=audit['manifest'],
        sourceDomain='retained_real_app_simulator',role=manifest['role'],ancestry=manifest['ancestry'],
        uniqueImages=audit['uniqueImages'],analysisFrames=len(rows),rows=rows,
        agreementCounts=dict(Counter(r['decision'] for r in rows)),
        detectorHash=detector,focusHash=focus,agreementIoU=.5,agreementIsAccuracy=False,
        independentAccuracy=None,noFocusSpecificity=None,navigationEligible=False,
        timing=[dict(frame=Path(r['input']).name,cache=r['runtime']['cacheState'],totalMs=r['totalMs']) for r in doc['results']])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('input','scan','output'):p.add_argument('--'+name,required=True)
    args=p.parse_args();result=run(args.input,args.scan);h.write(h.local(args.output),result)
    print(result['agreementCounts'])
