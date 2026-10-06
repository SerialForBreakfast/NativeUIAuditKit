import unittest
from copy import deepcopy
from artwork204_campaign import recipes
from export_artwork204 import select

class ExportTests(unittest.TestCase):
    def test_exact_train_selection(self):
        rows=select(recipes());self.assertEqual(len(rows),60)
        self.assertEqual({r['family'] for r in rows},{f'artwork204-family-r1-s{i}' for i in range(5)})
    def test_partial_reordered_relabelled_rejected(self):
        rows=recipes()
        changed=deepcopy(rows);changed[-1]['dataRole']='train'
        for bad in [rows[:-1],list(reversed(rows)),rows[:-1]+rows[:1],changed]:
            with self.assertRaises(ValueError):select(bad)

if __name__=='__main__':unittest.main()
