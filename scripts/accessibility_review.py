"""Optional accessibility evidence -> ordinary-image grouped diagnostic review."""
import argparse
import copy
import random
import shutil
import math
from collections import Counter
from PIL import Image
import human_annotation_review as h

VERSION = 'accessibility-review-batch-v1'
EVIDENCE = 'accessibility-review-evidence-v1'


def parse_perception(d):
    """Check advisory observations without granting focus or navigation authority."""
    h.require(isinstance(d,dict) and d.get('profile') in ('stable','combined','hover_text','high_contrast_focus') and
              isinstance(d.get('settingsEvidence'),str), 'unsupported_perception_report')
    boxes=d.get('outlineCandidates')
    h.require(isinstance(boxes,list) and len(boxes)<=64, 'outline_limit')
    for b in boxes:
        h.require(isinstance(b,dict) and set(b)=={'x','y','width','height'} and
            all(type(v) in (int,float) and math.isfinite(v) for v in b.values()),'outline_coordinates')
        h.require(b['x']>=0 and b['y']>=0 and b['width']>0 and b['height']>0 and
            b['x']+b['width']<=1 and b['y']+b['height']<=1,'outline_range')
    rules=d.get('focusRules')
    if rules is not None:
        h.require(isinstance(rules,dict) and type(rules.get('version')) is int and rules['version']==1,
                  'unsupported_focus_rules')
        h.require(rules.get('navigationEligible') is False and
                  rules.get('settingsEvidence')=='not_verified_from_pixels','focus_rules_authority')
        candidates=rules.get('candidates')
        h.require(isinstance(candidates,list) and len(candidates)<=128,'focus_candidate_limit')
        h.require(rules.get('state')==('candidate' if len(candidates)==1 else 'abstained'),
                  'focus_rule_state')
        h.require(isinstance(rules.get('reasons'),list) and
                  all(isinstance(x,str) for x in rules['reasons']),'focus_rule_reasons')
        for c in candidates:
            h.require(isinstance(c,dict) and (c.get('geometryRole'),c.get('strategy')) in (
                ('assisted_outline_proposal','bright_outline'),
                ('filled_row_proposal','row_fill_contrast_ocr')),'focus_geometry_role')
            # Reuse the same normalized coordinate checks for both geometry roles.
            parse_perception(dict(profile='stable',settingsEvidence='proposal',outlineCandidates=[c.get('bounds')]))
            h.require(isinstance(c.get('labels'),list) and len(c['labels'])<=8 and
                      all(isinstance(x,str) and len(x)<=512 for x in c['labels']),'focus_context_labels')
            contrast=c.get('contrast')
            h.require(contrast is None or (type(contrast) in (int,float) and math.isfinite(contrast)
                      and -1<=contrast<=1),'focus_contrast')
    return dict(profile=d['profile'],settingsEvidence=d['settingsEvidence'],outlineCandidates=boxes,
                banner=d.get('banner'),focusRules=copy.deepcopy(rules),
                interpretation=d.get('interpretation'),proposalOnly=True,navigationEligible=False)


def perception(record):
    """Read standalone reports or select an image-bound frame from a TTR sidecar."""
    if not record.get('perceptionReport'): return None
    d=h.read(h.checked(h.ROOT,record['perceptionReport']))
    if d.get('kind')=='vision_pair_preprocessing':
        h.require(type(d.get('schemaVersion')) is int and d['schemaVersion']==1 and
            d.get('coordinateConvention')=='top_left_normalized_xywh; pixels=normalized*per_frame_dimensions',
            'unsupported_perception_sidecar')
        frames=d.get('frames')
        h.require(isinstance(frames,list) and len(frames)==2 and
                  all(isinstance(f,dict) for f in frames),'perception_frames')
        h.require(sorted(f.get('role','') for f in frames)==['after','before'],'perception_frame_roles')
        role=record.get('perceptionFrameRole')
        h.require(role in ('before','after'),'perception_frame_role_required')
        frame=next(f for f in frames if f['role']==role)
        ref=record.get('perceptionImage')
        h.require(isinstance(ref,dict),'perception_image_required')
        image_path=h.checked(h.ROOT,ref)
        h.require(frame.get('sha256')==ref['sha256'],'perception_image_mismatch')
        with Image.open(image_path) as im:
            h.require(im.format=='PNG' and im.size==(frame.get('width'),frame.get('height')),
                      'perception_dimensions')
        d=frame.get('accessibility')
    return parse_perception(d)


def assess(frame, record, target):
    """Never copy an assistive outline into an ordinary body box."""
    reasons = []
    if record is None:
        return ['missing_accessibility_evidence']
    h.require(isinstance(record,dict), 'invalid_evidence_record')
    if record.get('ordinaryImageSHA256') != frame['image']['sha256']:
        reasons.append('ordinary_image_mismatch')
    if record.get('target') != target or not target:
        reasons.append('target_mismatch')
    if record.get('screen') != frame['screen'] or record.get('size') != frame['size']:
        reasons.append('screen_or_viewport_mismatch')
    profiles = record.get('profiles', {})
    h.require(isinstance(profiles,dict) and isinstance(record.get('correspondence',{}),dict),'invalid_profile_structure')
    for name, style in [('ordinary', 'default'), ('assisted', 'highContrast')]:
        p = profiles.get(name, {})
        h.require(isinstance(p,dict),'invalid_profile_structure')
        if p.get('focusStyle') != style or p.get('verification') != 'receipt':
            reasons.append(name + '_profile_unverified')
        if not p.get('receipt'): reasons.append(name + '_receipt_missing')
    for key in ('sameControl', 'sameViewport', 'settled', 'fresh', 'restored'):
        if record.get('correspondence', {}).get(key) is not True:
            reasons.append(key + '_unverified')
    if record.get('correspondence', {}).get('candidateCount') != 1:
        reasons.append('ambiguous_identity')
    if record.get('actionability') != 'control': reasons.append('nonactionable_or_unknown')
    if record.get('focusChannel') != 'input': reasons.append('assistive_focus_not_input')
    ids = {c['id'] for c in frame['proposals']}
    if record.get('focusedControlID') not in ids: reasons.append('unknown_control')
    if any(c['state']=='focused' and c['id']!=record.get('focusedControlID') for c in frame['proposals']):
        reasons.append('focus_disagreement')
    if record.get('status') != 'verified': reasons.append('observation_' + str(record.get('status', 'unknown')))
    return reasons


def project(source, evidence, sample_count, seed):
    h.require(evidence.get('version') == EVIDENCE, 'accessibility_evidence_version')
    records = evidence.get('frames', [])
    h.require(isinstance(records, list) and len(records) <= 256, 'evidence_limit')
    by = {r['frameID']: r for r in records}
    h.require(len(by) == len(records), 'duplicate_evidence_frame')
    frames = [f for f in source['frames'] if f['disposition'] == 'imported']
    h.require(set(by) <= {f['id'] for f in frames}, 'foreign_evidence_frame')
    h.require(type(sample_count) is int and 0 <= sample_count <= 256 and type(seed) is int, 'sampling_config')
    random_ids = random.Random(seed).sample(sorted(f['id'] for f in frames), min(sample_count, len(frames)))
    results = []
    for original in frames:
        f = copy.deepcopy(original)
        reasons = assess(f, by.get(f['id']), source.get('sourceDeviceID'))
        f['accessibility'] = dict(evidence=by.get(f['id']), reasons=reasons,
            randomSample=f['id'] in random_ids, targetedReview=bool(reasons), ordinaryGeometryRetained=True)
        if by.get(f['id']): f['accessibility']['perception']=perception(by[f['id']])
        if not reasons:
            focused = by[f['id']]['focusedControlID']
            for c in f['proposals']:
                # Positive evidence identifies one control; it does not label every other control.
                if c['id'] == focused: c['state'] = 'focused'
        results.append(f)
    selected={f['id'] for f in results if f['accessibility']['randomSample'] or f['accessibility']['targetedReview']}
    # Keep complete connected endpoint groups together for review, without expanding the random denominator.
    while True:
        expanded=selected | {i for p in source['pairs'] if selected.intersection(p['frames']) for i in p['frames']}
        if expanded==selected: break
        selected=expanded
    for f in results:
        f['accessibility']['pairCompanion']=f['id'] in selected and not (
            f['accessibility']['randomSample'] or f['accessibility']['targetedReview'])
    return [f for f in results if f['id'] in selected], random_ids


def evidence_refs(evidence):
    for r in evidence.get('frames', []):
        h.require(isinstance(r,dict),'invalid_evidence_record')
        if r.get('perceptionReport'): yield r['perceptionReport']
        if r.get('perceptionImage'): yield r['perceptionImage']
        for key in ('assistedImage', 'observation'):
            yield r[key]
        for p in r.get('profiles', {}).values():
            if p.get('receipt'): yield p['receipt']


def validate(path):
    d = h.sealed(h.local(path), VERSION)
    source_path = h.checked(h.ROOT, d['sourceBatch'])
    h.require(h.read(source_path).get('version') != VERSION, 'nested_accessibility_batch')
    source = h.validate_batch(source_path)
    h.require(d['id']==source['id']+'-accessibility' and d['sourceDeviceID']==source.get('sourceDeviceID')
              and d['categoryMap']==source['categoryMap'], 'changed_batch_identity')
    evidence = h.read(h.checked(h.ROOT, d['accessibilityEvidence']))
    for ref in evidence_refs(evidence): h.checked(h.ROOT, ref)
    expected, random_ids = project(source, evidence, d['sampling']['count'], d['sampling']['seed'])
    h.require(expected == d['frames'] and random_ids == d['sampling']['randomFrames'], 'changed_projection')
    h.require(d['pairs'] == [p for p in source['pairs'] if set(p['frames']) <= {f['id'] for f in expected}], 'changed_pairs')
    for f in expected: h.checked(h.ROOT, f['image'])
    return d


def prepare(batch_path, evidence_path, output, sample_count=8, seed=29):
    batch_path, evidence_path = h.local(batch_path), h.local(evidence_path)
    source = h.validate_batch(batch_path)
    h.require(source['version'] != VERSION, 'nested_accessibility_batch')
    evidence = h.read(evidence_path)
    for ref in evidence_refs(evidence): h.checked(h.ROOT, ref)
    for r in evidence.get('frames',[]): h.image(h.ROOT,r['assistedImage'])
    frames, random_ids = project(source, evidence, sample_count, seed)
    h.require(frames, 'no_reviewable_frames')
    output = h.fresh(output); output.mkdir(parents=True); (output/'editor').mkdir()
    selected = {f['id'] for f in frames}
    result = dict(version=VERSION, **h.FLAGS, id=source['id']+'-accessibility',
        sourceBatch=h.ref(batch_path), accessibilityEvidence=h.ref(evidence_path),
        categoryMap=source['categoryMap'], sourceDeviceID=source.get('sourceDeviceID'),
        frames=frames, pairs=[p for p in source['pairs'] if set(p['frames']) <= selected],
        sampling=dict(seed=seed,count=sample_count,randomFrames=random_ids), completeFrameCandidates=False)
    lines=['# Ordinary-image accessibility review', '',
        'Proposals only. Review focus and ordinary body bounds. Assisted outlines are supporting evidence.',
        'All frames are grouped in one editor session; random and targeted samples are reported separately.', '']
    for f in frames:
        im = h.checked(h.ROOT, f['image']); shutil.copyfile(im, output/'editor'/(f['editorStem']+'.png'))
        doc = h.editor_document(result['id'], f)
        if f['accessibility']['reasons']:
            for shape in doc['shapes']: shape['flags']['flagged'] = True
        h.write(output/'editor'/(f['editorStem']+'.json'), doc)
        a=f['accessibility']; lines += [f"## {f['id']}", '',
            f"Random sample: {a['randomSample']}; targeted review: {a['targetedReview']}.",
            'Reasons: '+(', '.join(a['reasons']) or 'candidate correspondence verified; human confirmation pending'),
            f"![Ordinary]({im})", '']
        if a['evidence']:
            lines += [f"![Assisted evidence]({h.checked(h.ROOT,a['evidence']['assistedImage'])})", '']
            if a.get('perception'):
                lines += ['Producer outline proposals (normalized; not ordinary body bounds):',
                          str(a['perception']['outlineCandidates']), '']
                if a['perception'].get('focusRules') is not None:
                    lines += ['HCF rule proposals. Geometry roles remain separate. Navigation is not permitted.',
                              str(a['perception']['focusRules']), '']
    h.write(output/'batch.json', result, sealed=True)
    (output/'review.md').write_text('\n'.join(lines)+'\n')
    validate(output/'batch.json')
    return result


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('batch','evidence','output'): p.add_argument('--'+key,required=True)
    p.add_argument('--sample-count',type=int,default=8); p.add_argument('--seed',type=int,default=29)
    a=p.parse_args(); r=prepare(a.batch,a.evidence,a.output,a.sample_count,a.seed)
    print(dict(frames=len(r['frames']),random=len(r['sampling']['randomFrames']),
        reasons=dict(Counter(x for f in r['frames'] for x in f['accessibility']['reasons']))))
