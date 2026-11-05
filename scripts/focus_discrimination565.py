"""Fixed crop colour intervention and training-only feature diagnosis. No model edits or training."""
import copy
import hashlib
from collections import Counter
import numpy as np
from PIL import Image, ImageOps
import torch
import research_queue as q
from template_adapters395 import document, resolve_inputs
from template_inputs398 import checked, pin

OUT=None


def neutralize_chroma(image):
    q.require(image.size==(256,256),'crop_dimensions')
    return ImageOps.grayscale(image.convert('RGB')).convert('RGB')


def refs():
    return resolve_inputs(q.load(OUT.parents[2]/'spec.json')['template'],OUT)


def receipt(names):
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path=n,sha256=q.digest(OUT/n)) for n in names]))


def prepare():
    r=refs();original=document(r['suite'])
    q.require(original.get('version')=='weight-surgery-suite-v1' and original['threshold']==.85,'source_suite')
    suite=copy.deepcopy(original);folder=OUT/'crops';folder.mkdir()
    cache={}
    def transform(ref):
        source=checked(ref)
        key=ref['sha256']
        if key not in cache:
            target=folder/(key+'.png')
            with Image.open(source) as image:neutralize_chroma(image).save(target)
            cache[key]=pin(target)
        return cache[key]
    suite['crops']={key:transform(ref) for key,ref in original['crops'].items()}
    for row in suite['legacy']:row['image']=transform(row['image'])
    for members in suite['ancillary'].values():
        for row in members:row['image']=transform(row['image'])
    suite.update(sourceSuite=r['suite'],intervention='Pillow-grayscale-RGB-replicated-v1',
        metricsStatus='provisional',modelAccepted=False)
    q.require(suite['frames']==original['frames'],'reference_geometry_changed')
    q.require([r['label'] for r in suite['legacy']]==[r['label'] for r in original['legacy']],'legacy_labels_changed')
    q.save(OUT/'suite.json',suite)
    q.save(OUT/'transform.json',dict(sourceSuite=r['suite'],intervention=suite['intervention'],uniqueCrops=len(cache),
        geometryChanged=False,labelsChanged=False,trainingEligible=False,metricsStatus='provisional',modelAccepted=False))
    receipt(['suite.json','transform.json'])


def compare_reports(left,right,suite,suite_ref,anchors):
    q.require(suite.get('intervention')=='Pillow-grayscale-RGB-replicated-v1','intervention_identity')
    q.require(left['suiteSHA256']==suite['sourceSuite']['sha256'] and right['suiteSHA256']==suite_ref['sha256'],'source_suite_changed')
    q.require(left['model']==right['model'] and left['threshold']==right['threshold']==.85,'model_or_threshold_changed')
    a={r['id']:r for r in left['outcomes']};b={r['id']:r for r in right['outcomes']}
    q.require(a.keys()==b.keys() and left['legacyLabels']==right['legacyLabels'],'comparison_membership')
    q.require(left['development']['negatives']==right['development']['negatives'],'proposal_population_changed')
    q.require(anchors.get('version')=='anchor-preservation565-v1' and anchors.get('complete') is True, 'anchor_evidence_missing')
    q.require(anchors['model']==left['model'] and anchors['sourceSuiteSHA256']==left['suiteSHA256'] and anchors['candidateSuiteSHA256']==right['suiteSHA256'],'anchor_binding')
    recovered=[k for k in a if not a[k]['correct'] and b[k]['correct']]
    lost=[k for k in a if a[k]['correct'] and not b[k]['correct']]
    wrong=[k for k in a if not a[k]['wrong'] and b[k]['wrong']]
    old=left['legacyProbabilities'];new=right['legacyProbabilities'];labels=left['legacyLabels']
    q.require(len(old)==len(new)==len(labels),'legacy_prediction_membership')
    legacy_lost=[i for i,(x,y,label) in enumerate(zip(old,new,labels)) if (x>=.85)==bool(label) and (y>=.85)!=bool(label)]
    lower=right['development']['falseHigh']<left['development']['falseHigh']
    outcome='contradicted' if lost or wrong or legacy_lost or anchors['lost'] else 'supported' if recovered and lower else 'inconclusive'
    return dict(version='focus-discrimination565-v1',outcome=outcome,recovered=recovered,lost=lost,newWrong=wrong,
        lostLegacy=legacy_lost,lostAncillary=anchors['lost'],baseline=left['development'],candidate=right['development'],
        metricsStatus='provisional',dataRole='development',modelAccepted=False,
        nextAction='If colour removal reduces confusion without losses, propose matched colour augmentation training. Otherwise prioritize native focus-style data and training-only feature evidence.',
        limitation='Colour intervention diagnostic on retained development frames. No deployment or release qualification.')


def compare():
    r=refs();result=compare_reports(document(r['baseline']),document(r['candidate']),document(r['suite']),r['suite'],document(r['retention']))
    q.save(OUT/'benchmark_summary.json',result);receipt(['benchmark_summary.json'])


def training_rows(protocol):
    content=dict(protocol);expected=content.pop('protocolSHA256',None)
    from focus_dataset_contract import digest
    q.require(expected==digest(content),'training_protocol_hash')
    q.require(protocol.get('version')=='focus-learning-protocol-v1' and
        protocol.get('scope')=='development-only-same-app-screen-groups','training_protocol_scope')
    rows=protocol['samples']
    q.require(len({r['id'] for r in rows})==len(rows),'duplicate_training_membership')
    q.require(Counter(r['split'] for r in rows)=={'train':74,'validation':18},'training_membership')
    selected=[r for r in rows if r['split']=='train']
    q.require(Counter(r['label'] for r in selected)=={0:37,1:37},'training_class_support')
    q.require(all(r['screenID'] in ('settings/root','settings/general') for r in selected),'training_source_group')
    q.require(not {r['group'] for r in selected}&{r['group'] for r in rows if r['split']=='validation'},'training_group_leak')
    return selected


def training_crop(row, policy):
    q.require(policy in ('stretch','aspect-fit'),'training_crop_policy')
    ref=row['crops'][policy]
    q.require(set(ref)=={'path','sha256','pixelSHA256'},'training_crop_fields')
    path=checked({key:ref[key] for key in ('path','sha256')})
    from focus_dataset_contract import pixel_digest
    q.require(pixel_digest(q.ROOT,ref)==ref['pixelSHA256'],'training_crop_pixels')
    with Image.open(path) as image:q.require(image.size==(256,256),'training_crop_dimensions')
    return path


def feature_probe():
    from focus_ring_backbone import mobilenetv4_conv_small
    r=refs();protocol=document(r['protocol']);rows=training_rows(protocol)
    policy=q.load(OUT.parents[2]/'spec.json')['template']['parameters'].get('cropPolicy','stretch')
    paths=[training_crop(row,policy) for row in rows]
    q.require(protocol['warmCheckpoint']==r['model'],'training_model_changed')
    model=mobilenetv4_conv_small();original_state=torch.load(checked(r['model']),map_location='cpu',weights_only=True)['state_dict']
    model.load_state_dict(original_state);model.eval()
    torch.set_num_threads(4)
    activations=[]
    handle=model.classifier.register_forward_pre_hook(lambda module,args:activations.append(args[0].detach().clone()))
    by_label={0:[],1:[]};predictions=[];largest_error=0.
    try:
        with torch.no_grad():
            for row,path in zip(rows,paths):
                with Image.open(path) as image:
                    x=torch.from_numpy(np.array(image.convert('RGB').resize((256,256),Image.Resampling.BILINEAR),copy=True)).permute(2,0,1).float().div(255).unsqueeze(0)
                logit=model(x).reshape(-1)[0];feature=activations.pop().reshape(-1)
                contribution=feature*model.classifier.weight.reshape(-1)
                reconstructed=contribution.sum()+model.classifier.bias.reshape(-1)[0]
                largest_error=max(largest_error,abs(float(logit-reconstructed)))
                by_label[row['label']].append(contribution)
                predictions.append(dict(id=row['id'],group=row['group'],label=row['label'],probability=float(logit.sigmoid())))
    finally:handle.remove()
    q.require(largest_error<=1e-4,'logit_reconstruction')
    q.require(all(torch.equal(value,model.state_dict()[key]) for key,value in original_state.items()),'probe_modified_model')
    positive=torch.stack(by_label[1]).mean(0);negative=torch.stack(by_label[0]).mean(0)
    ranked=torch.argsort(negative-positive,descending=True)[:20].tolist()
    q.save(OUT/'benchmark_summary.json',dict(version='training-feature565-v1',rows=len(rows),validationCropsRead=0,cropPolicy=policy,
        groups=sorted({row['group'] for row in rows}),model=r['model'],protocol=r['protocol'],
        maximumLogitReconstructionError=largest_error,
        negativeFavouringChannels=[dict(channel=i,positiveMeanContribution=float(positive[i]),negativeMeanContribution=float(negative[i])) for i in ranked],
        predictions=predictions,metricsStatus='provisional',dataRole='training-diagnostic',modelAccepted=False,
        limitation='Associations on historical native training crops. They do not prove channel causality or real-app generalization. No weights are changed.'))
    receipt(['benchmark_summary.json'])


def anchors():
    from eval_focus_ring_detector import predict_torch
    r=refs();source=document(r['source']);candidate=document(r['candidate']);model=document(r['model'])
    q.require(candidate.get('sourceSuite')==r['source'],'anchor_source_suite')
    checkpoint=checked(model['checkpoint']);torch.set_num_threads(4)
    rows=[];lost=[]
    for group,count in (('reserved',16),('calibration',8)):
        before=source['ancillary'][group];after=candidate['ancillary'][group]
        q.require(len(before)==len(after)==count and [v['label'] for v in before]==[v['label'] for v in after],'anchor_membership')
        old=predict_torch(checkpoint,[dict(path=checked(v['image'])) for v in before])
        new=predict_torch(checkpoint,[dict(path=checked(v['image'])) for v in after])
        for i,(a,b,label) in enumerate(zip(old,new,[v['label'] for v in before])):
            ident=group+'-'+str(i);previous=(a>=.85)==bool(label);current=(b>=.85)==bool(label)
            if previous and not current:lost.append(ident)
            rows.append(dict(id=ident,source=before[i]['image'],label=label,before=a,after=b,previousCorrect=previous,candidateCorrect=current))
    q.save(OUT/'retention.json',dict(version='anchor-preservation565-v1',complete=True,rows=rows,lost=lost,
        sourceSuiteSHA256=r['source']['sha256'],candidateSuiteSHA256=r['candidate']['sha256'],model=model['checkpoint'],
        metricsStatus='provisional',modelAccepted=False))
    receipt(['retention.json'])
