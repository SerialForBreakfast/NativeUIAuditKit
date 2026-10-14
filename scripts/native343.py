"""Capture the existing native scene without changing its recipe."""
import argparse
import time
from pathlib import Path
from PIL import Image
import direct_tvos_capture as d
import fixture_rendered_body as body
import research_queue as q
from focus_batch_harness import lock
from research_campaign340 import pin

TARGET='9026ECA9-77DB-4AE6-8FE6-BB239E9571FA'


def identity(snapshot):
    device,scene=snapshot['device'],snapshot['scene']
    return [device['simulator_udid'],device['fixture_instance_id'],device['fixture_run_id'],scene['recipe']]


def signature(snapshot,initial,expected):
    q.require(identity(snapshot)==identity(initial),'runtime_or_recipe_changed')
    scene=snapshot['scene'];obs=scene['focus_observation'];diag=scene['observation_diagnostics']
    q.require(scene['is_settled'] and obs['verified'] and obs['source']=='uikit_focus_system','unverified_focus')
    if expected is None:
        q.require(diag.get('nativeFocusResolved') is True and diag.get('reason')=='ready' and
                  diag.get('nativeProbe',{}).get('referenceFocused') is True, 'unfocused_reference_unverified')
    q.require(obs.get('observedID')==scene.get('focused_element_id')==expected,'wrong_focus')
    q.require(obs['generation']==scene['observation_generation']==diag['sampledGeneration'],'generation_mismatch')
    q.require(0<=diag['sampleAgeMilliseconds']<=200 and diag['stableMilliseconds']>=150,'stale_or_moving')
    q.require(snapshot['startedAt']-1<=scene['timestamp']<=snapshot['finishedAt']+1,'stale_timestamp')
    size=[scene['scene_width'],scene['scene_height']]
    elements=scene['elements'];ids=[e['element_id'] for e in elements]
    planned=set(obs['plannedFocusIDs'])
    composition=scene['recipe'].get('appearance',{}).get('composition',{})
    definitions=composition.get('definitions',{})
    decorations={i['id'] for r in composition.get('regions',[]) for i in r['items']
                 if definitions.get(i['component'],{}).get('kind') in ('text','artwork')}
    q.require(len(ids)==len(set(ids)) and planned<=set(ids) and set(ids)-planned<=decorations,'missing_controls')
    q.require([e['element_id'] for e in elements if e['is_focused']]==([] if expected is None else [expected]),'focus_conflict')
    for e in elements:
        if e['element_id'] in planned:
            q.require(body.validate(e.get('rendered_body_geometry'),size,e['element_id'],obs['generation']) is not None,'missing_body')
    return [obs['generation'],expected,size,elements,scene.get('semantic_inventory')]


def settle(fixture,initial,expected):
    until=time.monotonic()+10
    reason='no_observation'
    while time.monotonic()<until:
        value=fixture.snapshot()
        q.require(identity(value)==identity(initial),'runtime_or_recipe_changed')
        try:signature(value,initial,expected);return value
        except (ValueError,RuntimeError,KeyError) as error:
            reason=str(error);time.sleep(.1)
    raise ValueError('settle_timeout:'+reason)


def capture(output,execute=False):
    binding=d.bind_target(TARGET,'http://127.0.0.1:8080');f=d.Fixture(binding['endpoint']);initial=f.snapshot()
    ids=initial['scene']['focus_observation']['plannedFocusIDs'];original=initial['scene']['focused_element_id']
    q.require(len(ids)==4 and original in ids,'unexpected_scene')
    signature(initial,initial,original)
    plan=dict(binding=binding,initial=initial,targets=ids,framesPerTarget=2,role='development',
              correlation='capture_interval_only',trainingEligible=False,timeoutSeconds=120,maxOutputBytes=100_000_000)
    if not execute:return plan
    output=d.new_output(output);output.mkdir(parents=True);q.save(output/'plan.json',plan)
    records=[];cleanup=False;error=None;start=time.monotonic();mutated=False;last=original
    with lock():
        try:
            for target in [original]+[i for i in ids if i!=original]:
                q.require(time.monotonic()-start<100,'capture_timeout')
                signature(f.snapshot(),initial,last)
                if target!=last:
                    mutated=True
                    reply=f.request('/focus/set',{'element_id':target,'settle_time_ms':150})
                    q.save(output/f'{target}-response.json',reply)
                last=target;settle(f,initial,target)
                for repeat in range(2):
                    before=f.snapshot();sig=signature(before,initial,target)
                    q.require(d.bind_target(TARGET,binding['endpoint'])==binding,'binding_changed')
                    path=output/f'{target}-{repeat}.png';begin=time.time()
                    d.capture_screenshot(TARGET,path,timeout=15)
                    end=time.time();after=f.snapshot()
                    record=dict(before=before,after=after,image=pin(path),captureStart=begin,captureEnd=end,target=target)
                    q.save(output/f'{target}-{repeat}.json',record)
                    q.require(signature(after,initial,target)==sig,'capture_interval_changed')
                    with Image.open(path) as image:image.load();q.require(list(image.size)==sig[2],'image_dimensions')
                    records.append(record)
                    q.require(sum(p.stat().st_size for p in output.rglob('*') if p.is_file())<100_000_000,'output_limit')
        except Exception as exc:error=str(exc)
        finally:
            try:
                current=settle(f,initial,last);q.require(identity(current)==identity(initial),'cleanup_identity_changed')
                if mutated:
                    q.require(current['scene']['focused_element_id']==last,'cleanup_external_focus_change')
                    f.request('/focus/set',{'element_id':original,'settle_time_ms':150})
                settle(f,initial,original);cleanup=True
            except Exception as exc:error=(error or '')+'; cleanup: '+str(exc)
            q.save(output/'capture.json',dict(plan=pin(output/'plan.json'),frames=records,
                complete=len(records)==8 and cleanup and error is None,cleanup=cleanup,error=error,
                seconds=time.monotonic()-start,trainingEligible=False,
                limitations=['Capture intervals are not atomic framebuffer identities.',
                    'Installed binary hashes are pinned. Matching source build remains unverified.',
                    'One retained native scene is development evidence, not real-app qualification.']))
    q.require(error is None,error or 'capture_failed')
    return dict(frames=len(records),cleanup=cleanup,output=str(output))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true')
    parser.add_argument('--output',type=Path,default=q.ROOT/'reports/work/FOCUS-343/native-corner')
    args=parser.parse_args();print(capture(args.output,args.execute))
