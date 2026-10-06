"""Generated fixtures only; no prior reports, network or model dependencies."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import generator_asset_plan as g

ROOT = Path(__file__).resolve().parents[1]


def resource(name='a', payload=b'art', **changes):
    item = dict(id=name, kind='artwork', sha256=hashlib.sha256(payload).hexdigest(),
                bytes=len(payload), source='fixture', sourceRevision='test-v1',
                ancestryGroups=[name], dataRole='development', rightsStatus='verified',
                rightsEvidence=['fixture-rights'], reviewStatus='verified', reviewEvidence=['fixture-review'])
    item.update(changes)
    return item


def inventory(*items):
    return dict(schemaVersion='generator-resource-inventory-v1', resources=list(items))


class AssetPlanTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / '.build/debug-output'
        parent.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=parent, prefix='asset-plan-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.empty = dict(schemaVersion='asset-cache-index-v1', files=[])

    def run_plan(self, *items, cache=None):
        return g.plan(inventory(*items), cache or self.empty, self.root)

    def cache(self, payload=b'art'):
        (self.root / 'art.bin').write_bytes(payload)
        return dict(schemaVersion='asset-cache-index-v1', files=[
            dict(sha256=hashlib.sha256(b'art').hexdigest(), path='art.bin')])

    def test_verified_cache_no_requests_or_admission(self):
        p = self.run_plan(resource(), cache=self.cache())
        self.assertTrue(p['resources'][0]['renderEligible'])
        self.assertEqual(p['missingArtworkBatches'], [])
        self.assertEqual(p['resources'][0]['trainingAdmission'], 'not_assessed')

    def test_missing_deduplicated_and_order_independent(self):
        a, b = resource('a'), resource('b')
        p = self.run_plan(a, b)
        self.assertEqual(p, self.run_plan(b, a))
        self.assertEqual(p['summary']['missingEligibleObjects'], 1)
        self.assertEqual(p['missingArtworkBatches'][0]['files'][0]['ids'], ['a', 'b'])

    def test_batch_limits(self):
        rows = [resource(str(i), str(i).encode(), bytes=g.MAX_OBJECT) for i in range(5)]
        p = self.run_plan(*rows)
        self.assertEqual([b['bytes'] for b in p['missingArtworkBatches']],
                         [g.MAX_BATCH, g.MAX_BATCH, g.MAX_OBJECT])

    def test_pending_and_rejected_never_requested(self):
        for state in ('pending', 'rejected'):
            for field in ('rightsStatus', 'reviewStatus'):
                with self.subTest(state=state, field=field):
                    p = self.run_plan(resource(**{field: state}))
                    self.assertEqual(p['missingArtworkBatches'], [])
                    self.assertFalse(p['resources'][0]['renderEligible'])

    def test_non_artwork_routed_not_rendered(self):
        for kind in ('mockup', 'native_capture', 'ui_source'):
            p = self.run_plan(resource(kind=kind))
            self.assertEqual(p['missingArtworkBatches'], [])
            self.assertTrue(p['resources'][0]['blockers'])

    def test_unassigned_not_requested(self):
        self.assertEqual(self.run_plan(resource(dataRole='unassigned'))['missingArtworkBatches'], [])

    def test_same_hash_role_conflict(self):
        with self.assertRaisesRegex(ValueError, 'cross_role'):
            self.run_plan(resource('a', dataRole='train'), resource('b', dataRole='test'))

    def test_transitive_unassigned_bridge_conflict(self):
        a = resource('a', b'a', dataRole='train', ancestryGroups=['one'])
        b = resource('b', b'b', dataRole='unassigned', rightsStatus='pending', ancestryGroups=['one', 'two'])
        c = resource('c', b'c', dataRole='test', ancestryGroups=['two'])
        with self.assertRaisesRegex(ValueError, 'cross_role'):
            self.run_plan(a, b, c)

    def test_conflicting_sizes(self):
        with self.assertRaisesRegex(ValueError, 'size_conflict'):
            self.run_plan(resource('a'), resource('b', bytes=4))

    def test_duplicate_ids(self):
        with self.assertRaisesRegex(ValueError, 'duplicate_id'):
            self.run_plan(resource(), resource())

    def test_alias_cannot_bypass_pending_review(self):
        with self.assertRaisesRegex(ValueError, 'alias_assessment_conflict'):
            self.run_plan(resource('a'), resource('b', reviewStatus='pending'))

    def test_missing_required_field(self):
        row = resource()
        del row['sourceRevision']
        with self.assertRaisesRegex(ValueError, 'fields'):
            self.run_plan(row)

    def test_output_boundary_and_symlink(self):
        with self.assertRaisesRegex(ValueError, 'output_boundary'):
            g.output({}, ROOT.parent/'outside.json')
        dest = self.root/'original.json'
        dest.write_text('preserve')
        (self.root/'linked.json').symlink_to(dest)
        with self.assertRaisesRegex(ValueError, 'output_boundary'):
            g.output({}, self.root/'linked.json')
        self.assertEqual(dest.read_text(), 'preserve')

    def test_invalid_fields_and_statuses(self):
        for changes in (dict(bytes=True), dict(bytes=g.MAX_OBJECT+1), dict(bytes=0),
                        dict(sha256='bad'), dict(rightsStatus='approved'), dict(rightsEvidence=[]),
                        dict(ancestryGroups=[]), dict(dataRole='final'), dict(command='execute')):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.run_plan(resource(**changes))

    def test_unsupported_versions(self):
        for which in ('inventory', 'cache'):
            inv, cache = inventory(resource()), copy.deepcopy(self.empty)
            (inv if which == 'inventory' else cache)['schemaVersion'] = 'next'
            with self.assertRaises(ValueError):
                g.plan(inv, cache, self.root)

    def test_changed_cache_rejected_even_if_review_pending(self):
        with self.assertRaisesRegex(ValueError, 'hash_mismatch'):
            self.run_plan(resource(reviewStatus='pending'), cache=self.cache(b'bad'))

    def test_missing_cache_file_is_not_silently_requested(self):
        cache = self.cache()
        (self.root / 'art.bin').unlink()
        with self.assertRaises(ValueError):
            self.run_plan(resource(), cache=cache)

    def test_bad_cache_paths(self):
        for path in ('../art.bin', '/art.bin', './art.bin', 'a/../art.bin'):
            cache = self.cache()
            cache['files'][0]['path'] = path
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.run_plan(resource(), cache=cache)

    def test_symlink_and_directory_rejected(self):
        cache = self.cache()
        (self.root/'link').symlink_to(self.root/'art.bin')
        for path in ('link', '.'):
            cache['files'][0]['path'] = path
            with self.assertRaises(ValueError):
                self.run_plan(resource(), cache=cache)

    def test_cache_unknown_or_duplicate(self):
        cache = self.cache()
        cache['files'].append(cache['files'][0])
        with self.assertRaises(ValueError):
            self.run_plan(resource(), cache=cache)
        with self.assertRaises(ValueError):
            self.run_plan(resource(payload=b'other'), cache=self.cache())

    def cli(self, *args):
        return subprocess.run([sys.executable, '-B', str(ROOT/'scripts/generator_asset_plan.py'), *args],
                              text=True, capture_output=True)

    def test_real_cli_readonly_and_exclusive_output(self):
        inv, cache = self.root/'inventory.json', self.root/'cache.json'
        inv.write_text(json.dumps(inventory(resource())))
        cache.write_text(json.dumps(self.empty))
        args = ['plan', '--inventory', str(inv), '--cache-index', str(cache), '--cache-root', str(self.root)]
        before = sorted(self.root.iterdir())
        p = self.cli(*args)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(sorted(self.root.iterdir()), before)
        self.assertEqual(json.loads(p.stdout)['summary']['requestedBytes'], 3)
        dest = self.root/'plan.json'
        self.assertEqual(self.cli(*args, '--output', str(dest)).returncode, 0)
        original = dest.read_bytes()
        self.assertEqual(self.cli(*args, '--output', str(dest)).returncode, 2)
        self.assertEqual(dest.read_bytes(), original)

    def test_cli_rejects_duplicate_keys(self):
        p = self.root/'invalid.json'
        p.write_text('{"schemaVersion":"a","schemaVersion":"b"}')
        self.assertEqual(self.cli('normalize-image201', '--inventory', str(p)).returncode, 2)

    def test_adapter_retains_record_and_pending(self):
        r = dict(stable_id='image201/a', sha256=resource()['sha256'], bytes=3,
                 split='development_only;all pilot variants excluded from future independent final evaluation',
                 model_revisions={'model': 'a'*40}, derivative_group='family', licence='terms',
                 provenance='receipt', review={'provisional_decision':'candidate_for_review'})
        inv = g.normalize_image201(dict(schema_version=1, assets=[r]))
        self.assertEqual(inv['resources'][0]['sourceRecord'], r)
        p = g.plan(inv, self.cache(), self.root)
        self.assertEqual(p['summary']['verifiedCacheObjects'], 1)
        self.assertEqual(p['summary']['renderEligible'], 0)
        r['split'] = 'train'
        with self.assertRaises(ValueError):
            g.normalize_image201(dict(schema_version=1, assets=[r]))

    def test_metadata_symlink_rejected(self):
        p = self.root/'producer.json'
        p.write_text(json.dumps(dict(schema_version=1, assets=[])))
        link = self.root/'link.json'
        link.symlink_to(p)
        result = self.cli('normalize-image201', '--inventory', str(link))
        self.assertEqual(result.returncode, 2)
        self.assertIn('metadata_file_type', result.stderr)

    def test_adapter_cli(self):
        p = self.root/'producer.json'
        p.write_text(json.dumps(dict(schema_version=1, assets=[])))
        result = self.cli('normalize-image201', '--inventory', str(p))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['resources'], [])


if __name__ == '__main__':
    unittest.main()
