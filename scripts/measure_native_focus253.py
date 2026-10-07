"""Fit visible control growth from retained pairs without capture or training."""
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/work/TRANSITION-253/artifacts'


def checked(ref):
    path=ROOT/ref['path']
    if hashlib.sha256(path.read_bytes()).hexdigest()!=ref['sha256']:raise ValueError('changed_input')
    return path


def warp(image,parameters,center):
    sx,sy,dx,dy,gain,bias=parameters
    yy,xx=np.indices(image.shape[:2],dtype=np.float64)
    coords=[(yy-center[1]-dy)/sy+center[1],(xx-center[0]-dx)/sx+center[0]]
    return np.clip(np.stack([map_coordinates(image[:,:,c],coords,order=1,mode='nearest') for c in range(3)],-1)*gain+bias,0,1)


def metrics(pred,target,mask):
    error=np.abs(pred[mask]-target[mask])
    return dict(meanAbsolute255=float(error.mean()*255),rmse255=float(np.sqrt(np.mean(error**2))*255),
                differingPixelFraction=float(np.any(np.rint(pred[mask]*255)!=np.rint(target[mask]*255),axis=1).mean()))


def prepare(row,regions=False):
    images=[np.asarray(Image.open(checked(ref)).convert('RGB'),dtype=np.float64)/255 for ref in row['images']]
    if images[0].shape!=images[1].shape:raise ValueError('dimensions')
    docs=[json.loads(checked(ref).read_text()) for ref in row['metadata']]
    scenes=[]
    for doc,ref in zip(docs,row['images']):
        scenes.append(next(doc[key] for key,hashkey in [('baseline_scene','unfocused_sha256'),('focused_scene','focused_sha256')]
                           if doc[hashkey]==ref['sha256']))
    target=scenes[1]['focused_element_id']
    if scenes[0]['recipe']['recipe_hash']!=scenes[1]['recipe']['recipe_hash']:
        raise ValueError('recipe_changed')
    if scenes[0]['fixture_run_id']!=scenes[1]['fixture_run_id']:raise ValueError('instance_changed')
    if any((s['scene_height'],s['scene_width'])!=images[0].shape[:2] for s in scenes):
        raise ValueError('scene_dimensions')
    elements=[next(e for e in scene['elements'] if e['element_id']==target) for scene in scenes]
    if elements[0]['is_focused'] or not elements[1]['is_focused']:raise ValueError('focus_labels')
    for scene in scenes:
        if not scene['is_settled'] or not scene['focus_observation']['verified']:raise ValueError('observation')
    boxes=[np.asarray(e['rendered_body_geometry']['full_pixel_bounds'],float) for e in elements]
    a,b=boxes;center=a[:2]+a[2:]/2
    margin=max(a[2:])*.25
    x0,y0=np.floor(a[:2]-margin).astype(int);x1,y1=np.ceil(a[:2]+a[2:]+margin).astype(int)
    height,width=images[0].shape[:2]
    if x0<0 or y0<0 or x1>width or y1>height:raise ValueError('edge_crop')
    cropped=[im[y0:y1,x0:x1] for im in images]
    center=center-[x0,y0]
    yy,xx=np.indices(cropped[0].shape[:2]);visible=np.asarray(elements[1]['rendered_body_geometry']['visible_pixel_bounds'])
    # The interior test excludes borders and shadows. It does not qualify those effects.
    inset=.15*min(visible[2:]);vx,vy,vw,vh=visible
    mask=(xx+x0>vx+inset)&(xx+x0<vx+vw-inset)&(yy+y0>vy+inset)&(yy+y0<vy+vh-inset)
    if mask.sum()<100:raise ValueError('support')
    geometry=dict(scaleX=float(b[2]/a[2]),scaleY=float(b[3]/a[3]),
                  centerShift=(b[:2]+b[2:]/2-(a[:2]+a[2:]/2)).tolist())
    if regions:
        offset=np.array([x0,y0,0,0])
        return cropped,center,mask,geometry,dict(before=a-offset,after=b-offset,visible=visible-offset,
            clipping=elements[1]['rendered_body_geometry']['clipping'])
    return cropped,center,mask,geometry


def run():
    if OUT.exists():raise ValueError('output_collision')
    start=time.monotonic();OUT.mkdir(parents=True)
    member=ROOT/'reports/work/TRANSITION-249/artifacts/package/membership.json'
    rows=json.loads(member.read_text())['rows']
    selected=[r for r in rows if r['group'] in ('233:recipe-00','233:recipe-03') and r['changed'] and 'original_capture' in r['conditions']]
    if len(selected)!=8 or any(r['role']!='train' for r in selected):raise ValueError('membership')
    selected.sort(key=lambda r:(r['group'],r['id']))
    fitted=[];results=[]
    for index,row in enumerate(selected):
        (before,after),center,mask,geometry=prepare(row)
        fitting=row['group']=='233:recipe-00'
        if fitting:
            small=before[::4,::4];target=after[::4,::4];chosen=mask[::4,::4]
            def residual(p):return (warp(small,p,center/4)[chosen]-target[chosen]).flatten()
            fit=least_squares(residual,[1.1,1.1,0,0,1,0],
                bounds=([1,1,-8,-8,.6,-.3],[1.35,1.35,8,8,1.4,.3]),
                diff_step=1e-3,max_nfev=60)
            params=fit.x.copy();params[2:4]*=4;fitted.append(params)
        else:params=np.median(fitted,axis=0)
        predicted=warp(before,params,center)
        result=dict(id=row['id'],group=row['group'],role='parameter_fit' if fitting else 'training_role_diagnostic_check',
            sourceImages=row['images'],sourceMetadata=row['metadata'],parameters=params.tolist(),observedGeometry=geometry,
            unchanged=metrics(before,after,mask),rendered=metrics(predicted,after,mask),pixels=int(mask.sum()),
            exactRepeat=bool(np.array_equal(predicted,warp(before,params,center))))
        results.append(result)
        if index in (0,4):
            panel=np.concatenate([before,after,predicted,np.minimum(np.abs(predicted-after)*4,1)],axis=1)
            Image.fromarray(np.rint(panel*255).astype('uint8')).save(OUT/f'comparison-{index}.png')
        print(index,result['role'],result['rendered'],flush=True)
    (OUT/'result.json').write_text(json.dumps(dict(version=1,seconds=time.monotonic()-start,
        membershipSHA256=hashlib.sha256(member.read_bytes()).hexdigest(),scriptSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        results=results,parameterOrder=['scaleX','scaleY','shiftX_pixels','shiftY_pixels','gain','bias'],
        scope='Interior geometry and color only. Shadows, edges, parallax and timing remain unmeasured. No independent native-app qualification.',
        productionEligible=False),indent=2))


def shade():
    destination=OUT/'shading.json'
    if destination.exists():raise ValueError('output_collision')
    report=json.loads((OUT/'result.json').read_text())
    rows=json.loads((ROOT/'reports/work/TRANSITION-249/artifacts/package/membership.json').read_text())['rows']
    lookup={r['id']:r for r in rows};params=np.median([r['parameters'] for r in report['results'][:4]],axis=0)
    matrices=[];targets=[];prepared=[]
    for r in report['results']:
        (before,after),center,mask,_=prepare(lookup[r['id']]);base=warp(before,params,center)
        yy,xx=np.indices(mask.shape,dtype=float);xx=(xx-center[0])/(mask.shape[1]/2);yy=(yy-center[1])/(mask.shape[0]/2)
        basis=np.stack([np.ones_like(xx),xx,yy,xx*yy,xx*xx,yy*yy],axis=-1)
        if r['role']=='parameter_fit':
            matrices.append(basis[mask][::4]);targets.append((after-base)[mask][::4])
        prepared.append((r,before,after,base,basis,mask))
    coefficients=np.linalg.lstsq(np.concatenate(matrices),np.concatenate(targets),rcond=None)[0]
    results=[]
    for index,(r,before,after,base,basis,mask) in enumerate(prepared):
        predicted=np.clip(base+basis@coefficients,0,1)
        results.append(dict(id=r['id'],role=r['role'],base=metrics(base,after,mask),shaded=metrics(predicted,after,mask)))
        if index==4:
            panel=np.concatenate([before,after,predicted,np.minimum(np.abs(predicted-after)*4,1)],axis=1)
            Image.fromarray(np.rint(panel*255).astype('uint8')).save(OUT/'shading-comparison.png')
    destination.write_text(json.dumps(dict(coefficientsRGB=coefficients.tolist(),parameters=params.tolist(),results=results,
        scope='Shared quadratic color residual fitted on recipe00 only. Interior diagnostic, not a physical lighting formula or shadow model.'),indent=2))
    print(json.dumps(results,indent=2))


def coordinates(shape,center):
    yy,xx=np.indices(shape,dtype=float)
    return (xx-center[0])/(shape[1]/2),(yy-center[1])/(shape[0]/2)


def highlight(base,x,y,parameters):
    """Blend a white elliptical highlight in decoded RGB space."""
    gain,bias,alpha,mx,my,sx,sy=parameters
    if not np.isfinite(parameters).all() or sx<=0 or sy<=0 or not 0<=alpha<=1:
        raise ValueError('invalid_highlight_parameters')
    weight=alpha*np.exp(-.5*(((x-mx)/sx)**2+((y-my)/sy)**2))
    color=np.clip(base*gain+bias,0,1)
    return np.clip(color*(1-weight[...,None])+weight[...,None],0,1)


def formula_members(rows):
    groups=('233:recipe-00','233:recipe-03','233:recipe-04','233:recipe-05')
    selected=[r for r in rows if r['group'] in groups and r['changed'] and 'original_capture' in r['conditions']]
    if any(r['role']!='train' for r in selected):raise ValueError('data_role')
    if any(sum(r['group']==g for r in selected)!=4 for g in groups):raise ValueError('membership')
    if len({r['id'] for r in selected})!=16:raise ValueError('duplicate_pair')
    return sorted(selected,key=lambda r:(r['group'],r['id']))


def compare_formulas():
    """Fit once on recipe 00. Report fixed formulas on other training recipes."""
    destination=OUT/'formula-r2'
    if destination.exists():raise ValueError('output_collision')
    start=time.monotonic()
    member=ROOT/'reports/work/TRANSITION-249/artifacts/package/membership.json'
    previous_path=OUT/'result.json'
    previous=json.loads(previous_path.read_text())
    if hashlib.sha256(member.read_bytes()).hexdigest()!=previous['membershipSHA256']:
        raise ValueError('changed_membership')
    fitting=[r for r in previous['results'] if r['role']=='parameter_fit']
    if len(fitting)!=4 or any(r['group']!='233:recipe-00' for r in fitting):raise ValueError('prior_fit_membership')
    geometry=np.median([r['parameters'] for r in fitting],axis=0)
    rows=formula_members(json.loads(member.read_text())['rows'])
    destination.mkdir()
    records=[];samples=[];poly_x=[];poly_y=[];failures=[]
    # Retain one crop per row. No full-frame arrays survive prepare().
    for row in rows:
        try:
            (before,after),center,mask,observed=prepare(row)
        except (ValueError,KeyError,StopIteration) as error:
            failures.append(dict(id=row['id'],reason=str(error)));continue
        raw=warp(before,[*geometry[:4],1,0],center)
        base=np.clip(raw*geometry[4]+geometry[5],0,1)
        x,y=coordinates(mask.shape,center)
        basis=np.stack([np.ones_like(x),x,y,x*y,x*x,y*y],axis=-1)
        fit=row['group']=='233:recipe-00'
        if fit:
            samples.append((raw[mask][::16],x[mask][::16],y[mask][::16],after[mask][::16]))
            poly_x.append(basis[mask][::16]);poly_y.append((after-base)[mask][::16])
        records.append((row,before,after,raw,base,x,y,basis,mask,observed))
    if len(samples)!=4:raise ValueError('incomplete_fit')
    raw,x,y,target=[np.concatenate([s[i] for s in samples]) for i in range(4)]
    coefficients=np.linalg.lstsq(np.concatenate(poly_x),np.concatenate(poly_y),rcond=None)[0]
    trials=[]
    for initial in ([1,0,.2,-.3,-.5,.5,.5],[.9,0,.4,0,-1,1,1]):
        fit=least_squares(lambda p:(highlight(raw,x,y,p)-target).ravel(),initial,
            bounds=([.6,-.2,0,-1.5,-1.5,.1,.1],[1.4,.2,.8,1.5,1.5,2,2]),
            max_nfev=100,diff_step=1e-3)
        trials.append(dict(initial=initial,parameters=fit.x.tolist(),cost=float(fit.cost),
            evaluations=fit.nfev,success=bool(fit.success),message=fit.message))
    winner=min(trials,key=lambda r:r['cost'])
    results=[]
    for row,before,after,raw,base,x,y,basis,mask,observed in records:
        outputs=dict(unchanged=before,globalColor=base,
            quadratic=np.clip(base+basis@coefficients,0,1),
            whiteHighlight=highlight(raw,x,y,winner['parameters']))
        scores={name:metrics(value,after,mask) for name,value in outputs.items()}
        results.append(dict(id=row['id'],group=row['group'],role='parameter_fit' if row['group']=='233:recipe-00' else 'development_check',
            sourceImages=row['images'],sourceMetadata=row['metadata'],pixels=int(mask.sum()),
            observedGeometry=observed,scores=scores,
            exactRepeat=bool(np.array_equal(outputs['whiteHighlight'],highlight(raw,x,y,winner['parameters'])))))
        if row['id']==next(r['id'] for r in rows if r['group']==row['group']):
            # Show only measured pixels. Black areas are excluded, not predictions.
            panels=[before,after,outputs['quadratic'],outputs['whiteHighlight'],np.minimum(abs(outputs['whiteHighlight']-after)*4,1)]
            panel=np.concatenate([np.where(mask[...,None],p,0) for p in panels],axis=1)
            Image.fromarray(np.rint(panel*255).astype('uint8')).save(destination/(row['group'].replace(':','-')+'.png'))
    summary={}
    for group in sorted({r['group'] for r in results}):
        subset=[r for r in results if r['group']==group]
        summary[group]={name:float(np.mean([r['scores'][name]['meanAbsolute255'] for r in subset])) for name in subset[0]['scores']}
    import scipy
    report=dict(version=2,seconds=time.monotonic()-start,geometry=geometry.tolist(),trials=trials,
        selectedParameters=winner['parameters'],quadraticCoefficients=coefficients.tolist(),
        parameterOrder=['gain','bias','alpha','centerX','centerY','widthX','widthY'],
        membershipSHA256=hashlib.sha256(member.read_bytes()).hexdigest(),
        previousResultSHA256=hashlib.sha256(previous_path.read_bytes()).hexdigest(),
        scriptSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        numpyVersion=np.__version__,scipyVersion=scipy.__version__,results=results,failures=failures,summary=summary,
        productionEligible=False,trainingAdmission=False,
        scope='Decoded RGB interior only. No shadow, border, animation, parallax, or independent real-app qualification.')
    (destination/'result.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(summary=summary,seconds=report['seconds'],failures=failures,trials=trials),indent=2))


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--shade',action='store_true');mode.add_argument('--compare-formulas',action='store_true');args=parser.parse_args()
    if args.compare_formulas:compare_formulas()
    elif args.shade:shade()
    else:run()
