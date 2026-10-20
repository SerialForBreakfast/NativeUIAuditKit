"""Review importer contracts use synthetic evidence without device access."""
import copy
import unittest
from unittest.mock import patch, MagicMock
import native_interruption_review472 as n


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.obj = dict(id='interruption_action', annotation_label='interruption.continue',
                        focused=True, geometry_role='interruption_action',
                        bounds_normalized_xywh=[.1, .2, .3, .4],
                        native_pixel_xywh=[10, 20, 30, 40])
        self.snapshot = dict(underlay_focus_observation=None, underlay_observation_availability='unknown',
                             interruption=dict(observed_focus_id='interruption.continue',
                                 observation=dict(focus_owner='overlay', overlay_settled=True)))
        self.row = dict(sha256='a'*64, native_sidecar_sha256='b'*64, width=100, height=100,
                        bounds_encoding='image_top_left_normalized_xywh', training_admission=False,
                        class_review_status='unreviewed', reviewed_classes=[], whole_screen_complete=False,
                        complete_detector_class_labels=False,
                        capture_profile='unavailable_in_original_review_projection',
                        group='one', case_id='pairing', role='interrupted', native_focus='interruption.continue',
                        objects=[self.obj], body_scope_expected_ids=['interruption_action'],
                        body_scope_exported_ids=['interruption_action'], complete_for_reported_body_scope=True,
                        omitted_or_occluded_controls=[], temporal_evidence=dict(capture_event_key='c'*64,
                            capture_stream_key='d'*64, capture_sequence=1, receipt_state='delivered',
                            effect_status='unverified', correlation='validated_capture_bracket_not_atomic',
                            host_interval_clock_domain='capture_host_only',
                            fixture_clock_domain='fixture_only; never compare absolute values to host',
                            snapshots=dict(before_scene=copy.deepcopy(self.snapshot), after_scene=copy.deepcopy(self.snapshot))))
        self.native = dict(sha256='a'*64, split_group='one', case_id='pairing', role='interrupted',
                           native_focus='interruption.continue', training_admission=False, annotations=[
                               dict(label='interruption.continue', bounds=dict(x=.1,y=.2,width=.3,height=.4),
                                    attributes=dict(focused='true',geometry_role='interruption_action'))])
        self.doc = dict(schema_version=2, revision=2, serialized_annotation_bounds_encoding='xywh',
                        source_normalized_array_encoding='xyxy', training_admission=False,
                        events=1, distinct_png_hashes=1, independent_layout_groups=1, rows=[self.row])
        self.config = dict(version='native-interruption-review-input-v1', revision={},
                           sources=[dict(image=dict(sha256='a'*64),sidecar=dict(sha256='b'*64))])

    def evaluate(self):
        image = MagicMock()
        image.__enter__.return_value.size = (100,100)
        with patch.object(n, 'checked', return_value='unused'), \
             patch.object(n.q, 'load', side_effect=[self.doc,self.native]), \
             patch.object(n.Image, 'open', return_value=image):
            return n.review(self.config)

    def test_positive_preserves_unknown(self):
        r = self.evaluate()
        self.assertFalse(r['trainingEligible'])
        self.assertIsNone(r['rows'][0]['classLabels'])
        self.assertEqual(r['rows'][0]['underlayFocus'], 'unknown')

    def test_rejected_mutations(self):
        mutations = [
            ('review_schema', lambda: self.doc.update(revision=3)),
            ('review_training_claim', lambda: self.doc.update(training_admission=True)),
            ('review_source_hash', lambda: self.row.update(sha256='e'*64)),
            ('review_profile_claim', lambda: self.row.update(capture_profile='standard')),
            ('review_unverified_class_claim', lambda: self.row.update(reviewed_classes=['button'])),
            ('review_bounds_range', lambda: self.obj.update(bounds_normalized_xywh=[.9,.2,.3,.4])),
            ('review_geometry_mismatch', lambda: self.obj.update(native_pixel_xywh=[11,20,30,40])),
            ('review_focus_mismatch', lambda: self.obj.update(focused=False)),
            ('review_scope', lambda: self.row.update(body_scope_expected_ids=[])),
            ('review_clock_domain', lambda: self.row['temporal_evidence'].update(fixture_clock_domain='host')),
            ('review_unknown_coercion', lambda: self.row['temporal_evidence']['snapshots']['before_scene'].update(underlay_focus_observation='none')),
            ('review_totals', lambda: self.doc.update(events=2)),
        ]
        for reason, mutate in mutations:
            with self.subTest(reason=reason):
                self.setUp()
                mutate()
                with self.assertRaisesRegex(ValueError, reason):
                    self.evaluate()

    def test_hash_failure(self):
        with patch.object(n.q,'local_path') as path:
            path.return_value.is_file.return_value=True
            with patch.object(n.q,'digest',return_value='b'*64):
                with self.assertRaisesRegex(ValueError,'review_hash_changed'):
                    n.checked(dict(path='input.json',sha256='a'*64))

    def test_duplicate_event(self):
        self.doc['rows'].append(copy.deepcopy(self.row))
        self.config['sources'] *= 2
        image=MagicMock();image.__enter__.return_value.size=(100,100)
        with patch.object(n,'checked'), patch.object(n.q,'load',side_effect=[self.doc,self.native,self.native]), patch.object(n.Image,'open',return_value=image):
            with self.assertRaisesRegex(ValueError,'review_event_identity'):
                n.review(self.config)


if __name__ == '__main__':
    unittest.main()
