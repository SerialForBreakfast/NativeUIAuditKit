"""Tests for RESET604 T2.3 / T2.4 TTR sidecar ingest and 12-role membership builder."""
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image

import detector_training419 as t
import research_queue as q
import ttr_detector_ingest604 as ingest
from roles559 import ROLES
from template_inputs398 import pin


class Ingest604Tests(unittest.TestCase):
    def test_fixture_batch_respects_held_out_and_12_roles(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='ingest604-fix-') as tmp:
            root = Path(tmp)
            for name in ('f0.png', 'u0.png', 'f1.png'):
                Image.new('RGB', (200, 100)).save(root / name)
            q.save(root / 'm0.json', dict(
                is_settled=True, scene_width=200, scene_height=100,
                recipe=dict(archetype='media_shelf', seed=1),
                focused_element_id='c0', focused_png='f0.png', unfocused_png='u0.png',
                focused_sha256=q.digest(root / 'f0.png'), unfocused_sha256=q.digest(root / 'u0.png'),
                focused_scene=dict(elements=[
                    dict(element_id='c0', taxonomy_class='collectionItem', is_focused=True, is_hidden=False, pixel_bounds=[10, 10, 50, 40]),
                    dict(element_id='lbl', taxonomy_class='label', is_focused=False, is_hidden=False, pixel_bounds=[10, 55, 50, 15]),
                ]),
                baseline_scene=dict(elements=[
                    dict(element_id='c0', taxonomy_class='collectionItem', is_focused=False, is_hidden=False, pixel_bounds=[10, 10, 50, 40]),
                ]),
            ))
            q.save(root / 'm1.json', dict(
                is_settled=True, scene_width=200, scene_height=100,
                recipe=dict(archetype='hero_carousel', seed=2),
                focused_element_id='c1', focused_png='f1.png',
                focused_sha256=q.digest(root / 'f1.png'),
                focused_scene=dict(elements=[
                    dict(element_id='c1', taxonomy_class='pageControl', is_focused=True, is_hidden=False, pixel_bounds=[20, 80, 40, 10]),
                ]),
            ))
            q.save(root / 'manifest.json', [
                dict(id='s0', split='training', metadata=dict(metadataPath='m0.json')),
                dict(id='s1', split='training', metadata=dict(metadataPath='m1.json')),
            ])
            rows, held = ingest.ingest_fixture_batch(root, include_focused=True)

            # TTR advisory splits never set data roles (Joe, 2026-11-12).
            adv = q.load(root / 'manifest.json')
            adv[0]['split'] = 'calibration'
            q.save(root / 'manifest.json', adv, replace=True)
            adv_rows, _ = ingest.ingest_fixture_batch(root, include_focused=True)
            self.assertEqual({r['role'] for r in adv_rows}, {'train'})
            adv[0]['split'] = 'training'
            q.save(root / 'manifest.json', adv, replace=True)
            self.assertEqual(len(rows), 2)
            self.assertEqual(len(held), 1)
            self.assertEqual(held[0]['role'], 'held-out')
            self.assertFalse(held[0]['trainingEligible'])
            # 'label' dropped per D3; 'focused' included on f0 but not u0
            foc_row = next(r for r in rows if r['id'].endswith('-foc'))
            unf_row = next(r for r in rows if r['id'].endswith('-unf'))
            self.assertFalse(foc_row['labelsComplete'])
            self.assertEqual(foc_row['focusState'], 'focused')
            self.assertEqual(unf_row['focusState'], 'no_focus')
            self.assertEqual([c['class'] for c in foc_row['controls']], ['cell', 'focused'])
            self.assertEqual([c['class'] for c in unf_row['controls']], ['cell'])

            # Reconciliation gate: only 's0' focused frame passed; every mode excludes the rest.
            rows_q, _ = ingest.ingest_fixture_batch(root, include_focused=True, qualified={'s0': {'foc'}})
            self.assertNotIn('reconciliationFailed', next(r for r in rows_q if r['id'].endswith('s0-foc')))
            self.assertTrue(next(r for r in rows_q if r['id'].endswith('s0-unf'))['reconciliationFailed'])
            for mode in ('d1', 'f1-arma', 'focus-supervision'):
                kept, excluded = ingest._filter_rows_for_mode(rows_q, mode)
                self.assertNotIn('ttr604-s0-unf', {r['id'] for r in kept})
                self.assertIn('composition_reconciliation_failed', {e['reason'] for e in excluded})

    def test_generator_focus_state_and_mode_filtering(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='ingest604-gen-') as tmp:
            root = Path(tmp)
            for sub in ('train', 'validation'):
                (root / sub).mkdir()
            for idx, els in enumerate([
                # 0: single focused
                [dict(id='btn_0_focused', elementType='primaryButton', boundsPixels=dict(x=10, y=10, width=40, height=20))],
                # 1: two focused -> ambiguous
                [
                    dict(id='row_0_focused', elementType='listRow', boundsPixels=dict(x=10, y=10, width=80, height=30)),
                    dict(id='seg_1_focused', elementType='segmentedControl', boundsPixels=dict(x=20, y=12, width=40, height=20)),
                ],
                # 2: zero focused -> unknown
                [dict(id='btn_0', elementType='primaryButton', boundsPixels=dict(x=10, y=10, width=40, height=20))],
            ]):
                img = root / 'train' / f'img_{idx:06d}.png'
                Image.new('RGB', (200, 100)).save(img)
                q.save(img.with_suffix('.json'), dict(
                    schemaVersion=1,
                    image=dict(width=200, height=100),
                    imageSHA256=q.digest(img),
                    elements=els,
                ))
            gen_rows = ingest.ingest_generator(root, include_focused=True)
            by_id = {r['id']: r for r in gen_rows}
            self.assertEqual(by_id['gen604-tra-img_000000']['focusState'], 'focused')
            self.assertEqual([c['class'] for c in by_id['gen604-tra-img_000000']['controls']], ['button', 'focused'])
            self.assertEqual(by_id['gen604-tra-img_000001']['focusState'], 'ambiguous')
            self.assertEqual([c['class'] for c in by_id['gen604-tra-img_000001']['controls']], ['cell', 'segmentedControl'])
            self.assertEqual(by_id['gen604-tra-img_000002']['focusState'], 'unknown')

            partial_row = dict(id='part-1', sourceRole='fixture-batch', labelsComplete=False, focusState='focused', controls=[dict(id='c1', bounds=[0, 0, 10, 10], **{'class': 'cell'})])
            d1_kept, d1_ex = ingest._filter_rows_for_mode(gen_rows + [partial_row], 'd1')
            self.assertEqual(len(d1_kept), 3)
            self.assertEqual([e['id'] for e in d1_ex], ['part-1'])

            f1_kept, f1_ex = ingest._filter_rows_for_mode(gen_rows + [partial_row], 'f1-arma')
            self.assertEqual([r['id'] for r in f1_kept], ['gen604-tra-img_000000'])
            self.assertEqual(len(f1_ex), 3)

            foc_kept, foc_ex = ingest._filter_rows_for_mode(gen_rows + [partial_row], 'focus-supervision')
            self.assertEqual({r['id'] for r in foc_kept}, {'gen604-tra-img_000000', 'part-1'})
            self.assertEqual(len(foc_ex), 2)

    def test_audit_rejects_tvbench_overlap_and_group_leak(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='ingest604-aud-') as tmp:
            root = Path(tmp)
            p1, p2 = root / 'a.png', root / 'b.png'
            Image.new('RGB', (100, 100)).save(p1)
            Image.new('RGB', (100, 100)).save(p2)
            tvbench_manifest = root / 'tvbench.json'
            q.save(tvbench_manifest, dict(cases=[dict(image=pin(p1))]))
            row1 = dict(id='r1', group='g1', role='train', sourceRole='test', trainingEligible=True, labelsComplete=True,
                        width=100, height=100, image=pin(p1), controls=[dict(id='c1', bounds=[5, 5, 20, 20], **{'class': 'button'})])
            row2 = dict(id='r2', group='g1', role='calibration', sourceRole='test', trainingEligible=False, labelsComplete=True,
                        width=100, height=100, image=pin(p2), controls=[dict(id='c2', bounds=[5, 5, 20, 20], **{'class': 'cell'})])
            with self.assertRaisesRegex(ValueError, 'ttr_ingest_tvbench_overlap'):
                ingest.audit_membership(dict(rows=[row1]), tvbench_paths=[tvbench_manifest])
            with self.assertRaisesRegex(ValueError, 'ttr_ingest_group_leak'):
                ingest.audit_membership(dict(rows=[dict(row1, image=pin(p2)), row2]))

    def test_built_membership_prepares_cleanly_for_training(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='ingest604-prep-') as tmp:
            root = Path(tmp)
            doc = q.load(q.ROOT / 'reports/work/RESET604/membership/v2-d1/membership.json')
            self.assertEqual(doc['names'], ROLES)
            self.assertEqual(len(doc['names']), 12)
            self.assertTrue(all(r.get('labelsComplete') for r in doc['rows']))
            f1 = q.load(q.ROOT / 'reports/work/RESET604/membership/v2-f1-arma/membership.json')
            self.assertTrue(all(r.get('labelsComplete') and r.get('focusState') in ('focused', 'no_focus') for r in f1['rows']))
            train_sample = [r for r in doc['rows'] if r['role'] == 'train'][:4]
            cal_sample = [r for r in doc['rows'] if r['role'] == 'calibration'][:2]
            prog_sample = [r for r in doc['rows'] if r['sourceRole'] == 'artparity595-programme'][:4]
            sub = dict(doc, rows=train_sample + cal_sample + prog_sample)
            _, counts = t.prepare(sub, root)
            self.assertEqual(counts['train'], 8)
            self.assertEqual(counts['calibration'], 2)

    def test_role_specific_box_selection_and_occlusion_exclusion(self):
        # Cell keeps whole pixel_bounds (poster + title), standalone picture prefers rendered_body_geometry,
        # occluded controls and static labels are excluded.
        elements = [
            dict(
                element_id='card_0', taxonomy_class='collectionItem', is_focused=True, is_hidden=False,
                pixel_bounds=[10, 10, 200, 180],
                rendered_body_geometry=dict(visible_pixel_bounds=[10, 10, 200, 120]),
            ),
            dict(
                element_id='hero_img', taxonomy_class='imageView', is_focused=False, is_hidden=False,
                pixel_bounds=[250, 10, 200, 180],
                rendered_body_geometry=dict(visible_pixel_bounds=[260, 20, 180, 140]),
            ),
            dict(
                element_id='synopsis', taxonomy_class='label', is_focused=False, is_hidden=False,
                pixel_bounds=[10, 200, 400, 60],
            ),
            dict(
                element_id='under_modal', taxonomy_class='primaryButton', is_focused=False, is_occluded=True,
                pixel_bounds=[50, 50, 120, 60],
            ),
        ]
        controls, focus_state = ingest._fixture_controls(
            elements, 600, 300, focus_id='card_0', include_focused=True, is_focus_frame=True, has_paired_focus=True
        )
        self.assertEqual(focus_state, 'focused')
        by_cls = {c['class']: c['bounds'] for c in controls}
        self.assertEqual(set(by_cls), {'cell', 'picture', 'focused'})
        self.assertEqual(by_cls['cell'], [10, 10, 200, 180])
        self.assertEqual(by_cls['picture'], [260, 20, 180, 140])
        self.assertEqual(by_cls['focused'], [10, 10, 200, 180])


if __name__ == '__main__':
    unittest.main()
