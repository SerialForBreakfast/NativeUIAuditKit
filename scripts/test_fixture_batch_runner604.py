"""Tests for RESET604 T2.1 bounded Fixture batch runner and bisect isolation."""
import json
import tempfile
import unittest
from pathlib import Path

import fixture_batch_runner604 as runner
import research_queue as q


class FixtureBatchRunnerTests(unittest.TestCase):
    def test_parse_cli_json_skips_log_prefix(self):
        stdout = '[TVTR-LIFECYCLE] hello\n{"success": true, "data": {"ok": 1}}\n'
        parsed = runner.parse_cli_json(stdout)
        self.assertTrue(parsed['success'])
        self.assertEqual(parsed['data']['ok'], 1)

    def test_bisect_isolates_failing_recipe_and_preserves_valid_rows(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='fixrunner-') as tmp:
            root = Path(tmp)
            recipes_root = root / 'recipes'
            recipes_root.mkdir()
            for r in ('r0.json', 'r_bad.json', 'r2.json'):
                q.save(recipes_root / r, dict(recipe=r))
            work_root = root / 'work'
            work_root.mkdir()
            project = root / 'proj'
            project.mkdir()
            dst_chunk = root / 'out/c0000'
            row_lookup = {
                'r0.json': dict(family='plain:media_shelf', role='training'),
                'r_bad.json': dict(family='plain:grid_matrix', role='training'),
                'r2.json': dict(family='plain:hero_carousel', role='held-out'),
            }

            def fake_aatv(aatv, proj, rec_stage, out_dir, url, udid):
                staged = sorted(p.name for p in rec_stage.glob('*.json'))
                if 'r_bad.json' in staged:
                    return False, 'sceneNotSettled'
                abs_out = Path(out_dir)
                abs_out.mkdir(parents=True, exist_ok=True)
                manifest = []
                for name in staged:
                    stem = Path(name).stem
                    fpng = abs_out / f'{stem}_focused.png'
                    fpng.write_bytes(b'png-' + stem.encode())
                    mjson = abs_out / f'{stem}_metadata.json'
                    q.save(mjson, dict(
                        is_settled=True, focused_png=fpng.name,
                        focused_sha256=q.digest(fpng),
                    ))
                    manifest.append(dict(
                        id=stem, split='training',
                        metadata=dict(metadataPath=mjson.name, recipeFile=name),
                    ))
                q.save(abs_out / 'manifest.json', manifest)
                return True, dict(success=True)

            acc, rej = runner.run_chunk_with_bisect(
                ['r0.json', 'r_bad.json', 'r2.json'], recipes_root, work_root, dst_chunk, row_lookup,
                'aatv', project, 'http://127.0.0.1:8080', 'UDID', runner=fake_aatv,
            )
            self.assertEqual(len(acc), 2)
            self.assertEqual(len(rej), 1)
            self.assertEqual(rej[0]['recipe'], 'r_bad.json')
            by_id = {x['id']: x for x in acc}
            self.assertEqual(by_id['r0']['split'], 'training')
            self.assertEqual(by_id['r2']['split'], 'test')

    def test_run_batches_skips_excluded_families(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='fixskip-') as tmp:
            root = Path(tmp)
            recipes_dir = root / 'recipes'
            recipes_dir.mkdir()
            rows = []
            for idx, (rname, fam) in enumerate([('r0.json', 'plain:media_shelf'), ('r1.json', 'plain:grid_matrix')]):
                q.save(recipes_dir / rname, dict(recipe=rname))
                rows.append(dict(recipe=rname, family=fam, role='training', index=idx))
            q.save(recipes_dir / 'index.json', dict(rows=rows))
            out_dir = root / 'out'
            project = root / 'proj'
            project.mkdir()

            def fake_run_chunk(recipes, *args, **kwargs):
                return [dict(id=r) for r in recipes], []

            orig = runner.run_chunk_with_bisect
            runner.run_chunk_with_bisect = fake_run_chunk
            try:
                res = runner.run_batches(
                    recipes_dir=recipes_dir, out_dir=out_dir, batch_size=15, start=0, count=2,
                    skip_families=['plain:grid_matrix'], project=project,
                )
            finally:
                runner.run_chunk_with_bisect = orig
            self.assertEqual(res['newAcceptedRows'], 1)
            state = q.load(out_dir / 'runner-state.json')
            keys = list(state['completedChunks'])
            self.assertEqual(len(keys), 1)
            self.assertTrue(keys[0].startswith('c0000-'))
            self.assertEqual(state['completedChunks'][keys[0]]['recipes'], 1)
            self.assertEqual(state['completedChunks'][keys[0]]['skippedRecipes'], ['r1.json'])

            # Re-running with different skip_families produces a new content-addressed chunk key
            runner.run_chunk_with_bisect = fake_run_chunk
            try:
                res2 = runner.run_batches(
                    recipes_dir=recipes_dir, out_dir=out_dir, batch_size=15, start=0, count=2,
                    skip_families=[], project=project,
                )
            finally:
                runner.run_chunk_with_bisect = orig
            self.assertEqual(res2['newAcceptedRows'], 2)
            state2 = q.load(out_dir / 'runner-state.json')
            self.assertEqual(len(state2['completedChunks']), 2)


if __name__ == '__main__':
    unittest.main()
