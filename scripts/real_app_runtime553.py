"""MEASURE553: connect retained TTR `visual replay` exports to the REAL543 benchmark and gate candidates.

Reads retained exports only. It does not launch TTR, capture, train, tune, or accept a model.
A partial provider result stays an abstention. Unavailable runtime fields stay unavailable.
"""
import argparse
from collections import defaultdict
import hashlib
from pathlib import Path
import random
import statistics
import research_queue as q
from experiment_templates import pin
import real_app_benchmark543 as b

DESCRIPTOR = 'runtime-identity-descriptor-v1'
RUNTIME = 'real-app-runtime-v1'
PREDICTIONS = 'real-app-runtime-predictions-v1'
GATE = 'real-app-promotion-gate-v1'
LATENCY_SCOPE = 'request-to-result-durable'
GOOD = {'correct', 'correct-abstention'}


def require(value, reason):
    q.require(value, 'measure553_' + reason)


def hex_digest(value):
    """Return the hex part of `compiled-tree-sha256-v1:<hex>` or a plain hex digest."""
    text = value.split(':', 1)[1] if isinstance(value, str) and value.startswith('compiled-tree-sha256-v1:') else value
    require(isinstance(text, str) and len(text) == 64 and all(c in '0123456789abcdef' for c in text), 'digest_format')
    return text


def observed(root):
    """Read 1 replay export after the REAL543 integrity checks. Return its observed runtime fields."""
    root = Path(root)
    result = q.load(root/'result.json')
    provider = result['receipt']['provider']
    runtime = result.get('runtime_provenance') or {}
    focus = provider.get('focus_execution') or {}
    require(focus.get('model_digest_algorithm') == runtime.get('focus_digest_algorithm') == 'compiled-tree-sha256-v1', 'focus_algorithm')
    revision = runtime.get('source_revision')
    require(revision and revision == (result.get('ttr_observed') or {}).get('source_revision'), 'source_revision')
    return dict(detector=hex_digest(provider['detector_artifact_digest']), focus=hex_digest(focus['model_digest']),
                preprocessing=runtime.get('preprocessing_identity'), taxonomy=runtime.get('taxonomy_identity'),
                revision=revision, revisionScope=runtime.get('source_revision_scope'),
                unavailable=sorted(result.get('unavailable_provenance', [])), result=pin(root/'result.json'))


def descriptor(ref, kind):
    doc = b.read(ref)
    require(doc.get('version') == DESCRIPTOR and doc.get('kind') == kind and doc.get('identity'), 'descriptor_' + kind)
    return doc['identity']


def audited(root, audits):
    """Run the REAL543 export audit into a new receipt, then return the observed fields."""
    out = Path(audits)/(Path(root).name + '.json')
    b.audit_replay(root, out)
    return observed(root)


def runtime_receipt(request, out):
    """Write `real-app-runtime-v1` only when every replay observes the pinned models and identities."""
    r = q.load(request)
    require(r['replays'], 'replays')
    expected = dict(detector=b.model_identity(r['detector'])[0], focus=b.model_identity(r['focus'])[0],
                    preprocessing=descriptor(r['preprocessing'], 'preprocessing'), taxonomy=descriptor(r['taxonomy'], 'taxonomy'))
    audits = Path(out).with_name(Path(out).stem + '-audits')
    rows = [audited(q.ROOT/path, audits) for path in r['replays']]
    for row in rows:
        for key, value in expected.items():
            require(row[key] == value, 'observed_' + key)
    revisions = {row['revision'] for row in rows}
    require(len(revisions) == 1, 'mixed_revisions')
    revision = revisions.pop()
    require(len(revision) == 40 and all(c in '0123456789abcdef' for c in revision), 'revision_format')
    receipt = dict(version=RUNTIME, observedLoaded=True, inputMode='screenshots-only', ttrRevision=revision,
                   detectorSHA256=expected['detector'], focusSHA256=expected['focus'],
                   preprocessingSHA256=r['preprocessing']['sha256'], taxonomySHA256=r['taxonomy']['sha256'],
                   revisionScope=sorted({row['revisionScope'] for row in rows}),
                   unavailableProvenance=sorted({u for row in rows for u in row['unavailable']}),
                   evidence=[row['result'] for row in rows], request=pin(request), adapter=pin(Path(__file__)),
                   limitation='Observed session contract, not raw tensor capture. Crop identity is reported only when observed.')
    b.save_new(out, receipt)
    return receipt


def case_prediction(root, case, configuration, receipt, class_map, classes):
    root = Path(root)
    completion = q.load(root/'completion.json')
    result = q.load(root/'result.json')
    require(pin(root/'result.json') in receipt['evidence'], 'replay_not_in_runtime_receipt')
    seen = observed(root)
    require(seen['detector'] == receipt['detectorSHA256'] and seen['focus'] == receipt['focusSHA256'] and
            seen['revision'] == receipt['ttrRevision'], 'replay_runtime_identity')
    require(completion['source_sha256'] == case['image']['sha256'], 'replay_image')
    from PIL import Image
    with Image.open(root/'source.png') as image:
        pixels = hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()
    elements = result['receipt']['provider'].get('elements', [])
    detections = []
    for e in elements:
        name = class_map.get(e['role'], e['role'])
        require(name in classes, 'unmapped_runtime_class:' + e['role'])
        detections.append({'class': name, 'box': list(e['pixels']), 'score': e['confidence']})
    selected = result['predictionSelection'].get('id')
    focus = None
    if selected is not None:
        match = [e for e in elements if e['id'] == selected]
        require(len(match) == 1, 'selection_identity')
        focus = list(match[0]['pixels'])
    return dict(id=case['id'], status='ok', imageSHA256=completion['source_sha256'], pixelSHA256=pixels,
                baselineSHA256=q.text_digest(configuration), runtimeReceipt=configuration['runtimeReceipt'],
                latencyMs=completion['request_to_result_durable_ms'], latencyScope=LATENCY_SCOPE,
                detections=detections, focusBox=focus, selectionStatus=result['predictionSelection'].get('status'),
                replay=pin(root/'result.json'))


def predictions(request, out):
    """Convert audited replays for every captured freeze case. Failed cases need a stated error."""
    r = q.load(request)
    frozen = b.read(r['freeze'])
    require(frozen['version'] == 'real-app-freeze-v1', 'freeze')
    manifest = b.validate(b.read(frozen['manifest']))
    configurations = {q.text_digest(c): c for c in [manifest['baseline'], *manifest.get('candidates', [])]}
    require(r['configuration'] in configurations, 'undeclared_configuration')
    configuration = configurations[r['configuration']]
    receipt = b.read(configuration['runtimeReceipt'])
    require(receipt.get('version') == RUNTIME and receipt.get('evidence'), 'runtime_receipt')
    replays, failed = r.get('replays', {}), r.get('failed', {})
    class_map = r.get('classMap', {})
    captured = [c for c in manifest['cases'] if c['status'] == 'captured']
    require(set(replays) | set(failed) == {c['id'] for c in captured} and not set(replays) & set(failed), 'case_coverage')
    audits = Path(out).with_name(Path(out).stem + '-audits')
    cases = []
    for c in captured:
        if c['id'] in failed:
            require(isinstance(failed[c['id']], str) and failed[c['id']].strip(), 'failure_reason')
            cases.append(dict(id=c['id'], status='failed', error=failed[c['id']], imageSHA256=c['image']['sha256'],
                              pixelSHA256=c['pixelSHA256'], baselineSHA256=r['configuration'],
                              runtimeReceipt=configuration['runtimeReceipt'], latencyMs=None, detections=[], focusBox=None))
            continue
        root = q.ROOT/replays[c['id']]
        b.audit_replay(root, audits/(c['id'] + '.json'))
        cases.append(case_prediction(root, c, configuration, receipt, class_map, manifest['classes']))
    doc = dict(version=PREDICTIONS, freeze=r['freeze'], inputMode='screenshots-only', baselineSHA256=r['configuration'],
               cases=cases, partialResults=sum(c.get('selectionStatus') == 'partial_provider_result' for c in cases),
               unavailableProvenance=receipt.get('unavailableProvenance', []), adapter=pin(Path(__file__)), modelAccepted=False)
    b.save_new(out, doc)
    return doc


def _flows(rows):
    grouped = defaultdict(lambda: defaultdict(list))
    for row in rows:
        grouped[row['app']][row['flow']].append(row['id'])
    return {app: list(flows.values()) for app, flows in grouped.items()}


def _metrics(rows):
    """Equal-application focus rate and pooled detection recall for 1 sample of rows."""
    rates = []
    for app in sorted({r['app'] for r in rows}):
        known = [r for r in rows if r['app'] == app and r.get('focusState', 'unknown') != 'unknown']
        if known:
            rates.append(sum(r.get('focusOutcome') in GOOD for r in known) / len(known))
    truth = sum(len(r.get('objects', [])) for r in rows)
    found = sum(len(r.get('detected', [])) for r in rows)
    return dict(focus=sum(rates) / len(rates) if rates else None, recall=found / truth if truth else None)


def paired_bootstrap(left, right, samples=2000, seed=553):
    """Resample whole flows within apps. Both reports use the same draw, so the interval describes the difference."""
    a = {r['id']: r for r in left['rows'] if 'focusOutcome' in r}
    c = {r['id']: r for r in right['rows'] if 'focusOutcome' in r}
    require(a.keys() == c.keys(), 'paired_cases')
    flows = _flows(a.values())
    rng = random.Random(seed)
    draws = defaultdict(list)
    for _ in range(samples):
        ids = [i for app in sorted(flows) for flow in rng.choices(flows[app], k=len(flows[app])) for i in flow]
        x, y = _metrics([a[i] for i in ids]), _metrics([c[i] for i in ids])
        for key in ('focus', 'recall'):
            if x[key] is not None and y[key] is not None:
                draws[key].append(y[key] - x[key])
    point = {key: (lambda x, y: None if x is None or y is None else y - x)(_metrics(list(a.values()))[key], _metrics(list(c.values()))[key])
             for key in ('focus', 'recall')}
    out = {}
    for key in ('focus', 'recall'):
        values = sorted(draws[key])
        out[key] = dict(difference=point[key], interval95=[values[int(.025 * len(values))], values[min(len(values) - 1, int(.975 * len(values)))]]
                        if values else None, samples=len(values))
    return dict(method='paired whole-flow bootstrap within apps', seed=seed, metrics=out)


def _latency(report):
    values = [r['measuredLatencyMs'] for r in report['rows'] if r.get('measuredLatencyMs') is not None]
    scopes = {r.get('latencyScope') for r in report['rows'] if r.get('measuredLatencyMs') is not None}
    return (statistics.median(values) if values else None), scopes


def _retention(ref):
    if ref is None:
        return None
    doc = b.read(ref)
    for key in ('lostPriorSuccesses', 'lostRawSuccesses', 'lostSuccesses'):
        if key in doc:
            value = doc[key]
            return len(value) if isinstance(value, list) else int(value)
    require(False, 'retention_fields')


def gate(request, out):
    """Decide whether a candidate passes the MEASURE553 gate. The gate never accepts a model."""
    r = q.load(request)
    left, right = b.read(r['baselineReport']), b.read(r['candidateReport'])
    require(left['freeze'] == right['freeze'] and left['baselineSHA256'] != right['baselineSHA256'], 'gate_membership')
    ratio = r.get('latencyRatio', 1.1)
    require(type(ratio) in (int, float) and 1 <= ratio <= 2, 'latency_ratio')
    changes = b.compare(left, right)
    paired = paired_bootstrap(left, right)
    lost_retention = _retention(r.get('retentionReport'))
    (base_ms, base_scopes), (cand_ms, cand_scopes) = _latency(left), _latency(right)
    latency_ok = base_ms is not None and cand_ms is not None and base_scopes == cand_scopes and cand_ms <= ratio * base_ms
    improved = [k for k, v in paired['metrics'].items() if v['interval95'] and v['interval95'][0] > 0]
    checks = dict(noLostFocus=not changes['lost'], noLostControls=not changes['lostControls'], noNewWrong=not changes['newWrong'],
                  retentionPreserved=lost_retention == 0, improvementBeyondInterval=bool(improved), latencyWithinLimit=latency_ok)
    reasons = [name for name, passed in checks.items() if not passed]
    if lost_retention is None:
        reasons.append('retention report missing')
    doc = dict(version=GATE, baselineReport=r['baselineReport'], candidateReport=r['candidateReport'],
               retentionReport=r.get('retentionReport'), latencyRatio=ratio, checks=checks, failedChecks=reasons,
               gatePassed=not reasons, improvedMetrics=improved, paired=paired, changes=changes,
               latencyMs=dict(baseline=base_ms, candidate=cand_ms, scopes=sorted(s for s in base_scopes | cand_scopes if s)),
               lostRetentionSuccesses=lost_retention, adapter=pin(Path(__file__)), modelAccepted=False,
               limitation='Passing the gate permits a promotion request. Promotion keeps its separate authority.')
    b.save_new(out, doc)
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['runtime-receipt', 'predictions', 'gate'])
    parser.add_argument('request', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    dict(**{'runtime-receipt': runtime_receipt, 'predictions': predictions, 'gate': gate})[args.command](args.request, args.output)


if __name__ == '__main__':
    main()
