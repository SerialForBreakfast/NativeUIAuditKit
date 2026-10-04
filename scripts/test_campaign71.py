import copy
import json
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch
import stationary_campaign_journal as j
import prepare_transition_inputs as p
import focus_direct_transition as d
from test_transfer62 import StationaryTests
from test_prepared66 import PreparedTests


class ScopedInputs(PreparedTests):
    def test_model_only_changes_reuse_but_preprocessing_changes_reject(self):
        with patch.object(d,'collect',wraps=d.collect):
            # Publish the identical already-generated bank; no new source admission.
            arrays=p.load(self.mp,self.rows)
        out=self.root/'scoped'
        p.publish_bank(self.cp,self.ap,out,self.corpus,self.rows,arrays,p.DEFAULT_POLICY,True)
        path=out/'manifest.json'
        with patch.object(d,'pins',return_value={'differentModel':True}),patch.object(d,'model',side_effect=AssertionError('no model')):
            actual=d.training_bank(self.rows,d.h.ref(path))
            self.assertEqual(actual[0].shape,(5,6,64,96))
        with patch.object(p,'input_pins',return_value={'changedTransform':True}):
            with self.assertRaisesRegex(ValueError,'code_or_runtime_changed'):p.load(path,self.rows)
        with patch.dict(d.CONFIG,{'width':192}):
            with self.assertRaisesRegex(ValueError,'code_or_runtime_changed'):p.load(path,self.rows)


class CampaignTests(StationaryTests):
    def setup_campaign(self,two=False):
        self.case,self.raw=self.fixture()
        self.case_path=self.root/'case-bound.json';j.h.write(self.case_path,self.case)
        plan=dict(version='stationary-session-campaign-v1',cases=[dict(id='test',condition='boundary_noop',partition='development')],
            batches=[dict(id='batch-0',caseIDs=['test'])])
        self.runtime=dict(simulatorID='sim',fixtureRunID='run',buildSHA256='a'*64)
        pp=self.root/'plan.json';bp=self.root/'bindings.json'
        refs={'test':j.h.ref(self.case_path)}
        if two:
            second=copy.deepcopy(self.case);second['case_id']='second'
            sp=self.root/'second-bound.json';j.h.write(sp,second);refs['second']=j.h.ref(sp)
            plan['cases'].append(dict(id='second',condition='boundary_noop',partition='development'))
            plan['batches'].append(dict(id='batch-1',caseIDs=['second']))
        j.h.write(pp,plan);j.h.write(bp,dict(cases=refs,runtime=self.runtime))
        self.journal=self.root/'journal';self.dest=self.root/'attempt'
        return j.initialize(pp,bp,self.journal)

    def receipt(self,caseID='test',**kwargs):
        path=self.root/f'receipt-{len(list(self.root.glob("receipt-*")))}.json'
        j.h.write(path,dict(runtime=self.runtime,caseID=caseID,observedAtUTC='2026-10-03T00:00:00Z',
            authorityReference='test-only no device execution',**kwargs));return path

    def complete_case(self,v):
        v=j.record(self.journal,'test','start',self.receipt(ready=True),v['head'],self.dest)
        self.dest.mkdir()
        evidence=self.persist(self.case,self.raw)
        for name in ('before.png','after.png','before.json','after.json','transition-case.json'):
            shutil.copyfile(self.root/name,self.dest/name)
        v=j.record(self.journal,'test','complete',self.receipt(cleanupVerified=True,responsive=True,
            destination=str(self.dest.relative_to(j.h.ROOT))),v['head'])
        return v,self.dest/evidence.name

    def test_real_intake_once_resume_and_cli(self):
        v=self.setup_campaign();v,e=self.complete_case(v)
        v=j.ingest(self.journal,'test',e,v['head'])
        self.assertTrue(j.summary(v)['allInspectionAccepted']);self.assertFalse(j.summary(v)['trainingEligible'])
        with patch.object(j.intake,'run',side_effect=AssertionError('duplicate intake')):
            again=j.ingest(self.journal,'test',e,v['head'])
        self.assertEqual(v['head'],again['head'])
        frozen=j.freeze(self.journal,self.root/'corpus-frozen.json')
        self.assertEqual(len(frozen['records']),1)
        self.assertFalse(frozen['trainingEligible'])
        c=subprocess.run([sys.executable,str(j.h.ROOT/'scripts/stationary_campaign_journal.py'),'status','--root',str(self.journal)],capture_output=True,text=True)
        self.assertEqual(c.returncode,0,c.stderr);self.assertTrue(json.loads(c.stdout)['allInspectionAccepted'])
        (self.dest/'before.png').write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError,'changed_hash'):j.snapshot(self.journal)

    def test_interrupted_reconciliation_and_conflict(self):
        v=self.setup_campaign();old=v
        v=j.record(self.journal,'test','start',self.receipt(ready=True),v['head'],self.dest)
        with self.assertRaisesRegex(ValueError,'journal_conflict'):
            j.record(self.journal,'test','start',self.receipt(ready=True),old['head'],self.dest)
        self.assertEqual(j.summary(v)['missing'],[])
        v=j.record(self.journal,'test','interrupt',self.receipt(reason='uncertain cleanup'),v['head'])
        with self.assertRaisesRegex(ValueError,'reconciliation_required'):
            j.record(self.journal,'test','reconcile',self.receipt(cleanupVerified=False,retryAuthorized=True),v['head'])
        v=j.record(self.journal,'test','reconcile',self.receipt(cleanupVerified=True,retryAuthorized=True),v['head'])
        with self.assertRaisesRegex(ValueError,'attempt_collision'):
            j.record(self.journal,'test','start',self.receipt(ready=True),v['head'],self.dest)

    def test_wrong_runtime_and_cleanup(self):
        v=self.setup_campaign();r=self.receipt(ready=True);bad=j.h.read(r);bad['runtime']['simulatorID']='other';r.write_text(json.dumps(bad))
        with self.assertRaisesRegex(ValueError,'runtime_or_case_mismatch'):j.record(self.journal,'test','start',r,v['head'],self.dest)
        v=j.record(self.journal,'test','start',self.receipt(ready=True),v['head'],self.dest)
        with self.assertRaisesRegex(ValueError,'completion_unverified'):
            j.record(self.journal,'test','complete',self.receipt(cleanupVerified=False,responsive=True),v['head'])

    def test_invalid_labels_rejected_not_admitted(self):
        v=self.setup_campaign();self.raw['cleanup']='unknown';v,e=self.complete_case(v)
        v=j.ingest(self.journal,'test',e,v['head'])
        self.assertEqual(v['states']['test']['state'],'rejected')
        self.assertFalse(j.summary(v)['allInspectionAccepted'])

    def test_two_batches_resume_only_missing_and_preserve_first(self):
        v=self.setup_campaign(two=True);v,e=self.complete_case(v)
        v=j.ingest(self.journal,'test',e,v['head']);first=v['states']['test']['last']
        self.assertEqual(j.summary(v)['missing'],['second'])
        dest=self.root/'second-attempt'
        v=j.record(self.journal,'second','start',self.receipt(caseID='second',ready=True),v['head'],dest)
        dest.mkdir();raw=copy.deepcopy(self.raw);raw['case_id']='second'
        for name in ('before.png','after.png','before.json','after.json'):
            shutil.copyfile(self.dest/name,dest/name)
        j.h.write(dest/'transition-case.json',raw)
        v=j.record(self.journal,'second','complete',self.receipt(caseID='second',cleanupVerified=True,
            responsive=True,destination=str(dest.relative_to(j.h.ROOT))),v['head'])
        v=j.ingest(self.journal,'second',dest/'transition-case.json',v['head'])
        self.assertEqual(first,v['states']['test']['last'])
        frozen=j.freeze(self.journal,self.root/'two-frozen.json')
        self.assertEqual(len(frozen['records']),2);self.assertTrue(frozen['duplicateContentGroups'])

    def test_validator_change_and_partial_freeze(self):
        v=self.setup_campaign()
        with self.assertRaisesRegex(ValueError,'campaign_incomplete'):j.freeze(self.journal,self.root/'partial.json')
        with patch.object(j,'validator_pins',return_value={}):
            with self.assertRaisesRegex(ValueError,'intake_validator_changed'):j.snapshot(self.journal)

    def test_planned_visual_axes_must_match_bound_recipe(self):
        self.setup_campaign();plan=j.h.read(self.root/'plan.json')
        plan['cases'][0].update(referenceScreen='nostalgex_guide',seed=83,variant=0,theme='light',artworkStyle='city')
        path=self.root/'wrong-plan.json';j.h.write(path,plan)
        with self.assertRaisesRegex(ValueError,'planned_visual_coverage_mismatch'):
            j.initialize(path,self.root/'bindings.json',self.root/'wrong-journal')


if __name__=='__main__':unittest.main()
