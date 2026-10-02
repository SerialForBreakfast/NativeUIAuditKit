"""Generated stress and actual CLI contract checks for the optional paired verifier."""
import argparse
import copy
import os
import subprocess
import sys

import numpy as np
from PIL import Image,ImageDraw
import human_annotation_review as h
from test_focus_transition_verifier import scene


def run(output,common=False):
    out=h.fresh(output);out.mkdir(parents=True)
    a=scene();duplicate=scene()
    d=ImageDraw.Draw(duplicate);d.rectangle((200,100,359,159),fill=(80,)*3)
    d.text((222,125),'Settings unique 129',fill=(240,)*3)
    illumination=Image.fromarray(np.minimum(np.asarray(a,dtype=int)+40,255).astype('uint8'))
    replacement=scene();d=ImageDraw.Draw(replacement)
    d.rectangle((200,200,359,259),fill=(180,20,20));d.text((222,225),'Completely different',fill='white')
    pairs=[('unchanged',a,a,'unchanged'),('translate',a,scene(dy=-100),'unchanged'),
           ('grow',a,scene(scale=1.15),'arrival'),('scroll-highlight',a,scene(dy=-100,shade=235),'arrival'),
           ('translate-grow',a,scene(dx=10,dy=-100,scale=1.15),'arrival'),
           ('duplicate',a,duplicate,'unchanged'),('disappear',a,Image.new('RGB',a.size,(25,)*3),'unknown'),
           ('illumination',a,illumination,'unchanged'),('content-replacement',a,replacement,'unchanged'),
           # Same pixels as highlight, but source semantics say only content color changed.
           ('lookalike-content',a,scene(shade=235),'unchanged'),
           ('viewport',a,Image.new('RGB',(640,400)),'unknown')]
    records=[]
    def cli(req,name,enabled=True,expect_failure=False):
        path=out/(name+'-request.json');h.write(path,req);dest=out/(name+'-result.json')
        cmd=[sys.executable,str(h.ROOT/'scripts/focus_transition_verifier.py'),'--request',str(path),'--output',str(dest)]
        if enabled:cmd.append('--enable-experimental')
        if common:cmd.append('--common-support')
        p=subprocess.run(cmd,cwd=h.ROOT,env=os.environ.copy(),capture_output=True,text=True,timeout=120)
        if expect_failure:
            h.require(p.returncode!=0 and not dest.exists(),'invalid_request_accepted')
            return dict(name=name,exitCode=p.returncode,error=p.stderr.splitlines()[-1])
        h.require(p.returncode==0,'verify_cli_failed:'+name+':'+p.stderr[-300:])
        result=h.read(dest);h.require(result['controlIssued'] is False and result['releaseEligible'] is False,'unsafe_output')
        return dict(name=name,exitCode=0,result=result)
    for name,before,after,truth in pairs:
        bf=out/(name+'-before.png');af=out/(name+'-after.png');before.save(bf);after.save(af)
        req=dict(version=1,before=h.ref(bf),after=h.ref(af),beforeBounds=[200,200,160,60],
                 context=dict(sameScene=True,settled=True,fresh=True,identityVerified=True))
        record=cli(req,name);record['truth']=truth
        prediction=record['result']['decision']
        record['outcome']='abstained' if prediction in ('unknown','unavailable') else 'correct' if prediction==truth else 'wrong'
        records.append(record)
    base=copy.deepcopy(req);base['after']=base['before']
    boundaries=[cli({},'disabled',enabled=False)]
    for name in ('sameScene','settled','fresh','identityVerified'):
        req=copy.deepcopy(base);req['context'][name]=False
        record=cli(req,'false-'+name);h.require(record['result']['status']=='unavailable','context_gate_failed');boundaries.append(record)
    for name in ('missing-context','string-boolean','wrong-hash','bad-bounds','version'):
        req=copy.deepcopy(base)
        if name=='missing-context':req.pop('context')
        elif name=='string-boolean':req['context']['fresh']='yes'
        elif name=='wrong-hash':req['before']['sha256']='0'*64
        elif name=='bad-bounds':req['beforeBounds'][2]=-1
        else:req['version']=2
        boundaries.append(cli(req,name,expect_failure=True))
    h.write(out/'audit.json',dict(stress=records,contracts=boundaries,
        statement='Generated software/adversarial cases, not added training or independent TV evaluation.'))
    for r in records:print(r['name'],r['result']['decision'],r['outcome'],flush=True)
    print('CLI contract checks',len(boundaries),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    p.add_argument('--common-support',action='store_true')
    args=p.parse_args();run(args.output,args.common_support)
