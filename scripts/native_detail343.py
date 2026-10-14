"""Measure native control coverage without changing inference crops."""
import numpy as np
import research_queue as q
from research_campaign340 import pin
import additive341 as a

OUT=None


def fraction(box,window):
    x,y,w,h=box;u,v=window
    return max(0,min(x+w,u+32)-max(x,u))*max(0,min(y+h,v+32)-max(y,v))/(w*h)


def run():
    config=q.load(OUT/'config.json')
    for ref in config['inputs']:q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'input_hash')
    a.t.set_num_threads(2)
    capture=q.load(q.ROOT/'reports/work/FOCUS-343/native-corner-r2/capture.json')
    evaluated=q.load(q.QUEUE/'jobs/focus343-native/attempts/1/out/diagnostic.json')
    lookup={f['image']['sha256']:f for f in capture['frames']};output=[]
    for row in evaluated['rows']:
        if not row['changed']:continue
        images=[a.r.s.image(v['path'],v['sha256']) for v in row['images']]
        values=np.stack([a.r.s.encoded(*images,(192,128))[0]])
        old=[list(map(int,w)) for w in a.r.windows(a.t.from_numpy(values))[0]]
        added=a.added_windows(a.t.from_numpy(values))[0];windows=old+([] if added is None else [list(map(int,added))])
        controls=[]
        for ref in row['images']:
            frame=lookup[ref['sha256']];scene=frame['before']['scene']
            element=next(e for e in scene['elements'] if e['element_id']==frame['target'])
            box=element['rendered_body_geometry']['full_pixel_bounds'];w,h=scene['scene_width'],scene['scene_height']
            scaled=[box[0]*192/w,box[1]*128/h,box[2]*192/w,box[3]*128/h]
            controls.append(dict(target=frame['target'],nativeBody=box,resizedBody=scaled,
                originalCoverage=max(fraction(scaled,b) for b in old),
                extendedCoverage=max(fraction(scaled,b) for b in windows)))
        output.append(dict(id=row['id'],originalWindows=old,addedWindow=added,controls=controls))
    q.save(OUT/'diagnostic.json',dict(inputs=config['inputs'],rows=output,cropsChanged=False,
        limitation='Body coverage does not measure the full shadow or identify the cause of model failure.',
        nextAction='Use native matched-size controls before more content-only training. Preserve the original inference path.'))


def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS343';id='focus343-native-detail'
    q.require(not (q.QUEUE/'jobs'/id).exists(),'existing_job')
    paths=['scripts/native_detail343.py','scripts/additive341.py','scripts/regions313.py',
        'reports/work/FOCUS-343/native-corner-r2/capture.json',
        'reports/work/research-queue/jobs/focus343-native/attempts/1/out/diagnostic.json']
    refs=[pin(q.ROOT/path) for path in paths];config=folder/(id+'-config.json');q.save(config,dict(inputs=refs))
    spec=dict(version=q.SPEC_VERSION,id=id,task='FOCUS343',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
        hypothesis='Tiny native controls may lack useful detail coverage despite strong native growth.',
        decisionRule='Report actual crop coverage and resized body dimensions. Coverage alone does not prove a learned-feature defect.',
        adapter=dict(type='python-callable',steps=['native_detail343.run'],outputAttributes=['native_detail343.OUT']),
        inputs=refs,stage=[{'from':pin(config),'to':'config.json'}],limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    path=folder/(id+'.json');q.save(path,spec);print(q.submit(path))


if __name__=='__main__':register()
