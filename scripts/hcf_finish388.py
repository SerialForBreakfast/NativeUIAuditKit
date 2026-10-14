"""Report matched HCF repeats and the completed comparison without promotion."""
import research_queue as q
from hcf_crop_review376 import review

OUT = None


def inputs():
    docs = {}; refs = []
    for dep in q.load(OUT/'dependencies.json'):
        q.require(len(dep['outputs']) == 1, 'finish_output_count')
        ref = dep['outputs'][0]
        path = q.local_path(q.ROOT, ref['path'])
        q.require(q.digest(path) == ref['sha256'], 'finish_input_changed')
        q.require(dep['job'] not in docs, 'finish_duplicate_job')
        docs[dep['job']] = q.load(path); refs.append(ref)
    return docs, refs


def seed_review():
    docs, refs = inputs()
    baseline = docs.pop('hcf375c-80-crop-evaluate')
    q.require(set(docs) == {'hcf388-crop-seed372-evaluate', 'hcf388-crop-seed373-evaluate'}, 'seed_reports_missing')
    reports = {key: review(baseline, value, {}) for key, value in docs.items()}
    for report in reports.values():
        report['confoundedChanges'] = ['random seed only']
    q.save(OUT/'seed-review.json', dict(version='hcf-seeds-v1', comparisons=reports,
        previousSuccessesPreserved=all(r['losses'] == 0 for r in reports.values()),
        modelAccepted=False, auditOpened=False,
        limitation='Known control boxes and inspected groups only. No-focus and physical-device accuracy remain unknown.'))
    q.save(OUT/'sources.json', refs)


def finish():
    docs, refs = inputs()
    q.require(set(docs) == {'hcf388-method-decision', 'hcf388-seed-review'}, 'finish_reports_missing')
    method = docs['hcf388-method-decision']; seeds = docs['hcf388-seed-review']
    q.require(set(method.get('comparisons', {})) ==
        {'bright-closed-stroke-v1','crop-baseline','crop-candidate','full-screen-candidate'}, 'finish_methods_missing')
    q.require(type(seeds.get('previousSuccessesPreserved')) is bool, 'finish_seed_result_missing')
    detector = method['comparisons']['full-screen-candidate']
    q.save(OUT/'hcf-study-report.json', dict(version='hcf-study-report-v1',
        methods=method['comparisons'], cropSeeds=seeds,
        modelAccepted=False, productionChanged=False, auditOpened=False,
        nextActions=[
            'Test fixed deployable proposals and verified no-focus cases before deployment.',
            'Review crop seed losses before choosing a model.' if not seeds['previousSuccessesPreserved']
            else 'Crop repeats preserve inspected successes. Test coverage outside known boxes.',
            'Diagnose detector losses before more training.' if detector['losses']
            else 'Compare detector coverage and wrong selections before export qualification.'],
        limitations=['This completes the queued development comparison, not deployment qualification.',
                    'Core ML parity, no-focus performance, and physical transfer remain separate requirements.']))
    q.save(OUT/'sources.json', refs)
