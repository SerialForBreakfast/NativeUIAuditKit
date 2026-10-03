"""Prepare native-family candidates and a retained-prediction failure review.

No capture, inference, data admission or training is performed.
"""
import argparse
import copy
from collections import Counter, defaultdict
import human_annotation_review as h
from reference_coverage45 import native_manifest
from harvest_sidecar_v2 import recipe_hash
from real_fullscreen42 import xywh, frame_metrics, summarize, OLD
from real_model_scorecard import iou

BASE=h.ROOT/'reports/work/FAMILY-TRANSFER-48'
PRIOR=h.ROOT/'reports/work/FOCUS-AUGMENTATION-47/comparison'


def candidates(target):
    doc=native_manifest(target)
    doc['campaign_id']='0C34D662-758A-4B30-A66A-001048000001'
    doc['title']='Native UIButton width/fill and spatial coverage candidate'
    for c in doc['cases']:c['case_id']=c['case_id'].replace('native45','native48')
    for width in (160,480,960):
        for fill in ('gray','light'):
            for background,rgb in [('dark',0x202020),('light',0xDDDDDD)]:
                recipe=copy.deepcopy(doc['cases'][0]['recipe'])
                recipe.update(element_count=3,seed=148)
                recipe['appearance']['canvas']=dict(version=2,columns=1,spacing=80,inset=120,
                    backgroundRGB=rgb,showLabels=True,pairing='competitor_v1',presentation='buttons',
                    labels=['Continue','More information','Return'],
                    nativeButton=dict(version=1,width=width,restingFill=fill))
                recipe['recipe_hash']=recipe_hash(recipe)
                doc['cases'].append(dict(case_id=f'native48-w{width}-{fill}-{background}',recipe=recipe,
                    target_element_ids=['grid_cell_0_0','grid_cell_0_1','grid_cell_1_0'],
                    split_group='validation',priority=0,independence_group='fixture_procedural_renderer_v1'))
    doc['budget'].update(max_cases=18,max_wall_clock_seconds=1800)
    return doc


def assess(frame,predictions):
    focus=[c for c in frame['controls'] if c['state']=='focused']
    h.require(len(focus)==1,'single_focus')
    result=[]
    for p in predictions:
        box=xywh(p)
        if p['score']<.25:continue
        matches=[c for c in frame['controls'] if iou(box,c['bounds'])>=.5]
        kind=('focused' if any(c['state']=='focused' for c in matches) else
              'known_unfocused' if matches else 'unmatched_complete' if frame['complete'] else 'unreviewed')
        result.append(dict(box=p['box'],score=p['score'],kind=kind))
    return dict(targetLocated=any(x['kind']=='focused' for x in result),
        knownWrong=sum(x['kind']=='known_unfocused' for x in result),
        unreviewed=sum(x['kind']=='unreviewed' for x in result),detections=result)


def select_review(rows,limit=12):
    """One member per role/failure stratum first; deterministic priority thereafter."""
    def rank(r):
        a,b=r['translation'],r['translation-scale']
        return (-(b['knownWrong']-a['knownWrong']),a['targetLocated'],r['image']['sha256'])
    ordered=sorted(rows,key=rank);selected=[];seen=set();strata=set()
    for r in ordered:
        a,b=r['translation'],r['translation-scale']
        stratum=(r['role'],a['targetLocated'],b['knownWrong']>a['knownWrong'])
        if stratum not in strata and r['image']['sha256'] not in seen:
            selected.append(r);strata.add(stratum);seen.add(r['image']['sha256'])
            if len(selected)==limit:return selected
    for r in ordered:
        if r['image']['sha256'] not in seen:
            selected.append(r);seen.add(r['image']['sha256'])
            if len(selected)==limit:break
    return selected


def draw_review(frame,row,path):
    from PIL import Image,ImageDraw
    with Image.open(h.checked(h.ROOT,frame['image'])) as src:image=src.convert('RGB')
    scale=min(1,900/image.width);size=(round(image.width*scale),round(image.height*scale))
    canvas=Image.new('RGB',(size[0]*2,size[1]+45),(24,24,24))
    target=next(c['bounds'] for c in frame['controls'] if c['state']=='focused')
    colors={'focused':'cyan','known_unfocused':'orange','unreviewed':'magenta','unmatched_complete':'red'}
    for column,arm in enumerate(('translation','translation-scale')):
        panel=image.resize(size);d=ImageDraw.Draw(panel)
        for p in sorted(row[arm]['detections'],key=lambda x:-x['score'])[:12]:
            d.rectangle([v*scale for v in p['box']],outline=colors[p['kind']],width=2)
        x,y,w,v=target;d.rectangle([x*scale,y*scale,(x+w)*scale,(y+v)*scale],outline='lime',width=4)
        canvas.paste(panel,(column*size[0],45))
        ImageDraw.Draw(canvas).text((column*size[0]+8,8),
            f'{arm}: target={row[arm]["targetLocated"]}, known wrong={row[arm]["knownWrong"]}, '
            f'boxes shown={min(12,len(row[arm]["detections"]))}/{len(row[arm]["detections"])}',fill='white')
    canvas.save(path,quality=90)


def run(output,target_path):
    output=h.fresh(h.local(output));output.mkdir(parents=True)
    p=h.read(PRIOR/'protocol.json');summary=h.read(PRIOR/'summary.json')
    h.require(summary['protocol']==h.ref(PRIOR/'protocol.json'),'protocol_binding')
    for ref in p['metricSources']:h.checked(h.ROOT,ref)
    for ref in p['models'].values():h.checked(h.ROOT,ref)
    frames=p['realFrames'];h.require(len(frames)==46,'fixed_real_membership')
    rows=[dict(index=i,image=f['image'],screen=f['screen'],complete=f['complete'],
               role=h.control_label(next(c for c in f['controls'] if c['state']=='focused')))
          for i,f in enumerate(frames)]
    refs=[h.ref(PRIOR/'protocol.json'),h.ref(PRIOR/'summary.json')]
    for arm in p['models']:
        predictions=[];metrics=[]
        for i,f in enumerate(frames):
            path=PRIOR/arm/f'real-{i:03d}.json';raw=h.read(path);refs.append(h.ref(path))
            h.require(raw['image']==f['image'],'image_binding');h.checked(h.ROOT,f['image'])
            ds=raw['predictions'];rows[i][arm]=assess(f,ds);predictions.append(ds)
            metrics.append(frame_metrics(f,ds,h.read(OLD/f'{i:03d}.json')))
        h.require(summarize(frames,predictions,metrics)==summary['arms'][arm]['real'],'score_replay')
    selected=select_review(rows);review=[]
    for i,row in enumerate(selected):
        filename=f'{i+1:02d}.jpg';draw_review(frames[row['index']],row,output/filename)
        review.append(dict(index=row['index'],image=row['image'],overlay=h.ref(output/filename),role=row['role']))
    target=h.read(h.local(target_path))['target'];manifest=candidates(target)
    h.write(output/'candidate-manifest.json',manifest)
    groups=defaultdict(list)
    for c in manifest['cases']:groups[c['independence_group']].append(c['case_id'])
    proposal=dict(version='family-transfer48-candidate-v1',sourceRole='calibration',trainingReady=False,
        plannedCases=len(manifest['cases']),plannedTargetPairs=sum(len(c['target_element_ids']) for c in manifest['cases']),
        indivisibleRendererGroups=dict(groups),
        recommendedUse='Separately approve a new training batch; this plan does not relabel calibration inputs.',
        independentHoldout=[],
        constraints=['Existing 61 reference images, 500 synthetic and 46 real challenge frames remain outside training.',
            'All appearance/seed/position variants of each source family stay together; shared renderer ancestry is retained.',
            'A second seed is not an independent holdout; reserve an unexposed native app/layout family separately.'],
        capabilityGaps=['settings_rows and tabs here are UIButton styling, not actual native list/tab widgets.',
            'Targeting every control is planned coverage; measured full-frame position/aspect bins require capture.',
            'Current app-owned campaign export failure still needs producer repair.'])
    h.write(output/'membership-proposal.json',proposal)
    h.write(output/'analysis.json',dict(sources=refs,rows=rows,review=review,
        roles=dict(Counter(r['role'] for r in rows)),modelExecution=False,trainingAdmission=False))
    lines=['# Focus transfer: grouped failure review','',
        'Retained predictions only. Green: reviewed focused body; cyan: matching prediction; orange: known unfocused prediction; magenta: unreviewed region; red: unmatched on a complete frame.',
        '','At most12highest-scoring predictions per pane; captions retain total counts. All46frames are rescored; these12are a diagnostic sample, not an accuracy estimate.','']
    for i,r in enumerate(selected):
        lines += [f'## {i+1}. {r["screen"]} — {r["role"]}', '',f'![Position-only versus position-and-size]({i+1:02d}.jpg)','']
    lines += ['## Next data priorities','',
        '- Genuine native list rows, tabs, buttons and other focusable controls: both models locate0/25non-collection targets.',
        '- Tall/wide artwork and mixed scenes with matched-content focus switches and bright unfocused distractors.',
        '- Distributed measured focus positions; retain translation-only as the baseline.',
        '- Keep calibration and development challenges separate from the new training membership.','']
    (output/'Review.md').write_text('\n'.join(lines))
    print(dict(reviewFrames=len(selected),plannedCases=proposal['plannedCases'],plannedTargetPairs=proposal['plannedTargetPairs']))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    p.add_argument('--target-from',required=True);a=p.parse_args();run(a.output,a.target_from)
