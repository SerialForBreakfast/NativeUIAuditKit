"""Queue matched position and branch corrections with retained regression checks."""
import copy
import time
from pathlib import Path
import numpy as np
from PIL import Image
import appearance348 as m

q=m.q;a=m.a;t=m.t;OUT=None
ARMS=('control','position','position-branch')


def key(row):
    return q.text_digest({k:row[k] for k in ('group','sizePixels','widthPixels','contrast','separationPixels','corner')})


def positions(rows):
    keys=sorted({key(row) for row in rows if 'patchBounds' in row})
    return {value:i%9 for i,value in enumerate(keys)}


def translate(images,boxes,cell):
    """Move both authored patches together without interpolation or clipping."""
    q.require(type(cell) is int and 0<=cell<9,'position_cell')
    q.require(len(images)==2 and images[0].size==images[1].size,'image_dimensions')
    w,h=images[0].size
    q.require(boxes and all(len(b)==4 and all(type(v) is int for v in b) and
        min(b[:2])>=0 and min(b[2:])>0 and b[0]+b[2]<=w and b[1]+b[3]<=h for b in boxes),'patch_bounds')
    left=min(b[0] for b in boxes);top=min(b[1] for b in boxes)
    right=max(b[0]+b[2] for b in boxes);bottom=max(b[1]+b[3] for b in boxes)
    dx=round((w-(right-left))*(cell%3)/2)-left
    dy=round((h-(bottom-top))*(cell//3)/2)-top
    mask=np.zeros((h,w),bool)
    for x,y,bw,bh in boxes:mask[y:y+bh,x:x+bw]=True
    output=[]
    for image in images:
        pixels=np.asarray(image.convert('RGB'));color=tuple(int(v) for v in pixels[0,0])
        q.require(np.all(pixels[~mask]==color),'nonuniform_context')
        canvas=Image.new('RGB',(w,h),color)
        for x,y,bw,bh in boxes:canvas.paste(image.crop((x,y,x+bw,y+bh)),(x+dx,y+dy))
        output.append(canvas)
    return output,(dx,dy)


def training():
    start=time.monotonic();config=q.load(OUT/'config.json');m.check_inputs(config)
    arm=config['arm'];q.require(arm in ARMS,'arm');t.set_num_threads(2)
    m.OUT=OUT;a.e.f.OUT=OUT
    reg=q.load(a.e.OUT/'inputs.json');reg['trainer']=a.b.ref(Path(a.b.trainer.__file__))
    m.emit('Verify retained training views',0,10)
    x,d,y,w,aux,ad,ay,indices=a.e.f.prepare(reg)
    rows=q.load(OUT/'preparation.json')['rows']
    q.require(all(row['role']=='train' for row in rows),'training_role')
    net=a.e.load_candidate(a.e.OUT/'run/last.pt')
    original=m.raw_logits(net,x,d);aux_original=m.raw_logits(net,aux,ad)
    mapping=positions(rows);audit=[]
    if arm!='control':
        for i,row in enumerate(rows):
            if 'patchBounds' not in row:continue
            images=[a.r.s.image(v['path'],v['sha256']) for v in row['images']]
            images,offset=translate(images,row['patchBounds'],mapping[key(row)])
            values=a.r.s.encoded(*images,(192,128))[0]
            selected=a.r.windows(t.from_numpy(values[None]))[0];parts=[]
            for j in range(2):
                if not selected:parts.append(values.copy());continue
                px,py=selected[min(j,len(selected)-1)]
                parts.append(a.r.s.crop_pair(images,[px,py,px+32,py+32],preserve_padding=True))
            aux[i]=values;ad[i]=np.concatenate(parts)
            audit.append(dict(index=i,group=row['group'],cell=mapping[key(row)],offset=offset,
                patchBounds=[[bx+offset[0],by+offset[1],bw,bh] for bx,by,bw,bh in row['patchBounds']]))
            if i%64==0:m.emit('Prepare matched positions',i,len(rows))
    q.save(OUT/'augmentation.json',dict(rows=audit,cellCounts={str(c):sum(v['cell']==c for v in audit) for c in range(9)},
        auxiliarySHA256=a.e.f.digest(aux),detailSHA256=a.e.f.digest(ad),rolesChanged=False,
        limitation='Cells describe the translated patch group, not uniform focus-center coverage. Original examples remain in the primary loss.'))
    initial={k:v.clone() for k,v in net.state_dict().items()}
    settings=dict(reg['configuration'],epochs=10,seed=42,threads=2,detailOnly=arm!='position-branch')
    def progress(row):
        q.save(OUT/f"epoch-{row['epoch']:04d}.json",row);m.emit('Train '+arm,row['epoch'],10)
    net,history=a.b.trainer.fit(net,t.from_numpy(x),t.from_numpy(y),settings,progress,
        weights=t.from_numpy(w),detail_inputs=t.from_numpy(d),auxiliary_inputs=t.from_numpy(aux),
        auxiliary_detail=t.from_numpy(ad),auxiliary_indices=t.from_numpy(indices),auxiliary_weight=.25,
        preservation_logits=original,auxiliary_preservation_logits=aux_original,preservation_weight=1.)
    changed=[k for k,v in net.state_dict().items() if not t.equal(v,initial[k])]
    allowed=('change.',) if arm=='position-branch' else ('change.detail.','change.correction.')
    q.require(changed and all(k.startswith(allowed) for k in changed),'changed_scope')
    t.save(dict(state=net.state_dict(),representation=a.e.VERSION,windows=2),OUT/'last.pt')
    restored=a.e.load_candidate(OUT/'last.pt');sample=np.concatenate((x[:8],d[:8]),1)
    q.require(np.array_equal(a.b.worker.score(net,sample),a.b.worker.score(restored,sample)),'reload_parity')
    q.save(OUT/'fit.json',dict(configuration=settings,history=history,changedTensors=changed,
        seconds=time.monotonic()-start,checkpointParity=True,model=m.f.pin(OUT/'last.pt'),productionEligible=False))
    m.emit('Training complete; comparisons required',10,10)


def evaluate():
    config=q.load(OUT/'config.json');m.check_inputs(config)
    deps=q.load(OUT/'dependencies.json');q.require(len(deps)==1,'candidate_dependency')
    dep=deps[0]
    for ref in [dep['result'],*dep['outputs']]:
        q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'dependency_changed')
    candidate=next(ref for ref in dep['outputs'] if ref['path'].endswith('/last.pt'))
    config['models']={'control':m.f.pin(a.e.OUT/'run/last.pt'),'gamma':candidate}
    config['inputs'] += list(config['models'].values())
    q.save(OUT/'config.json',config,replace=True)
    if config.get('capture'):
        import compare351
        config.update(mode=config['mode'],inputs=config['inputs']+[config['capture']])
        q.save(OUT/'config.json',config,replace=True);compare351.OUT=OUT;compare351.run()
    elif config.get('sources'):
        import retained348
        retained348.OUT=OUT;retained348.run()
    else:m.OUT=OUT;m.diagnostic()


def collect():
    rows=[]
    for dep in q.load(OUT/'dependencies.json'):
        for ref in [dep['result'],*dep['outputs']]:
            q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'dependency_changed')
        doc=q.load(q.ROOT/dep['outputs'][0]['path'])
        if 'summaryRows' in doc:
            rows.extend(doc['summaryRows']);continue
        sets=doc['sets'].values() if 'sets' in doc else [doc]
        counts={}
        for item in sets:
            group=item['againstOriginal']['gamma'] if 'againstOriginal' in item else item['scores']['gamma']['counts']
            for value in group.values():
                for k,v in value.items():counts[k]=counts.get(k,0)+v
        rows.append(dict(job=dep['job'],counts=counts))
    q.require(len({r['job'] for r in rows})==len(rows),'duplicate_comparison')
    decisions={}
    for arm in ARMS:
        selected=[r for r in rows if r['job'].startswith('focus355-'+arm+'-') and
            (arm!='position' or not r['job'].startswith('focus355-position-branch-'))]
        complete=len(selected)==24
        lost=sum(r['counts'].get('lost',0) for r in selected)
        gained=sum(r['counts'].get('gained',0) for r in selected if r['job'].endswith('-movement'))
        decisions[arm]=dict(comparisons=len(selected),complete=complete,lostPrevious=lost,
            gainedNativeMovement=gained,passesDevelopmentRule=complete and lost==0 and gained>0)
    q.save(OUT/'summary.json',dict(summaryRows=rows,decisions=decisions,modelAccepted=False,
        limitation='Counts can include repeated cases. Development results do not establish deployment qualification.'))


def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS355';folder.mkdir(exist_ok=True)
    base=q.load(q.ROOT/'Research/ResearchSpecs/FOCUS348/focus348-00-control.json')
    oldconfig=q.load(q.ROOT/base['stage'][0]['from']['path'])
    chunks=[]
    for arm in ARMS:
        spec=copy.deepcopy(base);ident='focus355-'+arm+'-train'
        spec.update(id=ident,task='FOCUS355',hypothesis='Matched position examples test spatial bias; the branch arm also learns whole-frame features.',
            decisionRule='Require target gains with no lost previous successes. Preserve original views and thresholds 0.15/0.85.',
            adapter=dict(type='python-callable',steps=['position355.training'],outputAttributes=['position355.OUT']))
        spec['training']['experimentLogRunId']='FOCUS355'
        config=copy.deepcopy(oldconfig);config['arm']=arm
        refs={v['path']:m.f.pin(q.ROOT/v['path']) for v in config['inputs']}
        for name in ('position355.py','appearance348.py','native_adapt152.py'):
            refs['scripts/'+name]=m.f.pin(q.ROOT/'scripts'/name)
        config['inputs']=list(refs.values());spec['inputs']=config['inputs']
        if arm=='control':
            ident='focus348-00-control'
            spec=q.load(q.QUEUE/'jobs'/ident/'spec.json')
            q.require(q.state(q.QUEUE/'jobs'/ident)[0]=='complete','control_incomplete')
            fit=q.load(q.QUEUE/'jobs'/ident/'attempts/1/out/fit.json')
            q.require(fit['configuration']['epochs']==10 and fit['configuration']['seed']==42
                and fit['checkpointParity'] and spec['training']['initialization']==base['training']['initialization'], 'control_not_matched')
        else:
            cp=folder/(ident+'-config.json');q.save(cp,config);spec['stage']=[{'from':m.f.pin(cp),'to':'config.json'}]
            sp=folder/(ident+'.json');q.save(sp,spec);print(ident,q.submit(sp))
        sources=[q.ROOT/'Research/ResearchSpecs/FOCUS348'/('focus348-'+suffix+'.json') for suffix in
            ('01-original','02-regression-native','03-regression-replay','04-regression-global','05-regression-left','06-regression-center',
             '27-neighbors-0','28-neighbors-2','29-placeholders')]
        configs=[]
        for source in sources:
            prior=q.load(source);c=q.load(q.ROOT/prior['stage'][0]['from']['path'])
            configs.append((source.stem.replace('focus348-',''),c))
        for factor in ('size','growth','shadow','position','background'):
            capture=m.f.pin(q.QUEUE/f'jobs/generation354b-{factor}-capture/attempts/1/out/capture/capture.json')
            for mode in ('movement','content','recapture'):
                configs.append((factor+'-'+mode,dict(capture=capture,mode=mode,inputs=[capture])))
        consumers=[]
        for suffix,c in configs:
            eid=f'focus355-{arm}-{suffix}'
            c.pop('models',None);c['modelNames']={'control':'FOCUS329','gamma':arm}
            refs={v['path']:m.f.pin(q.ROOT/v['path']) for v in c['inputs']}
            for name in ('position355.py','appearance348.py','compare351.py','retained348.py'):
                refs['scripts/'+name]=m.f.pin(q.ROOT/'scripts'/name)
            c['inputs']=list(refs.values());cp=folder/(eid+'-config.json');q.save(cp,c)
            consumer=dict(version=q.SPEC_VERSION,id=eid,task='FOCUS355',owner='Maximum-mini-NUIAK',kind='screen',authority='diagnostic',
                hypothesis='Test '+arm+' against retained successes and controlled native failures: '+suffix,
                decisionRule='Report gains, losses, false changes, misses, and abstentions. Any lost previous success rejects replacement.',
                inputs=c['inputs'],stage=[{'from':m.f.pin(cp),'to':'config.json'}],
                dependencies=[dict(job=ident,specSHA256=q.text_digest(spec),outputs=['last.pt','fit.json'])],
                adapter=dict(type='python-callable',steps=['position355.evaluate'],outputAttributes=['position355.OUT']),
                limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
            sp=folder/(eid+'.json');q.save(sp,consumer);print(eid,q.submit(sp))
            consumers.append(dict(job=eid,specSHA256=q.text_digest(consumer),
                outputs=['diagnostic.json' if c.get('capture') else 'comparison.json']))
        for i in range(3):
            chunk=report_spec(f'focus355-{arm}-summary-{i}',consumers[i*8:(i+1)*8])
            sp=folder/(chunk['id']+'.json');q.save(sp,chunk);print(chunk['id'],q.submit(sp))
            chunks.append(dict(job=chunk['id'],specSHA256=q.text_digest(chunk),outputs=['summary.json']))
    final=report_spec('focus355-final-comparison',chunks)
    sp=folder/(final['id']+'.json');q.save(sp,final);print(final['id'],q.submit(sp))


def report_spec(ident,deps):
    return dict(version=q.SPEC_VERSION,id=ident,task='FOCUS355',owner='Maximum-mini-NUIAK',
        kind='screen',authority='diagnostic',hypothesis='Account for every comparison before judging a candidate.',
        decisionRule='Require all 24 comparisons per arm, target gains, and zero lost previous successes. Do not promote automatically.',
        inputs=[m.f.pin(Path(__file__))],dependencies=deps,
        adapter=dict(type='python-callable',steps=['position355.collect'],outputAttributes=['position355.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))


if __name__=='__main__':register()
