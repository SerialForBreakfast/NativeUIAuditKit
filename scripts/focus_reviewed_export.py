"""Complete frozen-encoder/head trace and development parity; no training."""
import argparse
import hashlib
import json
from pathlib import Path
from focus_dataset_contract import ROOT, local, digest, FocusDataError

def require(ok,reason):
    if not ok:raise FocusDataError(reason)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha(p))
def checked(r):
    p=local(ROOT/r['path']);require(sha(p)==r['sha256'],'changed_export_input');return p
def sealed(p):
    d=json.loads(local(p).read_text());v=dict(d);s=v.pop('seal');require(digest(v)==s,'changed_export_seal');return d
def save(p,d):
    with p.open('x') as f:json.dump(d,f,indent=2,allow_nan=False)

def checked_trace(path,weights_hash,checkpoint):
    d=sealed(path)
    require(d['version']=='focus-complete-trace-v1' and d['checkpoint']['sha256']==weights_hash
        and checkpoint.get('checkpointKind')=='frozen-pretrained-linear-head-v1'
        and checkpoint.get('protocolSHA256')==d['protocolSHA256']
        and checkpoint.get('representation')==d['representation'],'wrong_complete_trace')
    require(d['representation']['kind']=='mobilenet_v3_small_frozen' and d['representation']['features']==576,
        'unsupported_trace_representation')
    for k in ('trace','checkpoint','encoder','protocol','reference'):checked(d[k])
    require(d['encoder']==d['representation']['weights'],'changed_trace_encoder')
    return d

def prepare(protocol,weights,output):
    import torch
    import numpy as np
    from PIL import Image
    from torchvision.models import mobilenet_v3_small
    from focus_pretrained_experiment import REPRESENTATION, WEIGHTS_SHA, state_digest
    from focus_export_parity import compare
    p=json.loads(protocol.read_text());content=dict(p);s=content.pop('protocolSHA256')
    require(digest(content)==s and p['version']=='focus-reviewed-full-fit-v1','wrong_export_protocol')
    ck=torch.load(weights,map_location='cpu',weights_only=True);rep=p['representation']
    require(ck['protocolSHA256']==s and ck['checkpointKind']=='frozen-pretrained-linear-head-v1'
            and ck['representation']==rep,'checkpoint_protocol_mismatch')
    require({k:v for k,v in rep.items() if k!='weights'}==REPRESENTATION and rep['weights']['sha256']==WEIGHTS_SHA,'wrong_encoder')
    require(not output.exists(),'output_collision');output.mkdir(parents=True)
    net=mobilenet_v3_small(weights=None);net.load_state_dict(torch.load(checked(rep['weights']),map_location='cpu',weights_only=True))
    encoder=torch.nn.Sequential(net.features,net.avgpool).eval()
    receipt=json.loads(checked(p['baseCachedInputs']['receipt']).read_text())
    require(state_digest(encoder)==receipt['featureStateSHA256'],'wrong_encoder_state')
    head=torch.nn.Linear(576,1);head.load_state_dict(ck['state_dict'],strict=True)
    class Complete(torch.nn.Module):
        def __init__(self):
            super().__init__();self.encoder=encoder;self.head=head
            self.register_buffer('mean',torch.tensor(REPRESENTATION['normalization']['mean']).view(1,3,1,1))
            self.register_buffer('std',torch.tensor(REPRESENTATION['normalization']['std']).view(1,3,1,1))
        def forward(self,x):
            prob=torch.sigmoid(self.head(self.encoder((x-self.mean)/self.std).flatten(1))).reshape(-1)
            return prob,torch.abs(prob-.5)*2
    model=Complete().eval();traced=torch.jit.trace(model,torch.zeros(1,3,256,256)).eval()
    traced.save(str(output/'complete.pt'))
    rows=[r for r in p['samples'] if r['split']=='validation'];pred=[]
    with torch.no_grad():
        for r in rows:
            with Image.open(checked(r['crop'])) as im:
                require(im.size==(256,256),'wrong_crop_size')
                x=torch.from_numpy(np.array(im.convert('RGB'),copy=True)).permute(2,0,1).float().unsqueeze(0)/255
            a=model(x);b=traced(x);require(all(torch.allclose(v,w,atol=1e-6,rtol=1e-5) for v,w in zip(a,b)),'trace_changed_output')
            pred.append(dict(id=r['id'],label=r['label'],probability=float(a[0].item()),confidence=float(a[1].item())))
    result=json.loads((weights.parent.parent/'experiment-result.json').read_text())
    old=next(h['validation']['predictions'] for h in result['history'] if h['update']==ck['epoch'])
    cross=compare(old,pred);require(cross['passed'],'cpu_vs_cached_mps_failed')
    save(output/'reference.json',dict(predictions=pred,cpuVsCachedMPS=cross,torchVersion=str(torch.__version__),backend='torch-cpu'))
    d=dict(version='focus-complete-trace-v1',checkpoint=ref(weights),encoder=rep['weights'],protocol=ref(protocol),
        protocolSHA256=s,representation=rep,trace=ref(output/'complete.pt'),reference=ref(output/'reference.json'),releaseEligible=False)
    d['seal']=digest(d);save(output/'receipt.json',d);print('Complete trace and CPU reference: '+str(len(pred))+' crops')

def parity(receipt,model,export,output):
    import base64,io
    from PIL import Image
    from focus_export_parity import compare,validate_model_identity
    from focus_runtime import invoke,bounded_batches,identity
    from focus_ring_baseline import artifact_digest
    d=sealed(receipt);p=json.loads(checked(d['protocol']).read_text());reference=json.loads(checked(d['reference']).read_text())
    report=json.loads(export.read_text());require(report['checkpointSHA256']==d['checkpoint']['sha256'],'wrong_export_checkpoint')
    contract=validate_model_identity(model,report);before=artifact_digest(model);runtime=identity()
    rows=[r for r in p['samples'] if r['split']=='validation'];items=[]
    for r in rows:
        frame=r.get('frame',r.get('image'));items.append(dict(id=r['id'],path=str(checked(frame)),sha256=frame['sha256'],bounds=r['bounds']))
    observed=[];batches=[];by_id={r['id']:r for r in rows}
    for batch in bounded_batches(items):
        cropped=invoke(batch)
        for v in cropped['results']:
            with Image.open(io.BytesIO(base64.b64decode(v['png'],validate=True))) as im:
                px=hashlib.sha256(str(im.size).encode()+b'\0'+im.convert('RGB').tobytes()).hexdigest()
            r=by_id[v['id']]
            require(px==r.get('pixelSHA256',r['crop'].get('pixelSHA256')),'production_crop_parity_failed')
        reply=invoke(batch,model);batches.append({k:v for k,v in reply.items() if k!='results'});observed.extend(reply['results'])
    require([v['id'] for v in observed]==[r['id'] for r in rows],'incomplete_parity')
    predictions=[dict(id=r['id'],label=r['label'],probability=v['probability']) for r,v in zip(rows,observed)]
    input_pixels=sum(v.get('modelInputRGBSHA256')==r.get('pixelSHA256',r['crop'].get('pixelSHA256')) for r,v in zip(rows,observed))
    if report.get('inputPixelContract'):
        require(input_pixels==len(rows),'model_input_rgb_parity_failed')
    measured=compare(reference['predictions'],predictions)
    require(before==artifact_digest(model) and runtime==identity(),'runtime_or_model_changed')
    for r in rows:checked(r['crop']);checked(r.get('frame',r.get('image')))
    save(output,dict(version='focus-reviewed-coreml-parity-v1',releaseEligible=False,comparison=measured,
        compiledContract=contract,runtime=runtime,batches=batches,predictions=predictions,reference=d['reference'],productionCropPixelsMatched=len(rows),
        modelInputRGBPixelsMatched=input_pixels,inputPixelContract=report.get('inputPixelContract')))
    print(json.dumps({k:v for k,v in measured.items() if k!='differences'}));return 0 if measured['passed'] else 1

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','parity'])
    for k in ('protocol','weights','receipt','model','export','output'):p.add_argument('--'+k,type=local)
    a=p.parse_args()
    if a.mode=='prepare':prepare(a.protocol,a.weights,a.output);return 0
    return parity(a.receipt,a.model,a.export,a.output)
if __name__=='__main__':raise SystemExit(main())
