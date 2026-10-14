"""Require a complete detector run before the retained comparison."""
import research_queue as q


def register():
    folder = q.ROOT / 'Research/ResearchSpecs/DEPENDENCY-REPAIR-385'
    specs = []
    for suffix in ('71-detector-train', '81-detector-evaluate', '90-decision'):
        original_id = 'hcf375d-' + suffix
        spec = q.load(q.QUEUE / 'jobs' / original_id / 'spec.json')
        spec['id'] += '-v2'
        if suffix.startswith('71'):
            spec['adapter'] = dict(type='python-callable', steps=['hcf_complete_training.detector'],
                                   outputAttributes=['hcf_complete_training.OUT'])
            code = q.ROOT / 'scripts/hcf_complete_training.py'
            spec['inputs'].append(dict(path=q.relative(code), sha256=q.digest(code)))
            spec['decisionRule'] = 'Require 30 completed epochs and terminal checkpoint history. Early stopping is incomplete. Preserve all failed evidence.'
            spec['training']['acceptanceEvidence'] += ' Require all 30 epochs before the comparison.'
        else:
            for dep in spec['dependencies']:
                match = next((s for s in specs if s['id'] == dep['job'] + '-v2'), None)
                if match:
                    dep.update(job=match['id'], specSHA256=q.text_digest(match))
        specs.append(spec)
        path = folder / (spec['id'] + '.json')
        if path.exists():
            q.require(q.load(path) == spec, 'immutable_spec_changed')
        else:
            q.save(path, spec)
        print(spec['id'], q.submit(path))


if __name__ == '__main__':
    register()
