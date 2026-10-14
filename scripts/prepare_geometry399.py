"""Prepare five useful geometry and observer jobs. The runner owns execution."""
import argparse
import subprocess
import research_queue as q
import research_approval as approval
import hcf_templates395 as templates
from template_inputs398 import pin


def build():
    folder=q.ROOT/'reports/work/HCF399';folder.mkdir(parents=True,exist_ok=True);jobs=[]
    def output(job,name):
        attempt=q.QUEUE/'jobs'/job/'attempts/1';result=q.load(attempt/'result.json')
        q.require(result['status']=='complete','producer_incomplete')
        ref=pin(attempt/'out'/name)
        q.require(any(r['path']==name and r['sha256']==ref['sha256'] for r in result['outputs']),'producer_output_changed')
        return ref
    def add(name,template,question,decision,inputs,parameters=None):
        doc=dict(version='hcf-template-description-v1',id='hcf399-'+name,owner='research-host-NUIAK',template=template,
            question=question,decision=decision,inputs=inputs,parameters=parameters or {},dependencies=[])
        path=folder/(name+'.json')
        if path.exists():q.require(q.load(path)==doc,'immutable_description')
        else:q.save(path,doc)
        templates.register(doc);jobs.append(doc['id'])
    add('coordinate-fixtures','T27','Does the exact TTR kernel report known asymmetric rings in top-left coordinates?',
        'Separate an axis error from native proposal coverage. Authored rings are software tests, not training images.',
        dict(kernel=output('hcf398-outer-ring-proposals','outer-ring')))
    original=q.load(q.ROOT/'reports/work/HCF397/01-proposals.json')['inputs']
    inputs=dict(catalog=original['catalog'],retained=original['retained'],
        proposals=output('hcf398-outer-ring-proposals','comparison.json'),
        selection=output('hcf398-outer-ring-crop-v2','proposal-selection.json'))
    for mode,question,decision in [
        ('orientation','Does vertical inversion explain the retained proposal failures?',
         'Report paired matches and lost matches. Do not select orientation per image using labels.'),
        ('insets','How far do matched ring edges differ from observed body edges?',
         'Measure each edge before choosing a fixed geometry correction. Do not apply fitted offsets to audit data.'),
        ('coverage','Which screen regions lack matching ring proposals?',
         'Prioritize missing geometry by measured region support, not extra training volume.')]:
        add(mode,'T26',question,decision,inputs,dict(mode=mode))
    parity=output('hcf396-11-parity','parity.json')
    membership=q.load(q.ROOT/parity['path'])['membership']
    add('observer-smoke','T28','Does the delivered observer wrapper reproduce the fixed Vision sample and crop hashes?',
        'Qualify the producer adapter end to end. TTR inference remains a separate consumer requirement.',
        dict(export=output('hcf396-10-compress','export.json'),membership=membership,parity=parity,
             bundle=pin(q.ROOT/'reports/work/HCF396/ttr-handoff-v1/bundle.json'),
             tool=pin(q.ROOT/'.build/standard392-swift/arm64-apple-macosx/debug/FocusRingTool')),
        dict(sourceRevision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=q.ROOT,text=True).strip()))
    path=folder/'batch.json';value=dict(jobs=jobs,standardChanged=False,modelAccepted=False)
    if path.exists():q.require(q.load(path)==value,'immutable_batch')
    else:q.save(path,value)
    return jobs


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--approve',action='store_true');args=parser.parse_args()
    for job in build():
        if args.approve:approval.approve(q.QUEUE,job,'agent:research-host-NUIAK',
            'Maintainer approves retained geometry diagnostics and observer qualification. No training, capture, or Standard changes.')
        print(job,flush=True)
