"""Register 2 existing-model diagnostics on retained HCF pilot images."""
import research_queue as q
from research_campaign340 import pin


def register():
    folder = q.ROOT/'Research/ResearchSpecs/HCF361'
    specs = []
    for model in ('fdr021-reviewed-contrast', 'fdr038-retention234'):
        ident = 'hcf361-baseline-'+model.split('-')[0]
        q.require(not (q.QUEUE/'jobs'/ident).exists(), 'already_registered')
        weights = pin(q.ROOT/'NativeUITrainer/focus_ring_runs'/model/'weights/best.pt')
        refs = [weights] + [pin(q.ROOT/p) for p in (
            'scripts/hcf361_baseline.py', 'scripts/eval_focus_ring_detector.py',
            'scripts/focus_ring_backbone.py', 'scripts/focus_runtime.py',
            'Sources/NativeUIAuditKit/Detection/FocusRingClassifier.swift', '.build/debug/FocusRingTool')]
        metadata = {}
        for name in ('standard', 'hcf', 'hcf_card_unmatched'):
            p = q.ROOT/'reports/work/HCF357/extracted'/name/'synth-0_metadata.json'
            metadata[name] = pin(p); refs.append(pin(p)); doc = q.load(p)
            refs.extend(pin(p.parent/doc[s+'_png']) for s in ('focused', 'unfocused'))
        config = dict(inputs=refs, metadata=metadata, weights=weights)
        cp = folder/(ident+'-config.json'); q.save(cp, config)
        spec = dict(version=q.SPEC_VERSION, id=ident, task='HCF361', owner='research-host-NUIAK',
            kind='screen', authority='diagnostic',
            hypothesis='Score retained paired control crops with '+model+' using the production Swift cropper.',
            decisionRule='Identify reported-label misses before new training. Do not claim HCF benefit or qualified accuracy from this pilot.',
            inputs=refs, stage=[{'from':pin(cp), 'to':'config.json'}],
            adapter=dict(type='python-callable', steps=['hcf361_baseline.run'], outputAttributes=['hcf361_baseline.OUT']),
            limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1))
        path = folder/(ident+'.json'); q.save(path, spec); q.submit(path)
        specs.append(dict(id=ident, sha256=q.text_digest(spec)))
    q.save(q.ROOT/'reports/work/HCF361/baseline-additions.json', specs)
    return specs


if __name__ == '__main__': print(register())
