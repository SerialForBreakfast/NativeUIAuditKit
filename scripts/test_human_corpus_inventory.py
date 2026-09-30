"""Offline inventory grouping and revision selection; no model/runtime use."""
import unittest
import human_corpus_inventory as inventory


class InventoryTests(unittest.TestCase):
    def revision(self, path, date, kind='human', batch='batch', confirmed=True):
        return dict(reference={'path': path}, batch={'path': batch},
                    reviewer=dict(kind=kind, completedAt=date, confirmedBatch=confirmed))

    def test_latest_excludes_test_and_preserves_other_batches(self):
        rows = [self.revision('old', '2026-09-28T00:00:00Z'),
                self.revision('new', '2026-09-29T00:00:00Z'),
                self.revision('test', '2026-09-30T00:00:00Z', kind='software-test'),
                self.revision('other', '2026-09-27T00:00:00Z', batch='other')]
        self.assertEqual(inventory.latest_revisions(rows), ['new', 'other'])
        self.assertEqual(inventory.latest_revisions(list(reversed(rows))), ['new', 'other'])

    def test_equivalent_timestamps_are_ambiguous(self):
        with self.assertRaises(ValueError):
            inventory.latest_revisions([self.revision('a', '2026-09-29T00:00:00Z'),
                self.revision('b', '2026-09-28T17:00:00-07:00')])

    def test_unconfirmed_is_not_silently_admitted(self):
        with self.assertRaises(ValueError):
            inventory.latest_revisions([self.revision('a', '2026-09-29T00:00:00Z', confirmed=False)])

    def test_components_are_transitive_and_order_independent(self):
        rows = [dict(id='a', sessionID='one', family='a', pixelSHA256='a'),
                dict(id='b', sessionID='one', family='b', pixelSHA256='b'),
                dict(id='c', sessionID='two', family='b', pixelSHA256='c'),
                dict(id='d', sessionID='three', family='d', pixelSHA256='c'),
                dict(id='e', sessionID='unknown', family='unknown', pixelSHA256='e'),
                dict(id='f', sessionID='unknown', family='unknown', pixelSHA256='f')]
        expected = [['a', 'b', 'c', 'd'], ['e'], ['f']]
        self.assertEqual(inventory.components(rows), expected)
        self.assertEqual(inventory.components(list(reversed(rows))), expected)

    def test_metadata_does_not_follow_protected_paths(self):
        self.assertEqual(inventory.metadata_hashes({'path':'/missing/protected.png',
            'samples':[{'pixelSHA256':'abc', 'nested':{'sha256':'def'}}]}), {'abc','def'})

    def test_empty_inputs(self):
        self.assertEqual(inventory.latest_revisions([]), [])
        self.assertEqual(inventory.components([]), [])
        self.assertEqual(inventory.metadata_hashes(None), set())


if __name__ == '__main__':
    unittest.main()
