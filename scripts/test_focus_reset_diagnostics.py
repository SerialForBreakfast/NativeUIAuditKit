import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image
import focus_reset_diagnostics as d
import test_focus_representative_experiment as fixtures


class ResetTests(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.SelectionTests(); fixture.setUp()
        self.allrows = fixture.rows
        self.selection = fixture.selection
        self.allpred = fixture.pred
        for i, row in enumerate(self.allrows):
            row['bounds'] = [i % 2 * 20, 0, 10, 10]
        self.rows = self.allrows[18:]
        self.pred = self.allpred[18:]

    def score(self):
        return d.frame_scores(self.rows, self.pred, self.selection['framePolicy'])

    def test_perfect_and_chance_accounting(self):
        r = self.score()
        self.assertEqual((r['supported'], r['excluded'], r['top1ExpectedCorrect']), (13, 1, 13))
        self.assertEqual(r['randomExpectedCorrect'], 6.5)
        self.assertEqual(r['runtimeStyleCounts'], {'correct': 13})
        self.assertEqual(r['cropAUROC'], 1)

    def test_strict_and_runtime_are_distinct(self):
        self.pred[0]['probability'] = .90
        r = self.score()
        self.assertEqual(r['strictThresholdCounts']['multiple_focus'], 1)
        self.assertEqual(r['runtimeStyleCounts'], {'correct': 13})

    def test_low_confidence_and_ties_are_explicit(self):
        self.pred[0]['probability'] = .95
        r = self.score()
        self.assertEqual(r['runtimeStyleCounts']['tied_unavailable'], 1)
        self.assertEqual(r['top1ExpectedCorrect'], 12.5)
        for p in self.pred: p['probability'] = .1
        r = self.score()
        self.assertEqual(r['runtimeStyleCounts'], {'no_focus': 13})
        self.assertEqual(r['top1ExpectedCorrect'], 6.5)

    def test_unknown_empty_or_nonunique_truth(self):
        for f in self.selection['framePolicy']['frames']: f['coverage'] = 'unknown'
        self.assertIsNone(self.score()['top1ExpectedCorrect'])
        self.assertEqual(self.score()['supported'], 0)
        r = d.frame_scores([], [], dict(populations=dict(candidate=[], auxiliary=[], unresolved=[]), frames=[]))
        self.assertIsNone(r['cropAUROC'])
        self.assertIsNone(r['randomExpectedCorrect'])

    def test_invalid_scores_membership_and_roles(self):
        for value in (True, float('nan'), float('inf'), -1, 2):
            original = self.pred[0]['probability']; self.pred[0]['probability'] = value
            with self.assertRaises(ValueError): self.score()
            self.pred[0]['probability'] = original
        for pred in (self.pred[:-1], self.pred + [self.pred[0]], list(reversed(self.pred))):
            with self.assertRaises(ValueError):d.frame_scores(self.rows, pred, self.selection['framePolicy'])
        self.rows[0]['use'] = 'final-challenge'
        with self.assertRaisesRegex(ValueError, 'unsupported_role'):self.score()

    def test_deterministic_and_nonmutating(self):
        before = copy.deepcopy((self.rows, self.pred, self.selection))
        self.assertEqual(self.score(), self.score())
        self.assertEqual(before, (self.rows, self.pred, self.selection))

    def test_real_cli_and_negative_artifacts(self):
        directory = d.ROOT/'.build/debug-output/reset-tests'; directory.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=directory) as tmp:
            root = Path(tmp); image = root/'source.png'; crop = root/'crop.png'
            Image.new('RGB', (320, 256), 'gray').save(image)
            Image.new('RGB', (256, 256), 'gray').save(crop)
            for i, row in enumerate(self.rows):
                unique_crop = root/f'crop-{i}.png'
                Image.new('RGB', (256, 256), (i, 40, 50)).save(unique_crop)
                row.update(image=d.offline.ref(image), crop=d.offline.ref(unique_crop),
                           pixelSHA256=d.pixel_digest(d.ROOT, d.offline.ref(unique_crop)))
            protocol = dict(version='focus-sampler-experiment-v1', samples=self.allrows,
                            configuration=dict(epochs=1), selection=self.selection)
            protocol['protocolSHA256'] = d.digest(protocol)
            v = dict(predictions=self.allpred, **d.selection_metrics(self.allpred, self.allrows, self.selection))
            result = dict(protocolSHA256=protocol['protocolSHA256'], selection=self.selection,
                          status='completed', initial=v, history=[dict(epoch=1, validation=v)])
            pp, rp = root/'protocol.json', root/'result.json'
            d.offline.write(pp, protocol); d.offline.write(rp, result)
            original = [p.read_bytes() for p in (pp, rp, image, crop)]
            process = subprocess.run([sys.executable, str(d.ROOT/'scripts/focus_reset_diagnostics.py'),
                '--protocol', str(pp), '--result', str(rp), '--output', str(root/'out')],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(original, [p.read_bytes() for p in (pp, rp, image, crop)])
            report = d.offline.read(root/'out/report.json')
            self.assertEqual(report['verifiedPredictions'], 92)
            self.assertFalse(report['modelExecution'])
            result.pop('selection');d.offline.write(rp,result)
            self.assertEqual(d.load(pp,rp)[1]['status'],'completed')
            with self.assertRaisesRegex(ValueError, 'output_exists'):d.run(pp, rp, root/'out')
            image.write_bytes(b'broken')
            with self.assertRaisesRegex(ValueError, 'changed_hash'):d.run(pp, rp, root/'bad-image')
            result['history'].append(result['history'][0]);d.offline.write(rp,result)
            with self.assertRaisesRegex(ValueError,'incomplete_or_duplicate_epochs'):d.load(pp,rp)
            protocol['samples'][0]['use']='final-challenge'
            protocol.pop('protocolSHA256');protocol['protocolSHA256']=d.digest(protocol);d.offline.write(pp,protocol)
            with self.assertRaisesRegex(ValueError,'protected_or_unknown_role'):d.load(pp,rp)


if __name__ == '__main__': unittest.main()
