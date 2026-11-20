"""Complete detector comparisons without importing campaign authoring code."""
import research_queue as q
from template_inputs398 import checked

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
    retained=request.get('version')=='detector-retained-batch-v1'
    q.require(request.get('version') in ('detector-training-batch-v1','detector-retained-batch-v1') and
              request.get('question') == spec['question'], 'detector_batch_request_contract')
    if retained:
        q.require(set(request)=={'version','id','question','baselines','selection'},'detector_retained_request_fields')
        selection=request['selection']
        q.require(set(selection)=={'kind','checkpoint','trainingResult'} and selection['kind']=='training-diagnostic-best',
                  'detector_retained_selection')
        q.require(selection['checkpoint'] in spec['inputs'] and selection['trainingResult'] in spec['inputs'],
                  'detector_retained_input_pins')
        checked(selection['checkpoint']);checked(selection['trainingResult'])
    dependencies = q.dependency_inputs(spec, OUT.parents[4])
    q.require(len(dependencies) == len(request['baselines']), 'detector_batch_comparison_count')
    reports = [q.load(checked(d['outputs'][0])) for d in dependencies]
    if retained:
        q.require(all(r.get('candidateModel',{}).get('weightsSHA256')==selection['checkpoint']['sha256'] for r in reports),'detector_retained_model_identity')
    result = assessment(reports)
    result['evidence'] = [d['outputs'][0] for d in dependencies]
    result['comparisons'] = [dict(job=d['job'], decisions=r['decisions'])
                             for d, r in zip(dependencies, reports)]
    q.save(OUT/'decision.json', result)
    (OUT/'report.md').write_text(
        ('# Retained detector checkpoint comparison' if retained else '# Detector training comparison')+'\n\nOutcome: '+result['outcome']+
        '\n\nGains: '+str(len(result['gains']))+'. Lost successes: '+str(len(result['lostPriorSuccesses']))+
        '.\n\n'+result['nextAction']+'\n\n'+result['limitation']+'\n')
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=n, sha256=q.digest(OUT/n)) for n in ('decision.json', 'report.md')]))
