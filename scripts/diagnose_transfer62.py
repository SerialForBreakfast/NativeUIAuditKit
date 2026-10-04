"""Frozen-model order/translation sensitivity. No training or data admission."""
import argparse
import statistics
import focus_direct_transition as d
import evaluate_direct_transition as evaluate
from focus_recorded_transition_eval import iou
from focus_pair_translation import CONDITIONS, transform


def run(result_path, baseline_path, output):
    out=d.h.fresh(output);result=d.h.read(d.h.local(result_path))
    baseline=d.h.read(d.h.local(baseline_path))
    d.h.require(baseline['model']==result['model'],'baseline_model_changed')
    expected={r['id']:r for r in baseline['results']}
    protocol=d.h.read(d.h.checked(d.h.ROOT,result['protocol']))
    corpus=d.collect(protocol['sources'])
    d.h.require(corpus['corpusSHA256']==protocol['corpusSHA256'],'corpus_changed')
    rows=d.admitted(corpus,d.h.read(d.h.checked(d.h.ROOT,protocol['admission'])))
    d.h.require(len(rows)==29 and set(expected)=={r['id'] for r in rows},'membership_changed')
    torch=d.torch_runtime();torch.set_num_threads(2)
    checkpoint=d.h.checked(d.h.ROOT,result['model'])
    state=torch.load(checkpoint,map_location='cpu',weights_only=True)
    d.h.require(state['configuration'] in (d.FULL_FIT_CONFIG,*d.TRANSLATION_CONFIGURATIONS),'unexpected_checkpoint_configuration')
    net=d.model(state['configuration']);net.load_state_dict(state['state'],strict=True);net.eval()
    scores=[];rejected=[]
    for r in rows:
        images=[d.pixels(ref) for ref in r['images']]
        for condition in CONDITIONS:
            pair,truth=transform(images,r['boxes'],condition)
            if pair is None:
                rejected.append(dict(id=r['id'],condition=condition,reason='target_outside_frame'));continue
            prediction=d.infer(net,*pair)
            if condition=='baseline':evaluate.parity(expected[r['id']]['prediction'],prediction)
            overlaps=[iou(p,t) if p else 0 for p,t in zip(prediction['boxes'],truth)]
            scores.append(dict(id=r['id'],split=r['split'],condition=condition,prediction=prediction,baseline=None,
                expectedChange=r['changed'],rawChangeCorrect=(prediction['changeProbability']>=.5)==r['changed'],
                bothBoxesCorrect=min(overlaps)>=.5,boxIoUs=overlaps,
                localization=evaluate.localization(prediction['boxes'],truth,r['size'])))
    summaries=[]
    for split in ('train','development'):
        for condition in CONDITIONS:
            selected=[r for r in scores if r['split']==split and r['condition']==condition]
            summaries.append(dict(split=split,condition=condition,**d.summarize(selected),
                meanEndpointIoU=statistics.mean(v for r in selected for v in r['boxIoUs']) if selected else None))
    report=dict(version='transfer-sensitivity-v1',model=result['model'],source=d.h.ref(d.h.local(result_path)),
        baseline=d.h.ref(d.h.local(baseline_path)),corpusSHA256=corpus['corpusSHA256'],
        conditions=list(CONDITIONS),evaluations=len(scores),rejected=rejected,results=scores,summary=summaries,
        baselineParityPassed=True,trainingEligible=False,modelGatePassed=False,
        implementation=[d.h.ref(d.h.ROOT/'scripts'/s) for s in
            ('diagnose_transfer62.py','focus_pair_translation.py','focus_direct_transition.py','focus_spatial_transition.py')],
        limitations=['Synthetic sensitivity only; neither new corpus nor independent evaluation.',
            'Same fixed checkpoint/thresholds; reversed endpoint labels, unchanged semantic change.',
            'Black-filled translations may introduce distribution shifts; correlation is not causal proof.'])
    d.h.checked(d.h.ROOT,result['model']);out.parent.mkdir(parents=True,exist_ok=True)
    d.h.write(out,report,sealed=True)
    print(summaries);print('evaluated',len(scores),'rejected',len(rejected));return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('result','baseline','output'):p.add_argument('--'+key,required=True)
    a=p.parse_args();run(a.result,a.baseline,a.output)
