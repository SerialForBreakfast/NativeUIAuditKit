"""Account for retained native handoffs without rewriting producer evidence."""
import argparse
import hashlib
from collections import Counter
from pathlib import Path
from PIL import Image
import human_annotation_review as h
from fixture_owned_pairs import member
from harvest_bundle_validation import validate_bundle
from focus_corrected_transition_audit import validate_case, endpoint
from inventory_transition_sources import observed_scroll


def verify_selection(root, selection, *, expected_pairs=24):
    h.require(type(expected_pairs) is int and 1<=expected_pairs<=128,'native76_selection_bound')
    h.require(selection.get('version')==1 and selection.get('pairs')==expected_pairs and
        selection.get('endpoint_images')==2*expected_pairs and selection.get('source_role')=='calibration' and
        selection.get('ancestry')=='fixture_procedural_renderer_v1', 'native76_selection_contract')
    cases=selection['cases'];h.require(len(cases)==expected_pairs and len({c['case_id'] for c in cases})==expected_pairs,'native76_selection_membership')
    checked=[]
    for case in cases:
        bundle=member(root,case['bundle']);names=set()
        for item in case['members']:
            name=item['path'];h.require(name.casefold() not in names,'native76_duplicate_member');names.add(name.casefold())
            path=member(bundle,name)
            h.require(path.is_file() and path.stat().st_size==item['bytes'] and h.sha(path)==item['sha256'],'native76_member_integrity')
        actual={str(p.relative_to(bundle)).casefold() for p in bundle.rglob('*') if p.is_file()}
        h.require(actual==names,'native76_unlisted_member')
        receipt=member(root,case['source_receipt']);manifest=receipt.parent/'campaign-manifest.json'
        export=h.read(receipt)
        h.require(export.get('schema_version')==1 and export.get('outcome')=='completed' and
            export.get('campaign_id','').lower()==case['campaign_id'].lower(), 'native76_source_receipt')
        h.require(type(export.get('input_manifest_bytes')) is int and
            export['input_manifest_bytes']==manifest.stat().st_size and
            export.get('input_manifest_sha256')==h.sha(manifest), 'native76_source_manifest_bytes')
        doc=h.read(manifest);matched=[c for c in doc['cases'] if c['case_id']==case['case_id']]
        h.require(doc['campaign_id'].lower()==case['campaign_id'].lower() and len(matched)==1,'native76_source_case')
        account=export.get('case_accounting',{}).get(case['case_id'],{})
        h.require(account.get('state')=='completed' and account.get('case_id')==case['case_id'] and
            account.get('recipe_hash')==matched[0]['recipe']['recipe_hash'] and
            account.get('files')==case['members'] and
            export.get('files',{}).get(case['case_id'])==case['members'], 'native76_source_case_receipt')
        checked.append((case,bundle,matched[0]))
    return checked


def collection_selection(root):
    """Bind the named 36-case handoff; inspection only, not a producer schema adapter."""
    receipts=sorted(root.glob('*/export-0/campaign-receipt.json'))
    h.require(len(receipts)==4,'collection83_campaign_count')
    entries=[]
    for path in receipts:
        receipt=h.read(path);manifest=h.read(path.parent/'campaign-manifest.json')
        cases=manifest['cases']
        h.require(receipt['cases_count']==len(cases) and
            set(receipt['case_accounting'])==set(receipt['files'])=={c['case_id'] for c in cases},
            'collection83_receipt_accounting')
        for case in cases:
            h.require(case['split_group']=='validation' and
                case['independence_group']=='fixture_procedural_renderer_v1','collection83_source_role')
            bundle=member(path.parent,'splits/validation/'+case['case_id'])
            entries.append(dict(case_id=case['case_id'],campaign_id=manifest['campaign_id'],
                bundle=str(bundle.relative_to(root)),source_receipt=str(path.relative_to(root)),
                members=receipt['files'][case['case_id']]))
    return dict(version=1,pairs=36,endpoint_images=72,source_role='calibration',
        ancestry='fixture_procedural_renderer_v1',cases=entries)


def run_collection(root, output):
    import time
    start=time.monotonic();root=h.local(root);out=h.fresh(output)
    checked=verify_selection(root,collection_selection(root),expected_pairs=36)
    rows=[];pixels=set();files=0;byte_count=0
    for entry,bundle,case in checked:
        transition=bundle/'transition-case.json'
        kind='transition' if transition.exists() else 'appearance'
        if kind=='transition':
            raw=h.read(transition)
            paths=[member(bundle,r['image']) for r in raw['endpoints']]
        else:
            paths=sorted(bundle.glob('*_focused.png'))+sorted(bundle.glob('*_unfocused.png'))
        h.require(len(paths)==2,'collection83_image_count')
        images=[]
        for path in paths:
            with Image.open(path) as im:
                h.require(im.format=='PNG' and 0<im.width*im.height<=20_000_000,'collection83_image_bounds')
                im.load();rgb=im.convert('RGB')
                digest=hashlib.sha256(str(rgb.size).encode()+b'\0'+rgb.tobytes()).hexdigest()
                images.append(dict(**h.ref(path),size=list(rgb.size),decodedSHA256=digest));pixels.add(digest)
        row=dict(caseID=case['case_id'],kind=kind,images=images,recipe=case['recipe'],
            recipeAxes='producer-declared, not consumer-qualified',trainingEligible=False)
        try:
            if kind=='appearance':validate_bundle(bundle)
            else:validate_case(root,transition,case)
            row['consumer']='passed-inspection-only'
        except (ValueError,KeyError,TypeError,OSError) as error:
            row.update(consumer='blocked',blocker=str(error))
        rows.append(row);files+=len(entry['members']);byte_count+=sum(m['bytes'] for m in entry['members'])
    h.require(Counter(r['kind'] for r in rows)=={'appearance':24,'transition':12},'collection83_kind_accounting')
    report=dict(version='native83-inspection-v1',**h.FLAGS,results=rows,pairs=len(rows),
        endpointImages=sum(len(r['images']) for r in rows),uniqueDecodedImages=len(pixels),
        filesVerified=files,memberBytes=byte_count,consumerStates=dict(Counter(r['consumer'] for r in rows)),
        blockers=dict(Counter(r['blocker'] for r in rows if 'blocker' in r)),
        elapsedSeconds=time.monotonic()-start,sourceRole='calibration',
        sourceContract='Unpublished native-collection-v1 remains unqualified.')
    out.mkdir(parents=True);h.write(out/'intake.json',report,sealed=True)
    print({k:report[k] for k in ('pairs','endpointImages','uniqueDecodedImages','filesVerified','memberBytes','consumerStates','blockers','elapsedSeconds')})


def run(root,output):
    root=h.local(root);out=h.fresh(output);out.mkdir(parents=True)
    rich=root/'ttr-native-rich24-20261003-r1'
    selected=verify_selection(rich,h.read(rich/'qualified-cases.json'))
    cases=[]
    for entry,bundle,case in selected:
        cases.append(('rich24',entry['kind'],bundle,case))
    table=root/'ttr-native-table-directional12-20261003-r1'
    for manifest in sorted(table.rglob('campaign-manifest.json')):
        doc=h.read(manifest)
        by_id={c['case_id']:c for c in doc['cases']}
        for path in sorted(manifest.parent.glob('splits/validation/*/transition-case.json')):
            raw=h.read(path);cases.append(('table12','directional',path.parent,by_id[raw['case_id']]))
    h.require(Counter(lane for lane,_,_,_ in cases)=={'rich24':24,'table12':12},'native76_case_accounting')
    results=[];pixels={};images=[]
    for lane,kind,bundle,case in cases:
        record=dict(lane=lane,caseID=case['case_id'],kind=kind,bundle=str(bundle.relative_to(h.ROOT)),
            trainingEligible=False,independentEvaluationEligible=False)
        transition=bundle/'transition-case.json'
        if transition.exists():
            raw=h.read(transition);scroll=observed_scroll(raw)
            record.update(condition=raw['specification']['condition'],observedScroll=scroll[0],scrollEvidence=scroll[1])
            frame_paths=[member(bundle,e['image']) for e in raw['endpoints']]
            for e,path in zip(raw['endpoints'],frame_paths):
                h.require(h.sha(path)==e['capture_endpoint']['frame_png_sha256'] and
                    h.read(bundle/(e['role']+'.json'))==e, 'native76_transition_byte_binding')
            try:
                for role,e in zip(('before','after'),raw['endpoints']):endpoint(root,transition,e,role)
                record['endpointContract']='passed'
            except (ValueError,KeyError,TypeError,OSError) as error:
                record.update(endpointContract='blocked',endpointBlocker=str(error))
            try:
                validate_case(root,transition,case,stationary=scroll[0] is False,
                    directional=lane=='table12' and scroll[0] is not False)
                record.update(consumer='passed-inspection-only')
            except (ValueError,KeyError,TypeError,OSError) as error:
                record.update(consumer='blocked',blocker=str(error))
        else:
            frame_paths=sorted(bundle.glob('*_focused.png'))+sorted(bundle.glob('*_unfocused.png'))
            try:
                validate_bundle(bundle);record.update(consumer='passed-inspection-only')
            except (ValueError,KeyError,TypeError,OSError) as error:
                record.update(consumer='blocked',blocker=str(error))
        h.require(len(frame_paths)==2,'native76_pair_images')
        record['images']=[]
        for path in frame_paths:
            with Image.open(path) as im:
                h.require(im.format=='PNG' and 0<im.width*im.height<=20_000_000,'native76_png_bounds')
                im.load();rgb=im.convert('RGB');digest=hashlib.sha256(str(rgb.size).encode()+b'\0'+rgb.tobytes()).hexdigest()
            ref=h.ref(path);item=dict(**ref,size=list(rgb.size),decodedSHA256=digest)
            record['images'].append(item);images.append(item)
            pixels.setdefault(digest,[]).append(dict(lane=lane,caseID=case['case_id'],image=ref))
        results.append(record)
    report=dict(version='native76-intake-v1',**h.FLAGS,results=results,
        pairs=len(results),endpoints=len(images),uniqueDecodedImages=len(pixels),
        consumerStates=dict(Counter(r['consumer'] for r in results)),
        blockers=dict(Counter(r['blocker'] for r in results if 'blocker' in r)),
        duplicateGroups=[v for v in pixels.values() if len(v)>1],
        roles='Producer calibration retained; inspection only; no training or final evaluation admission.',
        selection=h.ref(rich/'qualified-cases.json'),transfer=h.ref(root/'receipt.json'))
    h.write(out/'intake.json',report,sealed=True)
    print({k:report[k] for k in ('pairs','endpoints','uniqueDecodedImages','consumerStates','blockers')})


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True);p.add_argument('--output',required=True)
    p.add_argument('--collection36',action='store_true',help='Inspect the named native collection handoff; never admit data')
    a=p.parse_args();(run_collection if a.collection36 else run)(a.root,a.output)
