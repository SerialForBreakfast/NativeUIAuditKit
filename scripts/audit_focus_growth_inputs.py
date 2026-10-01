"""Offline retained-input audit: weighting continuity and rendered mask growth."""
import argparse
import math
from collections import defaultdict
from PIL import Image
import human_annotation_review as h
import focus_native_body_assembly as a
from focus_appearance_experiment import FIXTURE_KINDS


def sealed(path):
    doc=h.read(h.local(path),limit=a.ASSEMBLY_MAX_BYTES)
    h.require(doc.get('protocolSHA256')==h.digest({k:v for k,v in doc.items() if k!='protocolSHA256'}),
              'changed_audit_protocol')
    return doc


def audit(protocol, context, output):
    doc=sealed(protocol); base=sealed(h.checked(h.ROOT,doc['baseline']))
    manifest=h.read(h.local(context),limit=a.ASSEMBLY_MAX_BYTES)
    h.require(manifest['protocol']==h.ref(h.local(protocol)), 'context_protocol_mismatch')
    old_ids=set(base['fullFit']['weights'])
    train=[r for r in doc['samples'] if r['split']=='train']
    new=[r for r in train if r['id'] not in old_ids]
    result=a.weighting(base,new,a.CONTINUITY_POLICY)
    totals=defaultdict(lambda:defaultdict(float));deltas=[]
    for r in train:
        group=('human' if r['use']=='human-static-auxiliary' else
               'fixture' if r['sourceKind'] in FIXTURE_KINDS else 'os')
        old=base['fullFit']['weights'].get(r['id'],0)
        totals[group]['baseline']+=old
        totals[group]['legacyExpanded']+=doc['fullFit']['weights'][r['id']]
        totals[group]['continuousExpanded']+=result[r['id']]
        if group!='fixture':h.require(result[r['id']]==old,'changed_nonfixture_weight')
        deltas.append(dict(id=r['id'],baseline=old,continuous=result[r['id']],delta=result[r['id']]-old))
    h.require(a.weighting(base,[],a.CONTINUITY_POLICY)==base['fullFit']['weights'],'no_addition_identity')
    index={r['id']:r for r in manifest['members']}; groups=defaultdict(dict)
    for r in train:
        if r['id'] in index and r.get('sourceElementID'):
            groups[(r['sourceID'],r['sourceElementID'])].setdefault(r['label'],r)
    pairs=[]
    for key,states in sorted(groups.items()):
        if set(states)!={0,1}:continue
        f,u=states[1],states[0];fm,um=index[f['id']],index[u['id']]
        ratios=[fm['geometry']['sceneBounds'][i]/um['geometry']['sceneBounds'][i] for i in (2,3)]
        raw=[f['bounds'][i]/u['bounds'][i] for i in (2,3)]
        sizes=[]
        for m in (fm,um):
            with Image.open(h.checked(h.ROOT,m['mask'])) as im:
                b=im.getbbox();h.require(b is not None,'empty_growth_mask');sizes.append([b[2]-b[0],b[3]-b[1]])
        pixel=[sizes[0][i]/sizes[1][i] for i in (0,1)]
        pairs.append(dict(focused=f['id'],unfocused=u['id'],raw=raw,scene=ratios,mask=pixel))
    growing=[p for p in pairs if min(p['raw'])>1.08]
    h.require(all(all(math.isclose(x,y,abs_tol=1e-10) for x,y in zip(p['raw'],p['scene'])) for p in pairs),
              'scene_growth_changed')
    out=h.fresh(output);out.mkdir(parents=True)
    h.write(out/'weights.json',dict(policy=a.CONTINUITY_POLICY,totals=totals,deltas=deltas,weights=result))
    report=dict(version='focus-growth-input-audit-v1',protocol=h.ref(h.local(protocol)),
                context=h.ref(h.local(context)),counts=manifest['counts'],totals=totals,
                pairs=len(pairs),growingPairs=len(growing),
                growingMasksRetainBothAxes=sum(min(p['mask'])>1 for p in growing),
                maxMaskRatioError=max((abs(x-y) for p in pairs for x,y in zip(p['raw'],p['mask'])),default=None),
                comparisons=pairs,modelExecuted=False)
    h.write(out/'audit.json',report)
    print({k:v for k,v in report.items() if k not in ('comparisons','protocol','context')})


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--protocol',required=True);p.add_argument('--context',required=True);p.add_argument('--output',required=True)
    args=p.parse_args();audit(args.protocol,args.context,args.output)
