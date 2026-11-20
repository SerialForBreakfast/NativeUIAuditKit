"""Prepare observed binary focus labels from episodes without inventing detector classes."""
from pathlib import Path
import research_queue as q
from experiment_templates import checked, pin
from sdk_episode_labels530 import normalize
from sdk_training513 import prepare_crops
OUT = None



def build(path):
    request = q.load(path); normalize(request)
    episode = q.load(checked(request['episodes']))
    refs = [pin(path), request['episodes'], request['tool']] + [r for e in episode['episodes'] for f in e['frames'] for r in f.values()]
    refs = list({r['path']: r for r in refs}.values())
    return dict(version='research-spec-v2', id=request['id'], task='SDK530', owner='Maximum-mini-NUIAK',
        kind='screen', jobKind='artifact', authority='diagnostic', dependencies=[], inputs=refs+[pin(Path(__file__))],
        adapter=dict(type='python-callable', steps=['sdk_episode_crops530.run'], outputAttributes=['sdk_episode_crops530.OUT']),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100000000, maxAttempts=1),
        evidence=dict(reads=[r['path'] for r in refs], artifactReceipt='artifact-receipt.json'),
        question='Can observed native focus and bounds supply production crops without detector class guesses?',
        hypothesis='Static focus labels remain usable when unrelated taxonomy or temporal fields are unavailable.',
        controlledComparison='Reuse exact images, native evidence, groups, and production preprocessing. No new capture or training.',
        decisionRule='Reject unknown frame focus and inconsistent pixel labels. Keep missing profile and training roles explicit.',
        nextActionByOutcome=dict(supported='Use these reviewed labels to verify the producer contract for independent training groups.',
                                 contradicted='Repair the exact failed label or crop requirement. Preserve source evidence.'))


def run():
    spec=q.load(OUT.parents[2]/'spec.json'); request=q.load(checked(spec['inputs'][0])); data=normalize(request)
    q.save(OUT/'labels.json', data)
    crops=prepare_crops(data, OUT/'crops', request['tool']) if data['frames'] else dict(rows=[], trainingEligible=False)
    q.save(OUT/'crops.json', crops)
    paths=[OUT/'labels.json',OUT/'crops.json']
    for row in crops['rows']:
        path=Path(row['path']).resolve()
        q.require(path.is_relative_to(OUT.resolve()) and q.digest(path)==row['sha256'], 'episode_crops_output')
        paths.append(path)
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[dict(path=str(p.relative_to(OUT)),sha256=q.digest(p)) for p in paths]))
