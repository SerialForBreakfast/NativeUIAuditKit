"""Fixed training-only paired translation bank and independently seeded schedule."""
from collections import Counter
import numpy as np
import focus_direct_transition as d
from focus_pair_translation import transform,DEFAULT_POLICY,POLICIES

TRAIN_CONDITIONS=('baseline','left','right','up','down')


def bank(rows,policy=DEFAULT_POLICY):
    return banks(rows,[policy])[policy]


def banks(rows,policies):
    d.h.require(rows and len(rows)<=256 and all(r.get('split')=='train' for r in rows),'augmentation_train_only')
    d.h.require(policies and len(policies)==len(set(policies)) and set(policies)<=set(POLICIES),'augmentation_policies')
    result={policy:([],[],[],[],[]) for policy in policies}
    for r in rows:
        images=[d.pixels(ref) for ref in r['images']]
        for policy,(xs,ys,options,entries,rejected) in result.items():
            available=[]
            for condition in TRAIN_CONDITIONS:
                pair,truth=transform(images,r['boxes'],condition,policy)
                if pair is None:
                    rejected.append(dict(id=r['id'],condition=condition));continue
                available.append(len(xs));xs.append(d.encode(*pair))
                ys.append([*(v for b in truth for v in d.target_box(b,r['size'])),float(r['changed'])])
                entries.append(dict(id=r['id'],condition=condition))
            d.h.require(available and entries[available[0]]['condition']=='baseline','invalid_baseline_truth')
            options.append(available)
    return {policy:(np.stack(xs),np.asarray(ys,dtype=np.float32),options,entries,rejected)
        for policy,(xs,ys,options,entries,rejected) in result.items()}


def schedule(options,epochs,seed):
    d.h.require(options and all(v for v in options) and type(epochs)is int and epochs>0,'invalid_schedule')
    rng=np.random.default_rng(seed)
    return [[int(rng.choice(values)) for values in options] for _ in range(epochs)]


def receipt(choices,entries,rejected,policy=DEFAULT_POLICY):
    result=dict(version='paired-translation-training-v1',scheduleSHA256=d.digest(choices),
        conditions=list(TRAIN_CONDITIONS),bankMembers=entries,rejected=rejected,
        counts=dict(Counter(entries[i]['condition'] for epoch in choices for i in epoch)),
        epochs=len(choices),sampledPairs=sum(map(len,choices)),seed=42,
        newCorpusAdmitted=False,trainingOnly=True)
    if policy!=DEFAULT_POLICY:result.update(version='paired-augmentation-training-v2',policy=policy)
    return result
