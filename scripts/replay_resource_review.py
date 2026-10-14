"""Review saved replay outputs without changing their original receipt."""
import copy
import research_queue as q

OUT = None


def comparison(spec, replay_out):
    """Keep scientific comparisons exact. Report peak memory separately."""
    revised = copy.deepcopy(spec)
    entry, = [item for item in revised['replay']['files'] if item['name'] == 'preparation.json']
    q.require(entry['compare'] == 'json' and entry.get('tolerance', 0) == 0, 'review_exact_required')
    original = q.load(q.ROOT / spec['replay']['recordedDirectory'] / 'preparation.json')
    replayed = q.load(replay_out / 'preparation.json')
    for value in (original.get('peakBytes'), replayed.get('peakBytes')):
        q.require(type(value) is int and value >= 0, 'review_peak_memory_missing')
    entry.setdefault('ignore', []).append(dict(path='peakBytes', reason='Peak process memory is a resource measurement.'))
    result = q.compare_replay(revised, replay_out)
    return dict(version='replay-resource-review-v1', scientificMatched=result['matched'],
                files=result['files'], resourceMeasurements=dict(
                    recordedPeakBytes=original['peakBytes'], replayedPeakBytes=replayed['peakBytes'],
                    deltaPeakBytes=replayed['peakBytes'] - original['peakBytes']),
                originalReceiptChanged=False, modelAccepted=False)


def run():
    config = q.load(OUT / 'review-config.json')
    spec_ref = config['replaySpec']
    source_path = q.ROOT / spec_ref['path']
    q.require(q.digest(source_path) == spec_ref['sha256'], 'review_spec_changed')
    spec = q.load(source_path)
    q.verify_pins(spec)
    dependencies = q.load(OUT / 'dependencies.json')
    dep, = dependencies
    q.require(dep['job'] == spec['id'] and dep['specSHA256'] == q.text_digest(spec), 'review_dependency_identity')
    for item in dep['outputs']:
        q.require(q.digest(q.ROOT / item['path']) == item['sha256'], 'review_output_changed')
    weight, = [item for item in dep['outputs'] if item['path'].endswith('/last.pt')]
    replay_out = (q.ROOT / weight['path']).parent
    review = comparison(spec, replay_out)
    q.save(OUT / 'review.json', review)
    q.save(OUT / 'sources.json', dep['outputs'])
    q.require(review['scientificMatched'], 'review_scientific_mismatch')
    q.save(OUT / 'model.json', dict(path=str(q.ROOT / weight['path']), sha256=weight['sha256'], seed=42))
