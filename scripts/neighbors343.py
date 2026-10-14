"""Compare neighboring focus with identical reviewed artwork."""
import os
import re
import shutil
import subprocess
import time
import research_queue as q
from research_campaign340 import pin
import authored319 as authored
import report_additive341 as report
from diagnostics343 import counts,REPORTS
from focus_batch_harness import lock

OUT=None
BINARY=q.ROOT/'reports/work/HCF-335/pilot/renderer-8925f2f627094c58b27a2cf1ff56fefc'
BINARY_HASH='85b2e17e1dce9ae95644cbf25ac303cab95027f919126ab01388cfeb205dce01'


def run():
    started=time.monotonic();config=q.load(OUT/'config.json')
    for ref in config['inputs']:q.require(q.digest(q.local_path(q.ROOT,ref['path']))==ref['sha256'],'input_hash')
    p=config['plan'];q.require(q.digest(BINARY)==BINARY_HASH,'renderer_binary_changed')
    q.require(q.digest(authored.SCRIPT)==p['renderer']['sha256'],'renderer_source_changed')
    names=sorted(set(re.findall(r'"([^"/]+\.jpg)"',authored.SCRIPT.read_text())))
    q.require(len(names)==16,'asset_contract_changed');rows=[];annotations=[]
    env=dict(os.environ,TMPDIR=str(q.ROOT/'.build'))
    with lock():
        for asset in [p['assets'][config['assetIndex']]]:
            folder=OUT/asset['id'];folder.mkdir();images=q.ROOT/config['assetDirectory']
            source=q.local_path(q.ROOT,asset['image']['path'])
            q.require(q.digest(source)==asset['image']['sha256'],'artwork_hash')
            for name in names:q.require(q.digest(images/name)==asset['image']['sha256'],'staged_artwork_changed')
            for layout in p['layouts']:
                states=[]
                for target in layout['targets']:
                    destination=folder/(layout['name']+'-'+target)
                    command=[str(BINARY),'--layout',layout['name'],'--resolution','1080p','--assets-dir',str(images),
                             '--output-dir',str(destination),'--focus-id',target]
                    with (folder/(destination.name+'.log')).open('x') as log:
                        subprocess.run(command,cwd=q.ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
                    image,annotation=authored.frame(destination,layout['name'],target)
                    if states:q.require(annotation['unfocusedImageSHA256']==annotations[-1]['unfocusedImageSHA256'],'base_changed')
                    states.append(image);annotations.append(annotation)
                    q.require(sum(f.stat().st_size for f in OUT.rglob('*') if f.is_file())<90_000_000,'output_limit')
                q.require(states[0]['sha256']!=states[1]['sha256'],'invisible_focus_change')
                for a,b in [(0,1),(1,0),(0,0),(1,1)]:
                    rows.append(dict(id=f'{asset["id"]}-{layout["name"]}-{a}-{b}',images=[states[a],states[b]],
                        changed=int(a!=b),condition='movement' if a!=b else 'identical',layout=layout['name'],
                        group=asset['groups'][0],role='development',ancestryRole='train'))
    generated=time.monotonic();report.a.t.set_num_threads(2)
    baseline=report.score_rows(report.a.e.load_candidate(q.ROOT/'reports/work/FOCUS-329/run/last.pt'),rows,False)
    scores={'FOCUS329':dict(counts=counts(rows,baseline),probabilities=baseline.tolist(),
        model=pin(q.ROOT/'reports/work/FOCUS-329/run/last.pt'))}
    for name,path in REPORTS.items():
        ref=q.load(q.ROOT/path)['model'];q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'model_hash')
        values=report.score_rows(report.a.load(q.ROOT/ref['path']),rows,True)
        scores[name]=dict(counts=counts(rows,values,baseline),probabilities=values.tolist(),model=ref)
    q.save(OUT/'diagnostic.json',dict(rows=rows,scores=scores,annotations=annotations,inputs=config['inputs'],
        seconds=time.monotonic()-started,generationSeconds=generated-started,modelAccepted=False,
        trainingEligible=False,independentGroups=len({r['group'] for r in rows}),
        limitations=['Authored effects only. Existing training artwork prevents final evaluation use.',
                    'Identical-frame negatives test a basic control, not fixed-focus content changes.',
                    '4 layouts and the current renderer appearance only. Other themes remain unsupported.']))


def register(index):
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS343';folder.mkdir(exist_ok=True);id=f'focus343-identical-neighbors-r2-{index}'
    q.require(not (q.QUEUE/'jobs'/id).exists(),'existing_job');p=authored.plan()
    paths=['scripts/neighbors343.py','scripts/diagnostics343.py','scripts/authored319.py','scripts/report_additive341.py',
           'scripts/additive341.py','reports/work/FOCUS-329/run/last.pt']+list(REPORTS.values())
    asset=p['assets'][index];images=q.ROOT/f'reports/work/FOCUS-343/identical-assets-{index}'
    q.require(not images.exists(),'asset_directory_collision');images.mkdir()
    names=sorted(set(re.findall(r'"([^"/]+\.jpg)"',authored.SCRIPT.read_text())))
    for name in names:shutil.copyfile(q.ROOT/asset['image']['path'],images/name)
    refs=[pin(q.ROOT/path) for path in paths]+[pin(BINARY),asset['image']]+[pin(images/n) for n in names]
    config=folder/(id+'-config.json');q.save(config,dict(inputs=refs,plan=p,assetIndex=index,assetDirectory=q.relative(images)))
    spec=dict(version=q.SPEC_VERSION,id=id,task='FOCUS343',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
        hypothesis='Identical artwork removes content identity as a cue for neighboring focus movement.',
        decisionRule='Compare pinned models at 0.15/0.85. Report lost successes and unsupported native conclusions.',
        adapter=dict(type='python-callable',steps=['neighbors343.run'],outputAttributes=['neighbors343.OUT']),
        inputs=refs,stage=[{'from':pin(config),'to':'config.json'}],limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    path=folder/(id+'.json');q.save(path,spec);print(q.submit(path))


if __name__=='__main__':
    import sys
    register(int(sys.argv[1]))
