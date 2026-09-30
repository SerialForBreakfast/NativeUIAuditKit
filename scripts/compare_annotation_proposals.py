"""Frozen development-only comparison of raster proposals and Apple Vision."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

from PIL import Image, ImageDraw
from human_annotation_review import read_revision
from human_auto_boxes import detect
from focus_dataset_contract import ROOT, local, member
from perception_benchmark import _iou


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def match(proposals, truth, threshold):
    """Maximum-cardinality one-to-one matching; confidence-independent geometry."""
    owners={}
    def assign(p,seen):
        candidates=sorted(range(len(truth)),key=lambda t:(-_iou(proposals[p],truth[t]),t))
        for t in candidates:
            if t in seen or _iou(proposals[p],truth[t])<threshold: continue
            seen.add(t)
            if t not in owners or assign(owners[t],seen): owners[t]=p; return True
        return False
    for p in range(len(proposals)): assign(p,set())
    return {'matches':len(owners),'reviewed':len(truth),'proposals':len(proposals),
            'missedReviewed':len(truth)-len(owners),'unmatchedProposals':len(proposals)-len(owners),
            'assignments':[{'reviewedIndex':t,'proposalIndex':p,'iou':_iou(proposals[p],truth[t])}
                           for t,p in sorted(owners.items())]}


def validate_boxes(boxes, width, height):
    from math import isfinite
    for box in boxes:
        if (not isinstance(box,list) or len(box)!=4 or
            any(type(v) not in (int,float) or not isfinite(v) for v in box)):
            raise ValueError('invalid_proposal')
        x,y,w,h=box
        if x<-.01 or y<-.01 or w<=0 or h<=0 or x+w>width+.01 or y+h>height+.01:
            raise ValueError('proposal_outside_frame')


def overlay(image, boxes, title, color):
    image=image.convert('RGB'); original=image.size; image.thumbnail((640,360))
    panel=Image.new('RGB',(640,392),'#202020'); panel.paste(image,(0,32))
    draw=ImageDraw.Draw(panel); draw.text((8,10),title,fill='white')
    sx,sy=image.width/original[0],image.height/original[1]
    for i,(x,y,w,h) in enumerate(boxes,1):
        draw.rectangle((x*sx,y*sy+32,(x+w)*sx,(y+h)*sy+32),outline=color,width=2)
        draw.text((x*sx+2,y*sy+34),str(i),fill=color)
    return panel


def run(revision_path, output, tool, reuse_run=None):
    revision_path,output,tool=map(local,(revision_path,output,tool))
    if output.exists(): raise ValueError('output_collision')
    doc=read_revision(revision_path)
    if doc.get('partition')!='development': raise ValueError('development_only')
    frames=doc['frames']
    if not frames or len(frames)>40 or len({f['id'] for f in frames})!=len(frames):
        raise ValueError('invalid_frame_membership')
    refs=[{'path':str(revision_path.relative_to(ROOT)),'sha256':sha(revision_path)}]
    refs+=doc['editorSnapshots']+[doc['batch']]
    requests=[]
    for frame in frames:
        if frame['disposition']!='reviewed' or any(c['disposition']!='reviewed' for c in frame['controls']):
            raise ValueError('unreviewed_input')
        ref=frame['image']; path=member(ROOT,ref['path'])
        with Image.open(path) as image:
            image.load(); validate_boxes([c['bounds'] for c in frame['controls']],*image.size)
        refs.append(ref)
        requests.append({'id':frame['id'],'path':str(path),'sha256':ref['sha256']})
    for ref in refs:
        if sha(member(ROOT,ref['path']))!=ref['sha256']: raise ValueError('changed_input')
    output.mkdir(parents=True)
    source_names=['scripts/vision_annotation_probe.swift','scripts/human_auto_boxes.py',
                  'scripts/compare_annotation_proposals.py','scripts/perception_benchmark.py']
    protocol={'version':1,'inputs':refs,'frames':requests,'completeFrameCandidates':doc.get('completeFrameCandidates'),
              'sources':{n:sha(ROOT/n) for n in source_names},'binarySHA256':sha(tool),
              'visionSettings':{'minimumSize':.01,'minimumAspectRatio':.05,'maximumAspectRatio':1,
                                'minimumConfidence':.5,'quadratureTolerance':15,'maximumObservations':40},
              'ocrSettings':{'level':'accurate','languages':['en-US'],'languageCorrection':False},
              'comparisonIoUs':[.5,.75],'trainingEligible':False,'independentEvaluationEligible':False}
    if reuse_run:
        reuse_run=local(reuse_run); prior=json.loads((reuse_run/'protocol.json').read_text())
        for key in ('inputs','frames','binarySHA256','visionSettings','ocrSettings'):
            if prior[key]!=protocol[key]: raise ValueError('incompatible_cached_vision')
        if prior['sources']['scripts/vision_annotation_probe.swift']!=protocol['sources']['scripts/vision_annotation_probe.swift']:
            raise ValueError('changed_vision_source')
        protocol['reusedVision']={'path':str((reuse_run/'vision.stdout').relative_to(ROOT)),
                                  'sha256':sha(reuse_run/'vision.stdout')}
    (output/'protocol.json').write_text(json.dumps(protocol,indent=2))
    if reuse_run:
        raw_text=(reuse_run/'vision.stdout').read_text()
        (output/'vision.stdout').write_text(raw_text)
    else:
        raw=subprocess.run([str(tool)],input=json.dumps({'version':1,'root':str(ROOT),'frames':requests}),
                           text=True,capture_output=True,timeout=240)
        raw_text=raw.stdout
        (output/'vision.stdout').write_text(raw.stdout);(output/'vision.stderr').write_text(raw.stderr)
        if raw.returncode: raise ValueError(f'vision_failed_exit_{raw.returncode}')
    native=json.loads(raw_text)
    if native.get('version')!=1 or [r['id'] for r in native['results']]!=[f['id'] for f in frames]:
        raise ValueError('vision_membership_mismatch')
    reports=[]
    for frame,v in zip(frames,native['results']):
        if v['sha256']!=frame['image']['sha256'] or v['errors']: raise ValueError('vision_frame_failure')
        with Image.open(member(ROOT,frame['image']['path'])) as image:
            if image.size!=(v['width'],v['height']): raise ValueError('vision_dimensions')
            start=time.perf_counter(); corners=detect(image); elapsed=time.perf_counter()-start
            heuristic=[[x,y,r-x,b-y] for (x,y),(r,b) in corners]
            vision=[]; rejected=[]
            for index, candidate in enumerate(v['rectangles']):
                try: validate_boxes([candidate['bounds']],*image.size)
                except ValueError as error:
                    rejected.append({'index':index,'bounds':candidate['bounds'],'reason':str(error)})
                else: vision.append(candidate['bounds'])
            truth=[c['bounds'] for c in frame['controls']]
            ocr=[r['bounds'] for r in v['text']]
            for boxes in (heuristic,vision,ocr):validate_boxes(boxes,*image.size)
            report={'id':frame['id'],'screen':frame['screen'],'image':frame['image'],'heuristic':heuristic,
                    'vision':vision,'visionRejected':rejected,'visionRawCount':len(v['rectangles']),
                    'ocrRegions':len(ocr),'seconds':{'heuristic':elapsed,
                    'visionRectangles':v['rectangleSeconds'],'visionOCR':v['ocrSeconds']},
                    'metrics':{name:{str(cutoff):match(boxes,truth,cutoff) for cutoff in (.5,.75)}
                               for name,boxes in (('heuristic',heuristic),('vision',vision))}}
            reports.append(report)
            sheet=Image.new('RGB',(1920,392))
            for index,(name,boxes,color) in enumerate((('Reviewed',truth,'#ffff00'),
                    ('Current heuristic',heuristic,'#00d8ae'),('Vision rectangles',vision,'#ff7f50'))):
                sheet.paste(overlay(image,boxes,f"{frame['id']} | {name}: {len(boxes)}",color),(index*640,0))
            sheet.save(output/(frame['id']+'-comparison.png'))
            overlay(image,ocr,f"{frame['id']} | OCR text regions: {len(ocr)}",'#00ccff').save(output/(frame['id']+'-ocr.png'))
    totals={}
    for name in ('heuristic','vision'):
        totals[name]={}
        for cutoff in ('.5','.75'):
            key=str(float(cutoff))
            totals[name][key]={k:sum(r['metrics'][name][key][k] for r in reports)
                              for k in ('matches','reviewed','proposals','missedReviewed','unmatchedProposals')}
    for ref in refs:
        if sha(member(ROOT,ref['path']))!=ref['sha256']:raise ValueError('input_changed_during_run')
    if sha(tool)!=protocol['binarySHA256'] or any(sha(ROOT/n)!=h for n,h in protocol['sources'].items()):
        raise ValueError('implementation_changed_during_run')
    result={'version':1,'os':native['os'],'frames':reports,'totals':totals,
            'inputHashesPreserved':True,'scope':'development geometry assistance; no semantic/focus accuracy claim'}
    (output/'comparison.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(totals))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--revision',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--tool',type=Path,required=True);p.add_argument('--reuse-run',type=Path);a=p.parse_args()
    run(a.revision,a.output,a.tool,a.reuse_run)
