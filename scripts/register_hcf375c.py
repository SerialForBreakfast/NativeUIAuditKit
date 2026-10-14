"""Register HCF375C with epoch evidence and immutable inputs.

See Research/ExperimentLog.md HCF375C. Earlier specifications remain unchanged.
Registration does not approve or run jobs. Approve each job with research_approval.py after its checks pass.
"""
import research_queue as q

TASK = 'HCF375C'
OWNER = None
CODE = ['hcf_study371.py', 'hcf_compare371.py', 'hcf_training375.py', 'hcf_capture362.py', 'hcf_settings368.py',
        'qualify_hcf362.py', 'generation352.py', 'dataset351.py', 'native343.py', 'direct_tvos_capture.py',
        'hcf_spatial_audit.py', 'focus_runtime.py', 'focus_ring_backbone.py', 'train_focus_ring_detector.py',
        'train_yolo.py', 'score_hcf_pilot.py']


def pin(path):
    return dict(path=q.relative(path), sha256=q.digest(path))


def output_pin(job, name):
    """Pin a completed producer output by its repository path."""
    folder = q.QUEUE / 'jobs' / job
    for attempt in q.attempts_of(folder):
        result = attempt / 'result.json'
        if result.exists() and q.load(result)['status'] == 'complete':
            return pin(attempt / 'out' / name)
    raise ValueError('producer_not_complete:' + job)


def dependency(job, outputs):
    return dict(job=job, specSHA256=q.text_digest(q.load(q.QUEUE / 'jobs' / job / 'spec.json')), outputs=outputs)


def base(ident, kind, authority, question, comparison, decision, outcomes, steps, inputs, stage, limits, **extra):
    spec = dict(version='research-spec-v2', id=ident, task=TASK, owner=OWNER, kind=kind, authority=authority,
                hypothesis=question, question=question, controlledComparison=comparison, decisionRule=decision,
                nextActionByOutcome=outcomes, inputs=inputs, stage=stage,
                adapter=dict(type='python-callable', steps=steps, outputAttributes=[steps[0].split('.')[0] + '.OUT']),
                limits=limits)
    spec.update(extra)
    return spec


def register():
    folder = q.ROOT / 'Research/ResearchSpecs' / TASK
    folder.mkdir(parents=True, exist_ok=True)
    code = [pin(q.ROOT / 'scripts' / name) for name in CODE]
    code += [pin(q.ROOT / '.build/arm64-apple-macosx/debug/FocusRingTool'),
             pin(q.ROOT / 'Sources/NativeUIAuditKit/Detection/FocusRingClassifier.swift')]
    crop_init = pin(q.ROOT / 'NativeUITrainer/focus_ring_runs/fdr038-retention234/weights/best.pt')
    yolo_init = pin(q.ROOT / 'NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.pt')
    crops = output_pin('hcf371r4-50-crops', 'crops.json')
    admission = output_pin('hcf371r4-40-catalog', 'admission.json')
    training_limits = dict(timeoutSeconds=1800, maxOutputBytes=2 << 30, maxAttempts=1)
    diagnostic_limits = dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1)
    specs = []

    def staged(name, value):
        path = folder / f'{name}-config.json'
        q.require(not path.exists(), 'immutable_config_exists')
        q.save(path, value)
        return [dict(**{'from': pin(path)}, to='config.json')]

    crop_train = base('hcf375c-70-crop-train', 'confirm', 'training',
        'Does a crop classifier trained on unique HCF and Standard crops keep HCF gains and remove Standard misses?',
        'The same 264 development frames scored by the HCF371 crop candidate, which trained on HCF crops only.',
        'Report gains, losses, wrong selections, and abstentions against the HCF371 baselines. No promotion.',
        {'supported': 'Repeat with 3 seeds before any audit or promotion decision.',
         'contradicted': 'Inspect Standard misses and crop coverage before more training.'},
        ['hcf_training375.crop'], code, staged('hcf375c-70-crop-train', dict(initialization=crop_init)), training_limits,
        dependencies=[dependency('hcf371r4-50-crops', ['crops.json'])], jobKind='training',
        evidence=dict(reads=[crops['path'], crop_init['path']], weights='final.pt', history='history.json', trainingReport='fit.json'),
        training=dict(experimentLogRunId=TASK, membership=[crops], initialization=crop_init, epochs=30,
                      storageBudgetBytes=2 << 30, resume='restart',
                      acceptanceEvidence='Development comparison counts against the HCF371 baselines; 1 seed, screening only.'))
    detector_train = base('hcf375c-71-detector-train', 'confirm', 'training',
        'Does a detector trained on HCF and Standard frames keep HCF gains and remove Standard misses?',
        'The same 264 development frames scored by the HCF371 detector, which trained on HCF frames only.',
        'Report gains, losses, wrong selections, and abstentions against the HCF371 baselines. No promotion.',
        {'supported': 'Repeat with 3 seeds before any audit or promotion decision.',
         'contradicted': 'Inspect Standard misses and detector proposals before more training.'},
        ['hcf_training375.detector'], code,
        staged('hcf375c-71-detector-train', dict(initialization=yolo_init, datasetFolder='yolo-training-hcf375c')),
        training_limits, dependencies=[dependency('hcf371r4-40-catalog', ['admission.json'])], jobKind='training',
        evidence=dict(reads=[admission['path'], yolo_init['path']], weights='detector/weights/best.pt',
                      history='history.json', trainingReport='fit.json'),
        training=dict(experimentLogRunId=TASK, membership=[admission], initialization=yolo_init, epochs=30,
                      storageBudgetBytes=2 << 30, resume='restart',
                      acceptanceEvidence='Development comparison counts against the HCF371 baselines; 1 seed, screening only.'))
    specs += [crop_train, detector_train]
    for step, train, name in (('hcf_compare371.candidate_crop', crop_train, 'hcf375c-80-crop-evaluate'),
                              ('hcf_compare371.candidate_detector', detector_train, 'hcf375c-81-detector-evaluate')):
        source = 'hcf371r5-80-crop-evaluate' if 'crop' in name else 'hcf371r5-81-detector-evaluate'
        source_spec = q.load(q.QUEUE / 'jobs' / source / 'spec.json')
        source_config = q.ROOT / next(s['from']['path'] for s in source_spec['stage'] if s['to'] == 'config.json')
        config = q.load(source_config)
        if 'crop' in name:
            config['candidate'] = True
        specs.append(base(name, 'screen', 'diagnostic',
            'Which development frames does the ' + ('crop' if 'crop' in name else 'detector') + ' candidate select correctly?',
            'The same 264 development frames and scoring code as HCF371.',
            'Save every prediction with its outcome. The decision job compares the counts.',
            {'supported': 'Pass the predictions to the decision job.',
             'contradicted': 'Diagnose the evaluator before reading any count.'},
            [step], code, staged(name, config), diagnostic_limits, jobKind='evaluation',
            dependencies=[dict(job=train['id'], specSHA256=q.text_digest(train), outputs=['model.json']),
                          dependency('hcf371r4-40-catalog', ['admission.json']),
                          dependency('hcf371-00-retained', ['admission.json'])],
            evidence=dict(predictions='comparison.json', membershipCount=264)))
    specs.append(base('hcf375c-90-decision', 'confirm', 'diagnostic',
        'Does either HCF375C candidate improve on HCF371 without new wrong selections?',
        'HCF371 rules and baseline against both HCF375C candidates on the same 264 development frames.',
        'Report gains and losses for each method. A single-seed result cannot accept a model.',
        {'supported': 'Register 3-seed repeats of the better candidate.',
         'contradicted': 'Keep HCF371 results. Diagnose Standard-profile misses.'},
        ['hcf_training375.decision'], code, [], diagnostic_limits, jobKind='aggregation', evidence=dict(citations='sources.json'),
        dependencies=[dependency('hcf371r4-60-rules', ['comparison.json']),
                      dependency('hcf371r4-61-baseline', ['comparison.json']),
                      dict(job=specs[2]['id'], specSHA256=q.text_digest(specs[2]), outputs=['comparison.json']),
                      dict(job=specs[3]['id'], specSHA256=q.text_digest(specs[3]), outputs=['comparison.json'])]))
    for spec in specs:
        path = folder / f"{spec['id']}.json"
        q.require(not path.exists(), 'immutable_spec_exists')
        q.save(path, spec)
        print(spec['id'], q.submit(path))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner', required=True)
    OWNER = parser.parse_args().owner
    register()
