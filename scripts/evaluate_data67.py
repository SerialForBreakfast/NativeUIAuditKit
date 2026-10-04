"""Batch two frozen checkpoints over identical admitted frames and fixed probes."""
import argparse
import time
from collections import Counter
import focus_direct_transition as d
from prepare_transition_inputs import manifest
from prepare_data67 import verify_gate
from diagnose_generalization65 import conditions,counterfactual_summary
from evaluate_direct_transition import parity
from focus_pair_translation import translate
from focus_recorded_transition_eval import iou


def group(row,original_ids):
    return 'development' if row['split']=='development' else 'original24' if row['id'] in original_ids else 'added8'


def summarize(scores):
    result=d.summarize(scores)
    result['decidedFalseChanges']=sum(not r['expectedChange'] and r['prediction']['decision']=='changed' for r in scores)
    result['decidedMissedChanges']=sum(r['expectedChange'] and r['prediction']['decision']=='unchanged' for r in scores)
    return result


def run(candidate,output,temporal=False,localization_replay=None,coverage_second=None):
    start=time.monotonic();out=d.h.fresh(output);candidate=d.h.local(candidate)
    result=d.h.read(candidate);protocol=d.h.read(d.h.checked(d.h.ROOT,result['protocol']))
    d.h.require(coverage_second is None or (temporal and localization_replay is None),'coverage_comparison_mode')
    configuration=d.BROAD_CONFIG if coverage_second else d.TEMPORAL_CONFIG if temporal else d.EXPOSURE_CONFIG
    d.h.require(protocol['configuration']==configuration,'candidate_configuration')
    retained=None;intake_start=time.monotonic()
    if localization_replay is not None:
        d.h.require(temporal,'localization_replay_requires_temporal_pair')
        retained=d.h.sealed(d.h.local(localization_replay),'data67-batched-comparison-v1')
        d.h.require(retained['candidate']==d.h.ref(candidate),'frozen_candidate_changed')
        corpus=d.collect(protocol['sources'])
        d.h.require(corpus['corpusSHA256']==protocol['corpusSHA256']==retained['corpusSHA256'],'frozen_corpus_changed')
        rows=d.admitted(corpus,d.h.read(d.h.checked(d.h.ROOT,protocol['admission'])))
    else:
        d.h.require(protocol['pins']==d.pins(),'candidate_pins')
        _,corpus,rows=manifest(d.h.checked(d.h.ROOT,protocol['preparedInputs']))
    intake_seconds=time.monotonic()-intake_start
    original_ids=verify_gate(protocol['expandedGate'],corpus,rows,protocol['admission'])
    d.h.require(set(result['trainingIDs'])=={r['id'] for r in rows if r['split']=='train'},'candidate_fitted_membership')
    reference_name,candidate_name=('DTM013','DTM014') if coverage_second else ('DTM012','DTM013') if temporal else ('DTM011','DTM012')
    if coverage_second:
        from prepare_coverage70 import verify_gate as coverage_gate
        coverage_gate(protocol['coverageGate'],corpus,rows)
        previous=d.h.sealed(d.h.checked(d.h.ROOT,protocol['coverageGate']),'data67-batched-comparison-v1')
        previous_model=previous['models'][reference_name]
        expected={r['id']:r['prediction'] for r in previous['results'] if r['model']==reference_name and r['condition']=='baseline'}
    elif temporal:
        from prepare_temporal68 import verify_gate as temporal_gate
        temporal_gate(protocol['temporalGate'],corpus,rows)
        previous=d.h.sealed(d.h.checked(d.h.ROOT,protocol['temporalGate']),'data67-batched-comparison-v1')
        previous_model=previous['models'][reference_name]
        expected={r['id']:r['prediction'] for r in previous['results'] if r['model']==reference_name and r['condition']=='baseline'}
    else:
        previous=d.h.sealed(d.h.ROOT/'reports/work/EXPOSURE-64/evaluation.json','direct-checkpoint-evaluation-v1')
        negatives=d.h.sealed(d.h.ROOT/'reports/work/EXPOSURE-64/candidate-negatives.json','retained-negative-evaluation-v1')
        negative_model=negatives['models'][0];previous_model=previous['model']
        d.h.require(negative_model['model']==previous_model,'reference_negative_model')
        expected={r['id']:r['prediction'] for r in previous['results']}
        expected.update({corpus['sources']['negatives']['sha256']+':'+r['id']:r['prediction'] for r in negative_model['results']})
    d.h.require(set(expected)=={r['id'] for r in rows},'reference_baseline_membership')
    dev={r['id']:r['prediction'] for r in result['results']}
    d.h.require(set(dev)=={r['id'] for r in rows if r['split']=='development'},'candidate_development_membership')
    torch=d.torch_runtime();torch.set_num_threads(2);models={}
    refs={reference_name:previous_model,candidate_name:result['model']}
    configurations={reference_name:d.TEMPORAL_CONFIG if coverage_second else d.EXPOSURE_CONFIG,candidate_name:configuration}
    devs={candidate_name:dev};additional=None
    if coverage_second:
        second_path=d.h.local(coverage_second);second=d.h.read(second_path)
        second_protocol=d.h.read(d.h.checked(d.h.ROOT,second['protocol']))
        d.h.require(second_protocol['pins']==d.pins() and second_protocol['configuration']==d.COMPRESSED_CONFIG and
            all(second_protocol[k]==protocol[k] for k in ('corpusSHA256','sources','admission','coverageGate')) and
            set(second['trainingIDs'])==set(result['trainingIDs']),'second_candidate_binding')
        refs['DTM015']=second['model'];configurations['DTM015']=d.COMPRESSED_CONFIG
        devs['DTM015']={r['id']:r['prediction'] for r in second['results']}
        d.h.require(set(devs['DTM015'])==set(dev),'second_development_membership')
        additional=d.h.ref(second_path)
    if retained is not None:d.h.require(refs==retained['models'],'frozen_models_changed')
    for name,ref in refs.items():
        state=torch.load(d.h.checked(d.h.ROOT,ref),map_location='cpu',weights_only=True)
        d.h.require(state['version']==d.VERSION and state['configuration']==configurations[name],'checkpoint_configuration')
        net=d.model(state['configuration']);net.load_state_dict(state['state'],strict=True);net.eval();models[name]=net
    scores=[];counterfactuals=[];rejected=[];decode_seconds=0;encode_seconds=0;forward_seconds=0;diagnostics=[]
    probes=conditions()+[('left-4pct',-.04,0),('right-4pct',.04,0),('up-4pct',0,-.04),('down-4pct',0,.04)]
    for row in rows:
        before=time.monotonic();images=[d.pixels(r) for r in row['images']];decode_seconds+=time.monotonic()-before
        category=group(row,original_ids)
        for condition,x,y in probes:
            pair,truth=translate(images,row['boxes'],round(images[0].width*x),round(images[0].height*y))
            if pair is None:
                rejected.append(dict(id=row['id'],group=category,condition=condition));continue
            before=time.monotonic();encoded=d.encode(*pair);encode_seconds+=time.monotonic()-before
            for name,net in models.items():
                before=time.monotonic();p=d.infer_encoded(net,encoded,pair[0].size);forward_seconds+=time.monotonic()-before
                if condition=='baseline':
                    if name==reference_name:parity(expected[row['id']],p)
                    elif row['id'] in devs[name]:parity(devs[name][row['id']],p)
                    if retained is not None:
                        from localization_diagnostics import diagnose
                        diagnostics.append(dict(id=row['id'],group=category,model=name,endpoints=diagnose(net,encoded,row,p)))
                overlaps=[iou(b,t) if b else 0 for b,t in zip(p['boxes'],truth)]
                scores.append(dict(id=row['id'],group=category,condition=condition,model=name,prediction=p,
                    expectedChange=row['changed'],rawChangeCorrect=(p['changeProbability']>=.5)==row['changed'],
                    boxIoUs=overlaps,bothBoxesCorrect=min(overlaps)>=.5,baseline=None))
        for endpoint,image in zip(('before','after'),images):
            before=time.monotonic();encoded=d.encode(image,image);encode_seconds+=time.monotonic()-before
            for name,net in models.items():
                before=time.monotonic();p=d.infer_encoded(net,encoded,image.size);forward_seconds+=time.monotonic()-before
                a,b=p['boxes']
                counterfactuals.append(dict(id=row['id'],group=category,endpoint=endpoint,model=name,
                    prediction=p,predictedBoxOverlap=iou(a,b) if a and b else 0))
    d.h.require(len(scores)+len(rejected)*len(models)==len(rows)*len(probes)*len(models) and
        len(counterfactuals)==len(rows)*2*len(models),'comparison_accounting')
    summary={name:{g:{c:summarize([r for r in scores if r['model']==name and r['group']==g and r['condition']==c])
        for c,_,_ in probes} for g in ('original24','added8','development')} for name in models}
    duplicated={name:{g:counterfactual_summary([r for r in counterfactuals if r['model']==name and r['group']==g])
        for g in ('original24','added8','development')} for name in models}
    for ref in refs.values():d.h.checked(d.h.ROOT,ref)
    if retained is not None:
        for current,old,keys in ((scores,retained['results'],('model','id','condition')),
                                 (counterfactuals,retained['counterfactuals'],('model','id','endpoint'))):
            expected_rows={tuple(r[k] for k in keys):r for r in old}
            d.h.require(len(current)==len(old)==len(expected_rows),'frozen_replay_membership')
            for row in current:parity(expected_rows[tuple(row[k] for k in keys)]['prediction'],row['prediction'])
        d.h.require(rejected==retained['rejected'],'frozen_rejections_changed')
    report=dict(version='data67-batched-comparison-v1',**d.h.FLAGS,candidate=d.h.ref(candidate),models=refs,
        corpusSHA256=corpus['corpusSHA256'],results=scores,rejected=rejected,counterfactuals=counterfactuals,
        summary=summary,duplicated=duplicated,baselineParityPassed=True,
        elapsedSeconds=time.monotonic()-start,pngDecodeSeconds=decode_seconds,
        stageTiming=dict(intakeSeconds=intake_seconds,encodeSeconds=encode_seconds,forwardAndBoxDecodeSeconds=forward_seconds,
            scope='Wall timers; forward includes input validation and tensor conversion; diagnostics/oracles and other overhead remain in total.'),
        limitations=['Original and added groups are training, Settings previously exposed development; no independent final evaluation.',
            ('DTM013/014/015 all2400updates, same32/5roles; augmentation support/rejections/view exposure differ.' if coverage_second else
             'DTM013/DTM012 both2400updates, same32/5roles; change architecture and gradient routing differ.' if temporal else
             'DTM012 has2400updates versusDTM0111800. Data, class balance and update count differ, architecture unchanged.'),
            'Duplicated images are synthetic zero-difference probes, not real action labels.'],
        implementation=d.h.ref(d.h.ROOT/'scripts/evaluate_data67.py'))
    if additional is not None:
        report['additionalCandidate']=additional
        from prepare_transition_inputs import load as prepared_bank
        fitted=[];training=[r for r in rows if r['split']=='train'];by_id={r['id']:r for r in training}
        for label,source_protocol in (('broad',protocol),('compressed',second_protocol)):
            policy=source_protocol['configuration']['augmentation']
            x,y,_,entries,rejections=prepared_bank(d.h.checked(d.h.ROOT,source_protocol['preparedInputs']),training,policy)
            bank_scores=[]
            for i,entry in enumerate(entries):
                row=by_id[entry['id']];truth=[d.raw_image_box(y[i,k:k+4].tolist(),row['size']) for k in (0,4)]
                for name,net in models.items():
                    p=d.infer_encoded(net,x[i],row['size']);overlaps=[iou(b,t) if b else 0 for b,t in zip(p['boxes'],truth)]
                    bank_scores.append(dict(id=row['id'],condition=entry['condition'],model=name,prediction=p,
                        expectedChange=row['changed'],rawChangeCorrect=(p['changeProbability']>=.5)==row['changed'],
                        bothBoxesCorrect=min(overlaps)>=.5,boxIoUs=overlaps,baseline=None))
            fitted.append(dict(bank=label,policy=policy,preparedInputs=source_protocol['preparedInputs'],rejected=rejections,
                results=bank_scores,summary={name:summarize([r for r in bank_scores if r['model']==name]) for name in models}))
        report['augmentedFit']=fitted
        report['elapsedSeconds']=time.monotonic()-start
    if retained is not None:
        from localization_diagnostics import summarize as geometry_summary
        report['localizationReplay']=dict(source=d.h.ref(d.h.local(localization_replay)),allPredictionsMatch=True,
            details=diagnostics,summary={name:{g:geometry_summary([r for r in diagnostics if r['model']==name and r['group']==g])
                for g in ('original24','added8','development')} for name in models},
            limitation='Ground-truth substitutions are scoring-only oracles, never usable detections.')
    out.parent.mkdir(parents=True,exist_ok=True);d.h.write(out,report,sealed=True)
    for name in models:
        for g in summary[name]:print(name,g,summary[name][g]['baseline'],duplicated[name][g])
    print('seconds',report['elapsedSeconds'],'decoding',decode_seconds);return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',required=True);p.add_argument('--output',required=True)
    p.add_argument('--temporal',action='store_true')
    p.add_argument('--localization-replay',help='Frozen comparison to reproduce exactly with fresh intake and raw geometry diagnostics')
    p.add_argument('--coverage-second',help='Compressed-arm result; --candidate is the broad-translation arm')
    a=p.parse_args();run(a.candidate,a.output,a.temporal,a.localization_replay,a.coverage_second)
