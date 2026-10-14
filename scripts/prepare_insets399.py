"""Queue one justified inset correction and matched regression reports."""
import argparse
import research_queue as q
import research_approval as approval
import hcf_templates395 as templates
from template_inputs398 import pin


def build():
    folder=q.ROOT/'reports/work/HCF399';jobs=[]
    def output(job,name):
        attempt=q.QUEUE/'jobs'/job/'attempts/1';result=q.load(attempt/'result.json')
        q.require(result['status']=='complete','producer_incomplete');ref=pin(attempt/'out'/name)
        q.require(any(r['path']==name and r['sha256']==ref['sha256'] for r in result['outputs']),'producer_changed')
        return ref
    def add(name,template,question,decision,inputs,parameters=None,dependencies=None):
        doc=dict(version='hcf-template-description-v1',id='hcf399-'+name,owner='research-host-NUIAK',template=template,
            question=question,decision=decision,inputs=inputs,parameters=parameters or {},dependencies=dependencies or [])
        path=folder/(name+'.json')
        if path.exists():q.require(q.load(path)==doc,'immutable_description')
        else:q.save(path,doc)
        templates.register(doc);jobs.append(doc['id']);return doc['id']
    def dependency(job,name):
        return dict(job=job,specSHA256=q.text_digest(q.load(q.QUEUE/'jobs'/job/'spec.json')),outputs=[name])
    original=q.load(q.ROOT/'reports/work/HCF397/01-proposals.json')['inputs']
    proposals=output('hcf398-outer-ring-proposals','comparison.json')
    correction=add('inset-correction','T29','Can other development groups supply a consistent ring-to-body inset?',
        'Fit group-balanced median edges outside each target group. Preserve unsupported profiles and original crops.',
        dict(proposals=proposals,geometry=output('hcf399-insets','geometry.json')))
    rules=dict(job=correction,output='comparison.json');rule_dep=dependency(correction,'comparison.json')
    scoring=add('inset-crop','T18','Does the group-excluded inset improve fixed crop selection?',
        'Score unchanged weights and thresholds. Reject replacement if retained successes are lost.',
        dict(original,rules=rules,membership=original['rules']),dependencies=[rule_dep])
    selected=dict(job=scoring,output='proposal-selection.json');score_dep=dependency(scoring,'proposal-selection.json')
    for job,file,label in [('hcf398-outer-ring-crop-v2','proposal-selection.json','uncorrected-rings'),
                            ('hcf388-detector-evaluate','comparison.json','detector'),
                            ('hcf375c-80-crop-evaluate','comparison.json','known-box-upper-bound'),
                            ('hcf397-01-proposals','proposal-selection.json','original-proposals')]:
        add('inset-vs-'+label,'T15','Which '+label+' successes survive the group-excluded correction?',
            'Report all gains and losses by profile. Standard and previous models remain selected.',
            dict(baseline=output(job,file),candidate=selected),dict(comparison=label+' versus group-excluded ring insets'),[score_dep])
    add('inset-failure-audit','T20','Which misses remain after the fixed geometry correction?',
        'Separate absent proposals from rejected matching crops. Use the result before proposing more training.',
        dict(catalog=original['catalog'],retained=original['retained'],rules=rules,selection=selected),dependencies=[rule_dep,score_dep])
    path=folder/'inset-batch.json';value=dict(jobs=jobs,standardChanged=False,modelAccepted=False)
    if path.exists():q.require(q.load(path)==value,'immutable_batch')
    else:q.save(path,value)
    return jobs


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--approve',action='store_true');args=parser.parse_args()
    for job in build():
        if args.approve:approval.approve(q.QUEUE,job,'agent:research-host-NUIAK',
            'Maintainer approves geometry tests using retained cases. No training, Standard changes, or navigation authority.')
        print(job,flush=True)
