"""Offline tests for scripts/h3_focused_membership666.py."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h3_focused_membership666 as h


def row(ident, state, role='train', sha='a'):
    return dict(id=ident, focusState=state, role=role, image=dict(sha256=sha + ident),
                controls=[dict(bounds=[0, 0, 10, 10], **{'class': 'cell'}, id='e0')])


def focus_row(ident, state, boxes, sha='a'):
    controls = [dict(bounds=[0, 0, 10, 10], **{'class': 'cell'}, id='e0')]
    controls += [dict(bounds=b, **{'class': 'focused'}, id=f'f{i}') for i, b in enumerate(boxes)]
    return dict(id=ident, focusState=state, image=dict(sha256=sha + ident), controls=controls)


class FocusedRowsTests(unittest.TestCase):
    def test_adds_focus_box_and_drops_unknown(self):
        d1 = dict(rows=[row('r1', 'focused'), row('r2', 'no_focus'), row('r3', 'unknown'), row('r4', 'ambiguous', 'calibration')])
        focus = dict(rows=[focus_row('r1', 'focused', [[0, 0, 10, 10]]), focus_row('r2', 'no_focus', [])])
        rows, dropped = h.focused_rows(d1, focus)
        self.assertEqual([r['id'] for r in rows], ['r1', 'r2'])
        self.assertEqual([c['class'] for c in rows[0]['controls']], ['cell', 'focused'])
        self.assertEqual([c['class'] for c in rows[1]['controls']], ['cell'])
        self.assertEqual(dict(dropped), {'train:unknown': 1, 'calibration:ambiguous': 1})
        self.assertEqual(len(d1['rows'][0]['controls']), 1)  # source row unchanged

    def test_rejects_hash_mismatch(self):
        d1 = dict(rows=[row('r1', 'focused')])
        focus = dict(rows=[focus_row('r1', 'focused', [[0, 0, 10, 10]], sha='b')])
        with self.assertRaises(ValueError):
            h.focused_rows(d1, focus)

    def test_rejects_two_focus_boxes(self):
        d1 = dict(rows=[row('r1', 'focused')])
        focus = dict(rows=[focus_row('r1', 'focused', [[0, 0, 10, 10], [5, 5, 10, 10]])])
        with self.assertRaises(ValueError):
            h.focused_rows(d1, focus)

    def test_rejects_state_mismatch(self):
        d1 = dict(rows=[row('r1', 'no_focus')])
        focus = dict(rows=[focus_row('r1', 'focused', [[0, 0, 10, 10]])])
        with self.assertRaises(ValueError):
            h.focused_rows(d1, focus)


if __name__ == '__main__':
    unittest.main()
