"""Retained-prediction diagnosis, without changing labels or operating thresholds."""
import argparse
from collections import Counter, defaultdict
import human_annotation_review as h
from real_fullscreen42 import xywh


def intersection(a, b):
    x,y,w,v=a;xx,yy,ww,vv=b
    return max(0,min(x+w,xx+ww)-max(x,xx))*max(0,min(y+v,yy+vv)-max(y,yy))


def associations(controls, predictions):
    """Containment diagnostic, not an alternative accuracy score or annotation."""
    assigned=defaultdict(list)
    for p in predictions:
        box=xywh(p);area=box[2]*box[3]
        hits=[c for c in controls if intersection(box,c['bounds'])/area>=.8]
        if len(hits)==1:assigned[hits[0]['id']].append(p)
    values={c['id']:max((p['score'] for p in assigned[c['id']]),default=0.) for c in controls}
    focused=next(c for c in controls if c['state']=='focused')
    negative=max((values[c['id']] for c in controls if c['state']=='unfocused'),default=0.)
    return dict(focusedContainedScore=values[focused['id']],unfocusedContainedScore=negative,
                focusAboveOperating=values[focused['id']]>=.25,
                unfocusedOutranksFocus=negative>values[focused['id']],
                anyContainedFocus=values[focused['id']]>0,
                perControl=values)


def run(folder, output):
    folder=h.local(folder);output=h.fresh(output)
    protocol=h.read(folder/'protocol.json');rows=[]
    for i,frame in enumerate(protocol['frames']):
        raw=h.read(folder/f'{i:03d}.json')
        h.require(raw['image']==frame['image'],'prediction_binding')
        rows.append(dict(index=i,family=frame['family'],image=frame['image'],
                         **associations(frame['controls'],raw['candidate'])))
    groups=defaultdict(Counter)
    for r in rows:
        g=groups[r['family']];g['frames']+=1
        for key in ('focusAboveOperating','unfocusedOutranksFocus','anyContainedFocus'):g[key]+=r[key]
    result=dict(version='reference-containment-diagnostic-v1',protocol=h.ref(folder/'protocol.json'),
                **h.FLAGS,rows=rows,summary=dict(groups),
                interpretation='A prediction with >=80% of its own area inside exactly one known body is associated with it. This diagnoses wrong-control ranking even when full-body IoU fails; it does not relabel artwork or count correct full-body detections.')
    h.write(output,result);print(result['summary'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--folder',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.folder,a.output)
