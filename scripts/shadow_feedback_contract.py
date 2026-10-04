"""Portable normalized feedback checks; no model, device, image or training access.

This is a consumer test interface, not a replacement TTR wire schema. Callers must
independently verify export bytes and review provenance before trusting real labels.
"""
import argparse
import json
import hashlib
import math
from pathlib import Path
import re

VERSION='nuiak-shadow-conformance-v1'
MODEL='focus-transition-experimental-dtm025-change-v1'
MODEL_TREES={
    MODEL:'194a84672325e6016828bd57c4baa5d7dfda720b8a553631d31c6af5d3951c32',
    'focus-transition-experimental-dtm030-change-v1':'59d5d5f528ab0da57f6af89a977f5490f4886d7e32422238aaee0e4e31aab567',
}
MODEL_CONTRACTS={
    MODEL:'31837a325f0fcfabba7a30c07018e18c5acf36418bedb69d3b9c0970583c9e31',
    'focus-transition-experimental-dtm030-change-v1':'44c6a8dfbc5c4dd3e954295f6e355a6b416a5e8838788a8a0fad706fe9942cd5',
}
MODEL_MANIFESTS={
    MODEL:{'117530ef7f901ec901ffee178dc6381d833261f37d4ca84e3f47514ca7b6e872'},
    'focus-transition-experimental-dtm030-change-v1':{
        '991100acdfbeb66ee0f229a1ee21467b105eca686da323be5e0172ccf3ff4182',
        'a77aa20ff64750811bde73ce0b42aaa57a0f718522ef437b75ea7ff2a210f447'},
}
BINDING={'case_id','action_id','before_observation_id','after_observation_id','before_sha256','after_sha256'}
STATES={'scored','skipped','model_unavailable','inference_failed','dropped','cancelled','stale'}


def require(value,reason):
    if not value:raise ValueError(reason)


def fields(value,keys):
    require(type(value) is dict and set(value)==set(keys),'fields')


def load(path):
    require(path.stat().st_size<=1_048_576,'document_size')
    return parse(path.read_bytes())


def parse(data):
    require(len(data)<=1_048_576,'document_size')
    def unique(pairs):
        result={}
        for key,value in pairs:
            require(key not in result,'duplicate_key');result[key]=value
        return result
    def invalid(_):raise ValueError('nonfinite_json')
    return json.loads(data,object_pairs_hook=unique,parse_constant=invalid)


def normalize_cli(request_bytes,reply,labels,*,test_only=False):
    """Join allowlisted CLI output to separately supplied review records.

    Verifies receipt association, not screenshot provenance or label correctness.
    There is no model invocation here; labels cannot enter the original request.
    """
    request=parse(request_bytes)
    fields(request,{'schemaVersion','mode','root','pairs'})
    require(request['schemaVersion']==1 and request['mode'] in ('off','score'),'request_contract')
    require(reply['schemaVersion']==1 and reply['task']=='focus-change-only' and
        reply['requestSHA256']==hashlib.sha256(request_bytes).hexdigest() and
        reply['mode']==request['mode'] and reply['modelID'] in MODEL_TREES and
        reply['backend']=='cpuOnly' and reply['inputEncoding']=='paired-rgb-letterbox192x128-pillow-bilinear-v1' and
        reply['changedThreshold']==.85 and reply['unchangedThreshold']==.15 and
        reply['releaseEligible'] is False,'reply_contract')
    scored=request['mode']=='score'
    require(reply['modelLoaded'] is scored and reply['compiledTreeSHA256']==
        (MODEL_TREES[reply['modelID']] if scored else 'not_loaded'),'loaded_artifact')
    pairs=request['pairs']; results=reply['results']
    require(type(pairs) is list and 1<=len(pairs)<=128 and len(results)==len(pairs) and len(labels)==len(pairs),'reply_membership')
    cases=[]; failed=0
    for pair,result,label in zip(pairs,results,labels):
        fields(pair,{'id','actionID','beforeObservationID','afterObservationID','before','after'})
        for side in ('before','after'):fields(pair[side],{'path','sha256'})
        for key in ('id','actionID','beforeObservationID','afterObservationID'):
            require(result[key]==pair[key],'reply_identity')
        require(result['beforeSHA256']==pair['before']['sha256'] and result['afterSHA256']==pair['after']['sha256'],'reply_images')
        state=result['state']; require(state in ({'scored','failed'} if scored else {'skipped'}),'reply_state')
        failed+=state=='failed'
        bind=dict(case_id=pair['id'],action_id=pair['actionID'],before_observation_id=pair['beforeObservationID'],
            after_observation_id=pair['afterObservationID'],before_sha256=pair['before']['sha256'],after_sha256=pair['after']['sha256'])
        prediction=dict(binding=bind,model_id=reply['modelID'],state='inference_failed' if state=='failed' else state,
                        probability=result.get('probability'),decision=result.get('decision'))
        cases.append(dict(binding=bind,prediction=prediction,label=label,
                          context=dict(highlight_geometry='unknown',content_motion='unknown')))
    require(type(reply['failed']) is int and reply['failed']==failed,'failure_accounting')
    return run(dict(version=VERSION,test_only=test_only,cases=cases,module_cases=[]))


def binding(value):
    fields(value,BINDING)
    for key,text in value.items():
        require(type(text) is str and 0<len(text.encode())<=512,'binding_value')
        if key.endswith('_sha256'):require(re.fullmatch('[0-9a-f]{64}',text) is not None,'binding_hash')


def decision(probability):
    require(type(probability) in (int,float) and math.isfinite(probability) and 0<=probability<=1,'probability')
    return 'changed' if probability>=.85 else 'unchanged' if probability<=.15 else 'uncertain'


def evaluate(case):
    fields(case,{'binding','prediction','label','context'})
    binding(case['binding'])
    prediction,label,context=case['prediction'],case['label'],case['context']
    fields(prediction,{'binding','model_id','state','probability','decision'})
    fields(label,{'binding','source','relation','review_id'})
    fields(context,{'highlight_geometry','content_motion'})
    for record in (prediction,label):
        binding(record['binding']);require(record['binding']==case['binding'],'association_mismatch')
    require(prediction['model_id'] in MODEL_TREES,'model_id')
    state=prediction['state']; require(state in STATES,'prediction_state')
    require(label['source'] in ('reviewed','native_hint','unknown'),'label_source')
    require(label['relation'] in ('changed','unchanged','unknown'),'label_relation')
    require(type(label['review_id']) is str,'review_id')
    if label['source']=='reviewed':require(bool(label['review_id']),'missing_review')
    else:require(label['review_id']=='','false_review_claim')
    if label['source']=='unknown':require(label['relation']=='unknown','unknown_truth')
    require(context['highlight_geometry'] in ('stationary','moved','unknown') and
            context['content_motion'] in ('stationary','scrolling','animated','unknown'),'context')
    result=dict(case_id=case['binding']['case_id'],outcome='not_assessed',correct=None,
                abstained=False,native_hint_disagreement=None,accuracy_denominator=0,training_eligible=False)
    if state!='scored':
        require(prediction['probability'] is None and prediction['decision'] is None,'failure_is_not_prediction')
        result['reason']=state;return result
    observed=decision(prediction['probability']);require(prediction['decision']==observed,'decision_mismatch')
    result['abstained']=observed=='uncertain'
    if label['source']=='native_hint' and label['relation']!='unknown':
        result['native_hint_disagreement']=None if result['abstained'] else observed!=label['relation']
        result['reason']='unreviewed_native_hint';return result
    if label['source']!='reviewed' or label['relation']=='unknown':
        result['reason']='missing_reviewed_truth';return result
    if result['abstained']:
        result['outcome']='abstained';result['reason']='model_uncertain';return result
    result.update(outcome='scored_development',correct=observed==label['relation'],
                  accuracy_denominator=1,reason='reviewed_identity_relation')
    return result


def optional_module(record):
    """Validate normalized test observations, not attest execution or packaging."""
    fields(record,{'module_present','enabled','model_loads','pixel_reads','inference_calls',
        'state','queue_peak','queue_limit','navigation_before','navigation_after'})
    for key in ('module_present','enabled'):require(type(record[key]) is bool,'module_boolean')
    for key in ('model_loads','pixel_reads','inference_calls','queue_peak','queue_limit'):
        require(type(record[key]) is int and record[key]>=0,'module_count')
    require(record['queue_limit']==8 and record['queue_peak']<=8,'queue_bound')
    require(type(record['navigation_before']) is list and type(record['navigation_after']) is list and
            record['navigation_before']==record['navigation_after'],'navigation_interference')
    require(record['state'] in STATES,'module_state')
    if not record['enabled'] or not record['module_present']:
        require(record['model_loads']==record['pixel_reads']==record['inference_calls']==0,'optional_access')
        expected='skipped' if not record['enabled'] else 'model_unavailable'
        require(record['state']==expected,'optional_state')
    elif record['state']=='scored':
        require(record['model_loads']>0 and record['pixel_reads']>0 and record['inference_calls']>0,'scored_without_execution')
    return dict(contract_passed=True,execution_attested=False,navigation_authority=False)


def run(document):
    fields(document,{'version','test_only','cases','module_cases'})
    require(document['version']==VERSION and type(document['test_only']) is bool,'version_or_role')
    require(type(document['cases']) is list and len(document['cases'])<=200 and
            type(document['module_cases']) is list and len(document['module_cases'])<=64,'batch_bound')
    ids=[v['binding']['case_id'] for v in document['cases']]
    require(len(ids)==len(set(ids)),'duplicate_case')
    results=[evaluate(v) for v in document['cases']]
    modules=[optional_module(v) for v in document['module_cases']]
    return dict(version=VERSION,test_only=document['test_only'],results=results,module_results=modules,
        accounting=dict(cases=len(results),assessed=sum(v['accuracy_denominator'] for v in results),
            correct=sum(v['correct'] is True for v in results),abstained=sum(v['abstained'] for v in results),
            native_hint_disagreements=sum(v['native_hint_disagreement'] is True for v in results)),
        training_eligible=False,independent_evaluation=False,execution_attested=False)


def inspect_peer_report(path):
    """Inspect retained producer metadata without claiming pixels, truth or execution."""
    import yaml
    require(path.stat().st_size<=1_048_576,'document_size')
    raw=path.read_bytes();require(len(raw)<=1_048_576,'document_size')
    class Unique(yaml.SafeLoader):pass
    def mapping(loader,node):
        result={}
        for key,value in node.value:
            key=loader.construct_object(key)
            require(type(key) is str and key not in result,'duplicate_or_invalid_key')
            result[key]=loader.construct_object(value)
        return result
    Unique.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,mapping)
    # Reject aliases: these diagnostic receipts have no legitimate recursive/shared nodes.
    try:
        depth=0;events=0
        for event in yaml.parse(raw):
            events+=1;require(events<=20000,'yaml_events')
            require(not isinstance(event,yaml.events.AliasEvent),'yaml_alias')
            if isinstance(event,(yaml.events.MappingStartEvent,yaml.events.SequenceStartEvent)):
                depth+=1;require(depth<=32,'yaml_depth')
            elif isinstance(event,(yaml.events.MappingEndEvent,yaml.events.SequenceEndEvent)):depth-=1
        doc=yaml.load(raw,Loader=Unique)
    except yaml.YAMLError as error:raise ValueError('yaml_syntax') from error
    require(type(doc) is dict and type(doc.get('schema_version')) is int and doc.get('schema_version')==1 and doc.get('from')=='TVTestRig' and
            doc.get('to')=='NUIAK' and doc.get('request_id')=='nuiak-20261004-dtm030-shadow-delivery','peer_contract')
    report=doc.get('feedback',doc)
    require(report.get('images_transferred') is False and doc.get('navigation_authority') is False,'peer_scope')
    summaries={};sources=[];totals=[]
    for name,model in [('dtm025',MODEL),('dtm030','focus-transition-experimental-dtm030-change-v1')]:
        row=report[name]
        require(row['state']=='completed' and row['model_id']==model and row['backend']=='cpuOnly' and
                row['compiled_tree_sha256']==MODEL_TREES[model] and row['contract_sha256']==MODEL_CONTRACTS[model] and
                row['navigation_authority'] is False and row['mode']=='retained_iteration','peer_model_contract')
        for field in ('source_survey_sha256','prediction_sha256','binary_sha256','source_manifest_sha256'):
            require(type(row[field]) is str and re.fullmatch('[0-9a-f]{64}',row[field]) is not None,'peer_hash')
        require(row['source_manifest_sha256'] in MODEL_MANIFESTS[model],'peer_manifest')
        counts=row['counts']
        require(type(counts) is dict and set(counts)<= {'native_hint_agreement','native_hint_disagreement','native_focus_unavailable'},'peer_counts')
        require(all(type(x) is int and x>=0 for x in counts.values()),'peer_count_value')
        total=sum(counts.values());require(0<total<=128,'peer_count_bound')
        sources.append(row['source_survey_sha256']);totals.append(total)
        summaries[name]=dict(producerReportedCounts=counts,intervals=total,
            nativeHintAvailable=total-counts.get('native_focus_unavailable',0))
    require(sources[0]==sources[1] and totals[0]==totals[1],'incompatible_comparison')
    require(summaries['dtm025']['nativeHintAvailable']==summaries['dtm030']['nativeHintAvailable'],'incompatible_hint_membership')
    cases=doc.get('cases',[]);require(type(cases) is list and len(cases)<=128,'peer_cases')
    differing=[];ids=set();frames=set()
    if cases:require(len(cases)==totals[0],'peer_case_accounting')
    for row in cases:
        require(type(row['id']) is str and row['id'] not in ids and row['id'].startswith(report['operation']+':'),'peer_case_identity')
        ids.add(row['id'])
        for side in ('before_sha256','after_sha256'):
            require(type(row[side]) is str and re.fullmatch('[0-9a-f]{64}',row[side]) is not None,'peer_case_hash')
            frames.add(row[side])
        require(row['dtm025'] in ('changed','unchanged','uncertain') and row['dtm030'] in ('changed','unchanged','uncertain'),'peer_decision')
        if row['dtm025']!=row['dtm030']:differing.append(row['id'])
    return dict(version='peer-shadow-inspection-v1',reportID=doc['id'],rawSHA256=hashlib.sha256(raw).hexdigest(),
        sourceSurveySHA256=sources[0],models=summaries,caseRows=len(cases),uniqueFrameHashes=len(frames),
        differingDecisionIDs=differing,internalMetadataChecksPassed=True,
        localInferenceVerified=False,imagesVerified=False,reviewedAccuracy=None,trainingEligible=False,
        independentEvaluation=False,executionAttested=False,
        missing=['original images','raw inference requests/replies','case-bound reviewed truth','prospective independent membership'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--input',type=Path);modes.add_argument('--peer-report',type=Path)
    args=parser.parse_args()
    try:print(json.dumps(inspect_peer_report(args.peer_report) if args.peer_report else run(load(args.input)),indent=2,allow_nan=False))
    except (ValueError,KeyError,TypeError,OSError) as error:
        print(json.dumps(dict(rejected=True,reason=str(error))));raise SystemExit(2)
