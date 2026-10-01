"""Controlled emphasis and native aspect-fit tests; no production default change."""
import argparse
import base64
import copy
import io
import math
import time

import human_annotation_review as h
import focus_artwork_experiment as artwork
import focus_context_experiment as context
import focus_visual_experiment as visual

VERSION = 'focus-transfer-experiment-v1'
ARMS = {'transfer-emphasis-partial': 'fdr033-emphasis',
        'transfer-aspect-partial': 'fdr034-aspect'}
ROOT = 'reports/work/FOCUS-TRANSFER-10'
PARENT = 'reports/work/FOCUS-CAMPAIGN-09/artifacts/protocol/artwork-added-partial/protocol.json'
AUTHORITY = 'Research/Plans/FocusTransfer10.md'
CODE = artwork.CODE + ['focus_transfer_experiment.py', 'focus_runtime.py']


def parent():
    p = context.sealed(h.ref(h.ROOT/PARENT))
    doc, base = artwork.admission(p['admission'])
    expected = artwork.expected(doc, base, 'artwork-added-partial')
    h.require(all(p[k] == v for k, v in expected.items()), 'transfer_parent_changed')
    return p, doc


def emphasis(rows, weights, targets, factor=10):
    from focus_appearance_experiment import FIXTURE_KINDS
    h.require(type(factor) in (int, float) and math.isfinite(factor) and factor >= 1,
              'transfer_invalid_factor')
    train = [r for r in rows if r['split'] == 'train']
    h.require(len({r['id'] for r in rows}) == len(rows) and
              set(weights) == {r['id'] for r in train} and
              all(math.isfinite(w) and w > 0 for w in weights.values()) and
              math.isclose(math.fsum(weights.values()), 1), 'transfer_invalid_weights')
    fixture = [r for r in train if r['use'] == 'train-candidate'
               and r.get('sourceKind') in FIXTURE_KINDS]
    h.require(targets and set(targets) <= {r['id'] for r in fixture}, 'transfer_invalid_targets')
    if factor == 1:
        return dict(weights)
    result = dict(weights)
    for label in (0, 1):
        ids = [r['id'] for r in fixture if r['label'] == label]
        mass = math.fsum(weights[i] for i in ids)
        proposed = {i: weights[i]*(factor if i in targets else 1) for i in ids}
        total = math.fsum(proposed.values())
        h.require(total > 0, 'transfer_missing_label')
        result.update({i: mass*w/total for i, w in proposed.items()})
    h.require(math.isclose(math.fsum(result.values()), 1), 'transfer_weight_mass')
    return result


def geometry(p):
    from PIL import Image
    old = context.sealed(h.ref(h.ROOT/'reports/work/FOCUS-VISUAL-05/artifacts/protocol-v2/protocol.json'))
    inputs = context.read(old['inputs'])
    records = {r['id']: r for r in inputs['records']}
    answer = []
    for r in p['samples']:
        if r['id'] in records:
            g = records[r['id']]
        else:
            with Image.open(h.checked(h.ROOT, r['frame'])) as im:
                size = list(im.size)
            g = dict(original=r['frame'], bounds=r['bounds'], sourceSize=size)
        h.checked(h.ROOT, g['original'])
        answer.append(dict(id=r['id'], original=g['original'], bounds=g['bounds'],
                           sourceSize=g['sourceSize'], production=r['crop']))
    return answer


def render(output):
    import numpy as np
    from PIL import Image
    import focus_runtime as runtime
    p, _ = parent(); records = geometry(p)
    before = runtime.identity(); started = time.monotonic()
    out = h.fresh(output); out.mkdir(parents=True)
    by_id = {r['id']: r for r in records}
    items = [dict(id=r['id'], path=str(h.ROOT/r['original']['path']),
                  sha256=r['original']['sha256'], bounds=r['bounds']) for r in records]
    results = []
    # Replay every retained production crop, not just a convenient sample.
    for batch in runtime.bounded_batches(items):
        production = runtime.invoke(batch)['results']
        for r in production:
            with Image.open(io.BytesIO(base64.b64decode(r['png'], validate=True))) as im:
                actual = np.array(im.convert('RGB'))
            with Image.open(h.checked(h.ROOT, by_id[r['id']]['production'])) as im:
                expected = np.array(im.convert('RGB'))
            h.require(actual.shape == (256, 256, 3) and np.array_equal(actual, expected),
                      'transfer_production_pixel_mismatch:' + r['id'])
        for r in runtime.invoke(batch, experimental_aspect_fit=True)['results']:
            raw = base64.b64decode(r['png'], validate=True)
            with Image.open(io.BytesIO(raw)) as im:
                h.require(im.size == (256, 256), 'transfer_aspect_size')
            path = out/(h.digest(r['id'])+'.png')
            with path.open('xb') as stream: stream.write(raw)
            results.append(dict(by_id[r['id']], aspect=h.ref(path)))
        print(f'Replayed and rendered {len(results)}/{len(records)}', flush=True)
    h.require(runtime.identity() == before, 'transfer_renderer_changed')
    receipt = dict(version='focus-transfer-render-v1', parent=h.ref(h.ROOT/PARENT),
                   records=results, productionPixelsExact=len(results), runtime=before,
                   transform='native-makeCrop-16percent-aspect-fit-black-256',
                   elapsedSeconds=time.monotonic()-started)
    h.write(out/'receipt.json', receipt)


def encode(render_path, output):
    import torch
    import numpy as np
    from PIL import Image
    from focus_pretrained_experiment import state_digest
    import focus_runtime as runtime
    p, _ = parent(); rr = h.ref(h.local(render_path)); rendered = context.read(rr)
    h.require(rendered['parent'] == h.ref(h.ROOT/PARENT) and
              rendered['runtime'] == runtime.identity() and
              rendered['productionPixelsExact'] == len(p['samples']) and
              [r['id'] for r in rendered['records']] == [r['id'] for r in p['samples']],
              'transfer_render_membership')
    h.require(torch.backends.mps.is_available(), 'transfer_requires_mps')
    started = time.monotonic()
    prefix = visual.make_network(p['representation']).features[:9].eval().to('mps')
    before = state_digest(prefix)
    h.require(before == context.read(p['features']['receipt'])['prefixSHA256'], 'transfer_prefix_changed')
    norm = p['representation']['normalization']
    mean = torch.tensor(norm['mean'], device='mps')[None,:,None,None]
    std = torch.tensor(norm['std'], device='mps')[None,:,None,None]
    values = []
    for start in range(0, len(rendered['records']), 32):
        h.require(time.monotonic()-started < 300, 'transfer_encoding_deadline')
        images = []
        for row in rendered['records'][start:start+32]:
            with Image.open(h.checked(h.ROOT, row['aspect'])) as im:
                h.require(im.size == (256,256), 'transfer_crop_size')
                images.append(torch.from_numpy(np.array(im.convert('RGB'),copy=True)).permute(2,0,1))
        x = torch.stack(images).to('mps').float()/255
        with torch.no_grad(): f = prefix((x-mean)/std).cpu()
        local = torch.cat((f, torch.ones(len(images),1,16,16)),1)
        values.append(torch.stack((local,torch.zeros_like(local)),1))
    x = torch.cat(values)
    h.require(state_digest(prefix) == before and bool(torch.isfinite(x).all()) and
              time.monotonic()-started < 300 and x.numel()*4 < 512*1024**2, 'transfer_encoding_budget')
    receipt = dict(version='focus-transfer-prefix-v1', render=rr,
                   ids=[r['id'] for r in p['samples']], prefixSHA256=before,
                   featureSHA256=context.tensor_digest(x), shape=list(x.shape),
                   prefixUnchanged=True, elapsedSeconds=time.monotonic()-started,
                   disabledContext='zero; detail-only arm')
    out=h.fresh(output); out.mkdir(parents=True)
    torch.save(dict(features=x,receipt=receipt),out/'prefix.pt')
    h.write(out/'receipt.json',receipt)
    h.write(out/'references.json',dict(cache=h.ref(out/'prefix.pt'),receipt=h.ref(out/'receipt.json')))
    print(f'Encoded {len(x)} aspect-fit crops in {receipt["elapsedSeconds"]:.2f}s',flush=True)


def expected(p, doc, arm):
    e = {k:copy.deepcopy(p[k]) for k in ('samples','configuration','fullFit','counts',
                                        'representation','selection','unmetQualificationBlockers')}
    if arm == 'transfer-emphasis-partial':
        e['fullFit']['weights'] = emphasis(p['samples'],p['fullFit']['weights'],
                                          {r['id'] for r in doc['additions']})
    return e


def runtime():
    return dict(code=[h.ref(h.ROOT/'scripts'/n) for n in CODE], packages=visual.packages())


def approval(p):
    return dict(version='focus-transfer-approval-v1', protocolSHA256=p['protocolSHA256'],
                authority=p['authority'], arm=p['arm'], name=ARMS[p['arm']], scope='training-no-export')


def validate_features(p, base):
    receipt=context.read(p['features']['receipt'])
    h.checked(h.ROOT,p['features']['cache'],limit=512*1024**2)
    h.require(receipt['ids']==[r['id'] for r in p['samples']] and
              receipt['prefixSHA256']==context.read(base['features']['receipt'])['prefixSHA256'],
              'transfer_cache_membership')
    if p['arm']=='transfer-emphasis-partial':
        h.require(p['features']==base['features'], 'transfer_emphasis_input_changed')
    else:
        import focus_runtime as native_runtime
        r=context.read(receipt['render'])
        h.require(receipt['version']=='focus-transfer-prefix-v1' and
                  r['runtime']==native_runtime.identity() and r['parent']==p['parent'] and
                  r['productionPixelsExact']==1895 and
                  r['transform']=='native-makeCrop-16percent-aspect-fit-black-256' and
                  [g['id'] for g in r['records']]==receipt['ids'], 'transfer_aspect_provenance')


def protocol(cache, output):
    base,doc=parent(); features=h.read(h.local(cache))
    out=h.fresh(output);out.mkdir(parents=True)
    for arm in ARMS:
        p=dict(version=VERSION,arm=arm,parent=h.ref(h.ROOT/PARENT),authority=h.ref(h.ROOT/AUTHORITY),
               runtime=runtime(),features=base['features'] if arm=='transfer-emphasis-partial' else features,
               releaseEligible=False,**expected(base,doc,arm))
        validate_features(p,base)
        p['protocolSHA256']=h.digest(p); dest=out/arm;dest.mkdir()
        h.write(dest/'protocol.json',p);h.write(dest/'approval.json',approval(p))
        print(arm,p['protocolSHA256'],flush=True)


def load_protocol(path, arm, run_name, approval_path=None):
    ref=h.ref(h.local(path));p=context.sealed(ref);base,doc=parent()
    h.require(p['version']==VERSION and p['arm']==arm and ARMS.get(arm)==run_name,
              'transfer_arm_binding')
    h.require(p['parent']==h.ref(h.ROOT/PARENT) and p['authority']==h.ref(h.ROOT/AUTHORITY)
              and p['runtime']==runtime() and all(p[k]==v for k,v in expected(base,doc,arm).items()),
              'transfer_configuration_changed')
    validate_features(p,base)
    out=h.ROOT/'NativeUITrainer/focus_ring_runs'/run_name
    h.require(not out.exists() and not any(x.is_symlink() for x in (out,*out.parents)), 'output_collision')
    ar=h.ref(h.local(approval_path)) if approval_path else None
    if ar: h.require(context.read(ar)==approval(p), 'transfer_approval_binding')
    report=dict(protocolVersion=VERSION,protocolFile=ref,approval=ar,arm=arm,visualTraining=True,
        features=p['features'],warmCheckpoint=None,configurationValid=True,executionAuthorized=False,
        releaseEligible=False,launchEligible=ar is not None,blockers=[] if ar else ['missing_transfer_approval'],
        **{k:p[k] for k in ('configuration','fullFit','representation','selection','counts','runtime',
                            'protocolSHA256','unmetQualificationBlockers')})
    return report,[dict(r,path=h.ROOT/r['crop']['path']) for r in p['samples']]


prepare_features = artwork.prepare_features


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['render','encode','protocol'])
    parser.add_argument('--render');parser.add_argument('--cache');parser.add_argument('--output',required=True)
    args=parser.parse_args()
    if args.mode=='render':render(args.output)
    elif args.mode=='encode':encode(args.render,args.output)
    else:protocol(args.cache,args.output)


if __name__=='__main__':main()
