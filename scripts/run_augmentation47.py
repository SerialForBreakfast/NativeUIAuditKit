"""Prepare and execute the two assigned, fixed-membership augmentation comparisons."""
import argparse
import copy
import time
import human_annotation_review as h
import train_fullscreen_focus as runner

BASE=h.ROOT/'reports/work/FOCUS-AUGMENTATION-47'


def prepare():
    baseline=h.ROOT/'reports/work/FULLSCREEN-EXPERIMENT-41/run.json'
    doc=h.read(baseline);h.require(doc['epochs']==1 and doc['batch']==8 and doc['seed']==42 and doc['imgsz']==640,'baseline_configuration')
    h.require(len(doc['frames'])==2500 and sum(f['split']=='train' for f in doc['frames'])==2000,'baseline_membership')
    h.require(doc['runtime']==runner.runtime_identity(),'runtime_changed')
    output=h.fresh(BASE/'contracts');output.mkdir(parents=True)
    authority=dict(approvedBy='Maintainer: Ok do that tranche, following FocusPriorities46 recommendation',
                   scope='FSF003/004 fixed one-epoch translation/scale comparisons and frozen diagnostic scoring',
                   baseline=h.ref(baseline),membershipSHA256=h.digest(doc['frames']),totalOutputBytes=2*1024**3,
                   timeLimitOverride=h.ref(h.ROOT/'reports/work/FULLSCREEN-EXPERIMENT-41/time-authority.json'))
    h.write(output/'authority.json',authority)
    for name,run_id,scale in [('translation','FSF003',0.),('translation-scale','FSF004',.2)]:
        d=copy.deepcopy(doc);d['augmentation']=dict(version=1,translate=.05,scale=scale)
        d['budget']=dict(seconds=None,bytes=768*1024**2);d['timeLimitOverride']=authority['timeLimitOverride']
        d['experiment']=dict(id=run_id,authority=h.ref(output/'authority.json'))
        runner.augmentation_options(d)
        h.write(output/(name+'.json'),d)
    sources=[h.ref(h.ROOT/'scripts'/name) for name in ('train_fullscreen_focus.py','fullscreen_readthrough.py','run_augmentation47.py')]
    h.write(output/'sources.json',dict(implementation=sources,baseline=h.ref(baseline)))
    print('FSF003/004 contracts frozen; same membership/init; one epoch each.',flush=True)


def execute():
    for ref in h.read(BASE/'contracts/sources.json')['implementation']:h.checked(h.ROOT,ref)
    for name in ('translation','translation-scale'):
        print(f'{name}: validating originals, then training and terminal evaluation',flush=True)
        started=time.monotonic()
        result=runner.execute(BASE/'contracts'/(name+'.json'),BASE/'runs'/name)
        h.write(BASE/(name+'-execution.json'),dict(receipt=result,totalSeconds=time.monotonic()-started))
        print(f'{name}: {result["outcome"]}',flush=True)
        h.require(result['outcome']=='completed','comparison_execution_failed')
        h.require(sum(p.stat().st_size for p in BASE.rglob('*') if p.is_file())<=2*1024**3,'tranche_output_budget')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');a=p.parse_args()
    if a.execute:execute()
    else:prepare()
