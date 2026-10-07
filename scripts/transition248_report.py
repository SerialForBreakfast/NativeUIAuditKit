"""Summarize the fixed comparison without selecting another training run."""
from datetime import datetime, timezone, timedelta
import numpy as np
import transition248 as run

t=run.t


def main():
    out=run.OUT;protocol=t.sealed(out/'protocol.json');complete=t.sealed(out/'completion.json')
    results={name:t.sealed(t.h.checked(t.h.ROOT,ref)) for name,ref in complete['results'].items()}
    rows=protocol['rows'];selected=protocol['selected'];held=protocol['held']
    groups=[protocol['components'][rows[i]['group']] for i in selected]
    y=np.array([rows[i]['changed'] for i in selected]);table={};mass={}
    for name,balanced in [('DTM066',False),('DTM067',True)]:
        r=results[name];w=run.weights(groups,668,balanced)[668:668+len(groups)]
        mass[name]=dict(native=float(w.sum()),changed=float(w[y==1].sum()),unchanged=float(w[y==0].sum()),
                        replay=668,reverseNative=float(w.sum()))
        table[name]={**{k:r['summary'][k] for k in ['reserved','development','original_capture','artwork_contrast']},
                     'fitting':r['fitting'],'trainingRoleHoldout':r['held'],
                     **{k:v['summary'] for k,v in r['regression'].items()}}
    a=np.array(results['DTM066']['probabilities']);b=np.array(results['DTM067']['probabilities'])
    truth=np.array([r['changed'] for r in rows]);da=t.p.decisions(a);db=t.p.decisions(b)
    differences=[dict(id=r['id'],role=r['role'],group=r['group'],changed=r['changed'],
                      control=float(a[i]),candidate=float(b[i])) for i,r in enumerate(rows) if da[i]!=db[i]]
    report=dict(table=table,weightMass=mass,decisionChanges=differences,
                gained=int(((da!=truth)&(db==truth)).sum()),lost=int(((da==truth)&(db!=truth)).sum()),
                trainingRoleHoldoutGroups=sorted({rows[i]['group'] for i in held}),
                completion=t.h.ref(out/'completion.json'),productionEligible=False,
                caveat='Group weighting also changes class mass. This comparison does not isolate those effects.')
    t.h.write(out/'comparison.json',report,sealed=True)
    now=datetime.now(timezone.utc)
    peer=dict(schema_version=1,id='nuiak-transition248-completed-v1',request_id='nuiak-coordination-priorities248-v1',
              **{'from':'NUIAK','to':['TVTestRig','joe-big-dog']},created_at=now.isoformat(),
              expires_at=(now+timedelta(days=7)).isoformat(),state='completed',
              message='The local matched sampling comparison is complete. No replacement model is offered.',
              results=table,limitations=['Retained Fixture cases, not real-app qualification.',
                                        'No capture or new runtime is needed for this completed comparison.'],
              next='Prioritize the existing adapter checks and exact receipts. Keep model experiments independent of service deployment.')
    t.h.write(out.parent/'coordination/model-result.json',peer)
    for name,values in table.items():print(name,{k:v['correct'] for k,v in values.items()})


if __name__=='__main__':main()
