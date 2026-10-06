import copy
import unittest
from harvest_sidecar_v2 import appearance_digest_source, recipe_hash, require
from fixture_native_visibility import visible_membership


def recipe(collection=False,rich=False):
    canvas=dict(version=2,columns=4 if collection else 1,spacing=40,inset=80,
        backgroundRGB=1450028,showLabels=True,pairing='competitor_v1',
        presentation='native_collection_v1' if collection else 'native_table_v2')
    if collection:canvas.update(collectionStyle='poster',cardGeometry=dict(version=1,width=360,height=640))
    else:
        canvas['nativeTable']=dict(version=2 if rich else 1,width=760,rowHeight=96,x=180,y=180)
        if rich:canvas['nativeTable'].update(viewportHeight=480,richContent=True);canvas['selectedIndex']=2
    return dict(schema_version=1,archetype='grid_matrix',element_count=12 if collection else 6,
        theme='dark',density='regular',seed=31,step_index=0,appearance=dict(version=1,
        preset='artwork',layout='standard',canvas=canvas,
        focus=dict(version=1,kind='native_image' if collection else 'native_button')))


def scene():
    ids=[f'grid_cell_{i//4}_{i%4}' for i in range(12)];visible=ids[:-1]
    exclusions={ids[-1]:'native_collection_offscreen'}
    return dict(recipe=recipe(True),focused_element_id=ids[0],elements=[dict(element_id=i) for i in visible],
        observation_diagnostics=dict(requiredIDs=visible,measuredIDs=visible,nativeProbe=dict(exclusionReasons=exclusions)),
        semantic_inventory=dict(coverage='partial',truncated=False,expected_control_ids=ids,visible_control_ids=visible,
            control_exclusions=exclusions,exclusions=exclusions,elements=[dict(id=i,role='control_wrapper') for i in visible]))


class Native84Tests(unittest.TestCase):
    def test_native_v3_strict_artwork_and_canonical(self):
        for design in ('city','orbit','collage','checkerboard'):
            for rich in (False,True):
                r=recipe(rich=True);r['appearance']['canvas']['nativeTable'].update(version=3,artwork=design,richContent=rich)
                self.assertIn(f':viewport=480:rich={str(rich).lower()}:artwork={design}',appearance_digest_source(r))
        for fields in (dict(artwork='unknown'),dict(artwork=None),dict(richContent=1),
                       dict(richContent=None),dict(viewportHeight=True),dict(version=2),dict(width=1401)):
            r=recipe(rich=True);r['appearance']['canvas']['nativeTable'].update(version=3,artwork='city')
            r['appearance']['canvas']['nativeTable'].update(fields)
            with self.assertRaises(ValueError):appearance_digest_source(r)

    def test_versioned_hash_inputs_and_legacy_compatibility(self):
        old=recipe();canonical=appearance_digest_source(old)
        null=copy.deepcopy(old);null['appearance']['canvas']['nativeTable'].update(viewportHeight=None,richContent=None)
        self.assertEqual(appearance_digest_source(null),canonical)
        self.assertNotEqual(recipe_hash(old),recipe_hash(recipe(rich=True)))
        self.assertIn(':native-table@2:760:96:180:180:viewport=480:rich=true',appearance_digest_source(recipe(rich=True)))
        self.assertIn(':collection=poster',appearance_digest_source(recipe(True)))

    def test_invalid_native_combinations_rejected(self):
        for collection,rich,field,value in ((False,False,'selectedIndex',2),(False,True,'columns',4),
            (True,False,'collectionStyle','unknown'),(True,False,'selectedIndex',0),(True,False,'showLabels',False),
            (False,False,'collectionStyle','poster')):
            r=recipe(collection,rich);r['appearance']['canvas'][field]=value
            with self.assertRaises(ValueError):appearance_digest_source(r)
        for fields in (dict(viewportHeight=100),dict(richContent=False),dict(version=3),dict(width=True),dict(viewportHeight=True)):
            r=recipe(rich=True);r['appearance']['canvas']['nativeTable'].update(fields)
            with self.assertRaises(ValueError):appearance_digest_source(r)

    def test_visibility_exclusions_require_observed_evidence(self):
        s=scene();self.assertEqual(len(visible_membership(s,require)),12)
        for field in ('expected_control_ids','visible_control_ids'):
            bad=copy.deepcopy(s);bad['semantic_inventory'][field]=[]
            with self.assertRaises(ValueError):visible_membership(bad,require)
        bad=copy.deepcopy(s);bad['focused_element_id']='grid_cell_2_3'
        with self.assertRaises(ValueError):visible_membership(bad,require)
        bad=copy.deepcopy(s);bad['observation_diagnostics']['requiredIDs']=[]
        with self.assertRaises(ValueError):visible_membership(bad,require)
        for reason,fields in (('native_hidden',dict(is_hidden=True)),('partially_clipped_bounds',dict(clipping='partially_clipped'))):
            bad=copy.deepcopy(s)
            bad['observation_diagnostics']['nativeProbe']['exclusionReasons']['grid_cell_2_3']=reason
            bad['semantic_inventory']['elements'].append(dict(id='grid_cell_2_3',role='control_wrapper',**fields))
            self.assertEqual(len(visible_membership(bad,require)),12)
            bad['semantic_inventory']['elements'][-1]=dict(id='grid_cell_2_3',role='control_wrapper')
            with self.assertRaises(ValueError):visible_membership(bad,require)


if __name__=='__main__':unittest.main()
