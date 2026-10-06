"""Fixed24training-frame resolution diagnostic; no training/threshold search."""
from pathlib import Path
import subprocess
import sys
import time
import fullframe_replay_baseline as baseline

a=baseline.a
OUT=a.ROOT/'reports/work/REPLAY-216/artifacts/scroll-resolution01'
BASE_REPORT='9e6d592891ad6fabab38c969447248d1db1be5df110d3577780f98ddf0f175ca'


def select(request,cid):
    return [im for im in request.images if any(int(line.split()[0])==cid for line in im.label_path.read_text().splitlines() if line.strip())]


def run():
    a.fresh(OUT)
    a.require(a.sha(baseline.OUT/'report.json')==BASE_REPORT and a.sha(baseline.CHECKPOINT)==baseline.PIN,'source_changed')
    old=a.evaluation.read(baseline.OUT/'report.json')
    request=a.artifact.load_request(baseline.OUT/'input.json',41)
    pre=a.document(baseline.OUT/'preflight.json')
    a.require(request.content_sha256==pre['inputContentSHA256'],'membership_changed')
    a.require(a.sha(baseline.OUT/'predictions.json')==old['predictionSHA256'],'predictions_changed')
    settings=dict(a.evaluation.PREDICTION_SETTINGS,postprocessing=a.DEGENERATE_POLICY)
    previous=a.evaluation.validated_artifact(a.evaluation.read(baseline.OUT/'predictions.json'),request,baseline.PIN,expected_settings=settings)
    names=a.evaluation.load_names();chosen=select(request,names.index('scrollIndicator'))
    a.require(len(chosen)==24,'scroll_membership')
    import torch
    a.require(torch.backends.mps.is_available(),'mps_unavailable')
    (OUT/'inputs').mkdir(parents=True);entries=[]
    for i,im in enumerate(chosen):
        image=f'inputs/{i:03d}.png';label=f'inputs/{i:03d}.txt'
        (OUT/image).symlink_to(im.image_path);(OUT/label).symlink_to(im.label_path)
        entries.append(dict(imageID=im.image_id,imagePath=image,labelPath=label,imageSHA256=im.image_sha256,labelSHA256=im.label_sha256))
    a.write(OUT/'input.json',dict(formatVersion=a.artifact.INPUT_FORMAT_VERSION,corpusID='scroll-training24',images=entries))
    selected=a.artifact.load_request(OUT/'input.json',41)
    a.write(OUT/'preflight.json',dict(sourceSHA256=a.sha(__file__),checkpointSHA256=baseline.PIN,
        corpusSHA256=selected.content_sha256,baselineReportSHA256=BASE_REPORT,imgsz=1280,secondsLimit=180))
    command=[sys.executable,'-c','from pathlib import Path; from eval_phase6a import export_predictions; import sys; export_predictions(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]),"mps",imgsz=1280,discard_degenerate=True)',str(OUT/'input.json'),str(baseline.CHECKPOINT),str(OUT/'predictions.json')]
    start=time.monotonic()
    with (OUT/'inference.log').open('x') as log:
        try:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        except subprocess.TimeoutExpired:
            a.write(OUT/'failure.json',dict(reason='timeout',seconds=time.monotonic()-start));raise
    elapsed=time.monotonic()-start
    a.write(OUT/'execution.json',dict(exitCode=result.returncode,seconds=elapsed))
    a.require(result.returncode==0,'inference_failed')
    a.require(sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())<32*1024**2,'output_budget')
    fresh=a.artifact.load_request(OUT/'input.json',41)
    a.require(fresh.content_sha256==selected.content_sha256 and a.sha(baseline.CHECKPOINT)==baseline.PIN,'inputs_changed')
    prediction=a.evaluation.validated_artifact(a.evaluation.read(OUT/'predictions.json'),fresh,baseline.PIN,expected_settings=dict(settings,imgsz=1280))
    reports={'640':a.evaluation.score(a.evaluation.subset(previous,selected),selected,names),
             '1280':a.evaluation.score(prediction,selected,names)}
    a.write(OUT/'report.json',dict(reports=reports,checkpointSHA256=baseline.PIN,predictionSHA256=a.sha(OUT/'predictions.json'),
        role='training diagnostic; not held-out qualification',seconds1280=elapsed,modelGatePassed=False))
    print({k:next(r for r in v['perClass'] if r['class']=='scrollIndicator') for k,v in reports.items()})


if __name__=='__main__':run()
