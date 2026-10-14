"""Prepare bounded experiment jobs. Registration never approves or starts work."""
import argparse
import json
from pathlib import Path

import research_queue as q

VERSION = 'experiment-description-v1'
# All contracts exist. Only named implemented bindings can become jobs.
DEFINITIONS = [
    ('T01', 'Evidence inventory', ['manifest'], ['coverage'], 'Verify admitted labels and complete input identities.'),
    ('T02', 'Dataset definition', ['manifest', 'groupPolicy'], ['membership'], 'Qualify ancestry and frozen data roles.'),
    ('T03', 'Native capture', ['recipe', 'target', 'restoration'], ['capture'], 'Qualify target ownership and native capture adapter.'),
    ('T04', 'Data qualification', ['capture', 'observations'], ['admission'], 'Qualify native labels and visible OS effects.'),
    ('T05', 'Prepare existing crops', ['manifest'], ['prepared'], ''),
    ('T06', 'PyTorch training', ['membership', 'initialization', 'training'], ['checkpoint'], 'Qualify crop and detector training wrappers; restart is the current supported behavior.'),
    ('T07', 'Crop model inference', ['prepared', 'model'], ['predictions'], ''),
    ('T08', 'Measured crop report', ['predictions'], ['report'], ''),
    ('T09', 'Candidate freeze', ['comparisons', 'checkpoint'], ['candidate'], 'Qualify predeclared candidate review and retained-success checks.'),
    ('T10', 'Core ML export', ['candidate', 'environment'], ['package'], 'Add explicit queue export support at an idle boundary.'),
    ('T11', 'Vision parity', ['package', 'reference', 'membership'], ['parity'], 'Qualify actual Vision adapter and fixed score tolerances.'),
    ('T12', 'Apple runtime measurement', ['package', 'host'], ['runtime'], 'Qualify warm/cold measurement through actual Apple inference.'),
    ('T13', 'Optional delivery package', ['package', 'qualification', 'license'], ['bundle'], 'Qualify immutable packaging and rollback checks.'),
    ('T14', 'Consumer verification', ['bundle', 'receipt'], ['verification'], 'Require real TTR inference receipt with matching package identity.'),
]


def catalog():
    return [dict(id=ident, version=1, title=title, requiredInputs=inputs, outputs=outputs,
                 implementation='available' if not blocker else 'contract-only', blocker=blocker or None,
                 owner='research-host-NUIAK', qualification='not_automatically_qualified')
            for ident, title, inputs, outputs, blocker in DEFINITIONS]


def validate_contract(ident, inputs, version=1):
    q.require(version == 1, 'template_version')
    matches = [r for r in catalog() if r['id'] == ident]
    q.require(len(matches) == 1, 'template_unknown')
    row = matches[0]
    q.require(isinstance(inputs, dict) and set(inputs) == set(row['requiredInputs']), 'template_input_fields')
    q.require(all(value is not None for value in inputs.values()), 'template_input_missing')
    return row


def pin(path):
    path = Path(path)
    return dict(path=q.relative(path), sha256=q.digest(path))


def checked(ref):
    q.check_pin(ref)
    path = q.local_path(q.ROOT, ref['path'])
    q.require(path.is_file(), 'input_missing:' + ref['path'])
    q.require(q.digest(path) == ref['sha256'], 'input_changed:' + ref['path'])
    return path


def validate(doc):
    q.require(isinstance(doc, dict) and set(doc) ==
              {'version', 'id', 'owner', 'question', 'decision', 'manifest', 'model', 'batchSize'}, 'description_fields')
    q.require(doc['version'] == VERSION, 'description_version')
    q.require(isinstance(doc['id'], str) and q.ID.fullmatch(doc['id']) and len(doc['id']) <= 48, 'description_id')
    from research_trust import OWNER
    q.require(isinstance(doc['owner'], str) and OWNER.fullmatch(doc['owner']), 'description_owner')
    for key in ('question', 'decision'):
        q.require(isinstance(doc[key], str) and 12 <= len(doc[key]) <= 2000, 'description_' + key)
    q.require(type(doc['batchSize']) is int and 1 <= doc['batchSize'] <= 16, 'batch_size')
    manifest = q.load(checked(doc['manifest']))
    checked(doc['model'])
    from experiment_steps393 import validate_manifest
    validate_manifest(manifest)
    return manifest


def build(doc):
    """Return a fully pinned three-step campaign without writing files."""
    manifest = validate(doc)
    source = [pin(q.MODULES / name) for name in ('experiment_steps393.py', 'experiment_templates.py',
              'train_focus_ring_detector.py', 'focus_ring_backbone.py')]
    specs = []
    for index, (template, step, output, kind) in enumerate([
        ('T05', 'prepare', 'prepared.json', 'evaluation'),
        ('T07', 'score', 'predictions.json', 'evaluation'),
        ('T08', 'report', 'report.json', 'aggregation'),
    ]):
        dependencies = [] if index == 0 else [dict(job=specs[-1]['id'], specSHA256=q.text_digest(specs[-1]),
            outputs=['prepared.json', 'tensors.npy'] if index == 1 else ['predictions.json'])]
        inputs = source + [doc['manifest'], doc['model']] + [r['image'] for r in manifest['rows']]
        inputs = list({p['path']: p for p in inputs}.values())
        # The fixed source manifest is staged under one known name. No generated Python or shell commands.
        stage = [dict(**doc, template=template, templateVersion=1)]
        evidence = (dict(reads=[doc['manifest']['path'], doc['model']['path']], model=doc['model']['path'],
                         predictions=output, membershipCount=len(manifest['rows'])) if kind == 'evaluation'
                    else dict(citations='sources.json'))
        spec = dict(version='research-spec-v2', id=doc['id'] + '-' + step, task='TEMPLATE393', owner=doc['owner'],
            kind='screen', authority='diagnostic', jobKind=kind, question=doc['question'], hypothesis=doc['question'],
            controlledComparison='Keep the same pixels, model, membership, roles, and threshold. Compare execution methods only.',
            decisionRule=doc['decision'], nextActionByOutcome=dict(
                supported='Use verified execution evidence to qualify this bounded template.',
                contradicted='Preserve the failure and repair the exact failed requirement.'),
            inputs=inputs, dependencies=dependencies, stage=[], evidence=evidence,
            adapter=dict(type='python-callable', steps=['experiment_steps393.'+step], outputAttributes=['experiment_steps393.OUT']),
            limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1),
            templateConfig=stage[0])
        # Template metadata remains inside the immutable spec, not an executable expression.
        q.validate(spec)
        specs.append(spec)
    return specs


def register(doc, queue=q.QUEUE):
    specs = build(doc)
    queue = q.local_path(q.ROOT, q.relative(Path(queue)))
    queue.mkdir(parents=True, exist_ok=True)
    with q.host_lock(queue / 'template-registration.lock'):
        folder = queue / 'template-registrations' / doc['id']
        folder.mkdir(parents=True, exist_ok=True)
        contract = folder / 'description.json'
        if contract.exists():
            q.require(q.load(contract) == doc, 'registration_conflict')
        else:
            q.save(contract, doc)
        results = []
        for spec in specs:
            path = folder / (spec['id'] + '.json')
            if path.exists():
                q.require(q.load(path) == spec, 'registration_code_or_input_changed')
            else:
                q.save(path, spec)
            results.append(dict(job=spec['id'], state=q.submit(path, queue), sha256=q.text_digest(spec)))
            q.save(folder / 'journal.json', dict(version=1, registered=results, executionStarted=False), replace=True)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['catalog', 'preview', 'register'])
    parser.add_argument('description', nargs='?', type=Path)
    parser.add_argument('--queue', type=Path, default=q.QUEUE)
    args = parser.parse_args()
    if args.action == 'catalog':
        value = catalog()
    else:
        q.require(args.description is not None, 'description_required')
        doc = q.load(args.description)
        value = build(doc) if args.action == 'preview' else register(doc, args.queue)
    print(json.dumps(value, indent=2))


if __name__ == '__main__':
    main()
