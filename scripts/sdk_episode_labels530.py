"""Check native episode labels without queue authoring or model execution."""
import research_queue as q
from template_inputs398 import checked
from sdk_episode529 import intake
from sdk_semantics529 import visible_control as visible


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

