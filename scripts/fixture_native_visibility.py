"""Measured native table/collection visibility, pinned to producer 50ff7fd8.

Offscreen native cells may have no instantiated wrapper. Clipped wrappers do not
become usable target boxes; complete planned/visible/excluded accounting is required.
"""
def kind(scene):
    return (((scene.get('recipe') or {}).get('appearance') or {}).get('canvas') or {}).get('presentation')


def visible_membership(scene, require):
    presentation=kind(scene)
    require(presentation in ('native_table_v2','native_collection_v1'),'native_visibility_contract')
    count=scene['recipe']['element_count'];columns=4 if presentation=='native_collection_v1' else 3
    planned={f'grid_cell_{i//columns}_{i%columns}' for i in range(count)}
    inv=scene.get('semantic_inventory') or {};diag=scene['observation_diagnostics']
    exclusions=(diag.get('nativeProbe') or {}).get('exclusionReasons') or {}
    visible={e['element_id'] for e in scene['elements']}
    offscreen='native_collection_offscreen' if columns==4 else 'native_table_offscreen'
    require(isinstance(exclusions,dict) and all(v in ('partially_clipped_bounds','clipped_or_zero_bounds','native_hidden',offscreen) for v in exclusions.values())
        and visible.isdisjoint(exclusions) and visible|set(exclusions)==planned,'native_visibility_accounting')
    require(inv.get('coverage')=='partial' and inv.get('truncated') is False and
        set(inv.get('expected_control_ids',[]))==planned and set(inv.get('visible_control_ids',[]))==visible and
        inv.get('control_exclusions')==inv.get('exclusions')==exclusions,'native_visibility_inventory')
    require(set(diag['requiredIDs'])==visible and set(diag['measuredIDs'])==visible,'native_visibility_measured')
    wrappers={e['id']:e for e in inv.get('elements',[]) if e.get('role')=='control_wrapper'}
    require(visible<=set(wrappers)<=planned,'native_visibility_wrappers')
    for eid,reason in exclusions.items():
        if reason==offscreen:
            require(eid not in wrappers,'native_offscreen_wrapper_conflict')
        elif reason=='native_hidden':
            require(eid in wrappers and (wrappers[eid].get('is_hidden') is True or
                wrappers[eid].get('effective_alpha')==0),'native_hidden_evidence')
        else:
            require(eid in wrappers and wrappers[eid].get('clipping')==
                ('partially_clipped' if reason=='partially_clipped_bounds' else 'fully_clipped'),'native_clipping_evidence')
    require(all(wrappers[eid].get('clipping') is None for eid in visible),'native_visible_clipping')
    require(scene.get('focused_element_id') is None or scene['focused_element_id'] in visible,'native_focused_exclusion')
    return sorted(planned)
