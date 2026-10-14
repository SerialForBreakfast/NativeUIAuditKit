"""Test scientific conditions, graph checks, and matched scene membership."""
import copy
import shutil
import unittest
import uuid
import research_queue as q
import research_graph as g
import graph364


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.root = q.ROOT / '.build' / ('graph-test-' + uuid.uuid4().hex)
        self.root.mkdir(parents=True)
        q.save(self.root / 'evidence.json', {'count': 2})
        self.evidence = {'path': 'evidence.json', 'sha256': q.digest(self.root / 'evidence.json')}
        self.doc = dict(version='research-condition-v1', outcome='supported', reason='Observed counts pass.', evidence=[self.evidence])
        self.spec = dict(dependencies=[dict(job='producer', specSHA256='a'*64, outputs=['gate.json'])],
                         conditions=[dict(job='producer', output='gate.json', outcome='supported')])

    def tearDown(self):
        shutil.rmtree(self.root)

    def resolved(self):
        q.save(self.root / 'gate.json', self.doc, replace=True)
        return [dict(job='producer', outputs=[dict(path='gate.json', sha256=q.digest(self.root / 'gate.json'))])]

    def test_supported(self):
        g.check_conditions(self.spec, self.resolved(), self.root)

    def test_negative_is_not_execution_failure(self):
        for outcome in ('contradicted', 'inconclusive'):
            self.doc['outcome'] = outcome
            with self.assertRaisesRegex(ValueError, 'condition_not_met'):
                g.check_conditions(self.spec, self.resolved(), self.root)

    def test_unknown_version(self):
        self.doc['version'] = 'future'
        with self.assertRaisesRegex(ValueError, 'condition_report_version'):
            g.check_conditions(self.spec, self.resolved(), self.root)

    def test_altered_report(self):
        resolved = self.resolved()
        q.save(self.root / 'gate.json', {}, replace=True)
        with self.assertRaisesRegex(ValueError, 'condition_report_changed'):
            g.check_conditions(self.spec, resolved, self.root)

    def test_altered_evidence(self):
        resolved = self.resolved()
        q.save(self.root / 'evidence.json', {'count': 0}, replace=True)
        with self.assertRaisesRegex(ValueError, 'condition_evidence_changed'):
            g.check_conditions(self.spec, resolved, self.root)

    def test_unbound_condition(self):
        self.spec['conditions'][0]['output'] = 'other.json'
        with self.assertRaisesRegex(ValueError, 'condition_output_missing'):
            g.validate_conditions(self.spec)

    def test_no_arbitrary_expression(self):
        self.spec['conditions'][0]['expression'] = 'True'
        with self.assertRaisesRegex(ValueError, 'condition_fields'):
            g.validate_conditions(self.spec)

    def test_duplicate_condition(self):
        self.spec['conditions'] *= 2
        with self.assertRaisesRegex(ValueError, 'condition_duplicate'):
            g.validate_conditions(self.spec)

    def test_malformed_evidence(self):
        self.doc['evidence'] = []
        with self.assertRaisesRegex(ValueError, 'condition_report_evidence'):
            g.check_conditions(self.spec, self.resolved(), self.root)

    def test_graph_pins_and_dependencies(self):
        specs = {'a': dict(limits=dict(timeoutSeconds=800, maxOutputBytes=100), dependencies=[])}
        specs['b'] = dict(limits=dict(timeoutSeconds=800, maxOutputBytes=100),
                          dependencies=[dict(job='a', specSHA256=q.text_digest(specs['a']))])
        nodes = []
        for name, spec in specs.items():
            folder = self.root / 'jobs' / name; folder.mkdir(parents=True)
            q.save(folder / 'spec.json', spec)
            nodes.append(dict(job=name, specSHA256=q.text_digest(spec), question='Does the test pass?', kind='experiment'))
        graph = dict(version='research-graph-v1', id='test-r1', nodes=nodes)
        self.assertEqual(g.validate_graph(graph, self.root)['maximumSeconds'], 1600)
        bad = copy.deepcopy(graph); bad['nodes'][0]['specSHA256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'graph_spec_changed'):
            g.validate_graph(bad, self.root)
        bad = copy.deepcopy(graph); bad['nodes'] = bad['nodes'][1:]
        with self.assertRaisesRegex(ValueError, 'graph_dependency_outside_revision'):
            g.validate_graph(bad, self.root)

    def test_matched_pairs(self):
        states = {name: [dict(path=name+'0', sha256='a'*64), dict(path=name+'1', sha256='b'*64)]
                  for name in graph364.VARIANTS}
        rows = graph364.make_rows(states, 'shelf', 'family-0')
        self.assertEqual(len(rows), 28)
        self.assertEqual(sum(r['changed'] for r in rows), 8)
        self.assertEqual({r['group'] for r in rows}, {'family-0'})
        self.assertEqual(len({r['id'] for r in rows}), len(rows))
        self.assertTrue(all(r['role'] == 'development' for r in rows))

    def test_queue_blocks_only_the_conditional_consumer(self):
        from test_research_queue import QueueTests
        fixture = QueueTests(); fixture.setUp()
        try:
            module = fixture.modules / 'rq_fixture.py'
            module.write_text(module.read_text() + '''
def qualify():
    import hashlib
    from pathlib import Path
    source = ROOT / "INPUT_PATH"
    evidence = dict(path=str(source.relative_to(ROOT)), sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    (OUT / 'gate.json').write_text(json.dumps(dict(version='research-condition-v1', outcome='contradicted',
        reason='The measured cue is absent.', evidence=[evidence])))
'''.replace('INPUT_PATH', q.relative(fixture.input)))
            producer = fixture.spec(id='a-producer', adapter=dict(type='python-callable',
                steps=['rq_fixture.qualify'], outputAttributes=['rq_fixture.OUT']))
            fixture.submit(producer)
            consumer = fixture.spec(id='b-consumer', dependencies=[dict(job='a-producer',
                specSHA256=q.text_digest(producer), outputs=['gate.json'])],
                conditions=[dict(job='a-producer', output='gate.json', outcome='supported')])
            fixture.submit(consumer)
            fixture.submit(fixture.spec(id='c-independent'))
            fixture.run_queue()
            self.assertEqual(q.state(fixture.queue/'jobs/a-producer')[0], 'complete')
            self.assertEqual(q.state(fixture.queue/'jobs/b-consumer')[0], 'blocked')
            self.assertEqual(q.state(fixture.queue/'jobs/c-independent')[0], 'complete')
            self.assertEqual(q.attempts_of(fixture.queue/'jobs/b-consumer'), [])
        finally:
            fixture.tearDown()


if __name__ == '__main__':
    unittest.main()
