"""Offline before-anchored focus-change probe. Never predicts from truth geometry."""
import argparse
import base64
from collections import Counter, defaultdict
import itertools
import math
import time

import numpy as np
from PIL import Image
import human_annotation_review as h
import focus_context_experiment as context
import focus_transfer_experiment as transfer
import focus_runtime as native

VERSION = 'focus-paired-growth-v1'
POLICY = dict(growth=1.05, shrink=.95, edge=.015, axisTolerance=.06,
              maxCenterDrift=8, brightness=.08, matching=.15, modelHigh=.85, modelLow=.15)


def box(b):
    h.require(len(b)==4 and all(type(v) in (int,float) and math.isfinite(v) for v in b)
              and b[0]>=0 and b[1]>=0 and b[2]>0 and b[3]>0, 'invalid_pair_box')


def match(before, after):
    """Mutual unique geometry matches; no focus labels or local IDs consulted."""
    def candidates(a, bs):
        box(a['bounds']);x,y,w,ht=a['bounds']; result=[]
        for b in bs:
            box(b['bounds']);u,v,q,r=b['bounds']
            if a['control']!=b['control']:continue
            distance=math.hypot(x+w/2-u-q/2,y+ht/2-v-r/2)
            if distance<=POLICY['matching']*min(w,ht,q,r):result.append(b['id'])
        return result
    forward={a['id']:candidates(a,after) for a in before}
    backward={a['id']:candidates(a,before) for a in after}
    return [(a,bs[0]) for a,bs in forward.items() if len(bs)==1 and backward[bs[0]]==[a]]


def edges(rgb, before):
    # Directional edge profiles retain rectangular-body enlargement in a fixed window.
    y=np.asarray(rgb,dtype=float) @ np.array([.2126,.7152,.0722])/255
    profiles=(np.abs(np.diff(y[64:192],axis=1)).mean(0),
              np.abs(np.diff(y[:,64:192],axis=0)).mean(1))
    ranges=((24,48),(208,232)) if before else ((8,64),(192,248))
    positions=[]; strengths=[]
    for profile in profiles:
        pair=[]
        for lo,hi in ranges:
            i=lo+int(np.argmax(profile[lo:hi]));pair.append(i);strengths.append(float(profile[i]))
        positions.append(pair)
    return positions,min(strengths)


def predict(before, after, *, settled, matched, stable_context, fresh, clipped=False):
    if not (settled and matched and stable_context and fresh) or clipped:
        return dict(growth='unavailable',brightness='unavailable',combined='unavailable',reason='context_or_geometry')
    a=np.asarray(before.convert('RGB'));b=np.asarray(after.convert('RGB'))
    h.require(a.shape==b.shape==(256,256,3),'pair_crop_dimensions')
    if np.array_equal(a,b):
        return dict(growth='unchanged',brightness='unchanged',combined='unchanged',reason='identical_pixels')
    ae,ascore=edges(a,True);be,bscore=edges(b,False)
    ratios=[(q[1]-q[0])/(p[1]-p[0]) for p,q in zip(ae,be)]
    drift=max(abs(sum(p)-sum(q))/2 for p,q in zip(ae,be))
    supported=min(ascore,bscore)>=POLICY['edge'] and abs(ratios[0]-ratios[1])<=POLICY['axisTolerance'] and drift<=POLICY['maxCenterDrift']
    growth='unknown'
    if supported:
        if min(ratios)>=POLICY['growth']:growth='arrival'
        elif max(ratios)<=POLICY['shrink']:growth='departure'
    delta=float(((b[32:224,32:224].astype(float)-a[32:224,32:224]) @ np.array([.2126,.7152,.0722])).mean()/255)
    brightness='arrival' if delta>=POLICY['brightness'] else 'departure' if delta<=-POLICY['brightness'] else 'unknown'
    signals={x for x in (growth,brightness) if x!='unknown'}
    combined=next(iter(signals)) if len(signals)==1 else 'unknown'
    return dict(growth=growth,brightness=brightness,combined=combined,ratios=ratios,
                edgeStrength=min(ascore,bscore),centerDrift=drift,lumaDelta=delta,
                reason='conflict' if len(signals)>1 else 'measured')


def truth(a,b):
    h.require(type(a) is int and type(b) is int and a in (0,1) and b in (0,1),'invalid_pair_label')
    return 'arrival' if b>a else 'departure' if b<a else 'unchanged'


def score_direction(a,b):
    for q in (a,b):h.require(type(q) in (int,float) and math.isfinite(q) and 0<=q<=1,'invalid_baseline_score')
    states=[1 if q>=.85 else 0 if q<=.15 else None for q in (a,b)]
    return 'unknown' if None in states else truth(*states)


def build(output):
    p,_=transfer.parent();geoms={r['id']:r for r in transfer.geometry(p)}
    samples={r['id']:r for r in p['samples']};groups=defaultdict(list);exclusions=[];pairs=[]
    for r in p['samples']:
        if r['split']!='train':continue
        if r.get('pairID'):key=('pair',r.get('sourceID'),r['pairID'])
        elif r.get('sourceElementID'):key=('native',r['sourceID'],r['sourceElementID'])
        else:exclusions.append(dict(id=r['id'],reason='no_cross_frame_identity'));continue
        groups[key].append(r)
    for key,rows in sorted(groups.items()):
        states={y:sorted((r for r in rows if r['label']==y),key=lambda r:r['id']) for y in (0,1)}
        if not all(states.values()):
            exclusions.append(dict(group=list(key),reason='missing_state',members=len(rows)));continue
        # One deterministic contrast per source/control; repeated observations are not independence.
        a,b=states[0][0],states[1][0]
        if a['control']!=b['control']:raise ValueError('native_pair_role_mismatch')
        pairs.append(dict(lane='native-training-contrast',a=a['id'],b=b['id'],group=list(key)))
    retention=defaultdict(dict);frames=defaultdict(list)
    for r in p['samples']:
        if r['split']!='validation':continue
        if r['use']=='retention-validation':retention[r['elementID']][r['label']]=r
        elif r.get('frameID'):frames[(r['family'],r['frameID'])].append(r)
    for key,states in sorted(retention.items()):
        h.require(set(states)=={0,1},'retention_pair_missing')
        pairs.append(dict(lane='retention-contrast',a=states[0]['id'],b=states[1]['id'],group=['retention',key]))
    frame_pairs=[]
    for (fa,a),(fb,b) in itertools.combinations(sorted(frames.items()),2):
        if fa[0]!=fb[0] or len(a)!=len(b):continue
        matches=match(a,b)
        group=['real',fa[0],fa[1],fb[1]]
        frame_pairs.append(dict(group=group,before=len(a),after=len(b),matched=len(matches)))
        for x,y in matches:pairs.append(dict(lane='real-development-contrast',a=x,b=y,group=group))
    cases=[]
    for pair in pairs:
        x,y=pair['a'],pair['b'];ga,gb=geoms[x],geoms[y]
        if ga['sourceSize']!=gb['sourceSize']:
            exclusions.append(dict(pair=pair,reason='different_viewports'));continue
        for role,a,b in (('forward',x,y),('reverse',y,x),('identical-a',x,x),('identical-b',y,y)):
            g=geoms[a];W,H=g['sourceSize'];bx,by,bw,bh=g['bounds']
            clipped=bx-.16*bw<0 or by-.16*bh<0 or bx+1.16*bw>W or by+1.16*bh>H
            cases.append(dict(id=h.digest([pair,role]),lane=pair['lane'],group=pair['group'],kind=role,
                before=a,after=b,anchor=g['bounds'],clipped=clipped,
                truth=truth(samples[a]['label'],samples[b]['label'])))
    doc=dict(version=VERSION,policy=POLICY,parent=h.ref(h.ROOT/transfer.PARENT),
        authority=h.ref(h.ROOT/'Research/Plans/FocusPaired11.md'),geometry=geoms,
        cases=cases,exclusions=exclusions,framePairs=frame_pairs,
        samples={i:dict(label=r['label'],control=r['control'],split=r['split'],
                        use=r['use'],family=r.get('family',r.get('sourceID')),crop=r['crop']) for i,r in samples.items()},
        scope='static contrasts, starting oracle geometry; no action causality or independent holdout',
        genuineActionPairs=0)
    doc['protocolSHA256']=h.digest(doc)
    out=h.fresh(output);out.mkdir(parents=True);h.write(out/'inventory.json',doc)
    print('cases',dict(Counter(r['lane'] for r in cases)),'exclusions',len(exclusions),'frame pairs',len(frame_pairs),flush=True)


def read_inventory(path):
    doc=context.sealed(h.ref(h.local(path)))
    h.require(doc['version']==VERSION and doc['policy']==POLICY,'paired_policy_changed')
    h.checked(h.ROOT,doc['authority']);base=context.sealed(doc['parent'])
    h.require(doc['parent']==h.ref(h.ROOT/transfer.PARENT),'paired_parent_changed')
    h.require(doc['geometry']=={r['id']:r for r in transfer.geometry(base)},'paired_geometry_changed')
    h.require(set(doc['samples'])=={r['id'] for r in base['samples']},'paired_membership_changed')
    for r in base['samples']:
        s=doc['samples'][r['id']]
        h.require((s['label'],s['split'],s['crop'])==(r['label'],r['split'],r['crop']),'paired_label_changed')
        h.require((s['control'],s['use'],s['family'])==(r['control'],r['use'],r.get('family',r.get('sourceID'))),'paired_context_changed')
    h.require(len({r['id'] for r in doc['cases']})==len(doc['cases']),'duplicate_pair_case')
    for c in doc['cases']:
        a,b=c['before'],c['after'];box(c['anchor'])
        h.require(c['anchor']==doc['geometry'][a]['bounds'] and c['truth']==truth(doc['samples'][a]['label'],doc['samples'][b]['label']), 'paired_case_binding')
        h.require(doc['samples'][a]['split']==doc['samples'][b]['split'], 'cross_split_pair')
    return doc


def crop_key(g,bounds):return h.digest([g['original'],bounds])


def frame_decision(rows, arm):
    """Exactly one correct arrival; ambiguity is not silently resolved by ranking."""
    expected=[r['after'] for r in rows if r['truth']=='arrival']
    selected=[r['after'] for r in rows if r['arms'][arm]=='arrival']
    if len(selected)>1:return 'ambiguous'
    if not selected:return 'safe_no_arrival' if not expected else 'abstained'
    return 'correct' if selected==expected else 'wrong'


def frame_analysis(decisions, inventory, baseline_frames):
    eligibility={r['id']:r['outcome']!='unavailable' for r in baseline_frames}
    counts={tuple(r['group']):r for r in inventory['framePairs']}
    groups=defaultdict(list)
    for row in decisions:
        if row['lane']=='real-development-contrast' and row['kind'] in ('forward','reverse'):
            groups[(tuple(row['group']),row['kind'])].append(row)
    result=[]
    for (group,direction),rows in sorted(groups.items()):
        c=counts[group];complete=c['before']==c['after']==c['matched']
        eligible=complete and all(eligibility.get(f,False) for f in group[2:])
        result.append(dict(group=list(group),direction=direction,matched=len(rows),
            eligible=eligible,reason='' if eligible else 'partial_correspondence_or_existing_frame_ineligible',
            outcomes={arm:frame_decision(rows,arm) for arm in rows[0]['arms']}))
    return result


def render(inventory,output):
    doc=read_inventory(inventory);items={};runtime=native.identity();started=time.monotonic()
    for c in doc['cases']:
        for role in ('before','after'):
            g=doc['geometry'][c[role]];key=crop_key(g,c['anchor'])
            if key not in items:
                items[key]=dict(id=key,path=str(h.checked(h.ROOT,g['original'])),sha256=g['original']['sha256'],bounds=c['anchor'])
    out=h.fresh(output);out.mkdir(parents=True);refs={}
    for batch in native.bounded_batches(list(items.values())):
        h.require(time.monotonic()-started<1800,'paired_render_deadline')
        for r in native.invoke(batch)['results']:
            path=out/(r['id']+'.png')
            with path.open('xb') as f:f.write(base64.b64decode(r['png'],validate=True))
            refs[r['id']]=h.ref(path)
        if len(refs)%100<16:print('fixed-window crops',len(refs),'/',len(items),flush=True)
    h.require(native.identity()==runtime,'paired_runtime_changed')
    h.write(out/'receipt.json',dict(version=VERSION,inventory=h.ref(h.local(inventory)),
                                   crops=refs,runtime=runtime,elapsedSeconds=time.monotonic()-started))


def evaluate(inventory,rendered,output):
    doc=read_inventory(inventory);rr=context.read(h.ref(h.local(rendered)))
    h.require(rr['inventory']==h.ref(h.local(inventory)) and rr['runtime']==native.identity(),'paired_render_binding')
    base=h.read(h.ROOT/'NativeUITrainer/focus_ring_runs/fdr021-reviewed-contrast/experiment-result.json',limit=32*1024**2)
    selected=next(s for s in base['history'] if s['update']==base['selectedUpdate'])
    scores={p['id']:p for p in selected['validation']['predictions']}
    images={};decisions=[];started=time.monotonic();summary=defaultdict(Counter)
    def im(key):
        if key not in images:
            with Image.open(h.checked(h.ROOT,rr['crops'][key])) as image:images[key]=image.convert('RGB')
        return images[key]
    for c in doc['cases']:
        a,b=c['before'],c['after'];ga,gb=doc['geometry'][a],doc['geometry'][b]
        before=im(crop_key(ga,c['anchor']));after=im(crop_key(gb,c['anchor']))
        pred=predict(before,after,settled=True,matched=True,stable_context=True,fresh=True,clipped=c['clipped'])
        # Normalization control uses historical independently resized crops, same pixel rule.
        with Image.open(h.checked(h.ROOT,doc['samples'][a]['crop'])) as ai, Image.open(h.checked(h.ROOT,doc['samples'][b]['crop'])) as bi:
            normalized=predict(ai,bi,settled=True,matched=True,stable_context=True,fresh=True,clipped=c['clipped'])
        arms={k:pred[k] for k in ('growth','brightness','combined')}
        arms['normalized-growth']=normalized['growth']
        ratio=[gb['bounds'][i]/ga['bounds'][i] for i in (2,3)]
        arms['oracle-box-growth']='arrival' if min(ratio)>=1.05 else 'departure' if max(ratio)<=.95 else 'unknown'
        if a==b:arms['oracle-box-growth']='unchanged'
        if a in scores and b in scores:
            h.require(scores[a]['label']==doc['samples'][a]['label'] and scores[b]['label']==doc['samples'][b]['label'],'baseline_label_mismatch')
            arms['fdr021']=score_direction(scores[a]['probability'],scores[b]['probability'])
        row=dict(c,arms=arms,measurement=pred);decisions.append(row)
        for arm,p in arms.items():
            outcome='abstained' if p in ('unknown','unavailable') else 'correct' if p==c['truth'] else 'wrong'
            key='/'.join((c['lane'],'identical' if c['kind'].startswith('identical') else 'contrast',c['truth'],arm))
            summary[key][outcome]+=1
    out=h.fresh(output);out.mkdir(parents=True)
    h.write(out/'result.json',dict(version=VERSION,inventory=h.ref(h.local(inventory)),render=h.ref(h.local(rendered)),
        decisions=decisions,summary=dict(summary),elapsedSeconds=time.monotonic()-started,
        frameComparisons=frame_analysis(decisions,doc,selected['validation']['real']['metrics']['completeFrameSelection']['frames']),
        baseline=h.ref(h.ROOT/'NativeUITrainer/focus_ring_runs/fdr021-reviewed-contrast/experiment-result.json'),
        releaseEligible=False,modelTraining=False,genuineTransitionAccuracy=None))
    print('evaluated',len(decisions),'cases',round(time.monotonic()-started,2),'seconds',flush=True)
    for key,value in summary.items():
        if key.startswith('real-development') and '/identical/' not in key:print(key,dict(value))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['inventory','render','evaluate'])
    p.add_argument('--inventory');p.add_argument('--rendered');p.add_argument('--output',required=True)
    a=p.parse_args()
    if a.mode=='inventory':build(a.output)
    elif a.mode=='render':render(a.inventory,a.output)
    else:evaluate(a.inventory,a.rendered,a.output)


if __name__=='__main__':main()
