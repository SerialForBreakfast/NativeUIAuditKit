"""Audit delivered native transition brackets and compare fixed pixel signals."""
import argparse
from collections import Counter
from PIL import Image
import human_annotation_review as h
from fixture_owned_pairs import member
from fixture_rendered_body import validate as body_bounds
from harvest_sidecar_v2 import scene_check
from synth05_intake import verify_package


def contract_observations(scene):
    """Describe source disagreements without repairing or qualifying the source."""
    inventory=scene.get('semantic_inventory',{}).get('elements',[])
    counts=Counter(e.get('id') for e in inventory)
    visible={e.get('element_id') for e in scene.get('elements',[])}
    planned=scene.get('focus_observation',{}).get('plannedFocusIDs',[])
    return dict(duplicateSemanticIDs={str(k):v for k,v in counts.items() if v>1},
                plannedIDsAbsentFromVisibleElements=sorted(set(planned)-visible))


def endpoint(root,evidence,capture,image_name, *, transition_visibility=False):
    path=member(root,image_name)
    h.require(path.parent==evidence.parent and path.name==capture['image'],'transition_image_binding')
    ref=h.ref(path);h.require(ref['sha256']==capture['sha256'],'transition_image_hash')
    with Image.open(path) as im:
        h.require(im.format=='PNG' and im.width*im.height<=16_000_000,'transition_image_size')
        size=im.size;im.verify()
    ticks=[capture[k] for k in ('before_scene_received_host_ns','frame_received_host_ns','after_scene_received_host_ns')]
    h.require(all(type(t)is int and t>=0 for t in ticks) and ticks==sorted(ticks),'transition_host_order')
    before,after=capture['before_scene'],capture['after_scene'];focus=after['focused_element_id']
    gen=scene_check(after,size,focus,transition_visibility=transition_visibility)
    h.require(scene_check(before,size,focus,transition_visibility=transition_visibility)==gen and all(before.get(k)==after.get(k) for k in
        ('recipe','elements','focus_observation','semantic_inventory')),'transition_changed_bracket')
    receipt=capture['action_capture_receipt']
    h.require(receipt['state']=='delivered' and type(receipt['sequence'])is int and receipt['sequence']>0 and
        all(isinstance(receipt[k],str) and receipt[k] for k in ('operationID','simulatorID','screenshotReference')),'transition_capture_receipt')
    controls=[];excluded=[]
    for e in after['elements']:
        bounds=body_bounds(e.get('rendered_body_geometry'),size,e['element_id'],gen)
        if bounds is None or e.get('is_hidden') is True:
            excluded.append(e['element_id']);continue
        controls.append(dict(id=e['element_id'],bounds=bounds,state='focused' if e['is_focused'] else 'unfocused'))
    h.require(focus in {c['id'] for c in controls},'transition_focused_body_missing')
    return dict(image=ref,controls=controls,excluded=excluded,focus=focus,ticks=ticks,receipt=receipt,scene=after)


def run(root,output):
    import focus_recorded_transition_eval as evaluate
    import focus_recorded_comparison as comparison
    root=h.local(root);output=h.fresh(output);manifest=verify_package(root/'manifest.json')
    index=h.read(root/'transition-index.json');h.require(index['pairs']==len(index['cases'])==16,'transition_count')
    h.require(len({c['id'] for c in index['cases']})==16,'duplicate_transition_id')
    rows=[];runtimes=[]
    for case in index['cases']:
        row=dict(id=case['id'],condition=case['condition'],status='blocked');rows.append(row)
        try:
            evidence=member(root,case['evidence']);summary=h.read(evidence)
            matches=[p for p in summary['pairs'] if p['id']==case['id']]
            h.require(len(matches)==1,'transition_summary_membership');pair=matches[0]
            row['sourceObservations']={k:contract_observations(pair[k]['after_scene']) for k in ('before','after')}
            h.require(pair['condition']==case['condition'] and pair['ancestry']=='fixture_procedural_renderer_v1','transition_condition_ancestry')
            before,after=[endpoint(root,evidence,pair[k],case[k]) for k in ('before','after')]
            h.require(before['ticks'][-1]<=after['ticks'][0],'transition_pair_order')
            receipts=[before['receipt']]+pair['action_receipts']+[after['receipt']]
            h.require(len(receipts)>=3 and len({r['operationID'] for r in receipts})==1 and
                len({r['simulatorID'] for r in receipts})==1 and all(r['state']=='delivered' for r in receipts),'transition_action_session')
            seq=[r['sequence'] for r in receipts]
            h.require(all(type(n)is int for n in seq) and seq==sorted(set(seq)),'transition_action_sequence')
            recipe=member(root,str(evidence.parent.relative_to(root)/pair['recipe']))
            h.require(h.sha(recipe)==pair['recipe_sha256'] and h.read(recipe)==before['scene']['recipe'],'transition_recipe_binding')
            expected=pair['expected_focus_relation'];actual='same' if before['focus']==after['focus'] else 'different'
            h.require(expected in ('same','different'),'transition_expected_relation')
            predictions,identity=evaluate.predict(before['image'],after['image'],[dict(id=c['id'],bounds=c['bounds']) for c in before['controls']])
            if identity and identity not in runtimes:runtimes.append(identity)
            after_ids={c['id'] for c in after['controls']}
            matches=[dict(before=c['id'],after=c['id'] if c['id'] in after_ids else None,text=c['id'],reason='native_id_not_visible_after') for c in before['controls']]
            controls=comparison.compare(predictions,before['controls'],after['controls'],matches)
            row.update(status='native-bracket-diagnostic',intentMatched=expected==actual,nativeRelation=actual,
                beforeFocus=before['focus'],afterFocus=after['focus'],controls=controls,
                inputs=[before['image'],after['image'],h.ref(evidence),h.ref(recipe)],
                excludedBodies=dict(before=before['excluded'],after=after['excluded']),
                screenshotCorrelation='producer_indexed_hash_and_host_bracket; capture receipt lacks independent rendered-image digest',
                summaries={arm:evaluate.summarize([r['arms'][arm] for r in controls]) for arm in comparison.ARMS})
        except (ValueError,KeyError,TypeError,OSError) as e:row['reason']=str(e)
    h.require(len(runtimes)<=1,'transition_runtime_changed')
    h.require(verify_package(root/'manifest.json')==manifest,'transition_source_changed')
    output.mkdir(parents=True)
    report=dict(version='focus-structural-transition-audit-v1',**h.FLAGS,manifest=manifest,sourceAncestry='fixture_procedural_renderer_v1',
        counts=dict(Counter(r['status'] for r in rows)),pairs=rows,runtime=runtimes,
        summaries={arm:evaluate.summarize([r['arms'][arm] for p in rows for r in p.get('controls',[])]) for arm in comparison.ARMS},
        implementation=[h.ref(h.ROOT/'scripts'/s) for s in ('focus_structural_transition_audit.py','focus_recorded_comparison.py','focus_recorded_transition_eval.py','harvest_sidecar_v2.py','fixture_rendered_body.py')])
    h.write(output/'audit.json',report,sealed=True)
    print(report['counts']);print(report['summaries']);return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.root,a.output)
