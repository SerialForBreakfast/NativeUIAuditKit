"""Tests for the production-path Q-packet importer check (`qpacket_import604`)."""
import tempfile
import unittest
from pathlib import Path

import qpacket_import604 as qp
import research_queue as q


class QPacketImportTests(unittest.TestCase):
    def test_equal_left_edges_survive_float_jitter_and_reordering(self):
        row = {'id': 'buttons', 'controls': [
            {'objectId': name, 'class': 'button', 'bounds': [100, y, 50, 20]}
            for name, y in [('top', 20), ('middle', 60), ('bottom', 100)]
        ]}
        decoded = {'buttons': [
            {'cls': 'button', 'box': [x, y, 50, 20]}
            for x, y in [(99.9998, 100), (100.0002, 20), (100, 60)]
        ]}
        self.assertEqual(qp.check_tensor(row, decoded), [])

    def test_matching_requires_distinct_same_class_boxes_within_one_pixel(self):
        row = {'id': 'pair', 'controls': [
            {'objectId': str(x), 'class': 'button', 'bounds': [x, 0, 10, 10]}
            for x in (1, 0)
        ]}
        left = {'cls': 'button', 'box': [0, 0, 10, 10]}
        right = {'cls': 'button', 'box': [2, 0, 10, 10]}
        # First target can use either box. The second needs the left box.
        self.assertEqual(qp.check_tensor(row, {'pair': [left, right]}), [])
        self.assertTrue(qp.check_tensor(row, {'pair': [right, right]}))
        self.assertIn('tensor.geometry:1', qp.check_tensor(
            dict(row, controls=row['controls'][:1]), {'pair': [dict(right, box=[2.001, 0, 10, 10])]}))
        self.assertIn('tensor.class:1:cell!=button', qp.check_tensor(
            row, {'pair': [left, dict(right, cls='cell')]}))

    def test_decoded_geometry_limits_apply_in_source_pixels(self):
        self.assertFalse(qp.geometry_in_tolerance([0, 0, 100, 80], 0.970, 1))
        self.assertFalse(qp.geometry_in_tolerance([0, 0, 1, 80], 0.50, 2))
        self.assertTrue(qp.geometry_in_tolerance([0, 0, 1, 80], 0.50, 1))

    def test_synthetic_packet_clean_accepted_and_each_twin_rejected_for_its_named_check(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='qpacket604-') as tmp:
            work = Path(tmp)
            summary = qp.run_packet(qp.build_synthetic(work / 'packet'), work)
            self.assertEqual(summary['frames'], 12)
            self.assertEqual(summary['clean_accepted'], 2)
            self.assertEqual(summary['twins_rejected_for_named_reason'], 10)
            by_mut = {r['mutation']: r for r in summary['results'] if r['mutation']}
            self.assertEqual(set(by_mut), set(qp.MUTATIONS))
            self.assertIn('tensor.class', by_mut['M8']['checks'])
            self.assertIn('importer.frame_identity_mismatch', by_mut['M10']['checks'])

    def test_twin_rejected_for_the_wrong_reason_does_not_pass(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='qpacket604-') as tmp:
            work = Path(tmp)
            packet = qp.build_synthetic(work / 'packet')
            manifest = q.load(packet / 'manifest.json')
            for f in manifest['frames']:
                if f.get('mutation') == 'M7':
                    f['expected'] = {'reject': ['answer_key.roles']}
            q.save(packet / 'manifest.json', manifest, replace=True)
            summary = qp.run_packet(packet, work)
            m7 = next(r for r in summary['results'] if r['mutation'] == 'M7')
            self.assertEqual(m7['outcome'], 'rejected')
            self.assertFalse(m7['passed'])


if __name__ == '__main__':
    unittest.main()
