"""Offline appearance lineage and sampling proposal; never a training protocol."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import time

from focus_dataset_contract import ROOT, FocusDataError, digest, image, pixel_digest, local
from focus_mixed_assembly import checked, reference, stratum
from focus_runtime import identity
from direct_tvos_capture import validate_capture, new_output
from direct_focus_manifest import validate_direct_manifest


def require(ok, reason):
    if not ok: raise FocusDataError(reason)


def components(rows):
    """Join exact pixels and explicit lineage without assigning new split roles."""
    require(len({r['id'] for r in rows})==len(rows),'duplicate_sample')
    parents={r['id']:r['id'] for r in rows}; owners={}; labels={}; edges=[]
    def find(x):
        while parents[x]!=x:
            parents[x]=parents[parents[x]]; x=parents[x]
        return x
    def join(a,b):
        a,b=find(a),find(b)
        if a!=b: parents[max(a,b)]=min(a,b)
    for r in sorted(rows,key=lambda r:r['id']):
        crop=r['crop']['pixelSHA256']
        require(crop not in labels or labels[crop]==r['label'],'contradictory_crop_labels')
        labels[crop]=r['label']
        keys=[('pair',r['sourceID'],r['pairID']),('related',r['relatedGroup']),
              ('intrinsic',r['sourceKind'],r['intrinsicGroup']),('pixels',crop),
              ('pixels',r['frame']['pixelSHA256'])]
        if r.get('recipeSeed') is not None: keys.append(('seed',r['sourceKind'],r['recipeSeed']))
        for key in keys:
            if key in owners:
                join(r['id'],owners[key]); edges.append({'a':owners[key],'b':r['id'],'reason':list(key)})
            else: owners[key]=r['id']
    groups=defaultdict(list)
    for r in rows: groups[find(r['id'])].append(r)
    result=[]
    for key,members in sorted(groups.items()):
        roles=sorted({r['split'] for r in members})
        # A development proposal can join training lineage, but never validation/test.
        protected=set(roles)&{'validation','test','challenge'}
        result.append({'id':key,'samples':sorted(r['id'] for r in members),'roles':roles,
                       'sourceIDs':sorted({r['sourceID'] for r in members}),
                       'seeds':sorted({r['recipeSeed'] for r in members if r.get('recipeSeed') is not None}),
                       'crossPartitionConflict':bool(protected and len(roles)>1)})
    return {'components':result,'edges':edges}


def balanced_weights(rows):
    train=sorted((r for r in rows if r['proposedRole']=='train-candidate'),key=lambda r:r['id'])
    require(bool(train),'empty_training_proposal')
    sources=sorted({r['sourceKind'] for r in train})
    counts=Counter((stratum(r),r['label']) for r in train)
    strata={s:{stratum(r) for r in train if r['sourceKind']==s} for s in sources}
    require(all(counts[k,0] and counts[k,1] for group in strata.values() for k in group),'missing_label_support')
    probabilities={r['id']:1/len(sources)/len(strata[r['sourceKind']])/2/counts[stratum(r),r['label']] for r in train}
    mass={s:sum(probabilities[r['id']] for r in train if r['sourceKind']==s) for s in sources}
    require(abs(sum(probabilities.values())-1)<1e-9,'invalid_probability_mass')
    return {'policy':'proposal-equal-source-then-stratum-then-label-v1','basis':'proposed-training-only',
            'probabilities':probabilities,'sourceMass':mass,
            'effectiveSampleSize':1/sum(p*p for p in probabilities.values()),
            'scope':'hypothesis, not proven optimal; no trainer integration or launch approval'}


def audit(previous, appearance, protocol_path, output):
    output=new_output(output); start=time.monotonic(); refs={}
    previous,appearance,protocol_path=map(local,(previous,appearance,protocol_path))
    def load(path):
        ref=reference(path); refs[ref['path']]=ref
        return json.loads(checked(ref).read_text())
    old=load(previous); new=load(appearance); protocol=load(protocol_path)
    require(old['protocolSHA256']==digest({k:v for k,v in old.items() if k!='protocolSHA256'}),'changed_previous_protocol')
    require(protocol['protocolSHA256']==digest({k:v for k,v in protocol.items() if k!='protocolSHA256'}),'changed_comparison_protocol')
    require(reference(previous)==protocol['trainingReference'] and reference(appearance)==protocol['manifest'],'changed_input_references')
    require(new['runtimeCrop']==old['samples'][0]['runtime']==identity(),'changed_crop_runtime')
    for ref in protocol['models'].values(): checked(ref); refs[ref['path']]=ref
    root=ROOT/new['sourceRoot']; capture=load(root/'direct-capture.json')
    validate_capture(capture,root); validate_direct_manifest(new,root)
    cached={}
    def record(ref):
        key=(ref['path'],ref['sha256'])
        if key not in cached:
            checked({'path':ref['path'],'sha256':ref['sha256']}); image(ROOT,ref)
            pixels=pixel_digest(ROOT,ref)
            require(ref.get('pixelSHA256',pixels)==pixels,'changed_decoded_pixels')
            cached[key]={**ref,'pixelSHA256':pixels}
        return cached[key]
    rows=[]
    for saved in old['samples']:
        r=dict(saved); r['frame']=record(saved['frame']); r['crop']=record(saved['crop'])
        r['proposedRole']='train-candidate' if r['split']=='train' else 'retention-validation'
        rows.append(r)
    for pair in new['pairs']:
        for role,label in [('focused',1),('unfocused',0)]:
            raw=pair['frames'][role]
            rows.append({'id':digest(['appearance-a2',pair['pair_id'],role]),'sourceID':'appearance-a2',
                'pairID':pair['pair_id'],'label':label,'split':'development','proposedRole':'train-candidate',
                'sourceKind':new['sourceKind'],'relatedGroup':'appearance-a2-development',
                'intrinsicGroup':pair['recipe_group'],'recipeSeed':pair['recipe_seed'],
                'scene':pair['fixture_scene'],'style':pair['theme'],'control':pair['element_type'],
                'recipe':pair['recipe'],'labelSource':pair['labelSource'],
                'frame':record({'path':str((root/raw['path']).relative_to(ROOT)),'sha256':raw['sha256']}),
                'crop':record({'path':str((appearance.parent/pair[role+'_crop']).relative_to(ROOT)),
                               'sha256':pair[role+'_crop_sha256']})})
    lineage=components(rows)
    bypair=defaultdict(list)
    for r in rows: bypair[(r['sourceID'],r['pairID'])].append(r)
    pairpixels=defaultdict(list)
    for key,members in sorted(bypair.items()):
        require(sorted(r['label'] for r in members)==[0,1],'incomplete_pair')
        pairpixels[tuple(r['crop']['pixelSHA256'] for r in sorted(members,key=lambda r:r['label']))].append(list(key))
    weights=balanced_weights(rows)
    oldmass=defaultdict(float)
    total=sum(old['sampling']['weights'].values())
    for r in old['samples']:
        if r['split']=='train': oldmass[r['sourceKind']]+=old['sampling']['weights'][r['id']]/total
    oldpixels={r['crop']['pixelSHA256'] for r in old['samples']}
    overlap=[r['id'] for r in rows if r['sourceID']=='appearance-a2' and r['crop']['pixelSHA256'] in oldpixels]
    coverage=Counter((r['proposedRole'],r['sourceKind'],r['scene'],r['style'],r['label']) for r in rows)
    blockers=['independent_appearance_validation_absent','untouched_appearance_challenge_absent',
              'proposal_not_supported_by_trainer','explicit_training_authorization_absent']
    if any(g['crossPartitionConflict'] for g in lineage['components']): blockers.append('cross_partition_lineage_conflict')
    duplicates=[v for v in pairpixels.values() if len(v)>1]
    if duplicates: blockers.append('duplicate_pair_disposition_required')
    doc={'version':'focus-appearance-proposal-v1','launchEligible':False,'trainingEligible':False,
         'inputs':list(refs.values()),'samples':rows,'lineage':lineage,'sampling':weights,
         'previousSourceMass':dict(oldmass),'newCropOverlapSampleIDs':overlap,'duplicatePairGroups':duplicates,
         'counts':dict(Counter(r['proposedRole'] for r in rows)),
         'coverage':[{'key':list(k),'samples':v} for k,v in sorted(coverage.items())],
         'blockers':blockers,'configurationProposal':old['configuration'],
         'initializationProposal':old['warmCheckpoint'],
         'selectionChangeRequired':'appearance validation plus fixed native retention; not native-only selection',
         'independentAppearanceValidation':[],'finalAppearanceChallenge':[],
         'modelGatePassed':'not_assessed','seconds':time.monotonic()-start}
    for ref in refs.values(): checked(ref)
    doc['proposalSHA256']=digest(doc)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as f: json.dump(doc,f,indent=2,allow_nan=False)
    print(json.dumps({'counts':doc['counts'],'components':len(lineage['components']),
                      'overlappingCrops':len(overlap),'duplicatePairGroups':len(duplicates),
                      'sourceMass':weights['sourceMass'],'blockers':blockers,'seconds':doc['seconds']}))
    return doc


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('previous','appearance','comparison-protocol','output'): p.add_argument('--'+name,required=True,type=Path)
    a=p.parse_args()
    try: audit(a.previous,a.appearance,a.comparison_protocol,a.output)
    except (OSError,ValueError,KeyError,TypeError) as e: p.exit(2,str(e)+'\n')

if __name__=='__main__': main()
