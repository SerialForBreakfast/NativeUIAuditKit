"""Compare two fixed candidates and their combination; no training or threshold tuning."""
import argparse
import time
from pathlib import Path
import focus_candidate_ranker as r
import focus_change_adaptation as change

h=r.d.h


def summary(rows):
    return dict(pairs=len(rows),rawChangeCorrect=sum(v['changeCorrect'] for v in rows),
        abstentions=sum(v['abstained'] for v in rows),
        correctEndpoints=sum(x>=.5 for v in rows for x in v['boxIoUs']),
        bothBoxes=sum(v['bothBoxesCorrect'] for v in rows),joint=sum(v['joint'] for v in rows),
        confidentFalseChanges=sum(not v['expectedChange'] and v['probability']>=.85 for v in rows))


def score(row,probability,boxes,group):
    import math
    h.require(type(probability) in (int,float) and math.isfinite(probability) and 0<=probability<=1,
        'collection104_score_probability')
    overlaps=[r.iou(p['bounds'],truth) if p else 0 for p,truth in zip(boxes,row['boxes'])]
    h.require(len(boxes)==len(overlaps)==2,'collection104_score_boxes')
    known=max(probability,1-probability)>=.85 and all(p is not None for p in boxes)
    correct=(probability>=.5)==row['changed'];both=min(overlaps)>=.5
    return dict(id=row['id'],group=group,split=row['split'],expectedChange=row['changed'],
        probability=probability,changeCorrect=correct,abstained=not known,boxIoUs=overlaps,
        bothBoxesCorrect=both,joint=bool(known and correct and both),
        condition=row.get('condition','legacy'),theme=row.get('recipe',{}).get('theme','unavailable'))


def evaluate(ready,change_result,rank_result,output,rank_protocol=None):
    start=time.monotonic();root=h.local(ready);out=h.fresh(output)
    rank_path=h.local(rank_protocol) if rank_protocol else root/'rank-protocol.json'
    cp=h.read(root/'change-protocol.json');rp=h.read(rank_path)
    for p in (cp,rp):h.require(p['protocolSHA256']==h.digest({k:v for k,v in p.items() if k!='protocolSHA256'}),'collection104_protocol_seal')
    cr=r.sealed(h.local(change_result),change.VERSION);rr=r.sealed(h.local(rank_result),r.VERSION)
    h.require(cr['protocol']==h.ref(root/'change-protocol.json') and rr['protocol']==h.ref(rank_path),
        'collection104_result_protocol')
    for v in (cr,rr):h.checked(h.ROOT,v['model'])
    rows=r.d.admitted(h.read(h.checked(h.ROOT,cp['corpus'])),h.read(h.checked(h.ROOT,cp['admission'])))
    baseline=r.sealed(h.checked(h.ROOT,cp['ranker']),'native-ranking-reference-v1')
    labels=r.sealed(h.checked(h.ROOT,rp['supervision']),'transition-candidate-supervision-v1')
    h.require(labels['corpus']==cp['corpus'] and labels['admission']==cp['admission'] and
        labels['inputs']==baseline['inputs'],'collection104_rank_data_binding')
    expected=[v['id'] for v in rows]
    h.require(all([v['id'] for v in res]==expected for res in (cr['results'],rr['results'],baseline['results'])),
        'collection104_result_membership')
    old={v['id']:v for v in baseline['results']};new={v['id']:v for v in rr['results']}
    changes={v['id']:v for v in cr['results']}
    h.require(all(abs(new[v['id']]['changeProbability']-changes[v['id']]['before'])<=1e-6 for v in rows),
        'collection104_fixed_control')
    results={}
    for name,field,rank in [('baseline','before',old),('changeOnly','after',old),
            ('rankOnly','before',new),('combined','after',new)]:
        values=[score(v,changes[v['id']][field],rank[v['id']]['selected'],
            'settingsDevelopment' if v['split']=='development' else 'oldTrain' if i<73 else 'newTrain')
            for i,v in enumerate(rows)]
        results[name]=dict(results=values,groups={g:summary([v for v in values if v['group']==g])
            for g in ('oldTrain','newTrain','settingsDevelopment')},
            newConditions={k:summary([v for v in values if v['group']=='newTrain' and v['condition']==k])
            for k in ('focus_moved','boundary_unchanged','content_only')},
            newThemes={k:summary([v for v in values if v['group']=='newTrain' and v['theme']==k])
            for k in ('light','dark')})
    base=results['baseline']['groups'];negative=cr['derivedNegatives']
    gates={}
    for name in ('changeOnly','rankOnly','combined'):
        now=results[name]['groups']
        checks=dict(oldJointRetained=now['oldTrain']['joint']>=base['oldTrain']['joint'],
            settingsJointRetained=now['settingsDevelopment']['joint']>=base['settingsDevelopment']['joint'],
            newJointImproved=now['newTrain']['joint']>base['newTrain']['joint'])
        if name!='rankOnly':checks['derivedNegativesRetained']=negative['count']==122 and negative['rawFalseChanges']==negative['abstentions']==0
        gates[name]=dict(checks=checks,passed=all(checks.values()))
    retention=None
    if rp['configuration'] in (r.RETENTION_CONFIG,r.GEOMETRY_CONFIG):
        oldframes={};newframes={};roles={}
        for index,row in enumerate(rows):
            group='settingsDevelopment' if row['split']=='development' else 'oldTrain' if index<73 else 'newTrain'
            for image,truth,a,b in zip(row['images'],row['boxes'],old[row['id']]['selected'],new[row['id']]['selected']):
                key=image['sha256']
                h.require(roles.setdefault(key,group)==group,'retention_frame_role_conflict')
                oldframes[key]=r.iou(a['bounds'],truth)>=.5;newframes[key]=r.iou(b['bounds'],truth)>=.5
        unique={group:dict(frames=sum(v==group for v in roles.values()),
            beforeCorrect=sum(oldframes[k] for k,v in roles.items() if v==group),
            afterCorrect=sum(newframes[k] for k,v in roles.items() if v==group),
            lostPreviouslyCorrect=sum(oldframes[k] and not newframes[k] for k,v in roles.items() if v==group))
            for group in ('oldTrain','newTrain','settingsDevelopment')}
        expected_train={k for k,v in roles.items() if v!='settingsDevelopment'}
        h.require(set(rr['trainingFrameIDs'])==expected_train and len(rr['trainingFrameIDs'])==178,
            'retention_optimizer_membership')
        # Verify checkpoint bytes independently of the trainer's summary fields.
        torch=r.d.torch_runtime()
        original=torch.load(h.checked(h.ROOT,rp['initializer']),map_location='cpu',weights_only=True)
        candidate=torch.load(h.checked(h.ROOT,rr['model']),map_location='cpu',weights_only=True)
        frozen_names=['2.bias','2.weight'] if rp['configuration']==r.RETENTION_CONFIG else []
        readout_equal=all(torch.equal(original['state'][k],candidate['state'][k]) for k in frozen_names)
        checks=dict(oldFramesRetained=unique['oldTrain']['lostPreviouslyCorrect']==0,
            settingsFramesRetained=unique['settingsDevelopment']['lostPreviouslyCorrect']==0,
            newFramesImproved=unique['newTrain']['afterCorrect']>unique['newTrain']['beforeCorrect'],
            newJointImproved=results['combined']['groups']['newTrain']['joint']>results['changeOnly']['groups']['newTrain']['joint'],
            settingsJointRetained=results['combined']['groups']['settingsDevelopment']['joint']>=results['changeOnly']['groups']['settingsDevelopment']['joint'],
            frozenReadout=readout_equal)
        if rp['configuration']==r.GEOMETRY_CONFIG:
            inputs=r.bank(h.checked(h.ROOT,rp['bank']))[1]
            r.geometry_targets(inputs,rows)
            checks.pop('frozenReadout')
            checks['geometryConsistent']=True
        retention=dict(uniqueFrames=unique,checks=checks,passed=all(checks.values()),
            changeControl='DTM025',comparison='DTM020_vs_DTM027' if rp['configuration']==r.RETENTION_CONFIG else 'DTM020_vs_geometry_candidate',settingsNeverOptimized=True,
            verifiedFrozenParameterNames=frozen_names,
            trainerFrozenNamesMatch=rr['frozenParameterNames']==frozen_names)
    out.mkdir(parents=True)
    report=dict(version='collection104-evaluation-v1',**h.FLAGS,
        changeResult=h.ref(h.local(change_result)),rankResult=h.ref(h.local(rank_result)),
        corpus=cp['corpus'],admission=cp['admission'],comparisons=results,developmentAdvancement=gates,
        derivedNegatives=negative,retentionAdvancement=retention,elapsedSeconds=time.monotonic()-start,
        implementation=h.ref(Path(__file__)),
        limitation='All Fixture results are training fit; Settings is exposed development. No independent final, live TTR qualification, export or promotion.')
    h.write(out/'evaluation.json',report,sealed=True)
    for name,value in results.items():print(name,value['groups'])
    print(gates)
    if retention:print('retention',retention)
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ('ready','change-result','rank-result','output'):p.add_argument('--'+flag,required=True)
    p.add_argument('--rank-protocol')
    a=p.parse_args();evaluate(a.ready,a.change_result,a.rank_result,a.output,a.rank_protocol)
