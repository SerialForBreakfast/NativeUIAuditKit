"""Prepare native HCF pilots without starting or restarting the background runner."""
import copy
import research_queue as q
from research_campaign340 import pin
import dataset351
import hcf_capture362 as h


def register():
    folder=q.ROOT/'Research/ResearchSpecs/HCF362';folder.mkdir(parents=True,exist_ok=True)
    qualification_path=q.ROOT/'reports/work/HCF362/qualification-01/qualification.json'
    qualification=q.load(qualification_path)
    q.require(qualification['complete'] and qualification['restoration']=='verified','caller_unqualified')
    original=dataset351.run(None)
    refs=[pin(q.ROOT/'scripts'/name) for name in ('generation352.py','hcf_capture362.py','qualify_hcf362.py',
        'dataset351.py','native343.py','direct_tvos_capture.py','fixture_rendered_body.py',
        'focus_batch_harness.py','hcf361.py')]+[pin(qualification_path)]
    additions=[]
    # These native cue pilots are not the varied training corpus.
    for name,size,background in [('small-dark',160,0x181818),('large-dark',320,0x181818),('small-light',160,0xCCCCCC)]:
        ident='hcf362-'+name+'-capture'
        q.require(not (q.QUEUE/'jobs'/ident).exists(),'already_registered:'+ident)
        recipe=dataset351.clean(original['original']['scene']['recipe'])
        comp=recipe['appearance']['composition']
        for definition in comp['definitions'].values():
            definition['width']=definition['height']=size
        comp['styles']['image']['focus']={'kind':'native_image','version':1}
        comp['styles']['image']['background']=background
        plan=dict(version='native-hcf362-v1',binding=original['binding'],recipe=recipe,
            role='development',trainingEligible=False,profiles=['standard','hcf'],
            targets=['item-0','item-3'],expectedFrames=8,originalProfile='standard',
            qualification=dict(complete=True,restoration='verified',evidence=pin(qualification_path)),
            helperSHA256=q.digest(h.CLI.resolve()),group='hcf362-native-cue-pilot',
            nativeReceiptBudgetBytes=1<<30,
            limitation='One related native image-card family. No real-app or training qualification.')
        h.validate_plan(plan)
        pp=folder/(name+'-plan.json');q.save(pp,plan)
        spec=dict(version=q.SPEC_VERSION,id=ident,task='HCF362',owner='research-host-NUIAK',
            kind='screen',authority='capture',
            hypothesis=f'Does OS HCF change native image-card focus for {size}-point controls on the {name.split("-")[-1]} background?',
            decisionRule='Compare matched profiles and repeat noise. Restore OS state and Fixture. Do not admit training data.',
            inputs=refs,capture=dict(target=h.n.TARGET,endpoint=plan['binding']['endpoint'],plan=pin(pp),
                approval='The maintainer approves native HCF Simulator data and queued capture. Retain at most 1 GiB of TTR receipts per pilot, plus 100 MB of queue output, within the 250 GiB study.'),
            adapter=dict(type='python-callable',steps=['generation352.run'],outputAttributes=['generation352.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        path=folder/(ident+'.json');q.save(path,spec);q.submit(path)
        additions.append(dict(id=ident,sha256=q.text_digest(spec)))
        compare=copy.deepcopy(spec);compare.pop('capture')
        compare.update(id='hcf362-'+name+'-compare',authority='diagnostic',
            hypothesis=f'Measure Standard/HCF differences and repeat noise on the same {name} native controls.',
            decisionRule='Do profile differences exceed capture noise? Report missing native cues without declaring HCF untrainable.',
            dependencies=[dict(job=ident,specSHA256=q.text_digest(spec),outputs=['capture/capture.json'])],
            adapter=dict(type='python-callable',steps=['hcf_capture362.compare'],outputAttributes=['hcf_capture362.OUT']))
        path=folder/(compare['id']+'.json');q.save(path,compare);q.submit(path)
        additions.append(dict(id=compare['id'],sha256=q.text_digest(compare)))
    q.save(q.ROOT/'reports/work/HCF362/additions.json',additions)
    return additions


if __name__=='__main__':
    print(register())
