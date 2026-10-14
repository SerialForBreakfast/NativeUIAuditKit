"""Inspect retained authored training predictions without rerunning inference."""
from collections import defaultdict
from pathlib import Path
import research_queue as q
from research_campaign340 import decision, pin

OUT = None
SOURCES = ('reports/work/FOCUS-329/run/training.json', 'reports/work/FOCUS-319/corpus.json',
           'reports/work/FOCUS-326/corpus.json')


def summarize(rows, probabilities, keys):
    q.require(len(rows)==len(probabilities),'cached_membership')
    groups=defaultdict(lambda:dict(count=0,correct=0,falseChange=0,missedChange=0,abstentions=0,groups=set()))
    for row,p in zip(rows,probabilities):
        q.require(row['role']=='train','training_role')
        key=' / '.join(str(row.get(k,'unavailable')) for k in keys)
        result=groups[key];d=decision(p);label=row['changed']
        result['count']+=1;result['correct']+=d==label
        result['falseChange']+=d==1 and label==0;result['missedChange']+=d==0 and label==1
        result['abstentions']+=d is None;result['groups'].add(row['group'])
    return {k:dict(v,groups=sorted(v['groups'])) for k,v in groups.items()}


def run():
    config=q.load(OUT/'config.json');docs=[]
    for ref in config['inputs']:
        path=q.local_path(q.ROOT,ref['path']);q.require(q.digest(path)==ref['sha256'],'cached_hash')
        docs.append(q.load(path))
    predictions,old,corpus=docs;rows=old['rows']+corpus['rows']['independent']
    q.require(len(rows)==len(predictions['probabilities'])==len(predictions['initialProbabilities']),'cached_membership')
    # The independent rows have controlled size, width, contrast, distance, and corner.
    start=len(old['rows']);rows=rows[start:]
    keys={'A1':['condition','group'], 'B1':['corner','condition'],
          'D4':['sizePixels','widthPixels','contrast','condition']}[config['code']]
    before=summarize(rows,predictions['initialProbabilities'][start:],keys)
    after=summarize(rows,predictions['probabilities'][start:],keys)
    q.save(OUT/'diagnostic.json',dict(version='research-diagnostic-v1',evidenceKind='cached-diagnostic',
        code=config['code'],inputs=config['inputs'],rows=len(rows),before=before,after=after,
        candidateJustified=False,
        limitations=['Training-only authored data from 3 artwork families; not independent model accuracy.',
                    'Fixed templates do not cover all 7 archetypes or all 3 themes.',
                    'This precheck does not complete the requested controlled experiment.'],
        nextAction='Use the measured errors to freeze missing coverage. Do not repeat the rejected FOCUS329 candidate.'))


def register():
    folder=q.ROOT/'Research/ResearchSpecs/RESEARCH340';folder.mkdir(parents=True,exist_ok=True)
    for code in ('A1','B1','D4'):
        id='measured340-'+code.lower()+'-precheck'
        if (q.QUEUE/'jobs'/id/'spec.json').exists():continue
        refs=[pin(q.ROOT/p) for p in SOURCES]
        config=folder/(id+'-config.json');q.save(config,dict(code=code,inputs=refs))
        spec=dict(version=q.SPEC_VERSION,id=id,task='RESEARCH340-'+code,owner='research-host-NUIAK',
            kind='screen',authority='diagnostic',batch='cached',
            hypothesis='Retained matched training cases identify errors before new generation.',
            decisionRule='Report per-factor errors and abstentions. Do not infer generalization or select another FOCUS329 run.',
            adapter=dict(type='python-callable',steps=['research_cached340.run'],outputAttributes=['research_cached340.OUT']),
            inputs=[pin(Path(__file__)),pin(q.ROOT/'scripts/research_campaign340.py')]+refs,
            stage=[{'from':pin(config),'to':'config.json'}],
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=2))
        path=folder/(id+'.json');q.save(path,spec);print(id,q.submit(path))


if __name__=='__main__':register()
