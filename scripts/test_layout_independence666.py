"""Offline tests for scripts/layout_independence666.py (synthetic drafts only)."""
import json
import tempfile
import unittest
from pathlib import Path
import layout_independence666 as li

GRID = [[100 + 700*i, 900, 600, 500] for i in range(5)] + [[100, 100, 600, 120]]


def draft(folder, name, app, screen, boxes, focus='focused', size=(3840, 2160)):
    d = dict(version='tvbench-ax-draft-v1', bundleIdentifier=app, screenID=screen, width=size[0], height=size[1],
             imageSHA256=name, focus=dict(state=focus), objects=[dict(id=f'ax-{i}', box=b, **{'class': 'cell'}) for i, b in enumerate(boxes)])
    (folder/f'{name}.draft.json').write_text(json.dumps(d))


class LayoutIndependenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_propose(self, exclude=(), reference=()):
        screens, skipped = li.load_drafts([str(self.dir/'*.draft.json')], set(exclude))
        return li.propose(screens, li.load_reference(list(reference))), skipped

    def test_sweep_frames_of_one_capture_count_once(self):
        draft(self.dir, 'a-00', 'org.x', 'cap-home-00', GRID)
        draft(self.dir, 'a-01-down', 'org.x', 'cap-home-01-down', GRID[1:])
        (layouts, _), _ = self.run_propose()
        self.assertEqual(len(layouts), 1); self.assertEqual(len(layouts[0]['frames']), 2)

    def test_same_geometry_with_other_content_merges(self):
        draft(self.dir, 'a-00', 'org.x', 'cap-foryou-00', GRID)
        draft(self.dir, 'b-00', 'org.x', 'cap-local-00', [[x+8, y, w, h] for x, y, w, h in GRID])
        (layouts, _), _ = self.run_propose()
        self.assertEqual(len(layouts), 1)

    def test_different_geometry_and_other_apps_stay_apart(self):
        draft(self.dir, 'a-00', 'org.x', 'cap-home-00', GRID)
        draft(self.dir, 'b-00', 'org.x', 'cap-detail-00', [[200, 1500, 400, 100], [700, 1500, 400, 100]])
        draft(self.dir, 'c-00', 'org.y', 'cap-home-00', GRID)
        (layouts, _), _ = self.run_propose()
        self.assertEqual(len(layouts), 3)

    def test_reference_match_is_familiar_and_resolution_independent(self):
        ref = self.dir/'ref'; ref.mkdir()
        draft(ref, 'old-00', 'org.jellyfin.swiftfin', 'old-00', [[x//2, y//2, w//2, h//2] for x, y, w, h in GRID], size=(1920, 1080))
        draft(self.dir, 'a-00', 'org.jellyfin.swiftfin', 'cap-home-00', GRID)
        (layouts, _), _ = self.run_propose(reference=[str(ref/'*.draft.json')])
        self.assertTrue(layouts[0]['familiar']); self.assertEqual(layouts[0]['credit'], 'none_familiar')

    def test_drafts_in_subfolders_are_found(self):
        sub = self.dir/'run'/'frames'; sub.mkdir(parents=True)
        draft(sub, 'a-00', 'org.x', 'cap-home-00', GRID)
        screens, _ = li.load_drafts([str(self.dir/'**'/'*.draft.json')], set())
        self.assertEqual(len(screens), 1)

    def test_roles_and_exclusions(self):
        draft(self.dir, 'a-00', 'com.jordankoch.NewsTV', 'cap-home-00', GRID)
        draft(self.dir, 'b-00', 'org.jellyfin.swiftfin', 'cap-bad-00', GRID)
        draft(self.dir, 'c-00', 'org.jellyfin.swiftfin', 'cap-empty-00', [])
        (layouts, _), skipped = self.run_propose(exclude=['cap-bad'])
        self.assertEqual([l['credit'] for l in layouts], ['none_training'])
        self.assertEqual({s['reason'] for s in skipped}, {'excluded_by_capture_report', 'no_objects'})

    def test_borderline_pair_is_reported_not_merged(self):
        draft(self.dir, 'a-00', 'org.x', 'cap-a-00', GRID)
        draft(self.dir, 'b-00', 'org.x', 'cap-b-00', GRID[:3] + [[100, 1700, 300, 100], [500, 1700, 300, 100], [900, 1700, 300, 100]])
        (layouts, pairs), _ = self.run_propose()
        self.assertEqual(len(layouts), 2); self.assertEqual(len(pairs), 1)


if __name__ == '__main__':
    unittest.main()
