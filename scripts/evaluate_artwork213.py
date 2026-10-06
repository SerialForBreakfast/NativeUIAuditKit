"""Prepare frozen worker213 evaluation inputs and independently score returned predictions.

No inference, training, checkpoint selection or promotion is performed here.
"""
import argparse
import json
from pathlib import Path
import shutil

from artwork204_campaign import recipes
from artwork200_campaign import sha, write
from export_artwork204 import ROOT, BASE
from shared_transfer import require, document
import prediction_artifact as artifact
import eval_run013 as evaluation
from eval_phase6a import DEGENERATE_POLICY

PAYLOAD = BASE/'worker213-input01/payload'
PIN = 'c55d12a27296bfd447b81402a1c2d8c256c305148652e7e670408c071033477c'
ROI = ROOT/'reports/work/WORKER-198/artifacts/eval02701/payload/inputs'
ROI_PINS = dict(fit='3bbb81b0789a88783f30398ced5003c111e5696f0b96597aaae17085d6c2fc3f',
                page='453d6cda4978329d93cdd0529d21093d531c1c95a6446492ae8c5821a5cd58bb',
                combined='687b44e8759953ab54f744ed30676106f5324f63971e8696c1c7b956d2679924')


def partitions(rows):
    expected = recipes()
    require(len(rows) == 96 and [r['id'] for r in rows] == [r['id'] for r in expected], 'membership')
    for row, spec in zip(rows, expected):
        require(row['role'] == spec['dataRole'] and row['family'] == spec['family'], 'role_family')
    return {key: [r for r in rows if r['role'] in roles] for key, roles in
            [('native', ('validation', 'test')), ('validation', ('validation',)), ('diagnostic', ('test',))]}


def fresh(path):
    path = path.absolute()
    require(path.is_relative_to(ROOT) and path.resolve() == path and not path.exists(), 'output_boundary_collision')
    return path


def prepare(out):
    out = fresh(out)
    require(sha(PAYLOAD/'manifest.json') == PIN, 'supplement_changed')
    source = document(PAYLOAD/'manifest.json')
    groups = partitions(source['examples'])
    for ref in source['files']:
        p = PAYLOAD/ref['path']
        require(p.resolve() == p and p.is_relative_to(PAYLOAD) and p.stat().st_size == ref['bytes'] and sha(p) == ref['sha256'], 'input_changed')
    require(shutil.disk_usage(ROOT).free > 256*1024**2, 'space')
    out.mkdir(parents=True)
    rows = []
    for row in groups['native']:
        entry = {'imageID': row['id']}
        for kind, field in [('image', 'image'), ('label', 'label')]:
            src = PAYLOAD/row[field]; dst = out/src.name
            shutil.copyfile(src, dst)
            require(sha(dst) == sha(src), 'copy_changed')
            entry[kind+'Path'] = dst.name; entry[kind+'SHA256'] = sha(dst)
        rows.append(entry)
    refs = {}
    for key, selected in groups.items():
        ids = {r['id'] for r in selected}
        path = out/(key+'.json')
        write(path, dict(formatVersion=artifact.INPUT_FORMAT_VERSION, corpusID='worker213-'+key,
                         images=[r for r in rows if r['imageID'] in ids]))
        request = artifact.load_request(path, 41)
        refs[key] = dict(count=len(request.images), contentSHA256=request.content_sha256, manifestSHA256=sha(path))
    write(out/'prepared.json', dict(sourceManifestSHA256=PIN, groups=refs, trainingEligible=False, modelGatePassed=False))
    return refs


def checked_requests(prepared):
    # Reconstruct expected IDs/roles from the pinned source, not a received claim.
    require(sha(PAYLOAD/'manifest.json') == PIN, 'supplement_changed')
    source = document(PAYLOAD/'manifest.json')
    groups = partitions(source['examples'])
    hashes = {r['path']:r['sha256'] for r in source['files']}
    requests = {}
    for key, rows in groups.items():
        request = artifact.load_request(prepared/(key+'.json'), 41)
        require([r.image_id for r in request.images] == [r['id'] for r in rows], 'evaluation_membership')
        for image, row in zip(request.images, rows):
            require(image.image_sha256 == hashes[row['image']] and image.label_sha256 == hashes[row['label']], 'evaluation_bytes')
        requests[key] = request
    for key, count in [('fit', 135), ('page', 37), ('combined', 413)]:
        require(sha(ROI/key/'input.json') == ROI_PINS[key], 'roi_manifest_changed')
        requests[key] = artifact.load_request(ROI/key/'input.json', 41)
        require(len(requests[key].images) == count, 'roi_membership')
    return requests


def scored(requests, returned, checkpoint, native_layout='combined'):
    require(native_layout in ('combined','split'), 'native_layout')
    settings = dict(evaluation.PREDICTION_SETTINGS, postprocessing=DEGENERATE_POLICY)
    model_hash = sha(checkpoint)
    accepted = {}
    native_keys=('native',) if native_layout=='combined' else ('validation','diagnostic')
    for key in native_keys+('fit', 'page', 'combined'):
        accepted[key] = evaluation.validated_artifact(evaluation.read(returned/(key+'.json')),
                            requests[key], model_hash, expected_settings=settings)
    reports = {}
    for key in ('validation', 'diagnostic', 'fit', 'page', 'combined'):
        predictions = evaluation.subset(accepted['native'], requests[key]) if key in ('validation', 'diagnostic') and native_layout=='combined' else accepted[key]
        reports[key] = evaluation.score(predictions, requests[key], evaluation.load_names())
    return dict(checkpointSHA256=model_hash, reports=reports, modelGatePassed=False,
                   qualification='Diagnostic comparison only; trainer configuration/count review required separately',
                   inputs={k:v.content_sha256 for k,v in requests.items()},
                   predictions={k:sha(returned/(k+'.json')) for k in accepted})


def score(prepared, returned, checkpoint, out, native_layout='combined'):
    out = fresh(out)
    result = scored(checked_requests(prepared), returned, checkpoint, native_layout)
    write(out, result)
    return {k: v['imageCount'] for k,v in result['reports'].items()}


def deltas(control, treatment):
    require(control['inputs']==treatment['inputs'] and set(control['reports'])==set(treatment['reports']), 'comparison_membership')
    changes={}
    for key,a in control['reports'].items():
        b=treatment['reports'][key]
        for field in ('imageCount','metricImplementation','operatingPoint'):
            require(a[field]==b[field], 'comparison_contract')
        require([r['class'] for r in a['perClass']]==[r['class'] for r in b['perClass']], 'comparison_classes')
        rows=[]
        for old,new in zip(a['perClass'],b['perClass']):
            require(old['support']==new['support'], 'comparison_support')
            values={}
            for metric in ('tp','fp','fn','ap50','ap50_95'):
                before,after=old[metric],new[metric]
                require((before is None)==(after is None), 'comparison_availability')
                values[metric]=None if before is None else after-before
            rows.append(dict(className=old['class'],support=old['support'],delta=values,
                operatingRegression=values['tp']<0 or values['fp']>0))
        changes[key]=rows
    return changes


def pair(prepared, control, control_checkpoint, treatment, treatment_checkpoint, out, native_layout='combined'):
    out=fresh(out);requests=checked_requests(prepared)
    require(sha(control_checkpoint)!=sha(treatment_checkpoint), 'same_checkpoint')
    a=scored(requests,control,control_checkpoint,native_layout);b=scored(requests,treatment,treatment_checkpoint,native_layout)
    changes=deltas(a,b)
    # Keep all metrics and identities, not only favorable differences.
    write(out,dict(control=a,treatment=b,deltas=changes,modelGatePassed=False,
        sourceSHA256=sha(Path(__file__)),backendEquivalence='requires separate worker config/source review'))
    return {k:[r['className'] for r in rows if r['operatingRegression']] for k,rows in changes.items()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare'); p.add_argument('out', type=Path)
    p = sub.add_parser('score')
    for name in ('prepared', 'returned', 'checkpoint', 'out'): p.add_argument(name, type=Path)
    p.add_argument('--native-layout',choices=['combined','split'],default='combined')
    p = sub.add_parser('pair')
    for name in ('prepared','control','control_checkpoint','treatment','treatment_checkpoint','out'):p.add_argument(name,type=Path)
    p.add_argument('--native-layout',choices=['combined','split'],default='combined')
    args = vars(parser.parse_args()); command = args.pop('command')
    print(json.dumps(dict(prepare=prepare,score=score,pair=pair)[command](**args)))
