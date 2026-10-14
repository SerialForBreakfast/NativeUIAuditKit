"""Diagnostic inset correction fitted outside each evaluated scene group."""
import copy
import statistics
import time
import research_queue as q
from template_adapters395 import document,resolve_inputs

OUT=None


def correct(proposals,geometry):
    rows=geometry['rows'];result=copy.deepcopy(proposals);fits=[]
    indexed={r['id']:r for r in rows}
    q.require(len(indexed)==len(rows) and set(indexed)=={r['id'] for r in result['rows']},'correction_membership')
    for row in result['rows']:
        target=indexed[row['id']]
        q.require(row['role'] in ('development','retained') and all(row[k]==target[k] for k in ('role','profile','group')),'correction_identity')
        eligible=[r for r in rows if r['role']=='development' and r['profile']==row['profile']
                  and r['group']!=row['group'] and 'ringInsetsPixels' in r]
        groups=sorted({r['group'] for r in eligible});offsets=None
        if len(groups)>=3:
            # Equal group influence prevents repeated frames from controlling the fit.
            medians=[[statistics.median(r['ringInsetsPixels'][i] for r in eligible if r['group']==g)
                      for i in range(4)] for g in groups]
            offsets=[statistics.median(r[i] for r in medians) for i in range(4)]
        boxes=[]
        for box in row['prediction']['candidates']:
            if offsets is None:boxes.append(box);continue
            x,y,w,h=box;left,top,right,bottom=offsets
            changed=[x-left,y-top,w+left+right,h+top+bottom]
            # This study only contracts rings. Expansion needs a separate fixed hypothesis.
            if all(v<=0 for v in offsets) and changed[2]>0 and changed[3]>0:boxes.append(changed)
            else:boxes.append(box)
        row['prediction']['candidates']=boxes
        fits.append(dict(id=row['id'],excludedGroup=row['group'],fitGroups=groups,offsets=offsets,
                         corrected=offsets is not None and all(v<=0 for v in offsets)))
    result['method']='TTR-outer-ring-v2-group-excluded-insets'
    result['modelAccepted']=False
    result['limitation']='Development-fitted diagnostic only. Each target group is excluded. This is not a deployable calibrated mapping.'
    return result,fits


def run():
    contract=q.load(OUT.parents[2]/'spec.json')['template'];start=time.monotonic()
    try:
        inputs=resolve_inputs(contract,OUT)
        result,fits=correct(document(inputs['proposals']),document(inputs['geometry']))
        q.save(OUT/'comparison.json',result);q.save(OUT/'fit.json',dict(rows=fits,modelAccepted=False))
        q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
            dict(path=str(p.relative_to(OUT)),sha256=q.digest(p)) for p in sorted(OUT.rglob('*')) if p.is_file()]))
        q.save(OUT/'template-result.json',dict(execution='complete',modelAccepted=False,seconds=time.monotonic()-start))
    except Exception as error:
        q.save(OUT/'template-result.json',dict(execution='failed',code=str(error)[:500],modelAccepted=False));raise
