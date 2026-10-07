import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from harvest_schema4_review import review, render_review, score_review, hydrate_recipe, compare_geometry
from test_ttr_sidecar_v2 import ROOT, write_bundle


class Schema4ReviewTests(unittest.TestCase):
    def test_inline_version3_requires_explicit_dispatch(self):
        from harvest_schema4_review import pair
        meta=copy.deepcopy(self.meta)
        source,_=hydrate_recipe(self.bundle,meta['recipe'])
        source['recipe_hash']=meta['recipe']['recipe_hash']
        def replace(value):
            if isinstance(value,dict):
                for key,child in list(value.items()):
                    if key=='recipe':value[key]=copy.deepcopy(source)
                    else:replace(child)
            elif isinstance(value,list):
                for child in value:replace(child)
        replace(meta);meta['schema_version']=3;self.save(meta)
        with self.assertRaisesRegex(ValueError,'unsupported_version'):pair(self.bundle,'m.json')
        self.assertEqual(pair(self.bundle,'m.json',expected_version=3)['state'],'structurally_reviewed')
        meta['focused_scene']['focus_observation']['verified']=False;self.save(meta)
        with self.assertRaises(ValueError):pair(self.bundle,'m.json',expected_version=3)

    def test_union_and_comparison_fail_closed(self):
        report=review(self.bundle)
        captured=[]
        def reply(items,model):
            captured.extend(items)
            return {'results':[dict(id=i['id'],probability=.2+n*.6) for n,i in enumerate(items)]}
        with patch('focus_ring_baseline.model_contract',return_value={'sha256':'pinned'}), \
             patch('focus_runtime.invoke',side_effect=reply):
            old=score_review(self.bundle,self.root,report)
            new=score_review(self.bundle,self.root,report,'pair-union')
        self.assertEqual(captured[-1]['bounds'],captured[-2]['bounds'])
        for endpoint in report['rows'][0]['endpoints']:
            x,y,w,h=endpoint['visibleBody'];a,b,c,d=captured[-1]['bounds']
            self.assertTrue(a<=x and b<=y and a+c>=x+w and b+d>=y+h)
        result=compare_geometry(old,new)
        self.assertFalse(result['trainingEligible'])
        self.assertEqual(result['pairs'][0]['marginDelta'],0)
        for mutate in [lambda v:v.update(runtime={}),lambda v:v.update(artifact={}),
                       lambda v:v.update(inspectionSHA256='changed'),
                       lambda v:v['rows'].pop(),lambda v:v['rows'].append(v['rows'][0]),
                       lambda v:v['rows'][0].update(probability=float('nan')),
                       lambda v:v.update(trainingEligible=True)]:
            bad=copy.deepcopy(new);mutate(bad)
            with self.assertRaises(ValueError):compare_geometry(old,bad)

    def test_union_cli_requires_scoring(self):
        out=self.root/'not-created'
        result=subprocess.run([sys.executable,str(ROOT/'scripts/ttr_focus_manifest.py'),
            '--review-schema4-subset','--bundle',str(self.bundle),'--output',str(out),
            '--review-geometry','pair-union'],capture_output=True)
        self.assertEqual(result.returncode,2)
        self.assertFalse(out.exists())

    def test_union_uses_both_distinct_endpoint_extents(self):
        report=review(self.bundle)
        report['rows'][0]['endpoints'][0]['visibleBody']=[1,2,10,11]
        report['rows'][0]['endpoints'][1]['visibleBody']=[3,1,11,13]
        captured=[]
        def reply(items,model):
            captured.extend(items)
            return {'results':[dict(id=i['id'],probability=.5) for i in items]}
        # Isolate box selection; real metadata validation is covered separately.
        with patch('harvest_schema4_review.review',return_value=report), \
             patch('focus_ring_baseline.model_contract',return_value={'sha256':'pinned'}), \
             patch('focus_runtime.invoke',side_effect=reply):
            score_review(self.bundle,self.root,report,'pair-union')
        self.assertEqual([r['bounds'] for r in captured],[[1,1,13,13]]*2)

    def test_shared_recipe_resolver_keeps_sidecar_boundary(self):
        compact=self.meta['recipe']
        source,source_hash=hydrate_recipe(self.bundle,compact)
        self.assertEqual(source_hash,compact['source_reference']['sha256'])
        self.assertEqual(hydrate_recipe(self.bundle,source),(source,None))
        with self.assertRaisesRegex(ValueError,'source_reference_required'):
            hydrate_recipe(self.bundle,source,allow_inline=False)
        for key,value,reason in [('bytes',1,'source_size'),('sha256','0'*64,'source_hash'),
                                 ('recipe_hash','0'*64,'source_identity'),('path','../x','unsafe_path')]:
            bad=copy.deepcopy(compact);bad['source_reference'][key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,reason):
                hydrate_recipe(self.bundle,bad)

    def test_scoring_is_unadmitted_and_checks_values(self):
        report=review(self.bundle)
        def reply(items,model):
            return {'results':[dict(id=i['id'],probability=.2+n*.6) for n,i in enumerate(items)]}
        with patch('focus_ring_baseline.model_contract',return_value={'sha256':'pinned'}), \
             patch('focus_runtime.invoke',side_effect=reply):
            result=score_review(self.bundle,self.root,report)
            self.assertFalse(result['trainingEligible'])
            self.assertFalse(result['modelGateAssessed'])
            self.assertAlmostEqual(result['pairs'][0]['difference'],.6)
        with patch('focus_ring_baseline.model_contract',return_value={'sha256':'pinned'}), \
             patch('focus_runtime.invoke',side_effect=lambda items,model:{'results':[dict(id=i['id'],probability=float('nan')) for i in items]}):
            with self.assertRaisesRegex(ValueError,'invalid_probability'):score_review(self.bundle,self.root,report)
        self.save({**self.meta,'schema_version':3})
        with self.assertRaisesRegex(ValueError,'changed_review'):score_review(self.bundle,self.root,report)

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(dir=ROOT/'.build/debug-output', prefix='schema4-'))
        self.bundle = self.root/'bundle'
        meta = write_bundle(self.bundle)
        source = json.dumps({k:v for k,v in meta['recipe'].items() if k != 'recipe_hash'}).encode()
        (self.bundle/'source.json').write_bytes(source)
        compact = copy.deepcopy(meta['recipe'])
        compact['source_reference'] = dict(version=1, path='source.json', bytes=len(source),
            sha256=hashlib.sha256(source).hexdigest(), recipe_hash=compact['recipe_hash'])
        meta.update(schema_version=4, pairing_mode='competitor_v1', competitor_element_id='other')
        for key, ck, observed in [('baseline_scene','reference_capture','other'),
                                   ('focused_scene','focused_capture','e')]:
            s = meta[key]; s['recipe'] = copy.deepcopy(compact)
            s['focused_element_id'] = observed
            s['focus_observation'].update(observedID=observed, requestedID=observed)
            other = copy.deepcopy(s['elements'][0]); other['element_id'] = 'other'
            s['elements'].append(other)
            for e in s['elements']:
                e['is_focused'] = e['element_id'] == observed
                e['rendered_body_geometry'] = dict(version=1, availability='measured',
                    source='native_body_presentation_layer', coordinate_space='image_top_left_pixels',
                    role='rendered_control_body', element_id=e['element_id'],
                    generation=s['focus_observation']['generation'], full_pixel_bounds=e['pixel_bounds'],
                    visible_pixel_bounds=e['pixel_bounds'], visible_normalized_bounds=e['normalized_bounds'])
            for when in ['before','after']:
                meta[ck][when+'_scene'] = copy.deepcopy(s)
                meta[key+'_'+when+'_capture'] = copy.deepcopy(s)
        for k in ['recipe','elements','focused_element_id','is_settled']:
            meta[k] = copy.deepcopy(meta['focused_scene'][k])
        self.meta = meta
        self.save(meta)
        (self.bundle/'subset-manifest.json').write_text(json.dumps({'selected_metadata':['m.json']}))

    def tearDown(self):
        shutil.rmtree(self.root)

    def save(self, meta):
        (self.bundle/'m.json').write_text(json.dumps(meta))

    def test_cli_and_no_training_artifact(self):
        output = self.root/'review'
        args = [sys.executable, str(ROOT/'scripts/ttr_focus_manifest.py'), '--review-schema4-subset',
                '--bundle', str(self.bundle), '--output', str(output)]
        a = subprocess.run(args, capture_output=True, env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        self.assertEqual(a.returncode,0,a.stderr)
        result = json.loads((output/'schema4-review.json').read_text())
        self.assertEqual(result['reviewed'],1)
        self.assertFalse(result['trainingEligible'])
        self.assertEqual([p.name for p in output.iterdir()], ['schema4-review.json'])
        self.assertEqual(subprocess.run(args,capture_output=True).returncode,2)

    def test_adversarial_metadata(self):
        cases = [lambda m:m.update(schema_version=3),
                 lambda m:m['recipe']['source_reference'].update(path='../source.json'),
                 lambda m:m['recipe']['source_reference'].update(sha256='0'*64),
                 lambda m:m['recipe'].update(seed=999),
                 lambda m:m['focused_capture'].update(frame_received_host_ns=0),
                 lambda m:m['focused_capture'].update(frame_png_sha256='0'*64),
                 lambda m:m['focused_scene']['focus_observation'].update(source='prediction'),
                 lambda m:m['focused_scene']['elements'][0]['rendered_body_geometry'].update(generation=99),
                 lambda m:m['focused_scene']['elements'][0]['rendered_body_geometry'].update(visible_pixel_bounds=[0,0,999,1]),
                 lambda m:m['focused_scene']['elements'][0]['rendered_body_geometry'].update(visible_normalized_bounds=[0,0,1,1]),
                 lambda m:m['elements'][0].update(is_focused=False)]
        for mutate in cases:
            m=copy.deepcopy(self.meta); mutate(m); self.save(m)
            with self.subTest(mutation=cases.index(mutate)):
                self.assertEqual(review(self.bundle)['reviewed'],0)

    def test_production_review_crops_and_changed_metadata(self):
        output=self.root/'crops';output.mkdir()
        report=review(self.bundle)
        result=render_review(self.bundle,output,report)
        self.assertEqual(len(result['crops']),2)
        self.assertFalse(result['trainingEligible'])
        self.assertEqual(result['preprocessing']['expansion'],.16)
        self.save({**self.meta,'id':'changed'})
        with self.assertRaisesRegex(ValueError,'metadata_changed'):
            render_review(self.bundle,output,report)
        with self.assertRaisesRegex(ValueError,'partial_review_no_crops'):
            render_review(self.bundle,output,{**report,'reviewed':0})

    def test_missing_corrupt_and_linked_image(self):
        p=self.bundle/'f.png'; raw=p.read_bytes()
        p.write_bytes(b'not png'); self.assertEqual(review(self.bundle)['reviewed'],0)
        p.unlink(); self.assertEqual(review(self.bundle)['reviewed'],0)
        (self.root/'other.png').write_bytes(raw); p.symlink_to(self.root/'other.png')
        self.assertEqual(review(self.bundle)['reviewed'],0)

    def test_geometry_failures_reach_geometry_checks(self):
        for field,value,reason in [('generation',99,'body_identity'),
                ('visible_pixel_bounds',[0,0,999,1],'body_extent'),
                ('visible_normalized_bounds',[0,0,1,1],'body_normalization')]:
            m=copy.deepcopy(self.meta)
            s=m['focused_scene']; s['elements'][0]['rendered_body_geometry'][field]=value
            for when in ['before','after']:
                m['focused_capture'][when+'_scene']=copy.deepcopy(s)
                m['focused_scene_'+when+'_capture']=copy.deepcopy(s)
            m['elements']=copy.deepcopy(s['elements']);self.save(m)
            self.assertEqual(review(self.bundle)['rows'][0]['reason'],reason)

    def test_partial_membership_and_duplicate_json(self):
        (self.bundle/'subset-manifest.json').write_text(json.dumps({'selected_metadata':['m.json','missing.json']}))
        result=review(self.bundle)
        self.assertEqual((result['expected'],result['reviewed']),(2,1))
        self.assertEqual(result['rows'][1]['state'],'rejected')
        (self.bundle/'m.json').write_text('{"schema_version":4,"schema_version":4}')
        self.assertEqual(review(self.bundle)['rows'][0]['reason'],'duplicate_key')

    def test_body_status_contradictions_reach_shared_validator(self):
        for field,value,reason in [
                ('unavailable_reason','animation_in_progress','rendered_body:availability'),
                ('clipping','partially_clipped','rendered_body:clipping'),
                ('clipping','fully_clipped','rendered_body:fully_clipped_geometry')]:
            m=copy.deepcopy(self.meta)
            scene=m['focused_scene']
            scene['elements'][0]['rendered_body_geometry'][field]=value
            for when in ['before','after']:
                m['focused_capture'][when+'_scene']=copy.deepcopy(scene)
                m['focused_scene_'+when+'_capture']=copy.deepcopy(scene)
            m['elements']=copy.deepcopy(scene['elements']);self.save(m)
            with self.subTest(field=field,value=value):
                result=review(self.bundle)
                self.assertEqual(result['reviewed'],0)
                self.assertEqual(result['rows'][0]['reason'],reason)
                self.assertFalse(result['trainingEligible'])


if __name__ == '__main__':
    unittest.main()
