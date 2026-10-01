"""Offline retained-frame discovery and exact full-fit loss audit; no models."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from PIL import Image, ImageDraw
import human_annotation_review as h
import human_recording_review as recorder
import focus_full_fit_experiment as fit
import human_auto_boxes
import human_review_presets
from focus_representative_validation import stratum


def disposition(role, pixels, reviewed, seen):
    if pixels in reviewed:
        return 'already-reviewed'
    if pixels in seen:
        return 'duplicate-observation'
    if role not in ('postInputSettled', 'postInputUnverified'):
        return 'transition-excluded'
    return 'unreviewed-candidate'


def inventory(source, reviewed, output):
    source = h.local(source); output = h.fresh(output); output.mkdir(parents=True)
    manifest = h.read(source/'manifest.json')
    h.require(manifest['schemaVersion'] == 2, 'unsupported_recording')
    events = recorder.events(source/'events.jsonl')
    expected = {r['sha256']: r for r in recorder.events(source/'files.jsonl')}
    rows=[]; seen=set(); cache={}; identifiers=set()
    for event in events:
        if 'frame' not in event:
            continue
        f=event['frame']['_0']; sid=f['sequenceNumber']
        h.require(sid not in identifiers, 'duplicate_sequence'); identifiers.add(sid)
        row=dict(sequence=sid, role=f['role'], sha256=f['sha256'], sessionID=manifest['sessionID'])
        try:
            h.require(f['sourceDeviceID'] == manifest['targetDeviceID'], 'wrong_target')
            digest=f['sha256']; p=source/'images'/('frame-'+digest+'.png')
            h.require(len(digest)==64 and all(c in '0123456789abcdef' for c in digest), 'invalid_hash')
            if digest not in cache:
                h.require(not p.is_symlink() and h.sha(p)==digest and p.stat().st_size==expected[digest]['bytes'], 'changed_image')
                ref=h.ref(p); px=h.pixel_digest(h.ROOT,ref)
                with Image.open(p) as im:
                    im.load(); size=list(im.size)
                cache[digest]=(ref,px,size)
            ref,px,size=cache[digest]
            h.require(size==[f['dimensions']['width'],f['dimensions']['height']], 'wrong_dimensions')
            row.update(image=ref,pixelSHA256=px,size=size,
                       disposition=disposition(f['role'],px,reviewed,seen))
            # Transition observations must not consume a later settled representative.
            if row['disposition']=='unreviewed-candidate': seen.add(px)
        except (OSError, ValueError, KeyError) as e:
            row.update(disposition='blocked', reason=str(e))
        rows.append(row)
    doc=dict(version='focus-retained-discovery-v1',source=str(source.relative_to(h.ROOT)),
             inputs=[h.ref(source/n) for n in ('manifest.json','events.jsonl','files.jsonl')],
             counts=dict(Counter(r['disposition'] for r in rows)),frames=rows,
             trainingEligible=False, independence='not-established')
    h.write(output/'inventory.json',doc)
    # Chronological contact sheets are discovery, not focus labels or frame selection.
    candidates=[r for r in rows if r['disposition']=='unreviewed-candidate']
    for start in range(0,len(candidates),48):
        sheet=Image.new('RGB',(1200,8*195),'#222222'); draw=ImageDraw.Draw(sheet)
        for i,r in enumerate(candidates[start:start+48]):
            x=(i%6)*200;y=(i//6)*195
            with Image.open(h.ROOT/r['image']['path']) as im:
                im.thumbnail((198,165)); sheet.paste(im,(x,y+22))
            draw.text((x+2,y+2),str(r['sequence']),fill='white')
        sheet.save(output/f'contact-{start//48+1:02d}.jpg')
    return doc


def audit(protocol, output):
    doc=h.read(protocol); unsealed=dict(doc); seal=unsealed.pop('protocolSHA256')
    h.require(h.digest(unsealed)==seal, 'changed_protocol')
    for ref in doc['inputs'].values():
        if isinstance(ref,dict) and 'path' in ref: h.checked(h.ROOT,ref)
    base=fit.s.sealed(doc['inputs']['base'],'protocolSHA256')
    rows,weights=fit.training_weights(base)
    h.require(weights==doc['fullFit']['weights'] and rows==doc['samples'][:len(rows)],'changed_weight_membership')
    groups=defaultdict(lambda:dict(count=0,positive=0,negative=0,mass=0.,positiveMass=0.))
    for r in doc['samples']:
        h.checked(h.ROOT,r['crop'])
        expected=r['crop'].get('pixelSHA256',r.get('pixelSHA256'))
        h.require(expected is not None and h.pixel_digest(h.ROOT,r['crop'])==expected,'changed_crop_pixels')
    for r in rows:
        source='human' if r['use']=='human-static-auxiliary' else 'native'
        for key in (source, source+':controlBucket:'+stratum(r),source+':source:'+str(r.get('sourceID',r.get('sourceSessionID','unknown')))):
            g=groups[key];g['count']+=1;g['positive' if r['label'] else 'negative']+=1
            g['mass']+=weights[r['id']];g['positiveMass']+=weights[r['id']]*r['label']
    result=dict(version='focus-full-fit-input-audit-v1',protocol=h.ref(protocol),
                inputs=[h.ref(h.ROOT/'scripts'/n) for n in ('focus_full_fit_experiment.py','focus_pretrained_experiment.py','train_focus_ring_detector.py')],
                groups=dict(groups),counts=doc['counts'],configuration=doc['configuration'],
                representation=doc['representation'],selection=doc['selection'],
                trainingIDs=[r['id'] for r in rows],validationIDs=[r['id'] for r in doc['samples'][len(rows):]],
                checkedCropCount=len(doc['samples']),modelLoaded=False)
    result['nativeAppearanceSupport']=base['sampling']['support']
    result['nativeAppearanceLossMass']={k:.8*v for k,v in base['sampling']['stratumMass'].items()}
    result['groupingNote']='controlBucket uses the evaluation control-name mapping, not the native presentation-aware training strata; do not equate them.'
    h.write(output,result)
    return result


def prepare_review(batch_path, output):
    """Use existing optional presets; never apply or confirm generated boxes."""
    output=h.fresh(output);output.mkdir(parents=True)
    batch=h.validate_batch(batch_path); rows=[]
    sheet=Image.new('RGB',(1280,800),'#222222'); draw=ImageDraw.Draw(sheet)
    for i,f in enumerate(batch['frames']):
        h.require(i<4,'review_preview_limit')
        with Image.open(h.ROOT/f['image']['path']) as im:
            points=human_auto_boxes.detect(im,limit=20)
            name='packet15-'+f['id']
            preset=human_review_presets.save(name,im.size,
                [dict(label='focus:otherFocusable',points=p) for p in points],output/'presets') if points else None
            thumb=im.copy();thumb.thumbnail((630,355));sheet.paste(thumb,((i%2)*640,(i//2)*400+30))
        draw.text(((i%2)*640+4,(i//2)*400+5),f['id']+' | optional proposals: '+str(len(points)),fill='white')
        rows.append(dict(id=f['id'],image=f['image'],pixelSHA256=f['pixelSHA256'],
            preset=h.ref(preset) if preset else None,proposalCount=len(points),humanConfirmed=False))
    sheet.save(output/'preview.jpg')
    result=dict(version='focus-retained-selection-v1',batch=h.ref(batch_path),sessionID=batch['sessionID'],
                frames=rows,trainingEligible=False,role='diagnostic-pending-review-and-admission')
    h.write(output/'selection.json',result)
    return result


def experiment_proposal(audit_path, selection_path, output):
    """A conditional data assignment, deliberately not a runnable trainer protocol."""
    audit_doc=h.read(audit_path); selection=h.read(selection_path)
    batch=h.validate_batch(h.checked(h.ROOT,selection['batch']))
    h.require([f['id'] for f in batch['frames']]==[f['id'] for f in selection['frames']], 'changed_selection')
    for f in selection['frames']: h.checked(h.ROOT,f['image'])
    doc=dict(version='focus-changed-data-proposal-v1',baseline=audit_doc['protocol'],
        audit=h.ref(audit_path),review=h.ref(selection_path),
        baselineTrainingIDs=audit_doc['trainingIDs'],validationIDs=audit_doc['validationIDs'],
        prospectiveFrameIDs=[f['id'] for f in selection['frames']],
        prospectiveSessionID=selection['sessionID'],newControlIDs=None,
        configuration=audit_doc['configuration'],selection=audit_doc['selection'],
        intervention='Add only explicitly reviewed/admitted controls from the four frozen Paramount frames; retain native80/human20 mass and label balance.',
        launchEligible=False,trainingApproved=False,
        blockers=['human_labels_and_settlement_unconfirmed','new_crop_qa_and_duplicate_checks_missing',
                  'explicit_control_admission_and_source_relationship_review_required',
                  'new_feature_cache_and_versioned_trainer_adapter_required','separate_training_approval_required'])
    doc['proposalSHA256']=h.digest(doc);h.write(output,doc)
    return doc


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--source',required=True)
    p.add_argument('--output',required=True); args=p.parse_args()
    out=h.fresh(args.output);out.mkdir(parents=True)
    reviewed=h.read(h.ROOT/'reports/work/HUMAN-CORPUS-INVENTORY-01/final-results/inventory.json')
    inv=inventory(args.source,{f['pixelSHA256'] for f in reviewed['frames']},out/'discovery')
    report=audit(h.ROOT/'reports/work/FOCUS-FULL-FIT-03/frozen/protocol.json',out/'training-audit.json')
    print(json.dumps(dict(inventory=inv['counts'],training=report['groups'])))


if __name__=='__main__': main()
