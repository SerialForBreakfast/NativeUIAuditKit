"""Queue the received TTR proposal kernel and dependent retained comparisons."""
import argparse
import research_queue as q
import research_approval as approval
import hcf_templates395 as templates
from template_inputs398 import pin


def build():
    folder=q.ROOT/'reports/work/HCF398'; base=folder/'source/outer-ring-v2-source'
    original=q.load(q.ROOT/'reports/work/HCF397/01-proposals.json')['inputs'];jobs=[]
    def add(name,template,question,decision,inputs,parameters=None,dependencies=None):
        doc=dict(version='hcf-template-description-v1',id='hcf398-'+name,owner='research-host-NUIAK',template=template,
            question=question,decision=decision,inputs=inputs,parameters=parameters or {},dependencies=dependencies or [])
        path=folder/(name+'.json')
        if path.exists():q.require(q.load(path)==doc,'immutable_description')
        else:q.save(path,doc)
        templates.register(doc);jobs.append(doc['id']);return doc['id']
    def dep(job,output):
        return dict(job=job,specSHA256=q.text_digest(q.load(q.QUEUE/'jobs'/job/'spec.json')),outputs=[output])
    producer=add('outer-ring-proposals','T25','Which retained controls receive TTR outer-ring-v2 proposals?',
        'Preserve exact kernel outputs and abstentions. Never reinterpret ring bounds as verified body bounds.',
        dict(catalog=original['catalog'],retained=original['retained'],membership=original['rules'],
             sourceManifest=pin(base/'manifest.json'),kernel=pin(base/'TVTestRig/TVTestRig/Services/HCFOuterRingDetector.swift'),
             geometry=pin(base/'TVTestRig/TVTestRig/Domain/AutomationRecords.swift'),
             errors=pin(base/'TVTestRig/TVTestRig/Domain/Errors.swift'),driver=pin(q.MODULES/'OuterRing398.swift')))
    rules=dict(job=producer,output='comparison.json');producer_dep=dep(producer,'comparison.json')
    selection=add('outer-ring-crop','T18','Does the fixed crop model benefit from TTR ring proposals?',
        'Measure selection with unchanged crops and thresholds. This is a ring-box diagnostic, not qualified body geometry.',
        dict(original,rules=rules,membership=original['rules']),dependencies=[producer_dep])
    selected=dict(job=selection,output='proposal-selection.json');selection_dep=dep(selection,'proposal-selection.json')
    for source,name,label in [('hcf397-01-proposals','proposal-selection.json','original-proposals'),
                              ('hcf388-detector-evaluate','comparison.json','detector'),
                              ('hcf375c-80-crop-evaluate','comparison.json','known-box-upper-bound')]:
        add('outer-ring-vs-'+label,'T15','Which '+label+' successes survive TTR ring proposals plus crop scoring?',
            'Report matched gains and losses by profile. Preserve Standard and reject replacement when successes are lost.',
            dict(baseline=pin(q.QUEUE/'jobs'/source/'attempts/1/out'/name),candidate=selected),
            dict(comparison=label+' versus TTR outer-ring proposals plus crop scoring'),[selection_dep])
    add('outer-ring-failure-audit','T20','Are TTR proposal misses caused by missing rings or rejected matching crops?',
        'Separate missing geometry from score errors before any new training.',
        dict(catalog=original['catalog'],retained=original['retained'],rules=rules,selection=selected),
        dependencies=[producer_dep,selection_dep])
    q.save(folder/'outer-ring-batch.json',dict(jobs=jobs,standardChanged=False,modelAccepted=False))
    return jobs


def repair():
    folder=q.ROOT/'reports/work/HCF398';jobs=[]
    old='hcf398-outer-ring-crop';new=old+'-v2'
    producer=q.QUEUE/'jobs/hcf398-outer-ring-proposals/attempts/1'
    result=q.load(producer/'result.json');q.require(result['status']=='complete','producer_incomplete')
    rules=pin(producer/'out/comparison.json')
    q.require(any(r['path']=='comparison.json' and r['sha256']==rules['sha256'] for r in result['outputs']),'producer_changed')
    for name in ('outer-ring-crop','outer-ring-vs-original-proposals','outer-ring-vs-detector',
                 'outer-ring-vs-known-box-upper-bound','outer-ring-failure-audit'):
        doc=q.load(folder/(name+'.json'));doc['id']+='-v2'
        if 'rules' in doc['inputs']:doc['inputs']['rules']=rules
        doc['dependencies']=[d for d in doc['dependencies'] if d['job']!='hcf398-outer-ring-proposals']
        for ref in doc['inputs'].values():
            if ref.get('job')==old:ref['job']=new
        for dependency in doc['dependencies']:
            if dependency['job']==old:
                dependency['job']=new
                dependency['specSHA256']=q.text_digest(q.load(q.QUEUE/'jobs'/new/'spec.json'))
        path=folder/(name+'-v2.json')
        if path.exists():q.require(q.load(path)==doc,'immutable_repair')
        else:q.save(path,doc)
        templates.register(doc);jobs.append(doc['id'])
    q.save(folder/'outer-ring-repair-batch.json',dict(jobs=jobs,reason='Original adapter counted full catalog, not retained proposal membership.',modelAccepted=False))
    return jobs


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--approve',action='store_true');parser.add_argument('--repair',action='store_true');args=parser.parse_args()
    for job in (repair() if args.repair else build()):
        if args.approve:approval.approve(q.QUEUE,job,'agent:research-host-NUIAK',
            'Maintainer approves retained TTR proposal comparisons. No capture, training, Standard change, or navigation authority.')
        print(job,flush=True)
