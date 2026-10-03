"""Compare three fixed pixel signals on OCR-corresponded reviewed transitions."""
import argparse
import copy
import json
from collections import Counter
import human_annotation_review as h
import focus_recorded_semantics as semantic
import focus_recorded_transition_eval as evaluate

ARMS=('brightness','growth','combined')


def decision(prediction,arm):
    h.require(arm in ARMS,'unknown_arm')
    if prediction['tracking']['status']=='identical':return 'unchanged'
    if prediction['tracking']['status']!='matched':return 'unavailable'
    if prediction.get('illuminationWarning'):return 'unknown'
    return prediction['decision'] if arm=='combined' else prediction[arm]


def compare(predictions,before,after,matches):
    """Semantic expected identity is evaluated after the pixel-only prediction."""
    b={c['id']:c for c in before};a={c['id']:c for c in after};p={c['id']:c for c in predictions}
    h.require(set(b)==set(p)=={m['before'] for m in matches},'comparison_membership')
    resolved=[m['after'] for m in matches if m['after'] is not None]
    h.require(len(resolved)==len(set(resolved)) and set(resolved)<=set(a),'comparison_after_membership')
    rows=[]
    for match in matches:
        ident=match['before'];prediction=p[ident];target=match['after'];expected=None
        if target:
            states=[c['state'] for c in (b[ident],a[target])]
            h.require(all(s in ('focused','unfocused') for s in states),'comparison_unknown_truth')
            expected='unchanged' if states[0]==states[1] else 'arrival' if states[1]=='focused' else 'departure'
        box=prediction['tracking'].get('afterBounds')
        overlap=evaluate.iou(box,a[target]['bounds']) if box and target else None
        spatial=overlap is not None and overlap>=evaluate.POLICY['minCorrespondenceIoU']
        armrows={}
        for arm in ARMS:
            raw=decision(prediction,arm)
            value=raw if spatial else 'unavailable'
            armrows[arm]=dict(id=ident,scorable=expected is not None,expected=expected,
                rawDecision=raw,decision=value,correct=value==expected if expected is not None else None,
                scoreReason='ocr_semantic_correspondence' if expected is not None else match['reason'])
        rows.append(dict(id=ident,afterControl=target,text=match['text'],expected=expected,
            correspondenceIoU=overlap,trackingAgreesWithSemanticTarget=spatial,prediction=prediction,arms=armrows))
    return rows


def markdown(result):
    lines=['# Recorded Settings signal comparison','',
        'Retrospective development diagnostics. Native OCR supports correspondence; human review supplies focus labels.',
        '', '| Signal | Correct | Wrong | Abstained | Scorable | Coverage |', '|---|---:|---:|---:|---:|---:|']
    for arm,s in result['summaries'].items():
        coverage='unavailable' if s['coverage'] is None else f"{s['coverage']:.1%}"
        lines.append(f"| {arm} | {s['correct']} | {s['wrong']} | {s['abstained']} | {s['scorable']} | {coverage} |")
    lines+=['','## Action results','','| Frames | Titles | Status | Reviewed changes | Combined correct / scored |','|---|---|---|---|---|']
    for a in result['actions']:
        frames='→'.join(str(a['endpoints'][k]['sequence']) for k in ('before','after'))
        titles=a['beforeTitle']+' → '+a['afterTitle'];s=a.get('summaries',{}).get('combined')
        changes=dict(Counter(r['expected'] for r in a.get('controls',[]) if r['expected'] is not None))
        lines.append(f"| {frames} | {titles} | {a['status']} | {changes} | {str(s['correct'])+' / '+str(s['scorable']) if s else 'excluded'} |")
    lines+=['','## Interpretation','',
        'All arms use identical pixels, before-bounds, tracking, semantic membership and fixed thresholds. Unavailable tracking counts as abstention when semantic truth exists.',
        'Changed screen titles are excluded from same-screen focus-switch scoring. Partial/unknown endpoint completeness prevents whole-screen accuracy claims.',
        'This repeatedly examined recording is development evidence, not an independent benchmark or runtime focus-identity qualification.','',
        '## Failures and uncertain controls','', '| Frames | Row | Expected | Brightness | Growth | Combined | Tracking |','|---|---|---|---|---|---|---|']
    for a in result['actions']:
        frames='→'.join(str(a['endpoints'][k]['sequence']) for k in ('before','after'))
        for r in a.get('controls',[]):
            if not all(v['correct'] for v in r['arms'].values()):
                values=' | '.join(r['arms'][arm]['decision'] for arm in ARMS)
                tracking=r['prediction']['tracking'].get('reason',r['prediction']['tracking']['status'])
                lines.append(f"| {frames} | {r['text'].replace('|','/')} | {r['expected']} | {values} | {tracking} |")
    return '\n'.join(lines)+'\n'


def run(semantics_path,output,*,tracker='template'):
    output=h.fresh(output);semantics_path=h.local(semantics_path)
    doc=h.sealed(semantics_path,'focus-recorded-semantics-v1')
    h.require(doc['policy']==semantic.POLICY,'changed_semantic_policy')
    h.require(doc['implementation']==h.ref(h.ROOT/'scripts/focus_recorded_semantics.py'),'changed_semantic_implementation')
    args={k:str(h.checked(h.ROOT,v)) for k,v in doc['inputs'].items() if k!='events'}
    audit,truth,actions,hashes=semantic.inputs(**args)
    raw=h.read(h.checked(h.ROOT,doc['raw']))
    h.require([r['id'] for r in raw['results']]==hashes,'semantic_raw_membership')
    descriptions={r['id']:semantic.describe(truth[r['id']],r) for r in raw['results']}
    h.require(descriptions==doc['descriptions'],'changed_semantic_descriptions')
    expected=[]
    for a in actions:
        b,f=[descriptions[a['endpoints'][k]['sha256']] for k in ('before','after')]
        expected.append(dict(actionID=a['actionID'],endpoints=a['endpoints'],**semantic.correspond(b,f)))
    h.require(expected==doc['actions'],'changed_semantic_matching')
    rows=[];runtime=[]
    for action in expected:
        row=copy.deepcopy(action);rows.append(row)
        if not action['sameTitle']:row['status']='screen-change-excluded';continue
        before,after=[truth[action['endpoints'][k]['sha256']] for k in ('before','after')]
        h.require(all(h.control_label(c) in ('listRow','focus:otherFocusable') for c in before['controls']+after['controls']),
                  'unsupported_settings_row_role')
        predictions,identity=evaluate.predict(before['image'],after['image'],[dict(id=c['id'],bounds=c['bounds']) for c in before['controls']],tracker=tracker)
        if identity and identity not in runtime:runtime.append(identity)
        row.update(status='retrospective-diagnostic',completeEndpoints=before['complete'] and after['complete'],
            controls=compare(predictions,before['controls'],after['controls'],action['matches']))
        row['summaries']={arm:evaluate.summarize([r['arms'][arm] for r in row['controls']]) for arm in ARMS}
    h.require(len(runtime)<=1,'runtime_changed')
    summary={arm:evaluate.summarize([r['arms'][arm] for a in rows for r in a.get('controls',[])]) for arm in ARMS}
    result=dict(version='focus-recorded-comparison-v1',**h.FLAGS,semantics=h.ref(semantics_path),actions=rows,tracker=tracker,
        summaries=summary,runtime=runtime,qualifiedTransitionAccuracy=None,
        implementation=[h.ref(h.ROOT/'scripts'/s) for s in ('focus_recorded_comparison.py','focus_recorded_transition_eval.py',
            'focus_transition_verifier.py','focus_paired_growth.py','focus_recorded_readiness.py')])
    for ref in doc['inputs'].values():h.checked(h.ROOT,ref)
    output.mkdir(parents=True);h.write(output/'comparison.json',result,sealed=True)
    (output/'comparison.md').write_text(markdown(result))
    print(json.dumps(summary));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--semantics',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.semantics,a.output)
