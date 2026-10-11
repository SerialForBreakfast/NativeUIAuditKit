"""Measure retained native effects and authored scales without changing labels."""
from collections import defaultdict
from pathlib import Path
import numpy as np
import scale311 as run
import report_source310 as geometry

s=run.s
b=s.base
OUT=b.ROOT/'reports/work/FOCUS-312'


def metrics(value,endpoints):
    b.require(value.shape==(6,128,192) and np.isfinite(value).all(),'effect_input')
    delta=np.abs(value[:3]-value[3:]).mean(0)
    x,y=s.boxes(s.torch.from_numpy(value[None]))[0]
    patch=delta[y:y+32,x:x+32];total=float(delta.sum())
    coverage=geometry.coverage(dict(endpoints=endpoints,window=[x,y,x+32,y+32]))
    return dict(mean=float(delta.mean()),maximum=float(delta.max()),
        areaAbove1=sum((delta>1/255).flatten()).item(),
        areaAbove8=sum((delta>8/255).flatten()).item(),
        windowMean=float(patch.mean()),windowEnergyFraction=float(patch.sum()/total) if total else None,
        window=[x,y,x+32,y+32],bodyCoverage=coverage,
        measuredEndpoints=sum(e['status']=='measured' for e in endpoints))


def scaled_endpoints(endpoints,ratios):
    result=[]
    for e in endpoints:
        b.require(e['status']=='measured','missing_body')
        w,h=e['sourceSize'];sx,sy=ratios;x,y,bw,bh=e['visibleBody']
        nw,nh=round(w*sx),round(h*sy)
        result.append(dict(e,visibleBody=[x*sx+(w-nw)//2,y*sy+(h-nh)//2,bw*sx,bh*sy]))
    return result


def main():
    b.require(not OUT.exists(),'output_collision');s.torch.set_num_threads(2);OUT.mkdir()
    old=b.read(s.OUT/'size-audit.json')['rows'];audit=b.read(run.OUT/'scale-audit.json')
    seen=set();records=[]
    for row in audit['rows']:
        key=tuple(sorted(r['sha256'] for r in row['sourceImages']))
        if key in seen:continue
        seen.add(key);original=old[row['index']]
        b.require(original['role']=='train' and original['group']==row['group'],'training_group')
        images=[s.image(r['path'],r['sha256']) for r in row['sourceImages']]
        scaled,ratios=run.scale_pair(images,row['scale'])
        for view,frames,endpoints in [('original',images,original['endpoints']),
                                     ('scaled',scaled,scaled_endpoints(original['endpoints'],ratios))]:
            value=s.encoded(*frames,(192,128))[0]
            if view=='scaled':b.require(b.sha(value.tobytes())==row['tensorSHA256'],'derived_hash')
            records.append(dict(index=row['index'],group=row['group'],changed=row['changed'],
                role='train',view=view,target=row['targetPixels'],metrics=metrics(value,endpoints)))
        if len(seen)%100==0:print('Measured pairs',len(seen),flush=True)
    tiny,rows,pin=s.tiny_rows()
    for i,row in enumerate(rows):
        images=[s.image(r['path'],r['sha256']) for r in row['images']]
        records.append(dict(index=i,group='tiny-development',role='development',view=row['condition'],
            changed=row['changed'],target=None,metrics=metrics(tiny[i],s.measured(row,images))))
    grouped=defaultdict(list)
    for r in records:grouped[(r['role'],r['view'],str(r['target']),int(r['changed']))].append(r)
    summaries=[]
    for key,rows in sorted(grouped.items()):
        fields={k:np.percentile([r['metrics'][k] for r in rows],[0,50,100]).tolist()
                for k in ('mean','maximum','areaAbove1','areaAbove8','windowMean')}
        summaries.append(dict(role=key[0],view=key[1],target=key[2],changed=key[3],count=len(rows),ranges=fields))
    b.write(OUT/'effect-audit.json',dict(runner=b.ref(Path(__file__)),sourceAudit=b.ref(s.OUT/'size-audit.json'),
        scaleAudit=b.ref(run.OUT/'scale-audit.json'),tiny=pin,records=records,summaries=summaries,
        limitation='Image changes include content and rendering differences. These metrics do not independently establish focus labels.'))
    for r in summaries:
        if r['changed'] and (r['view']!='original' or r['target']=='3.0'):print(r,flush=True)


if __name__=='__main__':main()
