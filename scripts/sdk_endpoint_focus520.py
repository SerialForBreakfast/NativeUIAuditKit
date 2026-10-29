"""Compare frozen crop models on verified SDK endpoints without action timing claims."""
import base64
import io
import math
from pathlib import Path
from collections import Counter
import research_queue as q
from experiment_templates import pin, checked
from sdk_campaign508 import packet
from native_selection404 import outcome

OUT = None
SUCCESS = {'correct', 'correct-abstention'}


def episode_frames(request):
    from sdk_episode529 import intake
    q.require(set(request) == {'version','id','episodes','models','tool'}, 'endpoint_episode_fields')
    q.require(q.ID.fullmatch(request['id']) and 0 < len(request['episodes']) <= 8, 'endpoint_episode_scope')
    frames=[]
    for ref in request['episodes']:
        for episode in intake(q.load(checked(ref)))['episodes']:
            for index,f in enumerate(episode['frames']):
                raw=q.load(checked(f['evidence']))
                controls=[]
                for control,element in zip(f['controls'],raw['after']['elements']):
                    state=element.get('observedState') or {}
                    alpha=state.get('effectiveAlpha')
                    # Disabled controls remain scoreable. They do not become known labels.
                    if (control['geometryAvailable'] and element.get('hidden') is False and
                        state.get('source')=='uikit_ancestor_state' and state.get('hidden') is False and
                        type(alpha) in (int,float) and 0 < alpha <= 1):
                        controls.append(dict(control,enabled=element.get('enabled')))
                known=f['frameReviewable']
                truth=next((c['pixelBounds'] for c in controls if c['identity']['id']==f['focusID']),None)
                q.require(not known or f['frameFocusState']=='no_focus' or truth is not None,'endpoint_episode_truth')
                frames.append(dict(id=episode['id']+'-frame-'+str(index),image=f['image'],evidence=f['evidence'],
                    sha256=f['image']['sha256'],width=raw['width'],height=raw['height'],controls=controls,
                    group=episode['group'],contentGroup=episode['group'],split=episode['role'],role='review_only',
                    profile='unknown',truth=truth if known else None,truthKnown=known,
                    nativeFocusState=f['focusState'],focusID=f['focusID'],frameIssues=f['frameIssues'],
                    episodeID=episode['id'],frameIndex=index,trainingEligible=False))
    q.require(0 < len(frames) <= 128 and len({f['id'] for f in frames})==len(frames),'endpoint_episode_membership')
    q.require(set(request['models'])=={'baseline','candidate'},'endpoint_models')
    for ref in [*request['models'].values(),request['tool']]:checked(ref)
    return frames


def frame_outcome(scores, boxes, frame):
    return outcome(scores,boxes,frame['truth']) if frame.get('truthKnown',True) else 'unknown'


def prepare(request):
    if request.get('version') == 'sdk-endpoint-episode-v1':
        return episode_frames(request)
    q.require(set(request)-{'proposals','proposalMode'} == {'version','id','endpoints','models','tool'}, 'endpoint_fields')
    q.require(request['version'] == 'sdk-endpoint-focus-v1' and q.ID.fullmatch(request['id']), 'endpoint_identity')
    q.require(set(request['models']) == {'baseline','candidate'}, 'endpoint_models')
    q.require(0 < len(request['endpoints']) <= 16, 'endpoint_scope')
    frames = []
    for row in request['endpoints']:
        q.require(set(row) == {'manifest','caseID'}, 'endpoint_reference')
        frame=packet(checked(row['manifest']), row['caseID'])
        frame['originalCaseID']=frame['id']
        frame['id'] += '-'+frame['sha256'][:12]
        frames.append(frame)
    q.require(len({f['id'] for f in frames}) == len(frames), 'endpoint_duplicate')
    q.require(len({f['sha256'] for f in frames}) == len(frames), 'endpoint_duplicate_pixels')
    for ref in [*request['models'].values(), request['tool']]: checked(ref)
    q.require('proposalMode' not in request or ('proposals' in request and request['proposalMode']=='resolution-supplement'), 'endpoint_proposal_mode')
    if 'proposals' in request:
        proposal_inputs(request, frames)
    return frames


def proposal_inputs(request, frames):
    from detector_native_inputs import bounds
    arms=request['proposals']
    q.require(set(arms)=={'baseline','candidate'}, 'endpoint_proposal_arms')
    q.require(request['models']['baseline']==request['models']['candidate'], 'endpoint_proposal_crop_changed')
    supplement=request.get('proposalMode')=='resolution-supplement'
    result={}; identity=None
    for name in ('baseline','candidate'):
        arm=arms[name]
        q.require(set(arm)=={'confidence','predictions'}, 'endpoint_proposal_fields')
        q.require(arm['confidence']==(.25 if supplement or name=='baseline' else .10), 'endpoint_proposal_threshold')
        size=960 if supplement and name=='candidate' else 1280
        q.require(len(arm['predictions'])==len(frames), 'endpoint_proposal_membership')
        rows=[]
        for ref,f in zip(arm['predictions'],frames):
            raw=q.load(checked(ref))
            q.require(raw.get('status')=='success' and raw['inputSHA256']==f['sha256'], 'endpoint_proposal_pixels')
            q.require((raw['width'],raw['height'])==(f['width'],f['height']), 'endpoint_proposal_dimensions')
            q.require(raw['coordinates']=='boundingBoxPixels: pixels top-left', 'endpoint_proposal_coordinates')
            q.require(raw['configuration']==dict(imageSize=size,minConfidence=arm['confidence']), 'endpoint_proposal_settings')
            detector=raw['runtime']['detector']
            q.require(detector.get('engine')=='pytorch' and detector.get('imageSize')==size and detector.get('nmsIoU')==.45, 'endpoint_proposal_detector')
            common={k:v for k,v in detector.items() if not(supplement and k=='imageSize')}
            if identity is None:identity=common
            q.require(identity==common, 'endpoint_proposal_detector_changed')
            boxes=[];rejected=[]
            elements=raw['runtime']['result']['elements']
            q.require(len(elements)<=128, 'endpoint_proposal_limit')
            for i,e in enumerate(elements):
                score=e['confidence']
                q.require(type(score) in (float,int) and math.isfinite(score) and arm['confidence']<=score<=1, 'endpoint_proposal_score')
                box=[e['boundingBoxPixels'][k] for k in ('x','y','width','height')]
                try:box=bounds(box,f['width'],f['height'])
                except ValueError:
                    rejected.append(dict(index=i,bounds=box,reason='detector_bounds'));continue
                boxes.append(box)
            rows.append(dict(boxes=boxes,rejected=rejected,source=ref))
        result[name]=rows
    if supplement:
        for old,new in zip(result['baseline'],result['candidate']):
            new['boxes'],new['supplementalCount']=supplement_boxes(old['boxes'],new['boxes'])
    return result


def supplement_boxes(baseline, candidate):
    from detector_focus_pilot import merge
    # Preserve every baseline box and its order. Deduplicate additions only.
    joined,_=merge([dict(box=b,source='baseline') for b in baseline],
                   [dict(box=b,source='supplement') for b in candidate])
    added=[c['box'] for c in joined if c['source']=='supplement']
    q.require(len(baseline)+len(added)<=128,'endpoint_supplement_limit')
    return baseline+added,len(added)


def build(path):
    r = q.load(path); frames=prepare(r)
    refs = [pin(path), *[e['manifest'] for e in r.get('endpoints',[])], *r.get('episodes',[]), *r['models'].values(), r['tool']]
    if 'episodes' in r:
        refs.extend(ref for f in frames for ref in (f['image'],f['evidence']))
    for arm in r.get('proposals',{}).values():refs.extend(arm['predictions'])
    refs=list({ref['path']:ref for ref in refs}.values())
    spec=dict(version='research-spec-v2', id=r['id'], task='SDK520', owner='Maximum-mini-NUIAK', kind='screen',
        jobKind='artifact', authority='diagnostic', dependencies=[], inputs=refs+[pin(Path(__file__).resolve())],
        adapter=dict(type='python-callable', steps=['sdk_endpoint_focus520.run'], outputAttributes=['sdk_endpoint_focus520.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),
        evidence=dict(artifactReceipt='artifact-receipt.json', reads=[p['path'] for p in refs]),
        question=('Do recovered detector proposals improve native focus without losing previous selections?' if 'proposals' in r else 'Does the retained candidate preserve observed endpoint focus and no-focus with identical registered boxes?'),
        hypothesis='Known geometry separates crop-score errors from missing detector proposals.',
        controlledComparison=('Same pixels, crop weights, native truth, and 0.85 focus threshold. Change only detector confidence from 0.25 to 0.10.' if 'proposals' in r else 'Same retained pixels, native observations, production crops and 0.85 threshold. Change only frozen crop weights.'),
        decisionRule='Reject lost successes or new wrong selections. Unknown profile stays unknown. Known boxes are diagnostic only.',
        nextActionByOutcome=dict(supported='Compare independent coverage before adoption.',contradicted='Use case-linked crop failures to choose the next correction.'))
    if r.get('proposalMode')=='resolution-supplement':
        spec.update(question='Do supplemental 960-pixel proposals recover focus without losing 1280-pixel successes?',
            controlledComparison='Same images, crop model, confidence, and threshold. Preserve baseline boxes; add only non-overlapping cached 960-pixel proposals.',
            decisionRule='Reject lost successes or new wrong selections. Retain every baseline box. Do not infer precision from partial labels.')
    return spec


def summarize(rows):
    return dict(rows=rows, gains=[r['id'] for r in rows if r['gain']], losses=[r['id'] for r in rows if r['loss']],
        newWrong=[r['id'] for r in rows if r['newWrong']],
        counts={m:dict(Counter(r['models'][m]['outcome'] for r in rows)) for m in ('baseline','candidate')},
        modelAccepted=False, trainingEligible=False,
        limitation='Known registered boxes only. Unknown profiles remain unknown. No complete-screen, action-timing, motion, or independent-app claim.')


def run():
    import numpy as np
    import torch
    from PIL import Image
    import focus_runtime
    from train_focus_ring_detector import load_mobilenetv4_conv_small
    spec=q.load(OUT.parents[2]/'spec.json');r=q.load(checked(spec['inputs'][0]));frames=prepare(r)
    torch.set_num_threads(2);focus_runtime.TOOL=checked(r['tool']);nets={}
    for name,ref in r['models'].items():
        net=load_mobilenetv4_conv_small()(pretrained=False,num_classes=1).eval()
        net.load_state_dict(torch.load(checked(ref),map_location='cpu',weights_only=True)['state_dict'],strict=True);nets[name]=net
    proposals=proposal_inputs(r,frames) if 'proposals' in r else None
    rows=[]
    for index,f in enumerate(frames):
        known=[e['pixelBounds'] for e in f['controls']];cache={}
        def score_boxes(net,boxes):
            missing=list(dict.fromkeys(tuple(b) for b in boxes if tuple(b) not in cache))
            items=[dict(id=str(i),path=str(checked(f['image'])),sha256=f['sha256'],bounds=list(b)) for i,b in enumerate(missing)]
            for batch in focus_runtime.bounded_batches(items,shared_images=True):
                reply=focus_runtime.invoke(batch,image_root=q.ROOT)
                q.require(len(reply['results'])==len(batch),'endpoint_crop_count')
                for request,item in zip(batch,reply['results']):
                    q.require(item['id']==request['id'],'endpoint_crop_order')
                    with Image.open(io.BytesIO(base64.b64decode(item['png'],validate=True))) as image:
                        q.require(image.size==(256,256),'endpoint_crop_shape');arr=np.array(image.convert('RGB'),copy=True)
                    cache[tuple(request['bounds'])]=(arr,__import__('hashlib').sha256(b'(256, 256)\0'+arr.tobytes()).hexdigest())
            arrays=[cache[tuple(b)][0] for b in boxes];scores=[]
            if arrays:
                tensor=torch.from_numpy(np.stack(arrays)).permute(0,3,1,2).float()/255
                with torch.no_grad():scores=torch.sigmoid(net(tensor)).reshape(-1).tolist()
            return dict(scores=scores,boxes=boxes,cropRGBSHA256=[cache[tuple(b)][1] for b in boxes],outcome=frame_outcome(scores,boxes,f))
        models={name:score_boxes(net,proposals[name][index]['boxes'] if proposals else known) for name,net in nets.items()}
        old,new=models['baseline']['outcome'],models['candidate']['outcome']
        row=dict(id=f['id'],image=f['image'],group=f['group'],contentGroup=f['contentGroup'],split=f['split'],role='review_only',
            profile=f['profile'],noFocus=(f['truth'] is None if f.get('truthKnown',True) else None),boxes=known,cropRGBSHA256=models['baseline']['cropRGBSHA256'],models=models,
            gain=old not in SUCCESS and new in SUCCESS,loss=old in SUCCESS and new not in SUCCESS,
            newWrong=old not in ('wrong','false-selection') and new in ('wrong','false-selection'))
        if 'episodes' in r:
            row.update({key:f[key] for key in ('truthKnown','nativeFocusState','focusID','frameIssues','episodeID','frameIndex','controls','evidence')})
        if proposals:
            row['knownBoxDiagnostic']=score_boxes(nets['baseline'],known)
            row['proposals']={name:proposals[name][index] for name in nets}
        rows.append(row)
    result=dict(version='sdk-endpoint-focus-results-v1',request=pin(checked(spec['inputs'][0])),**summarize(rows))
    if proposals:
        result['comparison']=r.get('proposalMode','detector-confidence')
        result['limitation']='Retained native development frames. Unknown profiles remain unknown. Registered truth is partial; no detector precision or release claim.'
        result['proposalCounts']={name:sum(len(row['models'][name]['boxes']) for row in rows) for name in nets}
    q.save(OUT/'benchmark_summary.json',result)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))


def report_spec(specs, ident):
    q.require(specs and len({s['id'] for s in specs}) == len(specs), 'endpoint_report_membership')
    return dict(version='research-spec-v2',id=ident,task='SDK520',owner='Maximum-mini-NUIAK',kind='screen',jobKind='artifact',authority='diagnostic',
        inputs=[pin(Path(__file__).resolve())],dependencies=[dict(job=s['id'],specSHA256=q.text_digest(s),outputs=['benchmark_summary.json']) for s in specs],
        adapter=dict(type='python-callable',steps=['sdk_endpoint_focus520.report_run'],outputAttributes=['sdk_endpoint_focus520.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),evidence=dict(reads=[],artifactReceipt='artifact-receipt.json'),
        question='Which registered groups expose crop errors or missing proposals?',hypothesis='Separate geometry and focus reports identify different correction needs.',
        controlledComparison='Join pinned completed reports without inference or data-role changes.',
        decisionRule='Keep geometry coverage separate from focus correctness. Preserve every lost success and unknown profile.',
        nextActionByOutcome=dict(supported='Choose a case-linked correction with regression coverage.',contradicted='Preserve models and diagnose failures.'))


def report_run():
    from sdk_diagnostics509 import completed
    spec=q.load(OUT.parents[2]/'spec.json');reports=[]
    for dep in spec['dependencies']:
        job=OUT.parents[4]/'jobs'/dep['job'];state,attempts=q.state(job)
        q.require(state=='complete','endpoint_report_dependency')
        q.require(q.load(attempts[-1]/'result.json')['specSHA256']==dep['specSHA256'],'endpoint_report_spec')
        ref=pin(attempts[-1]/'out/benchmark_summary.json');doc=completed(ref)
        reports.append(dict(job=dep['job'],source=ref,report=doc))
    q.save(OUT/'benchmark_summary.json',dict(version='sdk-endpoint-campaign-v1',reports=reports,modelAccepted=False,trainingEligible=False,
        limitation='Partial registered labels. Unknown profiles and action timing remain unknown. Related frames do not establish independent accuracy.'))
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
