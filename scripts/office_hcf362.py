"""Compare retained pixel evidence without inventing Office focus labels."""
import numpy as np
from PIL import Image
import research_queue as q
OUT = None


def change(a, b):
    q.require(a.shape == b.shape, 'dimensions')
    delta = np.abs(a.astype(np.float32)-b.astype(np.float32)).mean(axis=2)
    total=float(delta.sum())
    rows=[]
    for y,ys in enumerate(np.array_split(np.arange(delta.shape[0]),3)):
        for x,xs in enumerate(np.array_split(np.arange(delta.shape[1]),3)):
            rows.append(dict(region=y*3+x, fraction=None if total==0 else float(delta[np.ix_(ys,xs)].sum()/total)))
    return dict(meanAbsoluteDifference=float(delta.mean()), changedFraction=float((delta>0).mean()),
                strongChangeFraction=float((delta>32).mean()),regions=rows)


def run():
    config=q.load(OUT/'config.json')
    results=[]
    for pair in config['pairs']:
        images=[]
        for ref in pair['images']:
            path=q.local_path(q.ROOT,ref['path'])
            q.require(q.digest(path)==ref['sha256'],'image_changed')
            with Image.open(path) as image:
                image.load(); images.append(image.convert('RGB'))
        q.require(images[0].size==images[1].size,'pair_dimensions')
        results.append(dict(id=pair['id'], sourceDomain=pair['sourceDomain'],
            size=list(images[0].size), evidence=pair['images'],
            original=change(*[np.asarray(im) for im in images]),
            at1080=change(*[np.asarray(im.resize((1920,1080),Image.Resampling.BILINEAR)) for im in images])))
    q.save(OUT/'summary.json',dict(pairs=results, trainingEligible=False, modelAccepted=False,
        officeGroups=1, matchingScenes=False, osProfileEquivalent=None, accuracy=None,
        decision='Use native Simulator data for controlled training. Measure Office transfer separately after label review.',
        limitations=['Different scene content prevents a causal Simulator versus device comparison.',
            'Pixel differences do not identify focus. Office per-frame HCF receipts and body bounds remain unavailable.',
            'The Office journey remains inspected development evidence.']))
