"""Replay fixed full-scene predictions and compare like-for-like results."""
import argparse
from collections import defaultdict
from pathlib import Path
import human_annotation_review as h
from fullscreen_readthrough import score_boxes


def analyze(evaluation,output):
    path=h.local(evaluation);doc=h.read(path);base=h.ROOT/'reports/work/FULLSCREEN-EXPERIMENT-41'
    contract=h.read(base/'run.json');members=[f for f in contract['frames'] if f['split']=='evaluation']
    h.require([r['id'] for r in doc['frames']]==[f['id'] for f in members],'evaluation_membership_changed')
    groups=defaultdict(lambda:dict(frames=0,tp=0,fp=0,fn=0,exact=0));misses=[]
    totals=dict(tp=0,fp=0,fn=0);exact=0
    for frame,row in zip(members,doc['frames']):
        ann=h.read(h.checked(h.ROOT,frame['annotation']))
        focused=[c for c in ann['controls'] if c['state']=='focused']
        targets=[[x,y,x+w,y+v] for x,y,w,v in [c['bounds'] for c in focused]]
        score=score_boxes(row['predictedBounds'],targets)
        h.require(score=={k:row[k] for k in ('tp','fp','fn')},'stored_metric_mismatch')
        for key,value in score.items():totals[key]+=value
        exact+=score['fp']==0 and score['fn']==0
        for key in (frame['group'],'endpoint-'+frame['id'].rsplit('-',1)[-1],
                    'focused-'+focused[0]['id']):
            group=groups[key];group['frames']+=1
            for k,v in score.items():group[k]+=v
            group['exact']+=score['fp']==0 and score['fn']==0
        if score['fn'] or score['fp']:misses.append(dict(id=frame['id'],group=frame['group'],
            target=focused[0]['id'],**score,image=frame['image'],annotation=frame['annotation']))
    h.require(totals==doc['totals'] and exact==doc['exactFrames'],'stored_summary_mismatch')
    result=dict(evaluation=h.ref(path),contract=h.ref(base/'run.json'),groups=dict(groups),failures=misses,
        exactFrames=doc['exactFrames'],totalFrames=len(members),totals=doc['totals'],
        interpretation='Previously exposed synthetic configurations; no real-app or independent-test claim.')
    h.write(h.local(output),result);print(result['groups'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('evaluation');p.add_argument('output');a=p.parse_args();analyze(a.evaluation,a.output)
