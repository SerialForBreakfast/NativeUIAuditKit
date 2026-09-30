"""Offline source-contract tests, not live canvas qualification."""
import copy
import hashlib
import json
import unittest

from harvest_sidecar_v2 import appearance_digest_source, recipe_hash, SidecarError
from harvest_target_coverage import validate_coverage
from harvest_bundle_validation import validate_bundle, HarvestValidationError
import test_ttr_appearance as appearance_fixtures
from test_ttr_appearance import replace_recipes, recipe
from test_ttr_sidecar_v2 import reindex


def canvas_recipe():
    r = recipe('artwork', 'grid_matrix')
    r['appearance']['canvas'] = dict(version=1, columns=4, spacing=32, inset=80,
                                    backgroundRGB=2105376, showLabels=False)
    return r


class CanvasTests(unittest.TestCase):
    def test_received_canvas_v2_vectors(self):
        for presentation, columns, expected in (
            ('buttons',2,'76b9a0eb885bc80b9a290bbd759c20137f3525bad7cf032ee7686a4da6b07e1b'),
            ('settings_rows',1,'9583bc60898afa6ea101084189a12f3dbb01e30c5da95eb6b47a1ad4df1b421b'),
            ('tabs',2,'af1edeac4dce139e098249bb06fbb0cab77601293a480c5a36ca47e592bd0df8')):
            r=dict(schema_version=1,archetype='grid_matrix',density='regular',element_count=4,
                   seed=29001,step_index=0,theme='light',appearance=dict(version=1,preset='artwork',
                   layout='standard',focus=dict(version=1,kind='native_button'),canvas=dict(version=2,
                   columns=columns,inset=112,spacing=56,backgroundRGB=14211288,showLabels=True,
                   labels=['Home','Browse','Library','Search'],mixedSizes=True,pairing='competitor_v1',
                   presentation=presentation)))
            if presentation=='tabs': r['appearance']['canvas']['selectedIndex']=1
            self.assertEqual(recipe_hash(r),expected)
            for field,value in (('version',3),('fillViewport','true'),('background',{})):
                bad=copy.deepcopy(r);bad['appearance']['canvas'][field]=value
                with self.assertRaises(SidecarError):recipe_hash(bad)

    def test_live_producer_presentation_vectors(self):
        # Actual B76B7019 / DCA24AE6 exports, TTR399998d13500 + Fixture260aa9f867b6.
        # Expectations copied from producer metadata, not calculated by this test.
        for presentation, columns, selected, expected in (
            ('settings_rows', 1, None, 'ace2d4547737d203515c11a75412f47f8fc91292dc30a552e37cee34adebbfc8'),
            ('tabs', 4, 1, 'a9d6e770d88bfbf39e6a2316ae3b7fdebd21cf3b7d8e4b60f19faffcebe9b31a')):
            r = canvas_recipe(); r.update(element_count=4, theme='dark')
            r['appearance']['canvas'].update(columns=columns, showLabels=True,
                pairing='competitor_v1', presentation=presentation)
            if selected is not None: r['appearance']['canvas']['selectedIndex'] = selected
            r['appearance']['focus'] = {'version': 1, 'kind': 'native_button'}
            self.assertEqual(recipe_hash(r), expected)

    def test_presentation_identity_and_null_compatibility(self):
        r = canvas_recipe()
        c = r['appearance']['canvas']
        before = recipe_hash(r)
        c.update(presentation=None, selectedIndex=None, mixedSizes=None)
        self.assertEqual(recipe_hash(r), before)
        c.update(presentation='tabs', selectedIndex=1, mixedSizes=False, showLabels=True)
        r['appearance']['focus'] = {'version': 1, 'kind': 'native_button'}
        expected = (':appearance@1:artwork:standard:canvas@1:4:32:80:2105376:true'
                    ':presentation=tabs:selected=1:mixed=false'
                    ':focus@eyJraW5kIjoibmF0aXZlX2J1dHRvbiIsInZlcnNpb24iOjF9')
        self.assertEqual(appearance_digest_source(r), expected)
        r['appearance']['family_id'] = expected[1:].replace('appearance@1:artwork:standard:',
                                                          'appearance-v1.artwork.standard.', 1).replace(':focus@', '.focus@')
        self.assertEqual(appearance_digest_source(r), expected)
        old_hash = recipe_hash(r)
        c['selectedIndex'] = 0
        with self.assertRaisesRegex(SidecarError, 'appearance_family'): recipe_hash(r)
        del r['appearance']['family_id']
        self.assertNotEqual(recipe_hash(r), old_hash)
        c['mixedSizes'] = True
        self.assertIn(':mixed=true:', appearance_digest_source(r))

    def test_presentation_rejects_invalid_values_and_combinations(self):
        for field, values in {'presentation': [True, [], {}, 'future'],
                              'selectedIndex': [True, -1, 2, 64, 1.0, '1'],
                              'mixedSizes': [0, 1, 'false', []]}.items():
            for value in values:
                r = canvas_recipe()
                r['appearance']['canvas'].update(presentation='tabs', showLabels=True)
                r['appearance']['focus'] = {'version': 1, 'kind': 'native_button'}
                r['appearance']['canvas'][field] = value
                with self.subTest(field=field, value=value), self.assertRaises(SidecarError):
                    recipe_hash(r)
        for presentation in ('buttons', 'settings_rows', 'tabs'):
            r = canvas_recipe(); r['appearance']['canvas']['presentation'] = presentation
            with self.assertRaises(SidecarError): recipe_hash(r)
            r['appearance']['focus'] = {'version': 1, 'kind': 'native_button'}
            with self.assertRaises(SidecarError): recipe_hash(r)
            r['appearance']['canvas']['showLabels'] = True
            recipe_hash(r)
            r['appearance']['focus']['kind'] = 'native_image'
            with self.assertRaises(SidecarError): recipe_hash(r)
            r['appearance']['focus']['kind'] = 'native_button'
            if presentation != 'tabs':
                r['appearance']['canvas']['selectedIndex'] = 0
                with self.assertRaises(SidecarError): recipe_hash(r)

    def test_source_canonical_and_legacy_identity(self):
        r = canvas_recipe()
        suffix = ':appearance@1:artwork:standard:canvas@1:4:32:80:2105376:false'
        self.assertEqual(appearance_digest_source(r), suffix)
        # Literal source-derived vector, not claimed as an emitted producer receipt.
        canonical = '1:grid_matrix:2:light:regular:7:0:identity@1:system:regular:0:false:false:false:false' + suffix
        self.assertEqual(recipe_hash(r), hashlib.sha256(canonical.encode()).hexdigest())
        r['appearance']['family_id'] = 'appearance-v1.artwork.standard.canvas@1:4:32:80:2105376:false'
        self.assertEqual(appearance_digest_source(r), suffix)
        r['appearance']['canvas']['showLabels'] = True
        with self.assertRaises(SidecarError): recipe_hash(r)
        old = recipe('artwork','grid_matrix')
        null = copy.deepcopy(old); null['appearance']['canvas'] = None
        self.assertEqual(recipe_hash(old),recipe_hash(null))

    def test_closed_canvas_ranges_types_and_layouts(self):
        bad = {'version':[True,0,3], 'columns':[True,0,9,4.0], 'spacing':[15,81,'32'],
               'inset':[39,161,None], 'backgroundRGB':[-1,16777216,False],
               'showLabels':[0,1,'false']}
        for field,values in bad.items():
            for value in values:
                with self.subTest(field=field,value=value):
                    r=canvas_recipe(); r['appearance']['canvas'][field]=value
                    with self.assertRaises(SidecarError): recipe_hash(r)
        for c in ({}, [], False, {**canvas_recipe()['appearance']['canvas'],'extra':1}):
            r=canvas_recipe(); r['appearance']['canvas']=c
            with self.assertRaises(SidecarError): recipe_hash(r)
        for archetype,layout in [('media_shelf','standard'),('grid_matrix','dock')]:
            r=canvas_recipe(); r['archetype']=archetype; r['appearance']['layout']=layout
            with self.assertRaises(SidecarError): recipe_hash(r)

    def test_coverage_complete_and_incomplete_inventories(self):
        for n in (4,24):
            ids=[f'e{i}' for i in range(n)]
            rows=[{'metadata':{'recipeFile':'grid.json'},'expectedFocus':x} for x in ids]
            targets=[{'recipe':'grid.json','elementID':x,'outcome':'accepted'} for x in ids]
            receipt={'acceptedRowCount':n,'targetCoverage':{'targets':targets,'unavailableRecipes':[]}}
            self.assertTrue(validate_coverage(receipt,rows,{'grid.json':ids})['complete'])
            for state in ('excluded_by_limit','interrupted','unattempted','rejected'):
                changed=copy.deepcopy(receipt); changed['acceptedRowCount']=n-1
                changed['targetCoverage']['targets'][-1]['outcome']=state
                result=validate_coverage(changed,rows[:-1],{'grid.json':ids})
                self.assertFalse(result['complete']); self.assertEqual(result['counts'][state],1)
            with self.assertRaisesRegex(ValueError,'native_membership'):
                validate_coverage(receipt,rows,{'grid.json':ids+['missing']})

    def test_coverage_invalid_and_unknown(self):
        rows=[{'metadata':{'recipeFile':'a'},'expectedFocus':'e'}]
        target={'recipe':'a','elementID':'e','outcome':'accepted'}
        receipt={'acceptedRowCount':1,'targetCoverage':{'targets':[target],'unavailableRecipes':[]}}
        self.assertFalse(validate_coverage({},rows,{})['available'])
        self.assertFalse(validate_coverage(receipt,rows,{})['complete'])
        for coverage in ({}, {'targets':[target,target],'unavailableRecipes':[]},
                         {'targets':[target],'unavailableRecipes':['a']},
                         {'targets':[{**target,'outcome':'attempting'}],'unavailableRecipes':[]},
                         {'targets':[],'unavailableRecipes':[]}):
            with self.assertRaises(ValueError):
                validate_coverage({**receipt,'targetCoverage':coverage},rows,{'a':['e']})
        with self.assertRaises(ValueError): validate_coverage(receipt,rows*2,{'a':['e']})


class CanvasIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.fixture=appearance_fixtures.AppearanceTests(); self.fixture.setUp()
    def tearDown(self): self.fixture.tearDown()

    def test_actual_bundle_entrypoint_and_crop_cli(self):
        f=self.fixture; r=canvas_recipe(); r['recipe_hash']=recipe_hash(r)
        replace_recipes(f.meta,r); f.publish(f.meta)
        for name in ('manifest','calibration'):
            path=f.bundle/(name+'.json'); rows=json.loads(path.read_text())
            rows[0]['metadata']['recipeFile']='grid.json'; path.write_text(json.dumps(rows))
        path=f.bundle/'harvest-receipt.json'; receipt=json.loads(path.read_text())
        receipt['targetCoverage']={'targets':[{'recipe':'grid.json','elementID':'e','outcome':'accepted'}],
                                   'unavailableRecipes':[]}
        path.write_text(json.dumps(receipt)); reindex(f.bundle)
        result=validate_bundle(f.bundle)
        self.assertTrue(result['targetCoverage']['complete'])
        self.assertFalse(result['eligibleForTraining'])
        cli=f.cli('ttr_focus_manifest.py','--bundle',f.bundle,'--output',f.root/'crops',
                  '--corpus-id','test-canvas','--producer-reference','source-contract-test','--test-only')
        self.assertEqual(cli.returncode,0,cli.stdout+cli.stderr)
        self.assertTrue(json.loads(cli.stdout)['targetCoverage']['complete'])
        from ttr_focus_manifest import validate_ttr_manifest
        manifest=json.loads((f.root/'crops/focus_dataset_manifest.json').read_text())
        manifest['targetCoverage']['complete']=False
        with self.assertRaisesRegex(ValueError,'changed_target_coverage'):
            validate_ttr_manifest(manifest,f.bundle)
        receipt['targetCoverage']['targets'][0]['elementID']='wrong'
        path.write_text(json.dumps(receipt))
        with self.assertRaises(HarvestValidationError): validate_bundle(f.bundle)


if __name__ == '__main__': unittest.main()
