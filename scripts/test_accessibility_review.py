import copy
import os
import subprocess
import sys
import unittest
import accessibility_review as a
import human_annotation_review as h
import human_review_finish as finish
import test_human_annotation_review as fixture


class AccessibilityTests(unittest.TestCase):
    def setUp(self):
        self.f=fixture.ReviewTests();self.f.setUp();self.source=self.f.imported()
        self.evidence=dict(version=a.EVIDENCE,frames=[])
        for frame in self.source['frames']:
            ref=frame['observation']
            self.evidence['frames'].append(dict(frameID=frame['id'],ordinaryImageSHA256=frame['image']['sha256'],
                target='office',screen=frame['screen'],size=frame['size'],assistedImage=frame['image'],observation=ref,
                profiles={k:dict(focusStyle=v,verification='receipt',receipt=ref) for k,v in [('ordinary','default'),('assisted','highContrast')]},
                correspondence=dict(sameControl=True,sameViewport=True,settled=True,fresh=True,restored=True,candidateCount=1),
                focusChannel='input',focusedControlID='button',actionability='control',status='verified'))
        self.path=self.f.root/'evidence.json';self.output=self.f.root/'assisted'

    def tearDown(self): self.f.tearDown()

    def prepare(self):
        h.write(self.path,self.evidence)
        return a.prepare(self.f.batch/'batch.json',self.path,self.output,1,29)

    def test_real_review_caller_and_geometry_preserved(self):
        before=h.sha(self.f.batch/'batch.json');d=self.prepare()
        self.assertEqual(h.sha(self.f.batch/'batch.json'),before)
        self.assertEqual(h.validate_batch(self.output/'batch.json')['version'],a.VERSION)
        self.assertEqual(d['frames'][0]['proposals'][0]['bounds'],self.source['frames'][0]['proposals'][0]['bounds'])
        preview=finish.preview(self.output/'batch.json')
        self.assertTrue(preview)
        self.assertTrue((self.output/'review.md').exists())
        self.assertEqual(len(list((self.output/'editor').glob('*.json'))),2)

    def test_mismatch_matrix(self):
        frame=self.source['frames'][0];original=self.evidence['frames'][0]
        for key,value,reason in [('ordinaryImageSHA256','bad','ordinary_image_mismatch'),('target','other','target_mismatch'),
            ('screen','other','screen_or_viewport_mismatch'),('actionability','heading','nonactionable_or_unknown'),
            ('focusChannel','assistive','assistive_focus_not_input'),('focusedControlID','missing','unknown_control')]:
            r=copy.deepcopy(original);r[key]=value
            self.assertIn(reason,a.assess(frame,r,'office'))
        for key in ('sameControl','sameViewport','settled','fresh','restored'):
            r=copy.deepcopy(original);r['correspondence'][key]=False
            self.assertIn(key+'_unverified',a.assess(frame,r,'office'))
        r=copy.deepcopy(original);r['correspondence']['candidateCount']=2
        self.assertIn('ambiguous_identity',a.assess(frame,r,'office'))

    def test_flagged_rows_cannot_bulk_finish(self):
        self.evidence['frames'][0]['correspondence']['sameControl']=False
        self.prepare();doc=h.read(self.output/'editor'/ (self.source['frames'][0]['editorStem']+'.json'))
        self.assertTrue(doc['shapes'][0]['flags']['flagged'])
        self.assertFalse(doc['flags']['reviewed'])
        self.assertFalse(finish.preview(self.output/'batch.json')['frames'][0]['ready'])
        self.assertEqual(a.validate(self.output/'batch.json')['frames'][0]['accessibility']['targetedReview'],True)

    def test_changed_evidence_rejected(self):
        self.prepare();self.path.write_text('{}')
        with self.assertRaises(ValueError): a.validate(self.output/'batch.json')

    def test_missing_and_duplicate(self):
        self.evidence['frames']=[];d=self.prepare()
        self.assertTrue(all(f['accessibility']['targetedReview'] for f in d['frames']))
        e=dict(version=a.EVIDENCE,frames=[{'frameID':'a'},{'frameID':'a'}])
        with self.assertRaisesRegex(ValueError,'duplicate'): a.project(self.source,e,1,29)

    def test_actual_cli(self):
        h.write(self.path,self.evidence)
        r=subprocess.run([sys.executable,str(h.ROOT/'scripts/accessibility_review.py'),'--batch',str(self.f.batch/'batch.json'),
            '--evidence',str(self.path),'--output',str(self.output)],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(len(h.validate_batch(self.output/'batch.json')['frames']),2)

    def test_production_crop_qa_dispatch(self):
        self.prepare()
        result=h.crop_qa(self.output/'batch.json',self.f.root/'crops')
        self.assertEqual(result['completed'],2)
        self.assertEqual(result['labelStatus'],'proposals_only')

    def test_producer_report_is_advisory_and_bounds_do_not_transfer(self):
        p=self.f.root/'perception.json'
        d=dict(profile='stable',settingsEvidence='caller-declared',outlineCandidates=[dict(x=.1,y=.2,width=.3,height=.4)],
               interpretation='proposal only',banner=None)
        h.write(p,d);self.evidence['frames'][0]['perceptionReport']=h.ref(p)
        r=self.prepare()
        self.assertEqual(r['frames'][0]['accessibility']['perception']['outlineCandidates'],d['outlineCandidates'])
        self.assertEqual(r['frames'][0]['proposals'][0]['bounds'],self.source['frames'][0]['proposals'][0]['bounds'])

    def test_declared_profile_and_unknown_state_flagged(self):
        r=self.evidence['frames'][0];r['profiles']['assisted']['verification']='declared';r['status']='stale'
        d=self.prepare();reasons=d['frames'][0]['accessibility']['reasons']
        self.assertIn('assisted_profile_unverified',reasons);self.assertIn('observation_stale',reasons)


class AccessibilityGUI(unittest.TestCase):
    def test_editor_evidence_and_navigation(self):
        if not os.environ.get('NUIAK_GUI_TEST'): self.skipTest('Run in resident review environment')
        from unittest.mock import patch
        import human_review_editor as editor
        f=AccessibilityTests();f.setUp();previous=os.getcwd()
        try:
            f.prepare();os.environ['QT_QPA_PLATFORM']='offscreen';editor.configure(f.f.root/'runtime')
            from qtpy import QtWidgets
            app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
            w=editor.window(f.output/'batch.json',f.f.root/'runtime');w.show();app.processEvents()
            self.assertEqual(len(w.imageList),2)
            before=[[(p.x(),p.y()) for p in s.points] for s in w.canvas.shapes]
            def inspect(dialog):
                self.assertIsNotNone(dialog.findChild(QtWidgets.QLabel,'accessibilityEvidenceImage'))
                return QtWidgets.QDialog.Accepted
            with patch.object(QtWidgets.QDialog,'exec_',inspect):w.showAccessibilityEvidence()
            self.assertEqual(before,[[(p.x(),p.y()) for p in s.points] for s in w.canvas.shapes])
            self.assertFalse(w.dirty)
            w.loadFile(w.imageList[1]);app.processEvents();self.assertEqual(len(w.canvas.shapes),1)
            w.close()
        finally: os.chdir(previous);f.tearDown()


if __name__=='__main__': unittest.main()
