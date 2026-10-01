"""Offline corpus readiness join. Reports candidates; never admits or trains them."""
import argparse
from collections import defaultdict
from pathlib import Path

import fixture_batch_review as native
import human_annotation_review as h
from focus_corpus_planner import slots, verified_inventory
from human_corpus_inventory import metadata_hashes
from fixture_offline_pipeline import catalog_review

VERSION = 'focus-generation-readiness-v1'


def recipe_identity(recipe):
    # Ignore only capture bookkeeping, not seeds, themes, content or layout.
    return h.digest({k:v for k,v in recipe.items() if k not in ('recipe_hash','step_index')})


def lineage_review(path, root, samples):
    doc=h.read(path); root=h.local(root)
    h.require(doc.get('version')==1 and doc.get('purpose')=='source_overlap_review_not_split_assignment',
              'unsupported_lineage')
    recipes=doc.get('recipes');h.require(isinstance(recipes,list) and 0<len(recipes)<=10000,'lineage_membership')
    baseline=defaultdict(list)
    for s in samples:
        if s.get('recipe'):
            baseline[recipe_identity(s['recipe'])].append(dict(id=s['id'],source=s.get('sourceID'),use=s['use']))
    rows=[];seen=set()
    for e in recipes:
        rel=e['path'];h.require(isinstance(rel,str) and rel not in seen,'duplicate_recipe');seen.add(rel)
        p=h.local(root/rel);h.require(p.is_relative_to(root) and not p.is_symlink(),'unsafe_recipe')
        h.require(p.stat().st_size==e['bytes'] and h.sha(p)==e['sha256'],'changed_recipe')
        h.require(e.get('split')=='unreserved' and e.get('independence')=='unreviewed','unexpected_lineage_role')
        h.require(type(e.get('current_syn04')) is bool and isinstance(e.get('layout_signature'),str),'lineage_fields')
        recipe=h.read(p)
        rows.append(dict(path=rel,recipe=h.ref(p),current=e['current_syn04'],
            layoutSignature=e['layout_signature'],content=e['content'],
            retainedExactRecipeMatches=baseline.get(recipe_identity(recipe),[]),
            relationshipStatus='review_required_not_independent',reservedRole=None))
    edges=doc.get('related_to_current');h.require(isinstance(edges,dict),'lineage_edges')
    current={r['path'] for r in rows if r['current']}
    h.require(set(edges)==current,'lineage_edge_membership')
    for source,links in edges.items():
        h.require(isinstance(links,list) and len(links)<=10000,'lineage_edge_limit')
        for link in links:
            h.require(link.get('path') in seen and link['path']!=source and
                      isinstance(link.get('reasons'),list) and bool(link['reasons']),'invalid_lineage_edge')
    expected=dict(recipe_files=len(rows),current_recipes=len(current),
        current_layout_signatures=len({r['layoutSignature'] for r in rows if r['current']}),reservations=0)
    h.require(doc.get('summary')==expected,'lineage_summary_drift')
    return dict(summary=expected,recipes=rows,declaredRelationships=edges,policy=doc['policy'],
        retainedRecipeMatches=sum(bool(r['retainedExactRecipeMatches']) for r in rows),
        limitation='No pixel-similarity or ancestry independence claim; unmatched recipes remain unknown.')


def candidate_ledger(batch, revision, crops, baseline, protected):
    """Pure join, keeping exact aliases and unreviewed proposals explicit."""
    frames={f['id']:f for f in batch['frames']};h.require(len(frames)==len(batch['frames']),'duplicate_frame')
    crop_map={c['id']:c for c in crops};h.require(len(crop_map)==len(crops),'duplicate_crop')
    expected={f['id']+':'+c['id'] for f in batch['frames'] if f['disposition']=='imported' for c in f['proposals']}
    h.require(set(crop_map)==expected,'crop_membership')
    reviewed={f['id']:f for f in revision['frames'] if f['disposition']=='reviewed'}
    h.require(set(reviewed)<=set(frames),'review_membership')
    for fid,f in reviewed.items():
        original={c['id']:c for c in frames[fid]['proposals']}
        h.require({c['id'] for c in f['controls']}==set(original),'review_control_membership')
        for c in f['controls']:
            h.require(c['disposition']=='reviewed' and all(c[k]==original[c['id']][k] for k in ('bounds','class','state')),
                      'review_changed_requires_new_crop_QA')
    frame_owners=defaultdict(set);crop_owners=defaultdict(set)
    for r in baseline:
        frame_owners[r['framePixels']].add(r['role']);crop_owners[r['cropPixels']].add(r['role'])
    rows=[];pixel_labels=defaultdict(set)
    for f in batch['frames']:
        for c in f['proposals']:
            cid=f['id']+':'+c['id'];pixel=crop_map[cid]['pixelSHA256']
            h.require(pixel not in protected and f['pixelSHA256'] not in protected,'protected_candidate')
            roles=sorted(frame_owners[f['pixelSHA256']]|crop_owners[pixel])
            reasons=['unreserved_source_role','diagnostic_source_not_training_admission']
            if f['duplicateOf']:reasons.append('exact_frame_alias')
            if f['nativeUnresolved']:reasons.append('incomplete_body_inventory')
            if f['id'] in reviewed:
                human='accepted'
            else:
                human='not_individually_reviewed'
            if roles:reasons.append('exact_retained_pixel_overlap')
            if c.get('renderedBodyGeometry',{}).get('clipping'):reasons.append('clipping_occlusion_unmeasured')
            rows.append(dict(id=cid,frameID=f['id'],sourceRoot=f['sourceRoot'],sourcePairID=f['sourcePairID'],
                controlID=c['id'],state=c['state'],bounds=c['bounds'],crop=crop_map[cid]['crop'],
                cropPixels=pixel,framePixels=f['pixelSHA256'],humanReview=human,
                retainedOverlapRoles=roles,reasons=reasons,trainingEligible=False))
            pixel_labels[pixel].add(c['state'])
    for row in rows:
        if len(pixel_labels[row['cropPixels']])>1:row['reasons'].append('same_crop_pixels_conflicting_focus')
    return rows


def family(recipe):
    if recipe.get('archetype')=='action_dialog':return 'buttons'
    presentation=recipe.get('appearance',{}).get('canvas',{}).get('presentation')
    if presentation in ('tabs','nested_tabs_v1'):return 'tabs'
    if presentation=='settings_rows':return 'rows'
    if presentation=='buttons':return 'buttons'
    return 'artwork'


def body_proof(path):
    report=h.sealed(path,'fixture-batch-QA-v1')
    h.require(report['counts'].get('rejected',0)==0,'rejected_body_proof')
    qa_path=h.checked(h.ROOT,report['cropQA']);qa=h.sealed(qa_path,'human-review-crop-qa-v1')
    batch=native.validate(h.checked(h.ROOT,qa['batch']))
    h.require(batch['version']==native.BODY_VERSION,'body_batch_required')
    expected={f['id']+':'+c['id'] for f in batch['frames'] if f['disposition']=='imported' for c in f['proposals']}
    h.require(qa['expected']==qa['completed']==len(qa['crops'])==len(expected) and
              {c['id'] for c in qa['crops']}==expected,'body_proof_crop_membership')
    for c in qa['crops']:h.checked(h.ROOT,c['crop'])
    families=defaultdict(int)
    for f in batch['frames']:
        if f['disposition']=='imported' and not f['nativeUnresolved']:
            families[family(f['recipe'])]+=len(f['proposals'])
    return dict(report=h.ref(path),cropQA=h.ref(qa_path),families=dict(families),
                crops=qa['completed'],humanReviewed=False,scope='delivered_scene_configurations_only')


def prepare(batch_path, revision_path, crop_path, lineage_path, lineage_root, inventory_path, output,
            catalog_path, catalog_root, body_proof_path=None):
    output=h.fresh(output)
    # Existing validator rejects protected source membership before image decode.
    batch=native.validate(batch_path);h.require(batch['version']==native.BODY_VERSION,'body_batch_required')
    revision=h.read_revision(revision_path);h.require(revision['reviewer']['kind']=='human','human_review_required')
    review_batch=h.validate_batch(h.checked(h.ROOT,revision['batch']))
    h.require(review_batch['frames']==batch['frames'] and review_batch['sources']==batch['sources'],'wrong_review_batch')
    for snap in revision['editorSnapshots']:h.checked(h.ROOT,snap)
    qa=h.sealed(crop_path,'human-review-crop-qa-v1');h.require(qa['batch']==h.ref(batch_path),'wrong_crop_batch')
    h.require(qa['expected']==qa['completed']==len(qa['crops']),'incomplete_crop_QA')
    inventory,protocol,audit,protected,_=verified_inventory(inventory_path)
    protected |= metadata_hashes(h.read(h.checked(h.ROOT,batch['protectedMetadata'])))
    crops=[]
    for item in qa['crops']:
        h.require(item['crop']['sha256'] not in protected,'protected_crop_before_decode')
        h.checked(h.ROOT,item['crop'])
        crops.append(dict(item,pixelSHA256=h.pixel_digest(h.ROOT,item['crop'])))
    rows=candidate_ledger(batch,revision,crops,audit['records'],protected)
    lineage=lineage_review(lineage_path,lineage_root,protocol['samples'])
    catalog=catalog_review(catalog_path,catalog_root)
    catalog_slots={s['consumerSlot']:s for s in catalog['coverage']['mappedSlots']}
    recipe_refs={r['path']:r['recipe'] for r in lineage['recipes']}
    additional=body_proof(body_proof_path) if body_proof_path else None
    assignment=[]
    for slot in slots():
        state=('reserve_distinct_validation_sources_first' if slot['intendedRole']=='validation' else
               'body_capability_proven_recipe_and_role_binding_pending' if slot['family']=='artwork' or
               (additional and slot['family'] in additional['families']) else
               'native_body_measurement_pending')
        candidate=catalog_slots[slot['id']]
        ref=recipe_refs[candidate['candidateRecipe']]
        h.require(ref['sha256']==candidate['candidateSHA256'],'catalog_lineage_recipe_disagreement')
        assignment.append(dict(slot,generationState=state,dispatchAuthorized=False,
            candidateRecipe=ref,roleReserved=None,
            sourceGroup=candidate['sharedSourceGroup'],producerRemaining=candidate['remaining']))
    report=dict(version=VERSION,**h.FLAGS,inputs={k:h.ref(p) for k,p in dict(batch=batch_path,
        humanRevision=revision_path,cropQA=crop_path,lineage=lineage_path,baselineInventory=inventory_path,
        catalog=catalog_path).items()},
        sourceCatalogEvidence=catalog,
        additionalBodyProof=additional,
        candidates=rows,nativeAccounting=batch['records'],lineage=lineage,collection=assignment,
        counts=dict(originalFrames=len(batch['frames']),bodyCrops=len(rows),
            individuallyHumanAccepted=sum(r['humanReview']=='accepted' for r in rows),
            uniqueCropPixels=len({r['cropPixels'] for r in rows}),
            exactRetainedOverlap=sum(bool(r['retainedOverlapRoles']) for r in rows),
            duplicateFrameControls=sum('exact_frame_alias' in r['reasons'] for r in rows),
            conflictingFocusCrops=sum('same_crop_pixels_conflicting_focus' in r['reasons'] for r in rows),
            additionalBodyCrops=additional['crops'] if additional else 0,
            newlyAdmittedTraining=0,requestedCollectionPairs=sum(s['targetPairs'] for s in assignment)),
        decision=dict(limitedImageGenerationCapability='demonstrated_in_delivered_evidence',
            fullProductionCorpusReady=False,trainingDispatched=False,
            next='Bind fresh training roles/recipes/assets; qualify remaining recipe coverage; bounded generation then existing QA and assembly.'),
        limitations=['Sampling acceptance applies to the five reviewed frames, not a universal error rate.',
            'Collection targets are not altered qualification thresholds.',
            'Existing sources and training/development/retention/challenge roles are unchanged.',
            'Old lineage-pack captures are wrapper-only historical diagnostics; not new body-qualified members.'])
    output.mkdir(parents=True);h.write(output/'readiness.json',report,sealed=True)
    lines=['# Focus generation readiness','',
        'Delivered body-generation capabilities are listed below. Full production-corpus readiness: **not yet**.', '',
        '| Measure | Count |','| --- | ---: |']
    lines += [f'| {k} | {v} |' for k,v in report['counts'].items()]
    lines += ['', '## Collection assignment','', '| Family / intended role | Target pairs | Next boundary |', '| --- | ---: | --- |']
    for family in ('artwork','tabs','rows','buttons'):
        for role in ('training','validation'):
            members=[s for s in assignment if s['family']==family and s['intendedRole']==role]
            lines.append(f'| {family} / {role} | {sum(s["targetPairs"] for s in members)} | {members[0]["generationState"]} |')
    lines += ['', 'Exact candidate IDs, source links, holds and60collection slots: [readiness.json](readiness.json).',
        'No new capture, admission, role mutation, feature encoding or training was performed.']
    (output/'readiness.md').write_text('\n'.join(lines)+'\n')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('batch','revision','crops','lineage','lineage-root','inventory','output','catalog','catalog-root'):p.add_argument('--'+name,required=True,type=Path)
    p.add_argument('--body-proof',type=Path,help='Optional verified additional native-body batch QA report')
    a=p.parse_args()
    try:
        r=prepare(a.batch,a.revision,a.crops,a.lineage,a.lineage_root,a.inventory,a.output,a.catalog,a.catalog_root,a.body_proof)
        print(r['counts']);return 0
    except (ValueError,OSError,KeyError,TypeError) as error:
        print('Readiness blocked: '+str(error));return 2


if __name__=='__main__':raise SystemExit(main())
