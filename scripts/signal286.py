"""Measure retained image changes without training or changing data roles."""
import argparse
from collections import defaultdict
from functools import lru_cache
import time
import numpy as np
from PIL import Image
import transition270 as base
import transition244 as geometry
from diagnose_signal95 import encoded

OUT = base.ROOT / 'reports/work/SIGNAL-286'


def measure(value, absolute_reference, mask):
    """Compare visible differences with differences before image reduction."""
    delta = np.abs(value[3:] - value[:3]).mean(axis=0)
    base.require(delta.shape == mask.shape == absolute_reference.shape, 'shape')
    base.require(mask.any() and (~mask).any(), 'region_support')
    base.require(np.isfinite(delta).all() and np.isfinite(absolute_reference).all(), 'finite')
    total = float(delta.sum())
    reference = float(absolute_reference.sum())
    inside = float(delta[mask].sum())
    return dict(meanDifference255=float(delta.mean()*255),
                retainedAbsoluteDifference=None if reference == 0 else total/reference,
                focusRegionFraction=None if total == 0 else inside/total,
                focusRegionAreaFraction=float(mask.mean()),
                insideMean255=float(delta[mask].mean()*255),
                outsideMean255=float(delta[~mask].mean()*255),
                identical=bool(total == 0))


def outcome(probability, label):
    decision = int(base.decisions(np.array([probability]))[0])
    return 'uncertain' if decision == -1 else 'correct' if decision == label else 'wrong'


def run():
    base.require(not (OUT/'result.json').exists(), 'output_collision')
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    manifest = base.worker.read_package(base.PACKAGE)
    membership = base.read(base.PACKAGE/'membership.json')
    prior = base.read(base.ROOT/'reports/work/TRANSITION-266/preflight.json')
    replacement = base.read(base.checked(prior['replacements']))
    admission = base.read(base.checked(prior['admission']))
    base.require(admission['approved'] and admission['role']=='development-training', 'admission')
    rx = np.load(base.checked(replacement['tensor']), allow_pickle=False)
    native = np.load(base.PACKAGE/'native.npy', mmap_mode='r', allow_pickle=False)
    selected = {index: position for position,index in enumerate(membership['selected'])}
    replaces = {r['nativeIndex']: (r,v) for r,v in zip(replacement['rows'],rx)}
    scores = {}
    pins = [base.ref(base.PACKAGE/'manifest.json'), prior['replacements'], prior['admission']]
    for name in ('DTM078','DTM079'):
        directory = base.ROOT/'reports/work/CONFLICT-281'/name
        result = base.read(directory/'result.json')
        evaluation = base.read(directory/'evaluation.json')
        base.checked(result['model'])
        scores[name] = (result['fit']['probabilities'],
                       evaluation['conditions']['native.npy']['probabilities'])
        pins.extend([base.ref(directory/'result.json'),base.ref(directory/'evaluation.json')])
    verified = set()

    def checked(ref):
        key = (ref['path'],ref['sha256'])
        if key not in verified:
            base.checked(ref); verified.add(key)
        return base.storage.resolve_input(base.ROOT/ref['path'])

    @lru_cache(maxsize=4)
    def pixels(path):
        with Image.open(path) as image:
            return image.convert('RGB')

    @lru_cache(maxsize=256)
    def metadata(path):
        return base.read(path)

    results = []
    for index, original in enumerate(membership['rows']):
        row,value = replaces.get(index,(original,native[index]))
        base.require(base.sha(value.tobytes()) == row['tensorSHA256'], 'tensor_identity')
        base.require(row['role']==original['role'] and row['changed']==original['changed'], 'role_or_label')
        images = [pixels(checked(ref)) for ref in row['images']]
        scenes = []
        for image,ref in zip(row['images'],row['metadata']):
            doc = metadata(checked(ref))
            matches = [doc[s] for e,s in [('unfocused','baseline_scene'),('focused','focused_scene')]
                       if doc[e+'_sha256']==image['sha256']]
            base.require(len(matches)>0,'frame_binding')
            scenes.append(matches[0])
        base.require(geometry.p.label(*scenes)==row['changed'], 'observed_label')
        x,transform = encoded(*images,(192,128))
        base.require(np.array_equal(x,value), 'production_encoding_parity')
        mask = np.zeros((128,192),bool)
        widths = []
        for scene in scenes:
            element = next(e for e in scene['elements'] if e['element_id']==scene['focused_element_id'])
            box = element['rendered_body_geometry']['visible_pixel_bounds']
            base.require(len(box)==4 and np.isfinite(box).all() and min(box[2:])>0,'body_bounds')
            mask |= geometry.rect(box,transform,(128,192),1.2)
            widths.append(min(box[2]*transform[0],box[3]*transform[1]))
        # Absolute differences precede resizing here. This measures cancellation, not semantic focus strength.
        raw = np.abs(np.asarray(images[0],np.float32)-np.asarray(images[1],np.float32)).mean(axis=2)/255
        sx,sy,px,py = transform
        rw,rh = round(images[0].width*sx),round(images[0].height*sy)
        reference = np.zeros((128,192),np.float32)
        reference[py:py+rh,px:px+rw] = np.asarray(Image.fromarray(raw).resize((rw,rh),Image.Resampling.BILINEAR))
        predictions = {}
        for name,(fit,ev) in scores.items():
            p = fit[len(membership['replayLabels'])+selected[index]] if index in selected else ev[index]
            predictions[name] = dict(probability=p,outcome=outcome(p,row['changed']))
        results.append(dict(id=row['id'],originalID=original['id'],group=row['group'],role=row['role'],
                            changed=row['changed'],conditions=row['conditions'],predictions=predictions,
                            minimumFocusedWidth=min(widths),**measure(value,reference,mask)))
        if (index+1)%100==0:
            print('Measured',index+1,'pairs',flush=True)
    buckets = defaultdict(list)
    for row in results:
        condition = 'content' if 'content_contrast' in row['conditions'] else 'other'
        key = (row['role'],condition,row['changed'],row['predictions']['DTM078']['outcome'])
        buckets[key].append(row)
    summaries = []
    for (role,condition,label,result),rows in sorted(buckets.items()):
        item = dict(role=role,condition=condition,changed=label,outcome=result,pairs=len(rows),
                    groups=len({r['group'] for r in rows}))
        for metric in ('retainedAbsoluteDifference','focusRegionFraction','focusRegionAreaFraction',
                       'insideMean255','outsideMean255','minimumFocusedWidth'):
            values = [r[metric] for r in rows if r[metric] is not None]
            item[metric] = None if not values else float(np.median(values))
        summaries.append(item)
    report = dict(version='signal286-v1',inputs=pins,runner=base.ref(__file_path()),rows=results,
                  summaries=summaries,seconds=time.monotonic()-started,verifiedFiles=len(verified),
                  boundsUse='Observed focus regions are diagnostic only. They never enter model prediction.',
                  limitations=['Pixel differences are not focus labels.',
                               'Region overlap does not prove semantic inseparability.',
                               'Related pairs are not independent trials.',
                               'Cached results and inspected groups are not untouched final evaluation.'],
                  productionEligible=False)
    base.write(OUT/'result.json',report)
    print('Complete:',len(results),'pairs;',round(report['seconds'],2),'s',flush=True)


def __file_path():
    from pathlib import Path
    return Path(__file__).resolve()


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--execute',action='store_true',required=True)
    parser.parse_args()
    run()
