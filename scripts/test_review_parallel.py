"""Generated offline fixtures; all inference paths mocked, never load weights."""
import copy
import json
import subprocess
import sys
import unittest
from unittest.mock import patch
import human_annotation_review as h
import human_focus_evaluation as e
import human_focus_roles as roles
import human_regression_review as review
import human_review_qa as qa
import human_recording_audit as recorder
import test_human_focus_evaluation as legacy


class RoleTests(legacy.EvaluationTests):
    def setUp(self):
        super().setUp()
        self.complete = self.f.root/'completeness.json'
        review.attest_completeness(self.revision, ['frame-0','frame-1'], self.complete)
        self.role_doc = dict(version=roles.VERSION, **h.FLAGS, approved=True, reviewer='generated-test',
            authorizationReference='fixture-only', role=e.ROLE, revision=h.ref(self.revision),
            crops=h.ref(self.crops), completeness=h.ref(self.complete),
            populations=dict(candidate=[r['id'] for r in self.rows], auxiliary=[], unresolved=[]),
            frames=[dict(id=f, settlement='settled', coverage='complete') for f in ['frame-0','frame-1']])
        self.admission = self.f.root/'admission.json'
        h.write(self.admission, self.role_doc, sealed=True)

    def role_protocol(self):
        spec = dict(self.spec, version='human-focus-evaluation-approval-v2', admission=h.ref(self.admission), pairs=[])
        p = self.f.root/'role-approval.json'; self.f.dump(p,spec)
        protocol = self.f.root/'role-protocol.json'
        return protocol, e.freeze(p,protocol)

    def test_role_full_freeze_run_render_and_retained_no_runtime(self):
        protocol, doc = self.role_protocol()
        self.assertEqual(doc['version'], e.ROLE_VERSION)
        def fake(name,doc,predictions,receipts):
            predictions.extend(dict(id=r['id'],probability=float(r['label'])) for r in doc['samples'])
        with patch.object(e,'infer',side_effect=fake): result=e.run(protocol,self.f.root/'run')
        self.assertTrue(result['completed'])
        m=result['results']['shipped']['metrics']
        self.assertEqual(m['completeFrameSelection']['counts'],dict(unique_correct=1,unavailable=1))
        with patch.object(e,'runtime',side_effect=AssertionError('no runtime')):
            e.render(protocol,self.f.root/'run/comparison.json',self.f.root/'role-render')

    def test_partition_rejects_bad_membership_coverage_and_role(self):
        for mutate in [lambda d:d.update(approved=False),lambda d:d.update(role='final-challenge'),
                       lambda d:d['populations']['candidate'].pop(),
                       lambda d:d['populations']['auxiliary'].append(self.rows[0]['id']),
                       lambda d:d['frames'].pop(),
                       lambda d:d['frames'][0].update(settlement='disputed'),
                       lambda d:d.update(pairIDs=['invented'])]:
            d=copy.deepcopy(self.role_doc);mutate(d)
            with self.assertRaises(ValueError):roles.partition(self.report,d,{'frame-0','frame-1'})
        with self.assertRaises(ValueError):roles.partition(self.report,self.role_doc,set())

    def test_auxiliary_exclusion_incomplete_disputed_empty_and_ties(self):
        rows=[dict(self.rows[0],id='a'),dict(self.rows[0],id='b',label=0),
              dict(self.rows[0],id='decoration',label=0)]
        policy=dict(populations=dict(candidate=['a','b'],auxiliary=['decoration'],unresolved=[]),
                    frames=[dict(id='frame-0',settlement='settled',coverage='complete')])
        def score(values,pol=policy):return e.metrics(rows,[dict(id=r['id'],probability=v) for r,v in zip(rows,values)],[],pol)
        for values,expected in [([.9,.1,1],'unique_correct'),([.1,.9,0],'wrong'),([.1,.1,0],'no_focus'),([.9,.9,0],'multiple_focus')]:
            m=score(values);self.assertEqual(m['completeFrameSelection']['counts'],{expected:1})
        d=copy.deepcopy(policy);d['frames'][0].update(coverage='incomplete',reason='partial')
        self.assertEqual(score([.9,.1,0],d)['completeFrameSelection']['supported'],0)
        d['frames'][0].update(settlement='disputed')
        self.assertEqual(score([.9,.1,0],d)['candidate']['status'],'unavailable')
        for bad in [[dict(id='a',probability=.9)], [dict(id=r['id'],probability=float('nan')) for r in rows]]:
            with self.assertRaises(ValueError):e.metrics(rows,bad,[],policy)

    def test_changed_admission_hash_rejected(self):
        protocol,doc=self.role_protocol()
        self.admission.write_text('{}')
        with self.assertRaises(ValueError):e.validate(doc)

    def test_revision_v2_actual_roles_admitted_not_detector_mapped(self):
        # Build a new human fixture revision through the actual editor importer.
        for p in (self.f.batch/'editor').glob('*.json'):
            d=h.read(p);d['shapes'][0]['label']='focus:tabItem';self.f.dump(p,d)
        rp=self.f.root/'role-revision'
        h.finish(self.f.batch/'batch.json',rp,reviewer='fixture',reference='test',reviewer_kind='human',confirm_batch=True)
        cp=self.f.root/'role-crops';h.crop_qa(self.f.batch/'batch.json',cp,rp/'revision.json')
        with self.assertRaisesRegex(ValueError,'separate_admission'):e.admitted(rp/'revision.json',cp/'crop-qa.json')
        d=copy.deepcopy(self.role_doc);d.update(revision=h.ref(rp/'revision.json'),crops=h.ref(cp/'crop-qa.json'),completeness=None)
        d.pop('seal',None)
        d['frames']=[dict(id=f,settlement='settled',coverage='unknown',reason='fixture incomplete') for f in ['frame-0','frame-1']]
        p=self.f.root/'role-admit2.json';h.write(p,d,sealed=True)
        report,rows=e.admitted(rp/'revision.json',cp/'crop-qa.json',p)
        self.assertEqual({r['control'] for r in rows},{'focus:tabItem'})
        self.assertTrue(all(r['class'] is None for r in rows))
        spec=dict(self.spec,version='human-focus-evaluation-approval-v2',admission=h.ref(p),
                  revision=h.ref(rp/'revision.json'),crops=h.ref(cp/'crop-qa.json'),pairs=[],coverage=report['coverage'])
        ap=self.f.root/'v2-approval.json';self.f.dump(ap,spec)
        protocol=self.f.root/'v2-protocol.json';doc=e.freeze(ap,protocol)
        def fake(name,doc,predictions,receipts):
            predictions.extend(dict(id=r['id'],probability=0.0) for r in doc['samples'])
        with patch.object(e,'infer',side_effect=fake):result=e.run(protocol,self.f.root/'run')
        self.assertTrue(result['completed']);self.assertEqual(result['results']['shipped']['metrics']['completeFrameSelection']['supported'],0)

    def test_qa_real_crop_path_and_cli_reuse_preserve_sources(self):
        before=h.sha(self.revision)
        result=qa.run(self.revision,self.f.root/'qa',completeness=self.complete)
        self.assertTrue(result['completed']);self.assertFalse(result['trainingEligible'])
        p=subprocess.run([sys.executable,str(h.ROOT/'scripts/human_review_qa.py'),str(self.revision),
            str(self.f.root/'cli-qa'),'--crops',str(self.crops),'--completeness',str(self.complete)],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(before,h.sha(self.revision))
        with self.assertRaises(ValueError):qa.run(self.revision,self.f.root/'qa')

    def test_qa_missing_changed_inputs_and_partial_fail_closed(self):
        p=h.checked(h.ROOT,self.rows[0]['crop']);p.write_bytes(b'bad')
        result=qa.run(self.revision,self.f.root/'bad-qa',crops=self.crops)
        self.assertFalse(result['completed']);self.assertEqual(result['stage'],'audit')
        result=qa.run(self.f.root/'absent',self.f.root/'missing-qa')
        self.assertFalse(result['completed']);self.assertTrue((self.f.root/'missing-qa/handoff.json').exists())

    def test_qa_pending_and_final_challenge_rejected_without_crops(self):
        p=next((self.f.batch/'editor').glob('*.json'));d=h.read(p)
        d['flags']['reviewed']=False;self.f.dump(p,d)
        directory=self.f.root/'pending'
        h.finish(self.f.batch/'batch.json',directory,reviewer='test',reference='test',reviewer_kind='human',confirm_batch=True)
        with patch.object(h,'crop_qa',side_effect=AssertionError('no pending crop launch')):
            result=qa.run(directory/'revision.json',self.f.root/'pending-qa')
        self.assertFalse(result['completed']);self.assertTrue(result['blockedFrames'])
        d=h.read(self.revision);d['partition']='final-challenge';d.pop('seal')
        bad=self.f.root/'challenge.json';h.write(bad,d,sealed=True)
        self.assertFalse(qa.run(bad,self.f.root/'challenge-qa')['completed'])


def recording():
    m=dict(schemaVersion=2,sessionID='session',targetDeviceID='device')
    events=[dict(dispatch=dict(actionID='a',command={'press':'right'},target='device',monotonicNanoseconds=100))]
    events.append(dict(action={'_0':dict(actionID='a',targetDeviceID='device',command={'press':'right'},outcome='completed',
        connectionGeneration=1,preFrameHash='pre',commandTiming={k:dict(monotonic=dict(nanoseconds=n)) for k,n in [('enqueued',100),('transmitted',101),('completed',102)]})}))
    for ident,t,role in [('pre',90,'preInput'),('post',120,'postInputSettled')]:
        events.append(dict(frame={'_0':dict(frameID=ident,sourceDeviceID='device',connectionGeneration=1,
            capturedMonotonicNanoseconds=t,sha256=ident,role=role)}))
        events.append(dict(association=dict(actionID='a',frameID=ident,sha256=ident,role=role)))
    return m,events


class RecordingTests(unittest.TestCase):
    def test_good_and_deterministic(self):
        m,es=recording();r=recorder.analyze(m,es)
        self.assertEqual(r,recorder.analyze(m,es));self.assertEqual(r['counts']['associatedReady'],1)
        self.assertFalse(r['actions'][0]['trainingEligible'])

    def test_unknown_hash_generation_and_next_input(self):
        for mutation,reason in [(lambda es:es[-1]['association'].update(sha256='wrong'),'association_hash_mismatch'),
                               (lambda es:es[-1]['association'].update(frameID='absent'),'unknown_frame')]:
            m,es=recording();mutation(es);r=recorder.analyze(m,es)
            self.assertIn(reason,[i['reason'] for i in r['issues']]);self.assertEqual(r['counts']['associatedReady'],0)
        m,es=recording();es[-2]['frame']['_0']['connectionGeneration']=2
        self.assertIn('generation_mismatch',recorder.analyze(m,es)['actions'][0]['reasons'])
        m,es=recording();es.append(dict(dispatch=dict(actionID='b',command={},target='device',monotonicNanoseconds=110)))
        r=recorder.analyze(m,es);self.assertIn('post_frame_after_next_dispatch',r['actions'][0]['reasons'])

    def test_failed_dispatch_noop_not_inferred_duplicates_wrong_target(self):
        m,es=recording();es[1]['action']['_0']['outcome']='failed'
        self.assertIn('dispatch_not_completed',recorder.analyze(m,es)['actions'][0]['reasons'])
        m,es=recording();es[-2]['frame']['_0']['sha256']='pre';es[-1]['association']['sha256']='pre'
        r=recorder.analyze(m,es);self.assertTrue(r['actions'][0]['repeatedPrePostBytes']);self.assertNotIn('noOp',r['actions'][0])
        with self.assertRaises(ValueError):recorder.analyze(m,es+[es[0]])
        es[0]['dispatch']['target']='wrong'
        with self.assertRaises(ValueError):recorder.analyze(m,es)


if __name__ == '__main__':unittest.main()
