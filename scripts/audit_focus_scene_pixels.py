"""Whole-scene content-only counterexample through the actual pixel and scene CLIs."""
import argparse
import os
import subprocess
import sys
from PIL import Image, ImageDraw
import human_annotation_review as h


def run(output):
    out=h.fresh(output);out.mkdir(parents=True)
    images=[]
    for name,shades in [('before',(235,80)),('after',(80,235))]:
        image=Image.new('RGB',(800,600),(25,25,25));draw=ImageDraw.Draw(image)
        for i,shade in enumerate(shades):
            y=160+i*220
            draw.rectangle((200,y,519,y+99),fill=(shade,)*3)
            draw.text((230,y+40),'Settings unique 129' if i==0 else 'Network option 847',fill=(0,)*3 if shade>100 else (240,)*3)
        path=out/(name+'.png');image.save(path);images.append(h.ref(path))
    controls=[];pixel_results=[]
    def cli(script,req,name,extra):
        path=out/(name+'-request.json');dest=out/(name+'-result.json');h.write(path,req)
        p=subprocess.run([sys.executable,str(h.ROOT/'scripts'/script),'--request',str(path),'--output',str(dest),*extra],
                         capture_output=True,text=True,timeout=120,env=os.environ.copy())
        h.require(p.returncode==0,'pixel_cli:'+p.stderr[-400:]);return h.read(dest)
    for i in range(2):
        req=dict(version=1,before=images[0],after=images[1],beforeBounds=[200,160+i*220,320,100],
                 context=dict(sameScene=True,settled=True,fresh=True,identityVerified=True))
        result=cli('focus_transition_verifier.py',req,f'control-{i}',['--enable-experimental','--common-support'])
        pixel_results.append(result);controls.append(dict(id=str(i),decision=result['decision'],identityVerified=True))
    req=dict(version=1,context=dict(sameScene=True,settled=True,fresh=True,completeCoverage=True),controls=controls)
    scene=cli('focus_scene_transition.py',req,'scene',['--enable-experimental'])
    h.write(out/'audit.json',dict(images=images,pixelResults=pixel_results,sceneResult=scene,
        truth='No focus change: both controls changed their content colors only.',
        outcome='false_switch' if scene['decision']=='switch' else 'abstained',releaseEligible=False))
    print([c['decision'] for c in controls],scene['decision'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    run(p.parse_args().output)
