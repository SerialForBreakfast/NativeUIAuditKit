"""Check endpoint-only intake boundaries without model execution."""
import copy
import unittest
from unittest.mock import patch
import research_queue as q
import sdk_endpoint_focus520 as m
from native_selection404 import outcome

class EndpointTests(unittest.TestCase):
    def setUp(self):
        self.path=q.ROOT/'reports/work/STREAM520/prepared-r2/sdk520-focus-01-r2-request.json'
        self.request=q.load(self.path)

    def test_retained_endpoint_scope(self):
        rows=m.prepare(self.request)
        self.assertEqual(len(rows),len({r['sha256'] for r in rows}))
        self.assertTrue(all(r['profile']=='unknown' and not r['trainingEligible'] for r in rows))
        self.assertTrue(any(r['truth'] is None for r in rows))
        self.assertTrue(any(r['truth'] is not None for r in rows))

    def test_duplicate_pixels_rejected(self):
        r=copy.deepcopy(self.request);r['endpoints'].append(r['endpoints'][0])
        with self.assertRaisesRegex(ValueError,'endpoint_duplicate'):m.prepare(r)

    def test_changed_manifest_rejected(self):
        r=copy.deepcopy(self.request);r['endpoints'][0]['manifest']['sha256']='0'*64
        with self.assertRaises(ValueError):m.prepare(r)

    def test_wrong_case_rejected(self):
        r=copy.deepcopy(self.request);r['endpoints'][0]['caseID']='wrong-case'
        with self.assertRaisesRegex(ValueError,'sdk508_packet_identity'):m.prepare(r)

    def test_unknown_focus_rejected(self):
        from sdk_packet502 import review
        with patch('sdk_campaign508.review',return_value=dict(reviewable=False)):
            with self.assertRaisesRegex(ValueError,'sdk508_packet_unreviewable'):m.prepare(self.request)

    def test_no_focus_and_wrong_selection(self):
        b=[[0,0,20,20],[40,40,20,20]]
        self.assertEqual(outcome([.1,.2],b,None),'correct-abstention')
        self.assertEqual(outcome([.9,.2],b,None),'false-selection')
        self.assertEqual(outcome([.1,.9],b,b[0]),'wrong')
        self.assertEqual(outcome([.9,.1],b,b[0]),'correct')

    def test_build_declares_all_reads(self):
        spec=m.build(self.path);q.validate(spec)
        self.assertEqual(spec['authority'],'diagnostic')
        self.assertEqual(spec['limits']['maxAttempts'],1)
        self.assertIn(self.request['tool']['path'],spec['evidence']['reads'])

if __name__=='__main__':unittest.main()

class ProposalTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        from pathlib import Path
        self.temp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.request=q.load(q.ROOT/'reports/work/UNBLOCK527/proposals/sdk527-proposals-01-request.json')

    def altered(self,change):
        from experiment_templates import checked,pin
        r=copy.deepcopy(self.request);ref=r['proposals']['candidate']['predictions'][0]
        raw=q.load(checked(ref));change(raw);p=self.root/'raw.json';q.save(p,raw)
        r['proposals']['candidate']['predictions'][0]=pin(p)
        return r

    def test_matched_inputs_and_declared_reads(self):
        from experiment_templates import pin
        frames=m.prepare(self.request);arms=m.proposal_inputs(self.request,frames)
        self.assertEqual(len(arms['baseline']),len(frames))
        p=self.root/'request.json';q.save(p,self.request);spec=m.build(p);q.validate(spec)
        self.assertEqual(len(spec['evidence']['reads']),len(set(spec['evidence']['reads'])))
        self.assertIn(self.request['proposals']['candidate']['predictions'][0]['path'],spec['evidence']['reads'])

    def test_changed_pixels_rejected(self):
        r=self.altered(lambda d:d.update(inputSHA256='0'*64))
        with self.assertRaisesRegex(ValueError,'endpoint_proposal_pixels'):m.prepare(r)

    def test_changed_detector_rejected(self):
        r=self.altered(lambda d:d['runtime']['detector'].update(weightsSHA256='0'*64))
        with self.assertRaisesRegex(ValueError,'endpoint_proposal_detector_changed'):m.prepare(r)

    def test_wrong_coordinates_rejected(self):
        r=self.altered(lambda d:d.update(coordinates='normalized bottom-left'))
        with self.assertRaisesRegex(ValueError,'endpoint_proposal_coordinates'):m.prepare(r)

    def test_bad_box_is_reported_not_silently_clipped(self):
        r=self.altered(lambda d:d['runtime']['result']['elements'][0]['boundingBoxPixels'].update(x=-10))
        frames=m.prepare(r);arms=m.proposal_inputs(r,frames)
        self.assertEqual(len(arms['candidate'][0]['rejected']),1)

    def test_changed_crop_weights_rejected(self):
        r=copy.deepcopy(self.request);r['models']['baseline']=q.load(q.ROOT/'reports/work/STREAM520/prepared-r2/sdk520-focus-01-r2-request.json')['models']['baseline']
        with self.assertRaisesRegex(ValueError,'endpoint_proposal_crop_changed'):m.prepare(r)

    def test_two_campaigns_run_through_queue(self):
        from experiment_templates import pin
        import research_approval as approval
        queue=self.root/'queue'
        for i in range(2):
            r=copy.deepcopy(self.request);r['id']=f'endpoint-proposal-test-{i}'
            # Use one distinct retained frame per campaign, through the real crop scorer.
            r['endpoints']=[r['endpoints'][i+1]]
            for arm in r['proposals'].values():arm['predictions']=[arm['predictions'][i+1]]
            request=self.root/(r['id']+'-request.json');q.save(request,r)
            spec=m.build(request);path=self.root/(r['id']+'.json');q.save(path,spec)
            q.submit(path,queue);approval.approve(queue,r['id'],'agent:test','Qualify the retained proposal comparison through an isolated queue.')
            q.run(queue,job_ids=[r['id']],lock=self.root/'lock',max_jobs=1)
            state,attempts=q.state(queue/'jobs'/r['id'])
            self.assertEqual(state,'complete',q.load(attempts[-1]/'result.json'))
            doc=q.load(attempts[-1]/'out/benchmark_summary.json')
            self.assertEqual(doc['comparison'],'detector-confidence')
            self.assertIn('knownBoxDiagnostic',doc['rows'][0])
