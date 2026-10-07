"""Strict selected schema4 inspection; deliberately does not grant dataset eligibility."""
import hashlib
import base64
import io
import json
import math
from pathlib import Path

from harvest_bundle_validation import _png_size
from fixture_rendered_body import validate as validate_rendered_body

LIMIT = 32 * 1024 * 1024

# This adapter admits only a reviewed, fixed experiment. Inspection stays separate.
REPAIR_VERSION = 'schema4-focus-repair-v1'
REPAIR_CONFIG = dict(epochs=30, batch=64, lr=0.0003, seed=42,
    maxSeconds=86400, model='mobilenetv4_conv_small', augmentation='none',
    selection='fixed-last-epoch', testDuringTraining=False)
RETENTION_VERSION = 'schema4-focus-retention-v1'
RETENTION_CONFIG = {**REPAIR_CONFIG, 'lr': 0.00003}


def repair_protocol(path, arm, run_name, approval_path=None):
    """Check native pairs before the existing trainer reads their crops."""
    import re
    from focus_dataset_contract import ROOT, digest as seal, image, pixel_digest, member
    from focus_learning_experiment import checked
    from focus_runtime import identity
    doc = decode(Path(path).read_bytes())
    retention = doc.get('version') == RETENTION_VERSION
    require(doc.get('version') in (REPAIR_VERSION, RETENTION_VERSION) and arm == 'schema4-repair', 'repair_version')
    config = RETENTION_CONFIG if retention else REPAIR_CONFIG
    require(approval_path is None, 'repair_uses_bound_admission')
    require(doc.get('protocolSHA256') == seal({k:v for k,v in doc.items() if k != 'protocolSHA256'}), 'repair_seal')
    require(doc.get('configuration') == config and doc.get('releaseEligible') is False, 'repair_configuration')
    require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', run_name or '') is not None, 'repair_run_name')
    output = ROOT/'NativeUITrainer/focus_ring_runs'/run_name
    require(not output.exists(), 'output_collision')
    require(doc.get('runtime') == identity(), 'repair_runtime_changed')
    checked(doc['warmCheckpoint'])
    admission = decode(checked(doc['admission']).read_bytes())
    require(admission.get('approved') is True and admission.get('samplesSHA256') == seal(doc['samples']), 'repair_admission')
    require(admission.get('purpose') == 'development-only' and admission.get('visualReview'), 'repair_review')
    checked(admission['campaign'])
    seen=set(); groups={}; pixels={}; pairs={}; train=[]
    for row in doc['samples']:
        require(row['id'] not in seen and row['role'] in ('train','reserved'), 'repair_membership')
        seen.add(row['id'])
        require(type(row['label']) is int and row['label'] in (0,1), 'repair_label')
        group=row['group']; require(isinstance(group,str) and group, 'repair_group')
        require(groups.setdefault(group,row['role']) == row['role'], 'repair_group_leakage')
        root=ROOT/row['root']; key=(row['root'],row['metadata'])
        require(root.resolve().is_relative_to(ROOT) and root.resolve()==root, 'repair_source_boundary')
        if key not in pairs:
            pairs[key]=pair(root,row['metadata'],expected_version=row.get('sidecarVersion',4))
        inspected=pairs[key]
        require(inspected['metadataSHA256'] == row['metadataSHA256'], 'repair_metadata_changed')
        endpoint=inspected['endpoints'][row['label']]
        meta=decode(read(root,row['metadata']))
        role='focused' if row['label'] else 'unfocused'
        require(endpoint['role']==role and endpoint['visibleBody']==row['bounds'], 'repair_geometry')
        frame=dict(path=str((root/meta[role+'_png']).relative_to(ROOT)),sha256=meta[role+'_sha256'])
        image(ROOT,row['crop'],(256,256))
        for ref in (row['crop'],frame):
            value=pixel_digest(ROOT,ref)
            require(pixels.setdefault(value,row['role']) == row['role'], 'repair_pixel_leakage')
        if row['role']=='train':
            train.append(dict(id=row['id'],path=member(ROOT,row['crop']['path']),label=float(row['label']),split='train'))
    for root,name in pairs:
        require(sorted(r['label'] for r in doc['samples'] if r['root']==root and r['metadata']==name)==[0,1], 'repair_partial_pair')
    require(train and any(r['role']=='reserved' for r in doc['samples']), 'repair_missing_role')
    if retention:
        require(admission.get('replaySHA256') == seal(doc['replay']) and
                admission.get('legacyReplayDiagnosticOnly') is True, 'replay_admission')
        source = decode(checked(doc['replayManifest']).read_bytes())
        protected = set()
        by_id = {r['pair_id']:r for r in source['pairs']}
        require(len(by_id)==len(source['pairs']), 'replay_duplicate_manifest_id')
        for row in source['pairs']:
            if row['split'] != 'train':
                for key in ('focused_crop','unfocused_crop'):
                    path = member(ROOT/'dataset/focus_ring', row[key])
                    protected.add(pixel_digest(ROOT,dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))))
        selected=set(); replay_labels={}
        for row in doc['replay']:
            require(row['pairID'] in by_id and row['id'] not in seen, 'replay_membership')
            seen.add(row['id']); source_row=by_id[row['pairID']]
            require(source_row['split']=='train' and type(row['label']) is int and row['label'] in (0,1), 'replay_role')
            key='focused_crop' if row['label'] else 'unfocused_crop'
            require(row['crop']['path']=='dataset/focus_ring/'+source_row[key], 'replay_source')
            image(ROOT,row['crop'],(256,256)); value=pixel_digest(ROOT,row['crop'])
            require(value not in protected and pixels.get(value,'train')=='train', 'replay_pixel_leakage')
            require(replay_labels.setdefault(value,row['label'])==row['label'], 'replay_label_conflict')
            require((row['pairID'],row['label']) not in selected, 'replay_duplicate')
            selected.add((row['pairID'],row['label']))
            train.append(dict(id=row['id'],path=member(ROOT,row['crop']['path']),label=float(row['label']),split='train'))
        require(selected and all((p,1-l) in selected for p,l in selected), 'replay_partial_pair')
    return dict(formatVersion='schema4-focus-repair-preflight-v1', protocolVersion=doc['version'],
        launchEligible=True, releaseEligible=False, configurationValid=True,
        configuration=config, protocolSHA256=doc['protocolSHA256'],
        warmCheckpoint=doc['warmCheckpoint'], output=str(output.relative_to(ROOT)),
        terminalOnly=True), train


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def read(root, relative):
    require(isinstance(relative, str) and relative and '\\' not in relative,
            'unsafe_path')
    p = Path(relative)
    require(not p.is_absolute() and '..' not in p.parts and str(p) == relative,
            'unsafe_path')
    path = root / p
    require(path.resolve() == path and path.is_file(), 'missing_or_linked_file')
    require(path.stat().st_size <= LIMIT, 'file_budget')
    data = path.read_bytes()
    require(len(data) <= LIMIT, 'file_budget')
    return data


def decode(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'duplicate_key')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('nonfinite_json')
    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def box(value):
    require(isinstance(value, list) and len(value) == 4 and
            all(type(x) in (int, float) and math.isfinite(x) for x in value), 'box_type')
    require(value[2] > 0 and value[3] > 0, 'box_size')
    return value


def hydrate_recipe(directory, compact, allow_inline=True):
    require(isinstance(compact, dict), 'recipe_type')
    if 'source_reference' not in compact:
        require(allow_inline, 'source_reference_required')
        return compact, None
    reference=compact['source_reference']
    require(isinstance(reference, dict) and type(reference.get('version')) is int
            and reference['version']==1, 'source_reference_version')
    source_raw=read(directory,reference.get('path'))
    require(type(reference.get('bytes')) is int and len(source_raw)==reference['bytes'], 'source_size')
    require(digest(source_raw)==reference.get('sha256'), 'source_hash')
    source=decode(source_raw)
    require(isinstance(source,dict) and 'source_reference' not in source
            and reference.get('recipe_hash')==compact.get('recipe_hash')
            and isinstance(compact.get('recipe_hash'),str) and len(compact['recipe_hash'])==64,
            'source_identity')
    require(all(source.get(k)==v for k,v in compact.items()
                if k not in ('source_reference','recipe_hash')), 'source_summary_conflict')
    return source,digest(source_raw)


def pair(root, name, *, expected_version=4):
    raw = read(root, name)
    meta = decode(raw)
    require(expected_version in (3,4) and type(meta.get('schema_version')) is int and meta['schema_version'] == expected_version,
            'unsupported_version')
    require(meta.get('bounds_semantics') == 'measured_view_bounds; not_focus_effect_segmentation',
            'bounds_semantics')
    target, competitor = meta.get('focused_element_id'), meta.get('competitor_element_id')
    require(meta.get('pairing_mode') == 'competitor_v1' and isinstance(target, str) and target
            and isinstance(competitor, str) and competitor and target != competitor, 'pair_identity')
    directory = (root / name).parent
    compact = meta['recipe']
    source,source_hash=hydrate_recipe(directory,compact,allow_inline=expected_version==3)
    endpoints = []; generations = []; intervals = []
    for role, capture_key, scene_key, expected in (
            ('unfocused', 'reference_capture', 'baseline_scene', competitor),
            ('focused', 'focused_capture', 'focused_scene', target)):
        png = read(directory, meta[role + '_png']); size = _png_size(png)
        c = meta[capture_key]; scene = meta[scene_key]
        require(c.get('correlation') == 'validated_capture_bracket', 'capture_correlation')
        require(digest(png) == meta[role + '_sha256'] == c.get('frame_png_sha256'), 'image_hash')
        require(size == (c.get('frame_width'), c.get('frame_height')) ==
                (scene.get('scene_width'), scene.get('scene_height')) ==
                (meta.get('scene_width'), meta.get('scene_height')), 'dimensions')
        times = [c[k] for k in ('before_scene_received_host_ns', 'frame_received_host_ns',
                               'after_scene_received_host_ns')]
        require(all(type(t) is int and t >= 0 for t in times) and times == sorted(times), 'clock_order')
        intervals.append(times)
        before, after = c['before_scene'], c['after_scene']
        require(all(before.get(k) == after.get(k) for k in
                    ('recipe', 'elements', 'focus_observation', 'semantic_inventory',
                     'scene_width', 'scene_height', 'is_settled', 'focused_element_id')), 'changed_bracket')
        require(after == scene and meta.get(scene_key + '_before_capture') == before and
                meta.get(scene_key + '_after_capture') == after, 'scene_alias')
        require(scene.get('recipe') == compact and scene.get('is_settled') is True,
                'recipe_or_settlement')
        o = scene['focus_observation']; generation = o.get('generation')
        require(type(generation) is int and generation >= 0 and o.get('verified') is True and
                o.get('source') == 'uikit_focus_system' and o.get('observedID') == expected and
                scene.get('focused_element_id') == expected, 'native_focus')
        generations.append(generation)
        elements = scene['elements']; ids = [e['element_id'] for e in elements]
        require(len(ids) == len(set(ids)) and target in ids, 'target_membership')
        require([e['element_id'] for e in elements if e.get('is_focused') is True] == [expected],
                'element_focus_conflict')
        e = elements[ids.index(target)]; g = e['rendered_body_geometry']
        require(g.get('availability') == 'measured' and type(g.get('version')) is int and g['version'] == 1 and
                g.get('source') == 'native_body_presentation_layer' and
                g.get('coordinate_space') == 'image_top_left_pixels' and
                g.get('role') == 'rendered_control_body' and g.get('element_id') == target and
                type(g.get('generation')) is int and g['generation'] == generation, 'body_identity')
        x, y, w, h = visible = box(g['visible_pixel_bounds']); full = box(g['full_pixel_bounds'])
        require(x >= 0 and y >= 0 and x+w <= size[0]+1e-5 and y+h <= size[1]+1e-5 and
                x >= full[0]-1e-5 and y >= full[1]-1e-5 and
                x+w <= full[0]+full[2]+1e-5 and y+h <= full[1]+full[3]+1e-5, 'body_extent')
        normalized = g['visible_normalized_bounds']
        require(isinstance(normalized, list) and len(normalized) == 4 and
                all(type(a) in (int, float) and math.isfinite(a) and abs(a-b) <= 1e-6
                    for a,b in zip(normalized, [x/size[0], y/size[1], (x+w)/size[0], (y+h)/size[1]])),
                'body_normalization')
        require(validate_rendered_body(g, size, target, generation) == visible,
                'body_unavailable')
        endpoints.append(dict(role=role, visibleBody=visible, fullBody=full,
            clipped=any(abs(a-b) > 1e-5 for a,b in zip(visible, full)),
            nominalDiffers=any(abs(a-b) > 1e-5 for a,b in zip(visible, box(e['pixel_bounds']))),
            unavailableBodies=[a['element_id'] for a in elements
                               if a.get('rendered_body_geometry', {}).get('availability') != 'measured']))
    require(generations[1] > generations[0] and intervals[0][2] <= intervals[1][0], 'pair_order')
    require(all(meta.get(k) == meta['focused_scene'].get(k) for k in
                ('recipe', 'elements', 'focused_element_id', 'is_settled')), 'flat_alias')
    return dict(path=name, metadataSHA256=digest(raw), sourceSHA256=source_hash,
                endpoints=endpoints, trainingEligible=False, state='structurally_reviewed',
                remaining=['exact_source_semantics', 'pixel_review', 'data_role_admission', 'runtime_crop_parity'])


def review(root):
    root = root.absolute()
    require(root.resolve() == root and root.is_dir(), 'input_boundary')
    manifest_raw = read(root, 'subset-manifest.json'); manifest = decode(manifest_raw)
    names = manifest['selected_metadata']
    require(isinstance(names, list) and 0 < len(names) <= 1000 and
            all(isinstance(n, str) for n in names) and len(names) == len(set(names)), 'selection')
    rows = []
    for name in names:
        try:
            rows.append(pair(root, name))
        except (ValueError, OSError, KeyError, TypeError, IndexError, RecursionError) as error:
            rows.append(dict(path=name, state='rejected', reason=str(error), trainingEligible=False))
    return dict(version='schema4-inspection-v1', manifestSHA256=digest(manifest_raw),
                purpose='inspection_only', trainingEligible=False, expected=len(names),
                reviewed=sum(r['state'] == 'structurally_reviewed' for r in rows), rows=rows)


def render_review(root, output, report):
    """Use production makeCrop, never a new Python crop implementation."""
    from PIL import Image
    import focus_runtime as runtime
    require(report['expected'] == report['reviewed'], 'partial_review_no_crops')
    items=[]
    for row in report['rows']:
        meta_raw=read(root,row['path'])
        require(digest(meta_raw)==row['metadataSHA256'],'metadata_changed')
        meta=decode(meta_raw)
        for endpoint in row['endpoints']:
            role=endpoint['role']; relative=str(Path(row['path']).parent/meta[role+'_png'])
            # Revalidate bytes immediately before invoking the production helper.
            raw=read(root,relative)
            require(digest(raw)==meta[role+'_sha256'],'image_changed')
            items.append(dict(id=digest((row['path']+':'+role).encode()),
                path=str(root/relative),sha256=digest(raw),bounds=endpoint['visibleBody']))
    crops=[]
    for batch in runtime.bounded_batches(items):
        reply=runtime.invoke(batch)
        for item,result in zip(batch,reply['results']):
            raw=base64.b64decode(result['png'],validate=True)
            with Image.open(io.BytesIO(raw)) as im:
                im.load();require(im.size==(256,256),'runtime_crop_size')
            name=item['id']+'.png'
            with (output/name).open('xb') as stream:stream.write(raw)
            crops.append(dict(id=item['id'],path=name,sha256=digest(raw),
                              sourceSHA256=item['sha256'],bounds=item['bounds']))
    return dict(purpose='inspection_only',trainingEligible=False,
                runtime=runtime.identity(),preprocessing=runtime.RUNTIME_PREPROCESSING,crops=crops)


def score_review(root, model, report, geometry='endpoint'):
    """Diagnostic responses to unadmitted producer roles, never qualification metrics."""
    import focus_runtime as runtime
    from focus_ring_baseline import model_contract
    require(report == review(root), 'changed_review')
    require(geometry in ('endpoint', 'pair-union'), 'unsupported_diagnostic_geometry')
    require(report['expected'] == report['reviewed'] and 0 < report['reviewed'] <= 20,
            'diagnostic_membership_budget')
    artifact = model_contract(model); identity = runtime.identity()
    items=[]; provenance=[]
    for row in report['rows']:
        meta=decode(read(root,row['path']))
        bounds=[box(e['visibleBody']) for e in row['endpoints']]
        x=min(b[0] for b in bounds); y=min(b[1] for b in bounds)
        union=[x,y,max(b[0]+b[2] for b in bounds)-x,max(b[1]+b[3] for b in bounds)-y]
        for endpoint in row['endpoints']:
            role=endpoint['role']; name=str(Path(row['path']).parent/meta[role+'_png'])
            key=digest((row['path']+':'+role).encode())
            selected=union if geometry=='pair-union' else endpoint['visibleBody']
            items.append(dict(id=key,path=str(root/name),sha256=meta[role+'_sha256'],bounds=selected))
            provenance.append(dict(id=key,pair=row['path'],reportedRole=role,clipped=endpoint['clipped'],
                                   sourceSHA256=meta[role+'_sha256'],bounds=selected))
    scores={}; timings=[]
    for batch in runtime.bounded_batches(items):
        reply=runtime.invoke(batch,model)
        require([v['id'] for v in reply['results']] == [i['id'] for i in batch], 'score_membership')
        timings.append({k:v for k,v in reply.items() if k!='results'})
        for result in reply['results']:
            probability=result.get('probability')
            require(type(probability) in (int,float) and math.isfinite(probability) and 0<=probability<=1,
                    'invalid_probability')
            scores[result['id']]=probability
    require(artifact==model_contract(model) and identity==runtime.identity(),'changed_model_runtime')
    require(report==review(root),'changed_input_during_scoring')
    rows=[dict(**p,probability=scores[p['id']]) for p in provenance]
    pairs=[]
    for row in report['rows']:
        endpoints={v['reportedRole']:v for v in rows if v['pair']==row['path']}
        pairs.append(dict(path=row['path'],focusedProbability=endpoints['focused']['probability'],
            unfocusedProbability=endpoints['unfocused']['probability'],
            difference=endpoints['focused']['probability']-endpoints['unfocused']['probability'],
            clipped=any(v['clipped'] for v in endpoints.values())))
    result = dict(version='schema4-score-diagnostic-v1',purpose='inspection_only',trainingEligible=False,
        modelGateAssessed=False,labelStatus='producer_reported_pending_source_qualification',
        artifact=artifact,runtime=identity,preprocessing=runtime.RUNTIME_PREPROCESSING,
        inspectionSHA256=digest(json.dumps(report,sort_keys=True).encode()),rows=rows,pairs=pairs,
        diagnosticGeometry=geometry,
        timingBatches=timings,timingScope='CPU-only; new process/model load per bounded batch; not deployment latency')
    from focus_evidence import schema4_report
    result['evidence'] = schema4_report(result)
    return result


def compare_geometry(reference, candidate):
    """Compare paired responses, never reinterpret unadmitted roles as truth."""
    for value, geometry in ((reference,'endpoint'),(candidate,'pair-union')):
        require(value.get('version')=='schema4-score-diagnostic-v1' and
                value.get('purpose')=='inspection_only' and value.get('trainingEligible') is False and
                value.get('modelGateAssessed') is False and
                value.get('diagnosticGeometry','endpoint')==geometry, 'comparison_scope')
    for key in ('artifact','runtime','preprocessing','inspectionSHA256','labelStatus'):
        require(key in reference and reference[key]==candidate.get(key),'incompatible_'+key)
    def indexed(value):
        result={}
        for row in value['rows']:
            key=(row['pair'],row['reportedRole']);p=row['probability']
            require(key not in result and key[1] in ('focused','unfocused') and
                    type(p) in (float,int) and math.isfinite(p) and 0<=p<=1,'invalid_comparison_row')
            result[key]=row
        require(result and all((pair,role) in result for pair,_ in result
                               for role in ('focused','unfocused')),'partial_comparison')
        return result
    a,b=indexed(reference),indexed(candidate)
    require(set(a)==set(b),'comparison_membership')
    for key in a:
        require(a[key]['id']==b[key]['id'] and a[key]['clipped']==b[key]['clipped'],
                'comparison_identity')
    pairs=[]
    for pair in sorted({p for p,_ in a}):
        old=a[pair,'focused']['probability']-a[pair,'unfocused']['probability']
        new=b[pair,'focused']['probability']-b[pair,'unfocused']['probability']
        pairs.append(dict(pair=pair,endpointMargin=old,unionMargin=new,marginDelta=new-old,
                          clipped=any(a[pair,r]['clipped'] for r in ('focused','unfocused'))))
    return dict(purpose='inspection_only',trainingEligible=False,modelGateAssessed=False,
                labelStatus=reference['labelStatus'],artifact=reference['artifact'],
                pairs=pairs,positiveMargin=dict(endpoint=sum(p['endpointMargin']>0 for p in pairs),
                                               union=sum(p['unionMargin']>0 for p in pairs)),
                limitation='Both frames determine union box; not single-frame deployable or accuracy evidence')
