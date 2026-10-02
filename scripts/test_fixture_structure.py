"""Structural-v3 consumer checks with generated, non-training fixtures."""
import copy
import hashlib
import itertools
import json
import unittest
from unittest.mock import patch

import fixture_composition as composition
import fixture_semantic_inventory as semantic
from harvest_sidecar_v2 import require, recipe_hash
import test_fixture_composition as legacy
from test_fixture_semantic_inventory import inventory
import test_ttr_sidecar_v2 as fixtures
from audit_fixture_structure import audit


def recipe(kind='composite_card'):
    r=legacy.recipe(); c=r['appearance']['composition']; c['version']=3
    c['definitions']['d'].update(kind=kind,width=600 if kind=='ranked_row' else 200,height=180)
    c['regions'][0]['frame']=[0,0,900,500]
    if kind!='home_icon':
        c['styles']['s']['focus']=dict(version=1,kind='custom',custom=dict(
            scale=1.1,borderWidth=3,borderRGB=0xffffff,shadowOpacity=.45,shadowRGB=0,cornerRadius=12))
    r['recipe_hash']=recipe_hash(r)
    return r


class StructuralTests(unittest.TestCase):
    def test_four_families_actual_review_caller(self):
        for kind in ('composite_card','ranked_row','home_icon','hero'):
            with self.subTest(kind=kind), patch.object(legacy,'recipe',return_value=recipe(kind)):
                legacy.CompositionTests('test_actual_native_intake_and_capacity').test_actual_native_intake_and_capacity()

    def test_closed_structural_rules(self):
        r=recipe(); c=r['appearance']['composition']
        mutations=[lambda v:v.update(version=2),lambda v:v.update(version=True),
            lambda v:v['styles']['s'].update(focus=dict(version=1,kind='native_image')),
            lambda v:v['definitions']['d'].update(height=139),
            lambda v:v['definitions']['d'].update(kind='ranked_row',width=400,height=180),
            lambda v:v['definitions']['d'].update(kind='ranked_row',width=800,height=140),
            lambda v:v['regions'][0].update(scroll=1)]
        for fn in mutations:
            bad=copy.deepcopy(c);fn(bad)
            with self.subTest(mutation=mutations.index(fn)),self.assertRaises(ValueError):
                composition.resolve(bad,r,require)

    def test_scroll_limits_and_optional_hash(self):
        r=recipe(); c=r['appearance']['composition']; region=c['regions'][0]
        baseline=composition.resolve(c,r,require)[1]
        region['scroll']=None
        self.assertEqual(composition.resolve(c,r,require)[1],baseline)
        region['scroll']=False
        self.assertNotEqual(composition.resolve(c,r,require)[1],baseline)
        region.update(scroll=True,frame=[0,0,100,500])
        composition.resolve(c,r,require)
        region['items']=[dict(region['items'][0],id='e'+str(i)) for i in range(20)]
        r['element_count']=20
        with self.assertRaisesRegex(ValueError,'composition_overflow'):composition.resolve(c,r,require)
        region['items']=region['items'][:1]; r['element_count']=1
        c['version']=2
        with self.assertRaises(ValueError):composition.resolve(c,r,require)

    def test_semantic_optional_observations(self):
        doc=inventory(fixtures.scene('e',5)); element=doc['elements'][0]
        original=copy.deepcopy(doc)
        semantic.validate(doc); self.assertEqual(doc,original)
        element.update(is_hidden=False,effective_alpha=1,scroll_container_id='main.scroll',
                       scroll_offset_points=[-2,10],viewport_pixel_bounds=[0,0,64,48])
        self.assertFalse(semantic.validate(doc)['trainingEligible'])
        for field,value in [('is_hidden',1),('effective_alpha',True),('effective_alpha',1.01),
            ('effective_alpha',float('nan')),('scroll_container_id',''),('scroll_offset_points',[0]),
            ('scroll_offset_points',[0,float('inf')]),('viewport_pixel_bounds',[0,0,0,1])]:
            bad=copy.deepcopy(doc);bad['elements'][0][field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):semantic.validate(bad)


class CheckpointTests(unittest.TestCase):
    setUp=fixtures.V2Tests.setUp
    tearDown=fixtures.V2Tests.tearDown

    def checkpoint(self):
        root=self.root/'checkpoint';(root/'recipes').mkdir(parents=True)
        members={}
        def write(name,data):
            raw=json.dumps(data).encode();(root/name).write_bytes(raw)
            members[name]=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
            return members[name]['sha256']
        appearances=[];transitions=[]
        for family,light,bg,pos in itertools.product(('composite_card','ranked_row','home_icon','hero'),('dark','light'),('dark','light'),range(3)):
            name=f'{family}-{light}-{bg}-{pos}'
            r=recipe(family);c=r['appearance']['composition'];r['element_count']=2
            c['regions'][0]['items'].append(dict(c['regions'][0]['items'][0],id='other'))
            if family=='ranked_row': c['regions'][0]['scroll']=True
            digest=write('recipes/'+name+'.json',r)
            appearances.append(dict(id=name,family=family,artwork_luminance=light,background=bg,position=pos,
                                    target='e',competitor='other',recipe=name+'.json',sha256=digest))
        for condition,bg,seed in itertools.product(('boundary_unchanged','content_only','scroll_unchanged','scroll_moved'),('dark','light'),(71,83)):
            name=f'{condition}-{bg}-{seed}';digest=write('recipes/'+name+'.json',recipe())
            transitions.append(dict(id=name,condition=condition,background=bg,seed=seed,recipe=name+'.json',
                                    recipe_sha256=digest,initial_focus='e',expected_focus_relation='same'))
        write('recipes/matrix.json',dict(version=1,appearance_pairs=appearances))
        write('transitions.json',dict(version=1,pairs=transitions))
        (root/'manifest.json').write_text(json.dumps(dict(schema_version=1,members=members,new_captured_pairs=0)))
        return root

    def test_verified_plan_not_training_or_pixels(self):
        root=self.checkpoint();result=audit(root)
        self.assertEqual(result['appearanceRecipes'],48);self.assertEqual(result['transitionRecipes'],16)
        self.assertFalse(result['trainingEligible']);self.assertFalse(result['liveQualified'])
        self.assertEqual(result['appearanceFocusTreatments'],dict(custom=36,native_image=12))

    def test_tamper_and_unsafe_members_fail(self):
        root=self.checkpoint();manifest=json.loads((root/'manifest.json').read_text())
        key=next(iter(manifest['members']));path=root/key;raw=path.read_bytes();path.write_bytes(raw+b' ')
        with self.assertRaisesRegex(ValueError,'member_integrity'):audit(root)
        path.write_bytes(raw);manifest['members']['../outside']={}
        (root/'manifest.json').write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError,'member_path'):audit(root)

    def test_rehashed_missing_coverage_fails(self):
        root=self.checkpoint();path=root/'recipes/matrix.json';matrix=json.loads(path.read_text())
        matrix['appearance_pairs'][0]=matrix['appearance_pairs'][1]
        raw=json.dumps(matrix).encode();path.write_bytes(raw)
        manifest=json.loads((root/'manifest.json').read_text())
        manifest['members']['recipes/matrix.json']=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        (root/'manifest.json').write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError,'appearance_coverage'):audit(root)


if __name__=='__main__': unittest.main()
