"""Bounded HCF adapters. Execution receipts never grant model acceptance."""
import base64
from collections import Counter
import io
import json
import math
import os
import shutil
from pathlib import Path
import statistics
import subprocess
import time
import zipfile

import research_queue as q
from template_inputs398 import checked, pin

OUT = None


def document(ref):
    return q.load(checked(ref))


def resolve_inputs(contract, output):
    dependencies=q.load(output/'dependencies.json') if (output/'dependencies.json').exists() else []
    for dep in dependencies:
        for ref in dep['outputs']: checked(ref)
    resolved={}
    for key,ref in contract['inputs'].items():
        if set(ref)=={'job','output'}:
            matches=[item for dep in dependencies if dep['job']==ref['job'] for item in dep['outputs']
                     if item['path'].endswith('/'+ref['output'])]
            q.require(len(matches)==1,'dependency_input_missing:'+key)
            resolved[key]=matches[0]
        else:resolved[key]=ref
        checked(resolved[key])
    return resolved


def command(argv, output, name, timeout=180):
    cache=output/'cache';cache.mkdir(exist_ok=True)
    env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(cache), MPLCONFIGDIR=str(cache),
             TORCH_HOME=str(cache), HF_HUB_OFFLINE='1', PYTHONPATH=str(q.MODULES))
    start=time.monotonic()
    result=subprocess.run(argv,env=env,cwd=q.ROOT,text=True,capture_output=True,timeout=timeout)
    q.save(output/(name+'.json'),dict(returnCode=result.returncode,seconds=time.monotonic()-start,
                                    stdout=result.stdout[-16000:],stderr=result.stderr[-16000:]))
    q.require(result.returncode==0,'command_failed:'+name)
    return result


def inventory(inputs, parameters, output):
    from hcf_prepare389 import coverage_rows
    doc=document(inputs['catalog'])
    result=coverage_rows(doc['rows'])
    result.update(modelAccepted=False,source=inputs['catalog'])
    q.save(output/'inventory.json',result)


def dataset(inputs, parameters, output):
    from hcf_study371 import validate_groups
    doc=document(inputs['catalog']);policy=document(inputs['policy'])
    q.require(policy.get('version')=='frozen-roles-v1','role_policy_version')
    validate_groups(doc['cases'])
    assigned=policy['groups']; rows=doc['rows']
    q.require(rows and len({r['id'] for r in rows})==len(rows),'membership_duplicate')
    pixels={}
    for row in rows:
        q.require(assigned.get(row['group'])==row['role'],'role_change_refused')
        key=row.get('decodedSHA256',row.get('sha256'))
        q.require(key and pixels.setdefault(key,row['role'])==row['role'],'pixel_role_leak')
    q.require(set(assigned)=={r['group'] for r in rows},'policy_membership')
    q.save(output/'membership.json',dict(version='frozen-membership-v1',rows=rows,policy=inputs['policy'],
        catalog=inputs['catalog'],roleChanges=False,modelAccepted=False))
    if doc.get('version')=='hcf-study-admission-v1':
        q.require(doc.get('trainingAdmitted') is True,'source_not_admitted')
        q.save(output/'admission.json',dict(doc,sourceCatalog=inputs['catalog'],roleChanges=False))


def candidate(inputs, parameters, output):
    from hcf_prepare389 import choose
    review=document(inputs['review']); checkpoint=checked(inputs['checkpoint'])
    choices=choose(review['methods'],review['cropSeeds'])
    selected=parameters['method']
    q.require(selected=='crop-candidate','candidate_architecture_unsupported')
    q.require(choices[selected]['eligibleForExportQualification'],'candidate_regression_gate')
    q.require(review.get('models',{}).get(selected)==inputs['checkpoint'],'review_checkpoint_binding')
    q.save(output/'candidate.json',dict(version='template-candidate-v1',checkpoint=pin(checkpoint),
        review=inputs['review'],architecture='mobilenetv4_conv_small',eligibleForExport=True,
        modelAccepted=False,scope='optional-shadow',focusThreshold=.85,ambiguityThreshold=.70))


def export(inputs, parameters, output):
    doc=document(inputs['candidate']);environment=document(inputs['environment'])
    q.require(doc.get('version')=='template-candidate-v1' and doc.get('eligibleForExport') is True,'candidate_not_eligible')
    q.require(doc.get('architecture')=='mobilenetv4_conv_small','export_architecture')
    weights=checked(doc['checkpoint'])
    interpreter=q.ROOT/'.venv-coreml/bin/python'
    q.require(environment.get('interpreter')=='.venv-coreml/bin/python' and interpreter.is_file(),'export_environment')
    checked(environment['configuration'])
    # B405-128: palette6weights uses the frozen 6-bit palette method of the same compression step.
    q.require(parameters.get('precision') in ('fp16','fp32','int8weights','palette6weights','int8largestweights'),'export_precision')
    if parameters['precision']=='fp16' and 'sourcePackage' in inputs:
        reuse_fp16(inputs, parameters, doc, output)
    elif parameters['precision'] in ('int8weights','palette6weights','int8largestweights'):
        from focus_ring_baseline import artifact_digest
        source=document(inputs['sourcePackage']);report_path=checked(inputs['sourceReport'])
        original=q.load(report_path);package=q.local_path(q.ROOT,source['path'])
        q.require(source.get('digestAlgorithm')=='focus-artifact-v1','compression_digest')
        q.require(artifact_digest(package)==source['sha256'],'compression_source_changed')
        q.require(original['checkpointSHA256']==doc['checkpoint']['sha256'],'compression_checkpoint')
        command([str(interpreter),str(q.MODULES/'compress_focus_ring_coreml.py'),
            '--package',str(package),'--source-report',str(report_path),'--source-sha256',source['sha256'],
            '--output-dir',str(output/'export'),'--experimental-id',parameters['experimentalID']]+
            (['--method',{'palette6weights':'palette6','int8largestweights':'int8largest'}[parameters['precision']]]
             if parameters['precision'] in ('palette6weights','int8largestweights') else []),
            output,'compression',1200)
    else:
        q.require('sourceReport' not in inputs and 'sourcePackage' not in inputs,'unexpected_compression_inputs')
        limit=parameters.get('maximumPackageBytes',5_000_000)
        q.require(type(limit) is int and 0<limit<=50_000_000,'export_size_limit')
        command([str(interpreter),str(q.MODULES/'export_focus_ring_coreml.py'),'--weights',str(weights),
            '--output-dir',str(output/'export'),'--experimental-id',parameters['experimentalID'],
            '--precision',parameters['precision'],'--maximum-package-bytes',str(limit)],output,'conversion',1200)
    report=q.load(output/'export/focus_ring_detector_training_report.json')
    q.require(report['checkpointSHA256']==doc['checkpoint']['sha256'] and report['size_gate_pass'],'export_receipt')
    package=output/'export/FocusRingDetector.mlpackage'
    command(['xcrun','coremlc','compile',str(package),str(output/'export')],output,'compile',180)
    compiled=output/'export/FocusRingDetector.mlmodelc'
    q.require(compiled.is_dir(),'compiled_model_missing')
    files=[pin(p) for p in sorted((output/'export').rglob('*')) if p.is_file()]
    q.save(output/'export.json',dict(version='template-export-v1',files=files,checkpoint=doc['checkpoint'],
        compiled=q.relative(compiled),package=q.relative(package),modelAccepted=False,scope='optional-shadow'))


def reuse_fp16(inputs, parameters, candidate, output):
    """Copy a verified retained package. Preserve its original size failure."""
    from focus_ring_baseline import artifact_digest
    limit=parameters.get('maximumPackageBytes',5_000_000)
    q.require(type(limit) is int and 0<limit<=50_000_000,'export_size_limit')
    source=document(inputs['sourcePackage']);original=document(inputs['sourceReport'])
    package=q.local_path(q.ROOT,source['path'])
    q.require(source.get('digestAlgorithm')=='focus-artifact-v1','export_source_digest')
    q.require(artifact_digest(package)==source['sha256'],'export_source_changed')
    q.require(original['checkpointSHA256']==candidate['checkpoint']['sha256'],'export_source_checkpoint')
    q.require(original.get('method')=='torch.jit.trace/FP16/macOS15/RGB255','export_source_precision')
    q.require(not any(p.is_symlink() for p in package.rglob('*')),'export_source_symlink')
    size=sum(p.stat().st_size for p in package.rglob('*') if p.is_file())
    q.require(size<=limit,'export_size_gate')
    destination=output/'export/FocusRingDetector.mlpackage'
    shutil.copytree(package,destination)
    q.require(artifact_digest(destination)==source['sha256'],'export_copy_changed')
    report=dict(original,experimentalID=parameters['experimentalID'],mlpackage=str(destination),
        sourceReport=inputs['sourceReport'],sourcePackage=inputs['sourcePackage'],
        retainedPackageReused=True,size_bytes=size,size_limit_bytes=limit,size_gate_pass=True,
        size_gate_version='decimal-bytes-v1',releaseEligible=False)
    q.save(destination.parent/'focus_ring_detector_training_report.json',report)


def verified_export(ref):
    doc=document(ref)
    q.require(doc.get('version')=='template-export-v1' and doc.get('modelAccepted') is False,'export_version')
    q.require(doc.get('files'),'export_files_missing')
    for item in doc['files']: checked(item)
    compiled=q.local_path(q.ROOT,doc['compiled'])
    actual={q.relative(p) for p in compiled.rglob('*') if p.is_file()}
    expected={r['path'] for r in doc['files'] if r['path'].startswith(doc['compiled']+'/')}
    q.require(actual and actual==expected,'compiled_membership_changed')
    package=q.local_path(q.ROOT,doc['package'])
    q.require({q.relative(p) for p in package.rglob('*') if p.is_file()}==
              {r['path'] for r in doc['files'] if r['path'].startswith(doc['package']+'/')},'package_membership_changed')
    return doc,compiled


def runtime_items(ref):
    doc=document(ref)
    q.require(doc.get('version')=='focus-runtime-items-v1','runtime_membership_version')
    rows=doc['rows']
    q.require(1<=len(rows)<=16 and len({r['id'] for r in rows})==len(rows),'runtime_membership')
    items=[]
    for row in rows:
        q.require(row['role']=='development' and row['label'] in (0,1),'runtime_role')
        path=checked(row['image']);box=row['bounds']
        q.require(len(box)==4 and all(type(v) in (int,float) and math.isfinite(v) for v in box),'runtime_bounds')
        items.append(dict(id=row['id'],path=str(path),sha256=row['image']['sha256'],bounds=box))
    return rows,items


def vision(items, compiled, output, name):
    tool=q.ROOT/'.build/standard392-swift/arm64-apple-macosx/debug/FocusRingTool'
    q.require(tool.is_file(),'vision_tool_missing')
    request=dict(version=1,root=str(q.ROOT),mode='vision',model=str(compiled),items=items)
    cache=output/'cache';cache.mkdir(exist_ok=True)
    process=subprocess.run([str(tool)],input=json.dumps(request),capture_output=True,text=True,timeout=120,
                           env=dict(os.environ,TMPDIR=str(cache)))
    q.save(output/(name+'-process.json'),dict(returnCode=process.returncode,stderr=process.stderr[-4000:]))
    q.require(process.returncode==0,'vision_failed')
    reply=json.loads(process.stdout)
    q.require([r['id'] for r in reply['results']]==[r['id'] for r in items],'vision_membership_changed')
    return reply


def parity(inputs, parameters, output):
    import numpy as np
    import torch
    from PIL import Image
    import focus_runtime
    from train_focus_ring_detector import load_mobilenetv4_conv_small
    doc,compiled=verified_export(inputs['export']);rows,items=runtime_items(inputs['membership'])
    focus_runtime.TOOL=q.ROOT/'.build/standard392-swift/arm64-apple-macosx/debug/FocusRingTool'
    crops=focus_runtime.invoke(items)
    arrays=[]
    for row in crops['results']:
        with Image.open(io.BytesIO(base64.b64decode(row['png'],validate=True))) as image:
            arrays.append(np.array(image.convert('RGB'),copy=True))
    torch.set_num_threads(2)
    network=load_mobilenetv4_conv_small()(pretrained=False,num_classes=1).eval()
    network.load_state_dict(torch.load(checked(doc['checkpoint']),map_location='cpu',weights_only=True)['state_dict'])
    with torch.no_grad():
        values=torch.sigmoid(network(torch.from_numpy(np.stack(arrays)).permute(0,3,1,2).float()/255)).reshape(-1).tolist()
    observed=vision(items,compiled,output,'vision')
    from focus_export_parity import compare
    comparison=compare([dict(id=r['id'],label=r['label'],probability=p) for r,p in zip(rows,values)],
        [dict(id=r['id'],label=r['label'],probability=p['probability']) for r,p in zip(rows,observed['results'])])
    q.save(output/'parity.json',dict(version='template-parity-v1',comparison=comparison,export=inputs['export'],
        membership=inputs['membership'],observed=observed,modelAccepted=False,backend='Vision-cpuOnly'))
    q.require(comparison['passed'],'parity_failed')


def runtime(inputs, parameters, output):
    doc,compiled=verified_export(inputs['export']);rows,items=runtime_items(inputs['membership'])
    parity_doc=document(inputs['parity'])
    q.require(parity_doc['export']==inputs['export'] and parity_doc['comparison']['passed'],'runtime_parity_required')
    repetitions=parameters['repetitions']
    q.require(type(repetitions) is int and 3<=repetitions<=10,'runtime_repetitions')
    replies=[vision(items,compiled,output,f'run-{i}') for i in range(repetitions)]
    values=sorted(r['inferenceMilliseconds'] for doc in replies for r in doc['results'])
    q.save(output/'runtime.json',dict(version='template-runtime-v1',samples=len(values),medianMilliseconds=statistics.median(values),
        p95Milliseconds=values[math.ceil(.95*len(values))-1],loadMilliseconds=[d['modelLoadMilliseconds'] for d in replies],
        export=inputs['export'],modelAccepted=False,backend='Vision-cpuOnly',
        limitation='New helper process per repetition. OS caches are uncontrolled. No ANE, physical-device, or proposal timing claim.'))


def package(inputs, parameters, output):
    doc,compiled=verified_export(inputs['export']);parity_doc=document(inputs['parity']);runtime_doc=document(inputs['runtime'])
    license_path=checked(inputs['license'])
    q.require(license_path.stat().st_size>0,'license_empty')
    q.require(parity_doc['export']==inputs['export'] and parity_doc['comparison']['passed'],'package_parity')
    q.require(runtime_doc['export']==inputs['export'],'package_runtime_binding')
    package_root=q.local_path(q.ROOT,doc['package'])
    files=[p for p in sorted(package_root.rglob('*')) if p.is_file()]
    q.require(files and not any(p.is_symlink() for p in package_root.rglob('*')),'package_members')
    with zipfile.ZipFile(output/'experimental-model.zip','x',compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files: archive.write(path,'model.mlpackage/'+str(path.relative_to(package_root)))
        archive.write(license_path,'LICENSE.txt')
    q.save(output/'bundle.json',dict(version='template-bundle-v1',archive=pin(output/'experimental-model.zip'),
        export=inputs['export'],parity=inputs['parity'],runtime=inputs['runtime'],license=inputs['license'],
        modelAccepted=False,navigationAuthority=False,scope='optional-shadow',
        rollback='Remove the optional experimental selection. Keep the existing Standard model selected.'))


def consumer(inputs, parameters, output):
    bundle=document(inputs['bundle']);receipt=document(inputs['receipt']);expected=document(inputs['expected'])
    checked(bundle['archive'])
    q.require(receipt.get('version')=='ttr-model-inference-v1','consumer_receipt_version')
    q.require(receipt.get('bundleSHA256')==inputs['bundle']['sha256'],'consumer_bundle_mismatch')
    q.require(receipt.get('backend')=='Vision' and receipt.get('navigationAuthority') is False,'consumer_mode')
    actual=receipt['results'];reference=expected['results']
    q.require(reference and [r['id'] for r in actual]==[r['id'] for r in reference],'consumer_membership')
    q.require(len({r['id'] for r in actual})==len(actual),'consumer_duplicates')
    for a,b in zip(actual,reference):
        q.require(all(type(r.get('score')) in (int,float) and math.isfinite(r['score']) and 0<=r['score']<=1 for r in (a,b)),
                  'consumer_score')
        q.require(abs(a['score']-b['score'])<=.01 and (a['score']>=.85)==(b['score']>=.85),'consumer_parity')
    q.save(output/'verification.json',dict(version='template-consumer-verification-v1',receipt=inputs['receipt'],
        bundle=inputs['bundle'],matched=True,modelAccepted=False,
        limitation='Receipt validation does not authenticate the sender. Use the existing verified coordination receipt flow.'))


OPERATIONS={'T01':inventory,'T02':dataset,'T09':candidate,'T10':export,'T11':parity,'T12':runtime,'T13':package,'T14':consumer}


def run():
    spec=q.load(OUT.parents[2]/'spec.json');contract=spec['template'];start=time.monotonic()
    try:
        inputs=resolve_inputs(contract,OUT)
        OPERATIONS[contract['id']](inputs,contract['parameters'],OUT)
        outputs=[dict(path=str(p.relative_to(OUT)),sha256=q.digest(p)) for p in sorted(OUT.rglob('*'))
                 if p.is_file() and 'cache' not in p.relative_to(OUT).parts]
        q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=outputs))
        q.save(OUT/'template-result.json',dict(template=contract['id'],execution='complete',modelAccepted=False,
            seconds=time.monotonic()-start))
    except Exception as error:
        q.save(OUT/'template-result.json',dict(template=contract['id'],execution='failed',code=str(error)[:500],
            errorType=type(error).__name__,modelAccepted=False,seconds=time.monotonic()-start))
        raise
