"""Prepare equal-size rehearsal arms from pinned, training-only records."""
import copy
import hashlib
from collections import defaultdict
from pathlib import Path
import shutil
from PIL import Image
import artifact_storage
import research_queue as q
from experiment_templates import checked, pin
from detector_native_inputs import bounds

OUT = None


def eligible(inventory):
    q.require(inventory.get('integrityPassed') and not inventory.get('errors'), 'rehearsal_inventory')
    reserved = [r for r in inventory['members'] if r['split'] != 'train']
    groups = {(r['family'], r['seed']) for r in reserved}
    pixels = {r['pixelSHA256'] for r in reserved}
    return [r for r in inventory['members'] if r['split'] == 'train'
            and (r['family'], r['seed']) not in groups and r['pixelSHA256'] not in pixels]


def interleave(rows):
    families = defaultdict(list)
    for row in rows:
        families[row['family']].append(row)
    for values in families.values():
        values.sort(key=lambda r: hashlib.sha256(r['imageID'].encode()).hexdigest())
    for index in range(max(map(len, families.values()), default=0)):
        for family in sorted(families):
            if index < len(families[family]):
                yield families[family][index]


def mix(original, native, count):
    q.require(len(original) == count and 0 < len(native) < count, 'rehearsal_count')
    for row in original + native:
        q.require(row['role'] == 'train' and row['trainingEligible'] and row['labelsComplete'], 'rehearsal_role')
    q.require(len({r['image']['sha256'] for r in original + native}) == count + len(native), 'rehearsal_duplicate')
    return original, original[:count-len(native)] + native


def prepare(request, output):
    q.require(not output.exists(), 'rehearsal_output_exists')
    inv = q.load(checked(request['inventory']))
    freeze = q.load(checked(request['freeze']))
    q.require(freeze['auditSHA256'] == request['inventory']['sha256'], 'rehearsal_freeze')
    exported = q.load(checked(request['export']))
    native = q.load(checked(request['native']))
    q.require(native.get('trainingAdmitted') and native['version'] == 'detector-training-membership-v2', 'rehearsal_native')
    names = native['names']
    category = q.load(checked(request['categories']))
    q.require(request['categories']['sha256'] == freeze['categoryMapSHA256'] and
              names == [r['name'] for r in category['categories']], 'rehearsal_class_order')
    retained = [r for ref in request['evaluation'] for r in q.load(checked(ref))['frames']]
    reserved_groups = {r['group'] for r in retained}
    reserved_images = {r['sha256'] for r in retained}
    by = {Path(r['image']['path']).stem: r for r in exported['rows']}
    q.require(len(by) == len(exported['rows']), 'rehearsal_export_identity')
    selected, skipped, seen_groups, seen_pixels = [], [], set(), set()
    output.mkdir(parents=True)
    for row in interleave(eligible(inv)):
        group = row['family'] + ':' + str(row['seed'])
        if group in seen_groups or group in reserved_groups or row['pixelSHA256'] in seen_pixels:
            continue
        ref = by[Path(row['imageID']).stem]
        q.require(ref['split'] == 'train', 'rehearsal_export_role')
        image = artifact_storage.resolve_input(q.ROOT/ref['image']['path'])
        label = artifact_storage.resolve_input(q.ROOT/ref['label']['path'])
        q.require(q.digest(image) == ref['image']['sha256'], 'rehearsal_image_changed')
        q.require(q.digest(label) == ref['label']['sha256'], 'rehearsal_label_changed')
        # Keep original Run013 labels for this first matched comparison.
        if ref['label']['sha256'] != row['labelSHA256'] or ref['image']['sha256'] != row['imageSHA256']:
            skipped.append(dict(id=row['imageID'], reason='repaired_record_not_original')); continue
        with Image.open(image) as im:
            size = im.size
            pixel = hashlib.sha256(str(size).encode()+im.convert('RGBA').tobytes()).hexdigest()
        q.require(size == (row['width'], row['height']) and pixel == row['pixelSHA256'], 'rehearsal_pixels')
        q.require(ref['image']['sha256'] not in reserved_images, 'rehearsal_evaluation_overlap')
        controls = []
        try:
            for index, line in enumerate(label.read_text().splitlines()):
                values = line.split()
                if not values: continue
                kind = int(values[0]); cx, cy, w, h = map(float, values[1:])
                q.require(0 <= kind < len(names), 'rehearsal_class')
                box = [(cx-w/2)*size[0], (cy-h/2)*size[1], w*size[0], h*size[1]]
                controls.append(dict(id=str(index), **{'class': names[kind]}, bounds=bounds(box,*size)))
        except ValueError:
            skipped.append(dict(id=row['imageID'], reason='invalid_original_geometry')); continue
        if not controls:
            skipped.append(dict(id=row['imageID'], reason='empty_label_frame_outside_positive_rehearsal')); continue
        target = output/(ref['image']['sha256']+'.png')
        shutil.copyfile(image,target)
        q.require(q.digest(target) == ref['image']['sha256'], 'rehearsal_copy')
        selected.append(dict(id='rehearsal-'+Path(row['imageID']).stem, group=group,
            role='train', trainingEligible=True, labelsComplete=True, image=pin(target),
            width=size[0], height=size[1], controls=controls))
        seen_groups.add(group); seen_pixels.add(pixel)
        if len(selected) == request['count']: break
    for row in native['rows']:
        q.require(row['group'] not in reserved_groups and row['image']['sha256'] not in reserved_images,
                  'rehearsal_native_overlap')
    arms = mix(selected,native['rows'],request['count'])
    for name, rows in zip(('control','mixed'),arms):
        doc = copy.deepcopy(native)
        doc.update(rows=rows, lineage=[], rehearsalSources=request,
                   limitation='Matched development pilot. Equal frame counts do not prove equal semantic diversity.')
        q.save(output/(name+'.json'),doc)
    report = dict(version='ios-rehearsal-v1', framesPerArm=request['count'],
        sharedOriginal=request['count']-len(native['rows']), nativeFrames=len(native['rows']),
        originalGroups=len(seen_groups), skipped=skipped, sources=request,
        selection='Family round-robin with image-ID hash order. No evaluation scores.', modelAccepted=False)
    q.save(output/'qualification.json',report)
    return report


def compare():
    """Compare completed scores without repeating inference or accepting models."""
    import detector_case_match411 as matching
    spec=q.load(OUT.parents[2]/'spec.json')
    request=q.load(checked(spec['comparisonRequest']))
    dependencies=q.dependency_inputs(spec,OUT.parents[4])
    outputs={d['job']: {Path(r['path']).name: r for r in d['outputs']} for d in dependencies}
    reports=[]
    for pair in request['pairs']:
        candidate=outputs[pair['candidate']]['scorecard.json']
        control=outputs[pair['control']]['scorecard.json']
        for name,baseline in [('matched-control',control),('native-only',pair['native']),('Run013',pair['original'])]:
            a,b=q.load(checked(baseline)),q.load(checked(candidate))
            q.require(a['inputs']==b['inputs'] and a['settings']==b['settings'] and a['frames']==b['frames'],
                      'rehearsal_comparison_inputs')
            labels=q.load(checked(b['inputs']))
            bundle=dict(version='detector-case-inputs-v1',role='development',platform='iOS',
                format='real-model-scorecard-v1',confidence=b['settings']['confidence'],
                labelReview=labels['labelReview'],baseline=baseline,candidate=candidate,labels=b['inputs'])
            images,predictions,meta=matching.load_bundle(bundle)
            settings=('class',None,{},'class-aware')
            rows,extra=matching.evaluate(images,predictions,settings,bundle['confidence'])
            report=matching.summarize(rows,extra,settings,meta)
            report.update(condition=pair['candidate'],comparison=name)
            reports.append(report)
    publish(reports)


def aggregate():
    spec=q.load(OUT.parents[2]/'spec.json')
    request=q.load(checked(spec['comparisonRequest']))
    deps=q.dependency_inputs(spec,OUT.parents[4])
    q.require(len(deps)==2, 'rehearsal_report_count')
    reports=[r for d in deps for r in q.load(checked(d['outputs'][0]))['reports']]
    expected={(p['candidate'],name) for p in request['pairs'] for name in ('matched-control','native-only','Run013')}
    q.require(len(reports)==len(expected) and {(r['condition'],r['comparison']) for r in reports}==expected,
              'rehearsal_report_membership')
    publish(reports)


def publish(reports):
    losses=sum(len(r['lostPriorSuccesses']) for r in reports if r['comparison']=='Run013')
    gains=sum(len(r['gains']) for r in reports if r['comparison']=='matched-control')
    outcome='contradicted' if losses else 'supported' if gains else 'inconclusive'
    result=dict(version='research-condition-v1',outcome=outcome,
        reason='Retained losses prevent replacement.' if losses else 'Review the matched gain and independent qualification.',
        modelAccepted=False,reports=reports,
        limitation='Development detector comparisons only. No full-corpus, focus, or deployment qualification.')
    q.save(OUT/'decision.json',result)
    lines=['# Matched iOS rehearsal comparison','', 'Outcome: '+outcome,'',
           '| Comparison | Gains | Lost detections |','|---|---:|---:|']
    for name in ('matched-control','native-only','Run013'):
        values=[r for r in reports if r['comparison']==name]
        lines.append('| '+name+' | '+str(sum(len(r['gains']) for r in values))+' | '+
                     str(sum(len(r['lostPriorSuccesses']) for r in values))+' |')
    lines+=['',result['limitation'],'No model is promoted.']
    (OUT/'report.md').write_text('\n'.join(lines)+'\n')
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path=n,sha256=q.digest(OUT/n)) for n in ('decision.json','report.md')]))
