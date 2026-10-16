"""Prepare retained diagnostics and observer checks without running experiments."""
import argparse
import subprocess
import research_queue as q
import research_approval as approval
import hcf_templates395 as templates
from template_inputs398 import pin
from template_analysis397 import SUITES


def build():
    folder=q.ROOT/'reports/work/HCF398'; folder.mkdir(parents=True,exist_ok=True)
    jobs=[]
    def save(name, value):
        path=folder/name
        if path.exists(): q.require(q.load(path)==value,'immutable_preparation_changed')
        else: q.save(path,value)
        return pin(path)
    def output(job,name):
        attempt=q.QUEUE/'jobs'/job/'attempts/1'
        result=q.load(attempt/'result.json'); q.require(result['status']=='complete','producer_failed')
        path=attempt/'out'/name
        record=next(r for r in result['outputs'] if r['path']==name)
        q.require(q.digest(path)==record['sha256'],'producer_changed')
        return pin(path)
    def add(name,template,question,decision,inputs,parameters=None):
        doc=dict(version='hcf-template-description-v1',id='hcf398-'+name,owner='Maximum-mini-NUIAK',
            template=template,question=question,decision=decision,inputs=inputs,parameters=parameters or {},dependencies=[])
        save(name+'.json',doc); templates.register(doc); jobs.append(doc['id'])
    original=q.load(q.ROOT/'reports/work/HCF397/01-proposals.json')['inputs']
    for suffix in ('five-percent','ten-percent'):
        job='hcf397-boundary-'+suffix
        add('audit-'+suffix,'T24','Does '+suffix+' expansion lose proposal coverage or reject matching boxes?',
            'Explain the failed correction using retained scores. Do not expand this scale search.',
            dict(catalog=original['catalog'],retained=original['retained'],rules=original['rules'],
                 selection=output(job,'proposal-selection.json')),dict(scale=1.05 if suffix=='five-percent' else 1.10))
    add('rules-vs-detector','T15','Which retained cases distinguish the independent rules from the detector?',
        'Identify complementary cases and wrong selections. Do not select a combined policy using evaluation labels.',
        dict(baseline=output('hcf371r4-60-rules','comparison.json'),candidate=output('hcf388-detector-evaluate','comparison.json')),
        dict(comparison='Independent bright-stroke rules versus detector'))
    tests=save('qualification.json',dict(version='template-qualification-v1',suite='source-and-observer',
        tests=[pin(q.MODULES/(name+'.py')) for name in SUITES['source-and-observer']]))
    add('source-and-observer','T16','Do source isolation and observer receipt checks reject invalid inputs?',
        'Require positive and negative checks through the queue. Software checks do not qualify TTR inference.',
        dict(qualification=tests),dict(suite='source-and-observer'))
    add('observer-contract','T22','Can TTR verify the compiled model and original crop lineage?',
        'Use the production digest contract. Keep actual TTR verification blocked until its receipt arrives.',
        dict(export=output('hcf396-10-compress','export.json'),membership=pin(q.ROOT/'reports/work/TEMPLATE395/runtime-membership.json')),
        dict(sourceRevision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=q.ROOT,text=True).strip()))
    save('batch.json',dict(jobs=jobs,modelAccepted=False,standardChanged=False,
        blocked=['Actual TTR observer receipt with loaded identity and crop lineage.',
                 'Pinned outer-ring-v2 candidate outputs or executable source.',
                 'Qualified native no-focus cases and separate audit groups.']))
    return jobs


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--approve',action='store_true');args=parser.parse_args()
    for job in build():
        if args.approve:
            approval.approve(q.QUEUE,job,'agent:Maximum-mini-NUIAK',
                'Maintainer approves retained HCF comparisons, template repair, and observer preparation. No training or Standard changes.')
        print(job,flush=True)
