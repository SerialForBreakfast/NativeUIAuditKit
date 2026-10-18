"""Prepare development-only detector labels from qualified native captures.

Keep exported control bounds. Pixel probes qualify data; they do not replace labels.
"""
import math
import shutil
from pathlib import Path
from PIL import Image
import research_queue as q
from template_inputs398 import checked, pin

OUT = None
VERSION = 'detector-native-inputs-v1'


def bounds(value, width, height):
    q.require(len(value) == 4 and all(type(x) in (int, float) and math.isfinite(x) for x in value), 'detector_bounds')
    x, y, w, h = value
    q.require(x >= 0 and y >= 0 and w > 0 and h > 0 and x+w <= width and y+h <= height, 'detector_bounds')
    return list(value)


def source_file(root, ref):
    path = q.local_path(root, ref['path'])
    q.require(path.is_file() and q.digest(path) == ref['sha256'], 'detector_source_changed')
    return path


def ios_rows(source, excluded):
    path = checked(source['manifest'])
    doc = q.load(path)
    body = q.load(checked(source['bodies']))
    q.require(doc.get('version') == 'ios-native-capture-manifest-v1', 'detector_manifest_version')
    q.require(body.get('version') == 'ios-rendered-bodies-v1', 'detector_body_version')
    rows = []
    for row in doc['rows']:
        if row['family'] in excluded:
            continue
        q.require(row['role'] == 'development' and row['trainingEligible'] is False, 'detector_role')
        q.require(row['status'] == 'eligible', 'detector_eligibility')
        q.require(row['appearanceVerified'] == 'paired-rendered', 'detector_appearance')
        image = source_file(path.parent, row['image'])
        side = q.load(source_file(path.parent, row['sidecar']))
        q.require(side['imageSHA256'] == row['image']['sha256'], 'detector_sidecar_image')
        q.require(side['image']['platform'] == 'iOS', 'detector_platform')
        width, height = side['image']['pixelWidth'], side['image']['pixelHeight']
        with Image.open(image) as im:
            q.require(im.size == (width, height), 'detector_dimensions')
        measures = {m['id']: m for m in body['frames'][row['id']]}
        controls = []
        eligible = [e for e in side['elements'] if not e.get('excluded') and not e.get('knownIssues')
                    and e['boundsPixels']['width'] > 0 and e['boundsPixels']['height'] > 0]
        q.require(len(eligible) == row['labels'], 'detector_label_membership')
        for element in eligible:
            if element.get('occluded'):
                continue
            measure = measures.get(element['id'])
            q.require(measure is not None, 'detector_body_missing')
            status = measure.get('v2', measure)['status']
            # Ambiguous probes remain explicit. They do not establish visible-body accuracy.
            q.require(status not in ('outside', 'empty'), 'detector_body_failed')
            b = element['boundsPixels']
            controls.append(dict(id=element['id'], **{'class': element['elementType']},
                bounds=bounds([b[k] for k in ('x','y','width','height')], width, height),
                state='unknown', bodyCheck=status))
        rows.append(dict(id=row['id'], image=pin(image), sha256=row['image']['sha256'],
            width=width, height=height, screen=row['family'], group=row['group'],
            appearance=row['appearance'], controls=controls))
    return rows


def native_rows(source, families, profile, out):
    doc = q.load(checked(source['admission']))
    q.require(doc.get('version') == 'native-control-admission-v1', 'detector_admission_version')
    q.require(set(families) <= {'button','row','tab'} and families, 'detector_families')
    taxonomy = {}
    for ref in doc['sources']:
        artifact=q.load(checked(ref))
        path=Path(artifact['path'])
        q.require(path.resolve().is_relative_to(Path(artifact['storage']['root']).resolve()), 'detector_source_scope')
        q.require(q.digest(path) == artifact['sha256'], 'detector_source_changed')
        for frame in q.load(path)['frames']:
            classes={e['id']:e.get('taxonomy_class') or e.get('taxonomyRole')
                     for e in frame['before']['scene']['elements']}
            old=taxonomy.setdefault(frame['sha256'],classes)
            q.require(old == classes, 'detector_taxonomy_conflict')
    rows = []
    for row in doc['rows']:
        if row['role'] != 'development' or row['family'] not in families or row['profile'] != profile:
            continue
        image = Path(row['path'])
        # Admission pins images. Accept only project files or the approved local USB corpus.
        allowed = q.ROOT.parent.parent
        q.require(image.resolve().is_relative_to(q.ROOT) or image.resolve().is_relative_to(allowed), 'detector_image_scope')
        q.require(q.digest(image) == row['sha256'], 'detector_source_changed')
        with Image.open(image) as im:
            q.require(im.size == (row['width'], row['height']), 'detector_dimensions')
        if not image.is_relative_to(q.ROOT):
            target = out / 'images' / (row['sha256']+'.png')
            target.parent.mkdir(exist_ok=True)
            if not target.exists():
                shutil.copyfile(image, target)
            q.require(q.digest(target) == row['sha256'], 'detector_copy_changed')
            image = target
        q.require(all(taxonomy[row['sha256']].get(ident) for ident in row['boxes']), 'detector_taxonomy_missing')
        controls = [dict(id=ident, **{'class':taxonomy[row['sha256']][ident]},
            bounds=bounds(box,row['width'],row['height']),
            state='focused' if ident == row['focus'] else 'unfocused') for ident,box in row['boxes'].items()]
        rows.append(dict(id=row['id'], image=pin(image), sha256=row['sha256'], width=row['width'], height=row['height'],
            screen=row['family'], group=row['group'], appearance=profile, controls=controls))
    return rows


def prepare(config, out):
    q.require(config.get('version') == VERSION and config.get('role') == 'development', 'detector_configuration')
    q.require(set(config) == {'version','role','platform','sources','excludedFamilies','families','profile'}, 'detector_fields')
    q.require(config['platform'] in ('iOS','tvOS') and config['sources'], 'detector_platform')
    rows = []
    for source in config['sources']:
        if config['platform'] == 'iOS':
            q.require(set(source) == {'manifest','bodies'}, 'detector_source_fields')
            rows.extend(ios_rows(source, config['excludedFamilies']))
        else:
            q.require(set(source) == {'admission'}, 'detector_source_fields')
            rows.extend(native_rows(source,config['families'],config['profile'],out))
    unique = {}
    for row in rows:
        signature = q.text_digest(sorted(row['controls'], key=lambda c:c['id']))
        if row['sha256'] in unique:
            old = unique[row['sha256']]
            q.require(old['group'] == row['group'] and q.text_digest(sorted(old['controls'],key=lambda c:c['id'])) == signature,
                      'detector_duplicate_conflict')
        else:
            unique[row['sha256']] = row
    q.require(0 < len(unique) <= 64, 'detector_frame_count')
    return dict(version=VERSION, platform=config['platform'], role='development', trainingEligible=False,
        labelReview='unknown', labelsComplete=False, sources=config['sources'], frames=list(unique.values()),
        limitation='Native exported bounds. Body probes have limits. Unmatched predictions are not verified false positives.')


def run():
    from template_adapters395 import resolve_inputs, document
    cfg=q.load(OUT.parents[2]/'spec.json')['template']
    refs=resolve_inputs(cfg,OUT)
    doc=prepare(document(refs['configuration']),OUT)
    q.save(OUT/'labels.json',doc)
    q.save(OUT/'benchmark_summary.json',dict(version=VERSION,frames=len(doc['frames']),
        labels=sum(len(r['controls']) for r in doc['frames']),groups=len({r['group'] for r in doc['frames']}),
        platform=doc['platform'],modelAccepted=False,trainingEligible=False))
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path=n,sha256=q.digest(OUT/n)) for n in ('labels.json','benchmark_summary.json')]))
