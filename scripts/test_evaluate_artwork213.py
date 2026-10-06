import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import evaluate_artwork213 as runner
from test_eval_run013 import Run013Tests
from eval_phase6a import filter_degenerate_predictions
from prediction_artifact import build_artifact, make_result


class PartitionTests(unittest.TestCase):
    def rows(self):
        return [dict(id=r['id'], family=r['family'], role=r['dataRole']) for r in runner.recipes()]

    def test_roles(self):
        groups = runner.partitions(self.rows())
        self.assertEqual({k:len(v) for k,v in groups.items()}, dict(native=36, validation=24, diagnostic=12))
        self.assertFalse({r['id'] for r in groups['validation']} & {r['id'] for r in groups['diagnostic']})

    def test_partial_duplicate_role_family_reject(self):
        rows = self.rows()
        for bad in (rows[:-1], rows[:-1]+rows[:1], list(reversed(rows))):
            with self.assertRaises(ValueError): runner.partitions(bad)
        for field, value in [('role', 'train'), ('family', 'unrelated')]:
            bad = copy.deepcopy(rows); bad[-1][field] = value
            with self.assertRaises(ValueError): runner.partitions(bad)


class EntryTests(unittest.TestCase):
    def setUp(self):
        # Reuse existing image/label fixture; exercise the actual scorer, not a replacement metric.
        self.fixture = Run013Tests(); self.fixture.setUp()
        self.work = self.fixture.work
        self.requests = {k:self.fixture.request for k in ('native','validation','diagnostic','fit','page','combined')}
        settings = dict(runner.evaluation.PREDICTION_SETTINGS, postprocessing=runner.DEGENERATE_POLICY)
        image = self.fixture.request.images[0]
        detections, audit = filter_degenerate_predictions(image, 41, [])
        row = make_result(image, 41, detections=detections); row['postprocessingAudit'] = audit
        self.doc = build_artifact(self.fixture.request, self.work/'model.pt', runner.evaluation.CATEGORY_MAP, '1.0', settings, [row])
        for key in ('native','fit','page','combined'):
            (self.work/(key+'.json')).write_text(json.dumps(self.doc))

    def tearDown(self): self.fixture.tearDown()

    def invoke(self, out):
        with patch.object(runner, 'checked_requests', return_value=self.requests):
            return runner.score(self.work, self.work, self.work/'model.pt', out)

    def test_actual_score_and_collision(self):
        out = self.work/'report.json'
        self.assertEqual(set(self.invoke(out)), {'validation','diagnostic','fit','page','combined'})
        report = json.loads(out.read_text())
        self.assertFalse(report['modelGatePassed'])
        self.assertIsNone(report['reports']['validation']['perClass'][1]['ap50'])
        with self.assertRaises(ValueError): self.invoke(out)

    def test_changed_checkpoint_missing_predictions_and_settings(self):
        for mutate in (lambda d:d['model'].update(checkpointSHA256='0'*64),
                       lambda d:d.update(results=[]),
                       lambda d:d['settings'].update(imgsz=1280)):
            bad = copy.deepcopy(self.doc); mutate(bad)
            (self.work/'native.json').write_text(json.dumps(bad))
            with self.assertRaises(ValueError): self.invoke(self.work/'rejected.json')
            self.assertFalse((self.work/'rejected.json').exists())

    def test_pair_real_scorer_zero_deltas_and_same_checkpoint_rejection(self):
        second=self.work/'second';second.mkdir()
        cp=second/'model.pt';cp.write_bytes(b'second synthetic checkpoint')
        doc=copy.deepcopy(self.doc);doc['model']['checkpointSHA256']=runner.sha(cp)
        for key in ('native','fit','page','combined'):(second/(key+'.json')).write_text(json.dumps(doc))
        with patch.object(runner,'checked_requests',return_value=self.requests):
            output=self.work/'paired.json'
            runner.pair(self.work,self.work,self.work/'model.pt',second,cp,output)
            result=json.loads(output.read_text())
            self.assertFalse(result['modelGatePassed'])
            self.assertTrue(all(v in (None,0) for rows in result['deltas'].values() for r in rows for v in r['delta'].values()))
            with self.assertRaises(ValueError):runner.pair(self.work,self.work,cp,second,cp,self.work/'invalid.json')
        broken=copy.deepcopy(result['treatment']);broken['inputs']['native']='changed'
        with self.assertRaises(ValueError):runner.deltas(result['control'],broken)
        broken=copy.deepcopy(result['treatment']);broken['reports']['fit']['perClass'][0]['support']+=1
        with self.assertRaises(ValueError):runner.deltas(result['control'],broken)

    def test_delta_keeps_regressions_and_unsupported_metrics(self):
        with patch.object(runner,'checked_requests',return_value=self.requests):
            self.invoke(self.work/'base-report.json')
        a=json.loads((self.work/'base-report.json').read_text());b=copy.deepcopy(a)
        b['reports']['fit']['perClass'][0]['fp']+=1
        rows=runner.deltas(a,b)['fit']
        self.assertTrue(rows[0]['operatingRegression']);self.assertEqual(rows[0]['delta']['fp'],1)
        self.assertIsNone(rows[1]['delta']['ap50'])

    def test_explicit_split_layout(self):
        for key in ('validation','diagnostic'):(self.work/(key+'.json')).write_text(json.dumps(self.doc))
        result=runner.scored(self.requests,self.work,self.work/'model.pt',native_layout='split')
        self.assertEqual(result['reports']['validation']['imageCount'],1)
        self.assertEqual(set(result['predictions']),{'validation','diagnostic','fit','page','combined'})
        (self.work/'diagnostic.json').unlink()
        with self.assertRaises(OSError):runner.scored(self.requests,self.work,self.work/'model.pt',native_layout='split')


if __name__ == '__main__': unittest.main()
