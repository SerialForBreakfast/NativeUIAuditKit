"""Compare image-only boundary regions while preserving the crop budget."""
import argparse
from pathlib import Path
import time
import numpy as np
import boundary329 as a
import controls330 as c

b=a.b;r=a.r;t=a.t;OUT=b.ROOT/'reports/work/FOCUS-331'
POLICIES=('boundary','retain_first')
ORIGINAL_WINDOWS=r.windows


def boundary_energy(values):
    b.require(values.ndim==4 and values.shape[1:]==(6,128,192),'input_shape')
    b.require(bool(t.isfinite(values).all()),'nonfinite_input')
    smooth=t.nn.functional.avg_pool2d(t.nn.functional.pad(values,(2,2,2,2),mode='replicate'),5,stride=1)
    dx=t.nn.functional.pad((smooth[:,:,:,1:]-smooth[:,:,:,:-1]).abs(),(0,1,0,0))
    dy=t.nn.functional.pad((smooth[:,:,1:,:]-smooth[:,:,:-1,:]).abs(),(0,0,0,1))
    magnitude=(dx+dy)/2
    return (magnitude[:,3:]-magnitude[:,:3]).abs().mean(1,keepdim=True)


def windows(values,policy='retain_first'):
    b.require(policy in POLICIES,'unknown_policy')
    energy=boundary_energy(values)
    scores=t.nn.functional.avg_pool2d(energy,32,stride=1)[:,0]
    original=ORIGINAL_WINDOWS(values);result=[]
    yy,xx=t.meshgrid(t.arange(97,device=values.device),t.arange(161,device=values.device),indexing='ij')
    for i,old in enumerate(original):
        if not old:result.append([]);continue
        selected=[old[0]] if policy=='retain_first' else []
        score=scores[i].clone()
        for _ in range(2-len(selected)):
            for x,y in selected:score[(xx<x+32)&(xx+32>x)&(yy<y+32)&(yy+32>y)]=-1
            peak=int(score.flatten().argmax())
            if float(score.flatten()[peak])<=0:break
            selected.append((peak%161,peak//161))
        # No gradient change does not establish unchanged focus. Keep the old views.
        result.append(selected if len(selected)==2 else old)
    return result


def eligibility(summary):
    eligible=[]
    for policy in POLICIES:
        if all(summary[part][policy]['coverage']['mean']>=summary[part]['old']['coverage']['mean']+.02
               and summary[part][policy]['purity']['mean']>=summary[part]['old']['purity']['mean']-.02
               for part in ('all','content')):eligible.append(policy)
    return max(eligible,key=lambda k:summary['content'][k]['coverage']['mean']) if eligible else None


def audit():
    b.require(not (OUT/'audit.json').exists(),'output_collision');t.set_num_threads(2);start=time.monotonic()
    membership=b.read(b.PACKAGE/'membership.json');old=b.read(a.OUT/'audit.json')
    oldreg=b.read(b.checked(old['registration']));b.checked(oldreg['membership']);b.checked(oldreg['encoded'])
    oldrows={v['index']:v for v in old['rows']}
    values=np.load(b.PACKAGE/'native.npy',allow_pickle=False,mmap_mode='r');records=[]
    b.write(OUT/'registration.json',dict(version='regions331-audit-v1',source=b.ref(Path(__file__)),
        membership=b.ref(b.PACKAGE/'membership.json'),encoded=b.ref(b.PACKAGE/'native.npy'),prior=b.ref(a.OUT/'audit.json'),
        policies=list(POLICIES),smoothing=5,windowSize=32,count=2,role='train',
        supportRule='Mean coverage improves by 0.02 on all and content rows. Mean purity cannot fall by more than 0.02.',
        geometryIsDiagnosticOnly=True,trainingStarted=False))
    for i,row in enumerate(membership['rows']):
        if row['role']!='train':continue
        scenes,error=a.scenes_for(row);paired,_,error=a.bodies(row,scenes) if not error else (None,[],error)
        b.require(error is None,'missing_geometry')
        frames=[r.s.image(v['path'],v['sha256']) for v in row['images']]
        b.require(np.array_equal(r.s.encoded(*frames,(192,128))[0],values[i]),'source_encoding')
        delta=np.abs(np.asarray(frames[1],np.float32)/255-np.asarray(frames[0],np.float32)/255).mean(2)
        inner,band=a.masks(delta.shape,paired);part=t.from_numpy(np.array(values[i:i+1]));measurements={}
        for policy in POLICIES:
            selected=windows(part,policy)[0];mask=np.zeros(delta.shape,bool)
            for x,y in selected:
                x0,y0,x1,y1=a.source_window((x,y,x+32,y+32),frames[0].size)
                a.fill(mask,(x0,y0,x1-x0,y1-y0))
            measure=a.measure(delta,inner,band,mask)
            measurements[policy]=dict(windows=selected,coverage=measure['proposalBoundaryCoverage'],purity=measure['proposalBoundaryPurity'])
        measurements['old']=dict(windows=oldrows[i]['windows'],coverage=oldrows[i]['proposalBoundaryCoverage'],purity=oldrows[i]['proposalBoundaryPurity'])
        records.append(dict(index=i,id=row['id'],group=row['group'],conditions=row['conditions'],changed=row['changed'],measurements=measurements))
        if len(records)%100==0:print('Audited',len(records),flush=True)
    subsets={'all':records,'content':[v for v in records if 'content_contrast' in v['conditions']]}
    subsets.update({group:[v for v in records if v['group']==group] for group in sorted({v['group'] for v in records})})
    summary={part:{policy:{metric:c.summarize([v['measurements'][policy] for v in rows],metric)
        for metric in ('coverage','purity')} for policy in ('old',*POLICIES)} for part,rows in subsets.items()}
    selected=eligibility(summary)
    b.write(OUT/'audit.json',dict(registration=b.ref(OUT/'registration.json'),rows=records,summary=summary,
        selectedPolicy=selected,candidateJustified=selected is not None,seconds=time.monotonic()-start,rolesChanged=False))
    print({key:summary[key] for key in ('all','content')},flush=True);print('Selected',selected,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',required=True,action='store_true')
    parser.parse_args();audit()
