"""Prepare a finite template qualification graph. Do not start or approve jobs."""
import argparse
import copy
from pathlib import Path
import shutil

import research_queue as q
import hcf_templates395 as t
from experiment_templates import pin


def build(folder,queue):
    folder.mkdir(parents=True,exist_ok=True)
    def save(name,value):
        path=folder/name
        if path.exists():q.require(q.load(path)==value,'preparation_changed:'+name)
        else:q.save(path,value)
        return pin(path)
    def dep(ident,*outputs):
        return dict(job=ident,specSHA256=q.text_digest(q.load(queue/'jobs'/ident/'spec.json')),outputs=list(outputs))
    def existing(ident,*outputs):
        q.require(queue==q.QUEUE,'native_dependencies_require_live_queue')
        return dep(ident,*outputs)
    def add(ident,template,inputs,parameters=None,dependencies=None,**extra):
        doc=dict(version='hcf-template-description-v1',id='template395-'+ident,owner='research-host-NUIAK',template=template,
            question='Does '+template+' produce verified outputs through the existing execution queue?',
            decision='Pass only verified outputs. Preserve failures. Do not accept or promote a model.',
            inputs=inputs,parameters=parameters or {},dependencies=dependencies or [],**extra)
        doc['id']=doc['id'].replace('template395-','template395r2-')
        save(ident+'-description.json',doc);t.register(doc,queue);return doc['id']
    def future(job,output):return dict(job=job,output=output)

    model=q.QUEUE/'jobs/hcf375c-70-crop-train/attempts/1/out/final.pt'
    review=copy.deepcopy(q.load(q.QUEUE/'jobs/hcf388-study-report/attempts/1/out/hcf-study-report.json'))
    review['models']={'crop-candidate':pin(model)}
    review['source']=pin(q.QUEUE/'jobs/hcf388-study-report/attempts/1/out/hcf-study-report.json')
    candidate=add('09-candidate','T09',dict(review=save('review.json',review),checkpoint=pin(model)),dict(method='crop-candidate'))
    environment=save('environment.json',dict(interpreter='.venv-coreml/bin/python',configuration=pin(q.ROOT/'.venv-coreml/pyvenv.cfg')))
    export=add('10-export','T10',dict(candidate=future(candidate,'candidate.json'),environment=environment),
        dict(experimentalID='hcf-template395',precision='fp16'),[dep(candidate,'candidate.json')])

    corpus=q.QUEUE/'jobs/hcf371r4-40-catalog/attempts/1/out/admission.json'
    catalog=q.load(corpus)
    add('01-inventory','T01',dict(catalog=pin(corpus)))
    policy=save('roles.json',dict(version='frozen-roles-v1',groups={r['group']:r['role'] for r in catalog['rows']}))
    add('02-groups','T02',dict(catalog=pin(corpus),policy=policy))
    # Copy 2 inspected development frames. Keep their original bytes and control bounds.
    selected=[r for r in sorted(catalog['rows'],key=lambda r:r['id']) if r['role']=='development'][:2]
    members=[]
    for index,row in enumerate(selected):
        source=Path(row['path']);q.require(q.digest(source)==row['sha256'],'source_image_changed')
        destination=folder/f'frame-{index}.png'
        if not destination.exists():shutil.copyfile(source,destination)
        q.require(q.digest(destination)==row['sha256'],'copy_changed')
        for control,bounds in row['boxes'].items():
            members.append(dict(id=row['id']+'-'+control,role=row['role'],group=row['group'],
                label=int(control==row['focus']),image=pin(destination),bounds=bounds))
    membership=save('runtime-membership.json',dict(version='focus-runtime-items-v1',rows=members))
    parity=add('11-parity','T11',dict(export=future(export,'export.json'),membership=membership),
        dependencies=[dep(export,'export.json')])
    runtime=add('12-runtime','T12',dict(export=future(export,'export.json'),membership=membership,
        parity=future(parity,'parity.json')),dict(repetitions=3),[dep(export,'export.json'),dep(parity,'parity.json')])
    license=q.ROOT/'LICENSE';q.require(license.is_file(),'license_missing')
    add('13-package','T13',dict(export=future(export,'export.json'),parity=future(parity,'parity.json'),
        runtime=future(runtime,'runtime.json'),license=pin(license)),dependencies=[dep(export,'export.json'),dep(parity,'parity.json'),dep(runtime,'runtime.json')])
    # Recheck retained native evidence without recapture. Full native capture is a separate job.
    add('04-admission','T04',{},dependencies=[existing('hcf371r4-10-part-000-capture','artifact.json')])
    # A tiny admitted subset tests production crop preparation and training plumbing.
    groups={role:next(r['group'] for r in catalog['rows'] if r['role']==role) for role in ('train','development')}
    tiny=[]
    for role,group in groups.items():
        for profile in ('standard','hcf'):
            tiny.append(next(r for r in catalog['rows'] if r['group']==group and r['profile']==profile))
    tiny_doc=dict(catalog,rows=tiny,cases=[c for c in catalog['cases'] if c['group'] in groups.values()])
    tiny_ref=save('tiny-admission.json',tiny_doc)
    tiny_policy=save('tiny-roles.json',dict(version='frozen-roles-v1',groups={r['group']:r['role'] for r in tiny}))
    frozen=add('02b-smoke-groups','T02',dict(catalog=tiny_ref,policy=tiny_policy))
    crops=add('05-crops','T05',dict(configuration=save('crops-config.json',dict(roles=['train','development'],destination='template395r2-crops'))),
        dependencies=[dep(frozen,'admission.json')])
    planned=[dict(id=r['id']+'-'+control,role=r['role'],group=r['group'],profile=r['profile'],label=int(control==r['focus']))
             for r in tiny for control in r['boxes']]
    membership_plan=save('training-membership.json',dict(version='crop-membership-plan-v1',rows=planned,source=tiny_ref))
    training=dict(experimentLogRunId='TEMPLATE395-SMOKE',membership=[membership_plan],initialization=pin(model),epochs=30,
        storageBudgetBytes=2<<30,acceptanceEvidence='Software qualification only. Require changed finite weights and complete history. Do not accept this tiny-data model.',resume='restart')
    add('06-training-smoke','T06',dict(configuration=save('training-config.json',dict(initialization=pin(model),profile='balanced',deduplicate=True,seed=371)),
        initialization=pin(model),membership=membership_plan),dependencies=[dep(crops,'crops.json')],training=training)
    base=q.load(q.ROOT/'Research/ResearchSpecs/HCF371-r4/r4-shard-000-plan.json')
    native_case=next(c for c in catalog['cases'] if c['role']=='development')
    native=dict(base,cases=[native_case],expectedFrames=8,shard='template395r2-native-pilot')
    recipe=save('native-plan.json',native)
    add('03-native-pilot','T03',dict(recipe=recipe),capture=dict(target=native['binding']['simulatorUDID'],
        endpoint=native['binding']['endpoint'],plan=recipe,approval='Maintainer requests bounded native template qualification, 2026-10-14.'))
    records=[p.name for p in sorted((queue/'jobs').iterdir()) if p.name.startswith('template395r2-')]
    save('batch.json',dict(jobs=records,modelAccepted=False,
        outstanding=['T03 native pilot needs fresh target ownership.',
                     'T05/T06 need a frozen bounded training sample.',
                     'T07/T08 retain their existing qualification.',
                     'T14 live verification needs a returned TTR receipt.']))
    return records


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',type=Path);parser.add_argument('--queue',type=Path,default=q.QUEUE)
    args=parser.parse_args();print(build(args.folder.absolute(),args.queue.absolute()))
