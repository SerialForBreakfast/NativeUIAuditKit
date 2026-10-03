"""Qualify the resident augmented training loader on fixed training-only originals."""
import random
import time
import numpy as np
import human_annotation_review as h
from reference_benchmark45 import prepare_environment
from train_fullscreen_focus import source_image,augmentation_options
from fullscreen_readthrough import dataset_type


def main():
    prepare_environment()
    from ultralytics.cfg import get_cfg
    base=h.ROOT/'reports/work/FOCUS-AUGMENTATION-47'
    source=h.ROOT/'reports/work/FULLSCREEN-EXPERIMENT-41/run/validated.json'
    checked=h.read(source)
    frames=sorted([f for f in checked['frames'] if f['split']=='train'],key=lambda f:f['image']['sha256'])[:64]
    for f in frames:source_image(f['image'],f)
    reports=[]
    for name in ('translation','translation-scale'):
        doc=h.read(base/'contracts'/(name+'.json'));options=augmentation_options(doc)
        cfg=get_cfg(overrides=dict(imgsz=640,mosaic=0.,mixup=0.,copy_paste=0.,flipud=0.,fliplr=0.,
            hsv_h=0.,hsv_s=0.,hsv_v=0.,degrees=0.,shear=0.,perspective=0.,**options))
        random.seed(42);np.random.seed(42)
        ds=dataset_type()(frames,data={'names':{0:'focusedControl'},'channels':3},imgsz=640,batch_size=8,
                           augment=True,hyp=cfg,rect=False,stride=32,pad=0.)
        counts=[];clipped=0;start=time.monotonic()
        for i in range(len(frames)):
            sample=ds[i];boxes=sample['bboxes'].numpy()
            h.require(tuple(sample['img'].shape)==(3,640,640),'probe_shape')
            h.require(np.isfinite(boxes).all() and ((boxes>=0)&(boxes<=1)).all(),'probe_bounds')
            edges=np.c_[boxes[:,:2]-boxes[:,2:]/2,boxes[:,:2]+boxes[:,2:]/2]
            h.require((edges>=-1e-6).all() and (edges<=1+1e-6).all(),'probe_edges')
            clipped+=int(((edges<1e-6)|(edges>1-1e-6)).any())
            counts.append(len(sample['cls']))
        h.require(counts==[1]*64,'probe_focus_label_lost')
        reports.append(dict(arm=name,options=options,frames=64,retainedFocusLabels=sum(counts),
                            framesTouchingBoundary=clipped,seconds=time.monotonic()-start))
    h.write(h.fresh(base/'loader-probe.json'),dict(source=h.ref(source),members=[f['id'] for f in frames],
        arms=reports,scope='Training-only64frame probe, not proof every random draw is unclipped.'))
    print(reports)


if __name__=='__main__':main()
