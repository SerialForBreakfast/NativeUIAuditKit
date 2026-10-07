"""Make case-linked feedback from completed, fixed experiment results."""
import argparse
import numpy as np
import transition245 as t


def category(name,rows,probabilities,proposal,domain):
    labels=np.asarray([r['changed'] for r in rows])
    models={key:t.n.w.summary(np.asarray(value),labels) for key,value in probabilities.items()}
    wrong=set()
    for value in probabilities.values():
        wrong.update(np.flatnonzero(t.p.decisions(np.asarray(value))!=labels).tolist())
    examples=[]
    for i in sorted(wrong)[:5]:
        examples.append(dict(id=rows[i]['id'],role=rows[i]['role'],group=rows[i]['group'],changed=int(labels[i]),
                            source=rows[i].get('source','retained-authored'),
                            imageHashes=[v['sha256'] for v in rows[i].get('images',[])],
                            metadataHashes=[v['sha256'] for v in rows[i].get('metadata',[])],
                            probabilities={k:float(v[i]) for k,v in probabilities.items()}))
    return dict(name=name,support=len(rows),models=models,examples=examples,proposal=proposal,domain=domain,
                independentTrials=False,groupCount=len({r['group'] for r in rows}))


def feedback(rows,runs,baseline):
    probabilities={k:np.asarray(v['probabilities']) for k,v in runs.items()}
    probabilities['DTM054']=np.asarray(runs['DTM063']['initializerProbabilities'])
    categories=[]
    for name,select,proposal in [
        ('artwork_without_focus_change',lambda r:'artwork_contrast' in r['conditions'] and not r['changed'],
         'Keep focus fixed while varying artwork inside controls. Use new training artwork, not these development assets.'),
        ('training_content_without_focus_change',lambda r:'content_contrast' in r['conditions'] and not r['changed'],
         'Reuse current controls first. More copies cannot repair a failure to fit these existing cases.'),
        ('reserved_focus_changes',lambda r:r['role']=='reserved' and r['changed']==1,
         'Preserve these cases outside training. New related variations stay in the same protected family.'),
        ('original_native_focus_changes',lambda r:'original_capture' in r['conditions'] and r['changed']==1,
         'Separate missed focus cues from artwork responses before collecting more scenes.')]:
        ids=[i for i,r in enumerate(rows) if select(r)]
        categories.append(category(name,[rows[i] for i in ids],{k:v[ids] for k,v in probabilities.items()},proposal,'native_fixture'))
    for name in ('left8','center8','global8'):
        values={k:np.asarray(v['regression'][name]['probabilities']) for k,v in runs.items()}
        values['DTM054']=np.asarray(baseline[name]['probabilities'])
        cases=[dict(id=f'{name}:{i}',role='retained_diagnostic',group='retained-authored-family',changed=0)
               for i in range(len(values['DTM054']))]
        categories.append(category(name,cases,values,
            'Preserve this regression check. Native efficacy needs separately labeled controls, not these authored scores.',
            'authored_regression'))
    # Keep severity ordering explicit instead of ranking incompatible rates together.
    return dict(version='transition245-feedback-v1',categories=categories,
                ordering='Artwork repair first, reserved decisions next, then retained regression conditions. Rates are not pooled.',
                scope='Focus change only. No temporal readiness or navigation authority claim.',
                overlap='Categories can overlap. Do not sum their support.',productionEligible=False)


def run():
    destination=t.OUT/'feedback.json'
    t.p.review.require(not destination.exists(),'output_collision')
    complete=t.sealed(t.OUT/'completion.json')
    runs={k:t.sealed(t.h.checked(t.h.ROOT,ref)) for k,ref in complete['results'].items()}
    rows=t.sealed(t.OUT/'membership.json')['rows'];baseline=t.sealed(t.OUT/'baseline-regression.json')
    result=feedback(rows,runs,baseline)
    result['results']=complete['results'];result['source']=t.h.ref(__file__)
    t.h.write(destination,result,sealed=True)
    for entry in result['categories']:print(entry['name'],entry['models'])


if __name__=='__main__':
    argparse.ArgumentParser().parse_args();run()
