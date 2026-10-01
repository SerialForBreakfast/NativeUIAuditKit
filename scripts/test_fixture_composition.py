"""Generated composition cases exercise the real native intake, no retained data."""
import copy
import json
import unittest
from unittest.mock import patch
import fixture_composition as c
import fixture_batch_review as review
import fixture_semantic_inventory as semantic
from harvest_sidecar_v2 import require, recipe_hash
from harvest_bundle_validation import validate_bundle
import test_ttr_sidecar_v2 as fixtures
from test_fixture_semantic_inventory import inventory


def recipe():
    r=copy.deepcopy(fixtures.recipe()) if hasattr(fixtures,'recipe') else copy.deepcopy(fixtures.scene(None,4)['recipe'])
    comp=dict(version=1,styles={'s':dict(foreground=0xffffff,background=0,fontSize=24,cornerRadius=12,opacity=1.,blur=False,
              focus=dict(version=1,kind='native_image'))},definitions={'d':dict(kind='poster',style='s',width=100,height=100)},
              contents={'c':dict(title='Art',seed=1,preset='artwork',design='city')},
              regions=[dict(id='region',axis='row',frame=[0,0,200,200],gap=10,items=[dict(id='e',component='d',content='c',selected=False)])],
              background=dict(colors=[0,0xffffff],locations=[0.,1.],direction='vertical',interpolation='linear'))
    r.update(archetype='grid_matrix',theme='dark',density='regular',element_count=1,appearance=dict(version=1,preset='artwork',layout='standard',composition=comp))
    r['recipe_hash']=recipe_hash(r)
    return r


class CompositionTests(unittest.TestCase):
    def test_closed_contract_and_mutations(self):
        r=recipe();v=r['appearance']['composition'];items,identity=c.resolve(v,r,require)
        self.assertEqual(items[0]['id'],'e');self.assertTrue(items[0]['focusable']);self.assertTrue(identity.startswith('composition@1:'))
        mutations=[lambda d:d.update(version=3),lambda d:d.update(extra=1),lambda d:d['styles']['s'].update(opacity=.5),
            lambda d:d['styles']['s'].update(fontSize=True),lambda d:d['regions'][0]['items'][0].update(style=''),
            lambda d:d['regions'][0]['items'][0].update(content='missing'),lambda d:d['regions'][0]['items'][0].update(selected=True),
            lambda d:d['regions'].append(copy.deepcopy(d['regions'][0])),lambda d:d['definitions']['d'].update(width=300),
            lambda d:d['background'].update(locations=[1,0]),lambda d:d['contents']['c'].update(seed=-1),
            lambda d:d['styles']['s']['focus'].update(kind='native_button')]
        for fn in mutations:
            with self.subTest(mutation=mutations.index(fn)):
                bad=copy.deepcopy(v);fn(bad)
                with self.assertRaises(ValueError):c.resolve(bad,r,require)
        altered=copy.deepcopy(r);altered['appearance']['composition']['contents']['c']['title']='Different'
        self.assertNotEqual(recipe_hash(altered),r['recipe_hash'])
        integral=copy.deepcopy(v);integral['styles']['s']['opacity']=1;integral['background']['locations']=[0,1]
        self.assertEqual(c.resolve(integral,r,require)[1],identity)

    def test_scene_hierarchy_and_plan(self):
        s=fixtures.scene('e',5);s['recipe']=recipe();s['elements'][0]['parent_element_id']='region'
        c.hierarchy(s,require)
        for field,value in [('parent_element_id','wrong'),('taxonomy_class','primaryButton')]:
            bad=copy.deepcopy(s);bad['elements'][0][field]=value
            with self.assertRaises(ValueError):c.hierarchy(bad,require)
        s['focus_observation']['plannedFocusIDs']=[]
        with self.assertRaises(ValueError):c.hierarchy(s,require)

    def test_actual_native_intake_and_capacity(self):
        f=fixtures.V2Tests();f.setUp()
        try:
            def walk(v):
                if isinstance(v,dict):
                    for child in list(v.values()):walk(child)
                    if 'scene_width' in v:
                        v['recipe']=recipe();v['elements'][0]['parent_element_id']='region'
                        is_tab=v['recipe']['appearance']['composition']['definitions']['d']['kind']=='tab'
                        if is_tab:v['elements'][0]['taxonomy_class']='menuButton'
                        doc=inventory(v);doc['coverage']='complete_declared_composition'
                        doc['elements'][0]['declared_parent_id']='region'
                        if is_tab:doc['elements'][0]['selected']=False
                        for eid,role in [('region','layout_region'),('composition.background','decorative_background')]:
                            e=copy.deepcopy(doc['elements'][0]);e.update(id=eid,role=role,focusable=False,input_focused=False,is_accessibility_element=False)
                            e.pop('declared_parent_id',None);doc['elements'].append(e)
                        v['semantic_inventory']=doc
            walk(f.meta);f.meta['semantic_inventory_availability']='complete_declared_composition';f.mutate(lambda _:None)
            contract=validate_bundle(f.bundle);self.assertEqual(contract['acceptedRowCount'],1)
            self.assertFalse(contract['usableRows'][0]['eligibleForTraining'])
            result=review.prepare([f.bundle],f.root/'qa',self.protected(f),count=1,exception_limit=0)
            self.assertEqual(result['crops'],dict(expected=2,completed=2));self.assertFalse(result['trainingEligible'])
            batch=json.loads((f.root/'qa/native-review/batch.json').read_text())
            expected='focus:tabItem' if recipe()['appearance']['composition']['definitions']['d']['kind']=='tab' else 'collectionItem'
            self.assertTrue(all(p['class']==expected for frame in batch['frames'] for p in frame['proposals']))
            with self.assertRaisesRegex(ValueError,'bundle_size_limit'):validate_bundle(f.bundle,max_total_bytes=1)
            for budget in (True,0,512*1024*1024+1):
                with self.assertRaisesRegex(ValueError,'invalid_bundle_budget'):validate_bundle(f.bundle,max_total_bytes=budget)
            # Real caller opts into the larger bounded campaign lane.
            original=review.validate_bundle
            with patch.object(review,'validate_bundle',wraps=original) as checked:
                review.source_record(f.bundle,set());self.assertEqual(checked.call_args.kwargs,{'max_total_bytes':512*1024*1024})
            doc=f.meta['focused_scene']['semantic_inventory'];s=f.meta['focused_scene']
            for fn in [lambda d:d.update(truncated=True),lambda d:d['elements'].pop(),
                       lambda d:d['elements'][0].update(declared_parent_id='bad'),
                       lambda d:d['elements'][-1].update(focusable=True)]:
                bad=copy.deepcopy(doc);fn(bad)
                with self.assertRaises(ValueError):semantic.validate(bad,s)
            with self.assertRaisesRegex(ValueError,'complete_without_composition'):semantic.validate(doc)
        finally:f.tearDown()

    def test_native_menu_tab_is_not_dropped_from_focus_review(self):
        r=recipe();c=r['appearance']['composition'];c['definitions']['d']['kind']='tab'
        c['styles']['s']['focus']['kind']='native_button';c['contents']['c'].pop('design')
        r['recipe_hash']=recipe_hash(r)
        with patch(__name__+'.recipe',return_value=r):self.test_actual_native_intake_and_capacity()

    @staticmethod
    def protected(f):
        p=f.root/'protected.json';p.write_text('{}');return p


if __name__=='__main__':unittest.main()
