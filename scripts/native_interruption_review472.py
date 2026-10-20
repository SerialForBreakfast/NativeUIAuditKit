"""Import native interruption evidence for review, never for training."""
import math
from collections import Counter

from PIL import Image
import research_queue as q

OUT = None


def checked(pin):
    q.check_pin(pin)
    path = q.local_path(q.ROOT, pin['path'])
    q.require(path.is_file() and q.digest(path) == pin['sha256'], 'review_hash_changed')
    return path


def bounds(value, width=1, height=1):
    q.require(isinstance(value, list) and len(value) == 4 and
              all(type(v) in (int, float) and math.isfinite(v) for v in value),
              'review_bounds_type')
    x, y, w, h = value
    q.require(x >= 0 and y >= 0 and w > 0 and h > 0 and
              x + w <= width + 1e-6 and y + h <= height + 1e-6,
              'review_bounds_range')
    return value


def close(a, b):
    q.require(len(a) == len(b) and all(abs(x-y) <= 1e-5 for x, y in zip(a, b)),
              'review_geometry_mismatch')


def review(config):
    q.require(set(config) == {'version', 'revision', 'sources'} and
              config['version'] == 'native-interruption-review-input-v1', 'review_config')
    doc = q.load(checked(config['revision']))
    q.require(doc.get('schema_version') == 2 and doc.get('revision') == 2 and
              doc.get('serialized_annotation_bounds_encoding') == 'xywh' and
              doc.get('source_normalized_array_encoding') == 'xyxy', 'review_schema')
    q.require(doc.get('training_admission') is False, 'review_training_claim')
    rows, events, pixels, streams = [], set(), {}, {}
    q.require(len(config['sources']) == len(doc['rows']) > 0, 'review_source_count')
    for row, source in zip(doc['rows'], config['sources']):
        q.require(set(source) == {'image', 'sidecar'}, 'review_source_fields')
        image, native = checked(source['image']), q.load(checked(source['sidecar']))
        q.require(source['image']['sha256'] == row['sha256'] and
                  source['sidecar']['sha256'] == row['native_sidecar_sha256'], 'review_source_hash')
        with Image.open(image) as opened:
            q.require(opened.size == (row['width'], row['height']), 'review_dimensions')
        q.require(row['bounds_encoding'] == 'image_top_left_normalized_xywh', 'review_encoding')
        q.require(row['training_admission'] is False and
                  row['class_review_status'] == 'unreviewed' and row['reviewed_classes'] == [] and
                  row['whole_screen_complete'] is False and row['complete_detector_class_labels'] is False,
                  'review_unverified_class_claim')
        q.require(row['capture_profile'] == 'unavailable_in_original_review_projection', 'review_profile_claim')
        q.require(native['sha256'] == row['sha256'] and native['split_group'] == row['group'] and
                  native['case_id'] == row['case_id'] and native['role'] == row['role'] and
                  native['native_focus'] == row['native_focus'] and native['training_admission'] is False,
                  'review_sidecar_identity')
        q.require(pixels.setdefault(row['sha256'], row['group']) == row['group'], 'review_group_leakage')
        temporal = row['temporal_evidence']
        key = temporal['capture_event_key']
        q.require(isinstance(key, str) and q.HASH.fullmatch(key) and key not in events, 'review_event_identity')
        events.add(key)
        q.require(temporal['receipt_state'] == 'delivered' and temporal['effect_status'] == 'unverified' and
                  temporal['correlation'] == 'validated_capture_bracket_not_atomic',
                  'review_temporal_claim')
        q.require(temporal['host_interval_clock_domain'] == 'capture_host_only' and
                  temporal['fixture_clock_domain'] == 'fixture_only; never compare absolute values to host',
                  'review_clock_domain')
        sequence = temporal['capture_sequence']
        stream = temporal['capture_stream_key']
        q.require(type(sequence) is int and sequence > streams.get(stream, -1), 'review_sequence')
        streams[stream] = sequence
        objects = row['objects']
        ids = [o['id'] for o in objects]
        q.require(len(ids) == len(set(ids)) and set(ids) == set(row['body_scope_expected_ids']) ==
                  set(row['body_scope_exported_ids']) and row['complete_for_reported_body_scope'] is True,
                  'review_scope')
        annotations = native['annotations']
        q.require(len(annotations) == len(objects), 'review_annotation_count')
        by_label = {a['label']: a for a in annotations}
        q.require(len(by_label) == len(annotations), 'review_annotation_duplicate')
        for obj in objects:
            xywh = bounds(obj['bounds_normalized_xywh'])
            px = [xywh[0]*row['width'], xywh[1]*row['height'],
                  xywh[2]*row['width'], xywh[3]*row['height']]
            measured = obj.get('native_visible_pixel_xywh', obj.get('native_pixel_xywh'))
            bounds(measured, row['width'], row['height'])
            close(px, measured)
            if 'source_visible_normalized_xyxy' in obj:
                x, y, w, h = xywh
                close([x, y, x+w, y+h], obj['source_visible_normalized_xyxy'])
            label = obj.get('annotation_label', obj['id'])
            q.require(label in by_label, 'review_annotation_missing')
            annotation = by_label[label]
            close(xywh, [annotation['bounds'][k] for k in ('x', 'y', 'width', 'height')])
            q.require(type(obj['focused']) is bool and
                      annotation['attributes']['focused'] == str(obj['focused']).lower() and
                      annotation['attributes']['geometry_role'] == obj['geometry_role'],
                      'review_focus_mismatch')
        interrupted = row['role'] == 'interrupted'
        for snapshot in temporal['snapshots'].values():
            if interrupted:
                q.require(snapshot['underlay_focus_observation'] is None and
                          snapshot['underlay_observation_availability'] == 'unknown',
                          'review_unknown_coercion')
                overlay = snapshot['interruption']
                q.require(overlay['observation']['focus_owner'] == 'overlay' and
                          overlay['observation']['overlay_settled'] is True and
                          overlay['observed_focus_id'] == 'interruption.continue',
                          'review_overlay_focus')
        # Preserve source records. Do not turn excluded controls into negative examples.
        rows.append(dict(event=key, image=source['image'], sidecar=source['sidecar'],
                         group=row['group'], case=row['case_id'], role=row['role'],
                         profile=None, classLabels=None, classReview='withheld',
                         objects=objects, omitted=row['omitted_or_occluded_controls'],
                         temporalEvidence=temporal, nativeFocus=row['native_focus'],
                         underlayFocus='unknown' if interrupted else 'source-observed',
                         wholeScreenComplete=False, trainingEligible=False))
    q.require(len(rows) == doc['events'] and len(pixels) == doc['distinct_png_hashes'] and
              len({r['group'] for r in rows}) == doc['independent_layout_groups'], 'review_totals')
    return dict(version='native-interruption-review-v1', source=config['revision'],
                rows=rows, events=len(rows), uniqueImages=len(pixels),
                groups=len({r['group'] for r in rows}),
                classDecision='Withhold canonical classes. Producer declarations are not independent class reviews.',
                declaredClasses=dict(Counter(str(o.get('declared_taxonomy_class')) for r in rows for o in r['objects'])),
                reviewAccepted=True, trainingEligible=False, modelAccepted=False,
                captureBracketIndependentlyVerified=False)


def run():
    spec = q.load(OUT.parents[2] / 'spec.json')
    result = review(q.load(checked(spec['reviewConfig'])))
    q.save(OUT / 'review.json', result)
    q.save(OUT / 'benchmark_summary.json', {k: v for k, v in result.items() if k != 'rows'})
    q.save(OUT / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=name, sha256=q.digest(OUT/name)) for name in ('review.json', 'benchmark_summary.json')]))
