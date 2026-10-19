"""Qualify reusable proposal reports with software evidence, not model claims."""
import copy
import tempfile
from pathlib import Path
import unittest

import research_queue as q
import research_approval as approval
import detector_focus_pilot as pilot
import proposal_campaign443 as compiler
import proposal_report443 as worker
from experiment_templates import pin
import test_model_decision434 as fixtures


class ProposalTests(unittest.TestCase):
    complete=fixtures.DecisionTests.complete
    reinventory=fixtures.DecisionTests.reinventory

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='proposal443-test-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.queue=self.root/'queue';self.queue.mkdir()
        self.inputs={}
        for name in ('capture','scorecard','ringProposals','mapping','baseline','candidate','baselineSelection','candidateSelection','tool'):
            path=self.root/(name+'.json');q.save(path,dict(softwareOnly=name));self.inputs[name]=pin(path)

    def report(self):
        frame=dict(id='one',sha256='a'*64,case='group',profile='standard');box=[0,0,10,10]
        def score(name,boxes):return ([.1 if name=='baseline' else .95]*len(boxes),['a'*64]*len(boxes))
        row=pilot.compare_frame(frame,[box],box,[dict(box=box,source='detector',sourceIndex=0)],[],score)
        report=pilot.summarize([row]);report['inputs']=self.inputs
        return report

    def preservation(self,losses=None):
        return dict(version='model-batch-decision-v1',modelAccepted=False,losses=losses or [],newWrongSelections=[],
                    models={name:[self.inputs[name]['sha256']] for name in ('baseline','candidate')})

    def test_supported_and_preserved_external_failure(self):
        report=self.report()
        result=worker.analyze([('score',report)],self.preservation())
        self.assertEqual(result['outcome'],'supported');self.assertFalse(result['modelAccepted'])
        failed=worker.analyze([('score',report)],self.preservation([dict(id='old-consumer-loss')]))
        self.assertEqual(failed['outcome'],'contradicted')

    def test_competing_scores_not_positive_maximum(self):
        report=self.report()
        for arm in report['rows'][0]['arms'].values():
            arm['candidates']*=2
            for name in ('baseline','candidate'):
                arm['models'][name]['scores']=[.95,.9]
                arm['models'][name]['outcome']='miss'
        result=worker.analyze([('score',report)],self.preservation())
        self.assertEqual(result['rows'][0]['diagnosis'],'competing-above-threshold')
        self.assertAlmostEqual(result['rows'][0]['topTwoGap']['candidate'],.05)

    def test_duplicate_nan_and_model_drift_fail(self):
        report=self.report()
        with self.assertRaisesRegex(ValueError,'proposal_duplicate_case'):
            worker.analyze([('score',report),('score',report)],self.preservation())
        changed=copy.deepcopy(report);changed['inputs']['candidate']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'proposal_model_drift'):
            worker.analyze([('a',report),('b',changed)],self.preservation())
        report['rows'][0]['arms']['known-box']['models']['candidate']['scores']=[float('nan')]
        with self.assertRaisesRegex(ValueError,'proposal_scores'):worker.analyze([('a',report)],self.preservation())

    def test_nofocus_false_selection_is_not_success(self):
        report=self.report();row=report['rows'][0];row['noFocus']=True
        for arm in row['arms'].values():
            arm['models']['baseline']['outcome']='correct-abstention'
            arm['models']['candidate']['outcome']='false-selection'
        result=worker.analyze([('score',report)],self.preservation())
        self.assertEqual(result['outcome'],'contradicted');self.assertTrue(result['rows'][0]['newWrong'])

    def test_contrast_keeps_known_boxes_and_rejects_changed_pixels(self):
        left=worker.analyze([('score',self.report())],self.preservation());right=copy.deepcopy(left)
        row=next(r for r in right['rows'] if r['arm']=='detector');row['candidate']='miss'
        result=worker.contrast_reports(left,right)
        self.assertTrue(next(r for r in result['rows'] if r['arm']=='detector')['loss'])
        right['rows'][0]['sha256']='f'*64
        with self.assertRaisesRegex(ValueError,'proposal_contrast_identity'):worker.contrast_reports(left,right)

    def test_contrast_rejects_known_box_changes(self):
        left=worker.analyze([('score',self.report())],self.preservation());right=copy.deepcopy(left)
        right['rows'][0]['candidate']='miss'
        with self.assertRaisesRegex(ValueError,'proposal_contrast_known_box'):worker.contrast_reports(left,right)

    def graph(self,ident,invalid=False):
        self.complete(dict(id='preservation',adapter=dict(steps=['model_decision434.decision'])),
                      {'decision.json':self.preservation()})
        desc=dict(version='hcf-template-description-v1',id=ident+'-score',owner='Test-NUIAK',template='T57',
                  question='Does fixed proposal scoring preserve the retained successes?',decision='Reject any lost success or wrong selection.',
                  inputs=self.inputs,parameters={},dependencies=[])
        batch=self.root/(ident+'-batch.json');q.save(batch,dict(version='experiment-batch-v1',jobs=[desc]))
        plan=self.root/(ident+'-plan.json');q.save(plan,dict(version='proposal-campaign-v1',id=ident,
            question='Does this description produce a valid paired decision?',batch=pin(batch),preservation='preservation'))
        manifest=compiler.compile_plan(plan,self.root/ident,self.queue)
        score=next(r for r in manifest['jobs'] if r['job']==ident+'-score')
        report=self.report()
        if invalid:report['threshold']=.8
        self.complete(q.load(q.ROOT/score['spec']['path']),{'benchmark_summary.json':report})
        ids=[]
        for row in manifest['jobs']:
            if row==score:continue
            q.submit(q.ROOT/row['spec']['path'],self.queue)
            approval.approve(self.queue,row['job'],'test','Qualify report execution with software-only evidence.')
            ids.append(row['job'])
        for _ in range(3):q.run(self.queue,job_ids=ids,lock=self.root/'runner.lock',max_jobs=10)
        return ident+'-report'

    def test_two_descriptions_execute_through_queue(self):
        for ident in ('first','second'):
            report=self.graph(ident)
            self.assertEqual(q.state(self.queue/'jobs'/report)[0],'complete')
            self.assertEqual(q.state(self.queue/'jobs'/(ident+'-supported-followup'))[0],'complete')
            self.assertFalse(q.attempts_of(self.queue/'jobs'/(ident+'-contradicted-followup')))

    def test_bad_report_fails_in_queue_and_blocks_followups(self):
        report=self.graph('invalid',True)
        result=q.load(self.queue/'jobs'/report/'attempts/1/result.json')
        self.assertEqual(result['status'],'failed');self.assertEqual(result['reason'],'process_failed')
        self.assertIn('proposal_report_version',(self.queue/'jobs'/report/'attempts/1/stderr.log').read_text())
        self.assertFalse(q.attempts_of(self.queue/'jobs/invalid-supported-followup'))


    def test_contrast_executes_without_repeating_scores(self):
        self.graph('left');self.graph('right')
        manifest=compiler.compile_contrast(pin(self.root/'left/compiled.json'),
            pin(self.root/'right/compiled.json'),self.root/'contrast','paired-contrast')
        row=manifest['jobs'][0]
        q.submit(q.ROOT/row['spec']['path'],self.queue)
        approval.approve(self.queue,row['job'],'test','Qualify retained comparison without new scoring.')
        q.run(self.queue,job_ids=[row['job']],lock=self.root/'runner.lock',max_jobs=1)
        self.assertEqual(q.state(self.queue/'jobs'/row['job'])[0],'complete')
        result=q.load(self.queue/'jobs'/row['job']/'attempts/1/out/contrast.json')
        self.assertFalse(result['modelAccepted'])


if __name__=='__main__':unittest.main()
