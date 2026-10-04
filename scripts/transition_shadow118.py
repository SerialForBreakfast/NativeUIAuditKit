"""DTM030 intake/parity/package orchestration; conversion stays in the existing exporter."""
import argparse
import copy
import hashlib
from pathlib import Path
import shutil
import numpy as np
import adapt_reflow117 as a
import verify_transition_shadow106 as v
from transition_shadow_export import RESIDUAL_MODEL_ID,RESIDUAL_CHECKPOINT,ENCODING
from diagnose_signal95 import encoded

h=a.h
BASE=h.ROOT/'reports/work/TRANSITION-SHADOW-118/artifacts'


def prepare():
    out=h.fresh(BASE/'parity-inputs')
    compiled=BASE/'bundle/FocusTransitionChange.mlmodelc'
    h.require(compiled.is_dir(),'compiled_model_missing')
    digest,size=v.tree(compiled)
    parent,rows,x,y,endpoints=a.inputs()
    old=h.read(v.BASE/'parity-inputs/reference.json')
    h.require(len(old['examples'])==240 and old['realPairs']==113 and old['identityPairs']==122,'old_reference')
    admitted=h.read(h.checked(h.ROOT,parent['admission']))
    images=admitted['images'];h.require(len(images)==95,'region_membership')
    def frame(ref):
        path=h.checked(h.ROOT,ref)
        h.require(path.is_relative_to(h.ROOT),'parity_frame_boundary')
        return dict(path=str(path),sha256=ref['sha256'])
    def pair(name,before,after):
        return dict(id=name,actionID=name,beforeObservationID=name+'-before',afterObservationID=name+'-after',before=before,after=after)
    examples=copy.deepcopy(old['examples'][:113])
    examples.extend(pair('region-'+str(i),frame(b),frame(c)) for i,(b,c) in enumerate(zip(images,images[1:])))
    examples.extend(copy.deepcopy(old['examples'][113:235]))
    examples.extend(pair('region-identity-'+str(i),frame(ref),frame(ref)) for i,ref in enumerate(images))
    for i,item in enumerate(endpoints):
        ref=examples[item['row']]['before' if item['endpoint']==0 else 'after']
        examples.append(pair('settings-identity-'+str(i),ref,ref))
    h.require(len(examples)==433 and len({v['id'] for v in examples})==433,'parity_membership')
    for row in examples:
        for side in ('before','after'):
            path=Path(row[side]['path']);h.require(path.is_relative_to(h.ROOT) and hashlib.sha256(path.read_bytes()).hexdigest()==row[side]['sha256'],'parity_source')
    out.mkdir(parents=True);tensors=list(x)
    for row in copy.deepcopy(old['examples'][235:]):
        ims=[]
        for side in ('before','after'):
            source=Path(row[side]['path']);h.require(source.name.startswith('synthetic-') and source.parent==v.BASE/'parity-inputs','synthetic_only')
            dest=out/source.name;shutil.copyfile(source,dest);row[side]['path']=str(dest)
            ims.append(a.r.d.pixels(dict(path=str(dest.relative_to(h.ROOT)),sha256=row[side]['sha256'])))
        examples.append(row);tensors.append(encoded(*ims,size=(192,128))[0])
    torch=a.r.d.torch_runtime();torch.set_num_threads(2)
    model=h.ROOT/'NativeUITrainer/focus_ring_runs/reflow117-dtm030/last.pt'
    h.require(h.ref(model)['sha256']==RESIDUAL_CHECKPOINT,'checkpoint')
    state=torch.load(model,map_location='cpu',weights_only=True)
    net=a.r.model(a.r.d.model(a.r.d.PAIRED_TEMPORAL_CONFIG));net.load_state_dict(state['state']);net.eval()
    with torch.no_grad():
        scores=torch.cat([a.score(net,torch.from_numpy(x)),a.r.c.score_change(net,torch.from_numpy(np.stack(tensors[433:])),a.CONFIG)]).tolist()
    expected=h.read(model.parent/'result.json')['after'];h.require(np.allclose(scores[:433],expected,rtol=0,atol=1e-6),'reference_replay')
    reference=[dict(id=row['id'],encodedSHA256=hashlib.sha256(t.tobytes()).hexdigest(),probability=p,decision=v.decision(p)) for row,t,p in zip(examples,tensors,scores)]
    h.write(BASE/'bundle/contract.json',dict(schemaVersion=1,modelID=RESIDUAL_MODEL_ID,checkpointSHA256=RESIDUAL_CHECKPOINT,inputEncoding=ENCODING,compiledTreeSHA256=digest))
    h.write(out/'reference.json',dict(examples=examples,reference=reference,realPairs=207,identityPairs=226,syntheticPairs=5,
        uniqueRealFrames=len({f['sha256'] for row in examples[:433] for f in (row['before'],row['after'])}),compiledTreeSHA256=digest,compiledBytes=size,sourceModel=h.ref(model)))
    print('prepared',len(examples))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','verify','package']);args=p.parse_args()
    if args.mode=='prepare':prepare()
    elif args.mode=='verify':v.verify(h.ROOT/'.build/arm64-apple-macosx/release/TransitionShadowTool',BASE/'parity-final',base=BASE)
    else:
        from package_transition_shadow106 import main
        main(base=BASE,model_id=RESIDUAL_MODEL_ID,expected_pairs=438,archive_name='nuiak-transition-shadow-dtm030-v1.zip')
