"""Offline tests for scripts/nested_filter666.py."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nested_filter666 as nf


def det(box, cls='cell'):
    return dict(box=box, cls=cls)


FOCUSABLE = lambda d: d['cls'] in ('cell', 'button', 'toggle')


class NestedFilterTests(unittest.TestCase):
    def test_removes_chevron_inside_row(self):
        row, chevron = det([2120, 467, 1560, 132]), det([3575, 513, 42, 40], 'toggle')
        kept, removed = nf.drop_nested([row, chevron], FOCUSABLE)
        self.assertEqual(kept, [row])
        self.assertEqual(removed, [chevron])

    def test_keeps_siblings_and_partial_overlap(self):
        a, b = det([0, 0, 100, 50]), det([0, 60, 100, 50])
        c = det([90, 0, 40, 40], 'button')  # 25 % inside a
        kept, removed = nf.drop_nested([a, b, c], FOCUSABLE)
        self.assertEqual(kept, [a, b, c])
        self.assertEqual(removed, [])

    def test_keeps_similar_size_duplicate(self):
        a, b = det([0, 0, 100, 50]), det([2, 2, 96, 46])  # area ratio < 2
        kept, _ = nf.drop_nested([a, b], FOCUSABLE)
        self.assertEqual(kept, [a, b])

    def test_non_focusable_container_does_not_remove(self):
        bar, button = det([0, 0, 3840, 290], 'bar'), det([100, 100, 200, 80], 'button')
        kept, removed = nf.drop_nested([bar, button], FOCUSABLE)
        self.assertEqual(kept, [bar, button])
        self.assertEqual(removed, [])

    def test_non_focusable_inside_is_kept(self):
        row, pic = det([0, 0, 1000, 200]), det([10, 10, 50, 50], 'picture')
        kept, _ = nf.drop_nested([row, pic], FOCUSABLE)
        self.assertEqual(kept, [row, pic])


if __name__ == '__main__':
    unittest.main()
