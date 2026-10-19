"""Admit a frozen capture batch after verified recovery. Never execute captures."""
import copy
from pathlib import Path

import research_queue as q
import research_approval as approval
import hcf_templates395 as templates
from experiment_templates import checked, pin
from hcf_recovery367 import valid_result
import native343
import native_coverage402

OUT = None
OUTPUTS = ['recovery.json', 'qualification/qualification.json', 'fixture-before.json',
           'fixture-after.json', 'previous-marker.json', 'capture-evidence.json', 'restored-fixture.png']


def retain(path, value):
    """Resume an identical publication without overwriting an earlier record."""
    if path.exists():
        q.require(q.load(path) == value, 'gate_publication_conflict:' + path.name)
    else:
        q.save(path, value)


def verify_recovery(spec, queue, plan):
    resolved = q.dependency_inputs(spec, queue)
    q.require(len(resolved) == 1, 'gate_dependency_count')
    dep = resolved[0]
    q.require(dep['job'] == plan['recovery']['job'] and
              dep['specSHA256'] == plan['recovery']['specSHA256'], 'gate_recovery_identity')
    refs = dict(zip(OUTPUTS, dep['outputs']))
    q.require(len(refs) == len(OUTPUTS), 'gate_recovery_outputs')
    paths = {name: checked(ref) for name, ref in refs.items()}
    receipt = q.load(paths['recovery.json'])
    recovery_spec = q.load(queue/'jobs'/dep['job']/'spec.json')
    recovery_plan = q.load(checked(recovery_spec['capture']['plan']))
    q.require(recovery_plan['version'] == 'native-capture-recovery-v2', 'gate_recovery_version')
    q.require(receipt.get('complete') is True and receipt.get('trainingEligible') is False and
              receipt.get('target') == recovery_spec['capture']['target'], 'gate_recovery_incomplete')
    for key, name in [('qualification', 'qualification/qualification.json'),
                      ('fixture', 'fixture-after.json'), ('previousMarker', 'previous-marker.json')]:
        q.require(receipt[key] == refs[name], 'gate_receipt_binding:' + key)
    qualification = q.load(paths['qualification/qualification.json'])
    valid_result(qualification)
    q.require(bool(qualification['postflight']['ownership']), 'gate_ownership_missing')
    before, after = (q.load(paths[name]) for name in ('fixture-before.json', 'fixture-after.json'))
    native343.signature(after, before, before['scene']['focused_element_id'])
    q.require(after['device']['simulator_udid'] == receipt['target'], 'gate_fixture_target')
    q.require(q.digest(paths['previous-marker.json']) == recovery_plan['markerSHA256'] and
              q.load(paths['previous-marker.json'])['job'] == recovery_plan['failedJob'], 'gate_old_marker')
    capture = q.load(paths['capture-evidence.json'])
    q.require(capture.get('version') == 'research-capture-evidence-v1' and capture.get('cleanup') is True and
              capture.get('images') == [dict(path='restored-fixture.png', sha256=refs['restored-fixture.png']['sha256'])],
              'gate_capture_evidence')
    from PIL import Image
    with Image.open(paths['restored-fixture.png']) as image:
        image.verify()
    return recovery_plan, [dep['result'], *refs.values(), recovery_spec['capture']['plan']]


def prepare(spec, queue, plan, output):
    q.require(plan.get('version') == 'recovery-capture-admission-v1', 'gate_plan_version')
    q.require(set(plan) == {'version', 'recovery', 'captures', 'staging'}, 'gate_plan_fields')
    entries = plan['captures']
    q.require(len(entries) == 6 and len({e['id'] for e in entries}) == 6, 'gate_capture_count')
    q.require(all(set(e) == {'id', 'draft'} and q.ID.fullmatch(e['id']) for e in entries), 'gate_capture_fields')
    recovery, evidence = verify_recovery(spec, queue, plan)
    checked(plan['staging'])
    q.require(plan['staging'] == recovery['staging'], 'gate_staging_changed')
    gate = dict(version='research-condition-v1', outcome='supported',
                reason='Pinned recovery verifies Standard, Fixture, closed ownership, and screenshot readback.', evidence=evidence)
    # Compile every child before any registration. Only qualification fields change.
    children = []
    shards = set()
    for entry in entries:
        draft = q.load(checked(entry['draft']))
        q.require(draft['shard'] not in shards, 'gate_duplicate_shard')
        shards.add(draft['shard'])
        q.require(draft['qualification'] == dict(complete=False, restoration='pending'), 'gate_draft_not_pending')
        q.require(draft['binding'] == recovery['binding'] and draft['helperSHA256'] == recovery['helperSHA256'],
                  'gate_capture_identity')
        recipe = copy.deepcopy(draft)
        # The gate bytes are deterministic and become an input to each recipe.
        retain(output/'gate.json', gate)
        recipe['qualification'] = dict(complete=True, restoration='verified', evidence=pin(output/'gate.json'))
        native_coverage402.validate_controls(recipe)
        recipe_path = output/(entry['id']+'-recipe.json')
        retain(recipe_path, recipe)
        dependency = dict(job=spec['id'], specSHA256=q.text_digest(spec), outputs=['gate.json'])
        doc = dict(version='hcf-template-description-v1', id=entry['id'], task=spec['task'],
            owner='Maximum-mini-NUIAK', template='T03',
            question='Do native controls retain verified focus and measured body geometry across the frozen contrast conditions?',
            decision='Keep verified development pairs. Reject missing geometry or uncertain restoration. Preserve Standard and previous successes.',
            inputs=dict(recipe=pin(recipe_path), staging=plan['staging']), parameters={}, dependencies=[dependency],
            capture=dict(target=recipe['binding']['simulatorUDID'], endpoint=recipe['binding']['endpoint'],
                plan=pin(recipe_path), approval='The maintainer approves these 6 frozen native captures only after verified recovery.'))
        child = templates.build(doc)
        child['conditions'] = [dict(job=spec['id'], output='gate.json', outcome='supported')]
        child['inputs'].append(entry['draft'])
        q.validate(child)
        children.append(child)
    q.require(len({c['capture']['plan']['sha256'] for c in children}) == 6, 'gate_duplicate_recipe')
    return children, recovery


def preflight(recovery):
    """Read current identities. Existing capture approval checks ownership again."""
    import qualify_hcf362 as runtime
    from generation352 import MARKER
    q.require(not MARKER.exists(), 'gate_recovery_guard_present')
    q.require(q.digest(runtime.CLI.resolve()) == recovery['helperSHA256'], 'gate_helper_changed')
    q.require(runtime.d.bind_target(native343.TARGET, recovery['binding']['endpoint']) == recovery['binding'],
              'gate_fixture_changed')


def admit(children, queue, output):
    """Idempotent exact-ID admission. A revocation always requires human review."""
    with q.host_lock(queue/'recovery-admission.lock', wait=30):
        records = approval.load(queue)
        ids = {child['id'] for child in children}
        q.require(not any(e.get('action') == 'revoke' and e.get('job') in ids for e in records['events']),
                  'gate_child_revoked')
        for child in children:
            existing = queue/'jobs'/child['id']/'spec.json'
            if existing.exists():
                q.require(q.load(existing) == child, 'gate_child_conflict')
        for child in children:
            path = output/(child['id']+'-spec.json')
            retain(path, child)
            q.submit(path, queue)
        for child in children:
            approval.approve(queue, child['id'], 'agent:Maximum-mini-NUIAK',
                'Maintainer-approved frozen capture after verified restoration. No scope or budget expansion.')
    return [dict(job=c['id'], specSHA256=q.text_digest(c)) for c in children]


def run():
    spec = q.load(OUT.parents[2]/'spec.json')
    queue = OUT.parents[4]
    plan = q.load(checked(spec['admissionPlan']))
    children, recovery = prepare(spec, queue, plan, OUT)
    preflight(recovery)
    rows = admit(children, queue, OUT)
    retain(OUT/'admission.json', dict(version='recovery-capture-admission-result-v1', jobs=rows,
        executionStarted=False, modelAccepted=False, trainingEligible=False))
    retain(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=p.name, sha256=q.digest(p)) for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'artifact-receipt.json']))


def specification(ident, plan_path):
    plan = q.load(plan_path)
    inputs = [pin(plan_path), plan['staging'], *[e['draft'] for e in plan['captures']], pin(Path(__file__))]
    return dict(version='research-spec-v2', id=ident, task='GATE433', owner='Maximum-mini-NUIAK',
        kind='screen', authority='diagnostic', jobKind='artifact', admissionPlan=pin(plan_path),
        hypothesis='Verified recovery can release only the frozen capture batch through existing queue admission.',
        question='Does completed restoration safely release the 6 fixed native captures without another manual preparation step?',
        controlledComparison='Pending restoration blocks capture. Verified restoration binds only the approved recipes.',
        decisionRule='Admit only the named captures after verified recovery. Preserve guards, failures, and revoked approvals.',
        nextActionByOutcome=dict(supported='Let the existing runner execute the approved capture jobs.',
                                 contradicted='Preserve the failed admission and repair its exact requirement.'),
        inputs=inputs, dependencies=[dict(**plan['recovery'], outputs=OUTPUTS)],
        evidence=dict(reads=[p['path'] for p in inputs[:-1]], artifactReceipt='artifact-receipt.json'),
        adapter=dict(type='python-callable', steps=['recovery_capture_gate433.run'], outputAttributes=['recovery_capture_gate433.OUT']),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1))
