"""Same-corpus appearance sampling ablation; no model imports during preparation."""
import argparse
from collections import Counter, defaultdict
import json
import math
import re

import focus_representative_experiment as rep
from focus_dataset_contract import ROOT, digest, local

VERSION='focus-sampler-experiment-v1'
INPUT='focus-sampler-input-v1'
POLICY='equal-appearance-label-uniform-example-v1'
require=rep.require


def lane(row, presentation=None, parent=None):
    if presentation=='tabs' or (presentation=='nested_tabs_v1' and parent is None):return 'tabs'
    if presentation=='settings_rows':return 'rows'
    if row['sourceKind']=='tvos_simulator_os':
        require(row['scene'] in ('settings/root','settings/general','settings/apps'),'unknown_native_appearance')
        return 'rows'
    result={'primaryButton':'buttons','secondaryButton':'buttons','cancelAction':'buttons',
            'collectionItem':'artwork','imageView':'artwork','listRow':'rows','toggle':'rows'}.get(row['control'])
    require(result is not None,'unclassified_training_appearance')
    return result


def weights(rows, mapping):
    require(rows and len({r['id'] for r in rows})==len(rows),'invalid_training_membership')
    require(set(mapping)=={r['id'] for r in rows},'changed_mapping_membership')
    counts=Counter();pair_lanes=defaultdict(set)
    for r in rows:
        require(r['split']=='train' and r['use']=='train-candidate','evaluation_in_sampler')
        require(type(r['label']) is int and r['label'] in (0,1),'invalid_label')
        s=mapping[r['id']]['stratum'];require(s in rep.LANES,'unknown_sampling_stratum')
        counts[s,r['label']]+=1;pair_lanes[r['sourceID'],r['pairID']].add(s)
    require(all(len(s)==1 for s in pair_lanes.values()),'pair_stratum_conflict')
    require(set(counts)=={(s,l) for s in rep.LANES for l in (0,1)},'missing_training_bucket')
    result={r['id']:.125/counts[mapping[r['id']]['stratum'],r['label']] for r in rows}
    require(math.isclose(sum(result.values()),1),'invalid_sampling_mass')
    return dict(policy=POLICY,basis='training-only',weights=result,
        stratumMass={s:sum(result[r['id']] for r in rows if mapping[r['id']]['stratum']==s) for s in rep.LANES},
        sourceMass={s:sum(result[r['id']] for r in rows if r['sourceKind']==s) for s in sorted({r['sourceKind'] for r in rows})},
        support={s:{str(l):counts[s,l] for l in (0,1)} for s in rep.LANES})


def appearance_map(base, base_ref):
    prior=rep.a.object_json(rep.a.checked(base['inputs']['base']))
    extension=rep.a.object_json(rep.a.checked(prior['inputs']['extension']))
    sources={s['id']:s['manifest'] for s in extension['inputs']['additions']}
    reviewed=rep.a.object_json(rep.a.checked(base['inputs']['review']))
    for pair in reviewed['pairs']:
        sid=pair['corpusID'];ref=pair['evidence']['manifest']
        require(sid not in sources or sources[sid]==ref,'conflicting_source_manifest')
        sources[sid]=ref
    manifests={sid:rep.a.object_json(rep.a.checked(ref)) for sid,ref in sources.items()}
    result={}
    for r in base['samples']:
        if r['split']!='train':continue
        presentation=parent=None;evidence=base_ref
        if r['sourceID'] in manifests:
            doc=manifests[r['sourceID']];evidence=sources[r['sourceID']]
            pair=next(p for p in doc['pairs'] if p['pair_id']==r['pairID'])
            require(pair['elementID']==r['elementID'],'changed_target_identity')
            scene=pair.get('observationBinding',{}).get('focusedScene',{})
            presentation=scene.get('recipe',{}).get('appearance',{}).get('canvas',{}).get('presentation')
            if presentation is not None:
                require(presentation in ('tabs','nested_tabs_v1','settings_rows','buttons','grid'),'unknown_presentation')
                targets=[e for e in scene['elements'] if e['element_id']==r['elementID']]
                require(len(targets)==1,'missing_native_target')
                parent=targets[0].get('parent_element_id')
        result[r['id']]=dict(stratum=lane(r,presentation,parent),presentation=presentation,parent=parent,evidence=evidence)
    return result


def assemble(spec):
    require(spec['version']==INPUT,'unsupported_sampler_input')
    base=rep.appearance.sealed(spec['base'],rep.VERSION,'protocolSHA256')
    rebuilt=rep.assemble(base['inputs'])
    stable=lambda d:{k:v for k,v in d.items() if k not in ('runtime','protocolSHA256')}
    require(stable(base)==stable(rebuilt),'changed_ablation_baseline')
    mapping=appearance_map(base,spec['base'])
    train=[r for r in base['samples'] if r['split']=='train']
    doc={**rebuilt,'version':VERSION,'inputs':spec,'sampling':weights(train,mapping),
         'trainingAppearance':mapping,'ablation':'training-sampling-only','priorSampling':base['sampling']}
    doc['runtime']['code'] += [rep.a.reference(ROOT/'scripts/focus_sampler_experiment.py')]
    doc.pop('protocolSHA256',None);doc['protocolSHA256']=digest(doc)
    return doc


def load_protocol(path,arm,run_name,approval_path=None):
    path=local(path);doc=rep.appearance.sealed(rep.a.reference(path),VERSION,'protocolSHA256')
    require(doc==assemble(doc['inputs']),'changed_sampler_protocol_or_runtime')
    require(arm=='warm-stretch' and isinstance(run_name,str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',run_name),'invalid_arm_or_run')
    out=ROOT/'NativeUITrainer/focus_ring_runs'/run_name
    require(not out.exists() and not any(p.is_symlink() for p in (out,*out.parents)),'output_collision')
    blockers=[];approval_ref=None
    if approval_path is None:blockers.append('missing_experiment_approval')
    else:
        approval_ref=rep.a.reference(local(approval_path));approval=rep.a.object_json(rep.a.checked(approval_ref))
        require(approval.get('version')=='focus-sampler-approval-v1' and approval.get('approved') is True
            and approval.get('protocolSHA256')==doc['protocolSHA256'] and approval.get('arm')==arm
            and approval.get('runName')==run_name and approval.get('reviewer') and approval.get('reviewReference'),'stale_sampler_approval')
    rows=[{**r,'path':rep.a.checked({k:r['crop'][k] for k in ('path','sha256')}),
           'samplingWeight':doc['sampling']['weights'].get(r['id'],0.)} for r in doc['samples']]
    return dict(formatVersion=rep.FORMAT,protocolVersion=VERSION,configurationValid=True,
        launchEligible=not blockers,executionAuthorized=False,releaseEligible=False,blockers=blockers,
        **{k:doc[k] for k in ('configuration','selection','sampling','counts','warmCheckpoint','runtime','protocolSHA256','unmetQualificationBlockers')},
        protocolFile=rep.a.reference(path),approval=approval_ref,arm=arm,output=str(out.relative_to(ROOT))),rows


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inputs',type=local,required=True);p.add_argument('--output',type=local,required=True)
    args=p.parse_args();require(not args.output.exists(),'output_collision')
    doc=assemble(rep.a.object_json(args.inputs));args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as f:json.dump(doc,f,indent=2,allow_nan=False)
    print(json.dumps(dict(protocolSHA256=doc['protocolSHA256'],sampling={k:v for k,v in doc['sampling'].items() if k!='weights'})))
