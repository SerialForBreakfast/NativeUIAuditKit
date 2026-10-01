"""Offline native-bundle crop QA and sampled review; never capture, infer or admit."""
import argparse
from collections import Counter
import json
from pathlib import Path
import shutil

import human_annotation_review as h
import human_intake_audit as audit
from harvest_bundle_validation import validate_bundle
from harvest_focus_pairs import FOCUSABLE
from human_corpus_inventory import metadata_hashes

VERSION='fixture-native-review-batch-v1'
BODY_VERSION='fixture-native-review-batch-v2'


def preflight(root, protected):
    """Inspect identities and split metadata BEFORE the harvest validator decodes PNGs."""
    index=h.read(root/'dataset-index.json'); rows=h.read(root/'manifest.json')
    h.require(isinstance(rows,list) and len(rows)<=128,'pair_limit')
    h.require(all(isinstance(r,dict) and r.get('split') in ('training','calibration') for r in rows),
              'protected_or_unsupported_split')
    h.require(not (metadata_hashes(index)|metadata_hashes(rows)) & protected,'protected_reference')
    for record in index.get('artifacts',[]):
        path=record.get('path')
        h.require(isinstance(path,str) and Path(path).name==path,'unsafe_member')
        p=h.local(root/path)
        h.require(p.stat().st_size<=32*1024*1024,'member_size_limit')
        h.require(h.sha(p) not in protected,'protected_bytes')


def source_record(root, protected):
    preflight(root,protected)
    contract=validate_bundle(root)
    h.require(len(contract['usableRows'])==contract['acceptedRowCount'],'unusable_pair_membership')
    h.require(all(r['sidecarVersion'] in (2,3) for r in contract['usableRows']),'native_brackets_required')
    index=h.read(root/'dataset-index.json')
    refs=[h.ref(root/name) for name in ('dataset-index.json','harvest-receipt.json')]
    refs += [h.ref(root/a['path']) for a in index['artifacts']]
    return dict(root=str(root.relative_to(h.ROOT)), files=refs, targetCoverage=contract['targetCoverage']),contract


def project(sources, contracts, *, body_geometry=False):
    """Deterministic normalized proposals, with every observed native record accounted."""
    frames=[]; pairs=[]; records=[]; recipes={}; owners={}; pixel_annotations={}
    for source,contract in zip(sources,contracts):
        root=h.ROOT/source['root']; source_key=h.digest(source['files'])[:16]
        for pair in contract['usableRows']:
            binding=pair['observationBinding']; recipe=pair['recipe']
            key=h.digest(dict(source=source_key,recipe=recipe))
            original_ids=sorted({e['element_id'] for role in ('baselineScene','focusedScene') for e in binding[role]['elements']})
            local_ids={eid:f'control-{i:03d}' for i,eid in enumerate(original_ids,1)}
            pair_frames=[]
            for role,scene_key,image_key in [('unfocused','baselineScene','unfocusedPath'),('focused','focusedScene','focusedPath')]:
                scene=binding[scene_key]; inventory=scene.get('semantic_inventory')
                prefix=h.digest(dict(source=source_key,pair=pair['id'],role=role))[:24]
                fid='frame-'+prefix; number=len(frames)+1
                frame=dict(id=fid,number=number,screen='recipe-'+key[:16],context='Native Fixture proposals; review pending',
                    disposition='imported',reasons=[],editorStem=f'{number:03d}-{fid}',
                    image=h.ref(root/pair[image_key]),size=[scene['scene_width'],scene['scene_height']],
                    nativeRecord=h.ref(root/pair['metadataPath']),sourcePairID=pair['id'],sourceRole=role,
                    sourceRoot=source['root'],recipeKey=key,recipe=recipe,proposals=[],nativeUnresolved=False,
                    duplicateOf=None,reviewFindings=[])
                semantics={e['id']:e for e in inventory['elements']} if inventory else {}
                scene_ids={e['element_id'] for e in scene['elements']}
                if inventory is None: frame['reviewFindings'].append('legacy_semantics_unavailable')
                elif inventory['truncated']: frame['reviewFindings'].append('truncated_semantic_inventory')
                for e in scene['elements']:
                    eid=e['element_id']; native=semantics.get(eid,{})
                    reason=None
                    if e['taxonomy_class'] not in FOCUSABLE: reason='unsupported_or_nonfocusable_taxonomy'
                    elif inventory and native.get('focusable') is not True: reason='native_focusability_unknown_or_false'
                    body=e.get('rendered_body_geometry')
                    if body_geometry and reason is None:
                        from fixture_rendered_body import validate as validate_body
                        bounds=validate_body(body,frame['size'],eid,scene['focus_observation']['generation'])
                        if bounds is None:
                            reason='rendered_body_unavailable'
                            frame['nativeUnresolved']=True
                    if reason:
                        records.append(dict(frameID=fid,elementID=eid,disposition='excluded',reason=reason))
                        frame['reviewFindings'].append(reason)
                        continue
                    proposal=dict(id=local_ids[eid],sourceElementID=eid,bounds=e['pixel_bounds'],
                        **{'class':e['taxonomy_class']},state='focused' if e['is_focused'] else 'unfocused',
                        selected=native.get('selected'),accessibilityLabel=native.get('accessibility_label'),
                        declaredParentID=native.get('declared_parent_id'),declaredTaxonomy=native.get('declared_taxonomy'),
                        labelSource='observed_native_bracket',geometryRole='control_wrapper')
                    if body_geometry:
                        proposal.update(bounds=bounds,geometryRole='rendered_control_body',
                            layoutWrapperBounds=e['pixel_bounds'],renderedBodyGeometry=body)
                        if body.get('clipping'):
                            frame['reviewFindings'].append('clipped_rendered_body_occlusion_unmeasured')
                    if native.get('selected') is True and not e['is_focused']:
                        frame['reviewFindings'].append('selected_but_unfocused_control')
                    if native.get('clipping'): frame['reviewFindings'].append('clipped_control')
                    if native.get('declared_defect'): frame['reviewFindings'].append('declared_negative_recipe')
                    frame['proposals'].append(proposal)
                    records.append(dict(frameID=fid,elementID=eid,disposition='proposed',controlID=proposal['id']))
                for eid,e in semantics.items():
                    if eid not in scene_ids:
                        records.append(dict(frameID=fid,elementID=eid,disposition='excluded' if e['role']!='control_wrapper' else 'blocked',
                            reason='semantic_child_not_control' if e['role']!='control_wrapper' else 'no_scene_control_binding'))
                if inventory:
                    records.extend(dict(frameID=fid,elementID=eid,disposition='producer_excluded',reason=reason)
                                   for eid,reason in inventory['exclusions'].items())
                if not frame['proposals'] or len(frame['proposals'])>100:
                    frame.update(disposition='blocked',reasons=['no_supported_controls_or_editor_limit'],nativeUnresolved=True)
                    for record in records:
                        if record['frameID']==fid and record['disposition']=='proposed':
                            record.update(disposition='blocked',reason='editor_limit')
                frame['pixelSHA256']=h.pixel_digest(h.ROOT,frame['image'])
                duplicate_key=(key,frame['pixelSHA256'],h.digest(frame['proposals']))
                pixel_annotations.setdefault(duplicate_key[:2],[]).append((frame,duplicate_key[2]))
                frame['duplicateOf']=owners.get(duplicate_key)
                if not frame['duplicateOf']: owners[duplicate_key]=fid
                frame['reviewFindings']=sorted(set(frame['reviewFindings']))
                frames.append(frame); pair_frames.append(frame)
                if role=='focused' and frame['disposition']=='imported' and not frame['duplicateOf']:
                    recipes.setdefault(key,dict(recipe=recipe,frameID=fid,sourceRoot=source['root']))
            left,right=pair_frames
            other={c['id']:c for c in right['proposals']}
            for c in left['proposals']:
                b=other.get(c['id'])
                if b and c['class']==b['class'] and {c['state'],b['state']}=={'focused','unfocused'}:
                    ids=[left['id'],right['id']] if c['state']=='focused' else [right['id'],left['id']]
                    pairs.append(dict(id='pair-'+h.digest([source_key,pair['id'],c['id']])[:24],
                        frames=ids,controlID=c['id'],sourcePairID=pair['id']))
    h.require(len(frames)<=256,'frame_limit')
    for group in pixel_annotations.values():
        if len({signature for _,signature in group})>1:
            for frame,_ in group: frame['reviewFindings'].append('same_pixels_conflicting_native_proposals')
    for item in recipes.values():
        next(f for f in frames if f['id']==item['frameID'])['reviewFindings'].append('recipe_representative')
    return dict(frames=frames,pairs=pairs,records=records,recipes=recipes)


def validate(path):
    version=h.read(path).get('version')
    h.require(version in (VERSION,BODY_VERSION),'native_review_version')
    batch=h.sealed(path,version)
    h.require(h.ref(h.CATEGORY)==batch['categoryMap'],'taxonomy_changed')
    protected=metadata_hashes(h.read(h.checked(h.ROOT,batch['protectedMetadata'])))
    contracts=[]
    for source in batch['sources']:
        for ref in source['files']: h.checked(h.ROOT,ref)
        expected,contract=source_record(h.local(h.ROOT/source['root']),protected)
        h.require(expected==source,'source_binding_changed'); contracts.append(contract)
    expected=project(batch['sources'],contracts,body_geometry=version==BODY_VERSION)
    for field in ('frames','pairs','records','recipes'):
        h.require(batch[field]==expected[field],'native_review_projection_changed:'+field)
    h.require(not batch['transitions'] and batch['completeFrameCandidates'] is False,'unsupported_native_claim')
    return batch


def prepare(bundles, output, protected_path, *, seed=42, count=8, exception_limit=8, body_geometry=False):
    output=h.fresh(output); protected_path=h.local(protected_path)
    protected_ref=h.ref(protected_path); protected=metadata_hashes(h.read(protected_path))
    roots=sorted(map(h.local,bundles)); h.require(roots and len(roots)<=128 and len(set(roots))==len(roots),'bundle_membership')
    h.require(not any(output.is_relative_to(root) for root in roots),'output_inside_source')
    h.require(type(seed) is int and type(count) is int and 1<=count<=256 and
              type(exception_limit) is int and 0<=exception_limit<=256,'invalid_sampling_limits')
    sources=[]; contracts=[]; outcomes=[]
    for root in roots:
        row=dict(sourceRoot=str(root.relative_to(h.ROOT)),disposition='rejected',reasons=[])
        outcomes.append(row)
        try:
            source,contract=source_record(root,protected)
            sources.append(source); contracts.append(contract)
            row.update(disposition='accepted_for_diagnostic_QA',pairCount=len(contract['usableRows']),
                       targetCoverage=contract['targetCoverage'])
        except (ValueError,OSError,KeyError,TypeError) as error:
            row['reasons']=[str(error)]
            receipt=root/'harvest-receipt.json'
            if receipt.is_file():
                row['receipt']=h.ref(receipt)
                try: row['producerReportedReceipt']=h.read(receipt)
                except (ValueError,OSError): pass
    projection=project(sources,contracts,body_geometry=body_geometry)
    estimated=sum(h.checked(h.ROOT,f['image']).stat().st_size*3 for f in projection['frames'])
    estimated+=sum(len(f['proposals'])*300000 for f in projection['frames'])
    h.require(shutil.disk_usage(h.ROOT).free>estimated+2_000_000_000,'insufficient_space_for_review')
    output.mkdir(parents=True)
    report=dict(version='fixture-batch-QA-v1',**h.FLAGS,bundles=outcomes,
                counts=dict(Counter(r['disposition'] for r in outcomes)),pairCount=len(projection['pairs']),
                nativeRecords=projection['records'],liveSemanticQualified=False)
    h.write(output/'intake.json',dict(report,phase='intake_only'),sealed=True)
    if projection['frames']:
        work=output/'native-review'; (work/'editor').mkdir(parents=True); (output/'sheets').mkdir()
        version=BODY_VERSION if body_geometry else VERSION
        batch=dict(version=version,**h.FLAGS,id='native-'+h.digest([version,sources])[:20],sources=sources,
            protectedMetadata=protected_ref,categoryMap=h.ref(h.CATEGORY),**projection,
            transitions=[],completeFrameCandidates=False,counts=dict(Counter(f['disposition'] for f in projection['frames'])))
        h.write(work/'batch.json',batch,sealed=True)
        for f in batch['frames']:
            if f['disposition']!='imported': continue
            h.copy_ref(f['image'],work/'editor'/(f['editorStem']+'.png'))
            h.write(work/'editor'/(f['editorStem']+'.json'),h.editor_document(batch['id'],f))
        validate(work/'batch.json')
        try:
            qa=h.crop_qa(work/'batch.json',output/'crops')
        except (ValueError,OSError,KeyError,TypeError) as error:
            h.write(output/'failure.json',dict(stage='production_crop_QA',reason=str(error),complete=False))
            raise
        report['cropQA']=h.ref(output/'crops/crop-qa.json')
        report['crops']=dict(expected=qa['expected'],completed=qa['completed'])
        sample=audit.prepare(work/'batch.json',output/'audit',seed=seed,count=count,exception_limit=exception_limit)
        report['audit']=h.ref(output/'audit/plan.json'); report['reviewCounts']=sample['counts']
        report['reviewQueue']=h.ref(output/'audit/combined-queue.json')
        cards=[]
        for n,(key,recipe) in enumerate(sorted(batch['recipes'].items()),1):
            f=next(f for f in batch['frames'] if f['id']==recipe['frameID'])
            file=output/'sheets'/f'{n:03d}-recipe.png'
            h.preview(h.checked(h.ROOT,f['image']),file,f'{n:03d} {f["id"]} — proposals only',f['proposals'])
            details=[{k:c.get(k) for k in ('sourceElementID','class','state','selected','accessibilityLabel','declaredParentID')} for c in f['proposals']]
            cards.append(f'## {n:03d} {key}\n\n{f["id"]}\n\n'
                f'![Native annotation proposals]({file})\n\n```json\n{json.dumps(details,indent=2)}\n```\n')
        (output/'review.md').write_text('# Native recipe QA\n\n'
            'Diagnostic proposals only. Crop generation does not establish rendered-body alignment.\n\n'+'\n'.join(cards))
        validate(work/'batch.json')
    h.require(h.ref(protected_path)==protected_ref,'protected_metadata_changed')
    h.write(output/'report.json',report,sealed=True)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle',action='append',required=True); p.add_argument('--output',required=True)
    p.add_argument('--protected-metadata',required=True)
    p.add_argument('--seed',type=int,default=42); p.add_argument('--count',type=int,default=8)
    p.add_argument('--exception-limit',type=int,default=8)
    p.add_argument('--rendered-body',action='store_true',help='Use measured body bounds; no layout fallback')
    a=p.parse_args()
    try:
        result=prepare(a.bundle,a.output,a.protected_metadata,seed=a.seed,count=a.count,exception_limit=a.exception_limit,
                       body_geometry=a.rendered_body)
        print(json.dumps({k:result[k] for k in ('counts','pairCount','trainingEligible')}))
        return 2 if result['counts'].get('rejected') else 0
    except (ValueError,OSError,KeyError,TypeError) as error:
        print('Batch QA blocked: '+str(error)); return 2


if __name__=='__main__': raise SystemExit(main())
