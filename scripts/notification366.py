"""Queue fresh notification examples and preserve retained movement decisions."""
import hashlib
import time
from pathlib import Path
import numpy as np
from PIL import Image
import graph364 as g

q = g.q
OUT = None


def checked(ref):
    path = q.local_path(q.ROOT, ref['path'])
    q.require(q.digest(path) == ref['sha256'], 'changed_input:' + ref['path'])
    return path


def outputs(name):
    refs = []
    for dep in q.load(OUT/'dependencies.json'):
        checked(dep['result'])
        for ref in dep['outputs']:
            checked(ref)
            if ref['path'].endswith('/' + name):
                refs.append(ref)
    return refs


def build():
    g.OUT = OUT
    cfg = g.config()
    source = checked(cfg['source']).read_text()
    for old, new in cfg['replacements']:
        q.require(source.count(old) == 1, 'source_replacement:' + old)
        source = source.replace(old, new)
    # This derived source belongs to NUIAK. The TTR checkout stays unchanged.
    path = OUT/'renderer.swift'
    path.write_text(source)
    cfg['source'] = g.pin(path)
    cfg['inputs'].append(cfg['source'])
    q.save(OUT/'config.json', cfg, replace=True)
    g.build()


def produce():
    g.OUT = OUT
    g.produce()
    doc = q.load(OUT/'corpus.json')
    doc.update(role='training-candidate', trainingEligible=False,
               independentGroups=None, admissionRequired=True)
    for row in doc['rows']:
        row['role'] = 'training-candidate'
    q.save(OUT/'corpus.json', doc, replace=True)
    q.save(OUT/'qualification.json', dict(version='research-condition-v1', outcome='supported',
        reason='Fresh authored pairs pass geometry checks. Training still requires the separate admission check.',
        evidence=[g.pin(OUT/'corpus.json')]), replace=True)


def pixels(ref):
    with Image.open(checked(ref)) as image:
        rgb = image.convert('RGB')
        return hashlib.sha256(str(rgb.size).encode() + rgb.tobytes()).hexdigest()


def admit_rows(corpora, forbidden, fingerprint=pixels):
    rows = []; ids = set(); cache = {}
    for doc in corpora:
        q.require(doc.get('role') == 'training-candidate' and not doc['trainingEligible'], 'candidate_role')
        q.require(doc['sourceDomain'] == 'authored-headless', 'candidate_domain')
        for row in doc['rows']:
            q.require(row['role'] == 'training-candidate' and row['changed'] in (0, 1), 'candidate_label')
            q.require(row['id'] not in ids, 'duplicate_case'); ids.add(row['id'])
            for ref in row['images']:
                key = (ref['path'], ref['sha256'])
                if key not in cache:
                    cache[key] = fingerprint(ref)
                q.require(cache[key] not in forbidden, 'development_pixel_overlap')
            rows.append(dict(row, role='train'))
    q.require(rows and any(r['condition'] == 'dim-movement' for r in rows), 'missing_dim_movement')
    return rows, cache


def admission():
    g.OUT = OUT; cfg = g.config()
    dev = [q.load(checked(ref)) for ref in cfg['development']]
    q.require(sum(len(d['rows']) for d in dev) == 392, 'development_membership')
    refs = {r['path']: r for d in dev for row in d['rows'] for r in row['images']}
    forbidden = {pixels(ref) for ref in refs.values()}
    sources = outputs('corpus.json')
    q.require(len(sources) == 9, 'producer_count')
    rows, cache = admit_rows([q.load(checked(ref)) for ref in sources], forbidden)
    q.require(len(rows) == 252, 'training_membership')
    # The selected targets are outside both authored notification rectangles.
    # These rectangles come from the pinned renderer and its previous visibility audit.
    from visibility364 import overlap, OVERLAYS
    for ref in sources:
        for frame in q.load(checked(ref))['frames']:
            if frame['variant'] not in ('banner', 'toast'):
                continue
            annotation = q.load(checked(frame['annotation']))
            target = next(n for n in annotation['nodes'] if n['id'] == frame['target'])
            q.require(overlap(target['focusedBounds'], OVERLAYS[frame['variant']]) == 0, 'covered_training_control')
    q.save(OUT/'admission.json', dict(version='notification366-admission-v1', rows=rows, sources=sources,
        development=cfg['development'], pixelDisjoint=True, trainingEligible=True,
        pixelHashes=sorted(set(cache.values())), modelAccepted=False,
        limitation='Layouts and earlier artwork ancestry overlap development. This is not independent final evaluation.'))
    q.save(OUT/'qualification.json', dict(version='research-condition-v1', outcome='supported',
        reason='252 fresh authored pairs have no exact pixel overlap with the 392 development pairs.',
        evidence=[g.pin(OUT/'admission.json')]))


def schedule(primary, auxiliary, epochs):
    primary = np.asarray(primary).reshape(-1); auxiliary = np.asarray(auxiliary).reshape(-1)
    q.require(set(primary) == {0, 1} and set(auxiliary) == {0, 1}, 'schedule_labels')
    result = np.empty((epochs, len(primary)), np.int64)
    for label in (0, 1):
        slots = np.flatnonzero(primary == label); pool = np.flatnonzero(auxiliary == label)
        q.require(len(slots)*epochs >= len(pool), 'insufficient_exposure')
        for epoch in range(epochs):
            result[epoch, slots] = pool[(np.arange(len(slots)) + epoch*len(slots)) % len(pool)]
    q.require(np.array_equal(auxiliary[result], np.tile(primary, (epochs, 1))), 'schedule_label_mismatch')
    q.require(len(np.unique(result)) == len(auxiliary), 'unseen_auxiliary')
    return result


def training():
    import appearance348 as m
    a = m.a; t = m.t; started = time.monotonic()
    g.OUT = OUT; cfg = g.config(); arm = cfg['arm']
    q.require(arm in ('control', 'notification'), 'training_arm')
    refs = outputs('admission.json'); q.require(len(refs) == 1, 'admission_dependency')
    admitted = q.load(checked(refs[0]))
    q.require(admitted['trainingEligible'] and admitted['pixelDisjoint'], 'admission_failed')
    rows = admitted['rows']; q.require(len(rows) == 252 and all(r['role'] == 'train' for r in rows), 'training_rows')
    t.set_num_threads(2); m.OUT = OUT; a.e.f.OUT = OUT
    reg = q.load(a.e.OUT/'inputs.json'); reg['trainer'] = a.b.ref(Path(a.b.trainer.__file__))
    m.emit('Verify original images and crops', 0, 10)
    x,d,y,w,aux,ad,ay,_ = a.e.f.prepare(reg)
    old_count = len(aux); extra_labels = np.array([r['changed'] for r in rows], np.float32)
    if arm == 'control':
        offsets = {0: 0, 1: 0}; ids = []
        for label in extra_labels:
            pool = np.flatnonzero(ay == label)
            ids.append(pool[offsets[label] % len(pool)]); offsets[label] += 1
        extra = aux[ids].copy(); detail = ad[ids].copy()
    else:
        extra = np.empty((len(rows), *aux.shape[1:]), np.float32)
        detail = np.empty((len(rows), *ad.shape[1:]), np.float32)
        for i in range(0, len(rows), 8):
            subset = rows[i:i+8]
            values = np.stack([a.r.s.encoded(*[a.r.s.image(v['path'], v['sha256']) for v in r['images']], (192,128))[0] for r in subset])
            details,_ = a.r.prepare(values, subset, 2)
            extra[i:i+len(subset)] = values; detail[i:i+len(subset)] = details
            m.emit('Prepare fresh notification pairs', i+len(subset), len(rows))
    aux = np.concatenate((aux, extra)); ad = np.concatenate((ad, detail)); ay = np.concatenate((ay, extra_labels))
    indices = schedule(y, ay, 10)
    q.save(OUT/'schedule.json', dict(admission=refs[0], arm=arm, oldAuxiliaryRows=old_count,
        newSlots=len(rows), indicesSHA256=a.e.f.digest(indices), labelsSHA256=a.e.f.digest(ay),
        minimumExposure=int(np.bincount(indices.flatten(), minlength=len(aux)).min()), originalViewsUnchanged=True))
    net = a.e.load_candidate(a.e.OUT/'run/last.pt'); initial = {k:v.clone() for k,v in net.state_dict().items()}
    original = m.raw_logits(net,x,d); auxiliary = m.raw_logits(net,aux,ad)
    settings = dict(reg['configuration'], epochs=10, seed=42, threads=2, detailOnly=True)
    def progress(row):
        q.save(OUT/f"epoch-{row['epoch']:04d}.json", row); m.emit('Train '+arm, row['epoch'], 10)
    net,history = a.b.trainer.fit(net,t.from_numpy(x),t.from_numpy(y),settings,progress,
        weights=t.from_numpy(w),detail_inputs=t.from_numpy(d),auxiliary_inputs=t.from_numpy(aux),
        auxiliary_detail=t.from_numpy(ad),auxiliary_indices=t.from_numpy(indices),auxiliary_weight=.25,
        preservation_logits=original,auxiliary_preservation_logits=auxiliary,preservation_weight=1.)
    changed = [k for k,v in net.state_dict().items() if not t.equal(v,initial[k])]
    q.require(changed and all(k.startswith(('change.detail.','change.correction.')) for k in changed), 'changed_scope')
    t.save(dict(state=net.state_dict(),representation=a.e.VERSION,windows=2), OUT/'last.pt')
    restored = a.e.load_candidate(OUT/'last.pt'); sample = np.concatenate((x[:8],d[:8]),1)
    q.require(np.array_equal(a.b.worker.score(net,sample),a.b.worker.score(restored,sample)), 'reload_parity')
    q.save(OUT/'fit.json',dict(configuration=settings,history=history,changedTensors=changed,
        checkpointParity=True,model=g.pin(OUT/'last.pt'),seconds=time.monotonic()-started,productionEligible=False))


def collect():
    import position355 as p
    p.OUT = OUT; p.collect()
    doc = q.load(OUT/'summary.json'); target = []
    for ref in outputs('comparison.json'):
        for item in q.load(checked(ref)).get('sets', {}).values():
            for row, score in zip(item['rows'], item['probabilities']['gamma']):
                if row['id'].startswith('artwork-s') and row.get('layout'):
                    target.append(dict(id=row['id'], changed=row['changed'], condition=row['condition'], probability=score))
    doc['targetPredictions'] = target
    q.save(OUT/'summary.json',doc,replace=True)


def decide(summaries):
    from research_campaign340 import decision
    arms = {}
    for arm in ('control','notification'):
        selected = [d for job,d in summaries if job.startswith('focus366-'+arm+'-')]
        reports = [r for d in selected for r in d['summaryRows']]
        targets = [r for d in selected for r in d['targetPredictions']]
        q.require(len(reports) == 28 and len({r['job'] for r in reports}) == 28, 'missing_comparisons')
        q.require(len(targets) == 392 and len({r['id'] for r in targets}) == 392, 'target_membership')
        corner = next(r for r in targets if r['id'] == 'artwork-s1-focus_maze-005')
        arms[arm] = dict(lostPrevious=sum(r['counts'].get('lost',0) for r in reports),
            falseChanges=sum(r['changed']==0 and decision(r['probability'])==1 for r in targets),
            correct=sum(decision(r['probability'])==r['changed'] for r in targets),
            cornerPreserved=decision(corner['probability'])==1, cornerProbability=corner['probability'])
    candidate = arms['notification']; control = arms['control']
    passes = candidate['lostPrevious']==0 and candidate['cornerPreserved'] and candidate['falseChanges']<control['falseChanges'] and candidate['correct']>control['correct']
    return dict(arms=arms,passesDevelopmentRule=passes,modelAccepted=False,productionChanged=False,
        nextAction='Review native transfer before promotion.' if passes else 'Use case-linked losses to diagnose the correction. Do not promote.')


def decision():
    summaries = [(d['job'],q.load(checked(d['outputs'][0]))) for d in q.load(OUT/'dependencies.json')]
    doc = decide(summaries)
    doc['evidence'] = outputs('summary.json')
    q.save(OUT/'decision.json',doc)
