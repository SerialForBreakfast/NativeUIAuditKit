"""Qualify bounded selection and its queue integration without model execution."""
import copy
import shutil
import tempfile
import unittest
from pathlib import Path

import research_queue as q
import research_approval as approval
from experiment_templates import checked, pin
from proposal_report443 import contrast_reports
import bounded_selection444 as worker
import selection_campaign444 as compiler
from workflow_campaign439 import admit

RULES = dict(geometry=dict(cropLosses=dict(min=1),scoreFailures=dict(min=1)),
             supplemental=dict(proposalGains=dict(min=1),proposalLosses=dict(min=1)))


def reports():
    rows=[]
    for i in range(4):
        nofocus=i==3;old='correct-abstention' if nofocus else 'correct'
        for arm in ('known-box','detector','detector-plus-ring'):
            new='miss' if i==0 and arm!='known-box' else old
            rows.append(dict(id=str(i),sha256=str(i)*64,group='group-'+str(i),profile='standard',arm=arm,
                noFocus=nofocus,baseline=old,candidate=new,gain=False,loss=new!=old,newWrong=False,
                proposals=1,focusedProposalPresent=not nofocus,aboveThreshold=dict(baseline=1,candidate=0 if new=='miss' else 1),
                topTwoGap=dict(baseline=None,candidate=None),diagnosis='below-threshold' if new=='miss' else 'correct'))
    a=dict(version='proposal-campaign-decision-v1',modelAccepted=False,models={'fixed':'models'},rows=rows,
           preservation=dict(losses=[dict(id='prior-consumer',profile='standard')],newWrongSelections=[]))
    b=copy.deepcopy(a)
    for row in b['rows']:
        if row['arm']=='known-box' or row['noFocus']:continue
        row['candidate']='correct' if row['id']=='0' else 'miss' if row['id']=='1' else row['candidate']
        row['loss']=row['candidate']=='miss'
    return a,b,contrast_reports(a,b)


class SelectionTests(unittest.TestCase):
    def test_selects_diagnostics_not_model(self):
        result=worker.select(*reports(),RULES)
        self.assertEqual(result['branches'],dict(geometry='supported',supplemental='supported'))
        self.assertFalse(result['modelAccepted']);self.assertTrue(result['preservation']['losses'])

    def test_hcf_does_not_change_selection(self):
        a,b,c=reports();expected=worker.select(a,b,c,RULES)
        for doc in (a,b):
            extra=copy.deepcopy(doc['rows'])
            for row in extra:row['id']='hcf-'+row['id'];row['profile']='hcf'
            doc['rows']+=extra
        self.assertEqual(worker.select(a,b,contrast_reports(a,b),RULES),expected)

    def test_missing_nofocus_support_is_inconclusive(self):
        a,b,_=reports()
        for doc in (a,b):doc['rows']=[r for r in doc['rows'] if not r['noFocus']]
        self.assertEqual(set(worker.select(a,b,contrast_reports(a,b),RULES)['branches'].values()),{'inconclusive'})

    def test_rule_false_does_not_dispatch(self):
        rules=copy.deepcopy(RULES);rules['geometry']['cropLosses']['min']=999
        self.assertEqual(worker.select(*reports(),rules)['branches']['geometry'],'contradicted')

    def test_forged_counts_and_changed_contrast_fail(self):
        a,b,c=reports();a['rows'][0]['gain']=True
        with self.assertRaisesRegex(ValueError,'selection_counts'):worker.select(a,b,c,RULES)
        a,b,c=reports();c['rows'][0]['gain']=True
        with self.assertRaisesRegex(ValueError,'selection_contrast_changed'):worker.select(a,b,c,RULES)

    def test_invalid_rules_fail(self):
        for metric,bounds in [('accuracy',{'min':1}),('groups',{'min':float('nan')}),('groups',{'min':3,'max':1})]:
            rules=copy.deepcopy(RULES);rules['geometry']={metric:bounds}
            with self.assertRaises(ValueError):worker.rules_valid(rules)

    def test_real_graph_positive_and_negative_through_queue(self):
        """Retained-data integration. All work uses cached reports, never new inference."""
        sources=dict(baseline='standard443-base-report',candidate='standard443-new-report',contrast='standard443-detector-contrast')
        if not all((q.QUEUE/'jobs'/i/'spec.json').exists() for i in sources.values()):
            self.skipTest('STANDARD443 retained evidence is unavailable')
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='selection444-test-') as folder:
            root=Path(folder);queue=root/'queue';queue.mkdir()
            for ident in sources.values():shutil.copytree(q.QUEUE/'jobs'/ident,queue/'jobs'/ident)
            visited=set()
            def copy_specs(ident):
                if ident in visited:return
                visited.add(ident)
                source=q.QUEUE/'jobs'/ident/'spec.json';target=queue/'jobs'/ident/'spec.json'
                if not target.exists():target.parent.mkdir(parents=True);shutil.copyfile(source,target)
                for dep in q.load(source).get('dependencies',[]):copy_specs(dep['job'])
            for ident in sources.values():copy_specs(ident)
            for suffix, enabled in [('positive',True),('negative',False)]:
                rules=copy.deepcopy(RULES)
                if not enabled:
                    for rule in rules.values():rule['groups']=dict(min=999)
                request=root/(suffix+'.json')
                q.save(request,dict(version='bounded-selection-request-v1',id='test-selection-'+suffix,sources=sources,rules=rules))
                # Compilation reads verified live producer outputs. Only isolated jobs execute.
                manifest=compiler.compile_request(request,root/suffix)
                admit(manifest,queue)
                ids=[r['job'] for r in manifest['jobs']]
                for ident in ids:approval.approve(queue,ident,'test','Qualify bounded cached diagnostics in an isolated queue.')
                for _ in range(4):q.run(queue,job_ids=ids,lock=root/'runner.lock',max_jobs=10)
                self.assertEqual(q.state(queue/'jobs'/ids[0])[0],'complete')
                for ident in ids[1:]:
                    if enabled:
                        logs=queue/'jobs'/ident/'attempts/1/stderr.log'
                        result=logs.parent/'result.json'
                        self.assertEqual(q.state(queue/'jobs'/ident)[0],'complete',ident+': '+(logs.read_text() if logs.exists() else 'no stderr')+(result.read_text() if result.exists() else 'no result'))
                    else:self.assertFalse(q.attempts_of(queue/'jobs'/ident),ident)
                before={i:len(q.attempts_of(queue/'jobs'/i)) for i in ids}
                q.run(queue,job_ids=ids,lock=root/'runner.lock',max_jobs=10)
                self.assertEqual(before,{i:len(q.attempts_of(queue/'jobs'/i)) for i in ids})
                if enabled:
                    # A new invalid successor fails predictably. Its child never executes.
                    badplan=root/'bad-plan.json';q.save(badplan,dict(version='unsupported'))
                    gate=copy.deepcopy(q.load(checked(manifest['jobs'][0]['spec'])))
                    gate.update(id='invalid-selection-gate',selectionPlan=pin(badplan))
                    gate['inputs'][0]=pin(badplan);gate['evidence']['reads']=[q.relative(badplan)]
                    child=copy.deepcopy(q.load(checked(manifest['jobs'][1]['spec'])))
                    child['id']='invalid-selection-child'
                    child['dependencies'][0].update(job=gate['id'],specSHA256=q.text_digest(gate))
                    child['conditions'][0]['job']=gate['id']
                    for spec in (gate,child):
                        path=root/(spec['id']+'.json');q.save(path,spec);q.submit(path,queue)
                        approval.approve(queue,spec['id'],'test','Qualify invalid selector failure without child execution.')
                    q.run(queue,job_ids=[gate['id'],child['id']],lock=root/'runner.lock',max_jobs=2)
                    attempt=queue/'jobs'/gate['id']/'attempts/1'
                    self.assertEqual(q.load(attempt/'result.json')['status'],'failed')
                    self.assertIn('selection_plan_version',(attempt/'stderr.log').read_text())
                    self.assertFalse(q.attempts_of(queue/'jobs'/child['id']))


if __name__=='__main__':unittest.main()
