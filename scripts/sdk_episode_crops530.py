"""Prepare observed binary focus labels from episodes without inventing detector classes."""
from pathlib import Path
import research_queue as q
from experiment_templates import checked, pin
from sdk_episode529 import intake
from sdk_focus_episode529 import visible
from sdk_training513 import prepare_crops
OUT = None


def normalize(request):
    q.require(set(request) == {'version', 'id', 'episodes', 'tool'} and
              request['version'] == 'sdk-episode-crops-v1' and q.ID.fullmatch(request['id']), 'episode_crops_request')
    checked(request['tool'])
    data = intake(q.load(checked(request['episodes'])))
    frames = []; seen = {}; excluded = []; empty = []; occurrences = []
    for episode in data['episodes']:
        # This adapter prepares reviewed labels. Training admission remains a separate decision.
        q.require(episode['role'] in ('review_only', 'development', 'evaluation'), 'episode_crops_role')
        for index, frame in enumerate(episode['frames']):
            key = episode['id'] + f'-frame-{index:03}'
            if not frame['frameReviewable'] or frame['frameFocusState'] not in ('focused', 'no_focus'):
                excluded.append(dict(id=key, reasons=frame['frameIssues'], focusState=frame['frameFocusState']))
                continue
            controls = [c for c in frame['controls'] if visible(c)]
            q.require(frame['focusID'] is None or sum(c['identity']['id'] == frame['focusID'] for c in controls) == 1,
                      'episode_crops_focus_geometry')
            labels = sorted((c['identity']['id'], c['pixelBounds'], int(c['identity']['id'] == frame['focusID'])) for c in controls)
            digest = frame['image']['sha256']
            identity = dict(group=episode['group'], role=episode['role'], labels=labels)
            prior = seen.setdefault(digest, identity)
            q.require(prior == identity, 'episode_crops_conflicting_pixels')
            occurrences.append(dict(id=key, image=frame['image'], group=episode['group'], sourceRole=episode['role']))
            if sum(o['image']['sha256'] == digest for o in occurrences) > 1:
                continue
            if not controls:
                empty.append(dict(id=key, image=frame['image'], group=episode['group'], focusState='no_focus'))
                continue
            frames.append(dict(frame, id=key, sourceFrameID=frame['captureID'], sha256=digest,
                group=episode['group'], contentGroup=episode['group'], family=frame['appID'], controls=controls,
                role='review_only', sourceRole=episode['role'], profile='unknown', pair=request['episodes'],
                missing=['observed_profile_unqualified', 'training_admission_required'], trainingEligible=False))
    return dict(version='sdk-episode-crop-labels-v1', frames=frames, excluded=excluded, emptyFrames=empty,
        occurrences=occurrences, uniqueImages=len(seen), trainingEligible=False, modelAccepted=False,
        requirements=['Observed profile and continuity for profile-specific training.',
                      'Independent eligible training and development groups. Preserve existing evaluation exclusions.'],
        limitation='Binary focus labels do not require primary/secondary detector roles. Empty frames produce no crop. Repeated pixels produce one crop set.')


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
