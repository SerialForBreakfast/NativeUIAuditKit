"""Prepare HCF qualification from real receipts without changing active workers."""
from collections import Counter
import ast
import json
import os
from pathlib import Path
import subprocess
import research_queue as q

OUT = None
OLD_ROOT = Path.home() / 'Documents/GitHub/NativeUIAuditKit'


def inputs():
    docs, refs = {}, []
    for dep in q.load(OUT / 'dependencies.json'):
        for ref in dep['outputs']:
            path = q.local_path(q.ROOT, ref['path'])
            q.require(q.digest(path) == ref['sha256'], 'hcf389_input_changed')
            key = (dep['job'], path.name)
            q.require(key not in docs, 'hcf389_duplicate_input')
            docs[key] = q.load(path)
            refs.append(ref)
    q.require(docs, 'hcf389_inputs_missing')
    return docs, refs


def save(name, result, refs):
    q.save(OUT / name, dict(**result, modelAccepted=False, productionChanged=False))
    q.save(OUT / 'sources.json', refs)


def checked_model(record):
    path = Path(record['path'])
    if path.is_relative_to(OLD_ROOT):
        path = q.local_path(q.ROOT, str(path.relative_to(OLD_ROOT)))
    permitted = (q.ROOT, Path('/Volumes/training-drive/data/NUIAK/queue-artifacts'))
    q.require(path.is_absolute() and any(path.is_relative_to(root) for root in permitted), 'hcf389_model_scope')
    q.require(path.resolve() == path and path.is_file(), 'hcf389_model_path')
    q.require(q.digest(path) == record['sha256'], 'hcf389_model_changed')
    return dict(path=str(path), sha256=record['sha256'], kind=record['kind'])


def choose(methods, seeds):
    expected = {'bright-closed-stroke-v1', 'crop-baseline', 'crop-candidate', 'full-screen-candidate'}
    q.require(set(methods) == expected, 'hcf389_methods_missing')
    q.require(type(seeds.get('previousSuccessesPreserved')) is bool, 'hcf389_seed_evidence_missing')
    result = {}
    for name in ('crop-candidate', 'full-screen-candidate'):
        row = methods[name]
        q.require(isinstance(row.get('losses'), list) and isinstance(row.get('gains'), list), 'hcf389_case_lists')
        counts = row['counts']
        q.require(all(type(counts.get(k)) is int and counts[k] >= 0 for k in ('frames', 'correct', 'wrong', 'misses')),
                  'hcf389_counts')
        q.require(counts['frames'] > 0 and sum(counts[k] for k in ('correct', 'wrong', 'misses')) == counts['frames'],
                  'hcf389_counts')
        repeat_ok = name != 'crop-candidate' or seeds['previousSuccessesPreserved']
        result[name] = dict(eligibleForExportQualification=not row['losses'] and bool(row['gains']) and repeat_ok,
                           losses=row['losses'], gains=row['gains'], counts=counts, repeatsPreserved=repeat_ok)
    return result


def candidate():
    docs, refs = inputs()
    study = docs[('hcf388-study-report', 'hcf-study-report.json')]
    choices = choose(study['methods'], study['cropSeeds'])
    producers = {'crop-candidate': 'hcf375c-70-crop-train', 'full-screen-candidate': 'hcf388-detector-train'}
    for name, producer in producers.items():
        choices[name]['model'] = checked_model(docs[(producer, 'model.json')])
    save('candidate.json', dict(version='hcf389-candidate-v1', candidates=choices,
        selectionRule='Keep the predeclared seed371 crop and detector candidates. Do not select the best repeat seed.',
        decision='Qualify eligible candidates; diagnose losses for other candidates.',
        limitation='Development evidence only. No package, final audit, or deployment claim.'), refs)


def coverage_rows(rows):
    q.require(rows and len({r['id'] for r in rows}) == len(rows), 'hcf389_duplicate_or_empty_frames')
    groups = {}
    for row in rows:
        q.require(row['role'] in ('train', 'calibration', 'development', 'retained', 'audit'), 'hcf389_role')
        q.require(groups.setdefault(row['group'], row['role']) == row['role'], 'hcf389_group_leak')
    # Audit metadata counts do not inspect audit images or predictions.
    counts = Counter((r['role'], r['profile'], r['family']) for r in rows)
    return dict(frames=len(rows), groups=len(groups),
        slices=[dict(role=k[0], profile=k[1], family=k[2], frames=n,
                     groups=len({r['group'] for r in rows if (r['role'], r['profile'], r['family']) == k}))
                for k, n in sorted(counts.items())],
        noFocusLabelCount=sum(r.get('focus', 'unknown') is None for r in rows),
        auditImagesOpened=False, independentTrialCount=None)


def coverage():
    docs, refs = inputs()
    rows = [r for doc in docs.values() for r in doc['rows']]
    result = coverage_rows(rows)
    result.update(version='hcf389-coverage-v1',
        nextAction='Prepare observed no-focus cases and new native families. Do not infer labels from missing borders.',
        unknownFactors=['decorative-border label', 'physical-device transfer', 'untouched status of audit groups'],
        limitation='Metadata inventory is not new capture, label verification, or a usable final audit.')
    save('coverage.json', result, refs)


def export_preflight():
    docs, refs = inputs()
    q.require(('hcf375c-70-crop-train', 'model.json') in docs, 'hcf389_crop_input_missing')
    model = checked_model(docs[('hcf375c-70-crop-train', 'model.json')])
    scripts = ('export_focus_ring_coreml.py', 'export_yolo_coreml.py', 'focus_export_parity.py')
    source = []
    for name in scripts:
        path = q.ROOT / 'scripts' / name
        ast.parse(path.read_text())
        source.append(dict(path=q.relative(path), sha256=q.digest(path)))
    interpreter = q.ROOT / '.venv-coreml/bin/python'
    q.require(interpreter.is_file(), 'hcf389_export_interpreter_missing')
    scratch = OUT / 'probe-cache'
    scratch.mkdir()
    probe = 'import sys,json,torch,coremltools; print(json.dumps(dict(python=sys.version,torch=torch.__version__,coremltools=coremltools.__version__,prefix=sys.prefix)))'
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(scratch),
                       MPLCONFIGDIR=str(scratch), TORCH_HOME=str(scratch), HF_HUB_OFFLINE='1')
    run = subprocess.run([str(interpreter), '-I', '-c', probe], text=True, capture_output=True,
                         timeout=90, env=environment)
    # Import warnings remain evidence. Never install a missing dependency.
    q.save(OUT / 'import-probe.json', dict(returncode=run.returncode, stdout=run.stdout[-8000:], stderr=run.stderr[-8000:]))
    q.require(run.returncode == 0, 'hcf389_export_import_failed')
    versions = json.loads(run.stdout.strip().splitlines()[-1])
    q.require(Path(versions['prefix']) == q.ROOT / '.venv-coreml', 'hcf389_export_environment_changed')
    save('export-preflight.json', dict(version='hcf389-export-preflight-v1', environment=versions, sources=source,
        model=model, importsPassed=True, conversionPassed=False,
        queueExportSupported='export' in q.PERMITTED,
        blocker=None if 'export' in q.PERMITTED else 'research-host-NUIAK: queue rejects export authority; qualify an idle-boundary upgrade.',
        nextAction='Use the resident exporters after explicit export support passes tests. Imports alone do not qualify conversion.'), refs)


def proposal_selection(documents=None, references=None):
    """Score retained rule proposals without reading labels to choose candidates."""
    import base64
    import io
    import numpy as np
    from PIL import Image
    import torch
    import focus_runtime
    from train_focus_ring_detector import load_mobilenetv4_conv_small
    from hcf_compare371 import summarize
    docs, refs = inputs() if documents is None else (documents, references)
    rules = docs[('hcf371r4-60-rules', 'comparison.json')]
    frames = {r['id']: r for key, doc in docs.items() if key[1] == 'admission.json'
              for r in doc['rows'] if r['role'] in ('development', 'retained')}
    record = checked_model(docs[('hcf375c-70-crop-train', 'model.json')])
    torch.set_num_threads(2)
    network = load_mobilenetv4_conv_small()(pretrained=False, num_classes=1).eval()
    network.load_state_dict(torch.load(record['path'], map_location='cpu', weights_only=True)['state_dict'], strict=True)
    rows, predictions = [], []
    q.require(len({r['id'] for r in rules['rows']}) == len(rules['rows']), 'hcf389_duplicate_prediction')
    for rule in rules['rows']:
        row = dict(frames[rule['id']])
        q.require(all(row[k] == rule[k] for k in ('sha256', 'group', 'role', 'profile')), 'hcf389_case_mismatch')
        path = Path(row['path'])
        if path.is_relative_to(OLD_ROOT):
            path = q.local_path(q.ROOT, str(path.relative_to(OLD_ROOT)))
        q.require(path.resolve() == path and path.is_relative_to('/Volumes/training-drive/data/NUIAK'), 'hcf389_image_scope')
        q.require(q.digest(path) == row['sha256'], 'hcf389_image_changed')
        candidates = rule['prediction']['candidates']
        q.require(len(candidates) <= 128, 'hcf389_proposal_limit')
        scores = []
        if candidates:
            items = [dict(id=f"{row['id']}-{i}", path=str(path), sha256=row['sha256'], bounds=b)
                     for i, b in enumerate(candidates)]
            reply = focus_runtime.invoke(items, image_root=Path('/Volumes/training-drive/data/NUIAK'))
            arrays = []
            for item in reply['results']:
                with Image.open(io.BytesIO(base64.b64decode(item['png'], validate=True))) as image:
                    q.require(image.size == (256, 256), 'hcf389_crop_size')
                    arrays.append(np.array(image.convert('RGB'), copy=True))
            with torch.no_grad():
                batch = torch.from_numpy(np.stack(arrays)).permute(0, 3, 1, 2).float() / 255
                scores = torch.sigmoid(network(batch)).reshape(-1).tolist()
        selected = [i for i, value in enumerate(scores) if value >= .85]
        predictions.append(dict(id=row['id'], box=candidates[selected[0]] if len(selected) == 1 else None,
            decision='select' if len(selected) == 1 else 'abstain', scores=scores, candidateCount=len(candidates)))
        rows.append(row)
        q.save(OUT.parent / 'progress.json', dict(step='Score fixed outline proposals', completed=len(rows),
                                                 total=len(rules['rows']), updatedAt=__import__('time').time()), replace=True)
    result = summarize(rows, predictions)
    result.pop('modelAccepted', None)
    result.update(version='hcf389-proposal-selection-v1', modelSHA256=record['sha256'],
        proposalMode='bright-closed-stroke-v1', threshold=.85,
        limitation='Outline proposals are not control-body boxes. No calibrated inset is applied. Missing proposals constrain selection.')
    save('proposal-selection.json', result, refs)


def readiness_report():
    docs, refs = inputs()
    environment = docs[('hcf389-export-preflight', 'export-preflight.json')]
    coverage = docs[('hcf389-coverage', 'coverage.json')]
    selection = docs[('hcf389-proposal-selection', 'proposal-selection.json')]
    candidate_doc = docs[('hcf389-candidate', 'candidate.json')]
    save('next-actions.json', dict(version='hcf389-next-actions-v1', candidates=candidate_doc['candidates'],
        proposalSelection=selection['counts'], coverage=coverage, exportEnvironment=environment,
        completeCoreMLModel=False,
        blockers=['Queue export authority needs a tested idle-boundary upgrade.',
                  'New native coverage needs qualified no-focus and new-family producer recipes.',
                  'Core ML parity, frozen audit, and TTR inference receipts are still required.'],
        nextAction='Use measured proposal coverage and candidate losses to prepare export and native qualification, without new training.'), refs)
