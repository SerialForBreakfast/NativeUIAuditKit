"""Run the fixed size/background diagnostic through qualified local TTR jobs."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import time

import numpy as np

import measure_native_focus253 as m

OUT = m.OUT/'controlled-r5'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tool():
    capture = load('native253_capture234', m.ROOT/'reports/work/FOCUS-RETENTION-234/run.py')
    capture.OUT = OUT
    capture.prior.OUT = OUT
    return capture


def matrix(recipe):
    entries = []
    for width in (260, 360):
        for background in ('dark', 'light'):
            current = copy.deepcopy(recipe)
            composition = current['appearance']['composition']
            asset = composition['asset_pack']['assets'][0]
            composition['asset_pack']['assets'] = [asset]
            for content in composition['contents'].values():
                content['asset'] = dict(sha256=asset['sha256'], fit='fill', anchor=[.5, .5])
            composition['definitions']['poster']['width'] = width
            color = 0x182838 if background == 'dark' else 0xE0E8F0
            composition['background']['colors'] = [color, color]
            entries.append(dict(id=f'w{width}-{background}', role='training',
                                group='owned-pilot183-development-training', recipe=current,
                                factors=dict(widthPoints=width, background=background)))
    return entries


def plan():
    if OUT.exists():
        raise ValueError('output_collision')
    prior = json.loads((m.OUT/'formula-r2/result.json').read_text())
    member = m.ROOT/'reports/work/TRANSITION-249/artifacts/package/membership.json'
    if hashlib.sha256(member.read_bytes()).hexdigest() != prior['membershipSHA256']:
        raise ValueError('changed_membership')
    from measure_native_focus253_mapping import select_rows, source_for
    row = next(r for r in select_rows(json.loads(member.read_text())['rows']) if r['group']=='234:recipe-03')
    _, _, info = source_for(row)
    source = m.ROOT/info['recipeSource']['path']
    recipe = json.loads(source.read_text())
    capture = tool()
    OUT.mkdir(); (OUT/'exports').mkdir()
    capture.prior.save(OUT/'campaign-v3.json', dict(target=capture.prior.TARGET,
        recipes=matrix(recipe), expectedPairs=16, source=info['recipeSource'],
        dataRole='development_training_diagnostic', independentEvaluation=False,
        outputCapBytes=512*1024**2))
    capture.prior.save(OUT/'runtime.json', dict(app=str(capture.prior.APP),
        helperSHA256=hashlib.sha256(capture.prior.HELPER.read_bytes()).hexdigest(),
        appSHA256=hashlib.sha256((capture.prior.APP/'Contents/MacOS/TVTestRig').read_bytes()).hexdigest()))
    print('Prepared 4 recipes and 16 expected pairs. No capture started.')


def capture():
    runner = tool()
    capacity = runner.prior.cli('capacity', ['fixture', 'job-capacity', '--required-slots', '4'])
    if not capacity['fixtureJobCapacity']['_0']['canPrepare']:
        raise ValueError('job_capacity')
    env = runner.prior.cli('env-before', ['fixture', 'env', '--fixture-url', 'http://127.0.0.1:8080'])
    profile = env['fixtureEnvironment']['_0']
    for key in ('is_voice_over_running', 'is_switch_control_running', 'is_reduce_motion_enabled',
                'is_darker_system_colors_status'):
        if profile.get(key) is not False:
            raise ValueError('changed_accessibility_profile:'+key)
    runner.capture()


def intake():
    checker = load('native253_intake233', m.ROOT/'reports/work/FOCUS-REPAIR-233/intake.py')
    checker.OUT = OUT
    checker.ID_PREFIX = 'native253-r5:'
    checker.main()


def background_contrast(dark, light):
    compatible = (dark[0].shape == light[0].shape and all(np.allclose(dark[3][k], light[3][k], atol=.01, rtol=0)
                  for k in ('before', 'after', 'visible')))
    if not compatible:
        return dict(comparableGeometry=False, reason='geometry_or_shape_mismatch')
    from measure_native_focus253_edges import rectangle
    support = dark[2] & light[2]
    box = dark[3]['before'].copy(); inset=.15*min(box[2:]);box[:2]+=inset;box[2:]-=2*inset
    rest = rectangle(support.shape, box)
    if min(rest.sum(), support.sum()) < 100:
        raise ValueError('contrast_support')
    return dict(comparableGeometry=True, focusedInterior=m.metrics(dark[1], light[1], support),
                restingInterior=m.metrics(dark[0], light[0], rest))


def archive():
    """Archive only this campaign's completed jobs after verifying exported originals."""
    checker = load('native253_intake_checks', m.ROOT/'reports/work/FOCUS-REPAIR-233/intake.py')
    report = json.loads((OUT/'intake.json').read_text())
    if report['review']['reviewed'] != 16 or len(report['samples']) != 32:
        raise ValueError('incomplete_intake')
    runner = tool()
    campaign = json.loads((OUT/'campaign-v3.json').read_text())
    for entry in campaign['recipes']:
        root = OUT/'exports'/entry['id']
        receipt = json.loads((root/'harvest-receipt.json').read_text())
        if receipt['outcome'] != 'completed' or receipt['acceptedRowCount'] != 4:
            raise ValueError('incomplete_export')
        for item in json.loads((root/'dataset-index.json').read_text())['artifacts']:
            raw = checker.h.read(root, item['path'])
            if len(raw) != item['byteCount'] or hashlib.sha256(raw).hexdigest() != item['sha256']:
                raise ValueError('changed_export')
        start = json.loads((OUT/(entry['id']+'-start.json')).read_text())['data']['fixtureJob']['_0']
        if start['simulatorUDID'] != campaign['target']:
            raise ValueError('target_changed')
        runner.prior.cli('archive-'+entry['id'], ['fixture', 'archive-job', start['jobID']])
    runner.prior.cli('capacity-after', ['fixture', 'job-capacity', '--required-slots', '8'])
    print('Archived 4 verified owned jobs. Exported originals remain intact.')


def analyze(result_name='analysis.json'):
    if result_name not in ('analysis.json', 'analysis-verified.json'):
        raise ValueError('result_name')
    destination = OUT/result_name
    if destination.exists():
        raise ValueError('output_collision')
    tick = time.monotonic()
    checked = json.loads((OUT/'intake.json').read_text())
    if checked['review']['reviewed'] != 16 or len(checked['samples']) != 32:
        raise ValueError('incomplete_intake')
    campaign = json.loads((OUT/'campaign-v3.json').read_text())
    prior = json.loads((m.OUT/'formula-r2/result.json').read_text())
    results, bank = [], {}
    for entry in campaign['recipes']:
        root = OUT/'exports'/entry['id']
        manifest = json.loads((root/'manifest.json').read_text())
        for item in manifest:
            path = root/item['metadata']['metadataPath']
            meta = json.loads(path.read_text())
            ref = dict(path=str(path.relative_to(m.ROOT)), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            row = dict(images=[dict(path=str((root/meta[k+'_png']).relative_to(m.ROOT)),
                                   sha256=meta[k+'_sha256']) for k in ('unfocused', 'focused')], metadata=[ref, ref])
            (before, after), center, mask, geometry, regions = m.prepare(row, regions=True)
            raw = m.warp(before, [geometry['scaleX'], geometry['scaleY'], *geometry['centerShift'], 1, 0], center)
            x, y = m.coordinates(mask.shape, center)
            highlighted = m.highlight(raw, x, y, prior['selectedParameters'])
            target = meta['focused_scene']['focused_element_id']
            key = (entry['factors']['widthPoints'], target)
            bank.setdefault(key, {})[entry['factors']['background']] = (before, after, mask, regions)
            results.append(dict(recipe=entry['id'], target=target, factors=entry['factors'],
                geometry=geometry, bounds={k: regions[k].tolist() for k in ('before','after','visible')},
                sourceImages=row['images'], sourceMetadata=ref, pixels=int(mask.sum()),
                unchanged=m.metrics(before, after, mask), scaleOnly=m.metrics(raw, after, mask),
                frozenHighlight=m.metrics(highlighted, after, mask)))
    contrasts = []
    for (width, target), values in bank.items():
        dark, light = values['dark'], values['light']
        contrast = dict(widthPoints=width, target=target, **background_contrast(dark, light))
        contrasts.append(contrast)
    summary = {entry['id']: {name: float(np.mean([r[name]['meanAbsolute255'] for r in results if r['recipe']==entry['id']]))
                            for name in ('unchanged','scaleOnly','frozenHighlight')} for entry in campaign['recipes']}
    report = dict(version=1, results=results, backgroundContrasts=contrasts, summary=summary,
        seconds=time.monotonic()-tick, trainingEligible=False, usesObservedGeometry=True,
        sourceSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        intakeSHA256=hashlib.sha256((OUT/'intake.json').read_bytes()).hexdigest(),
        priorSHA256=hashlib.sha256((m.OUT/'formula-r2/result.json').read_bytes()).hexdigest())
    tool().prior.save(destination, report)
    print(json.dumps(dict(summary=summary, backgroundContrasts=contrasts, seconds=report['seconds']), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['plan', 'capture', 'intake', 'analyze', 'archive'])
    parser.add_argument('--result-name', choices=['analysis.json', 'analysis-verified.json'], default='analysis.json')
    args = parser.parse_args()
    if args.mode == 'analyze':
        analyze(args.result_name)
    else:
        globals()[args.mode]()
