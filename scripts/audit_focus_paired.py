"""Reproducible paired11 diagnostics, isolated clipped-context follow-up and CLI audit."""
import argparse
from collections import Counter,defaultdict
import copy
import os
import subprocess
import sys
import numpy as np
from PIL import Image,ImageDraw
import human_annotation_review as h
import focus_paired_growth as g

ROOT=h.ROOT/'reports/work/FOCUS-PAIRED-11/artifacts'


def rectangle(size=194,shade=240,offset=0):
    im=Image.new('RGB',(256,256),(40,40,40));x=(256-size)//2+offset
    ImageDraw.Draw(im).rectangle((x,x,x+size-1,x+size-1),fill=(shade,)*3)
    return im


def run(output):
    out=h.fresh(output);out.mkdir(parents=True)
    invpath=ROOT/'inventory/inventory.json';renderpath=ROOT/'rendered/receipt.json'
    inv=g.read_inventory(invpath);result=h.read(ROOT/'evaluation-final/result.json',limit=16*1024**2)
    render=h.read(renderpath);rows=copy.deepcopy(result['decisions']);summaries=defaultdict(Counter)
    cache={}
    def image(c,role):
        key=g.crop_key(inv['geometry'][c[role]],c['anchor'])
        if key not in cache:
            with Image.open(h.checked(h.ROOT,render['crops'][key])) as im:cache[key]=im.convert('RGB')
        return cache[key]
    for c in rows:
        a,b=image(c,'before'),image(c,'after')
        # Predeclared follow-up changes brightness availability only, not edge eligibility.
        raw=g.predict(a,b,settled=True,matched=True,stable_context=True,fresh=True)
        bright=raw['brightness'];growth=c['arms']['growth']
        signals={p for p in (bright,growth) if p not in ('unknown','unavailable')}
        combined=next(iter(signals)) if len(signals)==1 else 'unknown'
        c['arms']['brightness-clipping-followup']=bright
        c['arms']['combined-clipping-followup']=combined
        for arm,p in c['arms'].items():
            outcome='abstained' if p in ('unknown','unavailable') else 'correct' if p==c['truth'] else 'wrong'
            summaries['/'.join([c['lane'],c['group'][1],c['kind'],c['truth'],arm])][outcome]+=1
    baseline=h.read(h.checked(h.ROOT,result['baseline']),limit=32*1024**2)
    selected=next(s for s in baseline['history'] if s['update']==baseline['selectedUpdate'])
    frames=g.frame_analysis(rows,inv,selected['validation']['real']['metrics']['completeFrameSelection']['frames'])
    stress=[]
    cases=[('growth',rectangle(),rectangle(222),'arrival'),
           ('shift',rectangle(),rectangle(offset=15),'unchanged'),
           ('content-replacement',rectangle(shade=80),rectangle(shade=240),'unchanged'),
           ('illumination',rectangle(shade=80),Image.fromarray(np.minimum(np.array(rectangle(shade=80),dtype=int)+40,255).astype('uint8')),'unchanged')]
    for name,a,b,t in cases:
        raw=g.predict(a,b,settled=True,matched=True,stable_context=True,fresh=True)
        gated=g.predict(a,b,settled=True,matched=True,stable_context=name=='growth',fresh=True)
        stress.append(dict(case=name,truth=t,raw=raw,externalContextGate=gated))
    # Examples: three distinct home pairs, one tab, one Settings row, native opposite brightness.
    choices=[];seen=set()
    for c in rows:
        if c['kind']!='forward' or c['truth']!='arrival':continue
        family=c['group'][1]
        qualifies=(c['lane']=='real-development-contrast' and family in ('home','settings','app-store-tabs')) or (c['lane']=='native-training-contrast' and c['arms']['brightness']=='departure')
        if qualifies and family not in seen:choices.append(c);seen.add(family)
    for i,c in enumerate(choices):
        panel=Image.new('RGB',(1024,300),'#202020');draw=ImageDraw.Draw(panel)
        ims=[image(c,'before'),image(c,'after')]
        for role in ('before','after'):
            with Image.open(h.checked(h.ROOT,inv['samples'][c[role]]['crop'])) as im:ims.append(im.convert('RGB'))
        for j,im in enumerate(ims):panel.paste(im,(j*256,35))
        draw.text((5,4),'Fixed before / fixed after / normalized before / normalized after',fill='white')
        draw.text((5,18),str(c['group'][1])+' truth='+c['truth']+' growth='+c['arms']['growth'],fill='white')
        panel.save(out/f'example-{i+1}.png')
    # Real CLI tamper tests: verify rejection at caller, no render/model work.
    negatives=[]
    for name in ('seal','policy','label','geometry','context','duplicate','anchor'):
        bad=copy.deepcopy(inv)
        if name in ('seal','policy'):bad['policy']['growth']=1.01
        elif name=='label':bad['samples'][next(iter(bad['samples']))]['label']^=1
        elif name=='geometry':bad['geometry'][next(iter(bad['geometry']))]['bounds'][2]+=1
        elif name=='context':bad['samples'][next(iter(bad['samples']))]['control']='wrong'
        elif name=='duplicate':bad['cases'].append(copy.deepcopy(bad['cases'][0]))
        elif name=='anchor':bad['cases'][0]['anchor'][2]+=1
        if name!='seal':bad.pop('protocolSHA256');bad['protocolSHA256']=h.digest(bad)
        path=out/f'{name}.json';h.write(path,bad)
        cmd=[sys.executable,str(h.ROOT/'scripts/focus_paired_growth.py'),'evaluate','--inventory',str(path),'--rendered',str(renderpath),'--output',str(out/f'unexpected-{name}')]
        p=subprocess.run(cmd,cwd=h.ROOT,env=os.environ.copy(),capture_output=True,text=True,timeout=30)
        h.require(p.returncode!=0 and not (out/f'unexpected-{name}').exists(),'negative_cli_accepted')
        negatives.append(dict(case=name,returncode=p.returncode,error=p.stderr.splitlines()[-1]))
    h.write(out/'audit.json',dict(inventory=h.ref(invpath),primary=h.ref(ROOT/'evaluation-final/result.json'),
        amendment=h.ref(h.ROOT/'Research/Plans/FocusPaired11Clipping.md'),summary=dict(summaries),
        frameComparisons=frames,decisions=rows,stress=stress,negativeCLI=negatives,
        warning='External context gate supplied, not visually detected. Descriptive contrasts, not independent action trials.'))
    print('stress',[(r['case'],r['raw']['combined']) for r in stress])
    for eligible in (True,False):
        for arm in frames[0]['outcomes']:
            print('frame eligible',eligible,arm,dict(Counter(r['outcomes'][arm] for r in frames if r['eligible']==eligible)))
    print('negative CLI',len(negatives))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    run(p.parse_args().output)
