"""Offline tests for scripts/combine_ax_manifests666.py."""
import tempfile
import unittest
from pathlib import Path
import research_queue as q
import combine_ax_manifests666 as c

BASE = dict(version='tvbench-v2', classes=['button'], baseline=dict(confidence=0.25, matchingIoU=0.5),
            split='development', sealed=False, trainingEligible=False)


class CombineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=q.ROOT/'.build'); self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def manifest(self, name, cases, **extra):
        out = []
        for cid, pixel, layout in cases:
            label = self.dir/f'{cid}.json'; q.save(label, dict(objects=[]), replace=True)
            case = dict(id=cid, app='org.x', pixelSHA256=pixel, labels=dict(path=q.relative(label), sha256=q.digest(label)))
            if layout:
                case['independentLayoutId'] = layout
            out.append(case)
        path = self.dir/name; q.save(path, dict(BASE, apps=[dict(id='org.x', sealed=False)], cases=out, **extra)); return path

    def test_combines_and_counts_layouts(self):
        a = self.manifest('a.json', [('a1', 'p1', 'L1'), ('a2', 'p2', 'L1')]); b = self.manifest('b.json', [('b1', 'p3', 'L2')])
        r = c.combine([a, b], self.dir/'out.json')
        self.assertEqual((r['cases'], r['layouts']), (3, 2))

    def test_refuses_duplicates_missing_ids_and_sealed_sources(self):
        a = self.manifest('a.json', [('a1', 'p1', 'L1')])
        for bad, reason in ((self.manifest('d.json', [('a1', 'p9', 'L2')]), 'duplicate'),
                            (self.manifest('m.json', [('m1', 'p8', None)]), 'missing_layout'),
                            (self.manifest('s.json', [('s1', 'p7', 'L3')], ), 'sealed')):
            if reason == 'sealed':
                doc = q.load(bad); doc['sealed'] = True; q.save(bad, doc, replace=True); reason = 'source_mismatch'
            with self.assertRaisesRegex(ValueError, reason):
                c.combine([a, bad], self.dir/f'out-{reason}.json')


if __name__ == '__main__':
    unittest.main()
