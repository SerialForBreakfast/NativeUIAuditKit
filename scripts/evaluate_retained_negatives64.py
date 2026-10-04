"""Frozen image-only models on retained native no-scroll negatives; no admission."""
import argparse
from collections import Counter
import re
import time
import focus_direct_transition as d
from focus_corrected_transition_audit import validate_case
from inventory_transition_sources import observed_scroll
from synth05_intake import verify_package
from fixture_owned_pairs import member
from focus_recorded_transition_eval import iou


def connected_components(rows):
    """Count connected pairs sharing decoded pixels, not just distinct case IDs."""
    groups=[]
    for row in rows:
        pixels=set(row['decodedPixelHashes']);ids={row['id']};remaining=[]
        for old_pixels,old_ids in groups:
            if pixels & old_pixels:pixels|=old_pixels;ids|=old_ids
            else:remaining.append((old_pixels,old_ids))
        # A newly merged set can bridge earlier groups; close transitively.
        changed=True
        while changed:
            changed=False;kept=[]
            for old_pixels,old_ids in remaining:
                if pixels & old_pixels:pixels|=old_pixels;ids|=old_ids;changed=True
                else:kept.append((old_pixels,old_ids))
            remaining=kept
        groups=remaining+[(pixels,ids)]
    return [sorted(ids) for _,ids in groups]


def validate_negative(raw,b,a):
    d.h.require(raw['specification']['condition'] in ('boundary_unchanged','content_only'),'negative_condition')
    d.h.require(raw.get('cleanup')=='verified','negative_cleanup')
    d.h.require(observed_scroll(raw)[0] is False,'negative_scroll_unknown_or_changed')
    d.h.require(b['focus']==a['focus'],'negative_native_focus_changed')


def run(source_path,names,output):
    out=d.h.fresh(output);start=time.monotonic();source=d.h.local(source_path)
    doc=d.h.read(source)
    d.h.require(doc['version']=='corrected-transition-audit-v1','negative_source_version')
    root=d.h.checked(d.h.ROOT,doc['manifest']).parent
    manifest=verify_package(root/'file-manifest.json');campaign=d.h.read(root/'campaign-manifest.json')
    cases=[c for c in campaign['cases'] if c['transition']['condition'] in ('boundary_unchanged','content_only')]
    d.h.require(len(cases)==8 and len({c['case_id'] for c in cases})==8,'negative_membership')
    rows=[];blocked=[]
    for case in cases:
        evidence=member(root,f"splits/{case['split_group']}/{case['case_id']}/transition-case.json")
        try:
            raw,b,a=validate_case(root,evidence,case);validate_negative(raw,b,a)
            row=d.record(case['case_id'],'fixture-procedural-renderer-v1','calibration',b,a,False,
                [d.h.ref(evidence),d.h.ref(root/'campaign-manifest.json')],None)
            row['condition']=case['transition']['condition'];row['recipe']=case['recipe'];rows.append(row)
        except (ValueError,KeyError,TypeError,OSError) as error:
            blocked.append(dict(id=case['case_id'],reason=str(error),source=d.h.ref(evidence)))
    t=d.torch_runtime();t.set_num_threads(2);models=[]
    for name in names:
        d.h.require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',name),'negative_model_name')
        result_path=d.h.ROOT/'NativeUITrainer/focus_ring_runs'/name/'result.json';result=d.h.read(result_path)
        checkpoint=d.h.checked(d.h.ROOT,result['model']);state=t.load(checkpoint,map_location='cpu',weights_only=True)
        d.h.require(state['version']==d.VERSION and d.valid_configuration(state['configuration']),'negative_checkpoint')
        net=d.model(state['configuration']);net.load_state_dict(state['state'],strict=True);net.eval();scores=[]
        for row in rows:
            prediction=d.infer(net,*(d.pixels(ref) for ref in row['images']))
            overlaps=[iou(p,b) if p else 0 for p,b in zip(prediction['boxes'],row['boxes'])]
            scores.append(dict(id=row['id'],condition=row['condition'],prediction=prediction,expectedChange=False,
                rawChangeCorrect=prediction['changeProbability']<.5,bothBoxesCorrect=min(overlaps)>=.5,
                boxIoUs=overlaps,baseline=None))
        models.append(dict(name=name,model=result['model'],source=d.h.ref(result_path),results=scores,
            summary=d.summarize(scores),decidedFalseChanges=sum(r['prediction']['decision']=='changed' for r in scores),
            byCondition={c:d.summarize([r for r in scores if r['condition']==c]) for c in ('boundary_unchanged','content_only')}))
        d.h.checked(d.h.ROOT,result['model'])
    d.h.require(verify_package(root/'file-manifest.json')==manifest,'negative_source_changed')
    report=dict(version='retained-negative-evaluation-v1',**d.h.FLAGS,source=d.h.ref(source),manifest=doc['manifest'],
        expected=8,accepted=len(rows),blocked=blocked,records=rows,models=models,
        conditions=dict(Counter(r['condition'] for r in rows)),decodedPixelComponents=connected_components(rows),
        uniqueDecodedFrames=len({v for r in rows for v in r['decodedPixelHashes']}),elapsedSeconds=time.monotonic()-start,
        implementation=d.h.ref(d.h.ROOT/'scripts/evaluate_retained_negatives64.py'),
        limitations=['Calibration-only; same procedural renderer ancestry as training, not independent evaluation.',
            'Unchanged endpoint focus does not prove no transient intermediate focus motion.',
            'Content-only mutation is not a navigation action. Legacy producer conditions remain unchanged.',
            'No labels used as model inputs, no training admission or threshold tuning.'])
    out.parent.mkdir(parents=True,exist_ok=True);d.h.write(out,report,sealed=True)
    print([(m['name'],m['summary']) for m in models]);print('components',len(report['decodedPixelComponents']));return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True)
    p.add_argument('--models',nargs='+',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.source,a.models,a.output)
