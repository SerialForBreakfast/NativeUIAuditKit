"""Software qualification only. Generated test images do not measure model quality."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import research_queue as q
from experiment_templates import pin
import consumer_crop_comparison as m
from test_sdk_episode529 import EpisodeTests
from sdk_episode_crops530 import normalize
from sdk_training513 import prepare_crops


class Outcomes(unittest.TestCase):
    def rows(self, labels=(1,0)):
        return [dict(id=f'r{i}',frame='f',label=v,image=dict(path='f.png',sha256='a'*64),
                     group='g',role='review_only',profile='unknown',family='test') for i,v in enumerate(labels)]
    def refs(self,state):
        return [dict(id='f',focusState=state,image=dict(path='f.png',sha256='a'*64),
                     group='g',role='review_only',profile='unknown',family='test')]
    def test_focused_success_wrong_miss_and_multiple(self):
        for scores,outcome in [([.85,.1],'correct'),([.1,.85],'wrong'),([.84,.7],'miss'),([.9,.9],'miss')]:
            self.assertEqual(m.summarize(self.rows(),scores,self.refs('focused'))['frameCounts'],{outcome:1})
    def test_unique_inputs_do_not_turn_repeats_into_independent_evidence(self):
        rows=self.rows((1,1));rows[0]['modelInputRGBSHA256']=rows[1]['modelInputRGBSHA256']='a'*64
        out=m.unique_input_summary(rows)
        self.assertEqual(out['presentations'],2);self.assertEqual(out['uniqueModelInputs'],1)
        self.assertEqual(out['uniquePositiveInputs'],1)
        rows[1]['label']=0;self.assertEqual(len(m.unique_input_summary(rows)['conflictingLabels']),1)
        rows[1].pop('modelInputRGBSHA256');self.assertEqual(m.unique_input_summary(rows)['missingInputIdentity'],['r1'])
        unknown=dict(rows[0],label=0,category='unknown')
        counted=m.unique_input_summary([unknown]);self.assertEqual(counted['uniqueNegativeInputs'],0)
        self.assertEqual(counted['unknownReferencePresentations'],1)

    def test_known_no_focus_is_not_a_miss(self):
        for scores,outcome in [([.1,.69],'correct_abstention'),([.7,.84],'correct_abstention'),
                               ([.9,.1],'false_selection'),([.9,.9],'correct_abstention')]:
            out=m.summarize(self.rows((0,0)),scores,self.refs('no_focus'))
            self.assertEqual(out['frameCounts'],{outcome:1})
        out=m.summarize(self.rows((0,0)),[.9,.9],self.refs('no_focus'))
        self.assertEqual(out['rows'][0]['abstentionReason'],'multiple')
        self.assertEqual(out['rows'][0]['aboveThreshold'],2)
    def test_unknown_is_unscored_even_with_negative_placeholders(self):
        for labels in [(None,None),(0,0)]:
            out=m.summarize(self.rows(labels),[.9,.1],self.refs('unknown'))
            self.assertEqual(out['scoredFrames'],0);self.assertEqual(out['unknownReferenceFrames'],1)
            self.assertEqual(out['counts'],{'unknown':2})
    def test_no_reference_does_not_infer_no_focus(self):
        self.assertEqual(m.summarize(self.rows((0,0)),[.1,.1])['frameCounts'],{'miss':1})
    def test_empty_known_no_focus_and_unknown_remain_in_denominator(self):
        self.assertEqual(m.summarize([],[],self.refs('no_focus'))['frameCounts'],{'correct_abstention':1})
        self.assertEqual(m.summarize([],[],self.refs('unknown'))['scoredFrames'],0)
    def test_conflicts_missing_references_duplicates_and_bad_scores_fail(self):
        with self.assertRaisesRegex(ValueError,'frame_label_conflict'):m.summarize(self.rows(),[.1,.1],self.refs('no_focus'))
        with self.assertRaisesRegex(ValueError,'frame_references'):m.summarize(self.rows(),[.1,.1],[])
        with self.assertRaisesRegex(ValueError,'score_count'):m.summarize(self.rows()+self.rows(),[.1]*4)
        for score in (float('nan'),float('inf'),True,-.01,1.01):
            with self.assertRaisesRegex(ValueError,'probability'):m.summarize(self.rows(),[score,.1])


class SDKContracts(unittest.TestCase):
    def setUp(self):
        self.helper=EpisodeTests();self.helper.setUp();self.addCleanup(self.helper.doCleanups)
        self.root=self.helper.root
        self.tool=pin(q.ROOT/'.build/arm64-apple-macosx/debug/FocusRingTool')
        req=self.helper.request('consumer578')
        self.helper.edit(req,1,lambda e:[e[s].update(focusID=None) for s in ('before','after')])
        self.episodes=self.root/'episodes.json';q.save(self.episodes,req)
        normalized=normalize(dict(version='sdk-episode-crops-v1',id='consumer578',episodes=pin(self.episodes),tool=self.tool))
        self.source=prepare_crops(normalized,self.root/'crops',self.tool)
        self.source_path=self.root/'crops.json';q.save(self.source_path,self.source)
        self.manifest=dict(version='consumer-sdk-crops-v1',sourceCrops=pin(self.source_path))
    def load(self):return m.sdk_membership(self.manifest,self.tool)
    def change(self,fn):
        fn(self.source);q.save(self.source_path,self.source,replace=True);self.manifest['sourceCrops']=pin(self.source_path)
    def test_complete_native_labels_preserve_roles_and_unknown_profile(self):
        rows,frames=self.load()
        self.assertEqual([r['label'] for r in rows],[1,0])
        self.assertEqual([f['focusState'] for f in frames],['focused','no_focus'])
        self.assertTrue(all(r['role']=='review_only' and r['profile']=='unknown' for r in rows))
    def test_role_label_group_geometry_and_membership_changes_fail(self):
        original=copy.deepcopy(self.source)
        changes=[lambda d:d['rows'][0].update(role='development'),lambda d:d['rows'][0].update(label=0),
                 lambda d:d['rows'][0].update(group='other'),lambda d:d['rows'][0].update(box=[0,0,10,10]),
                 lambda d:d['frames'][0].update(profile='hcf'),lambda d:d['rows'].pop()]
        for change in changes:
            self.source=copy.deepcopy(original);self.change(change)
            with self.assertRaises(ValueError):self.load()
    def test_changed_source_and_crop_hashes_fail(self):
        crop=Path(self.source['rows'][0]['path']);crop.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'crop_hash'):self.load()
    def test_real_queue_connection_with_generated_software_checkpoint(self):
        import torch
        import research_approval as approval
        import hcf_templates395 as compiler
        from train_focus_ring_detector import load_mobilenetv4_conv_small
        torch.manual_seed(578)
        model=load_mobilenetv4_conv_small()(pretrained=False,num_classes=1)
        checkpoint=self.root/'software-only.pt';torch.save(dict(state_dict=model.state_dict()),checkpoint)
        membership=self.root/'membership.json';q.save(membership,self.manifest)
        doc=dict(version='hcf-template-description-v1',id='consumer578-software',task='NATIVE578',owner='test-NUIAK',
            template='T63',question='Does the real queue score review-only native crops without changing their roles?',
            decision='Check exact membership and crop hashes. These generated samples test software only.',
            inputs=dict(membership=pin(membership),model=pin(checkpoint),tool=self.tool),parameters=dict(backend='pytorch'),dependencies=[])
        queue=self.root/'queue';spec=compiler.build(doc);sp=self.root/'spec.json';q.save(sp,spec)
        self.assertIn(pin(self.source_path),spec['inputs'])
        q.submit(sp,queue);approval.approve(queue,spec['id'],'test','Software-only queue qualification with generated checkpoint.')
        result=q.run(queue,max_jobs=1,job_ids=[spec['id']],lock=self.root/'worker.lock')
        job=queue/'jobs'/spec['id'];self.assertEqual(result,[(spec['id'],'complete')],str(q.load(job/'attempts/1/result.json')))
        report=q.load(job/'attempts/1/out/benchmark_summary.json')
        self.assertEqual(report['model'],pin(checkpoint));self.assertEqual(len(report['rows']),2)
        self.assertEqual(report['peerParity']['cropMatches'],2)
        self.assertFalse(report['modelAccepted']);self.assertFalse(report['trainingEligible'])
        self.assertEqual({r['role'] for r in report['crops']},{'review_only'})
        altered=copy.deepcopy(report);altered['crops'][0]['modelInputRGBSHA256']='f'*64
        with self.assertRaisesRegex(ValueError,'crop_changed'):m.compare_reports(report,altered)
        altered=copy.deepcopy(report);altered['rows'].pop()
        with self.assertRaisesRegex(ValueError,'frames'):m.compare_reports(report,altered)
        self.assertEqual(m.compare_reports(report,report)['counts'],dict(gained=0,lost=0,newWrong=0))
        aggregate=dict(version='research-spec-v2',id='consumer578-aggregate',task='NATIVE578',owner='test-NUIAK',
            kind='screen',authority='diagnostic',jobKind='artifact',question='Does cached comparison run through the actual queue caller?',
            hypothesis='Identical software results give no gains, losses, or new wrong decisions.',
            controlledComparison='Generated software-only fixture. No scientific acceptance.',decisionRule='Reject changed membership or hashes.',
            nextActionByOutcome=dict(supported='Keep the verified software connection.',contradicted='Repair the exact reporting failure.'),
            inputs=[pin(q.MODULES/'consumer_crop_comparison.py')],
            dependencies=[dict(job=spec['id'],specSHA256=q.text_digest(spec),outputs=['benchmark_summary.json'])],
            template=dict(inputs={side+'_software':dict(job=spec['id'],output='benchmark_summary.json') for side in ('baseline','candidate')},parameters={}),
            adapter=dict(type='python-callable',steps=['consumer_crop_comparison.compare'],outputAttributes=['consumer_crop_comparison.OUT']),
            evidence=dict(reads=[],artifactReceipt='artifact-receipt.json'),limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1))
        ap=self.root/'aggregate.json';q.save(ap,aggregate);q.submit(ap,queue)
        approval.approve(queue,aggregate['id'],'test','Synthetic comparison caller qualification only.')
        self.assertEqual(q.run(queue,max_jobs=1,job_ids=[aggregate['id']],lock=self.root/'aggregate.lock'),[(aggregate['id'],'complete')])
        result=q.load(queue/'jobs'/aggregate['id']/'attempts/1/out/benchmark_summary.json')
        self.assertEqual(result['frames'],2);self.assertFalse(result['modelAccepted'])


if __name__=='__main__':unittest.main()
