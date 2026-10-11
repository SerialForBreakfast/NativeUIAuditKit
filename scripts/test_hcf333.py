"""Check HCF review compatibility without changing labels or model decisions."""
import copy
import unittest
import subprocess
import sys
import accessibility_review as a
import human_annotation_review as h
import test_accessibility_review as fixture


def report():
    return dict(profile='high_contrast_focus',settingsEvidence='caller_declared_not_verified',
        outlineCandidates=[],focusRules=dict(version=1,state='candidate',navigationEligible=False,
        settingsEvidence='not_verified_from_pixels',reasons=['identity_and_actionability_unverified'],
        candidates=[dict(bounds=dict(x=.1,y=.1,width=.2,height=.2),geometryRole='assisted_outline_proposal',
                         strategy='bright_outline',labels=[])]))


class HCFTests(unittest.TestCase):
    def test_preserves_both_geometry_roles(self):
        for role,strategy in [('assisted_outline_proposal','bright_outline'),
                              ('filled_row_proposal','row_fill_contrast_ocr')]:
            d=report();d['focusRules']['candidates'][0].update(geometryRole=role,strategy=strategy)
            result=a.parse_perception(d)
            self.assertEqual(result['focusRules'],d['focusRules'])
            self.assertTrue(result['proposalOnly'])
            self.assertFalse(result['navigationEligible'])

    def test_rejects_invalid_rule_contracts(self):
        for key,value in [('version',2),('version',True),('state','focused'),('navigationEligible',True),
                          ('settingsEvidence','verified'),('candidates',[]),('reasons',None)]:
            d=report();d['focusRules'][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError): a.parse_perception(d)
        for key,value in [('geometryRole','ordinary_body'),('contrast',float('nan')),('labels','focus')]:
            d=report();d['focusRules']['candidates'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError): a.parse_perception(d)

    def test_no_cue_is_abstention_not_no_focus(self):
        d=report();d['focusRules'].update(state='abstained',candidates=[],reasons=['no_supported_cue'])
        self.assertEqual(a.parse_perception(d)['focusRules']['state'],'abstained')
        self.assertNotIn('isFocused',a.parse_perception(d))

    def test_ambiguous_proposals_preserved(self):
        d=report();d['focusRules']['candidates']*=2;d['focusRules']['state']='abstained'
        self.assertEqual(len(a.parse_perception(d)['focusRules']['candidates']),2)

    def test_sidecar_integrates_with_existing_review(self):
        f=fixture.AccessibilityTests();f.setUp()
        try:
            image=f.source['frames'][0]['image'];path=h.checked(h.ROOT,image)
            with a.Image.open(path) as im: width,height=im.size
            side=dict(schemaVersion=1,kind='vision_pair_preprocessing',
                coordinateConvention='top_left_normalized_xywh; pixels=normalized*per_frame_dimensions',
                frames=[dict(role=role,sha256=image['sha256'],width=width,height=height,accessibility=report())
                        for role in ('before','after')])
            p=f.f.root/'sidecar.json';h.write(p,side)
            r=f.evidence['frames'][0]
            r.update(perceptionReport=h.ref(p),perceptionImage=image,perceptionFrameRole='before')
            r['status']='unverified'
            result=f.prepare()
            self.assertEqual(result['frames'][0]['proposals'],f.source['frames'][0]['proposals'])
            self.assertEqual(result['frames'][0]['accessibility']['perception']['profile'],'high_contrast_focus')
            self.assertIn('assisted_outline_proposal',(f.output/'review.md').read_text())
            for key,value in [('perceptionFrameRole',None),('perceptionImage',None)]:
                changed=copy.deepcopy(r);changed[key]=value
                with self.subTest(key=key),self.assertRaises(ValueError): a.perception(changed)
            for field,value in [('sha256','0'*64),('width',999)]:
                bad=copy.deepcopy(side);bad['frames'][0][field]=value
                p2=f.f.root/(field+'.json');h.write(p2,bad)
                changed=copy.deepcopy(r);changed['perceptionReport']=h.ref(p2)
                with self.subTest(field=field),self.assertRaises(ValueError): a.perception(changed)
            manifest=dict(schema_version=1,kind='hcf_review_feedback',
                role='development_review_only_not_training_admitted',ancestry='test-journey',
                frames=[dict(frame=1,file=str(path.relative_to(f.f.root)),sha256=image['sha256'],
                             profile='Default',width=width,height=height)],
                pairs=[dict(id='sample',before=1,after=1)])
            (f.f.root/'analysis').mkdir();h.write(f.f.root/'analysis/sample.json',side)
            h.write(f.f.root/'manifest.json',manifest)
            output=f.f.root/'audit.json'
            command=[sys.executable,str(h.ROOT/'scripts/report_hcf333.py'),
                     '--input',str(f.f.root),'--output',str(output)]
            run=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertFalse(h.read(output)['inferenceExecuted'])
            self.assertIsNone(h.read(output)['independentAccuracy'])
            # Existing output must not be replaced.
            self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)
            path.write_bytes(b'corrupt')
            import report_hcf333
            with self.assertRaises(ValueError): report_hcf333.run(f.f.root)
        finally: f.tearDown()


if __name__=='__main__': unittest.main()
