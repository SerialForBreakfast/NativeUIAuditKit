"""Test retained outcome comparisons without model or capture execution."""
import copy
import unittest

from hcf_failure_review import compare


class ReviewTests(unittest.TestCase):
    def documents(self):
        rows = [dict(id=str(i), sha256=str(i)*64, group='scene', role='development',
                     profile='hcf', family='cards', outcome='miss') for i in range(2)]
        documents = {'a': dict(rows=rows), 'b': dict(rows=copy.deepcopy(rows))}
        documents['b']['rows'][0]['outcome'] = 'correct'
        return documents

    def test_counts_and_decision(self):
        result = compare(self.documents())
        self.assertEqual(result['sharedMisses'], ['1'])
        self.assertEqual(len(result['disagreements']), 1)
        self.assertEqual(result['groups'], 1)
        self.assertFalse(result['modelAccepted'])

    def test_changed_pixels_fail(self):
        documents = self.documents()
        documents['b']['rows'][0]['sha256'] = 'f'*64
        with self.assertRaisesRegex(ValueError, 'case_identity_mismatch:sha256'):
            compare(documents)

    def test_duplicate_and_role_fail(self):
        for defect in ('duplicate', 'role'):
            documents = self.documents()
            if defect == 'duplicate':
                documents['a']['rows'].append(documents['a']['rows'][0])
            else:
                documents['a']['rows'][0]['role'] = 'audit'
            with self.assertRaises(ValueError):
                compare(documents)


if __name__ == '__main__':
    unittest.main()
