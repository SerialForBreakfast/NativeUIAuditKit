"""Generated owned-artwork diagnostic intake; real crop/review caller, no models."""
import copy
import json
from pathlib import Path
import tempfile
import shutil
import unittest
from unittest.mock import patch
from PIL import Image
import human_annotation_review as h
import fixture_owned_pairs as o
import fixture_batch_review as review
import fixture_composition as composition
from harvest_sidecar_v2 import recipe_hash
from test_fixture_composition import recipe
from test_ttr_sidecar_v2 import scene
from test_fixture_semantic_inventory import inventory


def asset():
    return dict(version=1,id='a',family='white_owned_mark',structural_family='ring',
        origin='original_repository_geometry',width=256,height=160,background=0xffffff,
        primitives=[dict(shape='ellipse',rect=[100,50,40,40],color=0)])


def reindex(root):
    files=[dict(path=p.relative_to(root).as_posix(),bytes=p.stat().st_size,sha256=h.sha(p))
           for p in sorted(root.rglob('*')) if p.is_file() and p.name!='manifest.json']
    (root/'manifest.json').write_text(json.dumps(dict(schema_version=1,files=files)))


def fixture(root):
    root.mkdir();(root/'assets').mkdir();(root/'pairs').mkdir();(root/'recipes').mkdir()
    r=recipe();v=r['appearance']['composition'];v['version']=2
    v['contents']['c'].pop('design');v['contents']['c']['owned_artwork']=asset()
    v['regions'][0]['frame']=[0,0,300,200]
    v['regions'][0]['items'].append(dict(id='neighbor',component='d',content='c',selected=False))
    r['element_count']=2;r['recipe_hash']=recipe_hash(r)
    (root/'recipes/p.json').write_text(json.dumps(r));(root/'assets/a.json').write_text(json.dumps(asset()))
    frames=[]
    for n,(state,focused) in enumerate([('unfocused','neighbor'),('focused','e')]):
        s=scene(focused,4+n);s['recipe']=r;s['monotonic_nanoseconds']=100+100*n
        other=copy.deepcopy(s['elements'][0]);other['element_id']='neighbor'
        s['elements'].append(other)
        for j,e in enumerate(s['elements']):
            e['is_focused']=e['element_id']==focused;e['parent_element_id']='region'
            x,y,w,ht=[2+30*j,5,24,20];e['pixel_bounds']=[x,y,w,ht]
            e['normalized_bounds']=[x/64,y/48,(x+w)/64,(y+ht)/48]
            e['rendered_body_geometry']=dict(version=1,role='rendered_control_body',coordinate_space='image_top_left_pixels',
                element_id=e['element_id'],generation=4+n,source='uikit_focused_frame_guide',availability='measured',
                full_pixel_bounds=e['pixel_bounds'],visible_pixel_bounds=e['pixel_bounds'],visible_normalized_bounds=e['normalized_bounds'])
        s['focus_observation']['plannedFocusIDs']=['e','neighbor']
        s['observation_diagnostics'].update(requiredIDs=['e','neighbor'],measuredIDs=['e','neighbor'])
        doc=inventory(s);doc['coverage']='complete_declared_composition'
        for e in doc['elements']:e['declared_parent_id']='region'
        for eid,role in [('region','layout_region'),('composition.background','decorative_background')]:
            e=copy.deepcopy(doc['elements'][0]);e.update(id=eid,role=role,focusable=False,input_focused=False,is_accessibility_element=False)
            e.pop('declared_parent_id');doc['elements'].append(e)
        s['semantic_inventory']=doc
        name='p-'+state
        Image.new('RGB',(64,48),'white' if n else 'gray').save(root/'pairs'/(name+'.png'))
        raw=dict(before=s,after=copy.deepcopy(s),capture=dict(state='delivered',effectStatus='unverified',
            operationID='session',sequence=n+1,simulatorID='test',screenshotReference='test/'+name+'.png'))
        (root/'pairs'/(name+'.json')).write_text(json.dumps(raw))
        frames.append(dict(image=name+'.png',native_focus=focused,body=s['elements'][0]['rendered_body_geometry']))
    pair=dict(recipe='recipes/p.json',recipe_sha256=h.sha(root/'recipes/p.json'),target_id='e',
        focused_request='e',unfocused_request='neighbor',asset_id='a',asset_group='a',structural_family='ring',
        renderer_ancestry='fixture_procedural_renderer_v1',owned_renderer='owned-artwork-v1',layout_group='test',
        role='diagnostic_unadmitted',frames=frames,frame_prefix='pairs/p',focus_label_source='observed_uikit',directional_success='not_measured')
    (root/'pair-index.json').write_text(json.dumps(dict(schema_version=1,format=o.FORMAT,pairs=[pair])))
    reindex(root)


class OwnedTests(unittest.TestCase):
    def setUp(self):
        (h.ROOT/'.build/debug-output').mkdir(parents=True,exist_ok=True)
        self.root=Path(tempfile.mkdtemp(dir=h.ROOT/'.build/debug-output',prefix='owned-test-'))
        self.bundle=self.root/'bundle';fixture(self.bundle)

    def tearDown(self):shutil.rmtree(self.root)

    def change(self,name,fn):
        path=self.bundle/name;v=h.read(path);fn(v);path.write_text(json.dumps(v));reindex(self.bundle)

    def test_exact_v2_and_v1_rejection(self):
        r=h.read(self.bundle/'recipes/p.json');v=r['appearance']['composition']
        self.assertTrue(composition.resolve(v,r,h.require)[1].startswith('composition@2:'))
        v['version']=1
        with self.assertRaises(ValueError):composition.resolve(v,r,h.require)

    def test_primitive_matrix(self):
        for fn in [lambda a:a.update(url='https://example.com'),lambda a:a.update(version=True),
            lambda a:a.update(width=255),lambda a:a.update(origin='download'),lambda a:a.update(id='../x'),
            lambda a:a.update(primitives=a['primitives']*33),lambda a:a.update(background=-1),
            lambda a:a['primitives'][0].update(rect=[250,0,10,10]),
            lambda a:a['primitives'][0].update(rect=[0,0,True,10]),
            lambda a:a['primitives'][0].update(shape='url'),lambda a:a['primitives'][0].update(color=0x1000000)]:
            a=asset();fn(a)
            with self.subTest(a=a),self.assertRaises(ValueError):composition.owned_artwork(a,h.require)
        a=asset();a['primitives']=[];self.assertTrue(composition.owned_artwork(a,h.require))

    def test_real_review_crops_and_no_fabricated_binding(self):
        p=self.root/'protected.json';p.write_text('{}')
        result=review.prepare([self.bundle],self.root/'qa',p,count=1,exception_limit=0,body_geometry=True,pair_ids=['pairs/p'])
        self.assertEqual(result['crops'],dict(expected=4,completed=4));self.assertFalse(result['trainingEligible'])
        batch=review.validate(self.root/'qa/native-review/batch.json')
        self.assertEqual(batch['sources'][0]['sourceFormat'],o.FORMAT)
        self.assertEqual(batch['frames'][0]['observationCorrelation'],o.CORRELATION)
        self.assertIn('screenshot_time_hash_binding_unqualified',batch['frames'][0]['admissionBlockers'])
        self.assertFalse((self.bundle/'harvest-receipt.json').exists())
        import human_intake_audit as audit
        balanced=audit.prepare(self.root/'qa/native-review/batch.json',self.root/'balanced',count=2,exception_limit=0,focus_element='e')
        self.assertEqual(balanced['sampling']['method'],'stratified-random-without-replacement')
        self.assertEqual([len(s['selected']) for s in balanced['sampling']['strata'].values()],[1,1])
        audit.validate_queue(self.root/'balanced/combined-queue.json')
        for options in (dict(count=1,focus_element='e'),dict(count=2,focus_element='missing')):
            with self.assertRaises(ValueError):audit.plan(self.root/'qa/native-review/batch.json',**options)
        from focus_native_body_assembly import candidates
        rows,_,_=candidates([dict(batch=h.ref(self.root/'qa/native-review/batch.json'),crops=h.ref(self.root/'qa/crops/crop-qa.json'))],set())
        self.assertTrue(all('screenshot_time_hash_binding_unqualified' in r['reasons'] for r in rows))

    def test_hash_role_and_protected_rejection_before_decode(self):
        with patch.object(o.Image,'open',side_effect=AssertionError('decoded protected input')):
            with self.assertRaisesRegex(ValueError,'protected'):o.source_record(self.bundle,{h.sha(self.bundle/'pairs/p-unfocused.png')})
            self.change('pair-index.json',lambda v:v['pairs'][0].update(role='final-challenge'))
            with self.assertRaisesRegex(ValueError,'role'):o.source_record(self.bundle,set())

    def test_bad_selection_and_integrity(self):
        for ids in ([],['missing'],['pairs/p']*2):
            with self.assertRaisesRegex(ValueError,'selection'):o.source_record(self.bundle,set(),ids)
        (self.bundle/'pairs/p-focused.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'integrity'):o.source_record(self.bundle,set())

    def test_changed_native_endpoint(self):
        self.change('pairs/p-focused.json',lambda v:v['after']['elements'][0].update(is_focused=False))
        with self.assertRaises(ValueError):o.source_record(self.bundle,set())

    def test_bad_asset_and_index_body(self):
        self.change('pair-index.json',lambda v:v['pairs'][0]['frames'][0]['body'].update(generation=99))
        with self.assertRaisesRegex(ValueError,'frame_index'):o.source_record(self.bundle,set())

    def test_asset_change_is_not_ignored(self):
        self.change('assets/a.json',lambda v:v.update(background=0))
        with self.assertRaisesRegex(ValueError,'asset_ancestry'):o.source_record(self.bundle,set())

    def test_paths_duplicates_and_capture_identity(self):
        for name in ('../escape','/absolute','a/../escape','a\\b'):
            with self.assertRaises(ValueError):o.member(self.bundle,name)
        self.change('pairs/p-focused.json',lambda v:v['capture'].update(sequence=1))
        with self.assertRaisesRegex(ValueError,'capture_receipt'):o.source_record(self.bundle,set())

    def test_declared_recipe_file_mismatch_stays_blocked(self):
        self.change('pair-index.json',lambda v:v['pairs'][0].update(recipe_sha256='0'*64))
        _,c=o.source_record(self.bundle,set())
        self.assertIn('pair_index_recipe_file_hash_mismatch',c['usableRows'][0]['admissionBlockers'])
        self.assertFalse(c['usableRows'][0]['eligibleForTraining'])


if __name__=='__main__':unittest.main()
