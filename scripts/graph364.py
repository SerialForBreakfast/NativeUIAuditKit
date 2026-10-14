"""Generate matched interruption scenes and compare pinned transition models."""
import os
import re
import shutil
import subprocess
import time
import research_queue as q
from research_campaign340 import pin

OUT = None
VARIANTS = {'base': [], 'dim': ['--scrim', '0.35'],
            'banner': ['--overlay', 'apns_banner'], 'toast': ['--overlay', 'hud_toast']}


def config():
    value = q.load(OUT / 'config.json')
    for ref in value['inputs']:
        q.require(q.digest(q.local_path(q.ROOT, ref['path'])) == ref['sha256'], 'input_changed')
    return value


def dependency(name):
    matches = [ref for dep in q.load(OUT / 'dependencies.json') for ref in dep['outputs']
               if ref['path'].endswith('/' + name)]
    q.require(len(matches) == 1, 'dependency_ambiguous:' + name)
    ref = matches[0]
    path = q.local_path(q.ROOT, ref['path'])
    q.require(q.digest(path) == ref['sha256'], 'dependency_changed')
    return path


def build():
    cfg = config()
    cache = q.ROOT / '.build/graph364-module-cache'
    cache.mkdir(exist_ok=True)
    command = ['swiftc', '-module-cache-path', str(cache), str(q.ROOT / cfg['source']['path']),
               '-o', str(OUT / 'renderer')]
    with (OUT / 'build.log').open('x') as log:
        subprocess.run(command, cwd=q.ROOT, env=dict(os.environ, TMPDIR=str(q.ROOT / '.build')),
                       stdout=log, stderr=subprocess.STDOUT, check=True, timeout=700)
    q.save(OUT / 'build.json', dict(source=cfg['source'], binary=pin(OUT / 'renderer')))


def make_rows(states, layout, group):
    rows = []
    def add(a, b, changed, condition):
        rows.append(dict(id=f'{group}-{layout}-{len(rows):03d}', images=[a, b], changed=changed,
                         condition=condition, layout=layout, group=group, role='development', ancestryRole='train'))
    for variant, frames in states.items():
        add(frames[0], frames[1], 1, variant + '-movement')
        add(frames[1], frames[0], 1, variant + '-movement')
        for target in range(2):
            add(frames[target], frames[target], 0, variant + '-identical')
            if variant != 'base':
                add(states['base'][target], frames[target], 0, variant + '-appearance')
                add(frames[target], states['base'][target], 0, variant + '-appearance')
    return rows


def produce():
    cfg = config(); started = time.monotonic()
    binary = dependency('renderer')
    import authored319
    frames, rows = [], []
    names = sorted(set(re.findall(r'"([^"/]+\.jpg)"', (q.ROOT / cfg['source']['path']).read_text())))
    q.require(len(names) == 16, 'artwork_contract_changed')
    for family in cfg['families']:
        asset_dir = OUT / ('assets-' + family['id']); asset_dir.mkdir()
        for index, name in enumerate(names):
            shutil.copyfile(q.ROOT / family['assets'][index % 2]['image']['path'], asset_dir / name)
        states = {}
        for variant, flags in VARIANTS.items():
            states[variant] = []
            for index, target in enumerate(cfg['layout']['targets']):
                folder = OUT / f'{family["id"]}-{variant}-{index}'
                command = [str(binary), '--layout', cfg['layout']['name'], '--resolution', '1080p',
                           '--assets-dir', str(asset_dir), '--output-dir', str(folder), '--focus-id', target] + flags
                with (OUT / (folder.name + '.log')).open('x') as log:
                    subprocess.run(command, cwd=q.ROOT, env=dict(os.environ, TMPDIR=str(q.ROOT / '.build')),
                                   stdout=log, stderr=subprocess.STDOUT, check=True, timeout=60)
                image, annotation = authored319.frame(folder, cfg['layout']['name'], target)
                states[variant].append(image)
                frames.append(dict(family=family['id'], variant=variant, target=target, image=image,
                                   annotation=pin(folder / (cfg['layout']['name'] + '_annotations.json'))))
                q.require(q.live_output_bytes(OUT) < 95_000_000, 'producer_output_limit')
                print(f'Rendered {len(frames)}/{len(cfg["families"])*8} states', flush=True)
            q.require(states[variant][0]['sha256'] != states[variant][1]['sha256'], 'invisible_movement')
        for variant in ('dim', 'banner', 'toast'):
            q.require(all(states[variant][i]['sha256'] != states['base'][i]['sha256'] for i in range(2)),
                      'ineffective_variant:' + variant)
        rows.extend(make_rows(states, cfg['layout']['name'], family['id']))
    # The target geometry must remain fixed across appearance variants.
    for family in cfg['families']:
        for target in cfg['layout']['targets']:
            annotations = [q.load(q.ROOT / f['annotation']['path']) for f in frames
                           if f['family'] == family['id'] and f['target'] == target]
            geometry = [[(n['id'], n['unfocusedBounds'], n['focusedBounds']) for n in a['nodes']] for a in annotations]
            q.require(all(g == geometry[0] for g in geometry), 'variant_geometry_changed')
    q.save(OUT / 'corpus.json', dict(version='graph364-corpus-v1', sourceDomain='authored-headless',
        role='development', trainingEligible=False, rows=rows, frames=frames, renderer=pin(binary),
        seconds=time.monotonic()-started, independentGroups=len(cfg['families']),
        limitations=['Authored focus identity is not an OS observation.',
                    'Notifications do not take focus in this authored scene. Native behavior may differ.',
                    'Related artwork and reversed pairs remain in the same group.',
                    'Only the renderer appearance is tested. Other themes remain unsupported.']))
    q.save(OUT / 'qualification.json', dict(version='research-condition-v1', outcome='supported',
        reason='The authored controls keep their geometry and identity while appearance changes.',
        evidence=[pin(OUT / 'corpus.json')]))


def score():
    cfg = config(); corpus = dependency('corpus.json'); doc = q.load(corpus)
    q.require(doc['sourceDomain'] == 'authored-headless' and doc['trainingEligible'] is False, 'corpus_role')
    rows = doc['rows']
    for row in rows:
        for ref in row['images']:
            q.require(q.digest(q.ROOT / ref['path']) == ref['sha256'], 'frame_changed')
    import report_additive341 as report
    from diagnostics343 import counts
    report.a.t.set_num_threads(2)
    scores = {}; baseline = None
    for name, ref in cfg['models'].items():
        timing = dict(preprocessingSeconds=0., inferenceSeconds=0., examples=0)
        values = report.score_rows(report.a.e.load_candidate(q.ROOT / ref['path']), rows, False, timing)
        scores[name] = dict(model=ref, probabilities=values.tolist(), counts=counts(rows, values, baseline), timing=timing)
        if baseline is None:
            baseline = values
    q.save(OUT / 'diagnostic.json', dict(version='graph364-comparison-v1', corpus=pin(corpus), rows=rows,
        scores=scores, thresholds=[.15, .85], modelAccepted=False, trainingEligible=False,
        independentGroups=doc['independentGroups'], limitations=doc['limitations'],
        decision='Use paired losses and gains to select the next data correction. Do not promote from this diagnostic.'))


def native_status():
    cfg = config()
    q.save(OUT / 'qualification.json', dict(version='research-condition-v1', outcome='inconclusive',
        reason='The retained native attempt fails observation checks. Native capture needs verified restoration and a corrected TTR build.',
        evidence=cfg['inputs'], modelAccepted=False))


def summarize():
    config(); deps = q.load(OUT / 'dependencies.json'); comparisons = []; native = None
    for dep in deps:
        for ref in dep['outputs']:
            doc = q.load(q.ROOT / ref['path'])
            if doc.get('version') == 'graph364-comparison-v1':
                comparisons.append((ref, doc))
            elif doc.get('version') == 'research-condition-v1':
                native = doc
    q.require(len(comparisons) == 4 and native is not None, 'incomplete_graph')
    totals = {}; failures = []
    from research_campaign340 import decision
    for ref, doc in comparisons:
        for name, result in doc['scores'].items():
            summary = totals.setdefault(name, dict(count=0, correct=0, falseChange=0, missedChange=0,
                                                   abstentions=0, lost=0, gained=0))
            for count in result['counts'].values():
                for key in summary:
                    summary[key] += count[key]
            for row, probability in zip(doc['rows'], result['probabilities']):
                if decision(probability) != row['changed']:
                    failures.append(dict(model=name, case=row['id'], group=row['group'], condition=row['condition'],
                                         label=row['changed'], probability=probability, evidence=ref))
    q.save(OUT / 'decision.json', dict(version='graph364-decision-v1', evidence=[r for r, _ in comparisons],
        totals=totals, failures=failures, nativeQualification=native, modelAccepted=False, productionChanged=False,
        nextAction='Target conditions with false changes only if matched movement remains correct. Qualify native transfer before training admission.',
        independentGroups=len({r['group'] for _, d in comparisons for r in d['rows']}),
        coverage=dict(layouts=4, themes=['renderer-default'], unsupportedThemes=['other appearances'], nativeHCF=0),
        limitation='This batch tests existing models. It does not train a candidate or replace the full retained regression suite.'))


def register():
    import authored319
    import research_graph
    folder = q.ROOT / 'Research/ResearchSpecs/FOCUS364'
    q.require(not folder.exists(), 'revision_exists')
    folder.mkdir()
    snapshot = q.ROOT / 'reports/work/FOCUS364'; snapshot.mkdir(exist_ok=True)
    source = snapshot / 'render-headless-screen.swift'
    shutil.copyfile(authored319.SCRIPT, source)
    plan = authored319.plan()
    families = [dict(id='artwork-s'+str(i), assets=[a for a in plan['assets'] if f'-s{i}-' in a['id']]) for i in (0, 1)]
    code = [pin(q.ROOT / 'scripts' / name) for name in ('graph364.py', 'research_graph.py', 'authored319.py',
            'report_additive341.py', 'additive341.py', 'diagnostics343.py', 'edge329.py', 'regions313.py')]
    models = {'FOCUS329': pin(q.ROOT / 'reports/work/FOCUS-329/run/last.pt'),
              'gamma348': pin(q.QUEUE / 'jobs/focus348-00-gamma/attempts/1/out/last.pt'),
              'movement349': pin(q.QUEUE / 'jobs/focus349-00-gamma/attempts/1/out/last.pt')}
    nodes = []; specs = {}
    def add(suffix, kind, question, answer, step, extra=None, deps=None, conditions=None):
        ident = 'focus364-' + suffix
        cfg = dict(inputs=code, **(extra or {}))
        cfg['inputs'] = code + cfg.get('pins', [])
        cp = folder / (ident + '-config.json'); q.save(cp, cfg)
        spec = dict(version=q.SPEC_VERSION, id=ident, task='FOCUS364', owner='research-host-NUIAK', kind='screen',
            authority='diagnostic', hypothesis=question, decisionRule=answer, inputs=cfg['inputs'],
            stage=[{'from': pin(cp), 'to': 'config.json'}], dependencies=deps or [], conditions=conditions or [],
            adapter=dict(type='python-callable', steps=['graph364.'+step], outputAttributes=['graph364.OUT']),
            limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1))
        sp = folder / (ident+'.json'); q.save(sp, spec); q.submit(sp); specs[ident] = spec
        nodes.append(dict(job=ident, specSHA256=q.text_digest(spec), question=question, kind=kind))
        return ident
    def dep(ident, outputs):
        return dict(job=ident, specSHA256=q.text_digest(specs[ident]), outputs=outputs)
    build_id = add('00-renderer', 'producer', 'Can the pinned TTR renderer build without the Simulator?',
        'Use this exact binary for every scene in the batch.', 'build', dict(source=pin(source), pins=[pin(source)]))
    comparisons = []
    for index, layout in enumerate(plan['layouts']):
        producer = add(f'1{index}-{layout["name"]}', 'producer',
            f'Does {layout["name"]} keep focus geometry fixed across dimming and notifications?',
            'Accept authored comparison inputs only when hashes, geometry, and effective changes pass.', 'produce',
            dict(source=pin(source), layout=layout, families=families,
                 pins=[pin(source)]+[a['image'] for f in families for a in f['assets']]), [dep(build_id, ['renderer'])])
        comparison = add(f'2{index}-{layout["name"]}', 'experiment',
            f'Do dimming and notifications cause false changes or missed movement in {layout["name"]}?',
            'Compare fixed models on matched cases. Count gains and lost successes without changing crops or thresholds.',
            'score', dict(models=models, pins=list(models.values())), [dep(producer, ['corpus.json', 'qualification.json'])],
            [dict(job=producer, output='qualification.json', outcome='supported')])
        comparisons.append(dep(comparison, ['diagnostic.json']))
    native_result = q.QUEUE / 'jobs/hcf362-large-dark-capture/attempts/1/result.json'
    native_id = add('05-native-evidence', 'qualification', 'Does the retained native HCF attempt support further capture?',
        'Keep native HCF generation blocked while restoration and observation checks remain unresolved.', 'native_status',
        dict(pins=[pin(native_result)]))
    add('90-decision', 'decision', 'Which appearance failures justify the next correction without losing movement?',
        'Return case-linked failures, paired counts, coverage limits, and the next data decision. Do not accept a model.',
        'summarize', deps=comparisons+[dep(native_id, ['qualification.json'])])
    graph = dict(version='research-graph-v1', id='FOCUS364-r1', nodes=nodes)
    graph['budget'] = research_graph.validate_graph(graph)
    q.save(folder / 'graph.json', graph)
    print(graph['budget'])


if __name__ == '__main__':
    register()
