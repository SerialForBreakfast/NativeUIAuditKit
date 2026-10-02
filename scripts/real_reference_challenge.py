"""Frozen, explicitly scoped historical challenge; never a live advisory gate."""
import argparse
import math
import os
import time
from PIL import Image
import human_annotation_review as h
import native_focus_transfer as t
import native_focus_spike as n
import focus_runtime as runtime

REVIEW=h.ROOT/'reports/work/ACCESSIBILITY-TRACKING-30/home-reference-review/review.json'
SEAL='bc3be3a8780f9b3b784dc7423ca9957058557578f398fdf80ec8100e4075eeb2'


def summarize(values):
    h.require(len(values)==2 and all(type(v) in (int,float) and math.isfinite(v)
                                    and 0<=v<=1 for v in values),'invalid_scores')
    a,b=values
    return dict(unfocusedScore=a,focusedScore=b,ordered=b>a,
                correctAt05=int(a<.5)+int(b>=.5),
                correctAt085=int(a<.85)+int(b>=.85),
                advisoryCorrect=int(a<=.15)+int(b>=.85),
                advisoryWrong=int(a>=.85)+int(b<=.15),
                advisoryUncertain=sum(.15<v<.85 for v in values))


def run(output):
    started=time.monotonic();review=h.sealed(REVIEW,'real-reference-review-v1')
    h.require(review['seal']==SEAL and [p['id'] for p in review['pairs']]==['photos','music'],
              'unapproved_membership')
    request=h.read(t.checked(review['request']));t.checked(review['implementation'])
    readiness=h.read(t.checked(request['readiness']))
    for ref in readiness['inputs'].values():t.checked(ref)
    identity=runtime.identity();h.require(identity==review['runtime'],'runtime_changed')
    images=[]
    for pair in review['pairs']:
        for frame,ref in zip(pair['frames'],pair['crops']):
            path=t.checked(frame['image']);saved=Image.open(t.checked(ref)).convert('RGB')
            im=t.crop(dict(id='parity',path=str(path),sha256=frame['image']['sha256'],
                           bounds=n.common_window(pair['frames'][0]['target']['bounds'])),h.ROOT)
            h.require(im.size==saved.size and im.tobytes()==saved.tobytes(),'crop_pixel_mismatch')
            images.append(im)
    out=h.fresh(output);out.mkdir(parents=True)
    h.write(out/'started.json',dict(pid=os.getpid(),review=h.ref(REVIEW),
        authority='User approved next tranche: two Home pairs as difficult-case development diagnostic',
        maximumSeconds=300,maximumOutputBytes=256*1024*1024))
    scorer=t.Scorer();scores=scorer.score(images)
    h.require(len(scores)==4 and time.monotonic()-started<300,'execution_budget_or_membership')
    h.require(runtime.identity()==identity,'runtime_changed')
    rows=[dict(id=p['id'],cleanContext=p['cleanContext'],**summarize(scores[i*2:i*2+2]))
          for i,p in enumerate(review['pairs'])]
    result=dict(version='real-reference-challenge-v1',**h.FLAGS,pid=os.getpid(),
        seconds=time.monotonic()-started,review=h.ref(REVIEW),implementation=h.ref(__file__),
        model=scorer.identity,runtime=identity,cropPixelParity=True,pairs=rows,
        qualification='Two related historical Home pairs; changing-neighbor contamination; development diagnostic only')
    h.write(out/'result.json',result,sealed=True)
    lines=['# Frozen FDR036 Home challenge','',result['qualification'],'',
           '| Item | Unfocused score | Focused score | Correct at0.85 | Advisory correct/wrong/uncertain |',
           '| --- | --- | --- | --- | --- |']
    for r in rows:
        lines.append(f"| {r['id']} | {r['unfocusedScore']:.6f} | {r['focusedScore']:.6f} | {r['correctAt085']}/2 | {r['advisoryCorrect']}/{r['advisoryWrong']}/{r['advisoryUncertain']} |")
    (out/'result.md').write_text('\n'.join(lines)+'\n')
    print(result,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    run(p.parse_args().output)
