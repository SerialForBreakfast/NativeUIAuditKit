"""Positive and negative contracts for reusable HCF comparisons."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import research_queue as q
import research_approval as approval
import hcf_templates395 as templates
import template_analysis397 as a
from experiment_templates import pin


class ComparisonTests(unittest.TestCase):
    def test_expansion_preserves_center_and_clips_edges(self):
        for actual,expected in zip(a.expand([10,10,100,100],1.10,200,200),[5,5,110,110]):
            self.assertAlmostEqual(actual,expected)
        self.assertEqual(a.expand([0,0,100,100],1.10,100,100),[0,0,100,100])
    def report(self):
        return dict(rows=[dict(id='one',sha256='a'*64,group='g',role='development',profile='hcf',family='cards',outcome='correct')])

    def test_preservation_and_loss(self):
        baseline=self.report();candidate=copy.deepcopy(baseline)
        self.assertTrue(a.matched(baseline,candidate)['previousSuccessesPreserved'])
        candidate['rows'][0]['outcome']='miss'
        self.assertEqual(a.matched(baseline,candidate)['slices']['hcf']['losses'],['one'])

    def test_bad_membership_identity_and_audit(self):
        for field,value,error in [('id','other','membership'),('sha256','b'*64,'identity'),('role','audit','audit_locked')]:
            candidate=self.report();candidate['rows'][0][field]=value
            with self.assertRaisesRegex(ValueError,error):a.matched(self.report(),candidate)
        candidate=self.report();candidate['rows']*=2
        with self.assertRaisesRegex(ValueError,'duplicate'):a.matched(self.report(),candidate)

    def test_real_queue_success_and_explicit_failure(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='analysis397-') as folder:
            root=Path(folder);queue=root/'queue';base=root/'base.json';q.save(base,self.report())
            for ident,bad in [('positive',False),('negative',True)]:
                value=self.report()
                if bad:value['rows'][0]['sha256']='b'*64
                candidate=root/(ident+'.json');q.save(candidate,value)
                doc=dict(version='hcf-template-description-v1',id=ident,owner='test-NUIAK',template='T15',
                    question='Does a matched report preserve identity?',decision='Reject altered image identity.',
                    inputs=dict(baseline=pin(base),candidate=pin(candidate)),parameters=dict(comparison='software-only'),dependencies=[])
                templates.register(doc,queue);templates.register(doc,queue)
                approval.approve(queue,ident,'test','Isolated contract validation.')
                result=q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[ident])
                self.assertEqual(result,[(ident,'failed' if bad else 'complete')])

    def test_qualification_does_not_overwrite_command_receipt(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='qualification397-') as folder:
            root=Path(folder);cfg=root/'cfg.json'
            q.save(cfg,dict(version='template-qualification-v1',suite='contracts',
                tests=[pin(q.MODULES/(name+'.py')) for name in a.SUITES['contracts']]))
            def command(*args,**kwargs):q.save(root/'qualification.json',dict(returnCode=0))
            with patch.object(a,'command',side_effect=command):
                a.qualify(dict(qualification=pin(cfg)),dict(suite='contracts'),root)
            self.assertEqual(q.load(root/'qualification.json'),dict(returnCode=0))
            self.assertTrue(q.load(root/'qualification-summary.json')['passed'])


if __name__=='__main__':unittest.main()
