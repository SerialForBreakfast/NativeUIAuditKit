"""Bounded retained feedback extraction; no training admission or live capture."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
from PIL import Image
import shared_transfer as t
from focus_surface_intake import safe_members, fresh, write


def extract(transaction,output):
    tx=t.document(transaction);source=t.path_under(t.ROOT,tx['localPath'])
    t.verified(source,tx);output=fresh(output)
    with tarfile.open(source) as archive:
        members,total=safe_members(archive)
        t.require(shutil.disk_usage(t.ROOT).free>total+1_000_000_000,'capacity')
        output.mkdir(parents=True)
        inventory=[]
        for m in members:
            target=output/m.name
            if m.isdir():target.mkdir(parents=True,exist_ok=True);continue
            target.parent.mkdir(parents=True,exist_ok=True)
            with archive.extractfile(m) as src,target.open('xb') as dst:shutil.copyfileobj(src,dst)
            with target.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
            row=dict(path=m.name,bytes=target.stat().st_size,sha256=digest)
            if target.suffix.lower()=='.png':
                t.require(target.stem==digest,'image_filename_hash')
                with Image.open(target) as image:
                    t.require(image.width*image.height<=40_000_000,'image_limit');image.verify()
                with Image.open(target) as image:image.load();row['dimensions']=list(image.size)
            inventory.append(row)
    t.verified(source,tx)
    result=dict(requestID=tx['requestID'],archiveSHA256=tx['sha256'],expandedBytes=total,
                inventory=inventory,trainingEligible=False,reviewedLabels=False)
    write(output/'extraction.json',result)
    print(json.dumps(dict(files=len(inventory),images=sum(x['path'].endswith('.png') for x in inventory),expandedBytes=total)))


def review(root,output):
    import numpy as np
    import adapt_reflow117 as a
    import transition_shadow_export as contract
    from diagnose_signal95 import encoded
    from verify_transition_shadow106 import decision
    root=root.absolute();t.require(root.is_relative_to(t.ROOT) and root.resolve()==root,'review_boundary');output=fresh(output)
    manifest=t.document(root/'manifest.json');t.require(manifest['version']==1,'manifest_version')
    seen=set()
    for r in manifest['files']:
        t.require(r['path'] not in seen,'manifest_duplicate');seen.add(r['path'])
        t.verified(t.path_under(root,r['path']),r)
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    t.require(actual==seen|{'manifest.json'},'manifest_membership')
    torch=a.r.d.torch_runtime();torch.set_num_threads(2)
    models={}
    for name,path,digest in [('transition','collection104-dtm025',contract.CHECKPOINT),
                             ('transition_dtm030','reflow117-dtm030',contract.RESIDUAL_CHECKPOINT)]:
        file=a.h.ROOT/f'NativeUITrainer/focus_ring_runs/{path}/last.pt'
        t.require(a.h.ref(file)['sha256']==digest,'checkpoint')
        state=torch.load(file,weights_only=True,map_location='cpu')
        net=a.r.d.model(state['configuration']) if name=='transition' else a.r.model(a.r.d.model(a.r.d.PAIRED_TEMPORAL_CONFIG))
        net.load_state_dict(state['state']);models[name]=net.eval()
    report={};canonical=None
    for name,net in models.items():
        folder=root/name;request=t.document(folder/'request.template.json');result=t.document(folder/'result.json')
        receipt=t.document(folder/'receipt.json');bindings=t.document(folder/'bindings-private.json')
        t.require(receipt['prediction_sha256']==a.h.ref(folder/'result.json')['sha256'],'prediction_binding')
        pairs=request['pairs'];ids=[p['id'] for p in pairs]
        t.require(len(ids)==len(set(ids)) and ids==[p['id'] for p in result['results']]==[p['id'] for p in bindings],'interval_membership')
        if canonical is None:canonical=pairs
        else:t.require(canonical==pairs,'model_input_disagreement')
        expected=contract.MODEL_ID if name=='transition' else contract.RESIDUAL_MODEL_ID
        t.require(result['modelID']==expected and result['inputEncoding']==contract.ENCODING and
                  result['changedThreshold']==.85 and result['backend']=='cpuOnly','model_contract')
        rows=[]
        for pair,prior,binding in zip(pairs,result['results'],bindings):
            images=[]
            for side in ('before','after'):
                ref=pair[side];t.require(ref['path']==f"$ROOT/originals/{ref['sha256']}.png",'relocation_scope')
                path=root/'originals'/f"{ref['sha256']}.png"
                with Image.open(path) as image:images.append(image.convert('RGB'))
                t.require(prior[side+'SHA256']==ref['sha256'],'pair_binding')
            x=encoded(*images,size=(192,128))[0];digest=hashlib.sha256(x.tobytes()).hexdigest()
            t.require(digest==prior['encodedSHA256'],'encoded_mismatch')
            with torch.inference_mode():
                p=float(a.r.c.score_change(net,torch.from_numpy(x[None]),a.CONFIG)[0])
            rows.append(dict(id=pair['id'],encodedSHA256=digest,peerProbability=prior['probability'],
                localProbability=p,delta=abs(p-prior['probability']),peerDecision=prior['decision'],
                localDecision=decision(p),nativeHint=binding['native_focus_changed'],
                identicalBytes=pair['before']['sha256']==pair['after']['sha256']))
        report[name]=dict(rows=rows,decisionsMatch=all(r['localDecision']==r['peerDecision'] for r in rows),
                          maxDelta=max(r['delta'] for r in rows),checkpoint=a.h.ref(a.h.ROOT/f"NativeUITrainer/focus_ring_runs/{'collection104-dtm025' if name=='transition' else 'reflow117-dtm030'}/last.pt"))
    output.parent.mkdir(parents=True,exist_ok=True)
    write(output,dict(source=a.h.ref(__file__),manifest=a.h.ref(root/'manifest.json'),models=report,trainingEligible=False,reviewedAccuracy=None))
    print(json.dumps({k:dict(decisionsMatch=v['decisionsMatch'],maxDelta=v['maxDelta'],pairs=len(v['rows'])) for k,v in report.items()}))


def contact_sheet(root,output):
    from PIL import ImageDraw
    root=root.absolute();output=fresh(output)
    records=t.document(root/'survey.json')['records'];unique={}
    for row in records:
        digest=row['image_sha256'];unique.setdefault(digest,[]).append(row.get('observation_id',row.get('id','?')))
    canvas=Image.new('RGB',(1440,310*((len(unique)+2)//3)),(30,30,30));draw=ImageDraw.Draw(canvas)
    for i,(digest,ids) in enumerate(unique.items()):
        with Image.open(root/'originals'/f'{digest}.png') as im:
            im=im.convert('RGB');im.thumbnail((480,270));x=(i%3)*480;y=(i//3)*310
            canvas.paste(im,(x,y));draw.text((x+5,y+273),digest[:12],fill='white')
            draw.text((x+5,y+288),','.join(str(v).split(':')[-1] for v in ids),fill='white')
    canvas.save(output)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path)
    mode=p.add_mutually_exclusive_group();mode.add_argument('--review',action='store_true');mode.add_argument('--contact-sheet',action='store_true')
    args=p.parse_args();(review if args.review else contact_sheet if args.contact_sheet else extract)(args.input,args.output)
