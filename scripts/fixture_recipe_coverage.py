"""Map producer recipe declarations to planner families, without reserving splits."""
import argparse
from collections import defaultdict
import re

import human_annotation_review as h
from focus_corpus_planner import slots

STRUCTURES = dict(mixed_aspect_shelves='mixed-aspect-shelf', dense_grids='dense-image-grid',
    hero_with_neighbors='hero-with-neighbors', placeholder_bright_neighbor='placeholder-and-bright-neighbor',
    selected_parent_focused_child='selected-parent-child-focus', strip_with_content='tab-strip-with-content',
    accessories='accessory-rows', long_duplicate_mixed_width='long-label-and-mixed-width-rows',
    dialog_actions='dialog-actions', wide_compact='wide-and-compact-buttons')


def map_catalog(doc, check):
    """Exact producer-catalog join to consumer slots; check verifies pinned file bytes."""
    h.require(doc.get('version')==1 and doc.get('purpose')=='source_review_catalog_not_capture_manifest','unsupported_catalog')
    requested={s['id']:s for s in slots()}; recipes={}; mapped=[]; seen=set()
    for recipe in doc['recipes']:
        path=recipe['path']; h.require(path not in recipes,'duplicate_recipe')
        original=check(recipe)
        h.require(original==recipe['recipe'],'recipe_object_disagreement')
        h.require(recipe['split_membership']=='unreserved','unexpected_reservation')
        recipes[path]=recipe
    for source in doc['sources']: check(source)
    for slot in doc['slots']:
        theme={'high_contrast':'highContrast'}.get(slot['requested_appearance'],slot['requested_appearance'])
        variation=STRUCTURES.get(slot['structure'])
        h.require(variation is not None,'unsupported_structure')
        key='-'.join((slot['family'],slot['requested_role'],variation,theme))
        h.require(key in requested and key not in seen,'missing_or_duplicate_slot')
        seen.add(key); recipe=recipes[slot['candidate_recipe']]
        h.require(slot['candidate_sha256']==recipe['sha256'],'candidate_hash_disagreement')
        h.require(slot['binding']=='unbound' and slot['requested_pairs']==requested[key]['targetPairs'],'changed_slot_request')
        h.require(isinstance(slot['remaining'],list) and bool(slot['remaining']),'missing_gap_accounting')
        mapped.append(dict(consumerSlot=key,producerSlot=slot['id'],candidateRecipe=recipe['path'],
            candidateSHA256=recipe['sha256'],sharedSourceGroup=recipe['shared_source_group'],
            support=slot['support'],remaining=slot['remaining'],roleReserved=None,trainingEligible=False))
    h.require(seen==set(requested),'incomplete_slot_catalog')
    h.require(doc['totals']==dict(slots=60,requested_pairs=480,bound=0),'totals_disagreement')
    return dict(version='fixture-source-catalog-review-v1',recipeCount=len(recipes),sourceCount=len(doc['sources']),
        declaredGroups=sorted({r['shared_source_group'] for r in recipes.values()}),
        mappedSlots=sorted(mapped,key=lambda r:r['consumerSlot']),exactSlotsBound=0,
        requestedPairs=480,trainingEligible=False,independentGroupsEstablished=0)


def map_membership(doc):
    h.require(doc.get('version')==1 and isinstance(doc.get('families'),list) and len(doc['families'])<=4096,'unsupported_membership')
    rows=[]; groups=defaultdict(list); paths=set()
    for entry in doc['families']:
        path=entry.get('recipe_path'); sha=entry.get('recipe_file_sha256')
        h.require(isinstance(path,str) and path and path not in paths,'duplicate_recipe')
        paths.add(path)
        h.require(isinstance(sha,str) and re.fullmatch('[0-9a-f]{64}',sha),'invalid_recipe_digest')
        recipe=entry.get('recipe'); h.require(isinstance(recipe,dict),'missing_recipe')
        appearance=recipe.get('appearance',{}); canvas=appearance.get('canvas',{})
        kind=appearance.get('focus',{}).get('kind'); presentation=canvas.get('presentation')
        family=('tabs' if presentation=='nested_tabs_v1' else 'rows' if presentation=='settings_rows'
                else 'artwork' if kind=='native_image' else 'buttons' if kind=='native_button' else None)
        theme={'high_contrast':'highContrast'}.get(recipe.get('theme'),recipe.get('theme'))
        candidates=[s['id'] for s in slots() if s['family']==family and s['theme']==theme]
        group=entry.get('independence_group')
        h.require(group is None or isinstance(group,str) and group,'invalid_source_group')
        if group: groups[group].append(path)
        rows.append(dict(recipePath=path,producerRecipeFileSHA256=sha,
            originalRecipeBytesVerified=False,embeddedRecipe=recipe,family=family,theme=theme,
            candidateSlots=candidates,exactSlotBinding=None,
            state='family_only_pending_rendered_variation_and_ancestry_review' if candidates else 'unsupported_family_or_theme',
            independenceGroup=group,rendererAncestry=entry.get('renderer_ancestry'),assetAncestry=entry.get('asset_ancestry'),
            roleReserved=None,trainingEligible=False))
    return dict(version='fixture-recipe-coverage-v1', recipes=rows,
        declaredGroups=dict(sorted(groups.items())), independentGroupsEstablished=0,
        exactSlotsBound=0, requestedSlots=len(slots()), trainingEligible=False,
        limitations=['Family/theme matching is not rendered coverage or admission.',
            'Original recipe file digests cannot be verified from embedded JSON objects.',
            'Shared ancestry cannot be split into independent sources by recipe name or seed.'])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--membership',required=True); p.add_argument('--output',required=True)
    p.add_argument('--catalog-root',help='Verify original recipes/sources for the newer exact source catalog')
    args=p.parse_args()
    try:
        source=h.local(args.membership)
        if args.catalog_root:
            root=h.local(args.catalog_root)
            def check(record):
                path=h.local(root/record['path'])
                h.require(path.is_relative_to(root) and not path.is_symlink(),'unsafe_catalog_member')
                h.require(h.sha(path)==record['sha256'],'changed_catalog_member')
                if 'bytes' in record: h.require(path.stat().st_size==record['bytes'],'changed_catalog_size')
                return h.read(path) if path.suffix=='.json' else None
            result=map_catalog(h.read(source),check)
        else:
            result=map_membership(h.read(source))
        result['source']=h.ref(source); h.write(h.fresh(args.output),result)
        print('Recipe mapping verified; 0 slots reserved')
        return 0
    except (ValueError,KeyError,TypeError,OSError) as error:
        print(str(error)); return 2


if __name__=='__main__': raise SystemExit(main())
