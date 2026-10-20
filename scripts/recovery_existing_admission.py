"""Approve pinned, unstarted capture successors after the existing recovery gate."""
import research_queue as q
import recovery_capture_gate437 as gate
from experiment_templates import checked

OUT = None


def prepare(spec, queue, plan):
    q.require(plan.get('version') == 'existing-capture-recovery-admission-v1', 'existing_gate_version')
    recovery, evidence = gate.verify_recovery(spec, queue, plan)
    refs = plan['captures']
    q.require(1 <= len(refs) <= 10, 'existing_gate_count')
    children = [q.load(checked(ref)) for ref in refs]
    q.require(len({child['id'] for child in children}) == len(children), 'existing_gate_duplicates')
    by_id = {child['id']: child for child in children}
    def anchored(child, visited):
        q.require(child['id'] not in visited, 'existing_gate_cycle')
        for dep in child.get('dependencies', []):
            if dep['job'] == plan['recovery']['job']:
                if dep['specSHA256'] == plan['recovery']['specSHA256'] and 'recovery.json' in dep['outputs']:
                    return True
            elif dep['job'] in by_id:
                parent = by_id[dep['job']]
                q.require(dep['specSHA256'] == q.text_digest(parent), 'existing_gate_parent_changed')
                if 'retention/compaction.json' in dep['outputs'] and anchored(parent, visited | {child['id']}):
                    return True
        return False
    for child in children:
        q.validate(child)
        q.require(child['authority'] == 'capture' and child['template']['id'] == 'T03', 'existing_gate_capture_only')
        q.require(child['capture']['target'] == recovery['binding']['simulatorUDID'], 'existing_gate_target')
        recipe = q.load(checked(child['capture']['plan']))
        q.require(recipe['binding'] == recovery['binding'] and recipe['helperSHA256'] == recovery['helperSHA256'],
                  'existing_gate_identity')
        q.require(anchored(child, set()), 'existing_gate_dependency')
        q.require(not q.attempts_of(queue/'jobs'/child['id']), 'existing_gate_started')
    return children, recovery


def run():
    spec = q.load(OUT.parents[2]/'spec.json')
    queue = OUT.parents[4]
    plan = q.load(checked(spec['admissionPlan']))
    children, recovery = prepare(spec, queue, plan)
    gate.preflight(recovery)
    rows = gate.admit(children, queue, OUT)
    gate.retain(OUT/'admission.json', dict(jobs=rows, executionStarted=False, modelAccepted=False))
    gate.retain(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=p.name, sha256=q.digest(p)) for p in sorted(OUT.iterdir())
        if p.is_file() and p.name != 'artifact-receipt.json']))
