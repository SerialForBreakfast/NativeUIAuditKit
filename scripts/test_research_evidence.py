"""Exercise measured evidence with explicit fictional inputs."""
import copy
import json
import shutil
import unittest
import uuid
import research_evidence as e
import research_queue as q
import benchmark_evaluator as evaluator


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.root = q.ROOT / '.build' / ('evidence-test-' + uuid.uuid4().hex)
        self.root.mkdir(parents=True)
        self.doc = dict(version=e.VERSION, task='focus-change', dataRole='development',
                        labelAuthority='authored', sourceDomain='authored')
        for key in ('model', 'preprocessing', 'settings', 'image'):
            (self.root / key).write_text(key)
            self.doc[key] = self.pin(key)
        self.rows = [dict(id=str(i), label=label, prediction=pred, role='development', group=str(i),
            inputs=[self.doc['image']], theme='dark_standard', archetype='shelf')
            for i, (label, pred) in enumerate([(1, 1), (1, 0), (0, 1), (0, 0), (1, None)])]
        self.write()

    def tearDown(self):
        shutil.rmtree(self.root)

    def pin(self, name):
        return dict(path=name, sha256=e.sha(self.root/name))

    def write(self):
        (self.root/'predictions').write_text(json.dumps(self.rows))
        (self.root/'membership').write_text(json.dumps([{k:v for k,v in r.items() if k!='prediction'} for r in self.rows]))
        for key in ('predictions', 'membership'):
            self.doc[key] = self.pin(key)

    def test_counts_and_denominators(self):
        r=e.score(self.doc,self.root)
        self.assertEqual(r['metrics']['accuracy'], .4)
        self.assertEqual(r['metrics']['positiveRecall'], 1/3)
        self.assertEqual(r['metrics']['errorAmongStable'], .5)
        self.assertEqual(r['metrics']['abstentions'], 1)
        self.assertEqual(len(r['coverage']),21)
        self.assertEqual(r['coverage']['grid/light_standard']['support'],0)

    def test_unknown_version(self):
        self.doc['version']='wrong'
        with self.assertRaisesRegex(ValueError,'evidence_version'):e.score(self.doc,self.root)

    def test_zero_support(self):
        self.rows=[];self.write()
        with self.assertRaisesRegex(ValueError,'zero_support'):e.score(self.doc,self.root)

    def test_duplicate_prediction(self):
        self.rows.append(self.rows[0]);self.write()
        with self.assertRaisesRegex(ValueError,'duplicate'):e.score(self.doc,self.root)

    def test_missing_inputs(self):
        self.rows[0]['inputs']=[];self.write()
        with self.assertRaisesRegex(ValueError,'missing_inputs'):e.score(self.doc,self.root)

    def test_hash_change(self):
        (self.root/'image').write_text('changed')
        with self.assertRaisesRegex(ValueError,'evidence_hash'):e.score(self.doc,self.root)

    def test_missing_theme(self):
        del self.rows[0]['theme'];self.write()
        with self.assertRaisesRegex(ValueError,'coverage_identity'):e.score(self.doc,self.root)

    def test_invalid_label(self):
        self.rows[0]['label']=True;self.write()
        with self.assertRaisesRegex(ValueError,'invalid_label'):e.score(self.doc,self.root)

    def test_cross_role_ancestry(self):
        members=json.loads((self.root/'membership').read_text())
        members.append(dict(members[0],id='audit',role='final-audit',inputs=[]))
        (self.root/'membership').write_text(json.dumps(members));self.doc['membership']=self.pin('membership')
        with self.assertRaisesRegex(ValueError,'cross_role_ancestry'):e.score(self.doc,self.root)

    def test_missing_prediction(self):
        del self.rows[0]['prediction'];self.write()
        with self.assertRaisesRegex(ValueError,'invalid_prediction'):e.score(self.doc,self.root)

    def test_unavailable_denominator(self):
        self.rows=[dict(self.rows[0],label=0,prediction=None)];self.write()
        self.assertIsNone(e.score(self.doc,self.root)['metrics']['positiveRecall'])

    def test_legacy_adapter_refused(self):
        with self.assertRaisesRegex(ValueError,'legacy_placeholder'):evaluator.run()

    def test_placeholder_classification(self):
        self.assertEqual(e.classification(dict(adapter=dict(steps=['benchmark_evaluator.run'])),None),('placeholder',None))

    def test_path_escape(self):
        self.doc['model']['path']='../outside'
        with self.assertRaisesRegex(ValueError,'evidence_path'):e.score(self.doc,self.root)

    def test_threshold_selection_leakage(self):
        self.doc['dataRole']='final-audit'
        for row in self.rows:row['role']='final-audit'
        self.write()
        (self.root/'selection').write_text(json.dumps([{'group':self.rows[0]['group']}]))
        self.doc['selectionMembership']=self.pin('selection')
        with self.assertRaisesRegex(ValueError,'selection_audit_leakage'):e.score(self.doc,self.root)


if __name__=='__main__':unittest.main()
