"""Replay the Q2 and Q3 Fixture images with independent SDK reference boxes."""
import hashlib
from pathlib import Path
import json
import coremltools as ct
import tvbench as t
from comparative_focus604 import predict_comparative_on_detections
from roles559 import ROLES

base = Path('reports/work/PAR613')
records = json.loads(Path('reports/work/IOS608/ttr/readback.json').read_text())
cases, refs, seen = [], {}, {}
for name, record in records.items():
    if not name.startswith(('q2-', 'q3-')):
        continue
    source = Path(record['sidecar'])
    image = source.with_name('frame.png')
    sha = hashlib.sha256(image.read_bytes()).hexdigest()
    assert record['eligible'] and sha == record['image_sha256']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == record['sidecar_sha256']
    if sha in seen:
        assert record['focus'] == refs[seen[sha]]['focus']
        continue
    seen[sha] = name
    refs[name] = record
    cases.append(dict(id=name,image=dict(path=str(image),sha256=sha),width=3840,height=2160))

def classify(prediction, reference):
    if reference is None: return 'unverified'
    if prediction is None: return 'abstain'
    return 'correct' if t.r543._iou(prediction,reference)>=.5 else 'wrong'

def matches(dets, labels, typed):
    available = list(labels)
    for det in sorted(dets,key=lambda d:-d['score']):
        allowed = [a for a in available if not typed or t._map_box_class(det['cls'],{a['cls']})==a['cls']]
        if not allowed: continue
        best = max(allowed,key=lambda a:t.r543._iou(a['box_src_px'],det['box']))
        if t.r543._iou(best['box_src_px'],det['box'])>=.5:
            available.remove(best)
    return [a["id"] for a in labels if a not in available]

models=Path('NativeUIAuditKitModels/Sources/NativeUIAuditKitModels')
fr=models/'Resources/FocusRingDetector.mlmodelc'
cf=Path('reports/work/RESET604/models')
paths=dict(scorerPackage=cf/'ComparativeFocusScorer.mlpackage',gatePackage=cf/'ComparativeFocusGate.mlpackage')
result={}
for arm,package in [('standard',models/'NativeUIModel_tvOS.mlpackage'),('r5',Path('NativeUITrainer/pills560-r5/final.mlpackage'))]:
    pred=t.predict_coreml(package,cases,focusring_model=fr)
    dets={k:v['detections'] for k,v in pred.items()}
    names=t.model_class_names(ct.models.MLModel(str(package)),None)
    comp=predict_comparative_on_detections({'gateThreshold':.28},cases,dets,class_names=names,coreml_paths=paths)
    for name,record in refs.items():
        labels=record['importer_targets']
        ref=next((o['box_src_px'] for o in labels if o['id']==record['focus']['object_id']),None)
        typed=matches(dets[name],labels,True)
        localized=matches(dets[name],labels,False)
        result.setdefault(name,{})[arm]=dict(targets=len(labels),detections=len(dets[name]),typed=len(typed),matchedIds=typed,
            localized=len(localized),targetProposed=any(t.r543._iou(d['box'],ref)>=.5 for d in dets[name]) if ref else None,
            legacy=classify(pred[name]['focusBox'],ref),comparative=classify(comp[name]['focusBox'],ref),sha=record['image_sha256'])
supplied={k:[dict(cls=v['cls'],box=v['box_src_px'],score=1.) for v in r['importer_targets']] for k,r in refs.items()}
leg=t.score_focus_with_focusring(cases,supplied,fr,class_names=ROLES)
com=predict_comparative_on_detections({'gateThreshold':.28},cases,supplied,class_names=ROLES,coreml_paths=paths)
for k,r in refs.items():
    ref=next((v['box_src_px'] for v in r['importer_targets'] if v['id']==r['focus']['object_id']),None)
    result[k]['supplied']=dict(legacy=classify(leg[k]['focusBox'],ref),comparative=classify(com[k]['focusBox'],ref))
(base/'tvos.json').write_text(json.dumps(result,indent=2))
