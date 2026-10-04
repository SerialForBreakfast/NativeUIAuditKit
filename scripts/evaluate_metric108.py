"""Build, reload and evaluate one fixed metric bank using existing rank/eval paths."""
import argparse
from pathlib import Path
import resource
import time
import numpy as np
import diagnose_retention105 as diagnosis
import evaluate_collection104 as evaluation
import focus_metric_reference as metric
from audit_representation107 import nearest

r = diagnosis.r
h = r.d.h
AUDIT = h.ROOT/'reports/work/RANK-REPRESENTATION-107/artifacts/audit-qualified/audit.json'


def load_bank(path, expected_sources, expected_members):
    manifest = r.sealed(path, metric.VERSION)
    h.require(manifest['sources'] == expected_sources and manifest['members'] == expected_members,
              'metric_bank_provenance_changed')
    h.require(manifest['encoding'] == 'production-crop256-rgb16-bilinear-normalized-size-v1' and
              manifest['implementation'] == h.ref(Path(metric.__file__)), 'metric_encoding_changed')
    tensor = np.load(h.checked(h.ROOT, manifest['tensor']), allow_pickle=False)
    return manifest, metric.ReferenceScorer(tensor, manifest['members'])


def run(output):
    start = time.monotonic()
    out = h.fresh(output)
    protocol, _, inputs, pixels, rows, positives = diagnosis.load()
    features = r.features(pixels, inputs, r.COLLECTION_CONFIG)
    oldframes = {im['sha256'] for row in rows[:73] if row['split']=='train' for im in row['images']}
    ancestry = {}
    for row in rows:
        for image in row['images']:
            h.require(ancestry.setdefault(image['sha256'], row['group']) == row['group'], 'metric_ancestry_conflict')
    members, indices, items = [], [], []
    for frame, a, b in diagnosis.groups(inputs):
        group = 'settingsDevelopment' if frame['split']=='development' else 'oldTrain' if frame['id'] in oldframes else 'newTrain'
        for i, candidate in enumerate(frame['candidates'], a):
            item = dict(frameID=frame['id'], candidateID=candidate['id'], role=frame['split'],
                        ancestry=ancestry[frame['id']], positive=candidate['id'] in positives[frame['id']])
            items.append(dict(**item, group=group))
            if frame['split']=='train':
                members.append(item); indices.append(i)
    h.require(len(members)==4799 and len({v['frameID'] for v in members})==178, 'metric_frozen_membership')
    sources = dict(bank=protocol['bank'], supervision=protocol['supervision'],
                   protocol=h.ref(diagnosis.READY/'rank-protocol.json'))
    out.mkdir(parents=True)
    np.save(out/'references.npy', features[indices], allow_pickle=False)
    h.write(out/'bank.json', dict(version=metric.VERSION, **h.FLAGS, sources=sources, members=members,
        tensor=h.ref(out/'references.npy'), implementation=h.ref(Path(metric.__file__)),
        encoding='production-crop256-rgb16-bilinear-normalized-size-v1'), sealed=True)
    manifest, scorer = load_bank(out/'bank.json', sources, members)
    audit = r.sealed(AUDIT, 'rank-representation107-audit-v1')
    h.require(audit['bank']==protocol['bank'] and audit['supervision']==protocol['supervision'], 'metric_audit_binding')
    prior = {v['frameID']:v for v in audit['exploratoryFrameDistanceContrast']}
    controls = dict(DTM020=r.sealed(h.checked(h.ROOT,protocol['reference']), 'native-ranking-reference-v1'),
                    DTM027=r.sealed(h.ROOT/'NativeUITrainer/focus_ring_runs/retention105-dtm027/result.json', r.VERSION))
    retained_protocol = h.read(h.checked(h.ROOT,controls['DTM027']['protocol']))
    h.require(retained_protocol['protocolSHA256']==h.digest({k:v for k,v in retained_protocol.items() if k!='protocolSHA256'}) and
              retained_protocol['bank']==protocol['bank'] and retained_protocol['supervision']==protocol['supervision'],
              'metric_rank_control_binding')
    change_path = h.ROOT/'NativeUITrainer/focus_ring_runs/collection104-dtm025/result.json'
    change = r.sealed(change_path, evaluation.change.VERSION)
    cp = h.read(diagnosis.READY/'change-protocol.json')
    labels = r.sealed(h.checked(h.ROOT,protocol['supervision']), 'transition-candidate-supervision-v1')
    h.require(change['protocol']==h.ref(diagnosis.READY/'change-protocol.json') and
              labels['corpus']==cp['corpus'] and labels['admission']==cp['admission'], 'metric_change_binding')
    expected = [v['id'] for v in rows]
    for doc in [change, *controls.values()]:
        h.require([v['id'] for v in doc['results']]==expected, 'metric_control_membership')
    h.checked(h.ROOT,change['model'])
    selections = {}
    for name, doc in controls.items():
        selections[name] = {}
        for row, result in zip(rows,doc['results']):
            for image, selected in zip(row['images'], result['selected']):
                key = image['sha256']
                h.require(selections[name].setdefault(key,selected)==selected, 'metric_control_inconsistent')
    details, latency = {}, {}
    torch = r.d.torch_runtime(); torch.set_num_threads(2)
    for name, ref in [('DTM020',protocol['initializer']),('DTM027',controls['DTM027']['model'])]:
        state=torch.load(h.checked(h.ROOT,ref),map_location='cpu',weights_only=True)
        network=r.model(torch,state['configuration']); network.load_state_dict(state['state'],strict=True); network.eval()
        timing=[]
        for frame,a,b in diagnosis.groups(inputs):
            tick=time.perf_counter()
            with torch.inference_mode(): scores=network(torch.from_numpy(features[a:b])).flatten().numpy()
            timing.append(time.perf_counter()-tick)
            h.require(r.choose(frame['candidates'],scores)==selections[name][frame['id']], 'metric_neural_control_replay')
        latency[name]=dict(firstFrameSeconds=timing[0],medianSeconds=float(np.median(timing)),
                          p95Seconds=float(np.percentile(timing,95)),totalSeconds=sum(timing),
                          preprocessingIncluded=False,threads=2)
    for mode, exclude in [('selfAllowedReplay',False), ('sameFrameExcluded',True)]:
        selections[mode], details[mode], timing = {}, [], []
        for frame, a, b in diagnosis.groups(inputs):
            tick = time.perf_counter()
            scored = scorer.score(features[a:b], [frame['id']]*(b-a), exclude_same_frame=exclude)
            timing.append(time.perf_counter()-tick)
            selected = r.choose(frame['candidates'], [v['score'] for v in scored])
            index = next(i for i,c in enumerate(frame['candidates']) if c['id']==selected['id'])
            correct = selected['id'] in positives[frame['id']]
            if exclude:
                ref = prior[frame['id']]
                h.require(selected['id']==ref['selectedCandidateID'] and scored[index]['score']==ref['contrast'], 'metric_naive_replay_mismatch')
            selections[mode][frame['id']] = selected
            details[mode].append(dict(frameID=frame['id'], group=items[a]['group'], correct=correct,
                candidates=[dict(candidateID=c['id'],positive=c['id'] in positives[frame['id']],**s)
                            for c,s in zip(frame['candidates'],scored)]))
        latency[mode] = dict(firstFrameSeconds=timing[0], medianSeconds=float(np.median(timing)),
            p95Seconds=float(np.percentile(timing,95)), totalSeconds=sum(timing),
            frames=len(timing), candidates=len(features), preprocessingIncluded=False)
        print(mode, {g:sum(v['correct'] for v in details[mode] if v['group']==g)
                     for g in ('oldTrain','newTrain','settingsDevelopment')}, latency[mode], flush=True)
    # Independent unchunked oracle checks every score, not just the selected box.
    oracle_start=time.monotonic()
    frame_ids=[v['frameID'] for v in items]
    pos=nearest(features,range(len(features)),[i for i in indices if items[i]['positive']],frame_ids)
    neg=nearest(features,range(len(features)),[i for i in indices if not items[i]['positive']],frame_ids)
    measured=[v for frame in details['sameFrameExcluded'] for v in frame['candidates']]
    h.require(all(v['positiveRMS']==a['rms'] and v['negativeRMS']==b['rms'] and
                  v['score']==b['rms']-a['rms'] for v,a,b in zip(measured,pos,neg)), 'metric_all_score_parity')
    oracle_seconds=time.monotonic()-oracle_start
    comparisons = {}
    for name, selected in selections.items():
        scored = [evaluation.score(row, change['results'][i]['after'],
                  [selected[im['sha256']] for im in row['images']],
                  'settingsDevelopment' if row['split']=='development' else 'oldTrain' if i<73 else 'newTrain')
                  for i,row in enumerate(rows)]
        comparisons[name] = dict(results=scored, groups={g:evaluation.summary([v for v in scored if v['group']==g])
                               for g in ('oldTrain','newTrain','settingsDevelopment')})
    lost = []
    for detail in details['sameFrameExcluded']:
        if detail['group']=='oldTrain' and not detail['correct']:
            frame = next(f for f in inputs['frames'] if f['id']==detail['frameID'])
            candidates = {c['id']:c for c in frame['candidates']}
            ranked = sorted(detail['candidates'],key=lambda v:(-v['score'],v['candidateID']))
            implicated = [v for v in ranked if v['positive'] or v==ranked[0]]
            truths=[dict(pairID=row['id'],endpoint=j,bounds=row['boxes'][j])
                    for row in rows for j,im in enumerate(row['images']) if im['sha256']==frame['id']]
            lost.append(dict(frame=frame, groundTruth=truths, affectedPairs=[v for v in comparisons['sameFrameExcluded']['results']
                if any(im['sha256']==frame['id'] for row in rows if row['id']==v['id'] for im in row['images'])],
                candidates=[dict(**v,bounds=candidates[v['candidateID']]['bounds'],
                    groundTruthIoUs=[r.iou(candidates[v['candidateID']]['bounds'],t['bounds']) for t in truths],
                    nearestPositive=scorer.members[v['positiveReference']],
                    nearestNegative=scorer.members[v['negativeReference']]) for v in implicated]))
    correct = {mode:{v['frameID']:v['correct'] for v in values} for mode,values in details.items()}
    retention = {}
    for group in ('oldTrain','newTrain','settingsDevelopment'):
        frames = [f for f,a,b in diagnosis.groups(inputs) if items[a]['group']==group]
        retention[group] = dict(frames=len(frames), correct=sum(correct['sameFrameExcluded'][f['id']] for f in frames),
            lostPreviouslyCorrect=sum(selections['DTM020'][f['id']]['id'] in positives[f['id']] and
                                     not correct['sameFrameExcluded'][f['id']] for f in frames))
    report = dict(version='metric108-evaluation-v1', **h.FLAGS, sources=sources, bank=h.ref(out/'bank.json'),
        changeResult=h.ref(change_path), audit=h.ref(AUDIT), implementation=h.ref(Path(__file__)),
        controls=dict(DTM020=protocol['reference'],DTM027=h.ref(h.ROOT/'NativeUITrainer/focus_ring_runs/retention105-dtm027/result.json')),
        comparisons=comparisons, retention=retention, details=details, lostOldFrames=lost, latency=latency,
        storage=dict(tensorBytes=scorer.tensor.nbytes, fileBytes=(out/'references.npy').stat().st_size,
            manifestBytes=(out/'bank.json').stat().st_size,
            distanceWorkspaceUpperBoundBytes=metric.BLOCK*metric.WIDTH*12+metric.BLOCK*8,
            processPeakRSSBytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        naiveSelectionAndSelectedScoreExact=True, all5022ScoresExact=True, oracleVerificationSeconds=oracle_seconds,
        trainingLaunched=False, nativeCropInvocations=0,
        accepted=retention['oldTrain']['correct']==122 and retention['settingsDevelopment']['lostPreviouslyCorrect']==0 and
                 retention['newTrain']['correct']>6,
        elapsedSeconds=time.monotonic()-start,
        limitation='Training replay and related-frame diagnostic; exposed Settings development only. No independent generalization, export or promotion.')
    h.write(out/'evaluation.json', report, sealed=True)
    print('retention',retention,'accepted',report['accepted'],flush=True)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True)
    run(parser.parse_args().output)
