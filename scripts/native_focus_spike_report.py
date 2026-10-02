"""Read retained Native26 evidence; write compact metrics and Markdown review queues.

No capture, model execution, relabeling, admission or cleanup. Partial reports keep
missing stages explicit. Synthetic configuration groups are not independent apps.
"""
import argparse
import json
import math
from pathlib import Path
import random
import statistics

import native_focus_spike as n
import native_focus_spike_model as model


def distribution(values):
    values=sorted(v for v in values if v is not None)
    if not values:return dict(count=0,median=None,p95=None,total=None,mean=None,minimum=None,maximum=None)
    n.require(all(isinstance(v,(int,float)) and math.isfinite(v) and v>=0 for v in values),'invalid_timing')
    return dict(count=len(values),median=statistics.median(values),mean=statistics.mean(values),
        minimum=min(values),maximum=max(values),
        p95=values[math.ceil(.95*len(values))-1],total=sum(values))


def paired_comparison(a,b):
    """Compare exact shared example IDs at a fixed threshold, never best-of selection."""
    left={r['id'].rsplit('-',1)[0]:r for r in a['predictions']}
    right={r['id'].rsplit('-',1)[0]:r for r in b['predictions']}
    n.require(len(left)==len(a['predictions']) and set(left)==set(right),'comparison_membership')
    pairs={};counts=dict(bothCorrect=0,normalizedOnly=0,commonOnly=0,bothWrong=0)
    for key,x in left.items():
        y=right[key];n.require(x['label']==y['label'],'comparison_label')
        good_a=(x['probability']>=.85)==bool(x['label'])
        good_b=(y['probability']>=.85)==bool(y['label'])
        name='bothCorrect' if good_a and good_b else 'normalizedOnly' if good_a else 'commonOnly' if good_b else 'bothWrong'
        counts[name]+=1
        pairs.setdefault(key.rsplit('-',1)[0],[]).append((good_a,good_b))
    n.require(all(len(v)==2 for v in pairs.values()),'comparison_pair')
    pair_counts=dict(bothCorrect=0,normalizedOnly=0,commonOnly=0,bothWrong=0)
    for decisions in pairs.values():
        ga=all(x[0] for x in decisions);gb=all(x[1] for x in decisions)
        pair_counts['bothCorrect' if ga and gb else 'normalizedOnly' if ga else 'commonOnly' if gb else 'bothWrong']+=1
    return dict(threshold=.85,controls=counts,pairs=pair_counts)


def collect(plan,batch,protocol_root):
    rows=[];accepted=[];receipts=[];crops=[];case_results=[]
    for index in range(50):
        folder=batch/f'chunk-{index:03d}'
        path=folder/'accepted.json'
        if not path.exists():continue
        a=json.loads(path.read_text());accepted.append(a);rows+=a['rows']
        terminal=[]
        for status_path in [*folder.glob('poll-*.json'),*folder.glob('reconcile-*.json')]:
            d=json.loads(status_path.read_text()).get('reply',{})
            if not d.get('success'):continue
            s=next(iter(d['data'].values()))['_0']
            if s.get('state') in n.TERMINAL and s.get('campaign_id','').lower()==a['campaignID'].lower():
                terminal.append((status_path.stat().st_mtime,s))
        n.require(bool(terminal),'missing_terminal_capture_status')
        status=max(terminal,key=lambda x:x[0])[1];case_results+=status['cases']
        if a.get('supplementCampaignID'):
            d=json.loads((folder/'recovery/delivery-status.json').read_text())['reply']
            supplement=next(iter(d['data'].values()))['_0']
            n.require(supplement['state']=='completed' and
                supplement['campaign_id'].lower()==a['supplementCampaignID'].lower(),'recovery_timing_identity')
            case_results+=supplement['cases']
        for name in a.get('receipts',['receipt.json']):
            receipts.append(json.loads((folder/name).read_text()))
        p=n.USB/f'crops20-chunk-{index:03d}/crops.json'
        if p.exists():crops.append(json.loads(p.read_text()))
    expected={r['caseID']:r for r in plan['members']}
    n.require(len({r['caseID'] for r in rows})==len(rows) and
        all(r['caseID'] in expected and all(r[k]==v for k,v in expected[r['caseID']].items()) for r in rows),
        'report_membership')
    timings={key:distribution([r.get(key) for r in accepted]) for key in
        ('captureSeconds','validationSeconds','totalSeconds')}
    timings['transferSeconds']=distribution([r['seconds'] for r in receipts])
    timings['cropSeconds']=distribution([r['seconds'] for r in crops])
    timings['successfulCaseSeconds']=distribution([r.get('duration_seconds') for r in case_results if r['state']=='completed'])
    timings['failedCaseSeconds']=distribution([r.get('duration_seconds') for r in case_results if r['state']=='failed'])
    result=dict(completedChunks=len(accepted),acceptedPairs=len(rows),expectedPairs=1250,
        trainPairs=sum(r['role']=='train' for r in rows),evaluationPairs=sum(r['role']=='evaluation' for r in rows),
        cropCount=sum(len(d['records']) for d in crops),
        cropExceptions=[e for d in crops for e in d['exceptions']],
        transferredBytes=sum(r['bytes'] for r in receipts),timings=timings,
        attemptedCases=sum(r['state'] in ('completed','failed') for r in case_results),
        failedCases=[r for r in case_results if r['state']=='failed'],
        unavailableTimingStages=['producer render/settle/PNG encoding substage breakdown'],
        geometryGrowthWidth=distribution([r['growth'][0] for r in rows]),
        geometryGrowthHeight=distribution([r['growth'][1] for r in rows]),
        independentRealAppEvaluation=False,models={})
    if rows:
        result['bytesPerPair']=result['transferredBytes']/len(rows)
    protocols={}
    for arm,name in model.ARMS.items():
        p=protocol_root/f'{arm}.json'
        if p.exists():
            protocols[arm]=json.loads(p.read_text())
            result.setdefault('encoding',{})[arm]={k:protocols[arm][k] for k in
                ('encodingSeconds','encodingTiming','environment')}
        p=n.ROOT/'NativeUITrainer/focus_ring_runs'/name/'result.json'
        if not p.exists():continue
        r=json.loads(p.read_text());protocol=protocols[arm]
        n.require(r['protocolSHA256']==protocol['protocolSHA256'],'report_protocol_binding')
        lookup={s['id']:s for s in protocol['samples'] if s['role']=='evaluation'}
        n.require(set(lookup)=={s['id'] for s in r['predictions']} and len(r['predictions'])==500,'report_eval_membership')
        n.require(all(lookup[s['id']]['label']==s['label'] for s in r['predictions']),'report_eval_labels')
        records=[lookup[s['id']] for s in r['predictions']];scores=[s['probability'] for s in r['predictions']]
        n.require(model.metric(records,scores,.85)==r['at085'] and model.metric(records,scores,.5)==r['at05'],
            'report_metric_replay')
        groups={}
        for group in sorted({s['configurationGroup'] for s in records}):
            ids=[i for i,s in enumerate(records) if s['configurationGroup']==group]
            groups[str(group)]=model.metric([records[i] for i in ids],[scores[i] for i in ids],.85)
        result['models'][arm]=dict(r,configurationGroups=groups)
        baseline=p.parent/'baseline.json'
        if baseline.exists():
            base=json.loads(baseline.read_text())
            n.require(base['checkpoint']==protocol['baseline'] and
                [s['id'] for s in base['predictions']]==[s['id'] for s in r['predictions']],
                'baseline_membership')
            base_scores=[s['probability'] for s in base['predictions']]
            n.require(model.metric(records,base_scores,.85)==base['at085'] and
                model.metric(records,base_scores,.5)==base['at05'],'baseline_metric_replay')
            result['baseline']=base
        retained=p.parent/'retained-replay.json'
        if retained.exists():
            from focus_representative_experiment import selection_metrics
            replay=json.loads(retained.read_text())
            ref=protocol['retainedProtocol']
            n.require(replay['protocol']==ref and n.sha(n.ROOT/ref['path'])==ref['sha256'],
                'retained_report_binding')
            retained_protocol=json.loads((n.ROOT/ref['path']).read_text())
            retained_rows=[s for s in retained_protocol['samples'] if s['split']=='validation']
            n.require(len(retained_rows)==333,'retained_report_count')
            for key in ('candidate','baseline'):
                predictions=replay[key]['predictions']
                n.require([s['id'] for s in predictions]==[s['id'] for s in retained_rows] and
                    all(a['label']==b['label'] for a,b in zip(predictions,retained_rows)),
                    'retained_report_membership')
                n.require(selection_metrics(predictions,retained_rows,retained_protocol['selection'])==
                    replay[key]['metrics'],'retained_metric_replay')
            result['retainedReplay']=replay
    if len(result['models'])==2:
        a,b=[result['models'][k] for k in model.ARMS]
        result['pairedComparison']=paired_comparison(a,b)
        result['equalTrainingUpdates']=a['updates']==b['updates']
        result['equalInitialization']=a['initialStateSHA256']==b['initialStateSHA256']
    result['complete']=len(rows)==1250 and result['cropCount']==5000 and not result['cropExceptions'] and len(result['models'])==2 and 'baseline' in result and 'retainedReplay' in result
    return result,rows,protocols


def review(rows,result):
    rng=random.Random(26);selected=[]
    for group in sorted({r['configurationGroup'] for r in rows}):
        selected.append(rng.choice(sorted((r for r in rows if r['configurationGroup']==group),key=lambda r:r['caseID'])))
    lines=['# Native focus spike — optional review','',
        'Random samples below are selected within each available configuration group, seed 26. '
        'They are independent of model scores; this is a spot-check queue, not an estimated defect rate.','']
    def example(row):
        index=row['configurationGroup']*5+int(row['caseID'].rsplit('v',1)[1])//25
        lines.extend([f"### {row['caseID']} — {row['role']}, {row['background']} background",'',
            f"Measured width/height growth: {row['growth'][0]:.3f}× / {row['growth'][1]:.3f}×.",'',
            '| Input | Unfocused | Focused |','|---|---|---|'])
        for arm in ('normalized','common'):
            paths=[n.USB/f'crops20-chunk-{index:03d}'/f"{row['caseID']}-{label}-{arm}.png" for label in (0,1)]
            lines.append(f'| {arm} | ![Unfocused]({paths[0]}) | ![Focused]({paths[1]}) |')
        lines.extend(['',f"[Original before]({row['frames'][0]['path']}) · [Original after]({row['frames'][1]['path']})",''])
    for row in selected:example(row)
    lines.extend(['## Model-error queue','',
        'Selected separately from the random sample. Errors suggest investigation, not an annotation override.',''])
    by_case={r['caseID']:r for r in rows};seen=set()
    for arm,r in result['models'].items():
        bad=[p for p in r['predictions'] if (p['probability']>=.85)!=bool(p['label'])]
        bad.sort(key=lambda p:abs(p['probability']-p['label']),reverse=True)
        lines.extend([f'### {arm}: {len(bad)} incorrect controls at 0.85',''])
        for p in bad[:6]:
            case=p['id'].rsplit('-',2)[0]
            lines.append(f"- {case}: label={p['label']}, score={p['probability']:.4f}")
            if case not in seen:seen.add(case)
        lines.append('')
    for case in sorted(seen):example(by_case[case])
    return '\n'.join(lines)+'\n'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan',required=True);p.add_argument('--batch',required=True)
    p.add_argument('--protocols',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();out=Path(a.output).resolve()
    n.require(out.is_relative_to(n.ROOT) and not out.exists(),'report_output_collision')
    result,rows,_=collect(json.loads(Path(a.plan).read_text()),Path(a.batch),Path(a.protocols))
    n.write(out/'summary.json',result)
    with (out/'review.md').open('x') as f:f.write(review(rows,result))
    print(json.dumps({k:result[k] for k in ('complete','acceptedPairs','cropCount','transferredBytes')}))


if __name__=='__main__':main()
