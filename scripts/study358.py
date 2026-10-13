"""Measure retained study inputs. Do not change labels or model decisions."""
import numpy as np
from PIL import Image
import research_queue as q
OUT = None


def pixels(a, b):
    q.require(a.shape == b.shape and a.size > 0, 'image_shape')
    delta = np.abs(a.astype(np.float32) - b.astype(np.float32))
    mask = np.any(delta != 0, axis=2)
    yy, xx = np.where(mask)
    return dict(meanAbsoluteDifference=float(delta.mean()), changedPixels=int(mask.sum()),
        pixels=int(mask.size), changeBounds=None if not len(xx) else
        [int(xx.min()), int(yy.min()), int(xx.max()+1), int(yy.max()+1)])


def trend(history):
    q.require(len(history) >= 4, 'history_support')
    values = np.asarray([r['loss'] for r in history], dtype=float)
    q.require(np.isfinite(values).all(), 'invalid_loss')
    slope = float(np.polyfit(np.arange(4), values[-4:], 1)[0])
    return dict(epochs=len(values), bestEpoch=int(values.argmin()+1), lastLoss=float(values[-1]),
        bestLoss=float(values.min()), lastFourSlope=slope,
        continuationSignal=bool(slope < 0 and values[-1] <= values.min()*1.05),
        limitation='Training loss alone cannot approve continuation or establish reserved accuracy.')


def profiles(c):
    paths = [q.ROOT / r['path'] for r in c['images']]
    rows = []
    with Image.open(paths[0]) as left, Image.open(paths[1]) as right:
        q.require(left.size == right.size, 'image_dimensions')
        for width in (left.width, 384, 192):
            size = (width, round(width*left.height/left.width))
            a = np.asarray(left.convert('RGB').resize(size, Image.Resampling.BILINEAR))
            b = np.asarray(right.convert('RGB').resize(size, Image.Resampling.BILINEAR))
            rows.append(dict(size=list(size), **pixels(a, b)))
    return dict(comparison=c['comparison'], rows=rows, trainingEligible=False,
        limitation='Focus-arrival differences are not HCF benefit. Standard counterparts establish that separate comparison.')


def separation(c):
    rows = []
    for ref in c['reports']:
        d = q.load(q.ROOT/ref['path'])
        for i, row in enumerate(d['rows']):
            rows.append(dict(case=row['id'], changed=row['changed'], values={
                name: dict(context=v['context'][i], detail=v['correction'][i]) for name,v in d['models'].items()}))
    models = {}
    for name in rows[0]['values']:
        values = {}
        for feature in ('context', 'detail'):
            positive = [r['values'][name][feature] for r in rows if r['changed']]
            negative = [r['values'][name][feature] for r in rows if not r['changed']]
            values[feature] = dict(positiveRange=[min(positive),max(positive)],
                negativeRange=[min(negative),max(negative)],
                positiveHighThresholdGap=min(positive)-max(negative),
                positiveLowThresholdGap=min(negative)-max(positive))
        models[name] = values
    return dict(models=models, rows=rows, relatedGroupCount=1, thresholdsChanged=False,
        limitation='Range overlap tests scalar thresholds only. It does not rule out nonlinear or combined features.')


def run():
    c = q.load(OUT/'config.json')
    for ref in c['inputs']:
        q.require(q.digest(q.ROOT/ref['path']) == ref['sha256'], 'input_changed')
    if c['mode'] == 'profiles':
        result = profiles(c)
    elif c['mode'] == 'separation':
        result = separation(c)
    elif c['mode'] == 'convergence':
        result = dict(runs=[dict(input=ref, **trend(q.load(q.ROOT/ref['path'])['history'])) for ref in c['reports']],
            decision='Review trends with existing regression failures before any longer run.')
    elif c['mode'] == 'storage':
        sizes = [r['bytes'] for r in c['images']]
        per_frame = max(sizes)
        result = dict(sampleFiles=len(sizes), maximumCompressedBytes=per_frame,
            stages=[dict(hcfFrames=n, matchedProfileFrames=n*2,
                imageBytesAtSampleMaximum=n*2*per_frame,
                exceedsStudyCeiling=n*2*per_frame > 250*(1<<30)) for n in (1000,5000,20000,50000)],
            limitation='Sample maxima are estimates, not upper bounds. Add labels, derived files, checkpoints, and temporary space before reservation.')
    else:
        raise ValueError('unsupported_study_mode')
    q.save(OUT/'summary.json',dict(**result,modelAccepted=False))


def blocked():
    raise ValueError('Study stage needs qualified inputs and an executable successor. Do not remove its requirements.')
