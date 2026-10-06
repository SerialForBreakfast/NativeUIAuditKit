"""Independent checks of returned training/configuration evidence, without loading weights."""
import math
import argparse
from pathlib import Path
from generator_asset_plan import inventory_metadata
from artwork200_campaign import sha,write
from export_artwork204 import ROOT
from shared_transfer import require

BASE=ROOT/'reports/work/WORKER-213/artifacts/return01/payload'
OUT=BASE.parent/'training-review01.json'


def check_epochs(epochs, slots):
    batches=(slots+3)//4
    require([x['epoch'] for x in epochs]==list(range(10)),'epochs')
    order=[f'{j:04d}.png' for j in range(slots)]
    for i,x in enumerate(epochs):
        updates=((i+1)*batches)//16-(i*batches)//16
        require(x['batches']==batches and x['updates']==updates,'batch_update_counts')
        require([Path(v).name for v in x['order']]==order,'slot_order')
        require(len(x['losses'])==batches and all(math.isfinite(v) for v in x['losses']),'losses')
    return batches*10,(batches*10)//16


def run(base=BASE,out=OUT,profile='213'):
    require(profile in ('213','216'),'profile')
    base=base.absolute();out=out.absolute()
    require(base.resolve()==base and base.is_relative_to(ROOT) and
            out.resolve()==out and out.is_relative_to(ROOT),'boundary')
    require(not out.exists(),'output_collision')
    pins={'worker198_full_trainer.py':'54570b518272bf18ae29f59caaa04d7d13927db8a77a1b41208051d6ced5b3de',
          'worker213_native_artwork.py':'51805eb16d6c46e008cc45534a203808c1a664a7f53a4ee213e95e0ff363f0e2'}
    if profile=='216':
        pins={'worker198_full_trainer.py':'07f226e011278d03640d65eab2778af5ca472260b625e70b2440524a307ad11f',
              'worker216_replay.py':'966c1dd311e0f26477a0fe44c05dde49a277fb72d6126267e3e79ddc448ffec6'}
    for name,digest in pins.items():require(sha(base/'scripts'/name)==digest,'source_changed')
    data=inventory_metadata(base/'evidence/training-results.json',max_bytes=(8 if profile=='216' else 4)*1024**2,
                            max_nodes=150000 if profile=='216' else 100000);results=[]
    require([r['arm'] for r in data]==['control','treatment'],'arms')
    require([r['run'] for r in data]==(['029','030'] if profile=='213' else ['031','032']),'run_identity')
    config=None
    expected=dict(batch=4,epochs=10,nbs=64,imgsz=640,optimizer='AdamW',lr0=.0001,lrf=1.,
                  warmup_epochs=0,seed=42,amp=False,resume=False,workers=0,device='0')
    zeros=('mosaic','mixup','cutmix','copy_paste','hsv_h','hsv_s','hsv_v','degrees','translate','scale','shear','perspective','flipud','fliplr','erasing','multi_scale')
    for arm in data:
        require(len(arm['results'])==1,'repetition_count');r=arm['results'][0];cfg=r['effective_config']
        require(all(cfg[k]==v for k,v in expected.items()) and all(cfg[k]==0 for k in zeros),'configuration')
        normalized={k:v for k,v in cfg.items() if k not in ('model','data','project','name','save_dir')}
        if config is None:config=normalized
        else:require(config==normalized,'arm_configuration_difference')
        batches,updates=check_epochs(r['epochs'],572 if profile=='213' else 1569)
        require(len(r['validations'])==11 and all(v['images']==512 and v['batches']==64 for v in r['validations']),'validation_role_counts')
        cp=(base/'checkpoints'/(arm['arm']+'-last.pt') if profile=='213'
            else base/arm['arm']/'last.pt');digest=sha(cp)
        require(r['checkpoints']['run'+arm['run']+'/weights/last.pt']==digest,'checkpoint_changed')
        results.append(dict(arm=arm['arm'],checkpointSHA256=digest,epochs=10,batches=batches,updates=updates,seconds=r['total_seconds']))
    evaluations=inventory_metadata(base/'evidence/evaluation-results.json')
    require(len(evaluations)==10,'evaluation_count')
    seen=set()
    for row in evaluations:
        key=(row['arm'],row['partition']);require(key not in seen,'duplicate_evaluation');seen.add(key)
        require(row['count']==dict(validation=24,test=12,fit=135,page=37,combined=413)[row['partition']],'evaluation_membership')
        path=base/'predictions'/Path(row['prediction']).name
        require(path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],'prediction_changed')
        require(row['checkpointSHA256']==next(r['checkpointSHA256'] for r in results if r['arm']==row['arm']),'prediction_model')
    require(seen=={(arm,part) for arm in ('control','treatment') for part in ('validation','test','fit','page','combined')},'evaluation_cells')
    write(out,dict(profile=profile,results=results,evaluations=len(evaluations),sourcePins=pins,
        evidenceSHA256=sha(base/'evidence/training-results.json'),modelGatePassed=False,
        sourceReview='Byte identity and reported configuration/counts verified; source semantics and actual model efficacy require independent review'))
    print(results)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',choices=['213','216'],default='213')
    parser.add_argument('--base',type=Path,default=BASE)
    parser.add_argument('--out',type=Path,default=OUT)
    run(**vars(parser.parse_args()))
