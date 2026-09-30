"""Source-pinned revision2 vectors and real intake; no runtime or prior reports needed."""
import copy
import itertools
import json
import unittest

from harvest_sidecar_v2 import SidecarError, recipe_hash
from harvest_bundle_validation import validate_bundle, HarvestValidationError
import test_ttr_appearance as fixtures
from test_ttr_appearance import replace_recipes
from test_ttr_competitor import competitor_meta
from test_ttr_canvas import canvas_recipe

# Producer archive51c90bbb..., proposal.json; family/content/background/geometry order.
HASHES = '''9843d606b9a9f72cfcd3cfa1d85aaf74755be1f298a71a78656ade6c8b604594
69b3b8d606c5e2a34ed6f6c5d51ba5d91c6cf5f1158de2381dc15ad2fc8bfd9b
38438442c4a75933721dbaddc5a12aa01e6ab9b8811fd1554b84bacd19c5bac7
b12ec46133773166c50496540f9a76a3b2fb70fee294efe64dbf84f64a0610c0
2ae4e947efd0267d87077344db87c766ce1d9cecc03a7702fff79778fa0c70f2
e026f82cd0f431a51d373a658d27aa038509cb97585f5da60c3679cc2c7146fd
6dbbd42aa6e4dff3f310c06dbb4c2311ec742702f49afac55597e59c3f20080f
6ddaab0c94a5aa5310981d0e1d45d77cd64de0bbc5d0b1f8654d608655ac2089
e55b145b85452efe7f5e28879531a3bcdbeb1d5dc238e92cc5a4f617be437e59
48eb632c9f978b4ff0bc78379c743bee13fa2f01a2f2c929ebd523b92111d508
3f28b58051c9d82dad9a1ea73757544b099669fe5a93d20d9ad2e6ea1bf1cd8d
4a0f25965dfc39a438e07bcec15e6ffb6ddf1f2bef2bd322e4db20431b011dda
d55af97bdd1036a5140feae6478889963741d11012744e50a0dcae6887585da7
3f561fb634a06c693907bd6b3ac6ad47a60cb2e7579346c0472da549d51724cb
771de3b9bbc700630886e96b85cd122a30b4df7fedc6eb478c5f3ccd236f3a44
9a7b541f3d8eb4e2ad7392c5b80c6c98c32491a568685f6219fbda535c83e58f
d6473310336148514c86a694b42fc57d5c6df8516ca97557bc906d6c39111fea
d689ff37ff1020bf6e6500f204da583a2db397fdc81978ad0830e00bb9a78d5a
00d9dce564bfc039db4fdcf754732898bc0d0313bd70699b131668556bfd853b
a7871e729c60e20143cf031bd253178a29bcd2292b1868a114b5c87776bad0fc
66fc050ebc11b2692fb44f5f0003a91fd9ba4801725f31eba023a6ff977f018c
1580955c93aa97f305152250fd96703445d31d8b89e1596ca83caf92527c5b58
dac975f7523016c49284154ad959980aa084b772b17f69407d629e3b34183e98
58b3e35c0788b9c940cac37948c693d9fc107e839f11c1b7ac22fa175dc0c24a'''.split()


def recipe(family='icon', content=0, background=0, geometry=0):
    button = family == 'wide_button'
    canvas = dict(version=2, columns=1 if button else 4, spacing=32, inset=80,
                  backgroundRGB=(0x202020, 0x982C18)[background], showLabels=button,
                  pairing='competitor_v1', presentation='buttons' if button else 'cards')
    appearance = dict(version=1, preset='artwork', layout='standard', canvas=canvas,
                      focus=dict(version=1, kind='native_button' if button else 'native_image'))
    if button:
        canvas.update(labels=[('Play', 'View Collection')[content], 'Other'],
                      nativeButton=dict(version=1, width=(600, 900)[geometry], restingFill='light'))
    else:
        w, h = {'icon': [(320, 200), (200, 200)],
                'artwork_card': [(201, 300), (320, 200)]}[family][geometry]
        canvas.update(fillViewport=False, mixedSizes=False,
                      cardGeometry=dict(version=1, width=w, height=h))
        appearance['artwork'] = dict(version=1, familyID='matched-appearance24-v2',
                                    seed=31000, split='calibration', assets=[],
                                    motifs=[{'icon': ('icon', 'emblem'),
                                             'artwork_card': ('landscape', 'cityscape')}[family][content]])
    return dict(schema_version=1, archetype='grid_matrix', element_count=2 if button else 8,
                density='regular', theme='dark', seed=31000, step_index=0, appearance=appearance)


class Revision2Tests(unittest.TestCase):
    def test_all_producer_hashes(self):
        axes = itertools.product(('icon', 'artwork_card', 'wide_button'), range(2), range(2), range(2))
        for args, expected in zip(axes, HASHES, strict=True):
            with self.subTest(args=args):
                self.assertEqual(recipe_hash(recipe(*args)), expected)

    def test_legacy_null_and_changed_identity(self):
        r = canvas_recipe(); old = recipe_hash(r)
        r['appearance']['canvas'].update(nativeButton=None, cardGeometry=None)
        self.assertEqual(recipe_hash(r), old)
        for family, key, field, value in [('icon', 'cardGeometry', 'width', 321),
                                         ('wide_button', 'nativeButton', 'restingFill', 'gray')]:
            r = recipe(family); before = recipe_hash(r)
            r['appearance']['canvas'][key][field] = value
            self.assertNotEqual(recipe_hash(r), before)

    def test_strict_fields_types_ranges_and_combinations(self):
        for family, key, fields in [('icon', 'cardGeometry', {'version':[True,2],
                    'width':[True,79,1201,320.0,float('nan')], 'height':[71,901,float('inf')],
                    'future':[1]}), ('wide_button', 'nativeButton', {'version':[True,2],
                    'width':[False,119,1201,600.0], 'restingFill':['white',[],None], 'future':[1]})]:
            for field, values in fields.items():
                for value in values:
                    r=recipe(family); r['appearance']['canvas'][key][field]=value
                    with self.subTest(key=key,field=field,value=value), self.assertRaises(SidecarError):
                        recipe_hash(r)
            for field, value in [('version',1),('fillViewport',True),('mixedSizes',True),('presentation','tabs')]:
                r=recipe(family);r['appearance']['canvas'][field]=value
                with self.assertRaises(SidecarError):recipe_hash(r)
            r=recipe(family);r['appearance']['canvas'][key].pop('version')
            with self.assertRaises(SidecarError):recipe_hash(r)
        r=recipe();r['appearance']['canvas']['nativeButton']=dict(version=1,width=600,restingFill='light')
        with self.assertRaises(SidecarError):recipe_hash(r)
        r=recipe('wide_button');r['appearance']['artwork']=recipe()['appearance']['artwork']
        with self.assertRaises(SidecarError):recipe_hash(r)
        r=recipe('wide_button');r['appearance']['focus']['kind']='native_image'
        with self.assertRaises(SidecarError):recipe_hash(r)
        r=recipe();r['appearance']['artwork']['motifs']=['future']
        with self.assertRaises(SidecarError):recipe_hash(r)

    def test_actual_bundle_and_cli_without_invented_artwork_bounds(self):
        for family in ('icon', 'artwork_card', 'wide_button'):
            with self.subTest(family=family):
                self.check_bundle(family)

    def check_bundle(self, family):
        f=fixtures.AppearanceTests();f.setUp()
        try:
            # Small two-control native fixture, not a real viewport fit test.
            r=recipe(family, content=1);r['element_count']=2;r['recipe_hash']=recipe_hash(r)
            f.meta=competitor_meta(f.meta)
            replace_recipes(f.meta,r);f.publish(f.meta)
            self.assertEqual(len(validate_bundle(f.bundle)['usableRows']),1)
            out=f.root/'revision2-crops'
            result=f.cli('ttr_focus_manifest.py','--bundle',f.bundle,'--output',out,
                         '--corpus-id','test-r2','--producer-reference','revision2-test','--test-only')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            meta=copy.deepcopy(f.meta)
            key='nativeButton' if family=='wide_button' else 'cardGeometry'
            meta['reference_capture']['before_scene']['recipe']['appearance']['canvas'][key]['width']=901
            f.publish(meta)
            with self.assertRaises(HarvestValidationError):validate_bundle(f.bundle)
        finally:f.tearDown()


if __name__ == '__main__':unittest.main()
