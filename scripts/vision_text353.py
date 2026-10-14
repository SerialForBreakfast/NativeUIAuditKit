"""Measure OCR stability on retained pairs without inventing text labels."""
import json
import subprocess
import research_queue as q
from compare351 import validate_capture

OUT = None


def stability(pairs, results):
    index = {r['id']: r for r in results}
    q.require(len(index) == len(results), 'duplicate_observations')
    q.require(not any(r['errors'] for r in results), 'ocr_request_failed')
    rows = []
    for p in pairs:
        q.require(p['before'] in index and p['after'] in index, 'missing_endpoint')
        words = [sorted(t['text'] for t in index[p[k]]['text']) for k in ('before','after')]
        rows.append(dict(case=p['case'], condition=p['condition'], changed=p['changed'],
            exactTextAgreement=words[0]==words[1], beforeCount=len(words[0]), afterCount=len(words[1]),
            bothEmpty=not words[0] and not words[1]))
    return dict(rows=rows, textAccuracy=None, labelAuthority='none_for_text',
        limitation='Text agreement is not OCR accuracy or stable focus. Empty results are reported separately.')


def run():
    config=q.load(OUT/'config.json')
    for ref in config['inputs']:
        q.require(q.digest(q.local_path(q.ROOT,ref['path']))==ref['sha256'],'input_changed')
    path=q.ROOT/config['capture']['path'];doc=q.load(path);frames=validate_capture(doc,path.parent)
    ids={p[k] for p in doc['pairs'] for k in ('before','after')}
    request=dict(version=1,root=str(q.ROOT),textOnly=True,**config['settings'],frames=[
        dict(id=k,path=str(path.parent/f['path']),sha256=f['sha256']) for k,f in frames.items() if k in ids])
    q.save(OUT/'request.json',request)
    with (OUT/'vision.json').open('x') as out,(OUT/'vision.stderr').open('x') as err:
        result=subprocess.run([str(q.ROOT/config['binary']['path'])],input=json.dumps(request),text=True,
                              stdout=out,stderr=err,timeout=740)
    q.require(result.returncode==0,'ocr_process_failed')
    receipt=q.load(OUT/'vision.json')
    q.require(len(receipt['results'])==len(ids) and {r['id'] for r in receipt['results']}==ids,'frame_membership')
    for row in receipt['results']:q.require(row['sha256']==frames[row['id']]['sha256'],'result_hash')
    q.save(OUT/'diagnostic.json',dict(version='vision353-text-v1',settings=config['settings'],inputs=config['inputs'],
        report=stability(doc['pairs'],receipt['results']),independentGroups=1,
        coldSeconds=receipt['results'][0]['ocrSeconds'],warmSeconds=[r['ocrSeconds'] for r in receipt['results'][1:]],
        modelAccepted=False,trainingEligible=False))


def summarize():
    dependencies=q.load(OUT/'dependencies.json');q.require(len(dependencies)==4,'dependency_count')
    results={}
    for dep in dependencies:
        for ref in [dep['result'],*dep['outputs']]:
            q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'changed_dependency')
        results[dep['job']]=q.load(q.ROOT/dep['outputs'][0]['path'])
    q.save(OUT/'comparison.json',dict(version='vision353-text-comparison-v1',results=results,
        selectedSetting=None,modelAccepted=False,nextDecision='Find text instability and empty results before requesting reviewed text labels.'))
