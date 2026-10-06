"""Qualify and baseline the189training-frame proposal; never train."""
from pathlib import Path
import subprocess
import sys
import time
import fullframe_replay_audit as audit
import evaluate_artwork213 as a
from page_regeneration41 import checked_export_labels
from annotation_schema_validation import validate_sidecar_structure

POOL=a.ROOT/'reports/work/REPLAY-216/artifacts/fullframe-pool02.json'
POOL_PIN='4f9d0cd0eb448f7b6f564185b5857c36c648536a742642c67aff09afa05face0'
OUT=a.ROOT/'reports/work/REPLAY-216/artifacts/fullframe-baseline02'
CHECKPOINT=a.ROOT/'NativeUITrainer/yolo_runs/replay184-r022/weights/last.pt'
PIN='d40ad18f8d7dea266082de153a3cf078845cf2c53bd277735d79aa4d226f8e6d'


def prepare():
    a.fresh(OUT);a.require(a.sha(POOL)==POOL_PIN and a.sha(CHECKPOINT)==PIN,'source_changed')
    doc=a.evaluation.read(POOL);a.require(doc['selectedCount']==len(doc['rows'])==189,'membership')
    names=a.evaluation.load_names();categories={n:i for i,n in enumerate(names)};entries=[];sources=[]
    for row in doc['rows']:
        a.require(row['split']=='train','role_changed')
        paths={k:audit.source.h.checked(a.ROOT,row[k]) for k in ('image','annotation','label')}
        annotation=a.evaluation.read(paths['annotation']);validate_sidecar_structure(annotation)
        a.require(annotation['imageSHA256']==row['image']['sha256'],'annotation_image_binding')
        checked_export_labels(annotation,paths['label'].read_text(),categories)
        sources.append(paths)
        index=len(entries)
        entries.append(dict(imageID=row['id'],imagePath=f'inputs/{index:04d}.png',labelPath=f'inputs/{index:04d}.txt',
            imageSHA256=row['image']['sha256'],labelSHA256=row['label']['sha256']))
    (OUT/'inputs').mkdir(parents=True)
    for entry,paths in zip(entries,sources):
        for kind in ('image','label'):(OUT/entry[kind+'Path']).symlink_to(paths[kind])
    a.write(OUT/'input.json',dict(formatVersion=a.artifact.INPUT_FORMAT_VERSION,corpusID='fullframe-replay-training189',images=entries))
    request=a.artifact.load_request(OUT/'input.json',41)
    a.write(OUT/'preflight.json',dict(poolSHA256=POOL_PIN,inputContentSHA256=request.content_sha256,
        checkpointSHA256=PIN,sourceSHA256=a.sha(__file__),role='training-only diagnostic',secondsLimit=300,outputLimitBytes=32*1024**2))


def infer():
    pre=a.document(OUT/'preflight.json')
    a.require(pre['poolSHA256']==POOL_PIN and a.sha(POOL)==POOL_PIN and a.sha(CHECKPOINT)==PIN and pre['sourceSHA256']==a.sha(__file__),'source_changed')
    a.require(not any((OUT/name).exists() for name in ('predictions.json','execution.json','inference.log','failure.json')),'output_collision')
    request=a.artifact.load_request(OUT/'input.json',41)
    a.require(request.content_sha256==pre['inputContentSHA256'],'membership_changed')
    import torch
    a.require(torch.backends.mps.is_available(),'mps_unavailable')
    command=[sys.executable,'-c','from pathlib import Path; from eval_phase6a import export_predictions; import sys; export_predictions(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]),"mps",discard_degenerate=True)',str(OUT/'input.json'),str(CHECKPOINT),str(OUT/'predictions.json')]
    started=time.monotonic()
    with (OUT/'inference.log').open('x') as log:
        try:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=300)
        except subprocess.TimeoutExpired:
            a.write(OUT/'failure.json',dict(reason='timeout',seconds=time.monotonic()-started));raise
    a.write(OUT/'execution.json',dict(exitCode=result.returncode,seconds=time.monotonic()-started))
    a.require(result.returncode==0,'inference_failed')
    a.require(sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())<32*1024**2,'output_budget')
    a.require(a.sha(POOL)==POOL_PIN and a.sha(CHECKPOINT)==PIN,'source_changed')
    request=a.artifact.load_request(OUT/'input.json',41)
    a.require(request.content_sha256==pre['inputContentSHA256'],'membership_changed')
    predictions=a.evaluation.validated_artifact(a.evaluation.read(OUT/'predictions.json'),request,PIN,
        expected_settings=dict(a.evaluation.PREDICTION_SETTINGS,postprocessing=a.DEGENERATE_POLICY))
    report=a.evaluation.score(predictions,request,a.evaluation.load_names())
    a.write(OUT/'report.json',dict(report=report,checkpointSHA256=PIN,predictionSHA256=a.sha(OUT/'predictions.json'),
        role='training fit diagnostic; not independent evaluation',modelGatePassed=False))
    print([(r['class'],r['support'],r['tp'],r['fp']) for r in report['perClass'] if r['support']])


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','infer']);globals()[p.parse_args().mode]()
