"""Register explicit capture prerequisites without claiming runnable capacity."""
import research_queue as q
from research_campaign340 import pin


def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS359';specs=[]
    names={1:'hero-swap',2:'selected-tab',3:'identical-rows',4:'library-state',5:'native-corners',
        6:'growth-curve',7:'clipping',8:'position-grid',9:'fonts',10:'alpha',11:'row-inversion',
        12:'palette',14:'animation',15:'no-focus',16:'renderer-gap',17:'journey-shadow',18:'family-holdout',19:'feature-cache'}
    for number,name in names.items():
        spec=dict(version=q.SPEC_VERSION,id=f'focus359-plan-{number:02d}-{name}',task='FOCUS359',
            owner='research-host-NUIAK',kind='screen',authority='diagnostic',
            hypothesis='Test proposal '+str(number)+' from the reviewed 7-family plan: '+name+'.',
            decisionRule='Require observed labels, matched inputs, per-condition counts, and retained-success comparisons. Do not claim navigation authority.',
            requirements=['peer-host-TTR: publish named 7-family source, recipe catalog, asset hashes, and one matching native capture receipt.',
                'research-host-NUIAK: qualify the specific control, freeze groups, and create a tested producer/comparison successor with exact inputs.'],
            inputs=[pin(q.ROOT/'scripts/study358.py')],stage=[],
            adapter=dict(type='python-callable',steps=['study358.blocked'],outputAttributes=['study358.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1),planningOnly=True,
            plan='Research/Plans/Focus359.md',executionBinding='Blocked planning entry. Keep immutable; create an executable successor after qualification.')
        path=folder/(spec['id']+'.json');q.save(path,spec);q.submit(path);specs.append(spec)
    q.save(q.ROOT/'reports/work/FOCUS359/family-additions.json',[dict(id=s['id'],sha256=q.text_digest(s)) for s in specs])


if __name__=='__main__':register()
