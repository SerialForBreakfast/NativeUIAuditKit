"""Run retained comparisons without changing models, crops, or thresholds."""
from collections import defaultdict
import time
import numpy as np
import research_queue as q
from research_campaign340 import pin,decision

OUT=None
REPORTS={
    'FOCUS341-content':'reports/work/FOCUS-341/added-detail-and-content-report.json',
    'FOCUS342-rotation':'reports/work/FOCUS-342/balanced-report.json',
    'FOCUS342-preservation':'reports/work/FOCUS-342/balanced-preservation-report.json'}


def counts(rows,values,baseline=None):
    q.require(len(rows)==len(values),'prediction_count')
    out=defaultdict(lambda:dict(count=0,correct=0,falseChange=0,missedChange=0,abstentions=0,lost=0,gained=0))
    for i,(row,value) in enumerate(zip(rows,values)):
        label=row['changed'];q.require(label in (0,1),'label');pred=decision(float(value))
        key='/'.join(str(row.get(k,'unavailable')) for k in ('layout','condition'))
        item=out[key];item['count']+=1;item['correct']+=pred==label
        item['falseChange']+=pred==1 and label==0;item['missedChange']+=pred==0 and label==1
        item['abstentions']+=pred is None
        if baseline is not None:
            old=decision(float(baseline[i]));item['lost']+=old==label and pred!=label
            item['gained']+=old!=label and pred==label
    return dict(out)


def cached(mode):
    first=q.load(q.ROOT/'reports/work/FOCUS-319/corpus.json')['rows']
    rows=first+q.load(q.ROOT/'reports/work/FOCUS-326/corpus.json')['rows']['independent']
    baseline=q.load(q.ROOT/'reports/work/FOCUS-329/run/training.json')['probabilities']
    q.require(len(rows)==len(baseline)==1200,'membership')
    selection=list(range(len(first))) if mode=='artwork' else list(range(len(rows)))
    q.require(all(rows[i]['role']=='train' for i in selection),'training_only')
    selected=[rows[i] for i in selection];old=[baseline[i] for i in selection]
    scores={'FOCUS329':dict(counts=counts(selected,old),probabilities=old,
        model=pin(q.ROOT/'reports/work/FOCUS-329/run/last.pt'))}
    conflicts=[]
    for name,path in REPORTS.items():
        report=q.load(q.ROOT/path);values=report['authoredProbabilities']
        q.require(len(values)==len(rows),'candidate_membership')
        q.require(q.digest(q.ROOT/report['model']['path'])==report['model']['sha256'],'model_hash')
        prob=[values[i] for i in selection]
        scores[name]=dict(counts=counts(selected,prob,old),probabilities=prob,model=report['model'])
        for i in selection:
            before,after=decision(float(baseline[i])),decision(float(values[i]));label=rows[i]['changed']
            if (before==label and after!=label) or (before is None and after is not None and after!=label):
                conflicts.append(dict(model=name,index=i,id=rows[i].get('id',str(i)),group=rows[i]['group'],
                    condition=rows[i]['condition'],label=label,before=baseline[i],after=values[i],
                    marginToCorrect=(values[i]-.85 if label else .15-values[i])))
    return dict(rows=selected,scores=scores,conflicts=conflicts,
        independentGroups=len({r['group'] for r in selected}),
        limitations=['Training-only authored evidence. Repeated and reversed pairs share ancestry.',
                    'Missing themes and layouts remain unsupported. No native accuracy claim.'])


def native():
    import report_additive341 as report
    report.a.t.set_num_threads(2)
    capture=q.load(q.ROOT/'reports/work/FOCUS-343/native-corner-r2/capture.json')
    q.require(capture['complete'] and capture['cleanup'],'incomplete_native_capture')
    frames=capture['frames'];rows=[]
    for i in range(0,8,2):
        for j,condition in [(i+1,'stable-repeat'),((i+2)%8,'movement')]:
            for reverse in (False,True):
                a,b=(frames[j],frames[i]) if reverse else (frames[i],frames[j])
                rows.append(dict(id=f'native343-{i}-{j}-{reverse}',images=[a['image'],b['image']],
                    changed=int(a['target']!=b['target']),condition=condition,layout='native-corners',
                    role='development',group='native343-existing-scene'))
    baseline=report.score_rows(report.a.e.load_candidate(q.ROOT/'reports/work/FOCUS-329/run/last.pt'),rows,False)
    scores={'FOCUS329':dict(counts=counts(rows,baseline),probabilities=baseline.tolist(),
        model=pin(q.ROOT/'reports/work/FOCUS-329/run/last.pt'))}
    for name,path in REPORTS.items():
        ref=q.load(q.ROOT/path)['model'];q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'model_hash')
        values=report.score_rows(report.a.load(q.ROOT/ref['path']),rows,True)
        scores[name]=dict(counts=counts(rows,values,baseline),probabilities=values.tolist(),model=ref)
    return dict(rows=rows,scores=scores,independentGroups=1,
        limitations=['Observed native focus labels use capture intervals, not atomic frame identity.',
                    'Source-to-installed-build match remains unresolved. Data stays outside training.',
                    'One scene and repeated/reversed pairs do not establish generalization.'])


def run():
    config=q.load(OUT/'config.json');start=time.monotonic()
    for ref in config['inputs']:
        q.require(q.digest(q.local_path(q.ROOT,ref['path']))==ref['sha256'],'input_hash')
    result=native() if config['mode']=='native' else cached(config['mode'])
    result.update(version='focus343-diagnostic-v1',inputs=config['inputs'],seconds=time.monotonic()-start,
                  thresholds=[.15,.85],modelAccepted=False,productionChanged=False)
    q.save(OUT/'diagnostic.json',result)


def register(mode):
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS343';folder.mkdir(exist_ok=True)
    id='focus343-'+mode;q.require(not (q.QUEUE/'jobs'/id).exists(),'existing_job')
    paths=['scripts/diagnostics343.py','scripts/research_campaign340.py',
        'reports/work/FOCUS-319/corpus.json','reports/work/FOCUS-326/corpus.json',
        'reports/work/FOCUS-329/run/training.json','reports/work/FOCUS-329/run/last.pt']+list(REPORTS.values())
    if mode=='native':
        paths+=['reports/work/FOCUS-343/native-corner-r2/capture.json','scripts/report_additive341.py','scripts/additive341.py']
        paths += [v['image']['path'] for v in q.load(q.ROOT/paths[-3])['frames']]
    refs=[pin(q.ROOT/p) for p in paths]
    config=folder/(id+'-config.json');q.save(config,dict(inputs=refs,mode=mode))
    spec=dict(version=q.SPEC_VERSION,id=id,task='FOCUS343',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
        hypothesis={'artwork':'Artwork-only cases expose retained appearance dependence.',
                    'margins':'Previous successes and previous abstentions show different correction failures.',
                    'native':'Native corner focus changes test transfer beyond authored training screens.'}[mode],
        decisionRule='Report raw errors and lost successes at fixed thresholds. Do not train or promote from this result alone.',
        adapter=dict(type='python-callable',steps=['diagnostics343.run'],outputAttributes=['diagnostics343.OUT']),
        inputs=refs,stage=[{'from':pin(config),'to':'config.json'}],
        limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    path=folder/(id+'.json');q.save(path,spec);print(q.submit(path))


if __name__=='__main__':
    import sys
    register(sys.argv[1])
