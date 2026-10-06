"""Matched style210 comparison through the existing ROI trainer/evaluator."""
import argparse
import importlib.metadata
import math
import shutil
import yaml
import roi_style210 as assembly

h,p,e=assembly.h,assembly.p,assembly.e
previous=assembly.previous
BASE=h.ROOT/'reports/work/IOS-STYLE-210/artifacts/training01'
RUNS={'control':'style210-r027','treatment':'style210-r028'}


def configure(arm):
    h.require(arm in RUNS,'unknown_arm')
    previous.OUT=BASE/arm
    previous.RUN=h.ROOT/'NativeUITrainer/yolo_runs'/RUNS[arm]
    previous.configure()


def prepare():
    comparison=assembly.OUT/'comparison.json';doc=p.sealed(comparison)
    for ref in doc['sources']+[doc['source'],doc['admission'],doc['oldProposal'],doc['initializer']]:
        h.checked(h.ROOT,ref,256*1024**2)
    h.require(not BASE.exists() and shutil.disk_usage(h.ROOT).free>8*1024**3,'collision_or_space')
    old=p.sealed(h.checked(h.ROOT,doc['oldProposal']))
    oldreq=e.load_request(h.checked(h.ROOT,doc['oldMembership']),41)
    newreq=e.load_request(h.checked(h.ROOT,doc['cropMembership']),41)
    byid={im.image_id:im for im in oldreq.images+newreq.images}
    h.require(len(byid)==1509 and len(doc['slots']['control'])==len(doc['slots']['treatment'])==1509,'membership')
    for plan in doc['evaluation'].values():e.load_request(h.checked(h.ROOT,plan['manifest']),41)
    import ultralytics.engine.trainer as trainer
    for arm in RUNS:
        configure(arm);out=previous.OUT
        h.require(not previous.RUN.exists(),'run_collision')
        images=out/'dataset/train/images';labels=out/'dataset/train/labels'
        images.mkdir(parents=True);labels.mkdir(parents=True);entries=[];slots=[]
        for i,key in enumerate(doc['slots'][arm]):
            im=byid[key];slot=f'slot-{i:05d}'
            image=images/(slot+'.png');label=labels/(slot+'.txt')
            image.symlink_to(im.image_path);label.symlink_to(im.label_path)
            entries.append(dict(imageID=slot,imagePath=str(image.relative_to(out)),labelPath=str(label.relative_to(out)),
                imageSHA256=im.image_sha256,labelSHA256=im.label_sha256))
            slots.append(dict(slot=slot,source=key))
        h.write(out/'train-input.json',dict(formatVersion=e.INPUT_FORMAT_VERSION,corpusID='style210-'+arm,images=entries))
        e.load_request(out/'train-input.json',41)
        data=out/'dataset/dataset.yaml'
        with data.open('x') as stream:yaml.safe_dump(dict(path=str(out/'dataset'),train='train/images',val='train/images',names=e.load_names()),stream)
        args=dict(old['args'],data=str(data),name=previous.RUN.name,project=str(previous.RUN.parent),exist_ok=False)
        sources=[h.ref(__file__),h.ref(assembly.__file__),h.ref(previous.__file__),h.ref(previous.runner.__file__),
                 h.ref(assembly.r.__file__),h.ref(e.__file__),h.ref(comparison),h.ref(data)]
        h.write(out/'proposal.json',dict(initializer=doc['initializer'],sources=sources,
            membership=h.ref(out/'train-input.json'),evaluation=doc['evaluation'],args=args,
            comparison=h.ref(comparison),samplingSlots=slots,role='train',productionEligible=False),sealed=True)
        h.write(out/'verification.json',dict(count=1509,arm=arm,proposal=h.ref(out/'proposal.json'),trainingOnly=True),sealed=True)
        previous.runner.OUT.mkdir()
        h.write(previous.runner.OUT/'protocol.json',dict(proposal=h.ref(out/'proposal.json'),verification=h.ref(out/'verification.json'),
            sources=sources,trainer=h.ref(trainer.__file__),packages={k:importlib.metadata.version(k) for k in ('torch','ultralytics','numpy','Pillow')},
            args=args,batches=189,budgetBytes=2*1024**3,schedule=assembly.r.c.g.r.schedule(189,10,.25),productionEligible=False),sealed=True)
    print('Prepared Run027/028;1509slots and189batches each; no training launched')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','train','infer','report']);parser.add_argument('--arm',choices=list(RUNS))
    a=parser.parse_args()
    if a.mode=='prepare':prepare()
    else:
        h.require(a.arm is not None,'arm_required');configure(a.arm)
        if a.mode=='train':previous.train()
        else:getattr(previous.runner,a.mode)()
