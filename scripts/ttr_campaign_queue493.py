"""Run pinned TTR campaigns through the existing queue. Never retry dispatch."""
import json
import os
from pathlib import Path
import signal
import subprocess
import time

import research_queue as q
from experiment_templates import checked

OUT = None
STEP = 'ttr_campaign_queue493.run'
TARGET = '9026ECA9-77DB-4AE6-8FE6-BB239E9571FA'


def validate_config(config):
    q.require(config.get('version') == 'ttr-campaign-queue-v1', 'campaign_config_version')
    manifest = config['manifest']
    q.require(manifest['target'] == {'simulator_udid': TARGET, 'fixture_url': 'http://127.0.0.1:8080'}, 'campaign_target')
    q.require(len(manifest['cases']) == 4 and len({c['case_id'] for c in manifest['cases']}) == 4, 'campaign_membership')
    q.require(type(manifest.get('reuse_runner')) is bool, 'campaign_reuse_flag')
    q.require(all(c.get('transition') and not c.get('interruption') and c.get('split_group') == 'validation'
                  for c in manifest['cases']), 'campaign_transition_scope')
    q.require(manifest['budget']['max_wall_clock_seconds'] <= 600 and
              manifest['budget']['max_retained_bytes'] <= 100000000, 'campaign_producer_budget')
    q.require(config['order'] in (1, 2, 3, 4) and manifest['reuse_runner'] == (config['order'] in (2, 3)), 'campaign_order')
    helper=Path(config['helper']['path'])
    q.require(helper.is_absolute() and helper.name == 'aatv' and helper.parent.name == 'Helpers' and
              'Developer/TVTestRig/.local-work/' in str(helper), 'campaign_source_helper')
    return manifest


class Client:
    def __init__(self, config, output):
        self.config, self.output, self.sequence = config, output, 0
        if 'callerExport' in config:
            self.export_pins()

    def export_pins(self):
        pins=self.config['callerExport']
        q.require(set(pins)=={'script','dependency','helper'}, 'campaign_export_pins')
        for ref in pins.values():
            path=Path(ref['path'])
            q.require(path.is_absolute() and path.is_file() and q.digest(path)==ref['sha256'],
                      'campaign_export_source_changed')
        script=Path(pins['script']['path'])
        q.require(script.name=='export-campaign.rb' and
                  Path(pins['dependency']['path'])==script.with_name('export-fixture-job.rb'),
                  'campaign_export_dependency')
        return pins

    def call(self, *args, timeout=30):
        if args[:2] == ('campaign', 'export') and 'callerExport' in self.config:
            return self.export(args[2], Path(args[4]), timeout)
        self.sequence += 1
        helper=Path(self.config['helper']['path'])
        q.require(q.digest(helper) == self.config['helper']['sha256'], 'campaign_helper_changed')
        env=dict(os.environ);env.pop('TVTESTRIG_PROJECT',None)
        result=subprocess.run([str(helper),'--json',*args],capture_output=True,text=True,timeout=timeout,env=env)
        q.save(self.output/f'call-{self.sequence:03d}.json',dict(arguments=list(args),returnCode=result.returncode,
              stdout=result.stdout,stderr=result.stderr))
        doc=json.loads(result.stdout)
        q.require(result.returncode == 0 and doc.get('success') is True, 'campaign_call_failed:'+str(doc.get('error')))
        return next(iter(doc['data'].values()))['_0']

    def export(self, campaign, destination, timeout):
        """Use TTR's pinned caller exporter. Never fall back to another capture."""
        pins=self.export_pins()
        script=Path(pins['script']['path'])
        q.require(destination.parent.resolve()==self.output.resolve() and not destination.exists(),
                  'campaign_export_destination')
        self.sequence+=1
        result=subprocess.run(['/usr/bin/ruby',str(script),pins['helper']['path'],campaign,str(destination)],
            capture_output=True,text=True,timeout=timeout)
        q.save(self.output/f'call-{self.sequence:03d}.json',dict(arguments=['caller-export',campaign],
            returnCode=result.returncode,stdout=result.stdout,stderr=result.stderr))
        q.require(result.returncode==0,'campaign_caller_export_failed:'+result.stderr[-500:])
        report=json.loads(result.stdout)
        q.require(report['campaign']['campaign_id']==campaign and
                  Path(report['exported_path']).resolve()==destination.resolve(), 'campaign_export_identity')
        for member in report['files']:
            path=destination/member['path']
            q.require(path.resolve().is_relative_to(destination.resolve()) and not path.is_symlink() and
                      path.is_file() and path.stat().st_size==member['bytes'] and
                      q.digest(path)==member['sha256'], 'campaign_export_bytes')
        q.save(self.output/'export-receipt.json',report)
        return dict(export_path=str(destination))


def readiness(client):
    value=client.call('simulator','readiness','--simulator-udid',TARGET)
    q.require(value.get('can_run') is True and value.get('ownership') and
              all(r['state']=='clear' for r in value['ownership']), 'campaign_target_not_clear')
    return value


def fixture_binding(config):
    from direct_tvos_capture import bind_target, Fixture
    binding = bind_target(TARGET, 'http://127.0.0.1:8080')
    q.require(binding['binaries'] == config['fixtureBinaries'], 'campaign_fixture_changed')
    return dict(binding=binding, snapshot=Fixture('http://127.0.0.1:8080').snapshot())


def export_labels(folder, manifest):
    """Reuse the native transition validator. Unknown semantic tags stay unknown."""
    from focus_corrected_transition_audit import validate_case
    cases={c['case_id']:c for c in manifest['cases']}; found={}; images=[]; labels=[]
    for path in sorted(folder.rglob('transition-case.json')):
        doc=q.load(path);ident=doc['case_id']
        q.require(ident in cases and ident not in found,'campaign_export_membership')
        evidence,before,after=validate_case(folder,path,cases[ident])
        q.require(evidence.get('cleanup') == 'verified', 'campaign_case_cleanup')
        found[ident]=True
        for role, endpoint in zip(('before','after'),(before,after)):
            image=path.parent/(role+'.png')
            q.require(image.is_file(),'campaign_image_missing')
            images.append(dict(path=str(image.relative_to(folder.parent)),sha256=q.digest(image)))
            labels.append(dict(case=ident,endpoint=role,focus=endpoint['focus'],controls=endpoint['controls'],
                group=cases[ident]['independence_group'],role='calibration',trainingEligible=False,
                condition=cases[ident]['transition']['condition'],
                missingTags=['selected-but-unfocused','decorative-border','bright-artwork']))
    q.require(set(found)==set(cases) and len(images)==8,'campaign_export_incomplete')
    return images, labels


def execute(config, client, output, clock=time.monotonic, sleep=time.sleep, intake=export_labels):
    manifest=validate_config(config); ident=manifest['campaign_id']; started=clock()
    marker=q.ROOT/'.build'/('campaign493-'+ident+'.json')
    marker.parent.mkdir(parents=True, exist_ok=True)
    q.require(not marker.exists(),'campaign_dispatch_already_attempted')
    readiness(client)
    q.save(output/'fixture-before.json', fixture_binding(config))
    idle=client.call('status')
    q.require(idle.get('commandActive') is False and idle.get('observationActive') is False and
              idle.get('queuedCommandCount') == 0,'campaign_coordinator_occupied')
    client.call('campaign','validate','--manifest-json',json.dumps(manifest))
    # Save before dispatch. A lost reply cannot authorize another start.
    q.save(marker,dict(campaign=ident,manifestSHA256=q.text_digest(manifest),output=str(output)))
    active=True; prior=signal.getsignal(signal.SIGTERM)
    def stop(*_):
        raise RuntimeError('campaign_cancelled_by_queue')
    signal.signal(signal.SIGTERM,stop)
    try:
        client.call('campaign','start','--manifest-json',json.dumps(manifest))
        while True:
            report=client.call('campaign','status',ident)
            q.save(output/'campaign-status.json',report,replace=True)
            if report['state'] not in ('running','cancelling'):break
            q.require(clock()-started < 620,'campaign_collection_deadline')
            sleep(2)
        active=False
        q.require(report['state']=='completed' and report['completed_cases']==4 and
                  report.get('failed_cases',0)==0,'campaign_incomplete')
        collected=clock()-started
        postflight=readiness(client)
        exported=client.call('campaign','export',ident,'--output-dir',str(output/'corpus'),timeout=100)
        q.require(Path(exported['export_path']).resolve()==(output/'corpus').resolve(),'campaign_export_path')
        exported_at=clock()
        images,labels=intake(output/'corpus',manifest)
        q.save(output/'fixture-after.json', fixture_binding(config))
        q.save(output/'labels.json',dict(version='campaign-observed-labels-v1',rows=labels,trainingEligible=False))
        result=dict(version='campaign-session-comparison-v1',campaign=ident,order=config['order'],reuse=manifest['reuse_runner'],
            cleanup=True,postflight=postflight,collectionSeconds=collected,exportSeconds=exported_at-started-collected,
            validationSeconds=clock()-exported_at,totalSeconds=clock()-started,
            campaignSeconds=report.get('elapsed_seconds'),acceptedFrames=len(images),
            modelAccepted=False,settingChanged=False,manifest=manifest,
            limitation='No model acceptance. Shared Fixture ancestry is not independent app evidence.')
        q.save(output/'session-result.json',result)
        q.save(output/'capture-evidence.json',dict(version='research-capture-evidence-v1',images=images,cleanup=True))
    finally:
        if active:
            # Cancel only our campaign. Retain the marker even after terminal cleanup.
            try:
                client.call('campaign','cancel',ident)
                report=client.call('campaign','status',ident)
                q.save(output/'cancel-status.json',report)
            except Exception as error:
                q.save(output/'cleanup-error.json',dict(error=str(error)))
        signal.signal(signal.SIGTERM,prior)


def run():
    spec=q.load(OUT.parents[2]/'spec.json')
    config=q.load(checked(spec['capture']['plan']))
    for dependency in q.load(OUT/'dependencies.json'):
        for reference in dependency['outputs']:
            receipt=q.load(checked(reference))
            q.require(receipt.get('cleanup') is True and receipt.get('modelAccepted') is False,
                      'campaign_dependency_cleanup')
    execute(config,Client(config,OUT),OUT)


def compare():
    """Compare matched label signatures before interpreting elapsed time."""
    rows=[]
    for dependency in q.load(OUT/'dependencies.json'):
        files={Path(p['path']).name:q.load(checked(p)) for p in dependency['outputs']}
        result=files['session-result.json']; labels=files['labels.json']['rows']
        signature=sorted(labels,key=lambda x:(x['case'],x['endpoint']))
        rows.append(dict(order=result['order'],reuse=result['reuse'],seconds=result['totalSeconds'],
                         campaignSeconds=result.get('campaignSeconds'),
                         frames=result['acceptedFrames'],signature=signature,cleanup=result['cleanup']))
    rows.sort(key=lambda x:x['order'])
    q.require([r['order'] for r in rows]==[1,2,3,4], 'comparison_four_arms')
    producer=all(type(r['campaignSeconds']) in (int,float) and r['campaignSeconds']>=0 for r in rows)
    if producer:
        for row in rows: row['seconds']=row['campaignSeconds']
    q.require(all(type(r['seconds']) in (int,float) and r['seconds']>=0 for r in rows),'comparison_timing_missing')
    matched=all(r['signature']==rows[0]['signature'] and r['cleanup'] for r in rows)
    separate=sum(r['seconds'] for r in rows if not r['reuse'])
    reused=sum(r['seconds'] for r in rows if r['reuse'])
    report=dict(version='campaign-reuse-comparison-v1',matchedLabels=matched,
                timingScope='TTR campaign elapsed; excludes caller export and label validation' if producer else 'caller total',
                separateSeconds=separate,reusedSeconds=reused,
                speedup=separate/reused if reused else None,
                outcome='supported' if matched and rows[1]['seconds'] < rows[0]['seconds'] and
                    rows[2]['seconds'] < rows[3]['seconds'] else 'contradicted' if not matched else 'inconclusive',
                rows=rows,modelAccepted=False,
                limitation='Two repetitions per arm. Shared Fixture ancestry. Timing evidence is preliminary.')
    q.save(OUT/'comparison.json',report)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path='comparison.json',sha256=q.digest(OUT/'comparison.json'))]))


def recover_import():
    """Validate retained capture bytes. Never contact TTR or dispatch capture."""
    spec=q.load(OUT.parents[2]/'spec.json')
    refs={Path(p['path']).name:checked(p) for p in spec['inputs']}
    failure=refs['result.json'];result=q.load(failure)
    q.require(result['job']=='adr493-session-1-r4' and result['status']=='failed','retained_attempt')
    old=q.load(failure.parents[2]/'spec.json')
    q.require(q.text_digest(old)==result['specSHA256'],'retained_spec_changed')
    config=q.load(checked(old['capture']['plan']))
    receipt=q.load(refs['export-receipt.json']);corpus=refs['export-receipt.json'].parent/'corpus'
    q.require(Path(receipt['exported_path']).resolve()==corpus.resolve(),'retained_export_path')
    for member in receipt['files']:
        path=corpus/member['path']
        q.require(path.resolve().is_relative_to(corpus.resolve()) and not path.is_symlink() and
                  path.is_file() and path.stat().st_size==member['bytes'] and q.digest(path)==member['sha256'],
                  'retained_export_changed')
    report=q.load(refs['campaign-status.json'])
    exported_report={k:v for k,v in receipt['campaign'].items() if k!='export_path'}
    q.require(report==exported_report and report['state']=='completed' and
              report['completed_cases']==4 and report['failed_cases']==0 and
              report['campaign_id']==config['manifest']['campaign_id'],'retained_campaign_incomplete')
    images,labels=export_labels(corpus,config['manifest'])
    q.save(OUT/'labels.json',dict(version='campaign-observed-labels-v1',rows=labels,trainingEligible=False))
    q.save(OUT/'session-result.json',dict(version='campaign-session-comparison-v1',campaign=report['campaign_id'],
        order=config['order'],reuse=config['manifest']['reuse_runner'],cleanup=True,
        totalSeconds=None,campaignSeconds=report['elapsed_seconds'],acceptedFrames=len(images),modelAccepted=False,
        settingChanged=False,manifest=config['manifest'],retainedAttempt=str(failure),
        limitation='Retained import only. Caller total timing is unavailable. No capture repeats.'))
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path=n,sha256=q.digest(OUT/n)) for n in ('labels.json','session-result.json')]))
