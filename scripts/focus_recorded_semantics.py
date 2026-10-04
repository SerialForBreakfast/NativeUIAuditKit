"""Advisory source-bound native OCR for retrospective Settings correspondence."""
import argparse
import json
import subprocess
import unicodedata
from collections import Counter
from pathlib import Path
import human_annotation_review as h
import focus_recorded_readiness as readiness

PROBE=h.ROOT/'.build/debug-output/vision-annotation/probe'
POLICY=dict(minConfidence=.7,leftLabelFraction=.65,titleMaxY=.16,maxFrames=16)


def normalize(text):
    return ' '.join(''.join(c if c.isalnum() else ' ' for c in unicodedata.normalize('NFKC',text).casefold()).split())


def describe(frame,ocr):
    h.require(not ocr['errors'],'ocr_errors')
    h.require(ocr['sha256']==frame['image']['sha256'],'ocr_image_binding')
    W,H=ocr['width'],ocr['height'];tokens=ocr['text']
    title=[t for t in tokens if t['confidence']>=POLICY['minConfidence'] and
           t['bounds'][1]+t['bounds'][3]<=H*POLICY['titleMaxY'] and t['bounds'][0]>W*.2]
    title.sort(key=lambda t:(t['bounds'][1],t['bounds'][0]))
    rows=[]
    for c in frame['controls']:
        x,y,w,ht=c['bounds']
        inside=[t for t in tokens if t['confidence']>=POLICY['minConfidence'] and
            x<=t['bounds'][0]+t['bounds'][2]/2<=x+POLICY['leftLabelFraction']*w and
            y<=t['bounds'][1]+t['bounds'][3]/2<=y+ht]
        inside.sort(key=lambda t:(t['bounds'][1],t['bounds'][0]))
        label=normalize(' '.join(t['text'] or '' for t in inside))
        rows.append(dict(id=c['id'],text=label,bounds=c['bounds']))
    return dict(image=frame['image'],title=normalize(' '.join(t['text'] or '' for t in title)),rows=rows)


def correspond(before,after):
    same=bool(before['title']) and before['title']==after['title']
    counts=[Counter(r['text'] for r in f['rows']) for f in (before,after)]
    matches=[]
    for r in before['rows']:
        label=r['text']; candidates=[s for s in after['rows'] if s['text']==label]
        unique=bool(label) and counts[0][label]==counts[1][label]==1
        matches.append(dict(before=r['id'],after=candidates[0]['id'] if same and unique else None,
            text=label,reason='unique_row_text' if same and unique else 'screen_title_mismatch' if not same else 'missing_or_duplicate_row_text'))
    return dict(sameTitle=same,beforeTitle=before['title'],afterTitle=after['title'],matches=matches,
        evidence='Native OCR advisory; not persistent runtime identity or accessibility focus')


def inputs(batch,baseline,pending,revision,completeness):
    audit,truth=readiness.run_with_frames(batch,baseline,pending,revision,completeness)
    actions=[a for a in audit['actions'] if a['metadataReady'] and a['annotationsComplete']]
    hashes=sorted({e['sha256'] for a in actions for e in a['endpoints'].values()})
    h.require(0<len(hashes)<=POLICY['maxFrames'],'ocr_frame_limit')
    return audit,truth,actions,hashes


def run(batch,baseline,pending,revision,completeness,output):
    output=h.fresh(output)
    audit,truth,actions,hashes=inputs(batch,baseline,pending,revision,completeness)
    probe=h.ref(PROBE);source=h.ref(h.ROOT/'scripts/vision_annotation_probe.swift')
    frames=[dict(id=s,path=str(h.checked(h.ROOT,truth[s]['image'])),sha256=s) for s in hashes]
    output.mkdir(parents=True)
    request=dict(version=1,root=str(h.ROOT),frames=frames);h.write(output/'request.json',request)
    result=subprocess.run([str(PROBE)],input=json.dumps(request),capture_output=True,text=True,timeout=180)
    h.write(output/'execution.json',dict(returncode=result.returncode,stderr=result.stderr,probe=probe,source=source))
    h.require(result.returncode==0,'native_ocr_failed')
    raw=json.loads(result.stdout);h.write(output/'native-ocr.json',raw)
    h.require(raw['version']==1 and [r['id'] for r in raw['results']]==hashes,'ocr_membership')
    descriptions={r['id']:describe(truth[r['id']],r) for r in raw['results']}
    rows=[]
    for a in actions:
        b,f=[descriptions[a['endpoints'][k]['sha256']] for k in ('before','after')]
        rows.append(dict(actionID=a['actionID'],endpoints=a['endpoints'],**correspond(b,f)))
    for ref in list(audit['inputs'].values())+[probe,source]:h.checked(h.ROOT,ref)
    doc=dict(version='focus-recorded-semantics-v1',**h.FLAGS,inputs=audit['inputs'],policy=POLICY,
        raw=h.ref(output/'native-ocr.json'),probe=probe,probeSource=source,
        implementation=h.ref(h.ROOT/'scripts/focus_recorded_semantics.py'),descriptions=descriptions,actions=rows)
    h.write(output/'semantics.json',doc,sealed=True)
    print(json.dumps([(r['beforeTitle'],r['afterTitle'],sum(m['after'] is not None for m in r['matches'])) for r in rows]))
    return doc


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('batch','baseline','pending','revision','completeness','output'):p.add_argument('--'+k,required=True)
    a=p.parse_args();run(**vars(a))
