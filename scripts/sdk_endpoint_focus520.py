"""Compare frozen crop models on verified SDK endpoints without action timing claims."""
import base64
import io
from pathlib import Path
from collections import Counter
import research_queue as q
from experiment_templates import pin, checked
from sdk_campaign508 import packet
from native_selection404 import outcome

OUT = None
SUCCESS = {'correct', 'correct-abstention'}


def prepare(request):
    q.require(set(request) == {'version','id','endpoints','models','tool'}, 'endpoint_fields')
    q.require(request['version'] == 'sdk-endpoint-focus-v1' and q.ID.fullmatch(request['id']), 'endpoint_identity')
    q.require(set(request['models']) == {'baseline','candidate'}, 'endpoint_models')
    q.require(0 < len(request['endpoints']) <= 16, 'endpoint_scope')
    frames = []
    for row in request['endpoints']:
        q.require(set(row) == {'manifest','caseID'}, 'endpoint_reference')
        frames.append(packet(checked(row['manifest']), row['caseID']))
    q.require(len({f['id'] for f in frames}) == len(frames), 'endpoint_duplicate')
    q.require(len({f['sha256'] for f in frames}) == len(frames), 'endpoint_duplicate_pixels')
    for ref in [*request['models'].values(), request['tool']]: checked(ref)
    return frames


def build(path):
    r = q.load(path); prepare(r)
    refs = [pin(path), *[e['manifest'] for e in r['endpoints']], *r['models'].values(), r['tool']]
    return dict(version='research-spec-v2', id=r['id'], task='SDK520', owner='Maximum-mini-NUIAK', kind='screen',
        jobKind='artifact', authority='diagnostic', dependencies=[], inputs=refs+[pin(Path(__file__).resolve())],
        adapter=dict(type='python-callable', steps=['sdk_endpoint_focus520.run'], outputAttributes=['sdk_endpoint_focus520.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),
        evidence=dict(artifactReceipt='artifact-receipt.json', reads=[p['path'] for p in refs]),
        question='Does the retained candidate preserve observed endpoint focus and no-focus with identical registered boxes?',
        hypothesis='Known geometry separates crop-score errors from missing detector proposals.',
        controlledComparison='Same retained pixels, native observations, production crops and 0.85 threshold. Change only frozen crop weights.',
        decisionRule='Reject lost successes or new wrong selections. Unknown profile stays unknown. Known boxes are diagnostic only.',
        nextActionByOutcome=dict(supported='Compare independent coverage before adoption.',contradicted='Use case-linked crop failures to choose the next correction.'))


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
    rows=[]
    for f in frames:
        boxes=[e['pixelBounds'] for e in f['controls']];arrays=[];hashes=[]
        items=[dict(id=str(i),path=str(checked(f['image'])),sha256=f['sha256'],bounds=b) for i,b in enumerate(boxes)]
        for batch in focus_runtime.bounded_batches(items,shared_images=True):
            reply=focus_runtime.invoke(batch,image_root=q.ROOT)
            for item in reply['results']:
                with Image.open(io.BytesIO(base64.b64decode(item['png'],validate=True))) as image:
                    q.require(image.size==(256,256),'endpoint_crop_shape');arr=np.array(image.convert('RGB'),copy=True)
                arrays.append(arr);hashes.append(__import__('hashlib').sha256(b'(256, 256)\0'+arr.tobytes()).hexdigest())
        scores={name:[] for name in nets}
        if arrays:
            tensor=torch.from_numpy(np.stack(arrays)).permute(0,3,1,2).float()/255
            with torch.no_grad():scores={name:torch.sigmoid(net(tensor)).reshape(-1).tolist() for name,net in nets.items()}
        models={name:dict(scores=s,outcome=outcome(s,boxes,f['truth'])) for name,s in scores.items()}
        old,new=models['baseline']['outcome'],models['candidate']['outcome']
        rows.append(dict(id=f['id'],image=f['image'],group=f['group'],contentGroup=f['contentGroup'],split=f['split'],role='review_only',
            profile=f['profile'],noFocus=f['truth'] is None,boxes=boxes,cropRGBSHA256=hashes,models=models,
            gain=old not in SUCCESS and new in SUCCESS,loss=old in SUCCESS and new not in SUCCESS,
            newWrong=old not in ('wrong','false-selection') and new in ('wrong','false-selection')))
    q.save(OUT/'benchmark_summary.json',dict(version='sdk-endpoint-focus-results-v1',request=pin(checked(spec['inputs'][0])),**summarize(rows)))
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
