"""Measure hash-only child recheck and actual USB preprocessing, without models."""
import time
import human_annotation_review as h
import train_fullscreen_focus as runner


def main():
    base=h.ROOT/'reports/work/FULLSCREEN-READTHROUGH-40'
    previous=h.read(base/'qualified-inputs.json')
    start=time.monotonic()
    _,checked=runner.validate(base/'run-draft-v2.json',inputs_only=True,_verified_frames=previous['frames'])
    h.require(checked['frames']==previous['frames'],'recheck_changed_membership')
    elapsed=time.monotonic()-start
    from fullscreen_readthrough import dataset_type
    from ultralytics.cfg import get_cfg
    samples=[next(f for f in checked['frames'] if f['split']==role) for role in ('train','evaluation')]
    start=time.monotonic()
    dataset=dataset_type()(samples,data={'names':{0:'focusedControl'},'channels':3},
        imgsz=640,batch_size=2,augment=False,hyp=get_cfg(),rect=False,stride=32)
    rows=[]
    for index in range(len(samples)):
        sample=dataset[index]
        h.require(tuple(sample['img'].shape)==(3,640,640) and len(sample['cls'])==1,'invalid_usb_preprocessing')
        rows.append(dict(id=samples[index]['id'],shape=list(sample['img'].shape),focusedLabels=len(sample['cls'])))
    h.write(base/'readthrough-benchmark.json',dict(hashRecheckSeconds=elapsed,
        preprocessingSeconds=time.monotonic()-start,samples=rows,
        sources=checked['sources'],note='Two-frame loader qualification, not throughput forecast or model execution.'))
    print('Recheck seconds',elapsed,'; actual USB transforms passed.')


if __name__=='__main__':main()
