"""Prepare one fixed mapping and separate-group comparisons through existing templates."""
import argparse
import research_queue as q
import research_approval as approval
import hcf_templates395 as templates
from template_inputs398 import pin


def build():
    folder=q.ROOT/'reports/work/HCF401';folder.mkdir(parents=True,exist_ok=True);jobs=[]
    def save(path,value):
        if path.exists():q.require(q.load(path)==value,'immutable_description')
        else:q.save(path,value)
    def output(job,name):
        attempt=q.QUEUE/'jobs'/job/'attempts/1';result=q.load(attempt/'result.json')
        q.require(result['status']=='complete','producer_incomplete');ref=pin(attempt/'out'/name)
        q.require(any(r['path']==name and r['sha256']==ref['sha256'] for r in result['outputs']),'producer_changed')
        return ref
    def add(name,template,question,decision,inputs,parameters=None,dependencies=None):
        doc=dict(version='hcf-template-description-v1',id='hcf401-'+name,owner='research-host-NUIAK',template=template,
            question=question,decision=decision,inputs=inputs,parameters=parameters or {},dependencies=dependencies or [])
        save(folder/(name+'.json'),doc);templates.register(doc);jobs.append(doc['id']);return doc['id']
    def dep(job,name):
        return dict(job=job,specSHA256=q.text_digest(q.load(q.QUEUE/'jobs'/job/'spec.json')),outputs=[name])
    proposals=output('hcf398-outer-ring-proposals','comparison.json')
    rows=q.load(q.ROOT/proposals['path'])['rows']
    development=sorted({r['group'] for r in rows if r['role']=='development'})
    q.require(len(development)==30,'development_group_count')
    policy=dict(version='fixed-inset-groups-v1',fitGroups=development[:15],
                evaluationGroups=sorted({r['group'] for r in rows}-set(development[:15])))
    from fixed_insets401 import partition
    partition(rows,policy);save(folder/'partition.json',policy);partition_ref=pin(folder/'partition.json')
    correction=add('fixed-mapping','T31','Does one mapping from 15 development groups transfer to separate groups?',
        'Fit group-balanced HCF edge medians only on named fitting groups. Preserve Standard and original geometry.',
        dict(proposals=proposals,geometry=output('hcf399-insets','geometry.json'),partition=partition_ref))
    rules=dict(job=correction,output='comparison.json');rule_dep=dep(correction,'comparison.json')
    original=q.load(q.ROOT/'reports/work/HCF397/01-proposals.json')['inputs']
    scoring=add('crop','T18','Does fixed inset geometry preserve crop selection on separate groups?',
        'Keep weights, thresholds, and production crops unchanged. Report losses before accepting any correction.',
        dict(original,rules=rules,membership=original['rules']),dependencies=[rule_dep])
    selection=dict(job=scoring,output='proposal-selection.json');score_dep=dep(scoring,'proposal-selection.json')
    primary=output('hcf388-detector-evaluate','comparison.json')
    fallback=add('fallback','T30','Does fixed-map fallback preserve detector successes and Standard?',
        'Keep detector selections. Use the crop fallback only for explicit HCF abstentions.',
        dict(primary=primary,fallback=selection),dict(enabled=True),[score_dep])
    candidate=dict(job=fallback,output='comparison.json');fallback_dep=dep(fallback,'comparison.json')
    for name,baseline in [('detector',primary),('prior-fallback',output('hcf400-enabled','comparison.json'))]:
        add('vs-'+name,'T32','Which '+name+' successes survive on groups outside the fit?',
            'Separate fitting and evaluation counts. Reject losses or more wrong selections; keep final audit unavailable.',
            dict(baseline=baseline,candidate=candidate,partition=partition_ref),dependencies=[fallback_dep])
    add('crop-vs-uncorrected','T32','Does the fixed mapping improve uncorrected crops outside the fit?',
        'Compare gains and losses on the same groups without changing Standard models.',
        dict(baseline=output('hcf398-outer-ring-crop-v2','proposal-selection.json'),candidate=selection,partition=partition_ref),dependencies=[score_dep])
    add('failure-audit','T20','Which proposal and crop failures remain after fixed mapping?',
        'Separate absent proposals from rejected matching crops before further training.',
        dict(catalog=original['catalog'],retained=original['retained'],rules=rules,selection=selection),dependencies=[rule_dep,score_dep])
    save(folder/'batch.json',dict(jobs=jobs,standardChanged=False,modelAccepted=False));return jobs


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--approve',action='store_true');args=parser.parse_args()
    for job in build():
        if args.approve:approval.approve(q.QUEUE,job,'agent:research-host-NUIAK',
            'Maintainer approves fixed mapping on separate inspected groups. Preserve Standard, models, crops, and prior successes.')
        print(job,flush=True)
