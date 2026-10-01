"""Read producer-indexed owned-artwork diagnostic pairs, never forge harvest receipts."""
from pathlib import PurePosixPath
from PIL import Image
import human_annotation_review as h
from human_corpus_inventory import metadata_hashes
from harvest_sidecar_v2 import scene_check, recipe_hash
from fixture_composition import resolve, owned_artwork

FORMAT='ttr_owned_artwork_native_pairs_v1'
CORRELATION='producer_indexed_native_endpoints_screenshot_time_unbound'


def member(root, name):
    h.require(isinstance(name,str) and name and '\\' not in name,'owned_member_path')
    p=PurePosixPath(name)
    h.require(not p.is_absolute() and '..' not in p.parts and str(p)==name,'owned_member_path')
    raw=root/name
    h.require(not any(p.is_symlink() for p in (raw,*raw.parents)),'owned_symlink_member')
    result=h.local(raw)
    h.require(result.is_relative_to(root),'owned_member_path')
    return result


def inventory(root, protected):
    manifest=h.read(root/'manifest.json');index=h.read(root/'pair-index.json')
    h.require(type(manifest.get('schema_version')) is int and manifest['schema_version']==1 and isinstance(manifest.get('files'),list)
              and 0<len(manifest['files'])<=1000,'owned_manifest')
    h.require(type(index.get('schema_version')) is int and index['schema_version']==1 and index.get('format')==FORMAT and
              isinstance(index.get('pairs'),list) and 0<len(index['pairs'])<=128,'owned_pair_index')
    h.require(not metadata_hashes([manifest,index])&protected,'protected_reference')
    h.require(all(p.get('role')=='diagnostic_unadmitted' for p in index['pairs']),'owned_protected_or_admitted_role')
    refs=[];names=set();total=0
    for record in manifest['files']:
        p=member(root,record['path']);key=record['path'].casefold()
        h.require(key not in names and p.is_file() and not p.is_symlink(),'owned_duplicate_or_missing_member')
        names.add(key);total+=p.stat().st_size
        h.require(type(record['bytes']) is int and 0<=record['bytes']<=32*1024**2 and
                  total<=640*1024**2,'owned_size_budget')
        ref=h.ref(p)
        h.require(ref['sha256']==record['sha256'] and p.stat().st_size==record['bytes'],'owned_member_integrity')
        h.require(ref['sha256'] not in protected,'protected_bytes');refs.append(ref)
    actual={p.relative_to(root).as_posix().casefold() for p in root.rglob('*') if p.is_file()}
    h.require(actual==names|{'manifest.json'} and 'pair-index.json' in names,'owned_unindexed_members')
    return index,[h.ref(root/'manifest.json')]+refs


def source_record(root, protected, pair_ids=None):
    index,refs=inventory(root,protected)
    ids=[p['frame_prefix'] for p in index['pairs']]
    h.require(len(set(ids))==len(ids),'owned_duplicate_pair')
    if pair_ids is not None:
        h.require(isinstance(pair_ids,list) and pair_ids and len(set(pair_ids))==len(pair_ids) and
                  set(pair_ids)<=set(ids),'owned_pair_selection')
    wanted=set(ids if pair_ids is None else pair_ids);rows=[];operations=set()
    for pair in index['pairs']:
        if pair['frame_prefix'] not in wanted:continue
        prefix=pair['frame_prefix'];member(root,prefix)
        target=pair['target_id'];competitor=pair['unfocused_request']
        h.require(isinstance(pair.get('recipe_sha256'),str) and len(pair['recipe_sha256'])==64 and
                  all(c in '0123456789abcdef' for c in pair['recipe_sha256']),'owned_declared_hash')
        h.require(target!=competitor and pair['focused_request']==target and
                  pair['focus_label_source']=='observed_uikit' and pair['directional_success']=='not_measured',
                  'owned_pair_focus_contract')
        recipe_path=member(root,pair['recipe']);recipe=h.read(recipe_path)
        h.require(recipe_hash(recipe)==recipe['recipe_hash'],'owned_recipe_identity')
        recipe_file_matches=h.sha(recipe_path)==pair['recipe_sha256']
        comp=recipe['appearance']['composition'];h.require(comp['version']==2,'owned_composition_version')
        items,_=resolve(comp,recipe,h.require);item=next((i for i in items if i['id']==target),None)
        h.require(item and item['focusable'] and item['style']['focus']['kind']=='native_image','owned_native_target')
        asset=item['content'].get('owned_artwork');h.require(asset is not None,'owned_asset_missing')
        identity=owned_artwork(asset,h.require)
        h.require(asset==h.read(member(root,'assets/'+pair['asset_id']+'.json')) and
                  asset['id']==pair['asset_id']==pair['asset_group'] and
                  asset['structural_family']==pair['structural_family'] and
                  pair['renderer_ancestry']=='fixture_procedural_renderer_v1' and
                  pair['owned_renderer']=='owned-artwork-v1' and isinstance(pair['layout_group'],str),
                  'owned_asset_ancestry_binding')
        h.require(len(pair['frames'])==2,'owned_frame_count');scenes=[];raws=[];images=[]
        for n,(state,expected) in enumerate((('unfocused',competitor),('focused',target))):
            path=member(root,prefix+'-'+state+'.png');raw=h.read(member(root,prefix+'-'+state+'.json'))
            h.require(set(raw)=={'before','after','capture'},'owned_bracket_fields')
            capture=raw['capture']
            h.require(capture.get('state')=='delivered' and capture.get('effectStatus')=='unverified' and
                      isinstance(capture.get('operationID'),str) and (capture['operationID'],capture.get('sequence')) not in operations and
                      type(capture.get('sequence')) is int and capture['sequence']>0 and
                      isinstance(capture.get('simulatorID'),str) and isinstance(capture.get('screenshotReference'),str),
                      'owned_capture_receipt')
            operations.add((capture['operationID'],capture['sequence']))
            with Image.open(path) as im:
                h.require(im.format=='PNG' and 0<im.width*im.height<=16_000_000,'owned_image_dimensions')
                size=im.size;im.verify()
            before,after=raw['before'],raw['after']
            bg=scene_check(before,size,expected);ag=scene_check(after,size,expected)
            h.require(bg==ag and all(before.get(k)==after.get(k) for k in
                       ('recipe','elements','focus_observation','semantic_inventory')),'owned_changed_endpoints')
            h.require(before['recipe']==recipe and type(before.get('monotonic_nanoseconds')) is int and
                      type(after.get('monotonic_nanoseconds')) is int and
                      0<=before['monotonic_nanoseconds']<=after['monotonic_nanoseconds'],'owned_scene_order')
            control=next((e for e in after['elements'] if e['element_id']==target),None)
            h.require(control and control['is_focused']==(state=='focused') and
                      pair['frames'][n]==dict(image=path.name,native_focus=expected,body=control['rendered_body_geometry']),
                      'owned_frame_index_binding')
            h.require(after.get('semantic_inventory',{}).get('coverage')=='complete_declared_composition',
                      'owned_incomplete_inventory')
            scenes.append(after);raws.append(raw);images.append(path.relative_to(root).as_posix())
        u,f=scenes
        h.require(raws[0]['capture']['simulatorID']==raws[1]['capture']['simulatorID'] and
                  u['monotonic_nanoseconds']<=raws[1]['before']['monotonic_nanoseconds'] and
                  u['focus_observation']['generation']<f['focus_observation']['generation'],'owned_pair_order')
        signature=lambda s:{e['element_id']:(e['taxonomy_class'],e.get('parent_element_id'),
            'isSelected' in e.get('accessibility_traits',[])) for e in s['elements']}
        h.require(signature(u)==signature(f),'owned_pair_membership')
        rows.append(dict(id=prefix,recipe=recipe,unfocusedPath=images[0],focusedPath=images[1],
            metadataPath=prefix+'-focused.json',sidecarVersion=None,eligibleForTraining=False,
            sourceRole=pair['role'],sourceAncestry={k:pair[k] for k in ('asset_id','asset_group','structural_family',
                'renderer_ancestry','owned_renderer','layout_group')},assetCanonical=identity,
            observationBinding=dict(baselineScene=u,focusedScene=f,referenceCapture=raws[0],focusedCapture=raws[1],
                correlation=CORRELATION),labelSource='producer_indexed_native_endpoints',
            declaredRecipeFileSHA256=pair['recipe_sha256'],observedRecipeFileSHA256=h.sha(recipe_path),
            admissionBlockers=['screenshot_time_hash_binding_unqualified']+
                ([] if recipe_file_matches else ['pair_index_recipe_file_hash_mismatch'])))
    source=dict(root=str(root.relative_to(h.ROOT)),files=refs,sourceFormat=FORMAT,
        pairIDs=sorted(wanted),sourceRoles={p['frame_prefix']:p['role'] for p in index['pairs']},
        targetCoverage=dict(pairs=len(rows),targetIDs=sorted({p['target_id'] for p in index['pairs'] if p['frame_prefix'] in wanted})))
    return source,dict(usableRows=rows,acceptedRowCount=len(rows),targetCoverage=source['targetCoverage'])
