"""Recover only the known history-field receipt failure. Never train or alter weights."""
import copy
import math
from pathlib import Path
import torch
import research_queue as q
from template_inputs398 import checked,pin
from research_trust import check_training_report
OUT=None


def normalize(history,epochs):
    q.require(len(history)==epochs and [r['epoch'] for r in history]==list(range(1,epochs+1)),'recovery_history_epochs')
    q.require(all(set(r)=={'epoch','loss'} and type(r['loss']) in (int,float) and math.isfinite(r['loss']) for r in history),'recovery_history_loss')
    return [dict(r,trainLoss=r['loss']) for r in history]


def recover():
    spec=q.load(OUT.parents[2]/'spec.json');r=q.load(checked(spec['inputs'][0]))
    q.require(r['version']=='focus-history-recovery568-v1','recovery_request')
    source=q.load(checked(r['sourceSpec']));result_path=checked(r['result']);result=q.load(result_path)
    q.require(checked(r['sourceSpec'])==result_path.parents[2]/'spec.json','recovery_source_location')
    q.require(result['specSHA256']==q.text_digest(source) and result['status']=='failed' and result['reason']=='training_history_loss_invalid' and result['returnCode']==0,'recovery_failure_reason')
    q.require(source['adapter']['steps']==['focus_replay568.train'] and source['training']['epochs']==30,'recovery_source_scope')
    q.require(q.outputs_intact(result_path.parent,result),'recovery_outputs_changed')
    archived=checked(r['sourceCode'])
    q.require(any(row['path']=='scripts/focus_replay568.py' and row['sha256']==q.digest(archived) for row in result['closure']['modules']),'recovery_code_identity')
    old=result_path.parent/'out';fit=q.load(old/'fit.json');history=normalize(q.load(old/'history.json'),30)
    weights=old/'final.pt';checkpoint=torch.load(weights,map_location='cpu',weights_only=True)
    q.require(checkpoint['epoch']==30 and abs(checkpoint['loss']-history[-1]['trainLoss'])<=1e-8,'recovery_checkpoint_epoch_or_loss')
    q.require(all(not t.is_floating_point() or torch.isfinite(t).all() for t in checkpoint['state_dict'].values()),'recovery_nonfinite_weights')
    from focus_ring_backbone import mobilenetv4_conv_small
    torch.set_num_threads(2);model=mobilenetv4_conv_small();model.load_state_dict(checkpoint['state_dict'],strict=True)
    q.require(fit['epochs']==30 and fit['initialization']==source['training']['initialization'] and fit['validationCropsRead']==0,'recovery_training_identity')
    checked(fit['initialization']);q.require(q.digest(weights)!=fit['initialization']['sha256'],'recovery_weights_unchanged')
    q.save(OUT/'history.json',history);q.save(OUT/'fit.json',fit)
    q.require(check_training_report(OUT,dict(history='history.json',trainingReport='fit.json'),30) is None,'recovery_normalized_report_invalid')
    original=q.load(old/'model.json');q.require(original['checkpoint']==pin(weights),'recovery_model_identity')
    ancestry=q.load(checked(original['edit']));q.require(ancestry['ancestry']['base']==fit['initialization'],'recovery_ancestry')
    ancestry.update(originalFailedResult=r['result'],normalizedTraining=pin(OUT/'fit.json'),additionalTraining=False)
    q.save(OUT/'ancestry.json',ancestry);original['edit']=pin(OUT/'ancestry.json');q.save(OUT/'model.json',original)
    q.save(OUT/'benchmark_summary.json',dict(version='focus-history-recovery568-v1',sourceResult=r['result'],checkpoint=pin(weights),
        epochs=30,historyFieldCorrection='loss to trainLoss',weightsUnchanged=True,additionalTraining=False,
        originalAttemptStatus='failed',receiptRecovered=True,metricsStatus='provisional',modelAccepted=False))
    names=['history.json','fit.json','ancestry.json','model.json','benchmark_summary.json']
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path=n,sha256=q.digest(OUT/n)) for n in names]))


def compile_successors(manifest,destination,archive):
    originals=[q.load(checked(row['spec'])) for row in manifest['jobs']]
    mapping={s['id']:s['id'].replace('focus568-','focus568-r1-',1) for s in originals if s['id']!='focus568-corpus'}
    made={};destination.mkdir(exist_ok=False);entries=[]
    for old in originals:
        if old['id']=='focus568-corpus':continue
        if old['id'] in ('focus568-control-train','focus568-native-train'):
            request=dict(version='focus-history-recovery568-v1',sourceSpec=pin(q.QUEUE/'jobs'/old['id']/'spec.json'),
                result=pin(q.QUEUE/'jobs'/old['id']/'attempts/1/result.json'),sourceCode=pin(archive))
            path=destination/(mapping[old['id']]+'-request.json');q.save(path,request)
            s=dict(version='research-spec-v2',id=mapping[old['id']],task='FOCUS568',owner='Maximum-mini-NUIAK',kind='screen',authority='diagnostic',jobKind='artifact',
                question='Can completed focus weights be recovered by correcting only the history receipt field?',hypothesis='The known schema failure does not invalidate completed training outputs.',
                controlledComparison='Preserve original failed attempts and exact checkpoint bytes. Add no training or inference.',decisionRule='Verify all outputs, 30 epochs, loss values, source identity, and strict checkpoint loading. Keep results provisional.',
                nextActionByOutcome=dict(supported='Release matched scoring without retraining.',contradicted='Keep failed evidence and report the exact mismatch.'),
                inputs=[pin(path),pin(Path(__file__)),request['sourceSpec'],request['result'],request['sourceCode']],dependencies=[],
                adapter=dict(type='python-callable',steps=['focus_receipt568.recover'],outputAttributes=['focus_receipt568.OUT']),
                evidence=dict(reads=[pin(path)['path'],request['sourceSpec']['path'],request['result']['path'],request['sourceCode']['path']],artifactReceipt='artifact-receipt.json'),
                limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1))
        else:
            s=copy.deepcopy(old);s['id']=mapping[old['id']]
            s['inputs']=[pin(q.ROOT/r['path']) if r['path']=='scripts/focus_replay568.py' else r for r in s['inputs']]
            for ref in s['template']['inputs'].values():
                if ref.get('job') in mapping:ref['job']=mapping[ref['job']]
            for dep in s['dependencies']:
                if dep['job'] in mapping:
                    parent=made[dep['job']];dep['job']=mapping[dep['job']];dep['specSHA256']=q.text_digest(parent)
            for condition in s.get('conditions',[]):condition['job']=mapping.get(condition['job'],condition['job'])
        q.validate(s);made[old['id']]=s;path=destination/(s['id']+'.json');q.save(path,s)
        entries.append(dict(job=s['id'],spec=pin(path),specSHA256=q.text_digest(s)))
    corpus=q.load(q.QUEUE/'jobs/focus568-corpus/spec.json')
    result=dict(version='model-decision-compiled-v1',plan=manifest['plan'],existing=[dict(job='focus568-corpus',specSHA256=q.text_digest(corpus))],jobs=entries,executionStarted=False)
    q.save(destination/'compiled.json',result);return result
