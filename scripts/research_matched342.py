"""Measure equal-magnitude focus and content cases from retained predictions."""
from collections import defaultdict
from pathlib import Path
import numpy as np
import research_queue as q
from research_campaign340 import pin,decision

OUT=None


def summarize(rows,probabilities):
    q.require(len(rows)==len(probabilities) and len({v['id'] for v in rows})==len(rows),'membership')
    groups=defaultdict(lambda:dict(count=0,correct=0,falseChange=0,missedChange=0,abstentions=0))
    for row,probability in zip(rows,probabilities):
        q.require(row['role']=='train' and row['changed'] in (0,1),'role_or_label')
        pred=decision(float(probability));v=groups[row['group']+'/'+row['condition']]
        v['count']+=1;v['correct']+=pred==row['changed'];v['abstentions']+=pred is None
        v['falseChange']+=pred==1 and row['changed']==0
        v['missedChange']+=pred==0 and row['changed']==1
    return dict(groups)


def run():
    config=q.load(OUT/'config.json')
    for ref in config['inputs']:
        q.require(q.digest(q.local_path(q.ROOT,ref['path']))==ref['sha256'],'input_hash')
    p=q.ROOT/'reports/work';neg=q.load(p/'FOCUS-341/negatives.json')['rows']
    validation=q.load(p/'FOCUS-341/negative-validation.json');q.require(validation['passed'],'negative_validation')
    q.require([v['id'] for v in validation['rows']]==[v['id'] for v in neg],'validation_membership')
    source=q.load(p/'FOCUS-326/corpus.json')['rows']['independent'];lookup={v['id']:v for v in source}
    movement=[lookup[v['matchedMovementID']] for v in neg];rows=neg+movement
    q.require(all(a['group']==b['group'] and a['changed']==0 and b['changed']==1
                  for a,b in zip(neg,movement)),'pair_labels')
    q.require(all(v['relativeError']<=.1 for v in validation['rows']),'magnitude_match')
    checked=set()
    for row in rows:
        for ref in row['images']:
            key=(ref['path'],ref['sha256'])
            if key not in checked:q.require(q.digest(q.local_path(q.ROOT,ref['path']))==ref['sha256'],'image_hash')
            checked.add(key)
    old=q.load(p/'FOCUS-329/run/training.json')['probabilities'][240:]
    q.require(len(old)==len(source),'baseline_membership')
    oldmap={r['id']:v for r,v in zip(source,old)}
    baseline=[v['probability'] for v in validation['rows']]+[oldmap[v['id']] for v in movement]
    models={'FOCUS329':baseline};refs={'FOCUS329':pin(p/'FOCUS-329/run/last.pt')}
    for name in ('added-detail','added-detail-and-content'):
        report=q.load(p/f'FOCUS-341/{name}-report.json')
        q.require(report['matchedIDs']==[v['id'] for v in rows],'prediction_membership')
        q.require(report['matchedLabels']==[v['changed'] for v in rows],'prediction_labels')
        q.require(q.digest(q.ROOT/report['model']['path'])==report['model']['sha256'],'model_hash')
        models[name]=report['matchedProbabilities'];refs[name]=report['model']
    scores={}
    for name,prob in models.items():
        scores[name]=dict(byGroup=summarize(rows,prob),model=refs[name],probabilities=prob,
            bothCausesCorrect=sum(decision(float(prob[i]))==0 and decision(float(prob[i+len(neg)]))==1
                                  for i in range(len(neg))))
    q.save(OUT/'diagnostic.json',dict(version='research-diagnostic-v1',code='A3-authored342',
        evidenceKind='cached-diagnostic',inputs=config['inputs'],cases=len(rows),groups=len({r['group'] for r in rows}),
        rows=[dict(id=r['id'],group=r['group'],role=r['role'],label=r['changed'],images=r['images']) for r in rows],
        scores=scores,maximumRelativeMagnitudeError=max(v['relativeError'] for v in validation['rows']),
        candidateJustified=False,fullExperimentComplete=False,
        limitations=['Training-only authored pairs from 3 related groups. Not native qualification.',
                    'Central background changes only. Other regions and inside-control content remain missing.',
                    'All 7 archetypes and 3 themes remain unqualified.'],
        nextAction='Use matched pairs in FOCUS342 regression checks. Do not repeat inference or request remote duplicates.'))


def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS342';id='measured340-a3-authored342'
    q.require(not (q.QUEUE/'jobs'/id).exists(),'existing_job')
    paths=['scripts/research_matched342.py','scripts/research_campaign340.py',
           'reports/work/FOCUS-341/negatives.json','reports/work/FOCUS-341/negative-validation.json',
           'reports/work/FOCUS-326/corpus.json','reports/work/FOCUS-329/run/training.json',
           'reports/work/FOCUS-329/run/last.pt',
           'reports/work/FOCUS-341/added-detail-report.json','reports/work/FOCUS-341/added-detail-and-content-report.json']
    refs=[pin(q.ROOT/path) for path in paths]
    config=folder/(id+'-config.json');q.save(config,dict(inputs=refs))
    spec=dict(version=q.SPEC_VERSION,id=id,task='FOCUS342',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
        hypothesis='Equal pixel magnitude alone does not establish focus change. Reuse 192 qualified authored pairs.',
        decisionRule='Report errors by cause and group. Training-only success cannot justify deployment.',
        adapter=dict(type='python-callable',steps=['research_matched342.run'],outputAttributes=['research_matched342.OUT']),
        inputs=refs,stage=[{'from':pin(config),'to':'config.json'}],
        limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    path=folder/(id+'.json');q.save(path,spec);print(q.submit(path))


if __name__=='__main__':register()
