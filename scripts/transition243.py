"""One matched native-content campaign and one fixed transition candidate."""
import argparse
import copy
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import time

import numpy as np
from PIL import Image
import transition242 as previous

h = previous.h
n = previous.n
review = previous.review
OUT = h.ROOT / 'reports/work/TRANSITION-243/artifacts'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def capture_tool():
    obj = module('capture234', h.ROOT / 'reports/work/FOCUS-RETENTION-234/run.py')
    obj.OUT = OUT
    obj.prior.OUT = OUT
    return obj


def matrix(source):
    entries = []
    for family in range(2):
        base = source['recipes'][family]
        for artwork, background in itertools.product(range(2), repeat=2):
            entry = copy.deepcopy(base)
            entry.update(id=f'family{family}-art{artwork}-background{background}',
                         group=f'training234-family{family}', role='training')
            c = entry['recipe']['appearance']['composition']
            assets = c['asset_pack']['assets']
            for i, content in enumerate(c['contents'].values()):
                content['asset']['sha256'] = assets[(i + artwork) % 2]['sha256']
            c['background']['colors'] = [0x101820, 0x203040] if not background else [0xD0E0F0, 0xFAF0E0]
            entries.append(entry)
    return entries


def plan():
    review.require(not OUT.exists(), 'output_collision')
    source = h.ROOT / 'reports/work/FOCUS-RETENTION-234/artifacts/campaign-v3.json'
    entries = matrix(h.read(source, limit=128*1024**2))
    OUT.mkdir(parents=True)
    (OUT / 'exports').mkdir()
    h.write(OUT / 'campaign-v3.json', dict(target=capture_tool().prior.TARGET, recipes=entries,
            expectedPairs=32, source=h.ref(source), role='development-training', independentEvaluation=False))
    tool = capture_tool()
    h.write(OUT / 'runtime.json', dict(app=str(tool.prior.APP),
        helperSHA256=previous.sha(tool.prior.HELPER.read_bytes()),
        appSHA256=previous.sha((tool.prior.APP/'Contents/MacOS/TVTestRig').read_bytes())))
    print('Frozen 8 recipes, 32 expected native pairs.', flush=True)


def capture():
    tool = capture_tool()
    capacity = tool.prior.cli('capacity', ['fixture', 'job-capacity', '--required-slots', '8'])
    review.require(capacity['fixtureJobCapacity']['_0']['canPrepare'], 'job_capacity')
    tool.prior.cli('env-before', ['fixture', 'env', '--fixture-url', 'http://127.0.0.1:8080'])
    tool.capture()


def archive_completed():
    """Preserve the failed preflight and archive only verified owned jobs."""
    tool = capture_tool()
    failed = OUT/'failed-capacity'; failed.mkdir(exist_ok=False)
    for path in list(OUT.iterdir()):
        if path.suffix in ('.json','.log') and path.name not in ('campaign-v3.json','runtime.json'):
            shutil.move(str(path), failed/path.name)
    old = h.ROOT/'reports/work/FOCUS-ARTWORK-239/artifacts/capture-v2'
    campaign = h.read(old/'campaign-v3.json',limit=128*1024**2)
    for entry in campaign['recipes']:
        root = old/'exports'/entry['id']
        review.require(h.read(root/'harvest-receipt.json')['outcome']=='completed','old_incomplete')
        for item in h.read(root/'dataset-index.json')['artifacts']:
            raw = review.read(root,item['path'])
            review.require(len(raw)==item['byteCount'] and previous.sha(raw)==item['sha256'],'old_export_changed')
        start = h.read(old/(entry['id']+'-start.json'))
        job = start['data']['fixtureJob']['_0']['jobID']
        tool.prior.cli('archive-'+entry['id'],['fixture','archive-job',job])
    print('Archived 8 completed owned jobs. Exported evidence remains intact.',flush=True)


def prepare():
    intake = module('intake233', h.ROOT / 'reports/work/FOCUS-REPAIR-233/intake.py')
    intake.OUT = OUT
    intake.ID_PREFIX = '243:'
    intake.main()
    review.require(not (OUT/'inputs.json').exists(), 'output_collision')
    campaign = h.read(OUT/'campaign-v3.json', limit=128*1024**2)
    banks = {}
    pins = []
    for entry in campaign['recipes']:
        root = OUT/'exports'/entry['id']
        bank = banks.setdefault(entry['id'], {})
        for item in h.read(root/'manifest.json'):
            path = root/item['metadata']['metadataPath']
            meta = h.read(path)
            review.pair(root, path.name, expected_version=meta['schema_version'])
            pins.append(h.ref(path))
            for endpoint, key in [('unfocused','baseline_scene'), ('focused','focused_scene')]:
                scene = meta[key]
                previous.label(scene, scene)
                image = root/meta[endpoint+'_png']
                digest = previous.sha(image.read_bytes())
                review.require(digest == meta[endpoint+'_sha256'], 'image_hash')
                if digest in bank:
                    review.require(bank[digest]['focus'] == scene['focused_element_id'], 'label_conflict')
                    continue
                with Image.open(image) as im:
                    rgb = im.convert('RGB')
                    pixels = previous.sha(str(rgb.size).encode()+rgb.tobytes())
                    tensor = previous.encoded(rgb,rgb,(192,128))[0][:3]
                bank[digest] = dict(image=h.ref(image), pixels=pixels, focus=scene['focused_element_id'],
                                   tensor=tensor, metadata=h.ref(path))
    rows, values, seen = [], [], {}
    for family in range(2):
        groups = sorted(k for k in banks if k.startswith(f'family{family}-'))
        for ga, gb in itertools.combinations(groups, 2):
            for a,b in itertools.product(banks[ga].values(), banks[gb].values()):
                value = np.concatenate([a['tensor'],b['tensor']])
                digest = previous.sha(value.tobytes())
                changed = int(a['focus'] != b['focus'])
                if digest in seen:
                    review.require(seen[digest] == changed, 'encoded_label_conflict')
                    continue
                seen[digest] = changed
                rows.append(dict(id='243:'+digest, group=f'training234-family{family}', role='train',
                    source='243', changed=changed, conditions=['content_contrast'],
                    images=[a['image'],b['image']],metadata=[a['metadata'],b['metadata']],
                    pixelHashes=[a['pixels'],b['pixels']], observedIDs=[a['focus'],b['focus']],tensorSHA256=digest))
                values.append(value)
    _, prior_rows, _ = previous.load_inputs()
    previous.check_roles(prior_rows+rows)
    review.require(rows and {r['changed'] for r in rows} == {0,1}, 'missing_conditions')
    np.save(OUT/'native.npy',np.stack(values),allow_pickle=False)
    shutil.copyfile(__file__,OUT/'preparation-source.py')
    h.write(OUT/'inputs.json',dict(version='transition243-v1',rows=rows,tensor=h.ref(OUT/'native.npy'),
            campaign=h.ref(OUT/'campaign-v3.json'),intake=h.ref(OUT/'intake.json'),metadata=pins,
            source=h.ref(__file__),independentEvaluation=False),sealed=True)
    print('Prepared',len(rows),'contrasts;',sum(r['changed']==0 for r in rows),'unchanged focus.',flush=True)


def archive_current():
    """Free owned job slots only after complete, verified local intake."""
    tool=capture_tool()
    intake=h.read(OUT/'intake.json')
    review.require(intake['review']['reviewed']==32 and intake['review']['expected']==32,'partial_intake')
    campaign=h.read(OUT/'campaign-v3.json',limit=128*1024**2)
    for entry in campaign['recipes']:
        root=OUT/'exports'/entry['id']
        review.require(h.read(root/'harvest-receipt.json')['outcome']=='completed','capture_incomplete')
        for item in h.read(root/'dataset-index.json')['artifacts']:
            raw=review.read(root,item['path'])
            review.require(len(raw)==item['byteCount'] and previous.sha(raw)==item['sha256'],'export_changed')
        job=h.read(OUT/(entry['id']+'-start.json'))['data']['fixtureJob']['_0']['jobID']
        tool.prior.cli('archive-current-'+entry['id'],['fixture','archive-job',job])
    tool.prior.cli('capacity-after',['fixture','job-capacity','--required-slots','8'])
    print('Archived 8 verified current jobs; original evidence retained.',flush=True)


def gate(before, after, stress_before, stress_after, replay_lost):
    return (replay_lost == 0 and after['reserved']['correct'] == before['reserved']['correct']
            and after['development']['correct'] > before['development']['correct']
            and after['artwork_0']['correct'] > before['artwork_0']['correct']
            and after['original_capture']['correct'] > before['original_capture']['correct']
            and all(stress_after[k]['correct'] >= stress_before[k]['summary']['correct']
                    and stress_after[k]['previousCorrectLost'] == 0 for k in stress_before))


def train():
    started = time.monotonic()
    review.require('DTM062' in (h.ROOT/'Research/ExperimentLog.md').read_text(),'unregistered')
    doc = h.read(OUT/'inputs.json')
    review.require(doc['seal']==h.digest({k:v for k,v in doc.items() if k!='seal'}), 'input_seal')
    h.checked(h.ROOT,doc['campaign'],128*1024**2)
    review.require(previous.sha((OUT/'preparation-source.py').read_bytes())==doc['source']['sha256'],
                   'preparation_source_changed')
    for ref in [doc['intake'],*doc['metadata']]: h.checked(h.ROOT,ref)
    admission = h.read(OUT/'admission.json')
    review.require(admission['inputs']==h.ref(OUT/'inputs.json') and admission['approved'] is True, 'admission')
    extra = np.load(h.checked(h.ROOT,doc['tensor'],512*1024**2),allow_pickle=False)
    review.require(extra.shape == (len(doc['rows']),6,128,192) and extra.dtype==np.float32
                   and np.isfinite(extra).all() and ((extra>=0)&(extra<=1)).all(), 'tensor_shape')
    for row,value in zip(doc['rows'],extra):
        review.require(row['tensorSHA256']==previous.sha(value.tobytes()), 'tensor_membership')
    _, rows, native = previous.load_inputs()
    previous.check_roles(rows+doc['rows'])
    torch = n.d.torch_runtime(); torch.set_num_threads(2)
    old_x, old_y, mask, _, _, _, _, _, replay, labels = n.inputs()
    control = h.read(previous.CONTROL/'protocol.json')
    review.require(previous.sha(replay.tobytes())==control['trainingSHA256']
                   and previous.sha(labels.tobytes())==control['labelsSHA256'], 'replay_changed')
    prior = h.read(previous.CONTROL/'result.json')
    checkpoint = h.checked(h.ROOT,prior['model'])
    net = n.make_model(torch,paired_context=True)
    net.load_state_dict(torch.load(checkpoint,weights_only=True,map_location='cpu')['state']);net.eval()
    baseline = h.read(previous.OUT/'baseline.json')
    review.require(baseline['seal']==h.digest({k:v for k,v in baseline.items() if k!='seal'})
                   and baseline['inputs']==h.ref(previous.OUT/'inputs.json')
                   and baseline['model']==h.ref(checkpoint), 'baseline_changed')
    review.require(np.array_equal(n.score(net,torch.from_numpy(replay)),np.array(prior['probabilities'],dtype=np.float32)),
                   'replay_prediction_changed')
    train_ids = [i for i,r in enumerate(rows) if r['role']=='train']
    added = np.concatenate([native[train_ids],extra])
    added_y = np.array([rows[i]['changed'] for i in train_ids]+[r['changed'] for r in doc['rows']],dtype=np.float32)
    protected = {previous.sha(v.tobytes()) for i,row in enumerate(native) if rows[i]['role']!='train'
                 for v in (row[:3],row[3:])}
    review.require(not any(previous.sha(v.tobytes()) in protected for row in added for v in (row[:3],row[3:])),
                   'protected_encoded_overlap')
    tx = np.concatenate([replay,added,np.concatenate([added[:,3:],added[:,:3]],axis=1)])
    ty = np.concatenate([labels,added_y,added_y])
    output = OUT/'candidate'; review.require(not output.exists(),'output_collision');output.mkdir()
    h.write(output/'protocol.json',dict(experiment='DTM062',configuration=n.CONFIG,source=h.ref(__file__),
        inputs=h.ref(OUT/'inputs.json'),admission=h.ref(OUT/'admission.json'),priorInputs=h.ref(previous.OUT/'inputs.json'),
        initializer=h.ref(checkpoint),trainer=h.ref(n.__file__),rows=len(tx),
        trainingSHA256=previous.sha(tx.tobytes()),labelsSHA256=previous.sha(ty.tobytes()),outputCapBytes=2*1024**3),sealed=True)
    before_extra=n.score(net,torch.from_numpy(extra))
    tick=time.monotonic()
    net,history=n.fit(net,torch.from_numpy(tx),torch.from_numpy(ty),n.CONFIG,lambda r:print('DTM062',r,flush=True))
    train_seconds=time.monotonic()-tick
    torch.save(dict(version='transition243-v1',state=net.state_dict(),protocol=h.ref(output/'protocol.json')),output/'last.pt')
    loaded=n.make_model(torch,paired_context=True)
    loaded.load_state_dict(torch.load(output/'last.pt',weights_only=True,map_location='cpu')['state']);loaded.eval()
    p=n.score(loaded,torch.from_numpy(native))
    review.require(np.array_equal(p,n.score(net,torch.from_numpy(native))),'reload_parity')
    after=n.score(loaded,torch.from_numpy(replay))
    reversal=n.score(loaded,torch.from_numpy(np.concatenate([replay[:,3:],replay[:,:3]],axis=1)))
    extra_p=n.score(loaded,torch.from_numpy(extra))
    summary=previous.summaries(p,rows)
    stress={}
    for mode in ('global8','left8','center8'):
        q=n.score(loaded,torch.from_numpy(n.nuisance.localized(old_x[207:],mask[207:],mode)))
        stress[mode]=n.w.summary(q,np.zeros(len(q)))
        stress[mode]['previousCorrectLost']=int(((previous.decisions(np.array(prior['stress'][mode]['probabilities']))==0)
                                                 & (previous.decisions(q)!=0)).sum())
    lost=int(((previous.decisions(np.array(prior['probabilities']))==labels)&(previous.decisions(after)!=labels)).sum())
    y=np.array([r['changed'] for r in doc['rows']])
    result=dict(experiment='DTM062',model=h.ref(output/'last.pt'),summary=summary,stress=stress,
        replay=n.w.summary(after,labels),reversal=n.w.summary(reversal,labels),replayLost=lost,
        extraBefore=n.w.summary(before_extra,y),extraAfter=n.w.summary(extra_p,y),
        probabilities=p.tolist(),extraProbabilities=extra_p.tolist(),history=history,
        repairPassed=gate(baseline['summary'],summary,prior['stress'],stress,lost),productionEligible=False,
        trainingSeconds=train_seconds,totalSeconds=time.monotonic()-started)
    h.write(output/'result.json',result,sealed=True)
    print({k:v for k,v in result.items() if k not in ('probabilities','extraProbabilities','history')},flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['plan','capture','prepare','train','archive_completed','archive_current'])
    args=parser.parse_args();globals()[args.mode]()
