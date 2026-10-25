"""Verify a completed campaign after queue evidence-read failure. Never contact TTR."""
from pathlib import Path
import research_queue as q
from experiment_templates import checked
from ttr_campaign_queue493 import export_labels, validate_config
OUT=None

def review(spec, output):
    source=checked(spec['reviewResult']);result=q.load(source)
    original=q.load(checked(spec['reviewSpec']))
    q.require(result['specSHA256']==q.text_digest(original),'review_spec_changed')
    missing=checked(spec['retentionReceipt'])
    q.require(result.get('status')=='failed' and result.get('returnCode')==0 and
              result.get('reason')=='evidence_not_read:'+q.relative(missing),'review_failure_scope')
    q.require(q.outputs_intact(source.parent,result),'review_outputs_changed')
    recovery=q.load(missing)
    q.require(recovery.get('cleanup') is True and recovery.get('modelAccepted') is False,'review_cleanup')
    config=q.load(checked(original['capture']['plan']));manifest=validate_config(config)
    origin=source.parent/'out';export=q.load(origin/'export-receipt.json')
    q.require(Path(export['exported_path']).resolve()==(origin/'corpus').resolve(),'review_export_path')
    status=q.load(origin/'campaign-status.json')
    q.require(status['campaign_id']==manifest['campaign_id'] and status['state']=='completed' and
              status['completed_cases']==4 and status['failed_cases']==0,'review_campaign_incomplete')
    q.require({k:v for k,v in export['campaign'].items() if k!='export_path'}==status,'review_export_status')
    for member in export['files']:
        path=origin/'corpus'/member['path']
        q.require(path.resolve().is_relative_to((origin/'corpus').resolve()) and not path.is_symlink() and
                  path.stat().st_size==member['bytes'] and q.digest(path)==member['sha256'],'review_export_changed')
    images,labels=export_labels(origin/'corpus',manifest)
    session=q.load(origin/'session-result.json')
    q.require(session['cleanup'] is True and session['campaign']==manifest['campaign_id'] and
              session['manifest']==manifest and session['order']==config['order'] and
              session['acceptedFrames']==len(images) and session['postflight']['can_run'] is True,'review_session')
    q.require(q.load(origin/'labels.json')['rows']==labels,'review_labels_changed')
    q.save(output/'session-result.json',session)
    q.save(output/'labels.json',dict(version='campaign-observed-labels-v1',rows=labels,trainingEligible=False))
    q.save(output/'review.json',dict(source=spec['reviewResult'],newCapture=False,newNavigation=False,modelAccepted=False))
    q.save(output/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path=name,sha256=q.digest(output/name)) for name in ('session-result.json','labels.json','review.json')]))

def run():
    review(q.load(OUT.parents[2]/'spec.json'),OUT)
