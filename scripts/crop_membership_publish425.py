"""Validate retained crop membership and publish it as a queue dependency."""
import shutil
import research_queue as q
from native_control_membership import validate_rows

OUT = None


def validate(document):
    rows = document['rows']
    q.require(rows and len({r['id'] for r in rows}) == len(rows), 'membership_duplicate_id')
    q.require({r['role'] for r in rows} == {'train', 'development'}, 'membership_roles')
    from focus_runtime import RUNTIME_PREPROCESSING
    q.require(document['preprocessing'] == RUNTIME_PREPROCESSING, 'membership_preprocessing')
    validate_rows(rows)
    return rows


def run():
    source = OUT / 'membership.json'
    spec = q.load(OUT.parents[2] / 'spec.json')
    reference = next(item['from'] for item in spec['stage'] if item['to'] == 'membership.json')
    from template_inputs398 import checked
    q.require(q.digest(checked(reference)) == q.digest(source), 'membership_stage_changed')
    rows = validate(q.load(source))
    shutil.copyfile(source, OUT / 'crops.json')
    q.require(q.digest(source) == q.digest(OUT / 'crops.json'), 'membership_copy_changed')
    q.save(OUT / 'summary.json', dict(
        version='crop-membership-publication-v1', rows=len(rows),
        trainingRows=sum(r['role'] == 'train' for r in rows),
        developmentRows=sum(r['role'] == 'development' for r in rows),
        imagePayloadsCopied=0, modelAccepted=False))
    q.save(OUT / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=name, sha256=q.digest(OUT / name)) for name in ('crops.json', 'summary.json')]))
