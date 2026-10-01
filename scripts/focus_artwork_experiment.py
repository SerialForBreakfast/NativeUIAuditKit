"""Exact reviewed artwork additions, using the existing partial-detail trainer."""
import argparse
import io
import time

import human_annotation_review as h
import focus_artwork_readiness as ready
import focus_context_experiment as context
import focus_native_body_assembly as native
import focus_visual_experiment as visual

VERSION = 'focus-artwork-experiment-v1'
ARMS = {'artwork-control-partial': 'fdr031-artwork-control',
        'artwork-added-partial': 'fdr032-artwork-added'}
ROOT = 'reports/work/FOCUS-CAMPAIGN-09'
AUTHORITY = 'Research/Plans/FocusArtwork09.md'
CODE = visual.CODE + ['focus_artwork_experiment.py', 'focus_artwork_readiness.py',
                      'focus_native_body_assembly.py']


def runtime():
    return dict(code=[h.ref(h.ROOT/'scripts'/n) for n in CODE], packages=visual.packages())


def admitted_rows(readiness):
    ids = readiness['conditionalOwnedComparison']['comparison']['proposedAdditionIDs']
    rows = {r['id']: r for r in readiness['candidates']}
    h.require(len(ids) == len(set(ids)) == 12, 'artwork_exact_twelve')
    selected = [rows[i] for i in ids]
    h.require(all(not r['reasons'] and r['sourceElementID'] == 'catalog-poster-0'
                  and r['producerSplit'] == 'calibration' for r in selected), 'artwork_ineligible_source')
    h.require(len({r['crop']['pixelSHA256'] for r in selected}) == 12 and
              sum(r['label'] for r in selected) == 6 and
              len({r['sourceID'] for r in selected}) == 6, 'artwork_pair_membership')
    return [dict(r, recipe=readiness['recipes'][r['recipeSHA256']], split='train',
                 use='train-candidate', trainingEligible=True, disposition='admitted',
                 sourceRoleDecision='maintainer-explicit-development-training-20261001') for r in selected]


def admit(output):
    old = h.read(h.ROOT/ROOT/'artifacts/readiness.json', limit=32*1024**2)
    current = ready.prepare(old['inputs'])
    h.require(current == old, 'artwork_readiness_changed')
    sample_ref = h.ref(h.ROOT/ROOT/'artifacts/sample-acceptance.json')
    samples = context.read(sample_ref)
    h.checked(h.ROOT, samples['authorization'])
    h.require(samples['sampledFramesApproved'] == 6 and len(samples['summaries']) == 3,
              'artwork_sample_count')
    for s in samples['summaries']:
        summary = s['summary']; h.checked(h.ROOT, summary['revision'])
        h.checked(h.ROOT, s['receipt'])
        lane = summary['lanes']['random']
        h.require(lane == dict(selected=2, completed=2, pending=0, changedAmongCompleted=0),
                  'artwork_sample_incomplete_or_corrected')
        qa = context.read(s['cropQA'])
        h.require(qa['expected'] == qa['completed'] == 104, 'artwork_review_crop_qa')
    additions = admitted_rows(current)
    doc = dict(version='focus-artwork-admission-v1', authority=h.ref(h.ROOT/AUTHORITY),
               readiness=h.ref(h.ROOT/ROOT/'artifacts/readiness.json'), sampleAcceptance=sample_ref,
               baseline=old['inputs']['baseline'], additions=additions,
               evaluationMembershipSHA256=current['conditionalOwnedComparison']['comparison']['evaluationMembershipSHA256'],
               originalProducerRole='calibration', consumerRole='development-training',
               independentTest=False, releaseEligible=False)
    doc['protocolSHA256'] = h.digest(doc)
    out = h.fresh(output); out.mkdir(parents=True); h.write(out/'admission.json', doc)
    print('Admitted 12 targets from 6 pairs; unchanged evaluation', flush=True)


def admission(ref):
    doc = context.sealed(ref)
    h.require(doc['version'] == 'focus-artwork-admission-v1' and not doc['independentTest'], 'artwork_admission_version')
    h.checked(h.ROOT, doc['authority']); context.read(doc['sampleAcceptance'])
    r = context.sealed(doc['readiness'])
    h.require(doc['additions'] == admitted_rows(r), 'artwork_admission_membership')
    base = ready.baseline(h.checked(h.ROOT, doc['baseline']))
    evaluation = [r for r in base['samples'] if r['split'] != 'train']
    h.require(len(evaluation) == 333 and h.digest(evaluation) == doc['evaluationMembershipSHA256'],
              'artwork_evaluation_changed')
    for row in doc['additions']:
        for key in ('crop', 'frame', 'nativeRecord', 'batch', 'cropQA'): h.checked(h.ROOT, row[key])
    return doc, base


def encode(admission_path, output):
    import torch
    import numpy as np
    from PIL import Image
    from focus_pretrained_experiment import state_digest
    ar = h.ref(h.local(admission_path)); doc, base = admission(ar)
    h.require(torch.backends.mps.is_available(), 'artwork_requires_mps')
    started = time.monotonic(); prefix = visual.make_network(base['representation']).features[:9].eval().to('mps')
    old_receipt = context.read(base['features']['receipt'])
    before = state_digest(prefix)
    h.require(before == old_receipt['prefixSHA256'], 'artwork_prefix_mismatch')
    norm = base['representation']['normalization']; images = []
    for row in doc['additions']:
        with Image.open(h.checked(h.ROOT, row['crop'])) as im:
            h.require(im.size == (256,256), 'artwork_crop_size')
            images.append(torch.from_numpy(np.array(im.convert('RGB'),copy=True)).permute(2,0,1))
    x = torch.stack(images).to('mps').float()/255
    mean = torch.tensor(norm['mean'],device='mps')[None,:,None,None]
    std = torch.tensor(norm['std'],device='mps')[None,:,None,None]
    with torch.no_grad(): f = prefix((x-mean)/std).cpu()
    local = torch.cat((f,torch.ones(12,1,16,16)),1)
    new = torch.stack((local,torch.zeros_like(local)),1)
    h.require(state_digest(prefix) == before and bool(torch.isfinite(new).all()) and
              time.monotonic()-started < 300 and new.numel()*4 <= 32*1024**2, 'artwork_encoding_budget')
    old = torch.load(h.checked(h.ROOT,base['features']['cache'],limit=512*1024**2),map_location='cpu',weights_only=True)
    h.require(old['receipt'] == old_receipt and context.tensor_digest(old['features']) == old_receipt['featureSHA256']
              and old_receipt['ids'] == [r['id'] for r in base['samples']], 'artwork_old_cache_changed')
    h.require(all(r['split']=='train' for r in base['samples'][:1550]) and
              all(r['split']=='validation' for r in base['samples'][1550:]), 'artwork_cache_order')
    values = torch.cat((old['features'][:1550],new,old['features'][1550:]))
    receipt = dict(version='focus-artwork-prefix-v1', admission=ar, baselineFeatures=base['features'],
        ids=old_receipt['ids'][:1550]+[r['id'] for r in doc['additions']]+old_receipt['ids'][1550:],
        prefixSHA256=before,prefixUnchanged=True, featureSHA256=context.tensor_digest(values),
        encodedControls=12,reusedControls=1883,disabledContext='zero; detail-only arm',
        elapsedSeconds=time.monotonic()-started,shape=list(values.shape))
    out=h.fresh(output); out.mkdir(parents=True)
    torch.save(dict(features=values,receipt=receipt),out/'prefix.pt'); h.write(out/'receipt.json',receipt)
    h.write(out/'references.json',dict(cache=h.ref(out/'prefix.pt'),receipt=h.ref(out/'receipt.json')))
    print(f'Encoded 12; reused 1883; {receipt["elapsedSeconds"]:.2f}s',flush=True)


def expected(doc, base, arm):
    additions=doc['additions'] if arm=='artwork-added-partial' else []
    rows=[r for r in base['samples'] if r['split']=='train']+additions+[r for r in base['samples'] if r['split']!='train']
    return dict(samples=rows, configuration=dict(base['configuration'],batch=1550+len(additions)),
        fullFit=dict(base['fullFit'],weights=native.continuous_weights(base,additions)),
        counts=dict(training=1550+len(additions),development=315,retention=18,evaluation=333,added=len(additions)),
        representation=base['representation'],selection=base['selection'],
        unmetQualificationBlockers=base['unmetQualificationBlockers'])


def approval(doc):
    return dict(version='focus-artwork-approval-v1',protocolSHA256=doc['protocolSHA256'],
                authority=doc['authority'],arm=doc['arm'],name=ARMS[doc['arm']],scope='matched-training-no-export')


def protocol(admission_path, cache, output):
    ar=h.ref(h.local(admission_path)); doc,base=admission(ar); features=h.read(h.local(cache))
    receipt=context.read(features['receipt']);h.checked(h.ROOT,features['cache'],limit=512*1024**2)
    h.require(receipt['admission']==ar and receipt['baselineFeatures']==base['features'] and
              receipt['encodedControls']==12, 'artwork_encoded_admission')
    out=h.fresh(output);out.mkdir(parents=True)
    for arm in ARMS:
        p=dict(version=VERSION,arm=arm,admission=ar,authority=doc['authority'],runtime=runtime(),
               features=features if arm=='artwork-added-partial' else base['features'],
               releaseEligible=False,**expected(doc,base,arm))
        p['protocolSHA256']=h.digest(p); dest=out/arm;dest.mkdir()
        h.write(dest/'protocol.json',p);h.write(dest/'approval.json',approval(p))
        print(arm,p['protocolSHA256'],flush=True)


def load_protocol(path, arm, run_name, approval_path=None):
    ref=h.ref(h.local(path)); p=context.sealed(ref)
    h.require(p['version']==VERSION and arm==p['arm'] and ARMS.get(arm)==run_name,'artwork_arm_binding')
    doc,base=admission(p['admission']); e=expected(doc,base,arm)
    h.require(all(p[k]==v for k,v in e.items()) and p['runtime']==runtime() and
              p['authority']==doc['authority'], 'artwork_configuration_changed')
    receipt=context.read(p['features']['receipt']);h.checked(h.ROOT,p['features']['cache'],limit=512*1024**2)
    h.require(receipt['ids']==[r['id'] for r in p['samples']], 'artwork_cache_membership')
    if arm=='artwork-added-partial':
        h.require(receipt['admission']==p['admission'] and receipt['baselineFeatures']==base['features'] and
                  receipt['prefixSHA256']==context.read(base['features']['receipt'])['prefixSHA256'], 'artwork_cache_source')
    else: h.require(p['features']==base['features'], 'artwork_control_cache')
    out=h.ROOT/'NativeUITrainer/focus_ring_runs'/run_name
    h.require(not out.exists() and not any(x.is_symlink() for x in (out,*out.parents)), 'output_collision')
    ar=h.ref(h.local(approval_path)) if approval_path else None
    if ar: h.require(context.read(ar)==approval(p), 'artwork_approval_binding')
    report=dict(protocolVersion=VERSION,protocolFile=ref,approval=ar,arm=arm,visualTraining=True,
        features=p['features'],warmCheckpoint=None,configurationValid=True,executionAuthorized=False,
        releaseEligible=False,launchEligible=ar is not None,blockers=[] if ar else ['missing_artwork_approval'],
        **{k:p[k] for k in ('configuration','fullFit','representation','selection','counts','runtime',
                            'protocolSHA256','unmetQualificationBlockers')})
    return report,[dict(r,path=h.ROOT/r['crop']['path']) for r in p['samples']]


def prepare_features(report, train, val, device, out):
    # Reuse the exact model/trainer/cache validation, with the known detail-only architecture.
    mapped=dict(report,arm='visual-local-partial')
    result=visual.prepare_features(mapped,train,val,device,out)
    for key in ('initialTailSHA256','initialBNSHA256'): report[key]=mapped[key]
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['admit','encode','protocol'])
    p.add_argument('--admission');p.add_argument('--cache');p.add_argument('--output',required=True)
    a=p.parse_args()
    if a.mode=='admit':admit(a.output)
    elif a.mode=='encode':encode(a.admission,a.output)
    else:protocol(a.admission,a.cache,a.output)


if __name__=='__main__':main()
