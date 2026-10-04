"""Retained data and synthetic parity for the isolated transition consumer; no training."""
import argparse
import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path
import numpy as np
from PIL import Image
import focus_direct_transition as d
import focus_change_adaptation as change
import focus_candidate_ranker as rank
from diagnose_signal95 import encoded
from prepare_collection103 import original_negatives
from transition_shadow_export import MODEL_ID,ENCODING,CHECKPOINT

h=d.h
BASE=h.ROOT/'reports/work/TRANSITION-SHADOW-106/artifacts'


def tree(root):
    digest=hashlib.sha256();total=0
    for p in sorted(root.rglob('*')):
        if p.is_symlink():raise ValueError('model_symlink')
        if p.is_file():
            raw=p.read_bytes();total+=len(raw)
            digest.update(p.relative_to(root).as_posix().encode()+b'\0'+raw)
    return digest.hexdigest(),total


def decision(p):return 'changed' if p>=.85 else 'unchanged' if p<=.15 else 'uncertain'


def prepare():
    out=h.fresh(BASE/'parity-inputs');out.mkdir(parents=True)
    model=BASE/'bundle/FocusTransitionChange.mlmodelc'
    digest,size=tree(model)
    h.write(BASE/'bundle/contract.json',dict(schemaVersion=1,modelID=MODEL_ID,checkpointSHA256=CHECKPOINT,
        inputEncoding=ENCODING,compiledTreeSHA256=digest))
    result=rank.sealed(h.ROOT/'NativeUITrainer/focus_ring_runs/collection104-dtm025/result.json',change.VERSION)
    protocol=h.read(h.checked(h.ROOT,result['protocol']))
    h.require(result['model']['sha256']==CHECKPOINT,'wrong_checkpoint')
    corpus=h.read(h.checked(h.ROOT,protocol['corpus']))
    rows=d.admitted(corpus,h.read(h.checked(h.ROOT,protocol['admission'])))
    x=np.load(h.checked(h.ROOT,protocol['x'],64*1024**2),allow_pickle=False)
    examples=[];tensors=[];copied={}
    def frame(ref):
        path=h.checked(h.ROOT,ref)
        if not path.is_relative_to(h.ROOT):
            target=out/(ref['sha256']+'.png')
            if ref['sha256'] not in copied:
                shutil.copyfile(path,target);copied[ref['sha256']]=True
                h.require(hashlib.sha256(target.read_bytes()).hexdigest()==ref['sha256'],'copy_hash')
            path=target
        return dict(path=str(path),sha256=ref['sha256'])
    for i,row in enumerate(rows):
        examples.append(dict(id=row['id'],actionID='retained-'+str(i),beforeObservationID='before-'+str(i),
            afterObservationID='after-'+str(i),before=frame(row['images'][0]),after=frame(row['images'][1])))
        tensors.append(x[i])
    for i,entry in enumerate(original_negatives(protocol,rows,x)):
        origin=entry['origins'][0];ri,j=origin['rowIndex'],origin['endpoint'];pixels=x[ri,3*j:3*j+3]
        ref=frame(rows[ri]['images'][j]); ident='identity-'+str(i)
        examples.append(dict(id=ident,actionID=ident,beforeObservationID=ident+'-before',afterObservationID=ident+'-after',before=ref,after=ref))
        tensors.append(np.concatenate((pixels,pixels)))
    for i,(width,height) in enumerate([(17,9),(637,359),(113,257),(192,128),(384,216)]):
        yy,xx=np.indices((height,width));a=np.stack(((xx*13+yy*3)%256,(xx*7)%256,(yy*11)%256),axis=2).astype('uint8')
        images=[];refs=[]
        for j,array in enumerate((a,np.roll(a,1,axis=1))):
            image=Image.fromarray(array);path=out/f'synthetic-{i}-{j}.png';image.save(path)
            images.append(image);refs.append(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        ident='synthetic-'+str(i)
        examples.append(dict(id=ident,actionID=ident,beforeObservationID=ident+'-before',afterObservationID=ident+'-after',before=refs[0],after=refs[1]))
        tensors.append(encoded(*images,size=(192,128))[0])
    torch=d.torch_runtime();torch.set_num_threads(2)
    state=torch.load(h.checked(h.ROOT,result['model']),map_location='cpu',weights_only=True)
    net=d.model(state['configuration']);net.load_state_dict(state['state'],strict=True);net.eval()
    with torch.inference_mode():scores=change.score_change(net,torch.from_numpy(np.stack(tensors)),change.COLLECTION_CONFIG).tolist()
    h.require(all(abs(p-r['after'])<=1e-6 for p,r in zip(scores[:113],result['results'])),'torch_environment_parity')
    reference=[dict(id=row['id'],encodedSHA256=hashlib.sha256(x.tobytes()).hexdigest(),probability=p,decision=decision(p))
        for row,x,p in zip(examples,tensors,scores)]
    h.write(out/'reference.json',dict(examples=examples,reference=reference,realPairs=113,identityPairs=122,
        syntheticPairs=5,uniqueRealFrames=len({im['sha256'] for r in rows for im in r['images']}),
        compiledTreeSHA256=digest,compiledBytes=size,sourceModel=result['model']))
    h.write(out/'smoke.json',dict(schemaVersion=1,mode='score',root=str(h.ROOT),pairs=examples[:1]))
    print('prepared',len(reference),'pairs',digest,size)


def verify(tool,output,base=BASE):
    out=h.fresh(output);out.mkdir(parents=True);source=base/'parity-inputs'
    ref=h.read(source/'reference.json');contract=base/'bundle/contract.json';contract_hash=hashlib.sha256(contract.read_bytes()).hexdigest()
    results=[];batches=[];start=time.monotonic()
    for i in range(0,len(ref['examples']),32):
        request=out/f'request-{i}.json';reply=out/f'reply-{i}.json'
        h.write(request,dict(schemaVersion=1,mode='score',root=str(h.ROOT),pairs=ref['examples'][i:i+32]))
        command=[str(h.local(tool)),'--bundle',str(base/'bundle'),'--manifest-sha256',contract_hash,
            '--request',str(request),'--output',str(reply)]
        t=time.monotonic();run=subprocess.run(command,capture_output=True,text=True,timeout=300)
        h.write(out/f'execution-{i}.json',dict(command=command,exitCode=run.returncode,stderr=run.stderr,seconds=time.monotonic()-t))
        h.require(run.returncode==0,'swift_parity_execution_failed_'+str(i))
        response=h.read(reply)
        h.require(response['modelID']==h.read(contract)['modelID'],'loaded_model_identity')
        results.extend(response['results']);batches.append(response['loadSeconds'])
        print('batch',i,'completed',flush=True)
    h.require([v['id'] for v in results]==[v['id'] for v in ref['reference']],'parity_membership')
    differences=[dict(id=a['id'],encodingExact=a['encodedSHA256']==b['encodedSHA256'],
        probabilityError=abs(a['probability']-b['probability']),decisionEqual=a['decision']==b['decision']) for a,b in zip(ref['reference'],results)]
    passed=all(v['encodingExact'] and v['probabilityError']<=1e-4 and v['decisionEqual'] for v in differences)
    h.write(out/'parity.json',dict(version='transition-shadow-parity-v1',passed=passed,counts={k:ref[k] for k in ('realPairs','identityPairs','syntheticPairs','uniqueRealFrames')},
        exactEncodings=sum(v['encodingExact'] for v in differences),decisionsEqual=sum(v['decisionEqual'] for v in differences),
        maxProbabilityError=max(v['probabilityError'] for v in differences),differences=differences,
        modelTreeSHA256=ref['compiledTreeSHA256'],contractSHA256=contract_hash,tool=h.ref(h.local(tool)),
        loadSeconds=batches,inferenceMedianSeconds=float(np.median([v['inferenceSeconds'] for v in results])),
        inferenceP95Seconds=float(np.percentile([v['inferenceSeconds'] for v in results],95)),
        preprocessingMedianSeconds=float(np.median([v['preprocessingSeconds'] for v in results])),
        elapsedSeconds=time.monotonic()-start,releaseEligible=False),sealed=True)
    print('parity passed',passed,'max',max(v['probabilityError'] for v in differences))
    h.require(passed,'parity_gate_failed')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--tool');p.add_argument('--output');a=p.parse_args()
    if a.prepare:prepare()
    else:verify(a.tool,a.output)
