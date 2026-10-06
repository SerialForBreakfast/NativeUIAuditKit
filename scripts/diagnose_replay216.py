"""Size-stratified retained213 errors; no inference or label/threshold changes."""
from collections import defaultdict
from pathlib import Path
import argparse
import evaluate_artwork213 as review
from artwork200_campaign import sha, write
from shared_transfer import require

ROOT=review.ROOT
BASE=ROOT/'reports/work/WORKER-213/artifacts'
REPORT=BASE/'paired01.json'
PIN='64c7d5a4bcfc9e86fd33fb11a7970d6fe4b173b1603363ec695a97ac04bf860a'


def operating_matches(truths,predictions,confidence=.25,threshold=.5):
    """Diagnostic association; every total must reconcile to unchanged scorer."""
    matched=set();false_positives=[]
    for index,(score,box) in sorted(enumerate(predictions),key=lambda item:-item[1][0]):
        if score<confidence:continue
        choices=[(review.evaluation.iou_xyxy(box,g),j) for j,g in enumerate(truths) if j not in matched]
        overlap,j=max(choices,default=(0,-1))
        if overlap>=threshold:matched.add(j)
        else:false_positives.append(index)
    return matched,false_positives


def size_bin(box,width,height):
    side=min(box[2]-box[0],box[3]-box[1])*640/max(width,height)
    return 'lt16' if side<16 else '16to32' if side<32 else '32to64' if side<64 else 'ge64'


def compare_cases(request,control,treatment,names):
    rows={arm:{r['imageID']:r for r in doc['results']} for arm,doc in [('control',control),('treatment',treatment)]}
    expected={im.image_id for im in request.images}
    require(all(set(index)==expected for index in rows.values()),'case_membership')
    bins={};totals={arm:[dict(tp=0,fp=0,fn=0) for _ in names] for arm in rows}
    for image in request.images:
        truths=defaultdict(list)
        for line in image.label_path.read_text().splitlines():
            if not line.strip():continue
            c,x,y,w,h=map(float,line.split())
            truths[int(c)].append(((x-w/2)*image.width,(y-h/2)*image.height,
                                  (x+w/2)*image.width,(y+h/2)*image.height))
        for c,name in enumerate(names):
            matches={}
            for arm in rows:
                predictions=[(d['score'],d['xyxyPixels']) for d in rows[arm][image.image_id]['detections'] if d['classID']==c]
                matched,fp=operating_matches(truths[c],predictions)
                matches[arm]=matched
                totals[arm][c]['tp']+=len(matched);totals[arm][c]['fp']+=len(fp)
                totals[arm][c]['fn']+=len(truths[c])-len(matched)
            for j,box in enumerate(truths[c]):
                size=size_bin(box,image.width,image.height);key=(name,size)
                row=bins.setdefault(key,dict(className=name,size=size,support=0,controlTP=0,treatmentTP=0,
                                             gained=0,lost=0,lostExamples=[],gainedExamples=[]))
                a=j in matches['control'];b=j in matches['treatment']
                row['support']+=1;row['controlTP']+=a;row['treatmentTP']+=b
                if a!=b:
                    kind='gained' if b else 'lost';row[kind]+=1
                    if len(row[kind+'Examples'])<3:
                        row[kind+'Examples'].append(dict(imageID=image.image_id,classTruthIndex=j,xyxyPixels=list(box)))
    return dict(bins=[bins[k] for k in sorted(bins)],totals=totals)


def run(out):
    out=review.fresh(out);require(sha(REPORT)==PIN,'accepted_report_changed')
    accepted=review.evaluation.read(REPORT)
    requests=review.checked_requests(ROOT/'reports/work/ARTWORK-204/artifacts/evaluation213-input01')
    names=review.evaluation.load_names();documents={};rescored={}
    for arm in ('control','treatment'):
        folder=BASE/'return01/mapped-predictions'/arm
        cp=BASE/'return01/payload/checkpoints'/(arm+'-last.pt')
        rescored[arm]=review.scored(requests,folder,cp,'split')
        require(rescored[arm]['reports']==accepted[arm]['reports'],'metric_drift')
        require(rescored[arm]['predictions']==accepted[arm]['predictions'],'prediction_changed')
        documents[arm]={k:review.evaluation.read(folder/(k+'.json')) for k in rescored[arm]['reports']}
    parts={}
    for key in ('validation','diagnostic','fit','page','combined'):
        result=compare_cases(requests[key],documents['control'][key],documents['treatment'][key],names)
        for arm in ('control','treatment'):
            for counts,metric in zip(result['totals'][arm],accepted[arm]['reports'][key]['perClass']):
                require(counts=={k:metric[k] for k in counts},'case_metric_disagreement')
        result['role']='training-derived fit diagnostic' if key=='fit' else 'retained development evaluation; not final qualification'
        parts[key]=result
    ranked=sorted([dict(row,partition=key) for key,result in parts.items() for row in result['bins'] if row['lost']],
                  key=lambda r:(-r['lost'],r['partition'],r['className'],r['size']))[:10]
    report=dict(sourceReportSHA256=PIN,sourceSHA256=sha(Path(__file__)),partitions=parts,topLostGroups=ranked,
                sizeDefinition='Minimum GT side after640letterbox; <16,16–32,32–64,>=64; not COCO bins',
                confidence=.25,iou=.5,causalEvidence=False,modelGatePassed=False,
                scope='Raw ROI and native artwork diagnostics, not composed fullframe or tvOS focus quality')
    write(out,report)
    return [(r['partition'],r['className'],r['size'],r['lost'],r['gained'],r['support']) for r in ranked]


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('out',type=Path)
    print(run(parser.parse_args().out))
