"""Reusable campaign admission checks. No live target or capture is used."""
import copy
import unittest
from pathlib import Path
from unittest.mock import patch
import research_queue as q
import ttr_campaign_queue493 as m
from test_ttr_campaign_queue493 import CampaignTests, Client

class ContractTests(CampaignTests):
    def cfg(self):
        c=super().cfg()
        c.update(version='ttr-campaign-queue-v2',job='native-alpha',task='WORKFLOW533',
                 fixtureBinaries={'sample':'source-built'},
                 callerExport={k:dict(path='/source/'+k,sha256='0'*64) for k in ('script','dependency','helper')})
        c['helper']['sha256']='0'*64
        return c
    def spec(self,c):
        root=Path(__file__).resolve().parents[1]
        s=q.load(root/'reports/work/ADRSPIKES493/session-1-queue-spec.json')
        s.update(id=c['job'],task=c['task'])
        return s
    def test_two_campaign_names_use_same_adapter(self):
        for name,order in [('native-alpha',1),('native-beta',2)]:
            c=self.cfg();c.update(job=name,order=order)
            c['manifest']['reuse_runner']=order==2
            c['manifest']['campaign_id']=name
            m.validate_spec(self.spec(c),c)
            out=self.root/name;out.mkdir()
            m.execute(c,Client(out),out,intake=lambda *_:([],[]))
            self.assertTrue(q.load(out/'session-result.json')['cleanup'])
    def test_wrong_job_task_target_and_budget_rejected(self):
        c=self.cfg()
        for field in ('id','task'):
            s=self.spec(c);s[field]='different'
            with self.assertRaisesRegex(ValueError,'campaign_spec_identity'):m.validate_spec(s,c)
        s=self.spec(c);s['capture']['endpoint']='http://elsewhere'
        with self.assertRaisesRegex(ValueError,'campaign_spec_target'):m.validate_spec(s,c)
        s=self.spec(c);s['limits']['timeoutSeconds']=500
        with self.assertRaisesRegex(ValueError,'campaign_spec_budget'):m.validate_spec(s,c)
    def test_unknown_fields_and_invalid_pins_rejected(self):
        c=self.cfg();c['extra']=True
        with self.assertRaisesRegex(ValueError,'campaign_config_fields'):m.validate_config(c)
        c=self.cfg();c['helper']['sha256']='bad'
        with self.assertRaisesRegex(ValueError,'pin_hash_format'):m.validate_config(c)
    def test_nonpositive_producer_budget_rejected(self):
        for value in (0,-1,True):
            c=self.cfg();c['manifest']['budget']['max_wall_clock_seconds']=value
            with self.assertRaisesRegex(ValueError,'campaign_producer_budget'):m.validate_config(c)
    def test_real_queue_admission_and_immutable_successor(self):
        # Submit only into an isolated queue. No approval and no live dispatch.
        root=Path(__file__).resolve().parents[1]
        with patch.object(q,'ROOT',root):
            for name in ('native-alpha','native-beta'):
                c=self.cfg();c['job']=name
                plan=self.root/(name+'-plan.json');q.save(plan,c)
                ref=dict(path=q.relative(plan),sha256=q.digest(plan))
                s=self.spec(c);s['capture']['plan']=ref;s['inputs']=[ref];s['evidence']['reads']=[ref['path']]
                path=self.root/(name+'-spec.json');q.save(path,s)
                self.assertEqual(q.submit(path,self.root/'queue',q.MODULES),'submitted')
                s['hypothesis']='Changed';q.save(path,s,replace=True)
                with self.assertRaisesRegex(ValueError,'job_exists'):q.submit(path,self.root/'queue',q.MODULES)

if __name__=='__main__':unittest.main()
