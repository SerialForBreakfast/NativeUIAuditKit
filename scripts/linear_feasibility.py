"""Minimum-infinity-norm margin witness, with original-space validation."""
import math
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, eye, hstack, vstack

TARGET=math.log(.85/.15)+.001


def solve(features,labels,time_limit=60):
    x=np.asarray(features,dtype=np.float64);y=np.asarray(labels,dtype=np.float64)
    if x.ndim!=2 or x.shape[1]<2 or len(x)==0 or y.shape!=(len(x),) or not np.isfinite(x).all() or not np.isin(y,[0,1]).all():
        raise ValueError('feasibility_inputs')
    if not math.isfinite(time_limit) or time_limit<=0 or time_limit>60:raise ValueError('solver_budget')
    signs=2*y-1;A=-signs[:,None]*x[:,1:];b=signs*x[:,0]-TARGET;n=x.shape[1]-1
    scale=np.maximum(1,np.maximum(np.max(np.abs(A),axis=1),np.abs(b)))
    matrix=vstack([hstack([csr_matrix(A/scale[:,None]),csr_matrix((len(x),1))]),
                   hstack([eye(n),-np.ones((n,1))]),hstack([-eye(n),-np.ones((n,1))])],format='csr')
    rhs=np.concatenate([b/scale,np.zeros(2*n)]);objective=np.zeros(n+1);objective[-1]=1
    result=linprog(objective,A_ub=matrix,b_ub=rhs,bounds=[(None,None)]*n+[(0,None)],method='highs-ds',
        options=dict(time_limit=time_limit,primal_feasibility_tolerance=1e-8,dual_feasibility_tolerance=1e-8))
    report=dict(status=int(result.status),message=result.message,iterations=int(result.nit),
                solverSuccess=bool(result.success),feasibleWitness=False,constraints=len(x),dimensions=n)
    if result.success:
        w=result.x[:-1];violation=float(np.max(A@w-b));norm=float(np.max(np.abs(w)))
        valid=np.isfinite(w).all() and math.isfinite(violation) and violation<=1e-6 and norm<=result.x[-1]+1e-6
        report.update(feasibleWitness=bool(valid),maxViolation=violation,infinityNorm=norm,objective=float(result.fun))
        return report,w if valid else None
    return report,None
