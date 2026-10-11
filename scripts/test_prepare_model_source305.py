"""Check metadata edits without model loading."""
import pickle
import unittest
from unittest.mock import patch
import prepare_model_source305 as p


class PrivacyTests(unittest.TestCase):
    def test_paths_only(self):
        source = {'path': '/Users/example/repo/weights.pt', 'root': '/Users/example/repo', 'shape': [1, 2, 3]}
        data, count = p.sanitize(pickle.dumps(source, protocol=2), '/Users/example/repo')
        self.assertEqual(count, 2)
        self.assertEqual(pickle.loads(data), {'path': 'weights.pt', 'root': '.', 'shape': [1, 2, 3]})

    def test_other_private_path_rejected(self):
        with self.assertRaisesRegex(ValueError, 'private_path'):
            p.sanitize(pickle.dumps('/Users/another/file', protocol=2), '/Users/example/repo')

    def test_new_protocol_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unsupported_protocol'):
            p.sanitize(pickle.dumps({}, protocol=4), '/Users/example/repo')

    def test_trailing_data_rejected(self):
        with self.assertRaisesRegex(ValueError, 'pickle_tail'):
            p.sanitize(pickle.dumps({}, protocol=2) + b'extra', '/Users/example/repo')

    def test_collision(self):
        with patch.object(p, 'OUT', p.ROOT), self.assertRaisesRegex(ValueError, 'output_exists'):
            p.prepare()


if __name__ == '__main__':
    unittest.main()
