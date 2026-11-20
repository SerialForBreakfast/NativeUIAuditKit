"""Tests for Swift vs Python retained-frame parity helper (`tvbench_parity604.py`)."""
import unittest

import tvbench_parity604 as tp


class TVBenchParityTests(unittest.TestCase):
    def test_compare_frame_pair_detects_parity_and_mismatch(self):
        swift_rec = dict(
            inputSHA256='abc',
            detections=[dict(cls='primaryButton', box=[10, 10, 50, 20], score=0.9)],
            eligibleCount=1,
            scoredCount=1,
            unsupportedRoleCount=0,
            cropRejectedCount=0,
            failedCount=0,
            focusBox=[10, 10, 50, 20],
            maxProbability=0.92,
            timings=dict(totalMs=12.0),
        )
        py_rec = dict(
            imageSHA256='abc',
            detections=[dict(cls='primaryButton', box=[10, 10, 50, 20], score=0.9)],
            focusBox=[10, 10, 50, 20],
            focusExecution=dict(
                eligibleCount=1,
                scoredCount=1,
                unsupportedRoleCount=0,
                cropRejectedCount=0,
                failedCount=0,
                maxProbability=0.92,
                candidates=[dict(disposition='scored', modelInputRGBSHA256='deadbeef')],
            ),
        )
        row = tp.compare_frame_pair('c1', swift_rec, py_rec)
        self.assertTrue(row['inputHashMatch'])
        self.assertTrue(row['eligibleCountMatch'])
        self.assertTrue(row['winnerMatch'])
        self.assertEqual(row['detections']['matched'], 1)
        self.assertEqual(row['pythonCropHashesPresent'], 1)

        py_miss = dict(py_rec, focusBox=None)
        row_miss = tp.compare_frame_pair('c1', swift_rec, py_miss)
        self.assertFalse(row_miss['winnerMatch'])

    def test_extract_swift_case_comparative_armb_v2_and_pair_match(self):
        swift_doc = {
            'status': 'success',
            'inputSHA256': 'hash123',
            'runtime': {
                'detector': {'treeSHA256': 'det-sha'},
                'result': {
                    'elements': [
                        {
                            'id': 'e1',
                            'elementType': 'imageView',
                            'confidence': 0.91,
                            'boundingBoxPixels': {'x': 10.0, 'y': 20.0, 'width': 40.0, 'height': 30.0},
                            'state': {'isFocused': False},
                        },
                        {
                            'id': 'e2',
                            'elementType': 'listRow',
                            'confidence': 0.88,
                            'boundingBoxPixels': {'x': 100.0, 'y': 200.0, 'width': 300.0, 'height': 80.0},
                            'state': {'isFocused': True},
                        },
                    ],
                    'focusExecution': {
                        'policy': 'comparative-armb-v2',
                        'threshold': 0.28,
                        'candidates': [
                            {'observationID': 'e1', 'disposition': 'unsupportedRole'},
                            {
                                'observationID': 'e2',
                                'disposition': 'scored',
                                'isFocused': True,
                                'probability': 0.995,
                            },
                        ],
                    },
                    'timings': {'totalMs': 25.0},
                },
            },
        }
        swift_rec = tp.extract_swift_case(swift_doc)
        self.assertEqual(swift_rec['inputSHA256'], 'hash123')
        self.assertEqual(swift_rec['eligibleCount'], 1)
        self.assertEqual(swift_rec['scoredCount'], 1)
        self.assertEqual(swift_rec['unsupportedRoleCount'], 1)
        self.assertEqual(swift_rec['focusBox'], [100.0, 200.0, 300.0, 80.0])
        self.assertAlmostEqual(swift_rec['maxProbability'], 0.995, places=6)

        py_rec = {
            'imageSHA256': 'hash123',
            'detections': [
                {'cls': 'imageView', 'box': [10.0, 20.0, 40.0, 30.0], 'score': 0.91},
                {'cls': 'listRow', 'box': [100.0, 200.0, 300.0, 80.0], 'score': 0.88},
            ],
            'focusBox': [100.0, 200.0, 300.0, 80.0],
            'focusExecution': {
                'eligibleCount': 1,
                'scoredCount': 1,
                'unsupportedRoleCount': 1,
                'cropRejectedCount': 0,
                'failedCount': 0,
                'maxProbability': 0.995,
                'candidates': [{'disposition': 'scored', 'probability': 0.995}],
            },
        }
        row = tp.compare_frame_pair('c-armb', swift_rec, py_rec)
        self.assertTrue(row['inputHashMatch'])
        self.assertTrue(row['eligibleCountMatch'])
        self.assertTrue(row['winnerMatch'])
        self.assertEqual(row['detections']['matched'], 2)
        self.assertAlmostEqual(row['maxProbDiff'], 0.0, places=6)


if __name__ == '__main__':
    unittest.main()
