"""Reusable review-only SDK model comparisons. No capture, training, or promotion."""
import base64
import hashlib
import io
from pathlib import Path
from collections import Counter
import research_queue as q
from experiment_templates import checked, pin
from sdk_dataset505 import audit
from sdk_packet502 import review
from sdk_semantics529 import transition
from detector_focus_pilot import merge
from detector_native_inputs import bounds
from native_selection404 import outcome
import detector_inference412 as inference

OUT=None
SUCCESS={'correct','correct-abstention'}

def observed(before,after):
    if before is None:return 'no_focus' if after is None else 'arrival'
    if after is None:return 'departure'
    return 'unchanged' if before==after else 'move'

def packet(path,ident):
    audit(path)
    doc=q.load(path);q.require(len(doc['cases'])==1,'sdk508_packet_cases')
    case=doc['cases'][0];q.require(case['id']==ident and len(case['frames'])==1,'sdk508_packet_identity')
    frame=case['frames'][0];image=path.parent/frame['image'];e=q.load(path.parent/frame['evidence'])
    r=review(e,image);q.require(r['reviewable'],'sdk508_packet_unreviewable')
    controls=[x for x in r['elements'] if x['geometryAvailable'] and x['observedVisibleEnabled']]
    focus=r['reportedFocusID'] if r['focusState']=='focused' else None
    truth=next((x['pixelBounds'] for x in controls if x['identity']['id']==focus),None)
    q.require(focus is None or truth is not None,'sdk508_focus_geometry')
    return dict(id=ident,image=pin(image),sha256=q.digest(image),width=e['width'],height=e['height'],
        group=case['group'],contentGroup=case['contentGroup'],split=case['split'],role=frame['role'],
        sourceID=e['sourceID'],appID=e['before']['appID'],processID=e['before']['processID'],runID=e['before']['runID'],
        profile=case['hcfMode'],focusID=focus,focusState=r['focusState'],truth=truth,controls=controls,trainingEligible=False)

def pair(ref):
    path=checked(ref);d=q.load(path)
    q.require(d['schemaVersion']==1 and d['kind']=='sdk_action_pair' and d['admission']=='review_only','sdk508_pair_contract')
    a=d['action'];q.require(a['receipt']['state']=='delivered','sdk508_action_not_delivered')
    q.require(all(a['request'][k]==a['receipt'][k] for k in ('operationID','simulatorID','sequence')),'sdk508_action_identity')
    keys=('beforeStartedNS','beforeFinishedNS','actionStartedNS','actionFinishedNS','afterStartedNS','afterFinishedNS')
    times=[a['timing'][k] for k in keys]
    q.require(a['timing']['clockID'] and all(type(x)==int and x>=0 for x in times) and times==sorted(times),'sdk508_action_order')
    frames=[]
    for side in ('before','after'):
        p=q.local_path(path.parent,d[side]['packet'])/'manifest.json'
        q.require(q.digest(p)==d[side]['manifestSHA256'],'sdk508_packet_hash')
        f=packet(p,d[side]['caseID']);q.require(f['sourceID']==a['request']['simulatorID'],'sdk508_target')
        frames.append(f)
    q.require(all(frames[0][k]==frames[1][k] for k in ('appID','processID','runID','group','contentGroup','split','profile')),'sdk508_pair_lineage')
    label=observed(frames[0]['focusID'],frames[1]['focusID'])
    q.require(label==d['observed'],'sdk508_observed_mismatch')
    identity=transition(*frames)
    return dict(id=path.parent.name,manifest=ref,expected=d['expected'],observed=identity['observed'],
        producerObserved=label,identityTransition=identity,temporalEligible=identity['eligible'],issues=d['issues'],
        coverage=d['coverage'],frames=frames)

def prepare(request):
    q.require(set(request)=={'version','id','pairs','detectors','crops','tool'},'sdk508_request_fields')
    q.require(request['version']=='sdk-model-campaign-v1' and q.ID.fullmatch(request['id']),'sdk508_request_identity')
    q.require(set(request['detectors'])=={'scoped','general'} and set(request['crops'])=={'hcf','mixed'},'sdk508_model_arms')
    q.require(0<len(request['pairs'])<=6 and len({r['path'] for r in request['pairs']})==len(request['pairs']),'sdk508_pair_membership')
    for ref in [*request['detectors'].values(),*request['crops'].values(),request['tool']]:checked(ref)
    rows=[pair(r) for r in request['pairs']]
    q.require(len({f['id'] for r in rows for f in r['frames']})==2*len(rows),'sdk508_duplicate_frame')
    return rows

def build(path):
    r=q.load(path);prepare(r)
    refs=[pin(path),*r['pairs'],*r['detectors'].values(),*r['crops'].values(),r['tool'],pin(Path(__file__).resolve())]
    return dict(version='research-spec-v2',id=r['id'],task='SDK508',owner='Maximum-mini-NUIAK',kind='screen',
        jobKind='artifact',authority='diagnostic',dependencies=[],inputs=refs,
        adapter=dict(type='python-callable',steps=['sdk_campaign508.run'],outputAttributes=['sdk_campaign508.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),
        evidence=dict(artifactReceipt='artifact-receipt.json',reads=[x['path'] for x in refs[:-1]]),
        question='Do frozen crop models and combined detector proposals preserve native focus and observed no-focus outcomes?',
        hypothesis='Native labels distinguish proposal failures from crop-score errors and false selections.',
        controlledComparison='Identical retained pixels and roles. Fixed 1280 detector input, 0.25 confidence, crop preprocessing, and 0.85 focus threshold.',
        decisionRule='Reject a correction with lost successes or new wrong selections. Report no-focus separately. Unknown HCF mode stays unknown.',
        nextActionByOutcome=dict(supported='Prepare broader independent groups with the same configuration-only pipeline.',
                                 contradicted='Use case-linked proposal and crop errors to choose one correction; preserve models.'))

def fallback(hcf,mixed):
    """Frozen unique-high-score fallback. Both model score vectors remain available."""
    return hcf if sum(s>=.85 for s in hcf)==1 else mixed if sum(s>=.85 for s in mixed)==1 else hcf

def compare(rows):
    comparisons=[]
    for row in rows:
        for model in ('hcf','mixed','fallback'):
            old=row['arms']['scoped']['models'][model]['outcome'];new=row['arms']['union']['models'][model]['outcome']
            comparisons.append(dict(id=row['id'],model=model,noFocus=row['truth'] is None,baseline=old,candidate=new,
                gain=old not in SUCCESS and new in SUCCESS,loss=old in SUCCESS and new not in SUCCESS,
                newWrong=old not in ('wrong','false-selection') and new in ('wrong','false-selection')))
    return comparisons

def run():
    import numpy as np
    import torch
    from PIL import Image
    import focus_runtime
    from train_focus_ring_detector import load_mobilenetv4_conv_small
    spec=q.load(OUT.parents[2]/'spec.json');request=q.load(checked(spec['inputs'][0]));pairs=prepare(request)
    frames=[f for p in pairs for f in p['frames']];unique=list({f['sha256']:f for f in frames}.values())
    torch.set_num_threads(2);inference.OUT=OUT;focus_runtime.TOOL=checked(request['tool'])
    predictions={};models={};raw_files=[]
    for name,ref in request['detectors'].items():
        folder=OUT/name;folder.mkdir();identity=inference.pytorch(checked(ref),unique,.25,1280,folder)
        predictions[name]={}
        for i,f in enumerate(unique):
            p=folder/('%03d.json'%i);d=q.load(p);raw_files.append(p)
            q.require(d['inputSHA256']==f['sha256'] and d['runtime']['detector']==identity,'sdk508_prediction_identity')
            proposals=[];rejected=[]
            for j,e in enumerate(d['runtime']['result']['elements']):
                v=[e['boundingBoxPixels'][k] for k in ('x','y','width','height')]
                try:b=bounds(v,f['width'],f['height'])
                except ValueError:rejected.append(dict(index=j,bounds=v));continue
                proposals.append(dict(box=b,source=name,sourceIndex=j,confidence=e['confidence']))
            predictions[name][f['sha256']]=dict(proposals=proposals,rejected=rejected)
    for name,ref in request['crops'].items():
        model=load_mobilenetv4_conv_small()(pretrained=False,num_classes=1).eval()
        model.load_state_dict(torch.load(checked(ref),map_location='cpu',weights_only=True)['state_dict'],strict=True);models[name]=model
    cache={};results=[]
    for frame in frames:
        scoped=predictions['scoped'][frame['sha256']]['proposals'];general=predictions['general'][frame['sha256']]['proposals']
        union,removed=merge(scoped,general)
        arms=dict(known=[dict(box=e['pixelBounds']) for e in frame['controls']],scoped=merge(scoped,[])[0],general=merge(general,[])[0],union=union)
        output={}
        for name,items in arms.items():
            boxes=[r['box'] for r in items];key=(frame['sha256'],tuple(tuple(b) for b in boxes))
            if key not in cache:
                scores={m:[] for m in models};hashes=[]
                if boxes:
                    req=[dict(id=str(i),path=str(checked(frame['image'])),sha256=frame['sha256'],bounds=b) for i,b in enumerate(boxes)]
                    reply=focus_runtime.invoke(req,image_root=Path('/Volumes/training-drive/data/NUIAK'))
                    arrays=[]
                    for item in reply['results']:
                        raw=base64.b64decode(item['png'],validate=True)
                        with Image.open(io.BytesIO(raw)) as im:
                            q.require(im.size==(256,256),'sdk508_crop_size');arr=np.array(im.convert('RGB'),copy=True)
                        arrays.append(arr);hashes.append(hashlib.sha256(b'(256, 256)\0'+arr.tobytes()).hexdigest())
                    tensor=torch.from_numpy(np.stack(arrays)).permute(0,3,1,2).float()/255
                    with torch.no_grad():scores={m:torch.sigmoid(net(tensor)).reshape(-1).tolist() for m,net in models.items()}
                scores['fallback']=fallback(scores['hcf'],scores['mixed']);cache[key]=(scores,hashes)
            scores,hashes=cache[key]
            output[name]=dict(boxes=boxes,cropRGBSHA256=hashes,models={m:dict(scores=s,outcome=outcome(s,boxes,frame['truth'])) for m,s in scores.items()})
        results.append(dict(**frame,arms=output,unionRemoved=removed))
    comparisons=compare(results)
    counts={arm:{m:dict(Counter(f['arms'][arm]['models'][m]['outcome'] for f in results)) for m in ('hcf','mixed','fallback')} for arm in ('known','scoped','general','union')}
    report=dict(version='sdk-model-comparison-v1',request=pin(checked(spec['inputs'][0])),rows=results,pairs=pairs,counts=counts,
        comparisons=comparisons,modelAccepted=False,trainingEligible=False,
        limitation='PyTorch diagnostic with production Swift crops, not TTR activation or Core ML parity. Registered labels are partial. HCF mode stays unknown. Related endpoints are not independent trials.')
    q.save(OUT/'benchmark_summary.json',report);raw_files.append(OUT/'benchmark_summary.json')
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path=str(p.relative_to(OUT)),sha256=q.digest(p)) for p in raw_files]))
