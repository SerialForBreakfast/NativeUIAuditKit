"""Add duplicate audits without changing the active HCF graph."""
import research_queue as q
from research_campaign340 import pin


def register():
    folder=q.ROOT/'Research/ResearchSpecs/HCF374';folder.mkdir(exist_ok=True)
    code=pin(q.ROOT/'scripts/capture_duplicates374.py')
    snapshots=sorted(q.QUEUE.glob('jobs/hcf371r4-10-part-00[0-4]-verify/attempts/1/out/admission.json'))
    q.require(len(snapshots)==5,'snapshot_incomplete')
    binary=q.load(q.ROOT/'Research/ResearchSpecs/VISION353/vision353-00-fit-v2-config.json')['binary']
    jobs=[
      ('hcf371r4-11-duplicates-snapshot','frames','admission.json',None,[pin(p) for p in snapshots],
       'Do the first 2,000 captured frames contain repeated pixels or conflicting labels?',
       'Count distinct pixels and groups. Keep capture events; report conflicts before interpreting model results.'),
      ('hcf371r4-41-duplicates-corpus','frames','admission.json','hcf371r4-40-catalog',[],
       'Does the complete HCF study repeat pixels across training and evaluation?',
       'Identify exact conflicts and repeated weighting. Do not change frozen groups or claim model acceptance.'),
      ('hcf371r4-11-duplicates-vision','vision','admission.json','hcf371r4-10-part-005-verify',[],
       'Does Vision call real focus movements similar to identical screens?',
       'Compare identical frames, focus moves, profile changes, and different scenes. Use similarity only for review.'),
      ('hcf371r4-51-duplicates-crops','crops','crops.json','hcf371r4-50-crops',[],
       'Do repeated control crops overweight training or cross evaluation boundaries?',
       'Report unique HCF crops, duplicate labels, and role conflicts. Preserve original crop preprocessing.')]
    additions=[]
    for ident,mode,filename,producer,refs,question,decision in jobs:
        q.require(not (q.QUEUE/'jobs'/ident).exists(),'already_registered:'+ident)
        config=dict(mode=mode,manifestName=filename,manifests=refs)
        inputs=[code]+refs
        if mode=='vision':config['binary']=binary;inputs.append(binary)
        path=folder/(ident+'-config.json');q.save(path,config)
        spec=dict(version=q.SPEC_VERSION,id=ident,task='HCF371',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
            hypothesis=question,decisionRule=decision,inputs=inputs,stage=[dict(**{'from':pin(path)},to='config.json')],
            adapter=dict(type='python-callable',steps=['capture_duplicates374.run'],outputAttributes=['capture_duplicates374.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        if producer:
            ps=q.load(q.QUEUE/'jobs'/producer/'spec.json')
            spec['dependencies']=[dict(job=producer,specSHA256=q.text_digest(ps),outputs=[filename])]
        target=folder/(ident+'.json');q.save(target,spec);q.submit(target)
        additions.append(dict(id=ident,sha256=q.text_digest(spec)))
    q.save(folder/'additions.json',additions)
    print('Registered 4 audits. The existing background runner handles execution.')

if __name__=='__main__':register()
