"""Compare fixed transition models with aligned image-selected regions."""
import argparse
import math
from pathlib import Path
import time
import numpy as np
from PIL import Image
import condition291 as c
from diagnose_signal95 import encoded
from report_spatial297 import counts, decision

base = c.base
OUT = base.ROOT/'reports/work/FOCUS-307'
OLD = base.ROOT/'reports/work/TRANSITION-297'
SMALL = base.ROOT/'reports/work/FOCUS-302/capture-r2/analysis'


def windows(regions):
    """Select at most 4 regions by area without reading labels."""
    for box in regions:
        base.require(len(box) == 4 and np.isfinite(box).all() and min(box[2:]) > 0, 'invalid_region')
    selected = sorted(regions, key=lambda b: (-b[2]*b[3], *b))[:4]
    result = []
    for x, y, w, h in selected:
        width, height = max(32, 2*w), max(32, 2*h)
        result.append([max(0, x+w/2-width/2), max(0, y+h/2-height/2),
                       min(192, x+w/2+width/2), min(128, y+h/2+height/2)])
    return result


def source_window(box, size):
    w, h = size
    scale = min(192/w, 128/h)
    rw, rh = max(1, round(w*scale)), max(1, round(h*scale))
    px, py = (192-rw)//2, (128-rh)//2
    x0, y0, x1, y1 = box
    result = (max(0, math.floor((x0-px)*w/rw)), max(0, math.floor((y0-py)*h/rh)),
              min(w, math.ceil((x1-px)*w/rw)), min(h, math.ceil((y1-py)*h/rh)))
    base.require(result[2] > result[0] and result[3] > result[1], 'empty_region')
    return result


def crop_pair(images, box, preserve_padding=False):
    base.require(images[0].size == images[1].size, 'size_mismatch')
    if preserve_padding:
        # Keep the complete encoded window, including padding outside the source image.
        x0,y0,x1,y1=box;w,h=images[0].size
        base.require(x1>x0 and y1>y0,'empty_region')
        scale=min(192/w,128/h);rw,rh=max(1,round(w*scale)),max(1,round(h*scale))
        px,py=(192-rw)//2,(128-rh)//2
        target_scale=min(192/(x1-x0),128/(y1-y0))
        tw,th=round((x1-x0)*target_scale),round((y1-y0)*target_scale)
        affine=((x1-x0)*w/rw/tw,0,(x0-px)*w/rw,
                0,(y1-y0)*h/rh/th,(y0-py)*h/rh)
        parts=[]
        for image in images:
            crop=image.transform((tw,th),Image.Transform.AFFINE,affine,
                                 resample=Image.Resampling.BILINEAR,fillcolor=(0,0,0))
            canvas=Image.new('RGB',(192,128));canvas.paste(crop,((192-tw)//2,(128-th)//2))
            parts.append(np.asarray(canvas,dtype=np.float32).transpose(2,0,1)/255)
        return np.concatenate(parts)
    region = source_window(box, images[0].size)
    return encoded(*(image.crop(region) for image in images), (192, 128))[0]


def tensor_images(value):
    return [Image.fromarray(np.rint(value[j:j+3].transpose(1, 2, 0)*255).clip(0, 255).astype(np.uint8))
            for j in (0, 3)]


def aggregate(probabilities, fallback):
    # Empty proposals retain the original model decision. They do not prove unchanged focus.
    values = list(probabilities) or [fallback]
    base.require(np.isfinite(values).all() and all(0 <= p <= 1 for p in values), 'invalid_score')
    return float(max(values))


def summarize(rows):
    summaries = []
    for dataset, role in sorted({(r['set'], r['role']) for r in rows}):
        selected = [r for r in rows if (r['set'], r['role']) == (dataset, role)]
        for model in rows[0]['scores']:
            for mode in ('whole', 'enlarged', 'source'):
                original = [decision(r['scores'][model]['whole']) for r in selected]
                actual = [decision(r['scores'][model][mode]) for r in selected]
                truth = [r['changed'] for r in selected]
                summaries.append(dict(set=dataset, role=role, model=model, mode=mode,
                    metrics=counts(truth, actual),
                    gains=sum(a != y and b == y for a, b, y in zip(original, actual, truth)),
                    losses=sum(a == y and b != y for a, b, y in zip(original, actual, truth))))
    return summaries


def run(out):
    base.require(not out.exists(), 'output_collision')
    started = time.monotonic()
    prior = base.read(OLD/'registration.json')
    membership = base.read(base.checked(prior['membership']))
    base.worker.read_package(base.PACKAGE)
    native = np.load(base.PACKAGE/'native.npy', mmap_mode='r', allow_pickle=False)
    old_rows = base.read(OLD/'result.json')['rows']
    proposals = base.read(OLD/'proposals.json')['results']
    small = base.read(SMALL/'evaluation.json')
    small_proposals = base.read(SMALL/'proposals.json')['results']
    base.require(len(old_rows) == len(proposals) == 1318, 'retained_count')
    base.require([p['id'] for p in proposals] == [str(i) for i in range(len(old_rows))], 'proposal_order')
    base.require([r['id'] for r in small['rows']] == [p['id'] for p in small_proposals], 'small_order')
    out.mkdir(parents=True)
    models = {name: base.checked(pin['model']) for name, pin in prior['models'].items()}
    base.write(out/'registration.json', dict(version='detail307-v1', runner=base.ref(Path(__file__)),
        inputs=[base.ref(p) for p in (OLD/'registration.json', OLD/'result.json', OLD/'proposals.json',
            SMALL/'evaluation.json', SMALL/'proposals.json')], models=prior['models'],
        membership=prior['membership'], thresholds=[.15, .85], maxRegions=4, expansion=2,
        minimumWindow=[32, 32], selection='area_then_coordinates', aggregation='maximum_or_original',
        inputSize=[192, 128], threads=2, outputCapBytes=64*1024**2, training=False,
        hypothesis='Original image regions recover detail that enlargement of encoded frames cannot recover.',
        acceptance='More tiny-control successes without losses on retained conditions. No production decision.',
        rolesChanged=False, finalAudit=False, sourceForAuthored='Only encoded frames exist; source equals enlargement.'))
    base.torch.set_num_threads(2)
    nets = {name: c.model.load_candidate(path) for name, path in models.items()}
    arrays = {name: np.load(base.PACKAGE/name, mmap_mode='r', allow_pickle=False)
              for name in ('left8.npy', 'center8.npy', 'global8.npy')}
    indices = {row['id']: i for i, row in enumerate(membership['rows'])}
    verified = set()

    def checked(ref):
        key = (ref['path'], ref['sha256'])
        if key not in verified:
            base.checked(ref); verified.add(key)
        return base.storage.resolve_input(base.ROOT/ref['path'])

    def image(ref):
        with Image.open(checked(ref)) as opened:
            return opened.convert('RGB')

    def cases():
        for i, (row, proposal) in enumerate(zip(old_rows, proposals)):
            if row['set'] == 'native.npy':
                n = indices[row['id']]; source = membership['rows'][n]
                value = np.array(native[n])
                base.require(base.sha(value.tobytes()) == source['tensorSHA256'], 'tensor_identity')
                images = [image(ref) for ref in source['images']]
                base.require(np.array_equal(encoded(*images, (192, 128))[0], value), 'source_encoding_parity')
            else:
                n = int(row['id'].rsplit(':', 1)[1]); value = np.array(arrays[row['set']][n])
                images = tensor_images(value)
            yield row, proposal, value, images, {k: v['original'] for k, v in row['models'].items()}
        for row, proposal in zip(small['rows'], small_proposals):
            path = checked(row['metadata']); meta = base.read(path)
            images = [image(dict(path=str((path.parent/meta[p+'_png']).relative_to(base.ROOT)),
                                sha256=meta[p+'_sha256'])) for p in ('unfocused', 'focused')]
            mode = row['condition']
            if mode == 'reverse': images.reverse()
            if mode == 'same-before': images[1] = images[0]
            if mode == 'same-after': images[0] = images[1]
            value, _ = encoded(*images, (192, 128))
            yield dict(row, set='tiny-'+mode), proposal, value, images, row['scores']

    records = []
    for row, proposal, value, images, originals in cases():
        boxes = windows(proposal['regions'])
        low = tensor_images(value)
        tensors = [crop_pair(low, box) for box in boxes] + [crop_pair(images, box) for box in boxes]
        record = {k: row.get(k) for k in ('id', 'set', 'role', 'group', 'changed', 'conditions')}
        record.update(windows=boxes, proposedRegions=len(proposal['regions']), scores={})
        for name, net in nets.items():
            scores = base.worker.score(net, np.stack(tensors)).tolist() if tensors else []
            record['scores'][name] = dict(whole=originals[name],
                enlarged=aggregate(scores[:len(boxes)], originals[name]),
                source=aggregate(scores[len(boxes):], originals[name]))
        records.append(record)
        if len(records) % 100 == 0: print('Scored', len(records), flush=True)
    base.require(len(records) == 1334, 'total_count')
    base.write(out/'result.json', dict(version='detail307-v1', rows=records, summaries=summarize(records),
        elapsedSeconds=time.monotonic()-started, productionEligible=False, rolesChanged=False,
        limitation='Pair-level diagnostic with changed preprocessing. Region labels are not inferred from pair labels.'))
    base.write(out/'completion.json', dict(rows=len(records), result=base.ref(out/'result.json'),
        outputBytes=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())))
    base.require(sum(p.stat().st_size for p in out.rglob('*') if p.is_file()) < 64*1024**2, 'output_budget')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', required=True, action='store_true')
    parser.add_argument('--output', type=Path, default=OUT)
    args = parser.parse_args()
    base.require(args.output.resolve().is_relative_to(base.ROOT) and args.output.resolve() != base.ROOT, 'output_boundary')
    run(args.output)
