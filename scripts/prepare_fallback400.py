"""Prepare a fixed fallback and its matched regression checks."""
import argparse
import research_queue as q
import research_approval as approval
import hcf_templates395 as templates
from template_inputs398 import pin


def build():
    folder=q.ROOT/'reports/work/HCF400';folder.mkdir(parents=True,exist_ok=True);jobs=[]
    def output(job,name):
        attempt=q.QUEUE/'jobs'/job/'attempts/1';result=q.load(attempt/'result.json')
        q.require(result['status']=='complete','producer_incomplete');ref=pin(attempt/'out'/name)
        q.require(any(r['path']==name and r['sha256']==ref['sha256'] for r in result['outputs']),'producer_changed')
        return ref
    def add(name,template,question,decision,inputs,parameters,dependencies=None):
        doc=dict(version='hcf-template-description-v1',id='hcf400-'+name,owner='Maximum-mini-NUIAK',template=template,
            question=question,decision=decision,inputs=inputs,parameters=parameters,dependencies=dependencies or [])
        path=folder/(name+'.json')
        if path.exists():q.require(q.load(path)==doc,'immutable_description')
        else:q.save(path,doc)
        templates.register(doc);jobs.append(doc['id']);return doc['id']
    primary=output('hcf388-detector-evaluate','comparison.json');fallback=output('hcf399-inset-crop','proposal-selection.json')
    for enabled in (False,True):
        arm='enabled' if enabled else 'disabled'
        job=add(arm,'T30','Does '+arm+' HCF fallback preserve detector decisions?',
            'Use fallback only on explicit HCF detector abstentions. Never inspect labels when choosing the branch.',
            dict(primary=primary,fallback=fallback),dict(enabled=enabled))
        dependency=dict(job=job,specSHA256=q.text_digest(q.load(q.QUEUE/'jobs'/job/'spec.json')),outputs=['comparison.json'])
        references=[('detector',primary)] if not enabled else [('detector',primary),('corrected-rings',fallback),
            ('known-box-upper-bound',output('hcf375c-80-crop-evaluate','comparison.json'))]
        for label,reference in references:
            add(arm+'-vs-'+label,'T15','Which '+label+' successes survive '+arm+' HCF fallback?',
                'Report case-linked gains and losses separately for HCF and Standard. No promotion follows.',
                dict(baseline=reference,candidate=dict(job=job,output='comparison.json')),
                dict(comparison=label+' versus '+arm+' HCF fallback'),[dependency])
    path=folder/'batch.json';value=dict(jobs=jobs,standardChanged=False,modelAccepted=False)
    if path.exists():q.require(q.load(path)==value,'immutable_batch')
    else:q.save(path,value)
    return jobs


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--approve',action='store_true');args=parser.parse_args()
    for job in build():
        if args.approve:approval.approve(q.QUEUE,job,'agent:Maximum-mini-NUIAK',
            'Maintainer approves cached HCF diagnostics preserving Standard. No model, threshold, capture, or navigation changes.')
        print(job,flush=True)
