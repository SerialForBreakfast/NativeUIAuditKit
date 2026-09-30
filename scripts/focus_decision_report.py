"""Hash-bound offline focus decision report; existing scores only, never inference."""
import argparse
import hashlib
import json
from pathlib import Path
from focus_dataset_contract import ROOT, local, digest
from focus_representative_experiment import selection_metrics
from harvest_sidecar_v2 import recipe_hash
from focus_ring_baseline import score_protocol, rows as pair_rows
from focus_dataset_contract import validate_manifest


def read(path, expected):
    path=local(path); raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected: raise ValueError('changed_input')
    return json.loads(raw)


def report(protocol, result, campaign):
    seal=protocol.get('protocolSHA256')
    if not seal or digest({k:v for k,v in protocol.items() if k!='protocolSHA256'})!=seal:
        raise ValueError('invalid_protocol_seal')
    if result.get('protocolSHA256')!=seal: raise ValueError('incompatible_predictions')
    rows=[r for r in protocol['samples'] if r['split']=='validation']
    if any(r.get('originSplit') in ('test','held-out','challenge','final-challenge') for r in rows):
        raise ValueError('protected_role')
    history=result.get('history',[])
    observed=[h for h in history if h.get('validation') is not None]
    if not observed: raise ValueError('missing_terminal_scores')
    updates=[h['update'] for h in history]
    if updates!=sorted(set(updates)): raise ValueError('invalid_history')
    reports={}
    for name,snapshot in [('initial',result['initial']),('terminal',observed[-1]['validation'])]:
        measured=selection_metrics(snapshot['predictions'],rows,protocol['selection'])
        if any(snapshot.get(k)!=v for k,v in measured.items()): raise ValueError('published_metrics_mismatch')
        reports[name]=measured
    cases=campaign['cases']
    if (campaign.get('schema_version')!=1 or len(cases)!=3 or len({c['case_id'] for c in cases})!=3
            or campaign['budget']['max_targets_per_case']!=1):raise ValueError('invalid_first3_contract')
    pending=[]
    for c in cases:
        if c['split_group']!='validation' or recipe_hash(c['recipe'])!=c['recipe']['recipe_hash']:
            raise ValueError('invalid_case_role_or_hash')
        pending.append(dict(id=c['case_id'],recipeSHA256=c['recipe']['recipe_hash'],
            labels='awaiting_capture_and_QA',scores='unavailable',pairedMetrics=None))
    a=reports['initial']['real'];b=reports['terminal']['real']
    delta={lane:{k:b['strata'][lane].get(k,0)-a['strata'][lane].get(k,0) for k in ('tp','fp','fn')}
           if a['strata'][lane]['status']==b['strata'][lane]['status']=='available' else None
           for lane in ('buttons','tabs','artwork','rows','other')}
    return dict(version='focus-decision-report-v1',threshold=.85,modelExecution=False,
        scope='development; initial versus terminal same run and exact membership; not causal data ablation',
        reports=reports,stratumDeltas=delta,terminalUpdate=observed[-1]['update'],pendingCases=pending,
        modelGatePassed=False,trainingAuthorized=False,
        next='Capture/QA first3; add no scores until separately authorized inference with frozen sample/selection protocol.')


def paired_delivery(delivery, campaign):
    """Consumer-owned references to existing crop manifests/protocols/score envelopes."""
    if delivery.get('version')!='focus-decision-pairs-v1':raise ValueError('unsupported_pair_delivery')
    cases={c['case_id']:c for c in campaign['cases']};seen=set();reports=[]
    for entry in delivery['cases']:
        cid=entry['caseID']
        if cid in seen or cid not in cases:raise ValueError('duplicate_or_unexpected_case')
        seen.add(cid)
        def get(ref):return read(ROOT/ref['path'],ref['sha256'])
        manifest=get(entry['manifest'])
        validated=validate_manifest(manifest,local(ROOT/entry['manifest']['path']).parent)
        if len(manifest['pairs'])!=1 or any(r['split']!='development' for r in validated):
            raise ValueError('wrong_pair_membership_or_role')
        pair=manifest['pairs'][0]
        for scene in ('focusedScene','baselineScene'):
            if recipe_hash(pair['observationBinding'][scene]['recipe'])!=cases[cid]['recipe']['recipe_hash']:
                raise ValueError('pair_recipe_mismatch')
        models=[];names=set()
        expected_rows=pair_rows(manifest)
        hard_ids={r['pairID'] for r in validated if r['theme'] in ('light','highContrast') and r['class'] in ('imageView','collectionItem')}
        for sample in expected_rows:sample['hard']=sample['label']==0 and sample['id'].rsplit(':',1)[0] in hard_ids
        for model in entry['models']:
            name=model['name']
            if name in names:raise ValueError('duplicate_model')
            names.add(name);protocol=get(model['protocol']);scores=get(model['scores'])
            if (protocol.get('manifestSHA256')!=digest(manifest) or protocol.get('partition')!='development'
                    or protocol.get('threshold')!=.85 or protocol.get('preprocessing')!=manifest['preprocessing']
                    or protocol.get('samples')!=expected_rows):
                raise ValueError('incompatible_pair_protocol')
            measured=score_protocol(protocol,scores)
            models.append(dict(name=name,report=measured))
        if not models:raise ValueError('missing_pair_scores')
        reports.append(dict(caseID=cid,models=models,frameSelection=None,
            scope='same-control paired targets only; incomplete competitor scores cannot establish unique focus'))
    return reports


def run(protocol,p_sha,result,r_sha,campaign,c_sha,output,delivery=None,delivery_sha=None):
    output=local(output)
    if output.exists():raise ValueError('output_collision')
    p=read(protocol,p_sha);r=read(result,r_sha);c=read(campaign,c_sha)
    # Validate every scored source crop without loading a model or changing pixels.
    seen={}
    for row in p['samples']:
        if row['split']!='validation':continue
        for key in ('crop','image','frame'):
            ref=row.get(key)
            if ref:
                path=local(ROOT/ref['path'])
                if path not in seen:seen[path]=hashlib.sha256(path.read_bytes()).hexdigest()
                if seen[path]!=ref['sha256']:raise ValueError('changed_sample')
    out=report(p,r,c)
    out['pairedResults']=paired_delivery(read(delivery,delivery_sha),c) if delivery else []
    for pending in out['pendingCases']:
        found=next((r for r in out['pairedResults'] if r['caseID']==pending['id']),None)
        if found:pending.update(labels='validated_existing_manifest',scores='supplied_not_executed_here',pairedMetrics=found)
    out['inputs']=[dict(path=str(local(x).relative_to(ROOT)),sha256=h) for x,h in
                   ((protocol,p_sha),(result,r_sha),(campaign,c_sha))]
    if delivery:out['inputs'].append(dict(path=str(local(delivery).relative_to(ROOT)),sha256=delivery_sha))
    out['metricSources']=[dict(path='scripts/'+n,sha256=hashlib.sha256((ROOT/'scripts'/n).read_bytes()).hexdigest())
        for n in ('focus_decision_report.py','focus_ring_baseline.py','focus_representative_experiment.py','focus_representative_validation.py','human_focus_evaluation.py','human_focus_roles.py')]
    output.mkdir(parents=True)
    (output/'report.json').write_text(json.dumps(out,indent=2,allow_nan=False))
    lines=['# Focus decision report','',out['scope'],'','| Stratum | Focused hits/support | False positives/negatives | Misses |','|---|---:|---:|---:|']
    for lane,m in out['reports']['terminal']['real']['strata'].items():
        if m['status']!='available':lines.append(f'| {lane} | unavailable | unavailable | unavailable |');continue
        lines.append(f"| {lane} | {m.get('tp',0)}/{m.get('tp',0)+m.get('fn',0)} | {m.get('fp',0)}/{m.get('fp',0)+m.get('tn',0)} | {m.get('fn',0)} |")
    frame=out['reports']['terminal']['real']['metrics']['completeFrameSelection']
    lines+=['','Complete-frame outcomes: '+json.dumps({k:v for k,v in frame.items() if k!='frames'}),
        '', 'Retention correct: '+str(out['reports']['terminal']['retention']['retentionCorrect']),
        '', 'Initial-to-terminal deltas (same exact inputs): '+json.dumps(out['stratumDeltas']),
        '', 'Matched-pair cases with supplied scores: '+str(len(out['pairedResults']))+'/3. Others remain unavailable. No synthetic score substitution.']
    (output/'report.md').write_text('\n'.join(lines)+'\n')
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('protocol','result','campaign'):
        p.add_argument('--'+n,type=Path,required=True);p.add_argument('--'+n+'-sha256',required=True)
    p.add_argument('--delivery',type=Path);p.add_argument('--delivery-sha256')
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if bool(a.delivery)!=bool(a.delivery_sha256):p.error('delivery and delivery-sha256 must be supplied together')
    run(a.protocol,a.protocol_sha256,a.result,a.result_sha256,a.campaign,a.campaign_sha256,a.output,a.delivery,a.delivery_sha256)
