"""Tests for `ax_snapshot_drafts666.draft_from_snapshot`."""
import unittest

import ax_snapshot_drafts666 as ax


def node(kind, bounds, parent=-1, focused=False, label='', depth=0):
    return dict(identifier='', label=label, kind=kind, bounds=bounds, focused=focused, enabled=True, selected=False, depth=depth, parent=parent)


def snap(nodes, focus='focused', settled=True):
    return dict(version='tvos-ax-snapshot-v1', pngSHA256='0' * 64, pixelDimensions=[3840, 2160], viewportPoints=[0, 0, 1920, 1080],
                bundleIdentifier='com.example.App', screenID='s', settled=settled, focusState=focus, inputsSent=0, nodes=nodes)


class AXDraftTests(unittest.TestCase):
    def test_targets_owned_content_scale_and_focus_owner(self):
        nodes = [node(2, [0, 0, 1920, 1080]),                      # application
                 node(75, [100, 100, 300, 200], parent=0),         # cell
                 node(43, [100, 100, 300, 150], parent=1),         # image inside the cell -> owned
                 node(48, [100, 260, 300, 40], parent=1, focused=True, label='Title'),  # focused text inside the cell
                 node(9, [500, 100, 200, 80], parent=0),           # button
                 node(43, [800, 100, 400, 300], parent=0),         # standalone image -> picture
                 node(48, [800, 500, 400, 40], parent=0, label='Synopsis'),             # free text -> no object
                 node(43, [0, 0, 1920, 1080], parent=0)]           # full-screen backdrop -> no object
        d = ax.draft_from_snapshot(snap(nodes))
        self.assertEqual([(o['class'], o['box']) for o in d['objects']],
                         [('cell', [200, 200, 600, 400]), ('button', [1000, 200, 400, 160]), ('picture', [1600, 200, 800, 600])])
        self.assertEqual(len(d['ownedContent']), 2)
        self.assertEqual((d['focus']['state'], d['focus']['objectId']), ('focused', 'ax-000'))
        self.assertTrue(all(o['roleSource'] == 'ax_element_type' for o in d['objects']))
        self.assertFalse(d['complete'])

    def test_control_nested_in_a_cell_is_owned_and_marks_disclosure(self):
        nodes = [node(2, [0, 0, 1920, 1080]), node(75, [1060, 269, 780, 66], parent=0, label='Apps'),
                 node(9, [1778, 282, 28, 40], parent=1, label='chevron'),
                 node(21, [0, 0, 1920, 145], parent=0), node(9, [100, 40, 200, 60], parent=3, label='Back'),
                 node(75, [1060, 1069, 780, 66], parent=0, label='Power Off', focused=True)]
        d = ax.draft_from_snapshot(snap(nodes))
        self.assertEqual([(o['class'], o['axLabel'], o['hasDisclosure'], o['clippedByScreen']) for o in d['objects']],
                         [('cell', 'Apps', True, False), ('bar', '', False, False), ('button', 'Back', False, False), ('cell', 'Power Off', False, True)])
        self.assertEqual(d['objects'][2]['parentObject'], d['objects'][1]['id'])

    def test_missing_or_unsettled_focus_is_unknown_never_no_focus(self):
        nodes = [node(2, [0, 0, 1920, 1080]), node(9, [500, 100, 200, 80], parent=0)]
        self.assertEqual(ax.draft_from_snapshot(snap(nodes, focus='none_observed'))['focus']['state'], 'unknown')
        nodes[1]['focused'] = True
        self.assertEqual(ax.draft_from_snapshot(snap(nodes, settled=False))['focus']['state'], 'unknown')
        text_focus = [node(2, [0, 0, 1920, 1080]), node(48, [10, 10, 100, 40], parent=0, focused=True)]
        self.assertEqual(ax.draft_from_snapshot(snap(text_focus))['focus']['reason'], 'focused_element_is_not_a_draft_target')


if __name__ == '__main__':
    unittest.main()
