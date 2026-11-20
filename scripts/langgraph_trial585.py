"""Compile two campaign reports through existing queue contracts. Never dispatch."""
import argparse
from pathlib import Path

import research_queue as q
from template_inputs398 import checked, pin
from model_decision_batch434 import retain


def compile_trial(description, destination):
    request=q.load(checked(description))
    q.require(set(request)=={'version','id','campaigns','softwareMeasurements'}
              and request['version']=='langgraph-trial585-description-v1', 'trial_description')
    q.require(q.ID.fullmatch(request['id']) and len(request['campaigns'])==2, 'trial_campaign_count')
    configs=[q.load(checked(ref)) for ref in request['campaigns']]
    q.require({c['track'] for c in configs}=={'iOS detection','tvOS focus'}
              and len({c['campaignID'] for c in configs})==2, 'trial_track_membership')
    checked(request['softwareMeasurements'])
    destination=Path(destination).absolute()
    q.require(destination.resolve()==destination and destination.is_relative_to(q.ROOT), 'compile_output_boundary')
    destination.mkdir(parents=True,exist_ok=True)
    specs=[];existing={}
    def make(ident,step,inputs,dependencies):
        return dict(version='research-spec-v2', id=ident, kind='screen', jobKind='artifact',
            authority='diagnostic', owner='Maximum-mini-NUIAK',task='LANGGRAPH585',
            hypothesis='Persistent campaign state reduces recovery effort without changing reports or scientific execution.',
            question='Does persistent campaign reporting reduce manual work while independent model streams continue?',
            controlledComparison='Use identical verified events and deterministic report functions. Keep the existing runner and scientific templates.',
            decisionRule='Require report agreement and independent review states. Measure overhead and actual interventions. Keep all results provisional.',
            nextActionByOutcome=dict(supported='Review measured workflow benefit before any wider adoption.',
                contradicted='Retain the working runner and record the failed workflow assumption.',
                inconclusive='Preserve the bounded prototype and report missing measurements.'),
            inputs=inputs, dependencies=dependencies,
            adapter=dict(type='python-callable',steps=['research_langgraph_adapter585.'+step],
                         outputAttributes=['research_langgraph_adapter585.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),
            evidence=dict(reads=[r['path'] for r in inputs if r not in sources],artifactReceipt='artifact-receipt.json'))
    sources=[pin(q.MODULES/name) for name in ('research_langgraph_adapter585.py','langgraph_campaign585.py','requirements-langgraph585.lock')]
    for ref,config in zip(request['campaigns'],configs):
        q.require(config['version']=='langgraph-campaign585-v1' and q.ID.fullmatch(config['campaignID']), 'trial_campaign_config')
        manifest=q.load(checked(config['manifest']));members={r['job']:r['specSHA256'] for r in manifest['jobs']};deps=[]
        for row in config['jobs']:
            spec=q.load(q.QUEUE/'jobs'/row['job']/'spec.json')
            q.require(members.get(row['job'])==q.text_digest(spec),'campaign_spec_drift')
            dep=dict(job=row['job'],specSHA256=q.text_digest(spec),outputs=row['outputs'])
            deps.append(dep);existing[row['job']]=dict(job=row['job'],specSHA256=dep['specSHA256'])
        spec=make(config['campaignID']+'-review','run',sources+[ref,config['manifest']],deps)
        spec['campaignConfig']=ref;specs.append(spec)
    summary=make(request['id']+'-comparison','compare',sources+[request['softwareMeasurements']],
        [dict(job=s['id'],specSHA256=q.text_digest(s),outputs=['benchmark_summary.json']) for s in specs])
    summary['softwareMeasurements']=request['softwareMeasurements'];specs.append(summary)
    entries=[]
    for spec in specs:
        q.validate(spec);q.verify_pins(spec)
        path=destination/(spec['id']+'.json');retain(path,spec)
        entries.append(dict(job=spec['id'],spec=pin(path),specSHA256=q.text_digest(spec)))
    result=dict(version='model-decision-compiled-v1',plan=description,jobs=entries,existing=list(existing.values()),executionStarted=False)
    retain(destination/'compiled.json',result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('description',type=Path);p.add_argument('destination',type=Path)
    args=p.parse_args();value=compile_trial(pin(args.description),args.destination)
    print({'jobs':[x['job'] for x in value['jobs']], 'executionStarted':False})


if __name__=='__main__':main()
