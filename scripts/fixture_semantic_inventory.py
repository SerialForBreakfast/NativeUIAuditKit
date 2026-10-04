"""Optional TTR native inventory-v1 checks; partial semantics are not training labels."""
import argparse
from collections import Counter
import math


def require(value, reason):
    if not value:
        raise ValueError('semantic_inventory:'+reason)


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def ids(value):
    return isinstance(value, list) and all(isinstance(v, str) and v for v in value) and len(value)==len(set(value))


def rect(value):
    require(isinstance(value, list) and len(value)==4 and all(number(v) for v in value), 'invalid_bounds')
    require(value[2]>0 and value[3]>0, 'empty_bounds')
    return value


def validate(doc, scene=None, *, transition_visibility=False):
    require(isinstance(doc, dict), 'object_required')
    composition=((scene or {}).get('recipe',{}).get('appearance') or {}).get('composition')
    reference=((scene or {}).get('recipe',{}).get('appearance') or {}).get('referencePack')
    complete=doc.get('coverage')=='complete_declared_composition'
    incomplete=transition_visibility and doc.get('coverage')=='incomplete_declared_composition'
    require(not complete or composition is not None,'complete_without_composition')
    require(type(doc.get('version')) is int and doc['version']==1 and
            doc.get('scope')=='instrumented_scene_components' and (doc.get('coverage') in ('partial','complete_declared_composition') or incomplete), 'unsupported_contract')
    require(ids(doc.get('unavailable_roles')), 'unavailable_roles')
    require(type(doc.get('generation')) is int and 0<=doc['generation']<2**64, 'generation')
    width,height=doc.get('width'),doc.get('height')
    require(all(number(v) and 0<v<=8192 for v in (width,height)), 'dimensions')
    require(type(doc.get('focus_known')) is bool and type(doc.get('truncated')) is bool, 'state_boolean')
    expected=doc.get('expected_control_ids'); exclusions=doc.get('exclusions'); elements=doc.get('elements')
    require(ids(expected) and len(expected)<=4096 and isinstance(exclusions, dict), 'expected_inventory')
    require(all(isinstance(k,str) and k and isinstance(v,str) and v for k,v in exclusions.items()), 'exclusions')
    require(isinstance(elements,list) and len(elements)<=4096 and all(isinstance(e,dict) for e in elements), 'element_limit')
    keys=[e.get('id') for e in elements]
    require(ids(keys), 'duplicate_or_invalid_id')
    by_id={e['id']:e for e in elements}; wrappers={}; focused=[]
    for e in elements:
        role=e.get('role')
        require(role in ('control_wrapper','label_view','image_view') or (complete or incomplete) and role in ('layout_region','decorative_background'), 'unsupported_role')
        if role in ('layout_region','decorative_background'):
            require(e.get('focusable') is False and e.get('input_focused') is False,'decorative_focus')
        require(all(isinstance(e.get(k),str) and e[k] for k in ('native_class','source')), 'native_provenance')
        for field in ('parent_id','declared_parent_id'):
            require(e.get(field) is None or isinstance(e[field],str) and bool(e[field]), 'parent_type')
        parent=e.get('parent_id')
        require(parent is None or parent in by_id and parent!=e['id'], 'parent_closure')
        for field in ('enabled','selected','focusable','input_focused','is_accessibility_element','is_hidden'):
            require(e.get(field) is None or type(e[field]) is bool, 'invalid_'+field)
        alpha=e.get('effective_alpha')
        require(alpha is None or number(alpha) and 0<=alpha<=1,'invalid_effective_alpha')
        container=e.get('scroll_container_id')
        require(container is None or isinstance(container,str) and 0<len(container.encode('utf-8'))<=65536,'invalid_scroll_container_id')
        offset=e.get('scroll_offset_points')
        require(offset is None or isinstance(offset,list) and len(offset)==2 and all(number(v) for v in offset),'invalid_scroll_offset_points')
        if e.get('viewport_pixel_bounds') is not None: rect(e['viewport_pixel_bounds'])
        # Hidden, alpha, clipping and occlusion are distinct observations. Missing
        # optional fields remain unknown; none establish an annotation rectangle.
        require(type(e.get('text_truncated')) is bool, 'text_truncated')
        for field in ('text','accessibility_label','accessibility_value','accessibility_hint','declared_text','declared_taxonomy','declared_defect'):
            # Bound retained payload without treating Swift Character count as Python len.
            require(e.get(field) is None or isinstance(e[field],str) and len(e[field].encode('utf-8'))<=65536, 'invalid_'+field)
        traits=e.get('accessibility_traits_raw')
        require(traits is None or type(traits) is int and 0<=traits<2**64, 'traits_raw')
        if not doc['focus_known']:
            require(e.get('input_focused') is None, 'unknown_focus_has_label')
        if e.get('input_focused') is True:
            require(role=='control_wrapper' and e.get('focusable') is not False, 'focused_noncontrol')
            focused.append(e['id'])
        if role=='control_wrapper':
            wrappers[e['id']]=e
            if doc['focus_known'] and e.get('focusable') is True:
                require(type(e.get('input_focused')) is bool, 'missing_known_control_focus')
        if e.get('focusable') is True and e.get('is_accessibility_element') is not None:
            require(e['is_accessibility_element'], 'focusable_not_accessible')
            require(bool((e.get('accessibility_label') or '').strip()) or e.get('declared_defect')=='missing_label', 'missing_accessible_name')
        x,y,w,h=rect(e.get('full_pixel_bounds'))
        clip=e.get('clipping')
        require(clip in (None,'partially_clipped','fully_clipped'), 'clipping')
        visible=e.get('visible_pixel_bounds'); normalized=e.get('visible_normalized_bounds')
        if clip=='fully_clipped':
            require(visible is None and normalized is None, 'fully_clipped_visible_bounds')
        else:
            vx,vy,vw,vh=rect(visible)
            require(vx>=0 and vy>=0 and vx+vw<=width+1e-6 and vy+vh<=height+1e-6, 'visible_outside_frame')
            # Producer projects pixel bounds and omits clipping for <=1px deltas.
            require(vx>=x-1 and vy>=y-1 and vx+vw<=x+w+1 and vy+vh<=y+h+1, 'visible_outside_full')
            require(isinstance(normalized,list) and len(normalized)==4 and all(number(v) for v in normalized)
                    and 0<=normalized[0]<normalized[2]<=1 and 0<=normalized[1]<normalized[3]<=1, 'normalized_bounds')
            require(all(abs(a-b)<=1e-6 for a,b in zip(normalized,[vx/width,vy/height,(vx+vw)/width,(vy+vh)/height])), 'normalized_disagreement')
            if clip is None:
                require(all(abs(a-b)<=1 for a,b in zip(visible,[x,y,w,h])), 'missing_clipping_state')
    from fixture_native_visibility import kind, visible_membership as native_membership
    if scene is not None and kind(scene) in ('native_table_v2','native_collection_v1'):
        native_membership(scene,require)
    elif reference is not None:
        from fixture_reference import visible_membership
        planned = visible_membership(scene, require)
        visible = doc['visible_control_ids']
        require(set(wrappers) == set(planned), 'reference_wrapper_membership')
        for eid, reason in exclusions.items():
            require(wrappers[eid].get('clipping') ==
                    ('partially_clipped' if reason == 'partially_clipped_bounds' else 'fully_clipped'),
                    'reference_exclusion_evidence')
        require(all(wrappers[eid].get('clipping') is None for eid in visible),
                'reference_visible_clipping')
    elif incomplete:
        require(composition is not None and not doc['truncated'], 'incomplete_composition')
        visible=doc.get('visible_control_ids')
        require(ids(visible) and doc.get('control_exclusions')==exclusions and
                set(visible).isdisjoint(exclusions) and set(visible)|set(exclusions)==set(expected) and
                set(wrappers)==set(expected), 'transition_control_accounting')
        from fixture_composition import resolve
        resolved,_=resolve(composition,scene['recipe'],require)
        require(set(expected)=={i['id'] for i in resolved},'transition_declared_membership')
        for eid,reason in exclusions.items():
            require(reason in ('partially_clipped_bounds','fully_clipped_bounds') and
                    wrappers[eid].get('clipping')==reason.removesuffix('_bounds'), 'transition_exclusion_evidence')
        require(scene is not None and set(visible)=={e['element_id'] for e in scene['elements']},
                'transition_visible_membership')
    else:
        require(set(wrappers).isdisjoint(exclusions) and set(wrappers)|set(exclusions)==set(expected), 'control_accounting')
    if complete:
        from fixture_composition import resolve
        resolved,_=resolve(composition,scene['recipe'],require)
        require(not doc['truncated'] and not exclusions and set(wrappers)=={i['id'] for i in resolved},'composition_complete_membership')
        require({e['id'] for e in elements if e['role']=='layout_region'}=={r['id'] for r in composition['regions']} and
                {e['id'] for e in elements if e['role']=='decorative_background'}=={'composition.background'},'composition_decorative_membership')
        for i in resolved:
            w=wrappers[i['id']]
            require(w.get('focusable')==i['focusable'] and w.get('declared_parent_id')==i['parent'],'composition_declared_binding')
            if i['kind']=='tab': require(w.get('selected')==i['selected'],'composition_tab_selection')
    for eid in keys:
        seen=set(); current=eid
        while current is not None:
            require(current not in seen, 'parent_cycle')
            seen.add(current); current=by_id[current].get('parent_id')
    target=doc.get('focused_id')
    require(target is None or isinstance(target,str) and bool(target), 'focused_id')
    require(doc['focus_known'] or target is None, 'unknown_focus_has_target')
    require(focused==([] if target is None else [target]), 'focus_membership')
    if scene is not None:
        require((width,height)==(scene.get('scene_width'),scene.get('scene_height')), 'scene_dimensions')
        obs=scene.get('focus_observation') or {}
        require(doc['generation']==obs.get('generation'), 'scene_generation')
        require(doc['focus_known'] and target==scene.get('focused_element_id'), 'scene_focus')
        for element in scene.get('elements',[]):
            eid=element['element_id']
            require(eid in wrappers, 'scene_control_missing')
            wrapper=wrappers[eid]
            require(wrapper.get('input_focused')==element.get('is_focused'), 'scene_control_focus')
            # Existing scene bounds are screen-clipped control rectangles.
            bounds=wrapper.get('visible_pixel_bounds')
            require(bounds is not None and all(abs(a-b)<=1.5 for a,b in zip(bounds,element['pixel_bounds'])), 'scene_control_bounds')
    return dict(version=1, coverage=doc['coverage'], elements=len(elements), roles=dict(Counter(e['role'] for e in elements)),
                excludedControls=len(exclusions), truncated=doc['truncated'], focusKnown=doc['focus_known'],
                completeScene=False, trainingEligible=False)


def main():
    import human_annotation_review as h
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True); p.add_argument('--output',required=True)
    args=p.parse_args()
    try:
        source=h.local(args.input); result=validate(h.read(source))
        h.write(h.fresh(args.output),dict(source=h.ref(source),result=result))
        print(result)
        return 0
    except (ValueError,KeyError,TypeError,OSError) as error:
        print(str(error)); return 2


if __name__=='__main__':
    raise SystemExit(main())
