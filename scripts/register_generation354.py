"""Freeze matched native capture jobs and their existing queue consumers."""
import argparse
import copy
import dataset351
import research_queue as q
from research_campaign340 import pin


def cases(original, factor):
    base = next(c for c in dataset351.recipes(original) if c['id'] == 'corners-growth')
    result = []
    values = dict(size=(80, 160), growth=(1.03, 1.15), shadow=(0, .4),
                  position=('corners', 'center'), background=(0x181818, 0xCCCCCC))
    for index, value in enumerate(values[factor]):
        case = copy.deepcopy(base)
        case.update(id=f'{factor}-{index}', factor=factor, value=value,
                    sourceFocus='item-2', targetFocus='item-3')
        comp = case['recipe']['appearance']['composition']
        for definition in comp['definitions'].values():
            definition['width'] = definition['height'] = 160
        style = comp['styles']['image']
        if factor == 'size':
            for definition in comp['definitions'].values():
                definition['width'] = definition['height'] = value
        elif factor == 'growth':
            style['focus']['custom']['scale'] = value
        elif factor == 'shadow':
            style['focus']['custom']['shadowOpacity'] = value
        elif factor == 'position' and value == 'center':
            for region, xy in zip(comp['regions'], ((550,250),(1050,250),(550,650),(1050,650))):
                region['frame'][:2] = xy
        elif factor == 'background':
            style['background'] = value
        result.append(case)
    return result


def register(factors):
    folder = q.ROOT/'Research/ResearchSpecs/GENERATION354'
    folder.mkdir(exist_ok=True)
    plan = dataset351.run(None)
    refs = [pin(q.ROOT/'scripts'/name) for name in (
        'generation352.py','dataset351.py','compare351.py','native343.py',
        'direct_tvos_capture.py','fixture_rendered_body.py','focus_batch_harness.py',
        'report_additive341.py','diagnostics343.py','regions313.py','edge329.py')]
    models = q.load(q.ROOT/'Research/ResearchSpecs/DATASET351/dataset351-00-movement-config.json')['models']
    for factor in factors:
        ident = f'generation354b-{factor}-capture'
        q.require(not (q.QUEUE/'jobs'/ident).exists(), 'already_registered:'+ident)
        frozen = copy.deepcopy(plan)
        frozen.update(cases=cases(plan['original']['scene']['recipe'],factor), expectedFrames=10,
            reloadPolicy='observe-before-focus-v1', group='fixture351-related-scenes')
        pp=folder/(factor+'-plan-b.json'); q.save(pp,frozen)
        producer=dict(version=q.SPEC_VERSION,id=ident,task='GENERATION354',owner='research-host-NUIAK',
            kind='screen',authority='capture',
            hypothesis=f'Change only {factor} across matched scenes to measure focus movement and content confusion.',
            decisionRule='Require 10 retained frames, 6 verified endpoint pairs, and successful scene restoration. Preserve failures.',
            inputs=refs,capture=dict(target=frozen['binding']['simulatorUDID'],endpoint=frozen['binding']['endpoint'],
                plan=pin(pp),approval='User approves queued controlled Fixture generation on the exact Simulator.'),
            adapter=dict(type='python-callable',steps=['generation352.run'],outputAttributes=['generation352.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        sp=folder/(ident+'.json');q.save(sp,producer);print(ident,q.submit(sp))
        for mode in ('movement','content','recapture','timing'):
            spec=copy.deepcopy(producer);spec.pop('capture')
            spec.update(id=f'generation354b-{factor}-{mode}',authority='diagnostic',
                hypothesis=f'Measure {mode} for both {factor} values with unchanged models and crops.',
                decisionRule='Report both cases and all model scores. No threshold selection or training admission.',
                dependencies=[dict(job=ident,specSHA256=q.text_digest(producer),outputs=['capture/capture.json'])],
                adapter=dict(type='python-callable',steps=['generation352.compare'],outputAttributes=['generation352.OUT']))
            cp=folder/(spec['id']+'-config.json');q.save(cp,dict(mode=mode,models=models))
            spec['inputs'] += list(models.values())
            spec['stage']=[{'from':pin(cp),'to':'comparison.json'}]
            sp=folder/(spec['id']+'.json');q.save(sp,spec);print(spec['id'],q.submit(sp))


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('factors',nargs='+',choices=['size','growth','shadow','position','background'])
    register(p.parse_args().factors)
