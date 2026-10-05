"""Hash-bound support audit; label geometry is not renderer identity."""
import math
from collections import Counter,defaultdict
import ios_repair165 as r
from eval_phase6a import load_names
h=r.h
OUT=h.ROOT/'reports/work/IOS-COVERAGE-169/artifacts'

def parse(text,names):
    result=[]
    for line in text.splitlines():
        if not line.strip():continue
        row=list(map(float,line.split()))
        h.require(len(row)==5 and all(math.isfinite(x) for x in row),'invalid_label')
        c,x,y,w,ht=row
        h.require(c.is_integer() and 0<=c<names and 0<w<=1 and 0<ht<=1 and
            0<=x<=1 and 0<=y<=1 and x-w/2>=-1e-6 and x+w/2<=1+1e-6 and
            y-ht/2>=-1e-6 and y+ht/2<=1+1e-6,'invalid_box')
        result.append(row)
    return result

def summary(rows):
    return dict(count=len(rows),horizontalThirds=dict(Counter(
        'left' if x[1]<1/3 else 'right' if x[1]>=2/3 else 'middle' for x in rows)),
        ranges={key:[min(x[i] for x in rows),max(x[i] for x in rows)] if rows else None
                for i,key in enumerate(('class','cx','cy','width','height')) if i})

def run():
    manifest=r.repair.BASE/'overlay/manifest.json'
    h.require(h.sha(manifest)==r.OVERLAY_SHA,'overlay_changed')
    doc=h.read(manifest,64*1024**2);names=load_names();cid=names.index('pageControl')
    selected=[x for x in doc['rows'] if x['split']=='train']
    h.require(len(selected)==14540 and len({x['id'] for x in selected})==14540,'training_membership')
    h.require(not OUT.exists(),'output_collision')
    rows=[];groups=defaultdict(list);classes=Counter();empty=0
    for entry in selected:
        label=h.checked(h.ROOT,entry['label'])
        labels=parse(label.read_text(),len(names));empty+=not labels
        classes.update(names[int(x[0])] for x in labels)
        page=[x for x in labels if x[0]==cid]
        if page:
            rows.append(dict(id=entry['id'],family=entry['family'],replaced=entry['replaced'],
                label=entry['label'],boxes=page))
            groups[entry['family']].extend(page)
    probe=r.repair.PROBES/'page156-manifest.json'
    from prediction_artifact import load_request
    request=load_request(probe,len(names));probe_boxes=[]
    for image in request.images:probe_boxes.extend(x for x in parse(image.label_path.read_text(),len(names)) if x[0]==cid)
    OUT.mkdir(parents=True)
    h.write(OUT/'audit.json',dict(source=h.ref(__file__),manifest=h.ref(manifest),probe=h.ref(probe),
        trainingMembers=len(selected),emptyMembers=empty,classInstances=dict(classes),
        pageMembers=len(rows),pageBoxes=summary([b for row in rows for b in row['boxes']]),
        families={k:summary(v) for k,v in groups.items()},probeBoxes=summary(probe_boxes),
        members=rows,rendererIdentity='not inferred from family; requires source review',
        independentEvaluation=False),sealed=True)
    print('training',len(selected),'page members',len(rows),'families',{k:summary(v) for k,v in groups.items()},flush=True)

if __name__=='__main__':run()
