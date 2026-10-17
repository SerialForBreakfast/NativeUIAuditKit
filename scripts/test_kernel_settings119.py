"""B405-119: check the frozen T25 kernel settings and their default compatibility."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import research_queue as q
import hcf_templates395 as templates
import outer_ring398 as ring

SOURCE = q.QUEUE / 'jobs/hcf398-outer-ring-proposals/spec.json'


@unittest.skipUnless(SOURCE.is_file(), 'HCF398 queue evidence is not present')
class KernelSettingsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='kernel119-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.spec = q.load(SOURCE)
        self.kernel = q.local_path(q.ROOT, self.spec['template']['inputs']['kernel']['path'])

    def description(self, parameters):
        return dict(version='hcf-template-description-v1', id='kernel-test', owner='Maximum-mini-NUIAK', template='T25',
                    question='Does a fixed kernel relaxation produce proposals on missed frames?',
                    decision='Test only; the job decides nothing about the models.',
                    inputs=self.spec['template']['inputs'], dependencies=[], parameters=parameters)

    def test_default_keeps_old_spec_fields_and_kernel(self):
        new = templates.build(self.description({}))
        self.assertEqual(new['template']['parameters'], {})
        self.assertEqual(new['template']['inputs'], self.spec['template']['inputs'])
        self.assertEqual(ring.kernel_source(self.kernel, 'frozen-v2', self.root), self.kernel)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_short_side_setting_changes_only_short_side_sampling(self):
        path = ring.kernel_source(self.kernel, 'short-side-v1', self.root)
        original, changed = self.kernel.read_text(), path.read_text()
        self.assertIn('let inset = max(1, (hi - lo) / (hi - lo < 48 ? 3 : 5))', changed)
        self.assertIn('outer-ring-v2-short-side-v1', changed)
        self.assertIn('pixels[seed] >= 160', changed)                 # Brightness gate unchanged.
        self.assertIn('support >= 0.65, contrast >= 0.12', changed)    # Support and contrast gates unchanged.
        different = [(a, b) for a, b in zip(original.splitlines(), changed.splitlines()) if a != b]
        self.assertEqual(len(different), 2)
        templates.build(self.description(dict(kernelSettings='short-side-v1')))

    def test_interpolation_setting_changes_only_the_drawing_quality(self):
        path = ring.kernel_source(self.kernel, 'interpolation-high-v1', self.root)
        original, changed = self.kernel.read_text(), path.read_text()
        self.assertIn('context.interpolationQuality = .high', changed)
        self.assertNotIn('context.interpolationQuality = .low', changed)
        for gate in ('pixels[seed] >= 160', 'support >= 0.65, contrast >= 0.12', 'let inset = max(1, (hi - lo) / 5)', '960.0'):
            self.assertIn(gate, changed)
        different = [(a, b) for a, b in zip(original.splitlines(), changed.splitlines()) if a != b]
        self.assertEqual(len(different), 2)
        templates.build(self.description(dict(kernelSettings='interpolation-high-v1')))

    def test_combined_setting_is_exactly_both_changes(self):
        settings = ring.KERNEL_SETTINGS
        combined = {old: new for old, new, _ in settings['interpolation-high-short-side-v1'] if 'version' not in old}
        parts = {old: new for name in ('interpolation-high-v1', 'short-side-v1') for old, new, _ in settings[name] if 'version' not in old}
        self.assertEqual(combined, parts)
        path = ring.kernel_source(self.kernel, 'interpolation-high-short-side-v1', self.root)
        different = [(a, b) for a, b in zip(self.kernel.read_text().splitlines(), path.read_text().splitlines()) if a != b]
        self.assertEqual(len(different), 3)
        templates.build(self.description(dict(kernelSettings='interpolation-high-short-side-v1')))

    def test_inner_setting_is_the_combined_setting_plus_the_inner_search(self):
        settings = ring.KERNEL_SETTINGS
        inner = {old: new for old, new, _ in settings['interpolation-high-short-side-inner-v1'] if 'version' not in old}
        combined = {old: new for old, new, _ in settings['interpolation-high-short-side-v1'] if 'version' not in old}
        self.assertEqual(inner, dict(combined, **{'let inner = (1...band).map': 'let inner = (1...(band + 2)).map'}))
        path = ring.kernel_source(self.kernel, 'interpolation-high-short-side-inner-v1', self.root)
        different = [(a, b) for a, b in zip(self.kernel.read_text().splitlines(), path.read_text().splitlines()) if a != b]
        self.assertEqual(len(different), 4)
        templates.build(self.description(dict(kernelSettings='interpolation-high-short-side-inner-v1')))

    def test_settings_values_are_checked(self):
        templates.build(self.description(dict(kernelSettings='relaxed-v1')))
        with self.assertRaisesRegex(ValueError, 'kernel_settings'):
            templates.build(self.description(dict(kernelSettings='relaxed-v2')))

    def test_relaxed_rewrites_only_the_listed_gates(self):
        path = ring.kernel_source(self.kernel, 'relaxed-v1', self.root)
        self.assertEqual(path.parent, self.root)
        old, new = self.kernel.read_text().splitlines(), path.read_text().splitlines()
        self.assertEqual(len(old), len(new))
        self.assertEqual(sum(a != b for a, b in zip(old, new)), 5)
        self.assertIn('outer-ring-v2-relaxed-v1', path.read_text())
        self.assertEqual(q.load(self.root / 'kernel-settings.json')['settings'], 'relaxed-v1')

    def test_changed_source_is_refused(self):
        changed = self.root / 'source' / self.kernel.name
        changed.parent.mkdir()
        changed.write_text(self.kernel.read_text().replace('pixels[n] >= 160', 'pixels[n] >= 150'))
        out = self.root / 'out'; out.mkdir()
        with self.assertRaisesRegex(ValueError, 'kernel_settings_source_changed'):
            ring.kernel_source(changed, 'relaxed-v1', out)

    def test_relaxed_kernel_compiles_and_scores_hcf398_membership(self):
        job = self.root / 'jobs/kernel-test'
        out = job / 'attempts/1/out'; out.mkdir(parents=True)
        q.save(job / 'spec.json', templates.build(self.description(dict(kernelSettings='relaxed-v1'))))
        with patch.object(ring, 'OUT', out):
            ring.run()
        result = q.load(out / 'comparison.json')
        self.assertEqual(result['method'], 'TTR-outer-ring-v2-proposals-relaxed-v1')
        old = q.load(SOURCE.parent / 'attempts/1/out/raw.json')
        new = q.load(out / 'raw.json')
        self.assertEqual([r['id'] for r in new], [r['id'] for r in old])
        self.assertTrue(all(r['report']['version'] == 'outer-ring-v2-relaxed-v1' for r in new))
        self.assertTrue((out / 'outer-ring').is_file())


if __name__ == '__main__':
    unittest.main()
