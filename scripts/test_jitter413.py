"""JITTER413: seeded box jitter for training crops, T41 fresh-reference scoring, and plan arm fields."""
import base64
import copy
import hashlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
import research_queue as q
import hcf_study371 as study
import box_intervention410 as t41
import backlog_pipeline as pipeline


def fake_invoke(items, image_root=None):
    """Return a deterministic 256x256 crop for each (source, rounded box). Equal inputs give equal pixels."""
    results = []
    for item in items:
        key = item['sha256'] + ':' + ','.join('%.4f' % v for v in item['bounds'])
        color = tuple(hashlib.sha256(key.encode()).digest()[:3])
        stream = io.BytesIO(); Image.new('RGB', (256, 256), color).save(stream, format='PNG')
        results.append(dict(id=item['id'], png=base64.b64encode(stream.getvalue()).decode()))
    return dict(results=results)


class CropJitterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='jitter413-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        images = self.root / 'images'; images.mkdir()
        rows = []
        # 2 train frames with equal pixels and boxes (a repeated source), 1 development frame.
        for ident, role, group, shade in [('a', 'train', 'g-train', 10), ('b', 'train', 'g-train', 10),
                                          ('c', 'development', 'g-dev', 90)]:
            path = images / (ident + '.png'); Image.new('RGB', (64, 48), (shade, shade, shade)).save(path)
            pixels = hashlib.sha256(Image.open(path).convert('RGB').tobytes()).hexdigest()
            rows.append(dict(id=ident, path=str(path), sha256=q.digest(path), decodedSHA256=pixels,
                             boxes={'item-0': [4.5, 6.25, 20, 12], 'item-1': [30, 6, 20, 12]}, focus='item-0',
                             role=role, profile='hcf', group=group, family='f-' + role))
        self.doc = dict(rows=rows, storage={})

    def prepare(self, name, config, doc=None):
        out = self.root / 'jobs' / name / 'out'; out.mkdir(parents=True)
        with patch.object(study, 'OUT', out), patch.object(study, 'dependency', return_value=[doc or self.doc]), \
                patch.object(study, 'load_config', return_value=config), \
                patch.object(study, 'verify_storage', return_value=self.root), \
                patch.object(study, 'progress'), \
                patch('focus_runtime.invoke', side_effect=fake_invoke), \
                patch('focus_runtime.identity', return_value=dict(helperSHA256='test')):
            study.prepare_crops()
        return q.load(out / 'crops.json')

    def config(self, destination, **jitter):
        value = dict(destination=destination, roles=['train', 'development'])
        if jitter:
            value['jitter'] = dict(dict(variants=3, maxSidePixels=2, seed=371), **jitter)
        return value

    @staticmethod
    def fields(rows):
        return [{k: r[k] for k in ('id', 'sha256', 'box', 'label', 'role', 'group')} for r in rows]

    def test_sides_are_fixed_bounded_and_exact(self):
        first = [study.jitter_sides(371, 'key', v, 2) for v in range(8)]
        self.assertEqual(first, [study.jitter_sides(371, 'key', v, 2) for v in range(8)])
        self.assertNotEqual(first[0], study.jitter_sides(372, 'key', 0, 2))
        values = [x for sides in first for x in sides]
        self.assertTrue(all(-2 <= x <= 2 and (x * 64).is_integer() for x in values))
        self.assertEqual(study.jitter_box([10, 20, 30, 40], [1, -2, 0.5, 2]), [9, 22, 31.5, 40])
        with self.assertRaisesRegex(ValueError, 'jitter_empty_box'):
            study.jitter_box([0, 0, 1, 1], [-1, 0, -1, 0])
        for bad, error in [(dict(variants=0, maxSidePixels=2, seed=1), 'jitter_variants'),
                           (dict(variants=2, maxSidePixels=3, seed=1), 'jitter_limit'),
                           (dict(variants=2, maxSidePixels=2), 'jitter_fields')]:
            with self.assertRaisesRegex(ValueError, error): study.jitter_config(bad)

    def test_jitter_is_deterministic_and_keeps_development_rows(self):
        plain = self.prepare('plain', self.config('plain'))
        first = self.prepare('first', self.config('first', variants=3))
        second = self.prepare('second', self.config('second', variants=3))
        self.assertNotIn('jitter', plain)
        self.assertEqual(self.fields(first['rows']), self.fields(second['rows']))
        originals = [r for r in first['rows'] if 'jitter' not in r]
        self.assertEqual(self.fields(originals), self.fields(plain['rows']))
        self.assertEqual(first['frames'], plain['frames'])
        variants = [r for r in first['rows'] if 'jitter' in r]
        # Frame b repeats frame a, so only the 2 unique crops of frame a get 3 variants each.
        self.assertEqual(len(variants), 6); self.assertEqual(first['jitter']['sources'], 2)
        self.assertEqual({r['frame'] for r in variants}, {'a'})
        self.assertTrue(all(r['role'] == 'train' for r in variants))
        for row in variants:
            source = next(r for r in originals if r['id'] == row['jitter']['source'])
            self.assertEqual(row['label'], source['label'])
            self.assertEqual(row['box'], study.jitter_box(source['box'], row['jitter']['sides']))
            self.assertTrue(all(abs(v) <= 2 for v in row['jitter']['sides']))
        self.assertEqual(len({r['sha256'] for r in variants}), 6)

    def test_group_and_pixel_leaks_are_refused(self):
        leak = copy.deepcopy(self.doc); leak['rows'][2]['group'] = 'g-train'
        with self.assertRaisesRegex(ValueError, 'jitter_group_leak'):
            self.prepare('group', self.config('group', variants=2), leak)
        self.assertFalse((self.root / 'group').exists() and any((self.root / 'group').iterdir()))
        pixels = copy.deepcopy(self.doc); pixels['rows'][2]['decodedSHA256'] = pixels['rows'][0]['decodedSHA256']
        with self.assertRaisesRegex(ValueError, 'jitter_pixel_leak'):
            self.prepare('pixels', self.config('pixels', variants=2), pixels)
        with self.assertRaisesRegex(ValueError, 'crop_config_fields'):
            self.prepare('fields', dict(self.config('fields'), scale=2))


class FreshReferenceTests(unittest.TestCase):
    def row(self):
        arm = dict(scores=[.95, .2], boxes=[[10, 20, 30, 40], [60, 20, 30, 40]], outcome='correct')
        return dict(id='frame', group='group', profile='hcf', noFocus=False,
                    arms={k: copy.deepcopy(arm) for k in t41.SOURCES})

    def test_loss_uses_candidate_reference(self):
        truth = [10, 20, 30, 40]
        # The candidate already misses on the unchanged box. A miss after the change is then no loss.
        fresh = t41.fresh_reference(self.row(), 'known-box', truth, [.5, .2])
        self.assertEqual(fresh['arms']['known-box']['outcome'], 'miss')
        self.assertEqual(self.row()['arms']['known-box']['outcome'], 'correct')
        result = t41.compare(fresh, truth, 'known-box', dict(kind='translate', dx=1, dy=0), [.4, .2], ['a', 'b'])
        self.assertFalse(result['loss'])
        kept = t41.fresh_reference(self.row(), 'known-box', truth, [.9, .1])
        lost = t41.compare(kept, truth, 'known-box', dict(kind='translate', dx=1, dy=0), [.4, .1], ['a', 'b'])
        self.assertTrue(lost['loss']); self.assertEqual(lost['target']['cachedScore'], .9)
        # In cache-off mode the 'none' arm reproduces its own fresh reference.
        none = t41.compare(kept, truth, 'known-box', dict(kind='none'), [.9, .1], ['a', 'b'])
        self.assertEqual(t41.summarize([none], 'known-box', dict(kind='none'))['maxCachedScoreDeviation'], 0)
        with self.assertRaisesRegex(ValueError, 'score_count'):
            t41.fresh_reference(self.row(), 'known-box', truth, [.9])

    def test_compiler_accepts_only_the_candidate_input(self):
        import experiment_batch402 as batches
        doc = q.load(q.ROOT / 'Research/Experiments/b405-002-interventions.json')['jobs'][0]
        doc['id'] = 'jitter413-compile'
        doc['inputs']['candidate'] = copy.deepcopy(doc['inputs']['model'])
        self.assertEqual(batches.compile_batch(dict(version='experiment-batch-v1', jobs=[doc]))[0]['id'],
                         'jitter413-compile')
        doc['inputs']['other'] = doc['inputs'].pop('candidate')
        with self.assertRaisesRegex(ValueError, 'template_inputs'):
            batches.compile_batch(dict(version='experiment-batch-v1', jobs=[doc]))


class CacheOffQueueTests(unittest.TestCase):
    """Cache-off T41 through the actual queue. The candidate equals the pinned model, so outcomes must agree."""

    def test_candidate_equal_to_pinned_model_reproduces_cached_outcomes(self):
        import experiment_batch402 as batches
        bundle = q.load(q.ROOT / 'Research/Experiments/backlog405-native-inputs.json')
        tall = [p for p in bundle['pairs'] if 'native404-selection-03/' in p['selection']['report']['path']]
        source = q.load(q.ROOT / 'Research/Experiments/b405-002-interventions.json')['jobs'][0]
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='jitter413-queue-') as folder:
            root = Path(folder); queue = root / 'queue'
            small = root / 'bundle.json'; q.save(small, dict(bundle, pairs=tall))
            docs = []
            for ident, change in [('cache-off-none', dict(kind='none')),
                                  ('cache-off-shift', dict(kind='translate', dx=0, dy=2))]:
                doc = copy.deepcopy(source)
                doc.update(id=ident, dependencies=[], parameters=dict(source='known-box', intervention=change))
                doc['inputs'] = dict(doc['inputs'], bundle=dict(file=q.relative(small)),
                                     candidate=copy.deepcopy(doc['inputs']['model']))
                docs.append(doc)
            batches.register_batch(dict(version='experiment-batch-v1', jobs=docs), queue,
                                   [d['id'] for d in docs], approver='test')
            self.assertEqual(q.run(queue, max_jobs=2, lock=root / 'lock', job_ids=[d['id'] for d in docs]),
                             [('cache-off-none', 'complete'), ('cache-off-shift', 'complete')])
            none, shift = [q.load(queue / 'jobs' / d['id'] / 'attempts/1/out/benchmark_summary.json') for d in docs]
            self.assertEqual(none['reference'], 'candidate-unchanged-box')
            self.assertEqual([r['outcome'] for r in none['rows']], [r['pinnedModelOutcome'] for r in none['rows']])
            self.assertEqual(none['lostPriorSuccesses'], [])
            # The fresh reference equals the cached scores within the T41 tolerance for equal weights.
            for row in shift['rows']:
                self.assertEqual(row['cachedOutcome'], row['pinnedModelOutcome'])


class PlanArmTests(unittest.TestCase):
    def test_arm_dependencies_and_training_merge(self):
        dep = dict(job='producer-a', specSHA256='0' * 64, outputs=['crops.json'])
        record = dict(id='B405-999', hypothesis='Jitter keeps decisions under box errors.',
                      comparison='Matched control.', plan=dict(
            template='T06', owner='Maximum-mini-NUIAK', jobPrefix='jitter-test', rule='manual', control='control',
            question='Does seeded crop jitter keep T41 successes within 2 px on the 74 retained frames?',
            decision='Accept only with zero losses within 2 px.',
            outcomes=dict(supported='a', contradicted='b', inconclusive='c'),
            shared=dict(training=dict(epochs=30, resume='restart')),
            arms=[dict(id='control', inputs={}, dependencies=[dep], training=dict(experimentLogRunId='X')),
                  dict(id='jitter', inputs={})]))
        control, jitter = pipeline.descriptions(record)
        self.assertEqual(control['dependencies'], [dep]); self.assertEqual(jitter['dependencies'], [])
        self.assertEqual(control['training'], dict(epochs=30, resume='restart', experimentLogRunId='X'))
        self.assertEqual(jitter['training'], dict(epochs=30, resume='restart'))
        # Review reads list outputs of native templates without failure.
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='jitter413-review-') as folder:
            job = Path(folder) / 'jobs/x'; out = job / 'attempts/1/out'; out.mkdir(parents=True)
            q.save(out / 'sources.json', [dict(path='a', sha256='0' * 64)])
            q.save(out / 'summary.json', dict(gains=['f'], lostPriorSuccesses=[]))
            listed = [dict(path=n, bytes=(out / n).stat().st_size) for n in ('sources.json', 'summary.json')]
            with patch.object(pipeline.q, 'state', return_value=('complete', [])), \
                    patch.object(pipeline.q, 'attempts_of', return_value=[job / 'attempts/1']), \
                    patch.object(pipeline.q, 'outputs_intact', return_value=True):
                q.save(job / 'attempts/1/result.json', dict(status='complete', outputs=listed, wallSeconds=1))
                row = pipeline.arm_row(Path(folder), 'arm', 'x')
            self.assertEqual(row['gains'], ['f'])
        record['plan']['arms'][1]['other'] = 1
        with self.assertRaisesRegex(ValueError, 'plan_arm_fields'):
            pipeline.descriptions(record)


if __name__ == '__main__':
    unittest.main()
