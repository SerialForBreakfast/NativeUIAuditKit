"""Queue adapters for matched replay training and retained focus comparison."""
import math
import shutil
from collections import Counter
import research_queue as q
from template_adapters395 import resolve_inputs,document
from template_inputs398 import checked,pin
from focus_corpus568 import receipt_files
OUT=None


def history_entry(number,loss):
    q.require(type(loss) in (int,float) and math.isfinite(loss),'focus_nonfinite_loss')
    return dict(epoch=number,trainLoss=loss)


def schedule(corpus,arm):
    q.require(corpus['version']=='native-focus-corpus568-v1' and corpus['trainingAdmitted'] is True,'focus_corpus_admission')
    q.require(arm in ('control','native','boost'),'focus_training_arm')
    all_train=[r for r in corpus['rows'] if r['role']=='train']
    rows=[r for r in all_train if arm in ('native','boost') or r['source']!='focus556-native']
    target=Counter(r['label'] for r in all_train)
    q.require(target[0]==target[1] and target[0]>0,'focus_training_balance')
    groups={r['group'] for r in rows}
    q.require(not groups & {r['group'] for r in corpus['rows'] if r['role']!='train'},'focus_training_group_leak')
    by_label={label:sorted((r for r in rows if r['label']==label),key=lambda r:r['id']) for label in (0,1)}
    q.require(all(by_label.values()),'focus_training_class_support')
    if arm=='boost':
        replay=[r for r in all_train if r['source']!='focus556-native']
        native=[r for r in all_train if r['source']=='focus556-native']
        per_class=target[0];replay_count=round(per_class*2/3)
        mixed=[]
        for label in (0,1):
            a=sorted((r for r in replay if r['label']==label),key=lambda r:r['id'])
            b=sorted((r for r in native if r['label']==label),key=lambda r:r['id'])
            q.require(a and b,'focus_boost_support')
            mixed.extend(a[i%len(a)] for i in range(replay_count))
            mixed.extend(b[i%len(b)] for i in range(per_class-replay_count))
        return sorted(mixed,key=lambda r:(r['id'],r['label']))
    # Equal presentation counts and optimizer updates; control repeats approved replay only.
    return [by_label[label][i%len(by_label[label])] for i in range(target[0]) for label in (0,1)]


def train():
    from train_focus556 import train_model
    import torch
    spec=q.load(OUT.parents[2]/'spec.json');r=resolve_inputs(spec['template'],OUT)
    corpus=document(r['corpus'])
    intent=document(spec['training']['membership'][0])
    q.require(corpus['sourceManifest']==intent['manifest'] and corpus['replayProtocol']==intent['replayProtocol'],'focus_training_intent_changed')
    original=document(intent['manifest']);protocol=document(intent['replayProtocol'])
    q.require(len(original)==92,'focus_original_membership')
    from focus_corpus568 import replay_members
    expected={row['id'] for row in replay_members(protocol)}
    q.require({row['id'] for row in corpus['rows'] if row['source']!='focus556-native'}==expected,'focus_replay_membership_changed')
    arm=spec['template']['parameters']['arm'];selected=schedule(corpus,arm)
    q.require(torch.backends.mps.is_available(),'focus_requires_qualified_mps')
    samples=[dict(path=str(checked(row['image'])),label=float(row['label']),pair_id=row['id']) for row in selected]
    initialization=checked(r['model']);history=[]
    def epoch(number,loss):
        q.require(math.isfinite(loss),'focus_nonfinite_loss');history.append(history_entry(number,loss))
        q.save(OUT/'progress.json',dict(step=number,total=30,stage='Train native focus comparison'),replace=(OUT/'progress.json').exists())
    checkpoint=train_model('focus568-'+arm,OUT/'fit',epochs=30,batch_size=64,lr=3e-5,seed=42,
        samples=samples,initialization=initialization,epoch_callback=epoch)
    q.require([r['epoch'] for r in history]==list(range(1,31)),'focus_epochs_incomplete')
    shutil.copyfile(checkpoint,OUT/'final.pt')
    fit=dict(version='native-focus-fit568-v1',arm=arm,initialization=r['model'],corpus=r['corpus'],epochs=30,seed=42,batch=64,
        learningRate=.00003,selection='fixed-last',presentationsPerEpoch=len(samples),
        optimizerUpdates=30*math.ceil(len(samples)/64),uniqueTrainingCrops=len({r['id'] for r in selected}),
        validationCropsRead=0,metricsStatus='provisional',modelAccepted=False)
    q.save(OUT/'fit.json',fit);q.save(OUT/'history.json',history)
    # Reuse the existing scorer's checkpoint contract. This is training ancestry, not weight interpolation.
    q.save(OUT/'ancestry.json',dict(ancestryVerified=True,method='strict-checkpoint-training-initialization',ancestry=dict(base=r['model']),training=pin(OUT/'fit.json')))
    q.save(OUT/'model.json',dict(version='weight-surgery-model-v1',arm='trained-'+arm,threshold=.85,checkpoint=pin(OUT/'final.pt'),edit=pin(OUT/'ancestry.json')))
    q.save(OUT/'benchmark_summary.json',fit);receipt_files_local(['final.pt','fit.json','history.json','ancestry.json','model.json','benchmark_summary.json'])


def score():
    import torch
    import weight_surgery_queue as old
    from eval_focus_ring_detector import predict_torch
    r=resolve_inputs(q.load(OUT.parents[2]/'spec.json')['template'],OUT)
    old.OUT=OUT;old.score()
    result=q.load(OUT/'benchmark_summary.json');suite=document(r['suite']);model=document(r['model'])
    torch.set_num_threads(4);anchors=[]
    for name,rows in suite['ancillary'].items():
        paths=[dict(path=checked(row['image'])) for row in rows]
        old_values=predict_torch(checked(r['base']),paths)
        values=predict_torch(checked(model['checkpoint']),paths)
        anchors.extend(dict(id=name+'-'+str(i),label=row['label'],before=a,after=b) for i,(row,a,b) in enumerate(zip(rows,old_values,values)))
    result.update(anchors=anchors,metricsStatus='provisional')
    q.save(OUT/'benchmark_summary.json',result,replace=True);receipt_files_local(['benchmark_summary.json'],replace=True)


def compare_reports(reference,control,candidate):
    q.require(reference['suiteSHA256']==control['suiteSHA256']==candidate['suiteSHA256'],'focus_comparison_membership')
    q.require(reference['threshold']==control['threshold']==candidate['threshold']==.85,'focus_comparison_threshold')
    baseline={r['id']:r for r in reference['outcomes']}
    expected_anchors={scope+'-'+str(i) for scope,n in (('reserved',16),('calibration',8)) for i in range(n)}
    q.require(len(control['anchors'])==len(candidate['anchors'])==24,'focus_anchor_count')
    q.require({r['id'] for r in control['anchors']}=={r['id'] for r in candidate['anchors']}==expected_anchors,'focus_anchor_membership')
    q.require(all(r['label'] in (0,1) and all(type(r[k]) in (int,float) and math.isfinite(r[k]) and 0<=r[k]<=1 for k in ('before','after')) for report in (control,candidate) for r in report['anchors']),'focus_anchor_scores')
    q.require([(r['id'],r['label'],r['before']) for r in control['anchors']]==[(r['id'],r['label'],r['before']) for r in candidate['anchors']],'focus_anchor_baseline_changed')
    result=[]
    for report in (control,candidate):
        current={r['id']:r for r in report['outcomes']};q.require(current.keys()==baseline.keys(),'focus_case_membership')
        gained=[i for i in current if current[i]['correct'] and not baseline[i]['correct']]
        lost=[i for i in current if baseline[i]['correct'] and not current[i]['correct']]
        wrong=[i for i in current if current[i]['wrong'] and not baseline[i]['wrong']]
        q.require(report['legacyLabels']==reference['legacyLabels'] and len(report['legacyProbabilities'])==len(reference['legacyProbabilities']),'focus_legacy_membership')
        legacy_lost=[i for i,(a,b,y) in enumerate(zip(reference['legacyProbabilities'],report['legacyProbabilities'],report['legacyLabels'])) if (a>=.85)==bool(y) and (b>=.85)!=bool(y)]
        anchor_lost=[r['id'] for r in report['anchors'] if (r['before']>=.85)==bool(r['label']) and (r['after']>=.85)!=bool(r['label'])]
        d=report['development'];anc=report['ancillary']
        q.require(len(report['legacyLabels'])==270,'focus_legacy_count')
        legacy_correct=sum((p>=.85)==bool(y) for p,y in zip(report['legacyProbabilities'],report['legacyLabels']))
        anchor_correct={scope:sum((r['after']>=.85)==bool(r['label']) for r in report['anchors'] if r['id'].startswith(scope+'-')) for scope in ('reserved','calibration')}
        passes=d['D1']>=12 and d['D2']<=8 and d['D3']>=5 and legacy_correct==270 and anchor_correct['reserved']>=14 and anchor_correct['calibration']>=3
        result.append(dict(arm=report['arm'],gains=gained,lostPriorSuccesses=lost,newWrong=wrong,lostLegacy=legacy_lost,lostAncillary=anchor_lost,
            measuredGatesPass=passes,outcome='contradicted' if lost or wrong or legacy_lost or anchor_lost or not passes else 'supported'))
    a={r['id']:r for r in control['outcomes']};b={r['id']:r for r in candidate['outcomes']}
    added=[i for i in a if not a[i]['correct'] and b[i]['correct']]
    lost=[i for i in a if a[i]['correct'] and not b[i]['correct']]
    new_wrong=[i for i in a if not a[i]['wrong'] and b[i]['wrong']]
    old_anchors={r['id']:r for r in control['anchors']};new_anchors={r['id']:r for r in candidate['anchors']}
    matched_anchor_lost=[i for i in old_anchors if (old_anchors[i]['after']>=.85)==bool(old_anchors[i]['label']) and (new_anchors[i]['after']>=.85)!=bool(new_anchors[i]['label'])]
    supported=result[1]['outcome']=='supported' and bool(added) and not lost and not new_wrong and not matched_anchor_lost
    return dict(version='research-condition-v1',outcome='supported' if supported else 'contradicted' if result[1]['outcome']=='contradicted' or lost or new_wrong or matched_anchor_lost else 'inconclusive',
        arms=result,nativeVersusReplayGains=added,nativeVersusReplayLosses=lost,nativeVersusReplayNewWrong=new_wrong,nativeVersusReplayLostAnchors=matched_anchor_lost,modelAccepted=False,metricsStatus='provisional',
        nextAction='If supported, propose independent runtime qualification. Otherwise diagnose native styles and preservation; do not promote or expand a coefficient sweep.')


def compare():
    r=resolve_inputs(q.load(OUT.parents[2]/'spec.json')['template'],OUT)
    result=compare_reports(*[document(r[key]) for key in ('reference','control','native')])
    q.save(OUT/'benchmark_summary.json',result)
    native=document(r['native']);d=native['development']
    trigger=d['D1']>=12 and d['D2']<=8 and any((p>=.85)!=bool(y) for p,y in zip(native['legacyProbabilities'],native['legacyLabels']))
    q.save(OUT/'replay-boost-condition.json',dict(version='research-condition-v1',outcome='supported' if trigger else 'contradicted',reason='Use the predefined replay correction only after focus gates pass and legacy retention fails.',modelAccepted=False,metricsStatus='provisional'))
    receipt_files_local(['benchmark_summary.json','replay-boost-condition.json'])


def receipt_files_local(names,replace=False):
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path=n,sha256=q.digest(OUT/n)) for n in names]),replace=replace)
