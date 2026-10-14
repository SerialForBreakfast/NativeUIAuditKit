"""Register approved diagnostics and explicit blocked stages without starting jobs."""
from pathlib import Path
import research_queue as q
from research_campaign340 import pin


def register():
    folder=q.ROOT/'Research/ResearchSpecs/HCF358'; folder.mkdir(exist_ok=True)
    source=pin(q.ROOT/'scripts/study358.py'); specs=[]
    def save(ident,hypothesis,decision,config=None,requirements=None):
        spec=dict(version=q.SPEC_VERSION,id=ident,task='HCF358',owner='research-host-NUIAK',
            kind='screen',authority='diagnostic',hypothesis=hypothesis,decisionRule=decision,
            inputs=[source],stage=[],adapter=dict(type='python-callable',steps=['study358.run' if config else 'study358.blocked'],
                outputAttributes=['study358.OUT']),limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        if config:
            cp=folder/(ident+'-config.json');q.save(cp,config)
            spec['inputs']+=config['inputs'];spec['stage']=[{'from':pin(cp),'to':'config.json'}]
        else:
            spec.update(requirements=requirements,planningOnly=True,plan='Research/Plans/WorkflowHCF357.md',
                executionBinding='Create an immutable successor after the named requirements pass. This entry cannot execute.')
        sp=folder/(ident+'.json');q.save(sp,spec);q.submit(sp);specs.append(spec)
    root=q.ROOT/'reports/work/HCF357/extracted'
    all_images=[]
    for family in ('standard','hcf','hcf_card_unmatched'):
        images=[pin(root/family/f'synth-0_{state}.png') for state in ('unfocused','focused')]
        all_images+=images
        save('hcf358-effect-'+family.replace('_','-'),
            'Measure retained focus-arrival pixels before and after resizing for '+family+'.',
            'Use measured changed area and magnitude to choose resolution tests. Do not infer HCF benefit from arrival alone.',
            dict(mode='profiles',comparison=family,images=images,inputs=images))
    fits=[pin(q.QUEUE/f'jobs/{name}/attempts/1/out/fit.json') for name in
        ('focus348-00-control','focus355-position-train','focus355-position-branch-train')]
    save('hcf358-duration-review','Test whether retained training loss supports more epochs.',
        'Require improving loss and an unresolved useful target before proposing continuation. Preserve prior regressions.',
        dict(mode='convergence',reports=fits,inputs=fits))
    reports=[pin(q.QUEUE/f'jobs/focus356-{factor}-branches/attempts/1/out/branches.json')
        for factor in ('size','growth','shadow','position','background')]
    save('hcf358-native-score-overlap','Test whether each retained scalar separates native movement from content changes.',
        'If both scalar ranges overlap, prioritize new evidence or representations instead of a scalar threshold adjustment.',
        dict(mode='separation',reports=reports,inputs=reports))
    sizes=[dict(**p,bytes=(q.ROOT/p['path']).stat().st_size) for p in all_images]
    save('hcf358-corpus-capacity','Estimate paired corpus storage from retained full-resolution PNG sizes.',
        'Stop stage preparation when estimated image bytes alone exceed the study ceiling. Do not reserve unmeasured capacity.',
        dict(mode='storage',images=sizes,inputs=all_images))
    stages=[
        ('visible-family','Qualify one matched Standard/HCF control family.',
         'peer-host-TTR: Standard counterpart for retained artwork, or matched native family with a visible HCF difference.'),
        ('producer-offload','Qualify shard closure and verified offload before 70% of producer quota.',
         'research-host-NUIAK and TTR: exact producer API, target ownership, restoration, mid-route quota test, and USB reservation.'),
        ('group-freeze','Freeze scene ancestry and training, development, calibration, and audit roles.',
         'research-host-NUIAK: qualified family, capture recipes, connected artwork ancestry, and at least 30 development and 30 audit groups.'),
        ('resume','Test interrupted training against uninterrupted training for both trainers.',
         'research-host-NUIAK: implement full optimizer, scheduler, random, epoch and data-order state in resident trainers.'),
        ('worker-capacity','Qualify worker-host-NUIAK local staging and measured throughput.',
         'worker-host-NUIAK: named disk reservation, environment versions, GPU memory, exact staged input hashes, and a bounded throughput return.'),
        ('baselines','Compare pinned rules and NUIAK on identical eligible membership.',
         'research-host-NUIAK: qualified shard, fixed proposals, pinned rules/models, and measured focus truth.'),
    ]
    for name,hypothesis,requirement in stages:
        save('hcf358-plan-'+name,hypothesis,'Return named evidence. Missing evidence remains blocked, not a successful experiment.',
            requirements=[requirement,'research-host-NUIAK: tested executable successor with immutable named inputs and output checks.'])
    for count in (1000,5000,20000,50000):
        save(f'hcf358-plan-generate-{count}',f'Generate and validate {count} accepted HCF frames with matched Standard comparisons.',
            'Count independent groups and verify all labels. Expand only when the prior stage supports a useful gain.',
            requirements=['research-host-NUIAK: visible-family, producer-offload, group-freeze, and stage-specific storage reservation.',
                'research-host-NUIAK: prior-stage decision and executable producer with exact recipes, seeds, shard limits, and approved target.'])
        for model in ('detector','classifier'):
            save(f'hcf358-plan-{model}-{count}',f'Test {model} learning at {count} accepted HCF frames.',
                'Compare equal eligible membership. Require target gains without increased wrong selections or lost retained successes.',
                requirements=[f'research-host-NUIAK: validated {count}-frame stage, fixed initialization and preprocessing, and complete paired comparison jobs.',
                    'worker-host-NUIAK: qualified storage, full resume, remaining 48 GPU-hour allocation, and immutable training successor.',
                    'Run budget: at most 100 epochs and 4 GPU-hours; patience 10 on development loss; no automatic retry.'])
    for name,hypothesis,requirement in (
        ('seed-repeats','Test 3 total seeds for selected useful configurations.','Selected development improvement and remaining 12 GPU-hour repeat allocation.'),
        ('final-audit','Test frozen candidates once on reserved audit groups.','Frozen models, thresholds, untouched audit membership, and passed retained-success comparisons.'),
        ('coreml','Test Apple conversion, preprocessing, decisions, and latency.','Qualified candidate checkpoint and resident Apple export/runtime lane.'),
        ('shadow','Deliver optional candidates and case-linked findings to TTR.','Verified package, optional shadow contract, and no navigation authority.')):
        save('hcf358-plan-'+name,hypothesis,'Retain complete comparisons and explicit unavailable metrics.',
            requirements=['research-host-NUIAK: '+requirement,'research-host-NUIAK: tested immutable executable successor.'])
    receipt=q.ROOT/'reports/work/HCF358';receipt.mkdir(exist_ok=True)
    q.save(receipt/'registered.json',dict(ready=[s['id'] for s in specs if not s.get('requirements')],
        blocked=[s['id'] for s in specs if s.get('requirements')],
        additions=[dict(id=s['id'],sha256=q.text_digest(s)) for s in specs]))


if __name__=='__main__':register()
