"""Qualify detector campaign compilation and receipt-based decisions without fitting."""
import copy
from unittest.mock import patch
import unittest

import research_queue as q
import detector_campaign457 as worker
from experiment_templates import pin, checked
from test_research_campaign451 import CampaignTests
from model_decision_batch434 import register


class DetectorCampaignTests(CampaignTests):
    def setUp(self):
        super().setUp()
        card=dict(settings=dict(engine='pytorch',confidence=.5,imageSize=640,slice='class'),
                  inputs=self.report['inputs']['capture'],frames=[r['sha256'] for r in self.rows],
                  identity=dict(detector=dict(nmsIoU=.7)))
        path=self.root/'scorecard.json';q.save(path,card,replace=True)
        self.report['inputs']['scorecard']=pin(path)
        self.left=copy.deepcopy(self.report);self.right=copy.deepcopy(self.report)
        for r in self.left['rows']:
            if not r['noFocus']:r['arms']['detector']['models']['candidate']=dict(scores=[.1],outcome='miss')
        for name,report in [('base',self.left),('correction',self.right)]:
            self.specs[name]['template']['inputs']=report['inputs'];self.complete(self.specs[name],report)

    def request(self,name='detector-test',**changes):
        doc=dict(version='detector-campaign-v1',id=name,question='Does a changed detector preserve full-screen Standard focus?',
            membership=pin(self.membership),training=None,pairs=[dict(condition='one',baseline='base',candidate='correction')],
            retainedFailures=[],budget=dict(maxJobs=1,maxSeconds=800,maxOutputBytes=100_000_000))
        doc.update(changes);path=self.root/(name+'.json');q.save(path,doc,replace=True);return path

    # Parent test methods describe a different compiler contract.
    def test_detector_positive_and_no_focus(self):
        rows=worker.compare(self.left,self.right,self.rows)
        self.assertEqual(worker.assess(rows,[])['outcome'],'supported')
        self.assertEqual(sum(r['gain'] for r in rows),3)
        self.assertEqual(rows[-1]['candidate'],'correct-abstention')

    def test_detector_rejects_regression_and_retained_failure(self):
        rows=worker.compare(self.right,self.left,self.rows)
        self.assertEqual(worker.assess(rows,[])['outcome'],'contradicted')
        self.assertEqual(worker.assess(worker.compare(self.left,self.right,self.rows),[{'reason':'lost tab'}])['outcome'],'contradicted')

    def test_detector_rejects_changed_crop_and_labels(self):
        bad=copy.deepcopy(self.right);bad['inputs']['candidate']=bad['inputs']['baseline']
        with self.assertRaisesRegex(ValueError,'crop_or_input_changed'):worker.compare(self.left,bad,self.rows)
        bad=copy.deepcopy(self.right);bad['rows'][0]['sha256']='f'*64
        with self.assertRaisesRegex(ValueError,'membership_changed'):worker.compare(self.left,bad,self.rows)

    def test_detector_rejects_duplicate_and_missing_support(self):
        rows=worker.compare(self.left,self.right,self.rows)
        with self.assertRaisesRegex(ValueError,'duplicate'):worker.assess(rows+rows,[])
        self.assertEqual(worker.assess(rows[:2],[])['outcome'],'inconclusive')

    def test_detector_budget_and_immutable_compile(self):
        request=self.request();manifest=worker.compile_request(request,self.root/'compiled',self.queue)
        self.assertEqual(manifest,worker.compile_request(request,self.root/'compiled',self.queue))
        with self.assertRaisesRegex(ValueError,'budget_exceeded'):
            worker.compile_request(self.request('small',budget=dict(maxJobs=1,maxSeconds=1,maxOutputBytes=1)),self.root/'small',self.queue)

    def training_description(self):
        init=self.root/'initializer.pt';init.write_bytes(b'software-test-only')
        config=self.root/'config.json';q.save(config,dict(initialization=pin(init),selection='fixed-last',patience=0),replace=True)
        membership=self.root/'train.json';q.save(membership,dict(version='detector-training-membership-v2',trainingAdmitted=True,
            rows=[dict(role='train',trainingEligible=True,labelsComplete=True,group='train-only',image=dict(sha256='e'*64))]),replace=True)
        return dict(version='hcf-template-description-v1',id='software-fit',owner='Maximum-mini-NUIAK',template='T89',
            question='Does new training coverage improve Standard control detection?',decision='Preserve every retained success without model promotion.',
            inputs=dict(configuration=pin(config),initialization=pin(init),membership=pin(membership)),parameters={},
            training=dict(initialization=pin(init),membership=[pin(membership)],epochs=30,resume='restart',storageBudgetBytes=2<<30,
                experimentLogRunId='SOFTWARE457',acceptanceEvidence='Require complete matched regression evidence.'))

    def test_detector_new_training_connects_scores_and_report(self):
        train=self.training_description()
        request=self.request('new-training',training=train,pairs=[dict(condition='one',baseline='base',candidate=None)],
            budget=dict(maxJobs=4,maxSeconds=9600,maxOutputBytes=3<<30))
        manifest=worker.compile_request(request,self.root/'new-training',self.queue)
        specs=[q.load(checked(r['spec'])) for r in manifest['jobs']]
        self.assertEqual([s.get('template',{}).get('id') for s in specs],['T89','T56','T57',None])
        self.assertEqual(specs[0]['limits']['timeoutSeconds'],7200)
        self.assertEqual(specs[1]['template']['inputs']['model'],dict(job='software-fit',output='final.pt'))
        self.assertEqual(specs[1]['dependencies'][0]['specSHA256'],q.text_digest(specs[0]))
        self.assertEqual(specs[2]['template']['inputs']['candidate'],self.report['inputs']['candidate'])
        self.assertEqual(specs[-1]['dependencies'][-1]['outputs'],['benchmark_summary.json'])

    def test_detector_training_rejects_leakage_and_unadmitted_rows(self):
        for field,value,reason in [('group',self.rows[0]['group'],'group_leak'),('trainingEligible',False,'training_roles')]:
            train=self.training_description();ref=train['inputs']['membership'];path=checked(ref);data=q.load(path)
            data['rows'][0][field]=value;q.save(path,data,replace=True);train['inputs']['membership']=pin(path);train['training']['membership']=[pin(path)]
            request=self.request('bad-training',training=train,pairs=[dict(condition='one',baseline='base',candidate=None)],
                budget=dict(maxJobs=4,maxSeconds=9600,maxOutputBytes=3<<30))
            with self.assertRaisesRegex(ValueError,reason):worker.compile_request(request,self.root/'bad-training',self.queue)

    def test_detector_two_campaigns_execute_and_reject_changed_evidence(self):
        for name in ('detector-a','detector-b'):
            manifest=worker.compile_request(self.request(name),self.root/name,self.queue)
            register(manifest,self.queue,approve=True)
            q.run(self.queue,job_ids=[name+'-decision'],lock=self.root/'lock')
            out=self.queue/'jobs'/(name+'-decision')/'attempts/1/out'
            self.assertEqual(q.load(out/'decision.json')['outcome'],'supported')
        manifest=worker.compile_request(self.request('detector-bad'),self.root/'bad',self.queue)
        register(manifest,self.queue,approve=True)
        q.save(self.queue/'jobs/correction/attempts/1/out/benchmark_summary.json',{},replace=True)
        q.run(self.queue,job_ids=['detector-bad-decision'],lock=self.root/'lock')
        self.assertFalse((self.queue/'jobs/detector-bad-decision/attempts/1/out/decision.json').exists())


# Reuse the setup and helpers, but do not inherit tests for RESEARCH451.
for name in list(vars(CampaignTests)):
    if name.startswith('test_') and name not in vars(DetectorCampaignTests):
        setattr(DetectorCampaignTests,name,None)

if __name__=='__main__':unittest.main()
