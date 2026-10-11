"""Validate small native pairs and score fixed models without training."""
import json
import subprocess
import numpy as np
from PIL import Image
import condition291 as c
import transition242 as labels
from diagnose_signal95 import encoded
from report_spatial297 import counts, decision, proposal_decision
import focus302 as capture
import harvest_schema4_review as review

base=c.base
OUT=capture.ROOT/'reports/work/FOCUS-302/capture-r2'
EVAL=OUT/'analysis'


def run():
    require=base.require
    require((OUT/'completion.json').exists() and not EVAL.exists(),'capture_incomplete_or_collision')
    EVAL.mkdir()
    campaign=base.read(OUT/'campaign-v3.json')
    tensors=[];rows=[];requests=[];dispositions=[];review_rows=[];indexed=0
    frames=EVAL/'encoded';frames.mkdir()
    for entry in campaign['recipes']:
        root=OUT/'exports'/entry['id']
        receipt=base.read(root/'harvest-receipt.json')
        require(receipt['outcome']=='completed' and receipt['acceptedRowCount']==4 and not receipt['rejections'],'incomplete_receipt')
        for artifact in base.read(root/'dataset-index.json')['artifacts']:
            raw=review.read(root,artifact['path'])
            require(len(raw)==artifact['byteCount'] and review.digest(raw)==artifact['sha256'],'indexed_hash')
            indexed+=1
        for item in base.read(root/'manifest.json'):
            path=root/item['metadata']['metadataPath'];meta=base.read(path)
            try:
                checked=review.pair(root,item['metadata']['metadataPath'],expected_version=meta['schema_version'])
            except ValueError as error:
                dispositions.append(dict(metadata=base.ref(path),accepted=False,reason=str(error),
                    bodyEvidence=[next(e for e in meta[s]['elements'] if e['element_id']==meta['focused_element_id'])['rendered_body_geometry']
                                  for s in ('baseline_scene','focused_scene')]))
                continue
            dispositions.append(dict(metadata=base.ref(path),accepted=True,scope='development inspection, not training admission'))
            review_rows.append(dict(checked,path=entry['id']+'/'+checked['path']))
            truth=labels.label(meta['baseline_scene'],meta['focused_scene'])
            require(truth==1,'expected_focus_change')
            images=[]
            for prefix in ('unfocused','focused'):
                imagepath=path.parent/meta[prefix+'_png']
                require(capture.digest(imagepath)==meta[prefix+'_sha256'],'image_hash')
                with Image.open(imagepath) as image: images.append(image.convert('RGB'))
            value,transform=encoded(*images,(192,128))
            minimum=[]
            for scene in (meta['baseline_scene'],meta['focused_scene']):
                element=next(e for e in scene['elements'] if e['element_id']==scene['focused_element_id'])
                box=element['rendered_body_geometry']['visible_pixel_bounds']
                minimum.append(min(box[2]*transform[0],box[3]*transform[1]))
            variants=[('forward',value,1),('reverse',np.concatenate((value[3:],value[:3])),1),
                      ('same-before',np.concatenate((value[:3],value[:3])),0),
                      ('same-after',np.concatenate((value[3:],value[3:])),0)]
            for mode,tensor,y in variants:
                identity=f'{entry["id"]}:{meta["focused_element_id"]}:{mode}'
                index=len(rows);refs=[]
                for offset in (0,3):
                    p=frames/f'{index}-{offset}.png'
                    Image.fromarray(np.rint(tensor[offset:offset+3].transpose(1,2,0)*255).astype(np.uint8)).save(p)
                    refs.append(dict(path=str(p),sha256=capture.digest(p)))
                requests.append(dict(id=identity,previous=refs[0],current=refs[1]))
                rows.append(dict(id=identity,condition=mode,recipe=entry['id'],group=entry['group'],
                    role='development',changed=y,minimumBodyInputPixels=min(minimum),metadata=base.ref(path)))
                tensors.append(tensor)
    require(len(dispositions)==8 and len(rows)==4*sum(r['accepted'] for r in dispositions),'expected_accounting')
    require(rows,'no_eligible_pairs')
    base.write(EVAL/'intake-subset.json',dict(dispositions=dispositions,indexedFiles=indexed,
        acceptedPairs=sum(r['accepted'] for r in dispositions),expectedPairs=8,trainingEligible=False))
    cropdir=EVAL/'qualified-crops';cropdir.mkdir()
    rendered=review.render_review(OUT/'exports',cropdir,dict(rows=review_rows,expected=len(review_rows),reviewed=len(review_rows)))
    base.write(EVAL/'crop-review.json',rendered)
    models={}
    for name,folder in [('DTM083','TRANSITION-291'),('DTM085','TRANSITION-292')]:
        result=base.read(base.ROOT/f'reports/work/{folder}/{name}/result.json')
        base.checked(result['model']);models[name]=result['model']
    base.write(EVAL/'scoring-registration.json',dict(models=models,rows=rows,campaign=base.ref(OUT/'campaign-v3.json'),
        noiseThreshold=24,thresholds=[.15,.85],training=False,outputCapBytes=128*1024**2,
        scope='New development derivatives of the existing training recipe. No final evaluation.'))
    request=EVAL/'proposal-request.json'
    base.write(request,dict(version=1,root=str(EVAL),noiseThreshold=24,localizeOnly=True,pairs=requests))
    with request.open('rb') as source,(EVAL/'proposals.json').open('xb') as target,(EVAL/'proposal.log').open('xb') as log:
        subprocess.run([str(base.ROOT/'.build/debug/TransitionTool')],stdin=source,stdout=target,stderr=log,check=True,timeout=120)
    proposals=base.read(EVAL/'proposals.json')['results']
    require([r['id'] for r in proposals]==[r['id'] for r in rows],'proposal_order')
    base.torch.set_num_threads(2)
    scores={name:base.worker.score(c.model.load_candidate(base.checked(ref)),np.stack(tensors)).tolist()
            for name,ref in models.items()}
    for i,row in enumerate(rows):
        row['emptyProposal']=not proposals[i]['regions']
        row['scores']={name:p[i] for name,p in scores.items()}
    reports=[]
    for recipe in ('size-40','size-80'):
        for mode in ('forward','reverse','same-before','same-after'):
            selected=[r for r in rows if r['recipe']==recipe and r['condition']==mode]
            for name in models:
                y=[r['changed'] for r in selected];a=[decision(r['scores'][name]) for r in selected]
                b=[proposal_decision(r['scores'][name],0 if r['emptyProposal'] else 1,'changed-only') for r in selected]
                reports.append(dict(recipe=recipe,condition=mode,model=name,original=counts(y,a),diagnostic=counts(y,b)))
    base.write(EVAL/'evaluation.json',dict(version='focus302-v1',rows=rows,reports=reports,
        models=models,productionEligible=False,training=False,independentGroups=None))
    print(json.dumps(reports,indent=2))


if __name__=='__main__':run()
