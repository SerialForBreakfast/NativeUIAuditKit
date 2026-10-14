"""Run the retained native spatial audit through the existing queue."""
import research_queue as q
from hcf_spatial_audit import audit

OUT = None


def run():
    dependencies = q.load(OUT/'dependencies.json')
    q.require(len(dependencies) == 1, 'dependency_count')
    reference = dependencies[0]['outputs'][0]
    path = q.ROOT/reference['path']
    q.require(q.digest(path) == reference['sha256'], 'capture_changed')
    q.save(OUT/'summary.json', audit(path))
