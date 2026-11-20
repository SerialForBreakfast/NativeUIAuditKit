"""Tests for RESET604 recipe generation (`fixture_recipes604.py`), including composition v5 gating."""
import json
import tempfile
import unittest
from pathlib import Path

import fixture_composition_qual604 as fcq
import fixture_recipes604 as fr
import research_queue as q


class FixtureRecipes604Tests(unittest.TestCase):
    def test_composition_mutation_preserves_ids_and_gates_on_qualification(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='recipes604-') as tmp:
            root = Path(tmp)
            qual_dir = root / 'qual'
            (qual_dir / 'recipes').mkdir(parents=True)
            sample = {
                'schema_version': 1,
                'archetype': 'grid_matrix',
                'theme': 'dark',
                'seed': 10,
                'appearance': {
                    'version': 1,
                    'composition': {
                        'version': 5,
                        'background': {'colors': [100, 200], 'locations': [0.0, 1.0]},
                        'definitions': {
                            'card': {'kind': 'composite_card', 'width': 400, 'height': 300},
                            'txt': {'kind': 'text', 'width': 500, 'height': 60},
                        },
                        'contents': {'c0': {'title': 'Old Title', 'seed': 1}, 't0': {'title': 'Synopsis'}},
                        'styles': {'s0': {'focus': {'version': 1, 'kind': 'custom', 'custom': {'scale': 1.05, 'borderWidth': 2, 'shadowOpacity': 0.4, 'borderRGB': 255}}}},
                        'regions': [{
                            'id': 'shelf_r', 'axis': 'shelf', 'frame': [80, 80, 1600, 400], 'gap': 30, 'content_insets': [0, 0, 0, 0],
                            'items': [{'id': 'c0', 'component': 'card', 'content': 'c0'}, {'id': 't0', 'component': 'txt', 'content': 't0'}],
                        }],
                    },
                },
                'capture_selection': {'version': 1, 'target_element_ids': ['c0'], 'max_targets': 1},
            }
            (qual_dir / 'recipes/passed.json').write_text(json.dumps(sample))
            (qual_dir / 'recipes/failed.json').write_text(json.dumps(sample))
            manifest_path = qual_dir / 'composition-qual-report.json'
            manifest_path.write_text(json.dumps({'rows': [
                {'recipe': 'passed.json', 'passed': True},
                {'recipe': 'failed.json', 'passed': False},
            ]}))

            out_dir = root / 'out'
            index = fr.build(out_dir, plain=1, canvas=1, seed=604, composition=2, composition_manifests=[manifest_path])
            comp_rows = [r for r in index['rows'] if r['family'].startswith('composition:')]
            self.assertGreaterEqual(len(comp_rows), 1)
            for row in comp_rows:
                self.assertEqual(row['origin'], str(qual_dir / 'recipes/passed.json'))
                gen = json.loads((out_dir / row['recipe']).read_text())
                exp = fcq.expected_from_composition(gen, 3840, 2160)
                self.assertEqual(list(exp['visibleControls']), ['c0'])
                self.assertEqual(exp['staticTextIDs'], ['t0'])
                self.assertEqual(gen['theme'], 'dark')  # source theme is preserved

            # A passed recipe with any `scroll: true` is not a qualified source (no scroll-offset truth).
            scrolled = json.loads(json.dumps(sample))
            scrolled['appearance']['composition']['regions'][0]['scroll'] = True
            scroll_dir = root / 'qual-scroll'
            (scroll_dir / 'recipes').mkdir(parents=True)
            (scroll_dir / 'recipes/scrolled.json').write_text(json.dumps(scrolled))
            scroll_manifest = scroll_dir / 'composition-qual-report.json'
            scroll_manifest.write_text(json.dumps({'rows': [{'recipe': 'scrolled.json', 'passed': True}]}))
            self.assertEqual(fr._load_qualified_compositions([scroll_manifest]), [])
            with self.assertRaises(Exception):
                fr.build(root / 'out-scroll', plain=0, canvas=1, seed=604, composition=1, composition_manifests=[scroll_manifest])


if __name__ == '__main__':
    unittest.main()
