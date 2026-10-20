"""Compile admitted detector training and retained comparisons using existing templates."""
from pathlib import Path
import research_queue as q
import hcf_templates395 as templates
from experiment_batch402 import compile_batch
from experiment_templates import checked, pin
from model_decision_batch434 import retain
from proposal_campaign443 import completed_output, resolved_inputs

OUT = None


def assessment(reports):
    q.require(reports and all(r.get('version') == 'detector-case-match-v1' for r in reports),
              'detector_batch_report_version')
    gains = [case for r in reports for case in r['gains']]
    losses = [case for r in reports for case in r['lostPriorSuccesses']]
    return dict(version='research-condition-v1',
        outcome='contradicted' if losses else 'supported' if gains else 'inconclusive',
        reason='Retained detections regressed.' if losses else 'New detections without retained losses.' if gains else 'No changed detections.',
        gains=gains, lostPriorSuccesses=losses, modelAccepted=False,
        limitation='Inspected native development groups only. Unmatched predictions are not verified false positives. Focus and no-focus are unavailable.',
        nextAction='Reject replacement and inspect regression cases.' if losses else
                   'Require independent qualification and full retained evaluation.' if gains else
                   'Stop this correction unless new failure evidence justifies further training.')


def finish():
    spec = q.load(OUT.parents[2]/'spec.json')
    reads = spec['evidence']['reads']
    q.require(len(reads) == 1, 'detector_batch_request_count')
    reference = next((p for p in spec['inputs'] if p['path'] == reads[0]), None)
    q.require(reference is not None, 'detector_batch_request_pin')
    request = q.load(checked(reference))
    q.require(request.get('version') == 'detector-training-batch-v1' and
              request.get('question') == spec['question'], 'detector_batch_request_contract')
    dependencies = q.dependency_inputs(spec, OUT.parents[4])
    q.require(len(dependencies) == len(request['baselines']), 'detector_batch_comparison_count')
    reports = [q.load(checked(d['outputs'][0])) for d in dependencies]
    result = assessment(reports)
    result['evidence'] = [d['outputs'][0] for d in dependencies]
    result['comparisons'] = [dict(job=d['job'], decisions=r['decisions'])
                             for d, r in zip(dependencies, reports)]
    q.save(OUT/'decision.json', result)
    (OUT/'report.md').write_text(
        '# Detector training comparison\n\nOutcome: '+result['outcome']+
        '\n\nGains: '+str(len(result['gains']))+'. Lost successes: '+str(len(result['lostPriorSuccesses']))+
        '.\n\n'+result['nextAction']+'\n\n'+result['limitation']+'\n')
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=n, sha256=q.digest(OUT/n)) for n in ('decision.json', 'report.md')]))


def compile_request(source, destination, queue=q.QUEUE):
    plan = q.load(source)
    q.require(set(plan) == {'version','id','question','training','baselines','budget'}, 'detector_batch_fields')
    q.require(plan['version'] == 'detector-training-batch-v1' and q.ID.fullmatch(plan['id']),
              'detector_batch_version')
    train = plan['training']
    q.require(train['template'] == 'T89', 'detector_batch_training')
    data = q.load(checked(train['inputs']['membership']))
    q.require(data['version'] == 'detector-training-membership-v2' and data['trainingAdmitted'],
              'detector_batch_admission')
    q.require(data['rows'] and all(r['role']=='train' and r['labelsComplete'] and r['trainingEligible']
                                  for r in data['rows']), 'detector_batch_training_roles')
    groups = {r['group'] for r in data['rows']}
    pixels = {r['image']['sha256'] for r in data['rows']}
    q.require(1 <= len(plan['baselines']) <= 8 and len(set(plan['baselines'])) == len(plan['baselines']),
              'detector_batch_baselines')
    authored, existing, scored = [train], [], []
    for index, ident in enumerate(plan['baselines']):
        original = q.load(queue/'jobs'/ident/'spec.json')
        q.require(original['template']['id'] == 'T56', 'detector_batch_score_template')
        refs = resolved_inputs(original, queue)
        labels = q.load(checked(refs['labels']))
        q.require(not groups & {r['group'] for r in labels['frames']} and
                  not pixels & {r['sha256'] for r in labels['frames']}, 'detector_batch_evaluation_overlap')
        baseline = completed_output(queue, ident, 'scorecard.json')
        score = plan['id']+f'-score-{index+1:02}'
        authored.append(dict(version='hcf-template-description-v1', id=score, task=plan['id'],
            owner='Maximum-mini-NUIAK', template='T56', question=plan['question'],
            decision='Preserve every retained success. Do not promote a model.',
            controlledComparison='Change weights only. Preserve labels, threshold, resolution, and class matching.',
            inputs=dict(labels=refs['labels'], model=dict(job=train['id'], output='final.pt'), baseline=baseline),
            parameters=original['template']['parameters']))
        existing.append(dict(job=ident, specSHA256=q.text_digest(original)))
        scored.append(score)
    specs = [templates.build(d) for d in compile_batch(dict(version='experiment-batch-v1',jobs=authored),queue)]
    terminal = dict(version='research-spec-v2', id=plan['id']+'-decision', task=plan['id'],
        owner='Maximum-mini-NUIAK', kind='screen', authority='diagnostic', jobKind='artifact',
        question=plan['question'], hypothesis=plan['question'],
        controlledComparison='Change detector weights only on identical retained evaluation frames.',
        decisionRule='Any lost success contradicts replacement. Gains require further qualification. Never promote.',
        nextActionByOutcome=dict(supported='Prepare independent qualification.', contradicted='Inspect case-linked losses.',
                                 inconclusive='Stop this correction without new evidence.'),
        inputs=[pin(source), pin(Path(__file__))],
        dependencies=[dict(job=s['id'],specSHA256=q.text_digest(s),outputs=['benchmark_summary.json'])
                      for s in specs if s['id'] in scored],
        evidence=dict(reads=[q.relative(source)],artifactReceipt='artifact-receipt.json'),
        adapter=dict(type='python-callable',steps=['detector_training_batch478.finish'],
                     outputAttributes=['detector_training_batch478.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    specs.append(terminal)
    # The fixed follow-up diagnoses class errors only after regression. It never starts another fit.
    followups = []
    for index, score in enumerate(scored):
        followups.append(dict(version='hcf-template-description-v1',id=plan['id']+f'-diagnose-{index+1:02}',
            task=plan['id'],owner='Maximum-mini-NUIAK',template='T42',question=plan['question'],
            decision='Separate class confusion from missing boxes after regression. No automatic retraining.',
            inputs=dict(bundle=dict(job=score,output='bundle.json')),
            parameters=dict(slice='class',classes=None,groups={},matching='class-agnostic')))
    # Compile against the generated parents without registering them.
    destination.mkdir(parents=True, exist_ok=True)
    for spec in specs:
        retain(destination/(spec['id']+'.json'),spec)
    # Explicit parent specifications let the standard batch compiler resolve future outputs.
    from tempfile import TemporaryDirectory
    import shutil
    with TemporaryDirectory(dir=q.ROOT/'.build') as temporary:
        scratch = Path(temporary)
        for spec in specs:
            folder=scratch/'jobs'/spec['id'];folder.mkdir(parents=True)
            shutil.copyfile(destination/(spec['id']+'.json'),folder/'spec.json')
        for doc in compile_batch(dict(version='experiment-batch-v1',jobs=followups),scratch):
            spec=templates.build(doc)
            spec['dependencies'].append(dict(job=terminal['id'],specSHA256=q.text_digest(terminal),outputs=['decision.json']))
            spec['conditions']=[dict(job=terminal['id'],output='decision.json',outcome='contradicted')]
            specs.append(spec)
    budget=plan['budget']
    q.require(set(budget)=={'maxJobs','maxSeconds','maxOutputBytes'} and
              all(type(v) is int and v>0 for v in budget.values()), 'detector_batch_budget')
    q.require(len(specs)<=budget['maxJobs'] and
              sum(s['limits']['timeoutSeconds'] for s in specs)<=budget['maxSeconds'] and
              sum(s['limits']['maxOutputBytes'] for s in specs)<=budget['maxOutputBytes'],
              'detector_batch_budget_exceeded')
    entries=[]
    for spec in specs:
        q.validate(spec);path=destination/(spec['id']+'.json');retain(path,spec)
        entries.append(dict(job=spec['id'],spec=pin(path),specSHA256=q.text_digest(spec)))
    manifest=dict(version='model-decision-compiled-v1',plan=pin(source),existing=existing,jobs=entries,
                  executionStarted=False,modelAccepted=False)
    retain(destination/'compiled.json',manifest)
    return manifest
