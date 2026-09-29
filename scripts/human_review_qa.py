"""One-command immutable review→production crops→audit; never admits or infers."""
import argparse
import json
import human_annotation_review as h
import human_regression_review as review
import human_review_audit as audit


def run(revision, output, *, completeness=None, crops=None):
    output = h.fresh(output)
    output.mkdir(parents=True)
    result = dict(version='human-review-qa-handoff-v1', **h.FLAGS, completed=False,
                  stage='revision', inputs={}, counts={}, blockedFrames=[])
    try:
        revision = h.local(revision)
        result['inputs']['revision'] = h.ref(revision)
        doc = review.checked_revision(revision)
        result['counts'] = dict(frames=len(doc['frames']),
                                controls=sum(len(f['controls']) for f in doc['frames']))
        result['blockedFrames'] = [dict(id=f['id'], disposition=f['disposition'])
                                  for f in doc['frames'] if f['disposition'] != 'reviewed']
        result['stage'] = 'completeness'
        result['completeFrames'] = []
        if completeness:
            result['completeFrames'] = sorted(review.checked_completeness(completeness, revision))
            result['inputs']['completeness'] = h.ref(h.local(completeness))
        h.require(not result['blockedFrames'], 'pending_frames_preserved_no_qualification')
        result['stage'] = 'crops'
        if crops is None:
            h.crop_qa(h.checked(h.ROOT, doc['batch']), output/'crops', revision)
            crops = output/'crops/crop-qa.json'
        result['inputs']['crops'] = h.ref(h.local(crops))
        result['stage'] = 'audit'
        report = audit.run(revision, crops, output/'audit')
        result['counts'].update(report['counts'])
        result['issues'] = report['issues']
        h.require(not any(i['severity'] == 'hard' for i in report['issues']), 'hard_audit_issues')
        result['stage'] = 'postflight'
        for ref in result['inputs'].values(): h.checked(h.ROOT, ref)
        review.checked_revision(revision)
        result.update(completed=True, stage='complete')
    except (ValueError, OSError, KeyError, TypeError) as error:
        result['error'] = f'{type(error).__name__}: {error}'
    h.write(output/'handoff.json', result, sealed=True)
    (output/'summary.md').write_text(
        '# Review QA — development diagnostics\n\n'
        + ('Completed' if result['completed'] else 'Blocked') + ': ' + result['stage'] + '\n\n'
        + 'Counts: ' + json.dumps(result['counts'], sort_keys=True) + '\n\n'
        + 'Human-attested complete frames: ' + str(len(result.get('completeFrames', []))) + '\n\n'
        + ('Error: ' + result['error'] + '\n\n' if 'error' in result else '')
        + 'See handoff.json for complete input bindings, exclusions and issues; '
          'audit/review.html contains numbered evidence when generated.\n\n'
          'No labels approved, no training admission, no model inference.\n')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('revision'); p.add_argument('output')
    p.add_argument('--completeness'); p.add_argument('--crops', help='Reuse a verified crop report; no regeneration')
    args = p.parse_args()
    result = run(args.revision, args.output, completeness=args.completeness, crops=args.crops)
    print(json.dumps(result, allow_nan=False))
    p.exit(0 if result['completed'] else 2)
