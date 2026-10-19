"""Test pre-publication checks without capture or model execution."""
import copy
from types import SimpleNamespace
from unittest import main
from unittest.mock import patch
import research_queue as q
import research_approval as approval
import workflow_campaign439 as campaign
import workflow_admission440 as admission
import test_model_decision434 as fixtures


class AdmissionTests(fixtures.DecisionTests):
    def campaign(self):
        request=dict(version='workflow-campaign-v1',id='preflight-test',decision=dict(plan=self.plan),branches=[
            dict(when='contradicted',jobs=[dict(id='audit-failures',kind='decision-audit',
                question='Which retained failures need a different proposal source?')])])
        path=self.root/'request.json';q.save(path,request)
        return campaign.compile_request(path,self.root/'compiled',self.queue)

    def test_pending_internal_producers_are_waits_not_errors(self):
        manifest=self.campaign();before=list(self.queue.rglob('*'))
        report=admission.inspect(manifest,self.queue,profile_sources=True)
        self.assertTrue(report['canRegister']);self.assertGreater(report['counts']['waiting'],0)
        self.assertFalse(report['approvalGranted']);self.assertFalse(report['executionChanged'])
        self.assertEqual(before,list(self.queue.rglob('*')))
        self.assertIn('sourceClosureSeconds',report['timings'])

    def test_missing_training_log_blocks_all_publication(self):
        manifest=self.pending_preparation()
        report=admission.inspect(manifest,self.queue)
        self.assertFalse(report['canRegister'])
        self.assertIn('experiment_log_missing',str(report))
        with self.assertRaisesRegex(ValueError,'campaign_preflight_failed'):
            campaign.admit(manifest,self.queue)
        self.assertFalse((self.queue/'jobs/pending-prepare').exists())
        self.assertFalse((self.queue/'jobs/pending-score').exists())

    def test_storage_exhaustion_blocks_without_publication(self):
        manifest=self.campaign()
        with patch.object(admission.shutil,'disk_usage',return_value=SimpleNamespace(free=0)):
            report=admission.inspect(manifest,self.queue)
            self.assertFalse(report['canRegister'])
            self.assertIn('approval_storage_insufficient',str(report))
        self.assertFalse((self.queue/'jobs/audit-failures').exists())

    def test_failed_producer_is_actionable_not_a_normal_wait(self):
        manifest=self.campaign();self.reinventory('native-candidate','failed')
        report=admission.inspect(manifest,self.queue)
        self.assertFalse(report['canRegister'])
        self.assertIn('producer_requires_review:native-candidate:failed',str(report))

    def test_changed_completed_evidence_is_blocked(self):
        manifest=self.campaign()
        q.save(self.queue/'jobs/native-candidate/attempts/1/out/selection.json',{},replace=True)
        report=admission.inspect(manifest,self.queue)
        self.assertFalse(report['canRegister'])
        self.assertIn('dependency_output_changed',str(report))

    def test_duplicate_manifest_ids_rejected(self):
        manifest=self.campaign();manifest['jobs'].append(copy.deepcopy(manifest['jobs'][0]))
        with self.assertRaisesRegex(ValueError,'admission_job_ids'):admission.inspect(manifest,self.queue)

    def test_profile_preserves_store_and_removes_disposable_copy(self):
        q.save(approval.path(self.queue),dict(version=approval.VERSION,jobs={},events=[]))
        original=approval.path(self.queue).read_bytes();folder=self.root/'profile'
        report=admission.profile_store(self.queue,folder,2)
        self.assertEqual(approval.path(self.queue).read_bytes(),original)
        self.assertEqual(list(folder.iterdir()),[])
        self.assertEqual(len(report['samples']),2)
        self.assertEqual(report['liveLockContention'],'not measured')

    def test_profile_write_failure_preserves_original_and_cleans_copy(self):
        q.save(approval.path(self.queue),dict(version=approval.VERSION,jobs={},events=[]))
        original=approval.path(self.queue).read_bytes();folder=self.root/'profile'
        with patch.object(q,'save',side_effect=OSError('disk full')):
            with self.assertRaisesRegex(OSError,'disk full'):admission.profile_store(self.queue,folder,1)
        self.assertEqual(approval.path(self.queue).read_bytes(),original)
        self.assertEqual(list(folder.iterdir()),[])


if __name__=='__main__':main()
