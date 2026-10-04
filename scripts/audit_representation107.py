"""Label-bound feature adequacy audit; no fit, native capture or new data admission."""
import argparse
from collections import defaultdict,Counter
from pathlib import Path
import hashlib
import time
import numpy as np
import diagnose_retention105 as diagnosis

r=diagnosis.r;h=r.d.h


def collisions(data,labels,indices):
    buckets=defaultdict(list)
    for i in indices:buckets[hashlib.sha256(data[i].tobytes()).hexdigest()].append(i)
    return [dict(sha256=k,indices=v,positive=sum(bool(labels[i]) for i in v),negative=sum(not labels[i] for i in v))
            for k,v in buckets.items() if len({bool(labels[i]) for i in v})>1]


def nearest(data,query,reference,frame_ids):
    """Exact RMS nearest neighbor, excluding same-frame proposals; deterministic ties."""
    result=[];reference=np.asarray(reference,dtype=np.int64)
    for i in query:
        eligible=reference[np.array([frame_ids[j]!=frame_ids[i] for j in reference])]
        h.require(len(eligible)>0,'audit_no_other_frame_reference')
        # Direct subtraction avoids cancellation errors for almost-identical crops.
        distances=np.mean((data[eligible].astype(np.float64)-data[i])**2,axis=1)
        which=int(np.argmin(distances));result.append(dict(query=int(i),neighbor=int(eligible[which]),rms=float(np.sqrt(distances[which]))))
    return result


def audit(output):
    start=time.monotonic();out=h.fresh(output)
    protocol,bank,inputs,pixels,rows,positives=diagnosis.load()
    features=r.features(pixels,inputs,r.COLLECTION_CONFIG)
    oldframes={im['sha256'] for row in rows[:73] if row['split']=='train' for im in row['images']}
    labels=[];frame_ids=[];roles=[];items=[]
    for frame in inputs['frames']:
        group='settingsDevelopment' if frame['split']=='development' else 'oldTrain' if frame['id'] in oldframes else 'newTrain'
        for c in frame['candidates']:
            labels.append(c['id'] in positives[frame['id']]);frame_ids.append(frame['id']);roles.append(frame['split'])
            items.append(dict(frameID=frame['id'],candidateID=c['id'],group=group,positive=labels[-1],bounds=c['bounds']))
    h.require(len(items)==len(pixels) and sum(f['split']=='train' for f in inputs['frames'])==178,'audit_membership')
    training=[i for i,v in enumerate(roles) if v=='train']
    development=[i for i,v in enumerate(roles) if v=='development']
    queries=[i for i,v in enumerate(labels) if v]
    reference_pos=[i for i in training if labels[i]];reference_neg=[i for i in training if not labels[i]]
    neighbors={}
    for name,data in [('rgb16',pixels),('rgb16_normalized_size',features)]:
        positive=nearest(data,queries,reference_pos,frame_ids);negative=nearest(data,queries,reference_neg,frame_ids)
        neighbors[name]=[dict(query=a['query'],group=items[a['query']]['group'],nearestPositive=a,nearestNegative=b,
            closerToNegative=b['rms']<a['rms']) for a,b in zip(positive,negative)]
    collision_report={}
    for name,data in [('rgb16',pixels),('rgb16_normalized_size',features)]:
        collision_report[name]=dict(training=collisions(data,labels,training),
            development=collisions(data,labels,development),all=collisions(data,labels,range(len(data))))
    # Exploratory fixed distance contrast, excluding the query's own frame.
    # No learned weights/thresholds or independent model-replacement claim.
    dev_pos=nearest(features,range(len(features)),reference_pos,frame_ids)
    dev_neg=nearest(features,range(len(features)),reference_neg,frame_ids)
    contrast={a['query']:b['rms']-a['rms'] for a,b in zip(dev_pos,dev_neg)}
    contrast_frames=[]
    for frame,a,b in diagnosis.groups(inputs):
        selected=min(range(a,b),key=lambda i:(-contrast[i],items[i]['candidateID']))
        contrast_frames.append(dict(frameID=frame['id'],group=items[a]['group'],selectedCandidateID=items[selected]['candidateID'],
            correct=bool(labels[selected]),contrast=contrast[selected]))
    sensitivity={}
    for group in ('oldTrain','newTrain'):
        indices=[i for i in training if items[i]['group']==group]
        pos=nearest(features,development,[i for i in indices if labels[i]],frame_ids)
        neg=nearest(features,development,[i for i in indices if not labels[i]],frame_ids)
        values={a['query']:b['rms']-a['rms'] for a,b in zip(pos,neg)}
        correct=0
        for f,a,b in diagnosis.groups(inputs):
            if f['split']=='development':
                selected=min(range(a,b),key=lambda i:(-values[i],items[i]['candidateID']));correct+=labels[selected]
        sensitivity[group]=dict(referenceFrames=len({frame_ids[i] for i in indices}),settingsCorrect=correct,settingsFrames=9)
    summary={}
    for group in ('oldTrain','newTrain','settingsDevelopment'):
        q=[i for i in queries if items[i]['group']==group]
        summary[group]=dict(frames=len({v['frameID'] for v in items if v['group']==group}),
            candidates=sum(v['group']==group for v in items),positiveCandidates=len(q),
            neighbors={name:dict(closerToTrainingNegative=sum(v['closerToNegative'] for v in values if v['group']==group),
                medianPositiveRMS=float(np.median([v['nearestPositive']['rms'] for v in values if v['group']==group])),
                medianNegativeRMS=float(np.median([v['nearestNegative']['rms'] for v in values if v['group']==group]))) for name,values in neighbors.items()})
    out.mkdir(parents=True)
    report=dict(version='rank-representation107-audit-v1',**h.FLAGS,bank=protocol['bank'],supervision=protocol['supervision'],
        sourceProtocol=diagnosis.h.ref(diagnosis.READY/'rank-protocol.json'),summary=summary,items=items,
        collisionGroups=collision_report,positiveNearestNeighbors=neighbors,referenceRole='train_only_other_frames',
        exploratoryFrameDistanceContrast=contrast_frames,settingsReferenceCohortSensitivity=sensitivity,
        relatedRecipesMayShareAncestry=True,trainingLaunched=False,nativeCropInvocations=0,
        elapsedSeconds=time.monotonic()-start,implementation=h.ref(Path(__file__)),
        limitation='Nearest-neighbor distances are descriptive; no learned metric, new labels, calibration or independent generalization claim. No collision does not prove representation adequacy.')
    h.write(out/'audit.json',report,sealed=True)
    print(summary)
    print('collision groups',{name:{role:len(v) for role,v in groups.items()} for name,groups in collision_report.items()})
    print('elapsed',report['elapsedSeconds'])
    print('Fixed-distance diagnostic',{g:sum(v['correct'] for v in contrast_frames if v['group']==g) for g in summary})
    print('Settings reference-cohort sensitivity',sensitivity)
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();audit(a.output)
