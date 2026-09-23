"""Fixed-threshold development comparison; no training or model selection."""
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from focus_dataset_contract import digest, validate_manifest, pixel_digest
from focus_ring_baseline import rows, evaluate, model_contract
from focus_runtime import identity, items_for
from focus_learning_report import infer_bounded
from focus_mixed_assembly import reference, checked
from PIL import Image

started=time.monotonic()
manifest_path=ROOT/'dataset/focus_ring/appearance-a2-pilot-intake2/focus_dataset_manifest.json'
manifest=json.loads(manifest_path.read_text()); validate_manifest(manifest,manifest_path.parent)
samples=rows(manifest)
shipped=ROOT/'NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc'
models={name:reference(ROOT/f'NativeUITrainer/focus_ring_runs/{directory}/weights/best.pt')
        for name,directory in [('fdr007','fdr007-native-incremental'),('fdr008','fdr008-mixed-appearance')]}
training_path=ROOT/'reports/work/FOCUS-DEV-01/dataset/focus_dataset_manifest.json'
training=json.loads(training_path.read_text())
assert training['protocolSHA256']==digest({k:v for k,v in training.items() if k!='protocolSHA256'})
known={s[k]['pixelSHA256'] for s in training['samples'] for k in ('frame','crop')}
protocol={'version':'appearance-development-comparison-v1','manifest':reference(manifest_path),
          'models':models,'shipped':model_contract(shipped),'runtime':identity(),
          'trainingReference':reference(training_path),'threshold':.85,
          'scope':'oracle-box crop classification; not navigation or independent holdout',
          'trainingEligible':False,'modelGatePassed':'not_assessed'}
protocol['protocolSHA256']=digest(protocol)
with (HERE/'protocol.json').open('x') as f: json.dump(protocol,f,indent=2)
items=items_for(manifest); reply=infer_bounded(items,shipped)
scores={r['id']:r['probability'] for r in reply['results']}
results={'shipped':{'backend':'CoreML CPU','evaluation':evaluate(samples,scores,require_hard=False),
                    'scores':scores,'timing':reply['batches']}}
os.environ['TORCH_HOME']=str(ROOT/'NativeUITrainer/.torch')
import numpy as np
import torch
from focus_ring_backbone import mobilenetv4_conv_small
tensors=[]; pixel_groups=defaultdict(list); pair_groups=defaultdict(list); overlaps=[]
for pair in manifest['pairs']:
    pixels=[]
    for role,label in [('focused',1),('unfocused',0)]:
        path=manifest_path.parent/pair[role+'_crop']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==pair[role+'_crop_sha256']
        sha=pixel_digest(manifest_path.parent,{'path':pair[role+'_crop'],'sha256':pair[role+'_crop_sha256']})
        sid=pair['pair_id']+':'+str(label); pixels.append(sha); pixel_groups[sha].append(sid)
        if sha in known: overlaps.append(sid)
        with Image.open(path) as im:
            assert im.size==(256,256)
            tensors.append(torch.from_numpy(np.array(im.convert('RGB'),copy=True)).permute(2,0,1).float().div(255))
    pair_groups[tuple(pixels)].append(pair['pair_id'])
for name,ref in models.items():
    model=mobilenetv4_conv_small(pretrained=False,num_classes=1)
    model.load_state_dict(torch.load(checked(ref),map_location='cpu',weights_only=True)['state_dict'],strict=True)
    model.eval(); values=[]; timings=[]
    with torch.inference_mode():
        for offset in range(0,len(samples),32):
            batch=torch.stack(tensors[offset:offset+32]); tick=time.monotonic()
            values.extend(torch.sigmoid(model(batch)).view(-1).tolist())
            timings.append({'samples':len(batch),'milliseconds':1000*(time.monotonic()-tick)})
    scores={s['id']:v for s,v in zip(samples,values,strict=True)}
    results[name]={'backend':'Torch CPU','evaluation':evaluate(samples,scores,require_hard=False),
                   'scores':scores,'batchTimings':timings}
for ref in models.values(): checked(ref)
checked(protocol['manifest']); checked(protocol['trainingReference'])
assert identity()==protocol['runtime'] and model_contract(shipped)==protocol['shipped']
report={'protocolSHA256':protocol['protocolSHA256'],'results':results,'seconds':time.monotonic()-started,
        'accounting':{'recipes':24,'pairs':len(manifest['pairs']),'samples':len(samples),
                      'uniqueCropPairs':len(pair_groups),'uniqueCrops':len(pixel_groups)},
        'duplicatePairGroups':[v for v in pair_groups.values() if len(v)>1],
        'contradictoryCropGroups':[v for v in pixel_groups.values() if len({s.rsplit(':',1)[1] for s in v})>1],
        'exactTrainingCropOverlaps':overlaps,'trainingEligible':False,'modelGatePassed':'not_assessed',
        'limitations':['Development source-related data, not independent evaluation',
                       'Repeated pixels do not add independent sample support',
                       'Ground-truth boxes supplied; detector proposals and navigation untested',
                       'CoreML versus Torch is not export parity or device latency qualification']}
with (HERE/'comparison.json').open('x') as f: json.dump(report,f,indent=2,allow_nan=False)
print(json.dumps({'accounting':report['accounting'],'duplicateGroups':len(report['duplicatePairGroups']),
                  'contradictions':len(report['contradictoryCropGroups']), 'trainingCropOverlaps':len(overlaps),
                  'overall':{k:v['evaluation']['groups']['overall'] for k,v in results.items()},'seconds':report['seconds']}))
