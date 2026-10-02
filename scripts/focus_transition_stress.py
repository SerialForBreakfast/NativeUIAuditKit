"""Fixed generated pixel stress experiment; software evidence, not app accuracy."""
import argparse
from PIL import Image,ImageDraw
import human_annotation_review as h
import focus_recorded_transition_eval as evaluator


def scene(dx=0,dy=0,scale=1,shade=80):
    im=Image.new('RGB',(640,480),(25,)*3);d=ImageDraw.Draw(im)
    x,y=200+dx,200+dy;w,ht=int(160*scale),int(60*scale)
    d.rectangle((x-(w-160)//2,y-(ht-60)//2,x+(w+160)//2-1,y+(ht+60)//2-1),fill=(shade,)*3)
    d.text((x+22,y+25),'Settings unique 129',fill=(240 if shade<128 else 15,)*3)
    return im


def run(output):
    output=h.fresh(output);output.mkdir(parents=True)
    a=scene();duplicate=scene();duplicate.paste(a.crop((200,200,360,260)),(200,100))
    illumination=a.point(lambda p:min(255,p+30))
    # Ground truth names the controlled generated visual manipulation, not focus truth.
    cases=[('unchanged',a,a,'unchanged'),('highlight',a,scene(shade=235),'arrival'),
           ('dim',scene(shade=235),a,'departure'),('scroll-highlight',a,scene(dy=-100,shade=235),'arrival'),
           ('growth',a,scene(scale=1.15),'arrival'),('scroll-only',a,scene(dy=-100),'unchanged'),
           ('duplicate',a,duplicate,'unavailable'),('missing',a,Image.new('RGB',a.size,(25,)*3),'unavailable'),
           ('illumination',a,illumination,'unknown')]
    results=[]
    for name,before,after,expected in cases:
        refs=[]
        for side,im in [('before',before),('after',after)]:
            path=output/(name+'-'+side+'.png');im.save(path);refs.append(h.ref(path))
        predictions,runtime=evaluator.predict(*refs,[dict(id='row',bounds=[200,200,160,60])])
        p=predictions[0];results.append(dict(name=name,expected=expected,observed=p['decision'],
            passed=p['decision']==expected,inputs=refs,prediction=p,runtime=runtime))
    report=dict(version='focus-transition-stress-v1',**h.FLAGS,generatedSoftwareFixture=True,
                cases=results,passed=sum(r['passed'] for r in results),total=len(results),
                implementation=[h.ref(h.ROOT/'scripts'/s) for s in
                    ('focus_transition_stress.py','focus_recorded_transition_eval.py','focus_transition_verifier.py')])
    h.write(output/'results.json',report,sealed=True)
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    a=p.parse_args();r=run(a.output);print(f"{r['passed']}/{r['total']} fixed generated cases")
