import copy
import tempfile
import unittest
from pathlib import Path
import research_queue as q
import research_approval as approval
from experiment_templates import pin, checked
import cascade_validation as worker
import test_model_decision434 as fixtures


class ValidationTests(unittest.TestCase):
    complete = fixtures.DecisionTests.complete
    reinventory = fixtures.DecisionTests.reinventory

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='validation448-test-')
        self.root=Path(self.temp.name);self.queue=self.root/'queue';self.queue.mkdir()
        self.prior=q.load(q.QUEUE/'jobs/cascade446-decision/attempts/1/out/decision.json')
        self.mapping=q.load(q.ROOT/'reports/work/COVERAGE447/membership.json')['priorCaseGroups']
        self.sources=[];self.rows=[];self.pairs=[]
        for n in (1,2):
            condition='condition-'+str(n)
            for tag in ('base','new'):
                ident=f'standard443-{tag}-score-{n:02}'
                spec=q.load(q.QUEUE/'jobs'/ident/'spec.json')
                report=q.load(q.QUEUE/'jobs'/ident/'attempts/1/out/benchmark_summary.json')
                self.sources.append((spec,report))
                (self.queue/'jobs'/ident).mkdir(parents=True)
                q.save(self.queue/'jobs'/ident/'spec.json',spec)
                if tag=='base':
                    self.rows.extend(dict(id=r['id'],sha256=r['sha256'],case=r['group'],group='shared-group',profile=r['profile'],condition=condition,relatedToPrior=True) for r in report['rows'])
            self.pairs.append(dict(condition=condition,primary=f'standard443-base-score-{n:02}',supplemental=f'standard443-new-score-{n:02}'))
        self.parent=dict(id='prior',adapter=dict(steps=['cached_model_cascade.finish']))
        self.complete(self.parent,{'decision.json':self.prior})

    def tearDown(self):self.temp.cleanup()

    def compile(self,name,pairs=None):
        pairs=pairs or self.pairs
        data=dict(version='coverage-membership-v1',rows=[r for r in self.rows if r['condition'] in {p['condition'] for p in pairs}],priorCaseGroups=self.mapping)
        path=self.root/(name+'-membership.json');q.save(path,data)
        request=self.root/(name+'.json')
        q.save(request,dict(version='cascade-validation-request-v1',id=name,membership=pin(path),prior='prior',pairs=pairs))
        return worker.compile_request(request,self.root/name,self.queue)

    def submit(self,manifest):
        ids=[]
        for row in manifest['jobs']:
            q.submit(checked(row['spec']),self.queue)
            approval.approve(self.queue,row['job'],'test','Verify immutable future receipt binding in isolation.')
            ids.append(row['job'])
        return ids

    def test_pending_receipts_release_and_second_description_reuses_adapter(self):
        for name,pairs in [('one',self.pairs[:1]),('two',self.pairs)]:
            manifest=self.compile(name,pairs);ids=self.submit(manifest)
            if name=='one':
                self.assertEqual(q.state(self.queue/'jobs'/ids[0])[0],'blocked')
                self.assertFalse(q.attempts_of(self.queue/'jobs'/ids[0]))
                for spec,report in self.sources:self.complete(spec,{'benchmark_summary.json':report})
            for _ in range(2):q.run(self.queue,job_ids=ids,lock=self.root/'lock',max_jobs=10)
            self.assertTrue(all(q.state(self.queue/'jobs'/i)[0]=='complete' for i in ids),[(i,q.state(self.queue/'jobs'/i)) for i in ids])
            result=q.load(self.queue/'jobs'/ids[-1]/'attempts/1/out/decision.json')
            self.assertEqual(result['slices']['standard/baseline']['groups'],1)
            self.assertEqual(result['retainedPrior']['originalGroups'],11)
            self.assertFalse(result['modelAccepted'])
            counts=[len(q.attempts_of(self.queue/'jobs'/i)) for i in ids]
            q.run(self.queue,job_ids=ids,lock=self.root/'lock',max_jobs=10)
            self.assertEqual(counts,[len(q.attempts_of(self.queue/'jobs'/i)) for i in ids])

    def test_changed_receipt_blocks_only_affected_branch(self):
        manifest=self.compile('changed');ids=self.submit(manifest)
        for spec,report in self.sources:self.complete(spec,{'benchmark_summary.json':report})
        path=self.queue/'jobs'/self.sources[0][0]['id']/'attempts/1/out/benchmark_summary.json'
        q.save(path,{'changed':True},replace=True)
        q.run(self.queue,job_ids=ids,lock=self.root/'lock',max_jobs=10)
        self.assertEqual(q.state(self.queue/'jobs'/ids[0])[0],'blocked')
        self.assertEqual(q.state(self.queue/'jobs'/ids[1])[0],'complete')
        self.assertFalse(q.attempts_of(self.queue/'jobs'/ids[-1]))

    def test_missing_duplicate_or_changed_membership_fails(self):
        a,b=self.sources[0][1],self.sources[1][1]
        report=worker.cascade.evaluate(a,b)
        expected=[r for r in self.rows if r['condition']=='condition-1']
        worker.normalize(report,expected)
        for rows in [expected[:-1],expected+[expected[0]], [dict(r,sha256='wrong') for r in expected]]:
            with self.assertRaises(ValueError):worker.normalize(report,rows)

    def test_path_traversal_rejected(self):
        pairs=copy.deepcopy(self.pairs);pairs[0]['primary']='../unsafe'
        with self.assertRaises(ValueError):self.compile('invalid',pairs)


if __name__=='__main__':unittest.main()
