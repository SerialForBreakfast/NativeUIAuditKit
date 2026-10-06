"""One bounded Run022 native-reserve diagnostic; no training or model selection."""
import subprocess
import sys
import time
import evaluate_artwork213 as a

OUT=a.BASE/'initializer213-baseline01'
CHECKPOINT=a.ROOT/'NativeUITrainer/yolo_runs/replay184-r022/weights/last.pt'
PIN='d40ad18f8d7dea266082de153a3cf078845cf2c53bd277735d79aa4d226f8e6d'


def run():
    a.fresh(OUT)
    prepared=a.BASE/'evaluation213-input01'
    requests=a.checked_requests(prepared)
    a.require(a.sha(CHECKPOINT)==PIN,'initializer_changed')
    import torch
    a.require(torch.backends.mps.is_available(),'mps_unavailable')
    OUT.mkdir()
    command=[sys.executable,'-c',
        'from pathlib import Path; from eval_phase6a import export_predictions; import sys; '
        'export_predictions(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]),"mps",discard_degenerate=True)',
        str(prepared/'native.json'),str(CHECKPOINT),str(OUT/'native.json')]
    a.write(OUT/'preflight.json',dict(checkpointSHA256=PIN,corpusSHA256=requests['native'].content_sha256,
                                    sourceSHA256=a.sha(__file__),command=command,secondsLimit=120))
    started=time.monotonic()
    with (OUT/'inference.log').open('x') as log:
        try:
            result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=120)
        except subprocess.TimeoutExpired:
            a.write(OUT/'failure.json',dict(reason='timeout',seconds=time.monotonic()-started))
            raise
    a.write(OUT/'execution.json',dict(exitCode=result.returncode,seconds=time.monotonic()-started))
    a.require(result.returncode==0,'inference_failed')
    a.require(sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())<16*1024**2,'output_budget')
    a.require(a.sha(CHECKPOINT)==PIN,'initializer_changed')
    requests=a.checked_requests(prepared)
    settings=dict(a.evaluation.PREDICTION_SETTINGS,postprocessing=a.DEGENERATE_POLICY)
    prediction=a.evaluation.validated_artifact(a.evaluation.read(OUT/'native.json'),requests['native'],PIN,expected_settings=settings)
    reports={k:a.evaluation.score(a.evaluation.subset(prediction,requests[k]),requests[k],a.evaluation.load_names())
             for k in ('validation','diagnostic')}
    a.write(OUT/'report.json',dict(reports=reports,checkpointSHA256=PIN,predictionSHA256=a.sha(OUT/'native.json'),
        matchedCUDComparison=False,modelGatePassed=False))
    for key,report in reports.items():
        print(key,[(r['class'],r['support'],r['tp'],r['fp'],r['ap50']) for r in report['perClass'] if r['support']])


if __name__=='__main__':run()
