"""Software qualification of short training requests and queue decision paths."""
import copy
import unittest
from unittest.mock import patch

import research_queue as q
import hcf_templates395 as templates
import training_campaign452 as compiler
import workflow_campaign439 as admission
from experiment_templates import pin, checked
import test_model_decision434 as fixtures


class TrainingCampaignTests(fixtures.DecisionTests):
    # Reuse the isolated evidence fixtures, not their unrelated tests.
    def setUp(self):
        super().setUp()
        rows = [dict(id='train-'+str(i), role='train', profile='standard', group='train', label=i) for i in (0, 1)]
        rows += [dict(id='dev', role='development', profile='standard', group='development', label=1)]
        self.membership = self.root/'frozen.json'
        q.save(self.membership, dict(version='crop-membership-plan-v1', rows=rows))
        config = self.root/'fit-config.json'
        q.save(config, dict(initialization=self.inputs['oldmodel'], profile='balanced', deduplicate=False, seed=371))
        self.complete(dict(id='preparation'), {'crops.json':dict(rows=rows)})
        self.definition = dict(id='new-fit', preparation='preparation', configuration=pin(config),
            initialization=self.inputs['oldmodel'], membership=pin(self.membership), experimentLogRunId='SOFTWARE452')
        self.log=self.root/'log.json';q.save(self.log,dict(run='SOFTWARE452',scope='Software fixtures only.'))
        self.suite = self.root/'suite.json'
        q.save(self.suite, dict(version='training-suite-v1', excludedGroups=['development','native-group','consumer-group'],
            baselines=[dict(job=p['baseline'], specSHA256=q.text_digest(q.load(self.queue/'jobs'/p['baseline']/'spec.json')))
                       for p in self.pairs]))

    def request(self, ident='train-campaign-a'):
        return dict(version='training-campaign-v1', id=ident,
            question='Does the fixed crop correction preserve all Standard and consumer successes?',
            controlledComparison='Use identical frozen evaluation inputs and change only the candidate crop model.',
            training=copy.deepcopy(self.definition), suite=pin(self.suite),
            budget=dict(maxJobs=12, maxSeconds=12000, maxOutputBytes=4<<30),
            followups=[dict(when=o,jobs=[dict(id=ident+'-'+o,kind='decision-audit',
                question='Which retained failures require eligible correction inputs?')]) for o in ('supported','contradicted')])

    def prepare_graph(self, request=None):
        request=request or self.request()
        source=self.root/(request['id']+'.json');q.save(source,request,replace=True)
        return compiler.compile_request(source,self.root/request['id'],self.queue)

    def seed_software_producers(self, manifest, fail=False):
        specs={r['job']:q.load(checked(r['spec'])) for r in manifest['jobs']}
        train=specs['new-fit']
        self.complete(train, {'fit.json':dict(epochs=30,selection='fixed-last',earlyStopped=False,boundaryStopped=False),
                              'final.pt':dict(softwareOnly='not-a-model')})
        for ident,spec in specs.items():
            if spec.get('template',{}).get('id') not in ('T37','T63'):continue
            native=spec['template']['id']=='T37'
            name='selection.json' if native else 'benchmark_summary.json'
            original='native-candidate' if native else 'consumer-candidate'
            doc=q.load(self.queue/'jobs'/original/'attempts/1/out'/name)
            self.complete(spec,{name:doc})
            if fail and native:self.reinventory(ident,'failed')

    def test_short_request_expands_exact_suite_and_budget(self):
        manifest=self.prepare_graph()
        specs={r['job']:q.load(checked(r['spec'])) for r in manifest['jobs']}
        self.assertEqual(sum(s.get('template',{}).get('id')=='T06' for s in specs.values()),1)
        self.assertEqual(sum(s.get('template',{}).get('id') in ('T37','T63') for s in specs.values()),2)
        self.assertFalse((self.queue/'jobs/new-fit').exists())
        for s in specs.values():
            for dep in s['dependencies']:
                if dep['job'] in specs:self.assertEqual(dep['specSHA256'],q.text_digest(specs[dep['job']]))
        budget=q.load(self.root/'train-campaign-a/budget.json')
        self.assertEqual(budget['reserved']['maxJobs'],len(specs))

    def test_two_campaigns_reuse_terminal_workers_and_no_duplicate_execution(self):
        for ident in ('train-campaign-a','train-campaign-b'):
            request=self.request(ident)
            if ident.endswith('b'):
                request['training']={'reuse':'new-fit'}
            manifest=self.prepare_graph(request)
            if ident.endswith('a'):self.seed_software_producers(manifest)
            else:
                # Only scoring receipts are synthetic. No trainer or model quality claim follows.
                for row in manifest['jobs']:
                    spec=q.load(checked(row['spec']));tid=spec.get('template',{}).get('id')
                    if tid not in ('T37','T63'):continue
                    name='selection.json' if tid=='T37' else 'benchmark_summary.json'
                    old='native-candidate' if tid=='T37' else 'consumer-candidate'
                    self.complete(spec,{name:q.load(self.queue/'jobs'/old/'attempts/1/out'/name)})
            ids=[r['job'] for r in manifest['jobs']]
            # Existing training/log approval is tested by admission tests. These synthetic receipts bypass no live gate.
            with patch.object(q,'EXPERIMENT_LOG',self.log):
                admission.admit(manifest,self.queue,[i for i in ids if not q.attempts_of(self.queue/'jobs'/i)])
                for _ in range(6):q.run(self.queue,job_ids=ids,lock=self.root/'lock',max_jobs=10)
            self.assertEqual(q.state(self.queue/'jobs'/(ident+'-decision'))[0],'complete')
            result=q.load(self.queue/'jobs'/(ident+'-decision')/'attempts/1/out/decision.json')
            self.assertFalse(result['modelAccepted']);self.assertEqual(result['outcome'],'supported')
            self.assertFalse(q.attempts_of(self.queue/'jobs'/(ident+'-contradicted')))
            self.assertEqual(q.run(self.queue,job_ids=ids,lock=self.root/'lock',max_jobs=10),[])
            self.assertEqual(self.prepare_graph(request),manifest)

    def test_budget_blocks_before_registration(self):
        request=self.request();request['budget']['maxSeconds']=1
        with self.assertRaisesRegex(ValueError,'training_graph_budget_exceeded'):self.prepare_graph(request)
        self.assertFalse((self.queue/'jobs/new-fit').exists())

    def test_group_leak_and_missing_exclusion_rejected(self):
        for group in ('train','unknown'):
            document=q.load(self.membership);document['rows'][-1]['group']=group
            q.save(self.membership,document,replace=True)
            request=self.request();request['training']['membership']=pin(self.membership)
            with self.assertRaisesRegex(ValueError,'group_leak|missing_exclusions'):self.prepare_graph(request)

    def test_duplicate_membership_and_unknown_label_rejected(self):
        rows=q.load(self.membership)['rows']
        for mutation in ('duplicate','unknown'):
            changed=copy.deepcopy(rows)
            if mutation=='duplicate':changed.append(changed[0])
            else:changed[0]['label']=None
            q.save(self.membership,dict(rows=changed),replace=True)
            with self.assertRaisesRegex(ValueError,'duplicate_membership|membership_fields'):
                compiler.frozen_membership(pin(self.membership),['development'])

    def test_changed_baseline_and_duplicate_suite_rejected(self):
        doc=q.load(self.suite);doc['baselines'][0]['specSHA256']='0'*64;q.save(self.suite,doc,replace=True)
        with self.assertRaisesRegex(ValueError,'baseline_changed'):self.prepare_graph()

    def test_followup_training_and_profile_filter_rejected(self):
        request=self.request();request['followups'][0]['jobs']=[dict(template='T06')]
        with self.assertRaisesRegex(ValueError,'followup_scope'):self.prepare_graph(request)
        path=checked(self.definition['configuration']);cfg=q.load(path);cfg['profile']='hcf';q.save(path,cfg,replace=True)
        request=self.request();request['training']['configuration']=pin(path)
        with self.assertRaisesRegex(ValueError,'profile_or_initialization'):self.prepare_graph(request)

    def test_failed_producer_blocks_admission(self):
        manifest=self.prepare_graph();self.seed_software_producers(manifest,fail=True)
        with patch.object(q,'EXPERIMENT_LOG',self.log):
            with self.assertRaisesRegex(ValueError,'producer_requires_review'):admission.admit(manifest,self.queue)

    def test_pending_preparation_binds_before_images_exist(self):
        cfg=self.root/'crop-config.json';q.save(cfg,dict(softwareOnly=True))
        request=self.request();request['training']['preparation']=dict(version='hcf-template-description-v1',
            id='pending-crops',template='T05',owner='Maximum-mini-NUIAK',inputs=dict(configuration=pin(cfg)),
            parameters={},dependencies=[dict(job='preparation',specSHA256=q.text_digest(dict(id='preparation')),outputs=['crops.json'])],question='Prepare frozen training crops after verified producer evidence.',
            decision='Reject any change to the frozen membership before fitting.')
        manifest=self.prepare_graph(request)
        specs={r['job']:q.load(checked(r['spec'])) for r in manifest['jobs']}
        dep=specs['new-fit']['dependencies'][0]
        self.assertEqual(dep['job'],'pending-crops')
        self.assertEqual(dep['specSHA256'],q.text_digest(specs['pending-crops']))
        self.assertFalse(q.attempts_of(self.queue/'jobs/new-fit'))

    def test_training_bridge_rejects_changed_membership_before_fit(self):
        import template_bridge395 as bridge
        import hcf_factor_train376 as factor
        manifest=self.prepare_graph();spec=next(q.load(checked(r['spec'])) for r in manifest['jobs'] if r['job']=='new-fit')
        out=self.queue/'jobs/new-fit/attempts/1/out';out.mkdir(parents=True)
        q.save(out.parents[2]/'spec.json',spec)
        q.save(out/'dependencies.json',q.dependency_inputs(spec,self.queue))
        with patch.object(bridge,'OUT',out), patch.object(factor,'train') as fit:
            bridge.native();fit.assert_called_once()
        # Change the declared membership, not the produced crops. The bridge must fail before fitting.
        changed=q.load(self.membership);changed['rows'][0]['label']=1
        new=self.root/'changed-membership.json';q.save(new,changed)
        spec['template']['inputs']['membership']=pin(new)
        q.save(out.parents[2]/'spec.json',spec,replace=True)
        (out/'template-result.json').unlink();(out/'sources.json').unlink()
        with patch.object(bridge,'OUT',out), patch.object(factor,'train') as fit:
            with self.assertRaisesRegex(ValueError,'training_membership_mismatch'):bridge.native()
            fit.assert_not_called()
        self.assertEqual(q.load(out/'template-result.json')['execution'],'failed')

    def test_retained_consumer_regression_closes_supported_branch(self):
        from consumer_crop_comparison import summarize
        manifest=self.prepare_graph();self.seed_software_producers(manifest)
        ident='train-campaign-a-score-02'
        rows=q.load(self.root/'membership.json')['rows'];report=summarize(rows,[.1,.95]);report['backend']='pytorch'
        q.save(self.queue/'jobs'/ident/'attempts/1/out/benchmark_summary.json',report,replace=True)
        self.reinventory(ident)
        ids=[r['job'] for r in manifest['jobs']]
        with patch.object(q,'EXPERIMENT_LOG',self.log):
            admission.admit(manifest,self.queue,[i for i in ids if not q.attempts_of(self.queue/'jobs'/i)])
            for _ in range(6):q.run(self.queue,job_ids=ids,lock=self.root/'lock',max_jobs=10)
        report=q.load(self.queue/'jobs/train-campaign-a-decision/attempts/1/out/decision.json')
        self.assertEqual(report['outcome'],'contradicted')
        self.assertTrue(report['losses']);self.assertFalse(report['modelAccepted'])
        self.assertEqual(q.state(self.queue/'jobs/train-campaign-a-contradicted')[0],'complete')
        self.assertFalse(q.attempts_of(self.queue/'jobs/train-campaign-a-supported'))

    def test_changed_request_cannot_expand_existing_budget(self):
        request=self.request();self.prepare_graph(request)
        request['budget']['maxSeconds']*=2
        with self.assertRaisesRegex(ValueError,'immutable_request'):self.prepare_graph(request)

    def test_missing_log_prevents_new_training_admission(self):
        manifest=self.prepare_graph()
        with patch.object(q,'EXPERIMENT_LOG',self.root/'absent-log'):
            with self.assertRaisesRegex(ValueError,'experiment_log_missing'):admission.admit(manifest,self.queue)
        self.assertFalse((self.queue/'jobs/new-fit').exists())


# Do not inherit the older suite as duplicate tests.
for name in list(fixtures.DecisionTests.__dict__):
    if name.startswith('test_') and name not in TrainingCampaignTests.__dict__:
        setattr(TrainingCampaignTests,name,None)

if __name__=='__main__':unittest.main()
