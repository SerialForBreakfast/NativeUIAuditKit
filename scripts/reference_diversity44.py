"""Executable data-diversity comparison preflight, with unchanged evaluation pins.

Inspect a validated review batch; never assign a split, admit data or load a model.
"""
import argparse
from collections import Counter, defaultdict
import statistics
import human_annotation_review as h
from fixture_batch_review import validate


def summarize(batch):
    frames = batch['frames']; families = defaultdict(list); pixels = defaultdict(list)
    pair_frames = defaultdict(list); positions = Counter(); role_counts = Counter()
    for frame in frames:
        pack = frame['recipe']['appearance']['referencePack']
        families[pack['screen']].append(frame['id'])
        pixels[frame['pixelSHA256']].append(frame)
        pair_frames[frame['sourcePairID']].append(frame)
        role_counts[frame['sourceRole']] += 1
        for c in frame['proposals']:
            if c['state'] != 'focused': continue
            x, y, w, v = c['bounds']; width, height = frame['size']
            column = min(2, int(3*(x+w/2)/width)); row = min(2, int(3*(y+v/2)/height))
            positions[f'{pack["screen"]}:{row}:{column}'] += 1
    growth = defaultdict(list); common = Counter(); excluded = Counter()
    for members in pair_frames.values():
        h.require(len(members) == 2, 'diversity_pair_membership')
        a, b = members
        by_id = {c['sourceElementID']:c for c in b['proposals']}
        family = a['recipe']['appearance']['referencePack']['screen']
        for c in a['proposals']:
            d = by_id.get(c['sourceElementID'])
            if d is None: continue
            common[a['evidenceKind']] += 1
            if {c['state'], d['state']} != {'focused', 'unfocused'}: continue
            focused, unfocused = (c, d) if c['state'] == 'focused' else (d, c)
            fw, fh = focused['bounds'][2:]; uw, uh = unfocused['bounds'][2:]
            growth[family].append(dict(pair=a['sourcePairID'], element=c['sourceElementID'],
                                      widthRatio=fw/uw, heightRatio=fh/uh, areaRatio=fw*fh/(uw*uh)))
    for record in batch['records']:
        if record['disposition'] == 'producer_excluded': excluded[record['reason']] += 1
    duplicate_groups = [[f['id'] for f in group] for group in pixels.values() if len(group)>1]
    # Family grouping is deliberately broader than seed/appearance changes.
    # All reference families additionally retain one shared renderer ancestry.
    return dict(frames=len(frames), uniquePixels=len(pixels), families=dict(families),
                roleCounts=dict(role_counts), focusedPositionBins=dict(positions),
                commonControlPairs=dict(common), excludedObservations=dict(excluded),
                duplicateGroups=duplicate_groups,
                growth={k:dict(observations=v, count=len(v), medianAreaRatio=statistics.median(
                    x['areaRatio'] for x in v)) for k,v in growth.items()},
                splitPolicy=dict(renderer='fixture_procedural_renderer_v1',
                    indivisibleGroups=dict(families), claim='same-renderer development, not independent real-app test'),
                missingRequiredNativeFamilies=['native_settings_rows', 'native_tabs', 'native_dialog_buttons'],
                sourceInterpretation={'nostalgex_guide':'custom row highlight; not native Settings styling',
                                      'stingray_catalog':'native image focus inside reference catalog card'})


def run(batch_path, baseline_path, output):
    batch_path, baseline_path, output = h.local(batch_path), h.local(baseline_path), h.fresh(output)
    batch = validate(batch_path); baseline = h.read(baseline_path)
    h.require(baseline['version'] == 'fullscreen-focus-run-v2', 'comparison_baseline_version')
    evaluation = [f for f in baseline['frames'] if f['split'] == 'evaluation']
    training = [f for f in baseline['frames'] if f['split'] == 'train']
    h.require(len(evaluation) == 500 and len(training) == 2000, 'comparison_baseline_membership')
    config = {k:baseline[k] for k in ('checkpoint','epochs','batch','imgsz','seed','runtime','evaluationPolicy','storage')}
    h.checked(h.ROOT, config['checkpoint'])
    report = dict(version='reference-diversity-preflight-v1', **h.FLAGS,
                  batch=h.ref(batch_path), baseline=h.ref(baseline_path), coverage=summarize(batch),
                  comparison=dict(question='Does adding reviewed reference layouts improve focus localization with the same model?',
                    fixedConfiguration=config, unchangedEvaluationSHA256=h.digest(evaluation),
                    baselineTrainingSHA256=h.digest(training), candidateMembershipSHA256=h.digest(batch['frames']),
                    arms=['original training corpus', 'original corpus plus admitted reference training families'],
                    metrics=['focused-body recall at fixed .25 confidence and IoU .50/.70/.90',
                             'correct/wrong/abstained selections on complete frames',
                             'per-family false positives and misses', 'actual optimizer updates and elapsed time'],
                    interpretation='Data addition also changes epoch exposure; record updates, do not claim equal-compute comparison.'),
                  trainingReady=False, blockers=[
                      'Reference delivery retains calibration role; exact reviewed training membership needs approval.',
                      'Sampled review and explicit complete-visible-focus confirmation remain pending.',
                      'Native Settings rows, tabs and dialog coverage are absent; reference guide is not a substitute.',
                      'New-family held-out comparison membership must be designated before fitting; preserve old evaluation.'])
    h.write(output, report)
    print({k: report['coverage'][k] for k in ('frames','uniquePixels','roleCounts','commonControlPairs')})
    return report


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',required=True);p.add_argument('--baseline',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.batch,a.baseline,a.output)
