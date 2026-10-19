"""Exercise campaign admission and outcome branches through isolated queues."""
import copy
from unittest import main
from unittest.mock import patch
import research_queue as q
import research_approval as approval
import workflow_campaign439 as campaign
import workflow_loss_audit439 as audit
import test_model_decision434 as fixtures


class CampaignTests(fixtures.DecisionTests):
    def request(self, ident='campaign-a'):
        plan=copy.deepcopy(self.plan);plan['id']=ident+'-decision-chain'
        return dict(version='workflow-campaign-v1',id=ident,decision=dict(plan=plan),branches=[
            dict(when=outcome,jobs=[dict(id=ident+'-'+outcome,kind='decision-audit',
                 question='Which retained failures need proposals or score inspection?')]) for outcome in ('supported','contradicted')])

    def prepare(self, ident='campaign-a'):
        source=self.root/(ident+'-request.json');q.save(source,self.request(ident))
        return campaign.compile_request(source,self.root/ident,self.queue)

    def test_two_campaigns_run_only_selected_branch_and_resume_without_duplicates(self):
        for ident in ('campaign-a','campaign-b'):
            manifest=self.prepare(ident)
            ids=[r['job'] for r in manifest['jobs']]
            campaign.admit(manifest,self.queue,ids)
            for unused in range(6):q.run(self.queue,job_ids=ids,lock=self.root/'run.lock',max_jobs=10)
            self.assertEqual(q.state(self.queue/'jobs'/(ident+'-supported'))[0],'complete')
            self.assertEqual(q.state(self.queue/'jobs'/(ident+'-contradicted'))[0],'blocked')
            self.assertFalse(q.attempts_of(self.queue/'jobs'/(ident+'-contradicted')))
            from workflow_batch435 import inspect
            report=inspect(manifest,self.queue)
            self.assertEqual(report['counts']['branch-not-selected'],1)
            report=q.load(self.queue/'jobs'/(ident+'-supported')/'attempts/1/out/audit.json')
            self.assertFalse(report['modelAccepted'])
            campaign.admit(manifest,self.queue,ids)
            self.assertEqual(len(q.attempts_of(self.queue/'jobs'/(ident+'-supported'))),1)

    def test_partial_registration_resumes(self):
        manifest=self.prepare();original=q.submit;calls=0
        def fail_once(*args,**kwargs):
            nonlocal calls
            calls+=1
            if calls==2:raise OSError('interrupted registration')
            return original(*args,**kwargs)
        with patch.object(q,'submit',side_effect=fail_once):
            with self.assertRaisesRegex(OSError,'interrupted'):campaign.admit(manifest,self.queue)
        campaign.admit(manifest,self.queue)
        self.assertTrue(all((self.queue/'jobs'/r['job']/'spec.json').exists() for r in manifest['jobs']))

    def test_transaction_admission_runs_and_retries_without_new_attempts(self):
        manifest=self.prepare('transaction-campaign');ids=[r['job'] for r in manifest['jobs']]
        self.assertLessEqual(len(ids),10)
        campaign.admit(manifest,self.queue,ids,approval_transaction=True)
        events=len(approval.load(self.queue)['events'])
        for unused in range(6):q.run(self.queue,job_ids=ids,lock=self.root/'run.lock',max_jobs=10)
        self.assertEqual(q.state(self.queue/'jobs/transaction-campaign-supported')[0],'complete')
        campaign.admit(manifest,self.queue,ids,approval_transaction=True)
        self.assertEqual(len(approval.load(self.queue)['events']),events)
        self.assertEqual(len(q.attempts_of(self.queue/'jobs/transaction-campaign-supported')),1)

    def test_transaction_requires_named_approvals(self):
        manifest=self.prepare()
        with self.assertRaisesRegex(ValueError,'campaign_transaction_limit'):
            campaign.admit(manifest,self.queue,approval_transaction=True)

    def test_contradicted_branch_runs_and_supported_stays_closed(self):
        from consumer_crop_comparison import summarize
        rows=q.load(self.root/'membership.json')['rows']
        report=summarize(rows,[.1,.95]);report['backend']='pytorch'
        q.save(self.queue/'jobs/consumer-candidate/attempts/1/out/benchmark_summary.json',report,replace=True)
        self.reinventory('consumer-candidate')
        manifest=self.prepare();ids=[r['job'] for r in manifest['jobs']]
        campaign.admit(manifest,self.queue,ids)
        for unused in range(6):q.run(self.queue,job_ids=ids,lock=self.root/'run.lock',max_jobs=10)
        self.assertEqual(q.state(self.queue/'jobs/campaign-a-contradicted')[0],'complete')
        self.assertFalse(q.attempts_of(self.queue/'jobs/campaign-a-supported'))

    def test_failed_producer_blocks_both_branches(self):
        self.reinventory('native-candidate','failed')
        manifest=self.prepare();ids=[r['job'] for r in manifest['jobs']]
        with self.assertRaisesRegex(ValueError,'producer_requires_review'):
            campaign.admit(manifest,self.queue,ids)
        self.assertFalse(q.attempts_of(self.queue/'jobs/campaign-a-supported'))
        self.assertFalse(q.attempts_of(self.queue/'jobs/campaign-a-contradicted'))

    def test_existing_template_branch_compiles_without_new_adapter(self):
        request=self.request()
        source_spec=q.load(self.queue/'jobs/consumer-candidate/spec.json')
        desc=dict(version='hcf-template-description-v1',id='existing-template-branch',owner='Maximum-mini-NUIAK',
                  template='T63',question='Does the fixed consumer path preserve the retained crop decisions?',
                  decision='Preserve every retained success before another correction.',
                  inputs=source_spec['template']['inputs'],parameters=source_spec['template']['parameters'],dependencies=[])
        request['branches']=[dict(when='supported',jobs=[desc])]
        source=self.root/'request-template.json';q.save(source,request)
        manifest=campaign.compile_request(source,self.root/'template-campaign',self.queue)
        spec=q.load(q.ROOT/manifest['jobs'][-1]['spec']['path'])
        self.assertEqual(spec['template']['id'],'T63')
        self.assertEqual(spec['conditions'][0]['outcome'],'supported')

    def test_changed_source_and_approval_outside_batch_fail(self):
        manifest=self.prepare()
        with self.assertRaisesRegex(ValueError,'campaign_approval_ids'):campaign.admit(manifest,self.queue,['unrelated'])
        path=self.queue/'jobs/training/spec.json';spec=q.load(path);spec['training']['epochs']=29;q.save(path,spec,replace=True)
        with self.assertRaisesRegex(ValueError,'campaign_existing_changed'):campaign.admit(manifest,self.queue)
        self.assertFalse((self.queue/'jobs/campaign-a-supported').exists())

    def test_revocation_is_not_restored(self):
        manifest=self.prepare();ids=[r['job'] for r in manifest['jobs']]
        campaign.admit(manifest,self.queue,ids)
        approval.revoke(self.queue,ids[0],'test','Explicit software-test revocation.')
        with self.assertRaisesRegex(ValueError,'campaign_revoked'):campaign.admit(manifest,self.queue,ids)

    def test_changed_request_does_not_replace_manifest(self):
        manifest=self.prepare();source=self.root/'campaign-a-request.json'
        request=q.load(source);request['branches'][0]['jobs'][0]['question']='Different scope must not replace an existing campaign.';q.save(source,request,replace=True)
        with self.assertRaisesRegex(ValueError,'immutable_conflict'):campaign.compile_request(source,self.root/'campaign-a',self.queue)

    def test_audit_counts_no_proposals_separately(self):
        row=dict(id='one',profile='standard',arm='raw-proposal',group='g',noFocus=False,
                 candidateProposals=0,loss=False,newWrong=False)
        result=audit.analyze(dict(version='model-batch-decision-v1',modelAccepted=False,rows=[row]))
        self.assertEqual(result['slices'][0]['absentProposals'],1)
        self.assertEqual(result['cases'][0]['diagnosis'],'no_candidate_proposal')
        with self.assertRaisesRegex(ValueError,'duplicate_case'):
            audit.analyze(dict(version='model-batch-decision-v1',modelAccepted=False,rows=[row,row]))


if __name__=='__main__':main()
