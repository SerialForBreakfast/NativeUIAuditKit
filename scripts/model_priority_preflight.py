"""Prepare diagnostic full-screen inputs and replay retained iOS localization errors.

No model imports, inference, training, data admission or label edits.
"""
import argparse
from collections import Counter
from pathlib import Path
import statistics

import human_annotation_review as h
import real_model_scorecard as s


def yolo_box(line, width, height):
    c,x,y,w,v=map(float,line.split())
    h.require(c.is_integer() and 0<=c<41 and 0<=x<=1 and 0<=y<=1 and 0<w<=1 and 0<v<=1,
              'invalid_yolo_label')
    return int(c),[(x-w/2)*width,(y-v/2)*height,w*width,v*height]


def resolution(box, size, side=640):
    scale=side/max(size)
    return dict(width=box[2]*scale,height=box[3]*scale,
                centerX=(box[0]+box[2]/2)/size[0],centerY=(box[1]+box[3]/2)/size[1],
                normalizedWidth=box[2]/size[0],normalizedHeight=box[3]/size[1])


def full_screen():
    frames=s.load_frames(s.INVENTORY);items=[];heights=[]
    for f in frames:
        size=h.image(h.ROOT,f['image'])
        controls=[]
        for c in f['controls']:
            geometry=resolution(c['bounds'],size);heights.append(geometry['height'])
            controls.append(dict(id=c['id'],role=h.control_label(c),focus=c['state'],
                                 bodyPixels=c['bounds'],letterbox640=geometry))
        items.append(dict(image=f['image'],screenLabel=f['screen'],size=size,controls=controls,
            completeFocusableControls=f['complete'],trainingEligible=False,
            proposedUse='diagnostic_replay_only',sourceGroup='unresolved_real_capture_ancestry',
            negativeLabelSafe=f['complete']))
    candidates=[h.ROOT/'NativeUITrainer/weights/yolo11n.pt',h.ROOT/'scripts/train_tvos_model.py']
    resident=[h.ref(p) for p in candidates if p.is_file()]
    return dict(version='full-screen-focus-preflight-v1',**h.FLAGS,inputs=h.ref(s.INVENTORY),
        frames=items,resident=resident,totalControls=sum(len(f['controls']) for f in items),
        heightAt640=dict(min=min(heights),median=statistics.median(heights),max=max(heights),
                         below16=sum(x<16 for x in heights)),
        trainingReady=False,blockers=[
            'Diagnostic membership is not training admission; acquisition/layout ancestry needs explicit split groups.',
            '39/46 frames lack explicit focusable-control completeness; do not treat omissions as unfocused/background.',
            'Existing tvOS trainer has no wall-time/output-cap enforcement and dry-run actually trains.',
            'Native26 training uses one artwork-row layout; native wide-row/button coverage intent33 awaits producer mapping.'],
        experiment=dict(question='Does full-screen focus detection recover targets missed by the shipped detector?',
            design='Compare focused-body detection from full frames with crop classification on the same admitted source groups.',
            target='Experimental focusedControl output; preserve public element taxonomy.',
            accounting='Report oracle-reviewed-box crop accuracy separately from predicted-box end-to-end accuracy.',
            controls='Fixed grouped membership, one operating threshold, same target/body convention, normal appearance.',
            firstCorrection='Containment-preserving proposals/rows and focused-control recall before another brightness-only classifier run.',
            newTraining='Requires explicitly scoped encoding/training budget and approved complete synthetic membership.'))


def ios_replay():
    root=h.ROOT/'reports/work/IOS-R013-EVAL'
    manifest=h.read(root/'withheld_manifest.json',32*1024*1024)
    predictions=h.read(root/'candidate_predictions.json',128*1024*1024)
    names=h.taxonomy()
    h.require(h.sha(h.CATEGORY)==predictions['categoryMap']['sha256'],'category_map_changed')
    by_id={r['imageID']:r for r in predictions['results']}
    h.require(len(by_id)==len(predictions['results']),'duplicate_prediction_image')
    counts={};confusions=Counter();narrow=Counter()
    for member in manifest['images']:
        row=by_id[member['imageID']]
        h.require(row['status']=='ok' and row['imageSHA256']==member['imageSHA256'] and
                  row['labelSHA256']==member['labelSHA256'],'prediction_identity_mismatch')
        # Run013's retained inputs link points to this versioned in-project dataset.
        # Resolve that known source explicitly, without relaxing harvest symlink rules.
        relative=Path(member['labelPath'])
        h.require(relative.parts[:1]==('inputs',) and '..' not in relative.parts,'invalid_label_path')
        dataset=h.ROOT/'NativeUITrainer/yolo_dataset_41class_r7'
        label=h.checked(dataset,dict(path=str(Path(*relative.parts[1:])),sha256=member['labelSHA256']))
        h.require((root/relative).resolve()==label,'changed_dataset_binding')
        truth=[yolo_box(line,row['width'],row['height']) for line in label.read_text().splitlines() if line.strip()]
        predictions_for_frame=[d for d in row['detections'] if d['score']>=.25]
        boxes=[]
        for d in predictions_for_frame:
            x,y,X,Y=d['xyxyPixels'];boxes.append(s.bounds(dict(x=x,y=y,width=X-x,height=Y-y)))
        matches=s.matching([b for _,b in truth],boxes,.5)
        for i,(cid,b) in enumerate(truth):
            name=names[cid];count=counts.setdefault(name,Counter())
            count['support']+=1;count['localized50']+=i in matches
            scaled=resolution(b,(row['width'],row['height']))
            narrow[name]+=min(scaled['width'],scaled['height'])<8
            predicted=names[predictions_for_frame[matches[i]]['classID']] if i in matches else 'missing'
            count['exactRole']+=predicted==name
            confusions[(name,predicted)]+=1
    prior=h.read(root/'evaluation.json',32*1024*1024)
    sources=[h.ROOT/'NativeUIDatasetGenerator/Templates'/f'{name}Template.swift'
             for name in ('CardDetail','Alert','GalleryPage','KitchenSink')]
    return dict(version='ios-localization-role-diagnosis-v1',**h.FLAGS,
        inputs=[h.ref(root/p) for p in ('withheld_manifest.json','candidate_predictions.json','evaluation.json')],
        implementation=h.ref(__file__),images=len(manifest['images']),counts=counts,
        confusion=[dict(truth=a,prediction=b,count=n) for (a,b),n in sorted(confusions.items())],
        shortSideBelow8At640=narrow,sourceEvidence=[h.ref(p) for p in sources],
        matching='Maximum cardinality class-agnostic IoU .50, confidence .25; diagnostic, not AP or historical greedy confusion.',
        retainedGate=prior['gate'],corrections=[
            'Retain secondaryButton truth: CardDetail captures an explicit secondary action; do not relabel it cancelAction to match predictions.',
            'Localize coarse button bodies first; use context/text to distinguish secondary versus cancel. Test on source-family-held-out examples.',
            'Prioritize listRow/imageView family diversity; synthetic addon success does not establish withheld-family transfer.',
            'Treat page dots/scroll indicators as resolution/localization errors; test a controlled resolution arm, not a semantic rename.',
            'Fill independent class coverage before interpreting a full-41-class release gate.'])


def run(output):
    out=h.fresh(output);out.mkdir(parents=True)
    full=full_screen();ios=ios_replay()
    h.write(out/'full-screen-preflight.json',full,sealed=True)
    h.write(out/'ios-diagnosis.json',ios,sealed=True)
    lines=['# Next model experiment readiness','',
      f"Full-screen diagnostic input prepared: {len(full['frames'])} screenshots / {full['totalControls']} controls.",
      f"Control height after 640 letterboxing: {full['heightAt640']}. This measures bodies, not shadow visibility.",
      '', '## Full-screen experiment prerequisites','']+['- '+x for x in full['blockers']]
    lines += ['', '## iOS retained-prediction diagnosis','',
      'Replayed 2,000 withheld screenshots at confidence .25 / IoU .50; no inference or label changes.',
      '', '| Role | Truth | Any class localized | Correct role | Short side <8px at 640 |',
      '|---|---:|---:|---:|---:|']
    for name,c in sorted(ios['counts'].items()):
        lines.append(f"| {name} | {c['support']} | {c['localized50']} | {c['exactRole']} | {ios['shortSideBelow8At640'][name]} |")
    lines += ['', 'Correction order:','']+['- '+x for x in ios['corrections']]
    (out/'readiness.md').write_text('\n'.join(lines)+'\n')
    print('Full-screen diagnostic inputs and iOS replay complete.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    run(p.parse_args().output)
