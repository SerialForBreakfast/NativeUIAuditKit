"""Catalog checks and isolated cached-analysis qualification; no live dispatch."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import research_queue as q
import experiment_backlog as backlog
import experiment_batch402 as batches
from template_inputs398 import pin
from cached_selection405 import analyze


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((q.ROOT/'Research/Experiments/backlog405.json').read_text())

    def test_real_catalog(self):
        open_rows = sum(r['reconciliation']['disposition'] == 'unresolved' for r in self.catalog['experiments'])
        self.assertEqual(backlog.validate(self.catalog)['outstandingScientificTasks'], open_rows)

    def test_duplicate_and_cycle(self):
        broken = copy.deepcopy(self.catalog); broken['experiments'].append(broken['experiments'][0])
        with self.assertRaisesRegex(ValueError, 'duplicate_id'): backlog.validate(broken)
        broken = copy.deepcopy(self.catalog); broken['experiments'][0]['dependencies'] = ['B405-002']
        with self.assertRaisesRegex(ValueError, 'dependency_cycle'): backlog.validate(broken)

    def test_required_evidence_and_decision(self):
        for field, value, error in [('sourceEvidence', ['../outside'], 'unsafe_source'),
                                    ('outcomes', {'supported':'yes'}, 'decision_branches'),
                                    ('requirements', [], 'requirement_missing')]:
            broken = copy.deepcopy(self.catalog)
            row = next(r for r in broken['experiments'] if r['reconciliation']['disposition'] == 'unresolved')
            row[field] = value
            with self.assertRaisesRegex(ValueError, error): backlog.validate(broken)

    def test_status_only_in_tasks(self):
        self.catalog['experiments'][0]['status'] = 'ready'
        with self.assertRaisesRegex(ValueError, 'duplicate_status_store'): backlog.validate(self.catalog)

    def test_answered_not_pending(self):
        result = backlog.validate(self.catalog)
        self.assertEqual(result['records']-result['answered'], result['outstandingScientificTasks'])

    def test_tasks_membership_and_readiness(self):
        tasks = (q.ROOT/'Tasks.md').read_text()
        # BACKLOG410: confirmed results close records, so the open count follows the catalog.
        self.assertEqual(backlog.report(self.catalog, tasks)['outstandingScientificTasks'],
                         sum(r['reconciliation']['disposition'] == 'unresolved' for r in self.catalog['experiments']))
        with self.assertRaisesRegex(ValueError, 'tasks_catalog_membership'):
            backlog.report(self.catalog, '')
        # An unplanned record still needs explicit job bindings before it can claim readiness.
        row = next(r for r in self.catalog['experiments'] if r['id'] == 'B405-004')
        self.assertNotIn('plan', row)
        row['existingJobs'] = []
        tasks = tasks.replace('| B405-004 | research-host-NUIAK | Needs data |',
                              '| B405-004 | research-host-NUIAK | Ready to register |')
        with self.assertRaisesRegex(ValueError, 'readiness_without_job_binding'):
            backlog.report(self.catalog, tasks)

    def test_baseline_and_cost(self):
        self.catalog['experiments'][0]['baseline'] = ''
        with self.assertRaisesRegex(ValueError, 'baseline_missing'):
            backlog.validate(self.catalog)
        self.catalog['experiments'][0]['baseline'] = 'Retained baseline'
        self.catalog['experiments'][0]['cost']['reviewMinutes'] = [20, 10]
        with self.assertRaisesRegex(ValueError, 'cost_range'):
            backlog.validate(self.catalog)

    def test_engineering_links_and_ownership(self):
        engineering = json.loads((q.ROOT/'Research/Experiments/engineering405.json').read_text())
        tasks = (q.ROOT/'Tasks.md').read_text()
        self.assertEqual(backlog.validate_engineering(engineering, self.catalog, tasks)['engineeringTasks'],
                         len(engineering['tasks']))
        engineering['tasks'][0]['unlocks'] = ['B405-999']
        with self.assertRaisesRegex(ValueError, 'engineering_science_link'):
            backlog.validate_engineering(engineering, self.catalog, tasks)


def pair(ident='frame', score=.9, overlap=.8, no_focus=False):
    arm = dict(scores=[score], boxes=[[0, 0, 10, 10]], outcome='false-selection' if no_focus else 'correct' if score >= .85 else 'miss')
    row = dict(id=ident, group='group', profile='hcf', noFocus=no_focus,
               arms={key:copy.deepcopy(arm) for key in ('known-box', 'raw-proposal', 'mapped-proposal')})
    geometry = dict(rows=[dict(id=ident, group='group', profile='hcf', noFocus=no_focus,
                              rawBestIoU=None if no_focus else overlap, mappedBestIoU=None if no_focus else overlap)])
    return dict(rows=[row], threshold=.85), geometry


class CachedTests(unittest.TestCase):
    def test_success_and_no_focus(self):
        report = analyze([pair(), pair('negative', no_focus=True)])
        self.assertFalse(report['modelAccepted'])
        self.assertEqual(report['slices']['hcf']['arms']['raw-proposal']['outcomes']['false-selection'], 1)

    def test_loss_is_retained(self):
        selection, geometry = pair()
        selection['rows'][0]['arms']['mapped-proposal'].update(scores=[.2], outcome='miss')
        self.assertEqual(analyze([(selection, geometry)])['slices']['hcf']['losses'], ['frame'])

    def test_missing_overlap_and_score(self):
        selection, geometry = pair(score=.2, overlap=.1)
        self.assertEqual(analyze([(selection, geometry)])['rows'][0]['arms']['raw-proposal']['reason'], 'insufficient_overlap')
        geometry['rows'][0]['rawBestIoU'] = .8
        self.assertEqual(analyze([(selection, geometry)])['rows'][0]['arms']['raw-proposal']['reason'], 'below_threshold')

    def test_invalid_identity_scores_and_duplicate(self):
        with self.assertRaisesRegex(ValueError, 'duplicate_frame'): analyze([pair(), pair()])
        for field, value, error in [('id', 'changed', 'row_identity'), ('rawBestIoU', float('nan'), 'invalid_overlap')]:
            a,b=pair();b['rows'][0][field]=value
            with self.assertRaisesRegex(ValueError, error):analyze([(a,b)])
        a,b=pair();a['rows'][0]['arms']['raw-proposal']['scores']=[float('nan')]
        with self.assertRaisesRegex(ValueError, 'invalid_score'):analyze([(a,b)])

    def test_changed_threshold(self):
        a,b=pair();a['threshold']=.7
        with self.assertRaisesRegex(ValueError, 'threshold_changed'):analyze([(a,b)])

    def test_actual_queue_and_second_description(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build', prefix='backlog405-') as folder:
            root=Path(folder);queue=root/'queue'
            def input_ref(name, value):
                attempt=root/name/'attempts/1';out=attempt/'out';out.mkdir(parents=True)
                target=out/'report.json';q.save(target,value)
                receipt=attempt/'result.json'
                q.save(receipt,dict(status='complete',outputs=[dict(path='report.json',sha256=q.digest(target))]))
                return dict(report=pin(target),result=pin(receipt))
            a,b=pair();bundle=root/'bundle.json'
            q.save(bundle,dict(version='cached-selection-inputs-v1',role='development',pairs=[dict(
                selection=input_ref('selected',a),geometry=input_ref('geometry',b))]))
            def desc(ident):
                return dict(version='hcf-template-description-v1',id=ident,owner='test-NUIAK',template='T40',
                    question='Do cached reports preserve outcomes?',decision='Reject identity drift before reporting.',
                    inputs=dict(bundle=dict(file=q.relative(bundle))),parameters={},dependencies=[])
            docs=[desc('cached-first'),desc('cached-second')]
            batch=dict(version='experiment-batch-v1',jobs=docs)
            batches.register_batch(batch,queue,[d['id'] for d in docs])
            batches.register_batch(batch,queue)
            self.assertEqual(q.run(queue,max_jobs=2,lock=root/'lock',job_ids=[d['id'] for d in docs]),
                             [('cached-first','complete'),('cached-second','complete')])
            values=[q.load(queue/'jobs'/d['id']/'attempts/1/out/benchmark_summary.json') for d in docs]
            self.assertEqual(values[0],values[1])
            bad=desc('cached-failure');bad['inputs']['bundle']=dict(file=q.relative(root/'bad.json'))
            value=q.load(bundle);value['role']='final-audit';q.save(root/'bad.json',value)
            batches.register_batch(dict(version='experiment-batch-v1',jobs=[bad]),queue,['cached-failure'])
            self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=['cached-failure']),[('cached-failure','failed')])
            self.assertFalse((queue/'jobs/cached-failure/attempts/1/out/benchmark_summary.json').exists())


if __name__ == '__main__':
    unittest.main()
