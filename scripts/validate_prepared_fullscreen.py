"""Bind the prepared full scenes to retained transfer receipts; emit blocked run draft."""
import argparse
from pathlib import Path

import human_annotation_review as h
import native_focus_spike as n
import train_fullscreen_focus as trainer
from prepare_native_fullscreen import BASE


def validate(directory):
    n.mounted();root=h.local(directory);doc=h.read(root/'draft.json',32*1024*1024)
    h.require(doc['version']=='native-fullscreen-draft-v1' and doc['trainingReady'] is False,'not_preparation_draft')
    protocol=h.read(root/'protocol.json');original={};receipt_refs=[]
    for reference in protocol['accepted']:
        path=h.checked(h.ROOT,reference);accepted=h.read(path)
        for name in accepted.get('receipts',['receipt.json']):
            receipt_path=h.local(path.parent/name);r=h.read(receipt_path)
            h.require(r['verified'] is True,'unverified_transfer_receipt')
            dest=Path(r['destination']);h.require(dest.is_relative_to(n.USB) and dest.resolve()==dest,'unexpected_transfer_root')
            receipt_refs.append(h.ref(receipt_path))
            for member in r['files']:
                rel=Path(member['path']);h.require(not rel.is_absolute() and '..' not in rel.parts,'unsafe_receipt_member')
                p=str(dest/rel);h.require(p not in original or original[p]==member['sha256'],'conflicting_receipt_hash')
                original[p]=member['sha256']
    frames=doc['frames'];h.require(len(frames)==2500 and len({f['id'] for f in frames})==2500,'unexpected_frame_membership')
    run_frames=[];metadata=set();groups={}
    for frame in frames:
        image=frame['image'];h.require(original.get(image['path'])==image['sha256'],'image_not_in_original_receipt')
        ann=h.read(h.checked(h.ROOT,frame['annotation']));source=ann['sourceMetadata']
        h.require(original.get(source['path'])==source['sha256'],'metadata_not_in_original_receipt')
        if source['path'] not in metadata:
            p=Path(source['path']);h.require(p.resolve()==p and n.sha(p)==source['sha256'],'changed_native_metadata');metadata.add(source['path'])
        h.require(ann['image']==image and ann['completeFocus'] is True and ann['profile']=='ordinary','changed_annotation_binding')
        h.require(groups.setdefault(frame['group'],frame['split'])==frame['split'],'cross_split_group')
        controls=ann['controls'];h.require(len(controls)==3 and len({c['id'] for c in controls})==3 and
            sum(c['state']=='focused' for c in controls)==1 and all(c['state'] in ('focused','unfocused') for c in controls),'invalid_focus_membership')
        run_frames.append({k:frame[k] for k in ('id','split','group','image','annotation')})
    admission=dict(version='fullscreen-focus-admission-v1',approved=False,purpose='full-screen-focus-training',
        membershipSHA256=h.digest(run_frames),approvedBy='',sourcePreparation=h.ref(root/'draft.json'),
        note='Prepared from prior experiment evidence; full-screen execution approval remains pending.')
    h.write(root/'admission-draft.json',admission)
    run=dict(version='fullscreen-focus-run-v1',runtime=trainer.runtime_identity(),frames=run_frames,
        checkpoint=h.ref(h.ROOT/'NativeUITrainer/weights/yolo11n.pt'),admission=h.ref(root/'admission-draft.json'),
        seed=42,epochs=1,batch=8,imgsz=640,budget=dict(seconds=300,bytes=2*1024**3))
    h.write(root/'run-draft.json',run)
    try:trainer.validate(root/'run-draft.json')
    except ValueError as e:
        h.require(str(e)=='membership_not_admitted','unexpected_runner_preflight_error');blocked=str(e)
    else:raise ValueError('unapproved_draft_was_accepted')
    result=dict(version='native-fullscreen-preparation-check-v1',preparedDataValid=True,frames=len(frames),
        metadataBoundToOriginalReceipts=len(metadata),receiptInputs=receipt_refs,groups=groups,
        run=h.ref(root/'run-draft.json'),executionReady=False,actualRunnerRejection=blocked,
        remaining=doc['blockers'])
    h.write(root/'readiness.json',result);print({k:v for k,v in result.items() if k not in ('receiptInputs','groups')})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory');a=p.parse_args();validate(a.directory)
