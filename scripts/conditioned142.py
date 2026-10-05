"""Equivalent scaled LP diagnosis; original-coordinate objective and runtime gates."""
import argparse
import math
import os
from pathlib import Path
import time
import numpy as np
import scipy
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, diags, hstack, vstack
import feasible140 as previous

a,h,d,c,j=previous.a,previous.h,previous.d,previous.c,previous.j
TARGET=previous.lp.TARGET


def preserve_coefficients(matrix,rhs,threshold=1e-9):
    matrix=matrix.tocsr();minimum=np.full(matrix.shape[0],np.inf)
    for i in range(matrix.shape[0]):
        values=np.abs(matrix.data[matrix.indptr[i]:matrix.indptr[i+1]])
        values=values[values!=0]
        if len(values):minimum[i]=values.min()
    factor=np.maximum(1,10*threshold/minimum)
    if not np.isfinite(factor).all() or factor.max()>1e8:raise ValueError('coefficient_amplification')
    result=diags(factor)@matrix;right=rhs*factor
    nonzero=np.abs(result.data[result.data!=0])
    if not np.isfinite(nonzero).all() or not np.isfinite(right).all() or np.max(np.abs(right))>1e12 or nonzero.max()>1e12 or nonzero.min()<=threshold:
        raise ValueError('coefficient_range')
    return result,right,factor


def solve(features,labels,time_limit=60,strict=False,preserve=False,margin=TARGET):
    x=np.asarray(features,dtype=np.float64);y=np.asarray(labels,dtype=np.float64)
    if x.ndim!=2 or x.shape[1]<2 or not len(x) or y.shape!=(len(x),) or not np.isfinite(x).all() or not np.isin(y,[0,1]).all():
        raise ValueError('feasibility_inputs')
    if not math.isfinite(time_limit) or not 0<time_limit<=60:raise ValueError('solver_budget')
    if type(strict) is not bool:raise ValueError('strict_mode')
    if type(preserve) is not bool or preserve and not strict:raise ValueError('preserve_mode')
    if not math.isfinite(margin) or margin<TARGET:raise ValueError('weakened_margin')
    signs=2*y-1;A=-signs[:,None]*x[:,1:];b=signs*x[:,0]-margin
    rows=np.any(A!=0,axis=1);columns=np.any(A!=0,axis=0)
    report=dict(constraints=len(x),dimensions=x.shape[1]-1,zeroRows=int((~rows).sum()),
                zeroColumns=int((~columns).sum()),feasibleWitness=False,method='highs-ipm')
    if np.any(b[~rows]<0):
        return dict(report,status=2,message='Exactly zero row violates target',solverSuccess=False,iterations=0),None
    if not columns.any():
        return dict(report,status=0,message='All constraints satisfied at zero',solverSuccess=True,
                    iterations=0,feasibleWitness=True,maxViolation=float((-b).max()),infinityNorm=0.,objective=0.),np.zeros(x.shape[1]-1)
    active=A[rows][:,columns];scale=np.linalg.norm(active,axis=0)
    if not np.isfinite(scale).all() or np.any(scale<=0):raise ValueError('column_scale')
    scaled=active/scale;rhs=b[rows]
    row_scale=np.maximum(1,np.maximum(np.max(np.abs(scaled),axis=1),np.abs(rhs)))
    n=len(scale);inverse=diags(1/scale)
    # u = scale*w. The norm bounds must use inverse scale, not |u| <= t.
    matrix=vstack([hstack([csr_matrix(scaled/row_scale[:,None]),csr_matrix((len(rhs),1))]),
                   hstack([inverse,-np.ones((n,1))]),hstack([-inverse,-np.ones((n,1))])],format='csr')
    objective=np.zeros(n+1);objective[-1]=1
    rhs_full=np.concatenate([rhs/row_scale,np.zeros(2*n)])
    if preserve:
        from scipy.optimize._highspy._core import HighsOptions
        threshold=HighsOptions().small_matrix_value
        if threshold!=1e-9:raise ValueError('solver_threshold_changed')
        matrix,rhs_full,factor=preserve_coefficients(matrix,rhs_full,threshold)
        report.update(smallMatrixValue=threshold,minimumSolverCoefficient=float(np.abs(matrix.data[matrix.data!=0]).min()),
                      maximumRowAmplification=float(factor.max()))
    tolerance=1e-10 if strict else 1e-8
    result=linprog(objective,A_ub=matrix,b_ub=rhs_full,
        bounds=[(None,None)]*n+[(0,None)],method='highs-ipm',options=dict(time_limit=time_limit,
        primal_feasibility_tolerance=tolerance,dual_feasibility_tolerance=tolerance,ipm_optimality_tolerance=tolerance))
    report.update(status=int(result.status),message=result.message,solverSuccess=bool(result.success),
                  iterations=int(result.nit),columnScaleMin=float(scale.min()),columnScaleMax=float(scale.max()),tolerance=tolerance)
    if result.x is None or not np.isfinite(result.x).all():return report,None
    w=np.zeros(x.shape[1]-1);w[columns]=result.x[:-1]/scale
    residual=A@w-b;violation=float(np.max(residual));norm=float(np.max(np.abs(w)))
    report.update(candidateWeights=w.tolist(),originalResiduals=residual.tolist(),
                  scaledResiduals=(residual[rows]/row_scale).tolist(),activeRowIndices=np.flatnonzero(rows).tolist(),
                  worstRow=int(np.argmax(residual)))
    valid=bool(result.success and np.isfinite(w).all() and math.isfinite(violation) and violation<=1e-6 and norm<=result.x[-1]+1e-6)
    report.update(feasibleWitness=valid,maxViolation=violation,infinityNorm=norm,objective=float(result.fun))
    return report,w if valid else None


def global_admission(cache):
    import adapt_reflow117 as source
    path=h.ROOT/'reports/work/GLOBAL-REPLAY-146/admission.json';role=h.read(path)
    h.require(role['version']=='global146-admission-v1' and role['decision']=='approved_local_exposed_robustness_training'
              and role['role']=='train' and role['cache']=='global8' and role['count']==226
              and role['changed'] is False and role['independent_evaluation'] is False
              and role['external_transfer'] is False and role['indices']==dict(start_inclusive=207,end_exclusive=433),'global_role')
    _,_,pixels,labels,_=source.inputs()
    h.require(j.hashlib.sha256(pixels.tobytes()).hexdigest()==role['source_tensor_sha256']
              and np.array_equal(pixels[207:,:3],pixels[207:,3:]) and (labels[207:]==0).all(),'global_identity_source')
    h.require(cache['global8'].shape==(433,1153) and np.isfinite(cache['global8']).all(),'global_features')
    return path,cache['global8'][207:]


def run(ready,strict=False,preserve=False,global_replay=False):
    started=time.monotonic();out=h.fresh(ready)
    p,cache,ref,families,prior,labels,z,y,guard,truth,ids=a.inputs()
    native=sum(families.values(),[])
    ny=np.asarray([0 if i in families['identical_control'] else 1 for i in native],np.float32)
    x=np.concatenate([guard,cache['peer'][native]]);target=np.concatenate([truth,ny])
    h.require(x.shape==(993,1153) and len(set(native))==9,'witness_membership')
    old=c.audit.sealed(h.ROOT/'reports/work/FEASIBILITY-140/artifacts/ready/protocol.json')
    hashes=dict(featuresSHA256=j.hashlib.sha256(x.tobytes()).hexdigest(),labelsSHA256=j.hashlib.sha256(target.tobytes()).hexdigest())
    h.require(all(old[k]==v for k,v in hashes.items()) and old['baseline']==prior['model'],'problem_changed')
    h.require(not preserve or strict,'preserve_requires_strict')
    role=None;margin=TARGET
    if global_replay:
        h.require(strict and preserve,'global_requires_preservation')
        role,extra=global_admission(cache);x=np.concatenate([x,extra]);target=np.concatenate([target,np.zeros(226,np.float32)])
        margin=math.log(.85/.15)+.01
        hashes=dict(featuresSHA256=j.hashlib.sha256(x.tobytes()).hexdigest(),labelsSHA256=j.hashlib.sha256(target.tobytes()).hexdigest())
    experiment='DTM043' if preserve else ('DTM042' if strict else 'DTM041')
    title='COEFFICIENT-REPLAY-144' if preserve else ('NUMERICAL-REPLAY-143' if strict else 'CONDITIONED-FEASIBILITY-142')
    if global_replay:experiment,title='DTM046','GLOBAL-REPLAY-146'
    h.require(f'{experiment} — {title}' in (h.ROOT/'Research/ExperimentLog.md').read_text(),'unlogged')
    name='global146-dtm046' if global_replay else ('coefficient144-dtm043' if preserve else ('numerical143-dtm042' if strict else 'conditioned142-dtm041'))
    run_dir=d.a.r.d.old.fresh_run(name);out.mkdir(parents=True);run_dir.mkdir(parents=True)
    h.write(out/'protocol.json',dict(version='conditioned142-v1',source=h.ref(__file__),adapter=h.ref(previous.__file__),
        parent=h.ref(a.PARENT),admission=h.ref(j.a.ADMISSION),globalAdmission=h.ref(role) if role else None,baseline=prior['model'],problem=hashes,
        configuration=dict(solver='highs-ipm',scipy=scipy.__version__,timeLimit=60,target=margin,runtimeTarget=TARGET,globalReplay=global_replay,strict=strict,preserveCoefficients=preserve,tolerance=1e-10 if strict else 1e-8,
                           objective='original-coordinate-min-infinity-norm'),independentEvaluation=False),sealed=True)
    h.write(run_dir/'execution.json',dict(experiment=experiment,pid=os.getpid(),protocol=h.ref(out/'protocol.json'),
        authority='Standing local training; one assigned conditioned feasibility comparison',status='started'),sealed=True)
    tick=time.monotonic();report,w=solve(x,target,strict=strict,preserve=preserve,margin=margin);seconds=time.monotonic()-tick
    records={};checks={};model=None
    if w is not None:
        torch=d.a.r.d.torch_runtime();net=d.model()
        net.change.linear.weight.data.copy_(torch.from_numpy(w.astype(np.float32)[None]))
        torch.save(dict(version='conditioned142-v1',correction=net.change.linear.weight.detach().clone(),
                        baseline=prior['model'],protocol=h.ref(out/'protocol.json')),run_dir/'last.pt')
        model=h.ref(run_dir/'last.pt');saved=torch.load(run_dir/'last.pt',weights_only=True,map_location='cpu');replay=d.model()
        replay.change.linear.weight.data.copy_(saved['correction'])
        with torch.inference_mode():
            margins=(2*target-1)*net.change(torch.from_numpy(x)).flatten().numpy()
            checks=dict(float32MinimumMargin=float(margins.min()),float32GatesPassed=bool((margins>=TARGET-1e-6).all()),
                        float32DecisionMarginsPassed=bool((margins>=math.log(.85/.15)).all()))
            for name,f in cache.items():
                tx=torch.from_numpy(f);logits=net.change(tx)
                probs=logits.sigmoid().flatten().numpy() if name=='peer' else d.probabilities(logits)
                again=replay.change(tx).sigmoid().flatten().numpy() if name=='peer' else d.probabilities(replay.change(tx))
                h.require(np.array_equal(probs,again),'witness_replay')
                if name=='peer':records[name]=[dict(v,probability=float(q),decision=c.decision(float(q))) for v,q in zip(p['peer'],probs)]
                else:records[name]=dict(probabilities=probs.tolist(),summary=d.q.summarize(probs,labels,p['groups'],ref[name]))
        checks['identityUnchanged']=bool(np.array_equal(np.asarray(records['original']['probabilities'],np.float32)[207:],ref['original'][207:]))
        pp=d.q.decisions(np.asarray([r['probability'] for r in records['peer']]))
        checks['native']={k:dict(count=len(ii),correct=int((pp[ii]==(0 if k=='identical_control' else 1)).sum())) for k,ii in families.items()}
        checks['originalRetained']=all(v['correct']==v['count'] for v in records['original']['summary'].values())
        checks['contrastRetained']={k:bool(np.all(d.q.decisions(np.asarray(records[k]['probabilities']))[ii]==labels[ii])) for k,ii in ids.items()}
    h.write(run_dir/'result.json',dict(experiment=experiment,protocol=h.ref(out/'protocol.json'),solver=report,
        checks=checks,records=records,model=model,solveSeconds=seconds,seconds=time.monotonic()-started,
        independentEvaluation=False,productionEligible=False),sealed=True)
    h.require(sum(v.stat().st_size for v in run_dir.rglob('*') if v.is_file())<2*1024**3,'output_budget')
    print({k:v for k,v in report.items() if k not in ('candidateWeights','originalResiduals','scaledResiduals','activeRowIndices')},checks,'solveSeconds',seconds,flush=True)
    print({k:{g:v['correct'] for g,v in r['summary'].items()} for k,r in records.items() if k!='peer'},flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--ready',type=Path,required=True);parser.add_argument('--strict',action='store_true');parser.add_argument('--preserve-coefficients',action='store_true')
    parser.add_argument('--global-replay',action='store_true')
    args=parser.parse_args();run(args.ready,args.strict,args.preserve_coefficients,args.global_replay)
