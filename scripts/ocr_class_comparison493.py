"""Compare a frozen text rule with retained detections. Never change production classes."""
import hashlib
import json
import math
import subprocess
import time
from collections import defaultdict
from pathlib import Path
import research_queue as q
from experiment_templates import checked, pin
import detector_case_match411 as match
from detector_native_inference import validate

OUT = None
VERSION = 'ocr-class-comparison-v1'


def text_for(box, regions):
    """Use one sufficiently confident overlapping text region; ambiguity keeps the baseline."""
    values = []
    for r in regions:
        if r['confidence'] >= .8 and match.iou(box, r['xyxy']) >= .1:
            values.append(' '.join(r['text'].casefold().split()))
    return values[0] if len(values) == 1 and values[0] else None


def validate_ocr(doc, frame):
    q.require(doc.get('version') == 'vision-ocr-regions-v1' and
              doc.get('coordinates') == 'top-left-pixel-xyxy', 'ocr_schema')
    q.require((doc['width'], doc['height']) == (frame['width'], frame['height']), 'ocr_dimensions')
    q.require(isinstance(doc['regions'], list) and len(doc['regions']) <= 4096, 'ocr_count')
    for row in doc['regions']:
        box = row['xyxy']
        q.require(isinstance(row['text'], str) and len(row['text']) <= 8192, 'ocr_text')
        q.require(len(box) == 4 and all(math.isfinite(x) for x in box) and
                  0 <= box[0] < box[2] <= frame['width'] and
                  0 <= box[1] < box[3] <= frame['height'], 'ocr_geometry')
        q.require(math.isfinite(row['confidence']) and 0 <= row['confidence'] <= 1, 'ocr_confidence')
    return doc['regions']


def split(frames):
    groups = sorted({r['group'] for r in frames}, key=lambda s: hashlib.sha256(s.encode()).hexdigest())
    q.require(len(groups) >= 4, 'ocr_group_support')
    fit = set(groups[:len(groups)//2])
    # Pixel duplicates cannot cross the fixed group boundary.
    a = {r['sha256'] for r in frames if r['group'] in fit}
    b = {r['sha256'] for r in frames if r['group'] not in fit}
    q.require(not a & b, 'ocr_split_overlap')
    return fit


def geometry(box, regions):
    token = text_for(box, regions)
    if token is None: return None
    r = next(r for r in regions if r['confidence'] >= .8 and match.iou(box, r['xyxy']) >= .1)
    w,h = box[2]-box[0],box[3]-box[1]
    return [w/h, (r['xyxy'][2]-r['xyxy'][0])/w, (r['xyxy'][3]-r['xyxy'][1])/h]


def compare(frames, predictions, ocr, confidence, mode='text-only'):
    q.require(mode in ('text-only','geometry-envelope'), 'ocr_rule_mode')
    fit_groups = split(frames)
    vocabulary, support = defaultdict(set), defaultdict(set)
    features = defaultdict(list)
    def box(c):
        x,y,w,h = c['bounds']; return [x,y,x+w,y+h]
    for f in frames:
        if f['group'] not in fit_groups: continue
        for c in f['controls']:
            token = text_for(box(c), ocr[f['sha256']])
            if token:
                vocabulary[token].add(c['class']); support[token].add(f['group'])
                features[token].append(geometry(box(c),ocr[f['sha256']]))
    # Fit on development groups only. Never resolve a conflicting token by majority vote.
    rule = {k: next(iter(v)) for k,v in vocabulary.items() if len(v)==1 and len(support[k])>=2}
    envelopes={k:[[min(v)*.8,max(v)*1.2] for v in zip(*features[k])] for k in rule}
    cases=[]; changes=[]; unchanged_text=0; rejected_geometry=0
    for f in frames:
        if f['group'] in fit_groups: continue
        labels=[(c['class'],box(c)) for c in f['controls']]
        old=[p for p in predictions[f['sha256']] if p[1]>=confidence]; new=[]
        for index,(cls,score,bounds) in enumerate(old):
            token=text_for(bounds,ocr[f['sha256']]); proposed=rule.get(token,cls)
            if mode=='geometry-envelope' and proposed!=cls:
                values=geometry(bounds,ocr[f['sha256']])
                if not all(lo<=v<=hi for v,(lo,hi) in zip(values,envelopes[token])):
                    proposed=cls; rejected_geometry+=1
            if token is None: unchanged_text+=1
            new.append((proposed,score,bounds))
            if proposed!=cls: changes.append(dict(image=f['sha256'],index=index,before=cls,after=proposed))
        _,left=match.match(labels,old,False); _,right=match.match(labels,new,False)
        for c,l,r in zip(f['controls'],left,right):
            cases.append(dict(image=f['sha256'],group=f['group'],control=c['id'],baseline=l['status'],candidate=r['status']))
    gains=[r for r in cases if r['baseline']!='detected' and r['candidate']=='detected']
    losses=[r for r in cases if r['baseline']=='detected' and r['candidate']!='detected']
    wrong=[r for r in cases if r['baseline']!='wrong-class' and r['candidate']=='wrong-class']
    return dict(rule=rule,ruleMode=mode,geometryEnvelopes=envelopes,geometryRejectedChanges=rejected_geometry,
                fitGroups=sorted(fit_groups),evaluationGroups=sorted({f['group'] for f in frames}-fit_groups),
                cases=cases,changes=changes,gains=gains,lostPreviousSuccesses=losses,newWrongClasses=wrong,
                ambiguousOrNoTextPredictions=unchanged_text,modelAccepted=False,productionChanged=False)


def run():
    spec=q.load(OUT.parents[2]/'spec.json'); request=q.load(checked(spec['ocrRequest']))
    q.require(request['version']==VERSION,'ocr_request_version')
    labels=q.load(checked(request['labels'])); frames=validate(labels)
    q.require(labels['platform']=='iOS','ocr_platform')
    card=q.load(checked(request['scorecard']))
    q.require(card['inputs']==request['labels'] and card['partition']=='development','ocr_scorecard_identity')
    q.require(card['frames']==[f['sha256'] for f in frames] and len(card['rawPredictions'])==len(frames),'ocr_membership')
    helper=checked(request['helper']); predictions={}; ocr={}; start=time.monotonic()
    cached={}
    q.require(not(request.get('reuseAttempt') and request.get('retainedAttempt')), 'ocr_cache_conflict')
    if request.get('reuseAttempt') or request.get('retainedAttempt'):
        source=checked(request.get('retainedAttempt') or request['reuseAttempt']); prior=q.load(source)
        q.require(prior['status']==('complete' if request.get('retainedAttempt') else 'failed'),'ocr_reuse_status')
        attempt=source.parent; parent=q.load(attempt.parents[1]/'spec.json')
        q.require(q.text_digest(parent)==prior['specSHA256'],'ocr_reuse_spec')
        original=q.load(checked(parent['ocrRequest']))
        q.require(all(original[k]==request[k] for k in ('labels','scorecard','helper')),'ocr_reuse_identity')
        q.require(q.outputs_intact(attempt,prior),'ocr_reuse_outputs')
        output_names={r['path'] for r in prior['outputs']}
        for i,f in enumerate(frames):
            name='ocr-%03d.json'%i
            if name in output_names:
                cached[f['sha256']]=q.load(attempt/'out'/name)
    for index,(f,ref) in enumerate(zip(frames,card['rawPredictions'])):
        raw=q.load(checked(ref)); q.require(raw['inputSHA256']==f['sha256'],'ocr_pixel_identity')
        q.require('boundingBoxPixels: pixels top-left' in raw['coordinates'],'ocr_prediction_coordinates')
        q.require(raw['runtime']['detector']==card['identity']['detector'],'ocr_model_identity')
        found=[]
        for e in raw['runtime']['result']['elements']:
            b=e['boundingBoxPixels']; found.append((e['elementType'],e['confidence'],[b['x'],b['y'],b['x']+b['width'],b['y']+b['height']]))
        predictions[f['sha256']]=found
        if f['sha256'] in cached:
            doc=cached[f['sha256']]
        else:
            q.require(not request.get('retainedAttempt'),'ocr_retained_missing:'+str(index))
            try:
                proc=subprocess.run([str(helper),str(checked(f['image'])),'--json'],capture_output=True,text=True,timeout=60)
            except subprocess.TimeoutExpired as error:
                raise ValueError('ocr_image_timeout:'+str(index)) from error
            q.require(proc.returncode==0,'ocr_process_failed:'+str(index))
            doc=json.loads(proc.stdout)
        ocr[f['sha256']]=validate_ocr(doc,f)
        q.save(OUT/('ocr-%03d.json'%index),doc)
    result=compare(frames,predictions,ocr,card['settings']['confidence'],request.get('ruleMode','text-only'))
    if request.get('ruleMode')=='geometry-envelope':
        text_result=compare(frames,predictions,ocr,card['settings']['confidence'])
        result['textOnlyComparison']={k:text_result[k] for k in ('gains','lostPreviousSuccesses','newWrongClasses','changes')}
    result.update(version=VERSION,seconds=time.monotonic()-start,reusedOCRFrames=len(cached),labelReview=labels['labelReview'],
                  labelsComplete=labels['labelsComplete'],sources=request,
                  limitation='Development diagnostic against supplied native annotations. Incomplete labels prevent false-positive or release qualification.')
    result['outcome']='contradicted' if result['lostPreviousSuccesses'] or result['newWrongClasses'] else 'inconclusive'
    if result['gains'] and not result['lostPreviousSuccesses'] and not result['newWrongClasses']:
        result['outcome']='supported-on-supplied-labels'
    q.save(OUT/'comparison.json',result)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path='comparison.json',sha256=q.digest(OUT/'comparison.json'))]))


def build(request_path, ident):
    request=q.load(request_path); labels=q.load(checked(request['labels'])); validate(labels); split(labels['frames'])
    card=q.load(checked(request['scorecard']))
    refs=[pin(request_path),request['labels'],request['scorecard'],request['helper']]+card['rawPredictions']+[f['image'] for f in labels['frames']]
    if request.get('reuseAttempt'): refs.append(request['reuseAttempt'])
    if request.get('retainedAttempt'): refs.append(request['retainedAttempt'])
    spec=dict(version='research-spec-v2',id=ident,task='ADRSPIKES493-05',owner='Maximum-mini-NUIAK',kind='screen',
        authority='diagnostic',jobKind='artifact',question='Can a disjoint-group OCR vocabulary recover localized iOS class errors without losing supplied-label successes?',
        hypothesis='Unambiguous text shared across development groups can correct some retained class confusions.',
        controlledComparison='Keep detector scores, boxes, images, labels and threshold fixed. Change only the text-based class rule.',
        decisionRule='Reject losses or new wrong classes. Treat sparse vocabulary as inconclusive. Never promote from partial labels.',
        nextActionByOutcome=dict(supported='Review broader label qualification.',contradicted='Reject this rule and preserve losses.',inconclusive='Inspect text ambiguity and missing coverage.'),
        ocrRequest=pin(request_path),inputs=list({r['path']:r for r in refs}.values()),stage=[],dependencies=[],
        adapter=dict(type='python-callable',steps=['ocr_class_comparison493.run'],outputAttributes=['ocr_class_comparison493.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),
        evidence=dict(reads=[request['labels']['path'],request['scorecard']['path']],artifactReceipt='artifact-receipt.json'))
    if request.get('ruleMode')=='geometry-envelope':
        q.require(request.get('retainedAttempt'), 'ocr_geometry_requires_retained')
        spec.update(question='Does control geometry prevent ambiguous OCR class changes on retained iOS outputs?',
            hypothesis='A fitting-group geometry envelope rejects text matches from incompatible control shapes.',
            controlledComparison='Reuse all OCR and detector outputs. Add a 20 percent geometry envelope fitted only on fixed fitting groups.')
    q.validate(spec); return spec


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request',type=Path)
    parser.add_argument('--id',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    q.save(args.output,build(args.request,args.id))
