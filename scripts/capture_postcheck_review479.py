"""Review a budget-only postcheck using the successful restoration observation."""
import copy
import shutil
from pathlib import Path
import research_queue as q
from experiment_templates import checked
import native_control_admission as admission

OUT = None


def validate(capture, plan, native):
    q.require(capture.get('complete') is False and capture.get('cleanup') is True and
              capture.get('cleanupErrors') == [] and capture.get('error') == 'profile-hcf:None',
              'postcheck_failure_scope')
    state=native['data']['navigationRoute']['_0']['hcf']
    q.require(state.get('requested') == 'hcf' and state.get('status') == 'stopped' and
              state.get('desiredVerified') is False and state.get('inputs') == 0 and
              state.get('inputsAttempted') == 0 and 'HCF evidence budget exhausted' in state.get('reason',''),
              'postcheck_native_cause')
    receipts=capture['profileReceipts']
    q.require([r['profile'] for r in receipts] == ['standard','hcf','standard'], 'postcheck_profiles')
    for row in receipts:
        hcf=row['receipt']['hcf']
        q.require(hcf.get('status') == 'completed' and hcf.get('desiredVerified') is True and
                  hcf.get('observed') == row['profile'], 'postcheck_profile_unverified')
    q.require(capture['originalProfile'] == 'standard' and
              receipts[-1]['receipt']['hcf'].get('original') == 'hcf', 'postcheck_restore_origin')
    frames=capture['frames']
    expected={(c['id'],p,t) for c in plan['cases'] for p in plan['profiles'] for t in c['targets']}
    actual=[(f['case'],f['profile'],f['focus']) for f in frames]
    q.require(len(actual) == len(set(actual)) == plan['expectedFrames'] and set(actual) == expected,
              'postcheck_membership')
    q.require(all(f['repeat'] == 0 and f['end'] < receipts[-1]['time'] for f in frames), 'postcheck_order')


def run():
    spec=q.load(OUT.parents[2]/'spec.json')
    review=q.load(checked(spec['reviewPlan']))
    result_path=checked(review['failedResult']);result=q.load(result_path)
    original=q.load(checked(review['failedSpec']))
    q.require(result['status']=='failed' and result['reason']=='process_failed' and
              result['specSHA256']==q.text_digest(original), 'postcheck_identity')
    q.require(q.outputs_intact(result_path.parent,result), 'postcheck_outputs_changed')
    artifact=q.load(result_path.parent/'out/artifact.json')
    import hcf_study371 as study
    root=study.verify_storage(artifact['storage'])
    source=Path(artifact['path'])
    q.require(source.resolve()==source and source.is_relative_to(root) and
              q.digest(source)==artifact['sha256'], 'postcheck_source_changed')
    capture=q.load(source);native=q.load(checked(review['nativeFailure']))
    validate(capture,artifact['plan'],native)
    destination=root/spec['id'];q.require(not destination.exists(),'postcheck_collision');destination.mkdir()
    for frame in capture['frames']:
        image=q.local_path(source.parent,frame['path'])
        q.require(q.digest(image)==frame['sha256'],'postcheck_image_changed')
        target=q.local_path(destination,frame['path']);shutil.copyfile(image,target)
        q.require(q.digest(target)==frame['sha256'],'postcheck_copy_changed')
    derived=copy.deepcopy(capture)
    derived.update(complete=True,error=None,postcheckReview=dict(originalCapture=str(source),
        originalSHA256=artifact['sha256'],originalFailure=capture['error'],captureRepeated=False,
        basis='Verified restoration observes original HCF after a zero-input budget stop.'))
    q.save(destination/'capture.json',derived)
    published=copy.deepcopy(artifact);published.update(path=str(destination/'capture.json'),sha256=q.digest(destination/'capture.json'))
    roles={c['group']:'development' for c in artifact['plan']['cases']}
    rows=admission.admit_artifact(published,roles,root,spec['id'])
    q.save(OUT/'artifact.json',published)
    q.save(OUT/'review.json',dict(frames=len(rows),captureRepeated=False,trainingAdmitted=False,modelAccepted=False,
        original=review['failedResult'],nativeFailure=review['nativeFailure']))
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path=n,sha256=q.digest(OUT/n)) for n in ('artifact.json','review.json')]))
