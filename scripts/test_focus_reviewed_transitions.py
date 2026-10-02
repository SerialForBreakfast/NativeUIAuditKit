"""Immutable review integration, real CLI and truth-isolated transition scoring."""
import copy
import json
import subprocess
import sys
import unittest
from unittest.mock import patch
import human_annotation_review as h
import human_regression_review as regression
import focus_recorded_readiness as readiness
import focus_recorded_transition_eval as evaluation
import focus_transition_stress as stress
import test_human_annotation_review as annotation
import test_human_recording_review as recording
import test_focus_artwork_readiness as baseline


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.f=annotation.ReviewTests();self.f.setUp();self.addCleanup(self.f.tearDown)
        self.f.imported();self.f.annotate();self.f.finish()
        self.batch=self.f.batch/'batch.json';self.revision=self.f.root/'revision/revision.json'

    def test_saved_revision_and_completeness(self):
        frames=readiness.reviewed_frames({'samples':[]},self.batch,self.revision)
        self.assertEqual(len(frames),2);self.assertTrue(all(not f['complete'] for f in frames.values()))
        path=self.f.root/'complete.json'
        regression.attest_completeness(self.revision,['frame-0'],path)
        frames=readiness.reviewed_frames({'samples':[]},self.batch,self.revision,path)
        self.assertEqual(sum(f['complete'] for f in frames.values()),1)
        # Working editor changes do not alter immutable truth.
        self.f.annotate(lambda d:d['shapes'][0]['flags'].update(focused=False,unfocused=True))
        self.assertEqual(frames,readiness.reviewed_frames({'samples':[]},self.batch,self.revision,path))

    def test_snapshot_tamper_rejected(self):
        p=next((self.revision.parent/'editor-snapshot').glob('*.json'));p.write_text('{}')
        with self.assertRaises(ValueError):readiness.reviewed_frames({'samples':[]},self.batch,self.revision)

    def test_foreign_batch_and_software_review_rejected(self):
        f=annotation.ReviewTests();f.setUp();self.addCleanup(f.tearDown);f.imported()
        with self.assertRaisesRegex(ValueError,'wrong_batch'):
            readiness.reviewed_frames({'samples':[]},f.batch/'batch.json',self.revision)
        other=self.f.root/'software'
        h.finish(self.batch,other,reviewer='test',reference='generated only',reviewer_kind='software-test',confirm_batch=True)
        with self.assertRaisesRegex(ValueError,'requires_human'):
            readiness.reviewed_frames({'samples':[]},self.batch,other/'revision.json')

    def test_pending_frames_are_not_truth(self):
        self.f.annotate(lambda d:d['flags'].update(reviewed=False))
        path=self.f.root/'pending'
        h.finish(self.batch,path,reviewer='test',reference='generated only',reviewer_kind='human',confirm_batch=True)
        self.assertEqual(readiness.reviewed_frames({'samples':[]},self.batch,path/'revision.json'),{})

    def test_conflicting_frozen_truth_rejected(self):
        r=h.read_revision(self.revision)['frames'][0];c=r['controls'][0]
        sample=dict(c,image=r['image'],screen=r['screen'],use='representative-selection',state='unfocused')
        with self.assertRaisesRegex(ValueError,'conflicts_with_frozen'):
            readiness.reviewed_frames({'samples':[sample]},self.batch,self.revision)

    def test_resealed_image_binding_tamper_rejected(self):
        r=h.read(self.revision);r['frames'][0]['image']=r['frames'][1]['image'];r.pop('seal')
        path=self.f.root/'rebound.json';h.write(path,r,sealed=True)
        with self.assertRaisesRegex(ValueError,'frame_binding'):
            readiness.reviewed_frames({'samples':[]},self.batch,path)


class ScoringTests(unittest.TestCase):
    def controls(self):
        return [dict(id='one',bounds=[10,10,100,30],state='unfocused',**{'class':'listRow'})]

    def test_scoring_truth_never_changes_prediction(self):
        before=self.controls();after=copy.deepcopy(before);after[0]['state']='focused'
        prediction=[dict(id='one',decision='arrival',tracking=dict(afterBounds=[10,10,100,30]))]
        first=evaluation.score(prediction,before,after)
        after[0]['state']='unfocused';second=evaluation.score(prediction,before,after)
        self.assertTrue(first[0]['correct']);self.assertFalse(second[0]['correct'])
        self.assertEqual(first[0]['decision'],second[0]['decision'])
        self.assertNotIn('expected',prediction[0])

    def test_ambiguous_both_directions_and_missing_match(self):
        b=self.controls();p=[dict(id='one',decision='arrival',tracking=dict(afterBounds=b[0]['bounds']))]
        a=copy.deepcopy(b);a.append(dict(a[0],id='two'))
        self.assertFalse(evaluation.score(p,b,a)[0]['scorable'])
        b.append(dict(b[0],id='two'));p.append(dict(p[0],id='two'))
        self.assertTrue(all(not r['scorable'] for r in evaluation.score(p,b,a[:1])))
        p[0]['tracking']={};self.assertFalse(evaluation.score(p[:1],b,a)[0]['scorable'])

    def test_abstentions_and_empty_support_not_accuracy(self):
        rows=[dict(scorable=True,expected='arrival',decision='unknown',correct=False),
              dict(scorable=True,expected='departure',decision='departure',correct=True),
              dict(scorable=False,expected=None,decision='unavailable',correct=None)]
        r=evaluation.summarize(rows)
        self.assertEqual(r['correctnessIncludingAbstentions'],.5)
        self.assertEqual(r['correctnessWhenDecided'],1)
        self.assertEqual(r['coverage'],1/3);self.assertEqual(r['unmatched'],1)
        self.assertIsNone(evaluation.summarize([])['correctnessIncludingAbstentions'])

    def test_prediction_rejects_truth_before_io(self):
        with self.assertRaisesRegex(ValueError,'truth_fields'):
            evaluation.predict({}, {}, self.controls())

    def test_actual_native_pixel_stress(self):
        f=annotation.ReviewTests();f.setUp();self.addCleanup(f.tearDown)
        r=stress.run(f.root/'stress')
        self.assertEqual(r['total'],9)
        by={c['name']:c for c in r['cases']}
        for name in ('unchanged','highlight','dim','scroll-highlight','scroll-only','duplicate','missing','illumination'):
            self.assertTrue(by[name]['passed'],by[name])
        self.assertTrue(any(c['runtime'] for c in r['cases']))

    def test_actual_cli_empty_recording_and_collision(self):
        f=recording.RecordingTests();f.setUp();self.addCleanup(f.tearDown);b=f.prepare()
        m=baseline.PipelineTests();m.setUp();self.addCleanup(m.tearDown)
        out=f.f.root/'eval.json'
        cmd=[sys.executable,str(h.ROOT/'scripts/focus_recorded_transition_eval.py'),
             '--batch',str(b),'--pending',str(b),'--baseline',str(m.path),'--output',str(out)]
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        doc=h.sealed(out,'focus-recorded-transition-eval-v1')
        self.assertIsNone(doc['summary']['correctnessIncludingAbstentions'])
        self.assertIsNone(doc['qualifiedTransitionAccuracy'])
        before=out.read_bytes();r=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
        self.assertNotEqual(r.returncode,0);self.assertEqual(out.read_bytes(),before)

    def test_reviewed_recording_full_cli_tracks_and_scores(self):
        f=recording.RecordingTests();f.setUp();self.addCleanup(f.tearDown)
        # Replace only this generated test recording with textured native-crop inputs.
        events=[];inventory=[]
        for n,im in enumerate((stress.scene(),stress.scene(dy=-100,shade=235))):
            temporary=f.source/f'generated-{n}.png';im.save(temporary);digest=h.sha(temporary)
            image=f.source/'images'/f'frame-{digest}.png';temporary.rename(image)
            frame=dict(frameID=f'f{n}',sequenceNumber=n,sourceDeviceID='office',role='postInputSettled',
                sha256=digest,capturedMonotonicNanoseconds=100+n*100,connectionGeneration=1)
            events.append(dict(frame={'_0':frame}));inventory.append(dict(sha256=digest,bytes=image.stat().st_size))
        events.extend([dict(dispatch=dict(actionID='a',target='office',command='down',monotonicNanoseconds=150)),
            dict(action={'_0':dict(actionID='a',targetDeviceID='office',command='down',outcome='completed',
                connectionGeneration=1,commandTiming={k:dict(monotonic=dict(nanoseconds=t))
                    for k,t in zip(('enqueued','transmitted','completed'),(151,152,153))})})])
        for n in range(2):events.append(dict(association=dict(actionID='a',frameID=f'f{n}',
            sha256=inventory[n]['sha256'],role='preInput' if n==0 else 'postInputSettled')))
        for name,rows in [('events.jsonl',events),('files.jsonl',inventory)]:
            (f.source/name).write_text('\n'.join(json.dumps(row) for row in rows))
        batch=f.prepare()
        for n,path in enumerate(sorted((batch.parent/'editor').glob('*.json'))):
            d=h.read(path);d['flags']={k:True for k in h.FRAME_FLAGS}
            y=200 if n==0 else 100
            d['shapes']=[dict(label='listRow',points=[[200,y],[360,y+60]],group_id=1,shape_type='rectangle',
                flags={k:k in (('unfocused','confirmed') if n==0 else ('focused','confirmed')) for k in h.SHAPE_FLAGS})]
            path.write_text(json.dumps(d))
        revdir=f.f.root/'reviewed'
        r=h.finish(batch,revdir,reviewer='unit-fixture',reference='generated test only',reviewer_kind='human',confirm_batch=True)
        self.assertEqual(r['frameCounts'],{'reviewed':2})
        model=baseline.PipelineTests();model.setUp();self.addCleanup(model.tearDown)
        out=f.f.root/'scored.json'
        cmd=[sys.executable,str(h.ROOT/'scripts/focus_recorded_transition_eval.py'),
            '--batch',str(batch),'--pending',str(batch),'--baseline',str(model.path),
            '--revision',str(revdir/'revision.json'),'--output',str(out)]
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        report=h.sealed(out,'focus-recorded-transition-eval-v1')
        self.assertEqual(report['readinessCounts']['annotatedMetadataReady'],1)
        self.assertEqual(report['summary']['correct'],1)
        self.assertEqual(report['actions'][0]['controls'][0]['expected'],'arrival')
        self.assertFalse(report['actions'][0]['completeEndpoints'])
        self.assertIsNone(report['qualifiedTransitionAccuracy'])
        # Same actual recording caller with only before truth: predictions remain
        # useful, but pending after checkboxes never become scoring labels.
        after_editor=sorted((batch.parent/'editor').glob('*.json'))[1]
        d=h.read(after_editor);d['flags']['reviewed']=False;after_editor.write_text(json.dumps(d))
        partial=f.f.root/'partial'
        h.finish(batch,partial,reviewer='unit-fixture',reference='generated test only',reviewer_kind='human',confirm_batch=True)
        observed=evaluation.run(batch,model.path,batch,partial/'revision.json',observe_pending=True)
        self.assertEqual(observed['actions'][0]['status'],'pixel-only')
        self.assertEqual(observed['observedDecisions'],{'arrival':1})
        self.assertEqual(observed['summary']['scorable'],0)
        self.assertIsNone(observed['summary']['correctnessIncludingAbstentions'])
        self.assertEqual(observed['summary']['unscoredReasons'],{'pending_human_after_review':1})


if __name__=='__main__':unittest.main()
