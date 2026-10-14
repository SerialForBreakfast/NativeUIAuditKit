"""Inventory resident delivery candidates without export or publication."""
import hashlib
import json
from pathlib import Path
import argparse

ROOT=Path(__file__).resolve().parents[1]
MODELS=ROOT/'NativeUIAuditKitModels/Sources/NativeUIAuditKitModels'


def inventory(path):
    if not path.exists():return dict(path=str(path.relative_to(ROOT)),available=False)
    files=[]
    for file in sorted(path.rglob('*')):
        if file.is_symlink():raise ValueError('Model contains a link')
        if file.is_file():
            data=file.read_bytes()
            files.append(dict(path=file.relative_to(path).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    if not files:raise ValueError('Empty model')
    encoded=json.dumps(files,sort_keys=True,separators=(',',':')).encode()
    return dict(path=str(path.relative_to(ROOT)),available=True,bytes=sum(r['bytes'] for r in files),
                inventorySHA256=hashlib.sha256(encoded).hexdigest(),files=files)


def run(output):
    if output.exists():raise ValueError('Output exists')
    entries=[]
    candidates=[('nativeui-ios-v2.0','NativeUIDetector_v2','element_detection','model_manifest_ios_v2.json',[]),
        ('nativeui-tvos-v3.0','NativeUIModel_tvOS','element_detection','model_manifest_tvos_v1.json',[
            MODELS/'NativeUIModel_tvOS.mlpackage',ROOT/'NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.mlpackage']),
        ('focus-ring-detector-v1.0','FocusRingDetector','single_frame_focus',None,[
            ROOT/'NativeUITrainer/focus_ring_runs/fdr001/export/FocusRingDetector.mlpackage'])]
    for model_id,name,task,manifest,sources in candidates:
        compiled=inventory(MODELS/f'Resources/{name}.mlmodelc')
        metadata=json.loads((MODELS/f'Resources/{name}.mlmodelc/metadata.json').read_text())
        entries.append(dict(modelID=model_id,task=task,compiled=compiled,sourceCandidates=[inventory(p) for p in sources],
            tensorContract=None if manifest is None else json.loads((MODELS/'Resources'/manifest).read_text()),
            compiledMetadata=metadata,testingRole='Existing bundled baseline; shadow only, no navigation authority',
            publicReleaseApproved=False,sourceToBundledParityVerified=False,
            licenseReview='Check embedded terms and provenance; MIT code does not clear weight distribution',
            minimumHostVerified=False))
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as file:json.dump(dict(version='model-distribution-inventory-v1',models=entries,
        archivePublished=False,catalogReady=False,canonicalInventory='Sorted paths; compact sorted-key JSON of path, bytes, sha256',
        packageGraph='NativeUIAuditKit still depends on NativeUIAuditKitModels',
        proposedLimits=dict(archiveBytes=32*1024**2,expandedBytes=64*1024**2,files=256,pathBytes=512,
                            compilationSeconds=120,requestSeconds=300),
        limitsStatus='Preparation limits for current small models; measure compilation before claiming supported timeout'),file,indent=2)
    print([(r['modelID'],r['compiled']['bytes']) for r in entries])


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();run(args.output)
