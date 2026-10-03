"""Finish terminal scoring of an already-completed fit, under its own supervisor."""
import argparse
import os
from pathlib import Path
import sys
import human_annotation_review as h
import train_fullscreen_focus as runner


def child(out):
    h.require(os.environ.get('NUIAK_SUPERVISOR_PID')==str(os.getppid()),'supervised_child_required')
    checked=h.read(out/'validated.json')
    h.require(h.sha(out/'validated.json')==os.environ.get('NUIAK_VALIDATED_SHA256'),'changed_validation')
    doc,fresh=runner.validate(h.checked(h.ROOT,checked['contract']),_verified_frames=checked['frames'])
    h.require(fresh==checked,'changed_evaluation_inputs')
    fit=h.read(h.checked(h.ROOT,h.read(out/'fit.json')['receipt']))
    h.require(fit['epochs']==doc['epochs'] and fit['selection']=='fixed-last-epoch','incomplete_fit')
    checkpoint=h.checked(h.ROOT,fit['checkpoint'],128*1024*1024)
    def offline(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('network_disabled')
    sys.addaudithook(offline)
    from fullscreen_readthrough import evaluate_terminal
    evaluate_terminal(doc,checked,checkpoint,out)


def execute(run,output):
    original=h.local(run);prior=h.read(original/'validated.json')
    doc,checked=runner.validate(h.checked(h.ROOT,prior['contract']),_verified_frames=prior['frames'])
    h.require(doc['version']=='fullscreen-focus-run-v2','terminal_v2_required')
    fit=h.read(original/'training-complete.json')
    h.require(fit['epochs']==doc['epochs'] and fit['selection']=='fixed-last-epoch','incomplete_fit')
    h.checked(h.ROOT,fit['checkpoint'],128*1024*1024)
    out=h.fresh(output);out.mkdir(parents=True)
    h.write(out/'validated.json',checked);h.write(out/'fit.json',dict(receipt=h.ref(original/'training-complete.json')))
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','YOLO_OFFLINE':'true','YOLO_AUTOINSTALL':'false',
        'NUIAK_SUPERVISOR_PID':str(os.getpid()),'NUIAK_VALIDATED_SHA256':h.sha(out/'validated.json')}
    for key in ('TMPDIR','YOLO_CONFIG_DIR','MPLCONFIGDIR','TORCH_HOME'):
        target=out/'cache'/key.lower();target.mkdir(parents=True,exist_ok=True);env[key]=str(target)
    receipt=runner.supervise([sys.executable,str(Path(__file__).resolve()),'--child',str(out)],out,300,64*1024*1024,env)
    print(receipt);return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run');p.add_argument('--output');p.add_argument('--child')
    a=p.parse_args()
    if a.child:child(h.local(a.child))
    else:
        r=execute(a.run,a.output);sys.exit(0 if r['outcome']=='completed' else 2)
