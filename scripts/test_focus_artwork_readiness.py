"""Generated native inputs and real CLI/preflight; no model loading or admission."""
import copy
from contextlib import redirect_stdout
import io
import json
import sys
import unittest
from unittest.mock import patch
from PIL import Image

import focus_artwork_readiness as a
import human_annotation_review as h
import test_focus_native_body_assembly as fixture
from test_fixture_composition import recipe


def rows():
    result=[]
    for frame,label in [('focused',1),('unfocused',0)]:
        for cid,y in [('target',label),('neighbor',1-label)]:
            result.append(dict(id=frame+cid,batchID='b',frameID=frame,controlID=cid,
                sourceElementID='e' if cid=='target' else 'n',sourceID='s',sourcePairID='p',
                recipe=recipe(),control='collectionItem' if cid=='target' else 'primaryButton',
                crop=dict(pixelSHA256=frame+cid),label=y,reasons=[],disposition='awaiting_admission',
                bounds=[0,0,100+10*y,100+10*y]))
    return result


def links():return [dict(id='pair',batchID='b',frames=['focused','unfocused'],controlID='target',sourcePairID='p')]


class CoverageTests(unittest.TestCase):
    def test_conditional_owned_proposal_never_clears_blockers(self):
        r=rows()
        for x in r:
            x['recipe']['appearance']['composition']['contents']['c']['owned_artwork']={'id':'test'}
            x['reasons']=['screenshot_time_hash_binding_unqualified'];x['disposition']='blocked'
        c=a.summarize(r,links(),{x['id']:1. for x in r});original=copy.deepcopy(r)
        self.assertEqual(c['proposedIDs'],[])
        with patch.object(a,'comparison',side_effect=lambda base,add:dict(ids=[x['id'] for x in add],executionAuthorized=False)):
            d=a.conditional_owned_comparison({},r,c)
            self.assertEqual(set(d['comparison']['ids']),{'focusedtarget','unfocusedtarget'})
            self.assertFalse(d['trainingEligible']);self.assertEqual(r,original)
            r[0]['reasons'].append('evaluation_lineage_overlap')
            c=a.summarize(r,links(),{x['id']:1. for x in r})
            self.assertEqual(a.conditional_owned_comparison({},r,c)['comparison']['ids'],[])

    def test_matched_white_pairs_and_unknown_semantics(self):
        r=rows();d=a.summarize(r,links(),{x['id']:1. for x in r})
        self.assertEqual(d['distinctSupportedWhitePairs'],1)
        self.assertEqual(d['proposedIDs'],['focusedtarget','unfocusedtarget'])
        self.assertIn('unknown',d['logoAndBlankCoverage'])
        self.assertAlmostEqual(d['artworkPairs'][0]['growth'][0],1.1)
        self.assertEqual(d,a.summarize(list(reversed(r)),links(),{x['id']:1. for x in r}))

    def test_no_white_unknown_asset_and_no_focused_competitor(self):
        for kind in ('no_white','asset','competitor'):
            r=rows();f={x['id']:0. if kind=='no_white' else 1. for x in r}
            if kind=='asset':
                for x in r:x['recipe']={}
            if kind=='competitor':r[-1]['label']=0
            d=a.summarize(r,links(),f);self.assertEqual(d['distinctSupportedWhitePairs'],0)
            if kind!='no_white':self.assertFalse(d['proposedIDs'])

    def test_duplicate_aliases_do_not_multiply_coverage(self):
        r=rows();alias=copy.deepcopy(r)
        for x in alias:
            original=x['id'];x['id']='copy-'+original;x['frameID']='copy-'+x['frameID']
            x.update(reasons=['duplicate_crop'],duplicateOf=original,disposition='blocked')
        pairs=links()+[dict(links()[0],id='copy-pair',frames=['copy-focused','copy-unfocused'])]
        d=a.summarize(r+alias,pairs,{x['id']:1. for x in r+alias})
        self.assertEqual(d['distinctSupportedWhitePairs'],1);self.assertEqual(len(d['proposedIDs']),2)
        self.assertEqual(d['groups']['collectionItem:0']['observations'],2)
        self.assertEqual(d['groups']['collectionItem:0']['uniqueCropPixels'],1)

    def test_invalid_membership_states_and_content(self):
        for kind in ('missing','duplicate','state','content','score'):
            r=rows();pairs=links();f={x['id']:1. for x in r}
            if kind=='missing':r.pop(0);f.pop('focusedtarget')
            if kind=='duplicate':pairs*=2
            if kind=='state':r[0]['label']=0
            if kind=='content':r[0]['recipe']['appearance']['composition']['contents']['c']['title']='changed'
            if kind=='score':f[r[0]['id']]=float('nan')
            with self.subTest(kind=kind),self.assertRaises(ValueError):a.summarize(r,pairs,f)
        r=rows();r[0]['reasons']=['conflicting_crop_labels']
        self.assertEqual(a.summarize(r,links(),{x['id']:1. for x in r})['distinctSupportedWhitePairs'],0)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.f=fixture.IntegrationTests();self.f.setUp();self.root=self.f.root
        encoder=self.root/'test-only-encoder.bin';encoder.write_bytes(b'not a model, hash only')
        samples=[];weights={}
        for kind in ('simulatorFixture','tvos_simulator_os','human','evaluation'):
            for label in (0,1):
                sid=kind+str(label);path=self.root/(sid+'.png')
                Image.new('RGB',(256,256),(40+len(samples)*10,20,30)).save(path)
                ref=dict(h.ref(path),pixelSHA256=h.pixel_digest(h.ROOT,h.ref(path)))
                samples.append(dict(id=sid,label=label,split='validation' if kind=='evaluation' else 'train',
                    use='representative-selection' if kind=='evaluation' else 'human-static-auxiliary' if kind=='human' else 'train-candidate',
                    sourceKind=kind,relatedGroup=kind,intrinsicGroup=kind,recipeSeed=None,crop=ref,frame=ref))
                if kind!='evaluation':weights[sid]=1/6
        self.base=dict(version='focus-visual-experiment-v1',samples=samples,fullFit=dict(weights=weights,microbatch=32),
            representation=dict(weights=h.ref(encoder)),selection=dict(threshold=.85),
            configuration=dict(epochs=100,batch=6,lr=.01,model='mobilenet_v3_small_partial_visual',maxSeconds=300))
        self.base['protocolSHA256']=h.digest(self.base);self.path=self.root/'baseline.json';h.write(self.path,self.base)
        self.spec=dict(baseline=h.ref(self.path),sources=[self.f.entry],protected=h.ref(self.f.f.protected))

    def tearDown(self):self.f.tearDown()

    def test_real_cli_and_trainer_dry_run_execute_and_approval_rejection(self):
        out=self.root/'readiness';before=h.sha(h.checked(h.ROOT,self.f.entry['batch']))
        args=['readiness','--baseline',str(self.path),'--protected',str(self.f.f.protected),
              '--source',str(h.checked(h.ROOT,self.f.entry['batch'])),str(h.checked(h.ROOT,self.f.entry['crops'])),
              '--output',str(out)]
        with patch.object(sys,'argv',args),redirect_stdout(io.StringIO()),patch.dict(sys.modules,{'torch':None}):
            self.assertEqual(a.main(),0)
        doc=h.read(out/'readiness.json');self.assertFalse(doc['trainingEligible']);self.assertEqual(doc['counts']['candidates'],2)
        self.assertEqual(len(doc['recipes']),1)
        self.assertTrue(all('recipe' not in r and r['recipeSHA256'] in doc['recipes'] for r in doc['candidates']))
        self.assertEqual(doc['sourceRoles'][next(iter(doc['sourceRoles']))],{'calibration':1})
        import train_focus_ring_detector as trainer
        for flag in ('--dry-run','--execute'):
            args=['trainer','--experiment-protocol',str(out/'readiness.json'),'--experiment-arm',a.ARM,'--name','test-readiness',flag]
            output=io.StringIO()
            with patch.object(sys,'argv',args),redirect_stdout(output),patch.dict(sys.modules,{'torch':None}):
                self.assertEqual(trainer.main(),2)
            report=json.loads(output.getvalue());self.assertTrue(report['configurationValid']);self.assertFalse(report['launchEligible'])
        with self.assertRaisesRegex(ValueError,'not_execution_approval'):a.load_protocol(out/'readiness.json',a.ARM,'x',self.path)
        self.assertEqual(h.sha(h.checked(h.ROOT,self.f.entry['batch'])),before)

    def test_fixed_eval_weights_and_no_addition_identity(self):
        # Historical reviewed human rows omit sourceKind. Keep the use/role and
        # weight; do not invent a device provenance or reject valid old evidence.
        for r in self.base['samples']:
            if r['use']=='human-static-auxiliary':r.pop('sourceKind')
        none=a.comparison(self.base,[]);self.assertEqual(none['hypotheticalAdditionWeights'],self.base['fullFit']['weights'])
        additions=[dict(self.base['samples'][y],id='new'+str(y),sourceKind='tvos_native_generator') for y in (0,1)]
        d=a.comparison(self.base,additions)
        self.assertEqual(d['evaluationMembershipSHA256'],none['evaluationMembershipSHA256'])
        for sid in ('human0','human1','tvos_simulator_os0','tvos_simulator_os1'):
            self.assertEqual(d['hypotheticalAdditionWeights'][sid],self.base['fullFit']['weights'][sid])
        for label in (0,1):
            self.assertAlmostEqual(sum(d['hypotheticalAdditionWeights'][sid] for sid in ('simulatorFixture'+str(label),'new'+str(label))),1/6)
        self.assertFalse(d['executionAuthorized'])

    def test_existing_competitor_canvas_is_supported_without_new_schema(self):
        from test_ttr_competitor import competitor_meta
        from test_fixture_semantic_inventory import inventory
        from test_fixture_rendered_body import body
        meta=competitor_meta(self.f.f.f.meta)
        def attach(value):
            if isinstance(value,dict):
                for child in list(value.values()):attach(child)
                if 'scene_width' in value:
                    W,H=value['scene_width'],value['scene_height']
                    for e in value['elements']:
                        x,y,w,ht=e['pixel_bounds'];b=body(e['element_id'],value['focus_observation']['generation'])
                        b.update(full_pixel_bounds=[x,y,w,ht],visible_pixel_bounds=[x,y,w,ht],
                                 visible_normalized_bounds=[x/W,y/H,(x+w)/W,(y+ht)/H])
                        e['rendered_body_geometry']=b
                    value['semantic_inventory']=inventory(value)
        attach(meta);self.f.f.f.meta=meta;self.f.f.f.mutate(lambda _:None)
        out=self.root/'competitor';a.native.native.prepare([self.f.f.bundle],out,self.f.f.protected,count=1,body_geometry=True)
        spec=dict(self.spec,sources=[dict(batch=h.ref(out/'native-review/batch.json'),crops=h.ref(out/'crops/crop-qa.json'))])
        d=a.prepare(spec)
        self.assertEqual(len(d['coverage']['artworkPairs']),2)
        self.assertTrue(all(p['visibleCompetitors'] and p['content'] is not None for p in d['coverage']['artworkPairs']))
        self.assertGreater(d['counts']['proposedAdditions'],0)
        self.assertFalse(d['trainingEligible'])

    def test_protected_source_no_decode_and_changed_baseline(self):
        raw=h.read(h.checked(h.ROOT,self.f.entry['batch']))
        protected=self.root/'additional-protected.json'
        protected.write_text(json.dumps({'sha256':raw['frames'][0]['image']['sha256']}))
        # Rebinding protected metadata is deliberate; source is then quarantined.
        self.spec['protected']=h.ref(protected)
        with patch.object(a.native.native,'source_record',side_effect=AssertionError('must not decode')):
            d=a.prepare(self.spec)
        self.assertEqual(d['counts']['candidates'],0);self.assertIn('no_supported_unique_artwork_additions',d['blockers'])
        self.path.write_text(self.path.read_text()+' ')
        with self.assertRaisesRegex(ValueError,'changed_hash'):a.prepare(self.spec)

    def test_protected_baseline_and_resealed_plan_cannot_launch(self):
        plan=a.prepare(self.spec);plan['comparison']['evaluationIDs'].reverse()
        plan.pop('protocolSHA256');plan['protocolSHA256']=h.digest(plan)
        altered=self.root/'resealed-readiness.json';h.write(altered,plan)
        with self.assertRaisesRegex(ValueError,'readiness_inputs_changed'):a.load_protocol(altered,a.ARM,'test')
        bad=copy.deepcopy(self.base);bad['samples'][-1]['use']='final-challenge'
        bad.pop('protocolSHA256');bad['protocolSHA256']=h.digest(bad);self.path.write_text(json.dumps(bad))
        with self.assertRaisesRegex(ValueError,'protected_or_invalid'):a.baseline(self.path)

    def test_exact_descriptor_channels_and_required_production_size(self):
        for i,(color,expected) in enumerate([((255,255,255),1.),((220,220,220),0.),((255,230,230),0.)]):
            path=self.root/('color'+str(i)+'.png');Image.new('RGB',(256,256),color).save(path)
            self.assertEqual(a.white_fraction(h.ref(path)),expected)
        path=self.root/'not-production.png';Image.new('RGB',(256,160),'white').save(path)
        with self.assertRaisesRegex(ValueError,'production_crop_size'):a.white_fraction(h.ref(path))


if __name__=='__main__':unittest.main()
