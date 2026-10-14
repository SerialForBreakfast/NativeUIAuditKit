"""Register bounded HCF preparation jobs without starting or restarting the runner."""
import research_queue as q
from research_campaign340 import pin


def register():
    folder = q.ROOT/'Research/ResearchSpecs/HCF361'
    folder.mkdir(parents=True, exist_ok=True)
    retained = q.ROOT/'reports/work/HCF357/extracted'
    jobs = [
        ('matched-profiles', 'Compare Standard and HCF pixels in unchanged production crops and fixed boundary crops.',
         'Does either image view contain an HCF-specific cue? Do not infer learnability from a setting label.', ['standard', 'hcf']),
        ('artwork-detail', 'Measure native artwork focus detail at full resolution, screen resolution, and crop resolution.',
         'Which view preserves focus-arrival evidence? The missing Standard counterpart still prevents an HCF benefit claim.', ['hcf_card_unmatched']),
        ('stage1000-design', 'Reserve roles and count capture work for the first 1,000 HCF training frames.',
         'How many paired images and scene groups must the producer supply before a matched training comparison?', []),
    ]
    additions = []
    for name, hypothesis, decision, profiles in jobs:
        ident = 'hcf361-' + name
        existing = q.QUEUE/'jobs'/ident/'spec.json'
        if existing.exists():
            spec = q.load(existing)
            additions.append(dict(id=ident, sha256=q.text_digest(spec)))
            continue
        refs = [pin(q.ROOT/'scripts/hcf361.py'), pin(q.ROOT/'scripts/focus_dataset_contract.py')]
        metadata = {}
        for profile in profiles:
            path = retained/profile/'synth-0_metadata.json'
            metadata[profile] = pin(path); refs.append(pin(path))
            doc = q.load(path)
            refs.extend(pin(path.parent/doc[state+'_png']) for state in ('focused', 'unfocused'))
        config = dict(mode='cue-review' if profiles else 'design', metadata=metadata,
                      inputs=refs, frames=1000)
        cp = folder/(ident+'-config.json'); q.save(cp, config)
        spec = dict(version=q.SPEC_VERSION, id=ident, task='HCF361', owner='research-host-NUIAK',
            kind='screen', authority='diagnostic', hypothesis=hypothesis, decisionRule=decision,
            inputs=refs, stage=[{'from':pin(cp), 'to':'config.json'}],
            adapter=dict(type='python-callable', steps=['hcf361.run'], outputAttributes=['hcf361.OUT']),
            limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1))
        sp = folder/(ident+'.json'); q.save(sp, spec); q.submit(sp)
        additions.append(dict(id=ident, sha256=q.text_digest(spec)))
    destination = q.ROOT/'reports/work/HCF361/additions.json'
    if destination.exists():
        q.require(q.load(destination) == additions, 'changed_additions')
    else:
        q.save(destination, additions)
    return additions


if __name__ == '__main__':
    print(register())
