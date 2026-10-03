"""Read/resize parity probe using the installed Ultralytics load_image method; no model."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
from types import SimpleNamespace
import artifact_storage as s


def qualify(old, new):
    for key,sub in (('YOLO_CONFIG_DIR','.ultralytics'),('MPLCONFIGDIR','.mplconfig'),
                    ('TORCH_HOME','.torch'),('TMPDIR','.tmp')):
        os.environ[key]=str(s.ROOT/'NativeUITrainer'/sub)
    from ultralytics.data.base import BaseDataset
    import cv2
    rows=[]
    for split in ('train','val','test'):
        before=sorted((old/split/'images').glob('*.png'))
        after=sorted((new/split/'images').glob('*.png'))
        s.require([p.name for p in before]==[p.name for p in after],'split_membership_changed')
        for path in before:
            s.require(s.resolve_input(path.resolve()) == (new/split/'images'/path.name).resolve(),
                      'image_target_changed')
            name=path.stem+'.txt'
            s.require((old/split/'labels'/name).read_bytes()==(new/split/'labels'/name).read_bytes(),
                      'label_bytes_changed')
        for i in sorted({int(k*(len(before)-1)/15) for k in range(16)}):
            paths=[before[i],after[i]]
            for path in paths:
                s.require(not path.with_suffix('.npy').exists(),'unexpected_image_cache')
            loader=SimpleNamespace(ims=[None,None],im_files=[str(p) for p in paths],
                npy_files=[p.with_suffix('.npy') for p in paths],channels=3,cv2_flag=cv2.IMREAD_COLOR,
                imgsz=640,augment=False)
            values=[];timings=[]
            for repeat in range(2):
                for j in range(2):
                    start=time.perf_counter();array,original,resized=BaseDataset.load_image(loader,j)
                    timings.append(dict(repeat=repeat,storage='local' if j==0 else 'ssd',
                                        seconds=time.perf_counter()-start))
                    values.append((hashlib.sha256(array.tobytes()).hexdigest(),original,resized))
            s.require(all(value==values[0] for value in values),'loader_tensor_changed')
            rows.append(dict(split=split,image=paths[0].name,sha256=values[0][0],timings=timings))
    return dict(version='storage-loader-parity-v1',samples=len(rows),rows=rows,
        scope='Actual Ultralytics load_image decode/resize only; not augmentation, model or epoch throughput. OS caches not flushed; first/repeat timings are not cold-disk measurements.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--old',type=Path,required=True);p.add_argument('--new',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=s.local_output(a.output);s.require(not out.exists(),'output_collision')
    result=qualify(a.old,a.new)
    with out.open('x') as f:json.dump(result,f,indent=2)
    print('loader parity:',result['samples'])
