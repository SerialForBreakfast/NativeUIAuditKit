"""Capture one fixed small-control diagnostic with the existing Fixture jobs."""
import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path
from direct_tvos_capture import bind_target, require, write_json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'reports/work/FOCUS-302'
APP = Path('/Users/josephmccraw/Library/Developer/Xcode/DerivedData/TVTestRig-fssavpzkujakgqggjglqjvvrtyoo/Build/Products/Debug/TVTestRig.app')
HELPER = APP/'Contents/Helpers/aatv'
TARGET = '9026ECA9-77DB-4AE6-8FE6-BB239E9571FA'
URL = 'http://127.0.0.1:8080'
EXPORT = Path('/Users/josephmccraw/Developer/TVTestRig/Skills/tvtestrig/references/export-fixture-job.rb')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recipes(source):
    result = []
    for size in (40, 80):
        recipe = copy.deepcopy(source)
        recipe['seed'] = 30200 + size
        composition = recipe['appearance']['composition']
        composition['definitions']['poster'].update(width=size, height=size)
        composition['regions'] = [dict(id=f'region-{i}', axis='row', frame=[x,y,200,200], gap=0,
            items=[dict(id=f'item-{i}',component='poster',content=f'content-{i}',selected=False)])
            for i,(x,y) in enumerate(((100,100),(1500,100),(100,700),(1500,700)))]
        result.append(dict(id=f'size-{size}', role='training', group='portrait-grid-training',
                           requestedSizePoints=size, recipe=recipe))
    return result


def plan():
    require(not OUT.exists(), 'output_collision')
    source = ROOT/'reports/work/FOCUS-REPAIR-233/artifacts/campaign-v3.json'
    data = json.loads(source.read_text())
    entries = recipes(data['recipes'][0]['recipe'])
    OUT.mkdir()
    (OUT/'exports').mkdir()
    for entry in entries:
        path = OUT/(entry['id']+'.json')
        write_json(path,entry['recipe'])
        entry['recipeSHA256'] = digest(path)
    write_json(OUT/'campaign-v3.json',dict(version='focus302-v1',target=TARGET,endpoint=URL,
        recipes=entries,expectedPairs=8,source=dict(path=str(source.relative_to(ROOT)),sha256=digest(source)),
        helperSHA256=digest(HELPER),appSHA256=digest(APP/'Contents/MacOS/TVTestRig'),
        outputCapBytes=512*1024**2,recipeTimeoutSeconds=600,
        purpose='Development-only small native effects. Preserve parent training ancestry. No final audit claim.'))


def cli(name,args):
    reply = subprocess.run([str(HELPER),'--json',*args],capture_output=True,text=True,timeout=30)
    with (OUT/(name+'.stdout')).open('x') as f: f.write(reply.stdout)
    with (OUT/(name+'.stderr')).open('x') as f: f.write(reply.stderr)
    value = json.loads(reply.stdout)
    require(reply.returncode == 0 and value.get('success'), 'cli_failure:'+name+':'+str(value.get('error')))
    return value['data']


def capture(resume=False):
    require(resume == (OUT/'attempt.json').exists(),'existing_attempt_requires_review')
    campaign = json.loads((OUT/'campaign-v3.json').read_text())
    require(digest(HELPER)==campaign['helperSHA256'] and digest(APP/'Contents/MacOS/TVTestRig')==campaign['appSHA256'],'changed_runtime')
    require(shutil.disk_usage(ROOT).free > 3*1024**3, 'insufficient_space')
    binding = bind_target(TARGET,URL)
    prefix='resume-' if resume else ''
    ready = cli(prefix+'readiness',['simulator','readiness','--simulator-udid',TARGET])['simulatorReadiness']['_0']
    require(ready['can_run'] and all(r['state']=='clear' for r in ready['ownership']),'target_ownership')
    require(cli(prefix+'capacity',['fixture','job-capacity','--required-slots','2'])['fixtureJobCapacity']['_0']['canPrepare'],'capacity')
    if resume:
        attempt=json.loads((OUT/'attempt.json').read_text())
        require(attempt['campaignSHA256']==digest(OUT/'campaign-v3.json') and attempt['binding']==binding,'changed_attempt')
    else:
        write_json(OUT/'attempt.json',dict(binding=binding,campaignSHA256=digest(OUT/'campaign-v3.json'),training=False))
    for entry in campaign['recipes']:
        name=entry['id']; path=OUT/(name+'.json')
        require(digest(path)==entry['recipeSHA256'],'changed_recipe')
        if (OUT/(name+'-job.json')).exists():
            require(resume,'existing_job')
            job=json.loads((OUT/(name+'-job.json')).read_text())['jobID']
            state=cli(name+'-resume-status',['fixture','job-status',job])['fixtureJob']['_0']['state']
            require(state=='completed','unfinished_job_requires_review')
            export(name,job)
            continue
        prepared=cli(name+'-prepare',['fixture','prepare','--recipe-json',path.read_text(),'--split','training'])
        write_json(OUT/(name+'-prepared.json'),prepared)
        values=[v['_0'] for v in prepared.values() if isinstance(v,dict) and '_0' in v]
        require(len(values)==1,'prepare_shape')
        job=values[0]['jobID']
        write_json(OUT/(name+'-job.json'),dict(jobID=job))
        cli(name+'-start',['fixture','run-job',job,'--simulator-udid',TARGET,'--fixture-url',URL])
        deadline=time.monotonic()+600
        for poll in range(120):
            status=cli(name+f'-status-{poll:03}',['fixture','job-status',job])['fixtureJob']['_0']
            state=status.get('state',status.get('status'))
            if state=='completed': break
            require(state not in ('failed','cancelled'),'capture_failed:'+name)
            if time.monotonic()>=deadline:
                cli(name+'-cancel',['fixture','cancel-job',job])
                raise ValueError('timeout_cleanup_requires_review')
            time.sleep(5)
        else:
            cli(name+'-cancel',['fixture','cancel-job',job])
            raise ValueError('poll_limit_cleanup_requires_review')
        export(name,job)
        require(sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<campaign['outputCapBytes'],'output_cap')
        print('Completed',name,flush=True)
    cli('postflight',['simulator','readiness','--simulator-udid',TARGET])
    cli('fixture-health',['fixture','env','--fixture-url',URL])
    write_json(OUT/'completion.json',dict(capturedRecipes=2,expectedPairs=8,intake='pending'))


def export(name,job):
    destination=OUT/'exports'/name
    require(not destination.exists(),'existing_export_requires_review')
    reply=subprocess.run(['ruby',str(EXPORT),str(HELPER),job,str(destination)],capture_output=True,text=True,timeout=180)
    with (OUT/(name+'-chunk-export.json')).open('x') as f: f.write(reply.stdout)
    with (OUT/(name+'-chunk-export.log')).open('x') as f: f.write(reply.stderr)
    require(reply.returncode==0,'chunk_export_failed')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('plan','capture','resume'))
    p.add_argument('--output',type=Path,default=OUT);args=p.parse_args()
    OUT=args.output.resolve();require(OUT.is_relative_to(ROOT),'output_boundary')
    {'plan':plan,'capture':capture,'resume':lambda: capture(True)}[args.mode]()
