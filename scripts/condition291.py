"""Run a matched comparison using approved same-recipe focus states."""
import argparse
from collections import defaultdict
from pathlib import Path
import time
import numpy as np
from PIL import Image
import layout290
import matched_states290
from diagnose_signal95 import encoded

model=layout290.model
base=model.base
torch=base.torch
OUT=base.ROOT/'reports/work/TRANSITION-291'


def select_controls(membership, added):
    pools=defaultdict(list)
    start=len(membership['replayLabels'])
    for position,index in enumerate(membership['selected']):
        row=membership['rows'][index]
        base.require(row['role']=='train','control_role')
        pools[(row['group'],row['changed'])].append((row['id'],start+position))
    pools={key:sorted(values) for key,values in pools.items()}
    used=defaultdict(int);indices=[]
    for row in added:
        base.require(row['role']=='train','added_role')
        key=(row['group'],row['changed']);n=used[key]
        base.require(n<len(pools.get(key,[])),'control_support')
        indices.append(pools[key][n][1]);used[key]+=1
    return np.asarray(indices,dtype=np.int64)


def balanced_weights(weights, labels, membership, added, controls):
    start=len(membership['replayLabels']);count=len(membership['selected'])
    base.require(len(weights)==len(labels)==start+2*count,'base_shape')
    base.require(np.isfinite(weights).all() and (weights>0).all(),'base_weights')
    forward=[membership['rows'][index]['group'] for index in membership['selected']]
    groups=[None]*start+forward+forward
    add_groups=[r['group'] for r in added]
    out_groups=groups+add_groups+add_groups
    extra_labels=np.asarray([r['changed'] for r in added],dtype=labels.dtype)
    base.require(np.array_equal(labels[controls],extra_labels),'control_labels')
    out_labels=np.concatenate((labels,extra_labels,extra_labels))
    result=np.concatenate((weights,weights[controls],weights[controls])).copy()
    summaries=[]
    for group,label in sorted({(r['group'],r['changed']) for r in added}):
        old=np.array([g==group for g in groups]) & (labels==label)
        new=np.array([g==group for g in out_groups]) & (out_labels==label)
        total=float(weights[old].astype(np.float64).sum())
        base.require(total>0,'group_support')
        result[new]*=total/float(result[new].astype(np.float64).sum())
        actual=float(result[new].astype(np.float64).sum())
        base.require(np.isclose(actual,total,rtol=1e-6,atol=1e-6),'group_weight_total')
        summaries.append(dict(group=group,label=int(label),before=total,after=actual,
                              oldRows=int(old.sum()),newRows=int(new.sum())))
    base.require(np.array_equal(result[:start],weights[:start]),'replay_weights')
    return out_labels,result,summaries


def verify_state(state, doc):
    base.require(state['role']=='train' and state['settled'] is True,'state_role')
    scenes=[doc[key] for prefix,key in [('unfocused','baseline_scene'),('focused','focused_scene')]
            if doc[prefix+'_sha256']==state['image']['sha256']]
    base.require(bool(scenes),'state_image_binding')
    for scene in scenes:
        base.require(scene['is_settled'] and scene['focused_element_id']==state['focusID']
            and scene['fixture_run_id']==state['runID']
            and scene['recipe']['recipe_hash']==state['recipeHash']==doc['recipe']['recipe_hash'],
            'state_observation')
    base.require(bool(state['focusID']),'unknown_focus')


def prepare():
    manifest,_,replacement,rx,_,_,_,initializer,pins=base.prepare()
    membership=base.read(base.PACKAGE/'membership.json')
    original=np.load(base.PACKAGE/'training.npy',allow_pickle=False)
    labels=np.load(base.PACKAGE/'labels.npy',allow_pickle=False)
    full=layout290.replace_rows(original,labels,replacement,rx,len(membership['selected']))
    del original,rx
    control_reg=base.read(base.ROOT/'reports/work/TRANSITION-287/DTM081/registration.json')
    reg=base.read(base.ROOT/'reports/work/TRANSITION-266/DTM074/registration.json')
    weights=np.load(base.checked(reg['weights']),allow_pickle=False)
    for name,value in [('training',full),('labels',labels),('weights',weights)]:
        base.require(base.sha(value.tobytes())==control_reg[name+'SHA256'],name+'_identity')
    base.require(base.ref(initializer)==control_reg['initializer'],'initializer_identity')
    path=base.ROOT/'reports/work/TRANSITION-290/matched-states.json'
    matched=base.read(path)
    base.require(matched['version']=='matched-states290-v1' and matched['role']=='development-training-derived'
                 and not matched['independentEvaluation'],'matched_contract')
    base.checked(matched['runner'])
    parent=base.read(base.checked(pins['prior']))
    base.require(matched['parentReplacements']==parent['replacements']
                 and matched['parentAdmission']==parent['admission'],'replacement_parent')
    base.checked(matched['parentReplacements'])
    admission=base.read(base.checked(matched['parentAdmission']))
    base.require(admission['approved'] and admission['role']=='development-training'
                 and admission['protectedEndpointOverlap'] is False,'parent_admission')
    allowed={(image['sha256'],row['group']) for row in replacement['rows'] for image in row['images']}
    protected=[r for r in membership['rows'] if r['role']!='train']
    protected_raw={v for row in protected for v in row['pixelHashes']}
    protected_files={r['sha256'] for row in protected for r in row['images']}
    native=np.load(base.PACKAGE/'native.npy',mmap_mode='r',allow_pickle=False)
    protected_encoded={base.sha(value.tobytes()) for i,row in enumerate(membership['rows']) if row['role']!='train'
                       for value in (native[i,:3],native[i,3:])}
    images={};raw_hashes={}
    for state in matched['states']:
        base.require((state['image']['sha256'],state['group']) in allowed,'unapproved_state')
        verify_state(state,base.read(base.checked(state['metadata'])))
        image_hash=state['image']['sha256']
        with Image.open(base.checked(state['image'])) as image:rgb=image.convert('RGB')
        raw_hash=base.sha(str(rgb.size).encode()+rgb.tobytes())
        value,_=encoded(rgb,rgb,(192,128))
        base.require(image_hash not in protected_files and raw_hash not in protected_raw
                     and base.sha(value[:3].tobytes()) not in protected_encoded,'protected_overlap')
        images[image_hash]=rgb;raw_hashes[image_hash]=raw_hash
    added=matched_states290.make_pairs(matched['states'])
    base.require(added==matched['rows'] and len(added)==80 and sum(r['changed'] for r in added)==48,'added_membership')
    controls=select_controls(membership,added)
    extra=np.stack([encoded(*(images[r['sha256']] for r in row['images']),(192,128))[0] for row in added])
    out_labels,out_weights,totals=balanced_weights(weights,labels,membership,added,controls)
    base.require(len(out_labels)==1820 and np.array_equal(labels[controls],out_labels[1660:1740]),'schedule_accounting')
    return manifest,membership,full,out_labels,out_weights,extra,controls,initializer,dict(
        pins=pins,matchedManifest=base.ref(path),configuration=control_reg['configuration'],
        representation=model.REPRESENTATION,initializer=base.ref(initializer),
        parentTrainingSHA256=control_reg['trainingSHA256'],labelsSHA256=base.sha(out_labels.tobytes()),
        weightsSHA256=base.sha(out_weights.tobytes()),candidateExtraSHA256=base.sha(extra.tobytes()),
        controlExtraSHA256=base.sha(full[controls].tobytes()),controlIndices=controls.tolist(),
        addedRows=added,decodedHashes=raw_hashes,weightTotals=totals,protectedOverlap=False,
        runner=base.ref(Path(__file__)),trainer=base.ref(Path(base.trainer.__file__)),
        encoder=base.ref(base.ROOT/'scripts/diagnose_signal95.py'),rows=1820,updates=13680,
        thresholds=[.15,.85],outputCapBytes=256*1024**2,wallTimeLimit=None,
        roles='Existing development-training ancestry; no new final evaluation.',
        hypothesis='Same-content focus comparisons improve focus recognition outside the original left-side layouts.',
        acceptance='No individual regression against DTM067, DTM078, DTM081, or the matched control.',
        productionEligible=False)


def train_one(name, full, added, labels, weights, initializer, registration, references, manifest, diagnostic):
    out=OUT/name;out.mkdir()
    values=np.concatenate((full,added,base.reporting.reverse(added)))
    base.require(len(values)==1820 and labels.shape==weights.shape==(1820,),'training_shape')
    base.write(out/'registration.json',dict(parent=base.ref(OUT/'registration.json'),
        trainingSHA256=base.sha(values.tobytes()),name=name))
    started=time.monotonic()
    def progress(row):
        base.write(out/f"epoch-{row['epoch']:04d}.json",row);print(name,row,flush=True)
    net=model.extend(base.load_model(initializer))
    net,history=base.trainer.fit(net,torch.from_numpy(values),torch.from_numpy(labels),
        registration['configuration'],progress,torch.from_numpy(weights))
    torch.save(dict(state=net.state_dict(),representation=model.REPRESENTATION,
        registration=base.ref(out/'registration.json')),out/'last.pt')
    restored=model.load_candidate(out/'last.pt')
    fit=base.metrics(restored,values,labels)
    base.require(fit==base.metrics(net,values,labels),'checkpoint_parity')
    base.write(out/'result.json',dict(fit=fit,history=history,model=base.ref(out/'last.pt'),
        addedFit=base.metrics(restored,diagnostic,np.array([r['changed'] for r in registration['addedRows']],np.float32)),
        seconds=time.monotonic()-started,checkpointParity=True,productionEligible=False))
    del values
    evaluation=base.evaluate_full(restored,references,manifest)
    base.write(out/'evaluation.json',evaluation)
    base.write(out/'completion.json',dict(seconds=time.monotonic()-started,
        regressionPassed=evaluation['regressionPassed'],productionEligible=False))
    return restored


def run():
    base.require(not OUT.exists(),'output_collision')
    torch.set_num_threads(2)
    manifest,_,full,labels,weights,extra,controls,initializer,registration=prepare()
    OUT.mkdir()
    base.write(OUT/'registration.json',registration)
    print('Registered 2 serial runs: 1820 rows and 13680 updates each.',flush=True)
    references={'DTM067':base.load_model(initializer)}
    for name,folder in [('DTM078','CONFLICT-281'),('DTM081','TRANSITION-287')]:
        checkpoint=base.checked(base.read(base.ROOT/f'reports/work/{folder}/{name}/result.json')['model'])
        references[name]=base.load_model(checkpoint) if name=='DTM078' else model.load_candidate(checkpoint)
    control=train_one('DTM083',full,full[controls],labels,weights,initializer,registration,references,manifest,extra)
    references['DTM083']=control
    train_one('DTM084',full,extra,labels,weights,initializer,registration,references,manifest,extra)
    size=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    base.require(size<256*1024**2,'output_budget')
    base.write(OUT/'completion.json',dict(outputBytes=size,control='DTM083',candidate='DTM084',
        regressionPassed=base.read(OUT/'DTM084/evaluation.json')['regressionPassed'],productionEligible=False))
    print('Both runs complete.',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true',required=True)
    parser.parse_args();run()
