"""Append qualified HCF preparation jobs without restarting the runner."""
import argparse
import research_queue as q
import research_approval as approval

FOLDER = q.ROOT / 'Research/ResearchSpecs/HCF389'


def pin(path):
    return dict(path=path, sha256=q.digest(q.local_path(q.ROOT, path)))


def dependency(job, *outputs):
    source = q.QUEUE / 'jobs' / job / 'spec.json'
    if not source.exists():
        source = FOLDER / (job + '.json')
    spec = q.load(source)
    return dict(job=job, specSHA256=q.text_digest(spec), outputs=list(outputs))


def make(ident, step, question, deps, *, evaluation=False):
    sources = ['scripts/hcf_prepare389.py', 'scripts/export_focus_ring_coreml.py',
               'scripts/export_yolo_coreml.py', 'scripts/focus_export_parity.py', '.venv-coreml/pyvenv.cfg']
    if evaluation:
        sources += ['.build/arm64-apple-macosx/debug/FocusRingTool',
                    'Sources/NativeUIAuditKit/Detection/FocusRingClassifier.swift']
    evidence = (dict(predictions='proposal-selection.json', membershipCount=264)
                if evaluation else dict(citations='sources.json'))
    return dict(version='research-spec-v2', id=ident, task='HCF389', owner='research-host-NUIAK',
        kind='screen', authority='diagnostic', jobKind='evaluation' if evaluation else 'aggregation',
        question=question, hypothesis=question,
        controlledComparison='Use pinned retained evidence. Keep model weights, thresholds, data roles, and current training unchanged.',
        decisionRule='Report measured support and missing requirements. Missing or changed inputs fail. Do not accept a model.',
        nextActionByOutcome=dict(supported='Use verified evidence to prepare the next qualification step.',
                                 contradicted='Name the missing requirement and repair only the affected branch.'),
        inputs=[pin(p) for p in sources], dependencies=deps, stage=[], evidence=evidence,
        adapter=dict(type='python-callable', steps=['hcf_prepare389.' + step], outputAttributes=['hcf_prepare389.OUT']),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1))


def persist(spec):
    path = FOLDER / (spec['id'] + '.json')
    if path.exists():
        q.require(q.load(path) == spec, 'hcf389_immutable_spec_changed')
    else:
        q.save(path, spec)
    q.validate(spec)
    q.verify_pins(spec)
    return spec


def build():
    FOLDER.mkdir(parents=True, exist_ok=True)
    corpus = [dependency('hcf371r4-40-catalog', 'admission.json'), dependency('hcf371-00-retained', 'admission.json')]
    model = dependency('hcf375c-70-crop-train', 'model.json')
    specs = []
    specs.append(persist(make('hcf389-export-preflight', 'export_preflight',
        'Can the resident Core ML environment import the required tools without downloads?', [model])))
    specs.append(persist(make('hcf389-coverage', 'coverage',
        'Which native families, profiles, roles, and absent-focus labels exist in our retained corpus?', corpus)))
    specs.append(persist(make('hcf389-candidate', 'candidate',
        'Which predeclared HCF candidates preserve previous successes and merit export qualification?',
        [dependency('hcf388-study-report', 'hcf-study-report.json'), model,
         dependency('hcf388-detector-train', 'model.json')])))
    specs.append(persist(make('hcf389-proposal-selection', 'proposal_selection',
        'Does the crop model select focus using fixed outline proposals instead of known control boxes?',
        [*corpus, model, dependency('hcf371r4-60-rules', 'comparison.json')], evaluation=True)))
    specs.append(persist(make('hcf389-next-actions', 'readiness_report',
        'Which measured requirements still prevent a complete experimental Core ML delivery?',
        [dependency('hcf389-export-preflight', 'export-preflight.json'),
         dependency('hcf389-coverage', 'coverage.json'),
         dependency('hcf389-candidate', 'candidate.json'),
         dependency('hcf389-proposal-selection', 'proposal-selection.json')])))
    return specs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--submit', action='store_true')
    args = parser.parse_args()
    for spec in build():
        if args.submit:
            q.submit(FOLDER / (spec['id'] + '.json'))
            approval.approve(q.QUEUE, spec['id'], 'agent:hcf389',
                'Maintainer requests executable HCF qualification jobs. Preserve active training and model gates.')
        print(spec['id'], q.text_digest(spec), flush=True)


if __name__ == '__main__':
    main()
