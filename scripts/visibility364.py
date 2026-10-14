"""Check whether notification overlays hide the annotated focus cue."""
import numpy as np
from PIL import Image
import research_queue as q
from research_campaign340 import pin

OUT = None
OVERLAYS = {'banner': (550, 40, 820, 90), 'toast': (1560, 80, 280, 72)}


def overlap(box, cover):
    x, y, w, h = box; a, b, c, d = cover
    return max(0, min(x+w, a+c)-max(x, a))*max(0, min(y+h, b+d)-max(y, b))/(w*h)


def run():
    cfg = q.load(OUT/'config.json')
    for ref in cfg['inputs']:
        q.require(q.digest(q.ROOT/ref['path']) == ref['sha256'], 'input_changed')
    reports = []
    for dependency in q.load(OUT/'dependencies.json'):
        ref = next(r for r in dependency['outputs'] if r['path'].endswith('/corpus.json'))
        doc = q.load(q.ROOT/ref['path']); by_image = {f['image']['path']: f for f in doc['frames']}
        arrays = {}
        for row in doc['rows']:
            if row['changed'] != 1:
                continue
            boxes = []; variant = row['condition'].removesuffix('-movement')
            for image in row['images']:
                q.require(q.digest(q.ROOT/image['path']) == image['sha256'], 'image_changed')
                frame = by_image[image['path']]; annotation = frame['annotation']
                q.require(q.digest(q.ROOT/annotation['path']) == annotation['sha256'], 'annotation_changed')
                nodes = q.load(q.ROOT/annotation['path'])['nodes']
                boxes.append(next(n['focusedBounds'] for n in nodes if n['isFocused']))
                if image['path'] not in arrays:
                    with Image.open(q.ROOT/image['path']) as decoded:
                        arrays[image['path']] = np.asarray(decoded.convert('RGB'), dtype=np.int16)
            delta = np.abs(arrays[row['images'][1]['path']]-arrays[row['images'][0]['path']])
            mask = np.zeros(delta.shape[:2], dtype=bool)
            for x, y, w, h in boxes:
                x0,y0=max(0,int(x)-8),max(0,int(y)-8)
                x1,y1=min(mask.shape[1],int(np.ceil(x+w))+8),min(mask.shape[0],int(np.ceil(y+h))+8)
                mask[y0:y1,x0:x1] = True
            covered = [overlap(box, OVERLAYS[variant]) if variant in OVERLAYS else 0. for box in boxes]
            reports.append(dict(case=row['id'], group=row['group'], condition=row['condition'], layout=row['layout'],
                boxCoveredFraction=covered, localMeanDifference=float(delta[mask].mean()),
                localChangedPixels=int(np.any(delta>1,axis=2)[mask].sum()),
                visibility='covered-control' if max(covered)>.9 else 'not-fully-covered', corpus=ref))
        del arrays
    q.save(OUT/'visibility.json',dict(version='focus364-visibility-v1',rows=reports,modelAccepted=False,
        nextAction='Keep covered controls in an interruption test. Do not treat them as ordinary visible-focus training failures.',
        limitation='Overlay rectangles come from the pinned renderer. Coverage does not measure exact remaining perceptual visibility.'))


def register():
    graph=q.load(q.ROOT/'Research/ResearchSpecs/FOCUS364-r2/graph.json')
    producers=[n for n in graph['nodes'] if n['kind']=='producer' and n['job']!='focus364-00-renderer']
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS364-r2'; ident='focus364-r2-91-visibility'
    refs=[pin(q.ROOT/'scripts/visibility364.py'),pin(q.ROOT/'reports/work/FOCUS364/render-headless-screen.swift')]
    cfg=folder/(ident+'-config.json');q.save(cfg,dict(inputs=refs))
    spec=dict(version=q.SPEC_VERSION,id=ident,task='FOCUS364',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
        hypothesis='Do notification overlays hide the focus cue in the missed movement cases?',
        decisionRule='Measure box coverage and local pixel changes. Separate hidden controls from visible-cue training failures.',
        inputs=refs,stage=[{'from':pin(cfg),'to':'config.json'}],
        dependencies=[dict(job=n['job'],specSHA256=n['specSHA256'],outputs=['corpus.json','qualification.json']) for n in producers],
        conditions=[dict(job=n['job'],output='qualification.json',outcome='supported') for n in producers],
        adapter=dict(type='python-callable',steps=['visibility364.run'],outputAttributes=['visibility364.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    path=folder/(ident+'.json');q.save(path,spec);q.submit(path)
    graph.update(id='FOCUS364-r3',supersedes='FOCUS364-r2',reason='Add a visibility check after all models miss movement beneath the banner.')
    graph['nodes'].append(dict(job=ident,specSHA256=q.text_digest(spec),kind='experiment',question=spec['hypothesis']))
    import research_graph
    graph['budget']=research_graph.validate_graph(graph)
    q.save(folder/'graph-r3.json',graph)
    print(ident,q.text_digest(spec))


if __name__=='__main__':register()
