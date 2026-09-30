"""Offline SYNTH05 producer vectors and fail-closed compatibility tests."""
import base64
import copy
import io
import json
from pathlib import Path
import tempfile
import tarfile
import unittest

from harvest_artwork import artwork_identity, validate_hierarchy, swift_json
from harvest_sidecar_v2 import require, SidecarError, recipe_hash
from synth05_receive import bounded_members
from test_ttr_canvas import canvas_recipe
from test_ttr_sidecar_v2 import write_bundle, reindex
from test_ttr_appearance import replace_recipes
from harvest_bundle_validation import validate_bundle, HarvestValidationError
from focus_dataset_contract import ROOT
from synth05_intake import verify_package


def nested():
    r = canvas_recipe()
    r.update(element_count=6, theme='dark')
    r['appearance']['canvas'].update(columns=2,showLabels=True,pairing='competitor_v1',
        presentation='nested_tabs_v1',selectedIndex=1,tabCount=2,
        labels=['Home','Browse','Popular','Recently Added','Saved','Recommended'])
    r['appearance']['focus'] = {'version':1,'kind':'native_button'}
    return r


def artwork():
    return dict(version=1,familyID='procedural-checkerboard',seed=1907,split='calibration',
                motifs=['checkerboard'],assets=[])


def hierarchy():
    r = nested()
    return {'recipe':r,'elements':[dict(element_id=f'grid_cell_{i//3}_{i%3}',
        parent_element_id=None if i<2 else 'grid_cell_0_1',taxonomy_class='primaryButton',
        accessibility_traits=['isButton']+(['isSelected'] if i==1 else []),
        text_content=r['appearance']['canvas']['labels'][i],is_focused=i==3) for i in range(6)]}


class Synth05Tests(unittest.TestCase):
    def test_actual_producer_nested_vector(self):
        self.assertEqual(recipe_hash(nested()),
                         '7e584685e1f7aca183781a1e6f8572b3e7548ced3ae9c70dd94714ae0db04973')

    def test_actual_producer_artwork_vector(self):
        r = canvas_recipe(); r.update(element_count=4,theme='dark')
        r['appearance']['canvas'].update(pairing='competitor_v1',mixedSizes=True)
        r['appearance'].update(focus={'version':1,'kind':'native_image'},artwork=artwork())
        self.assertEqual(recipe_hash(r),'da64cfabf830230e851a979ca07469ccc9f70d8d16f386e5cb8acf0daf789773')

    def test_optional_absence_keeps_legacy_hash(self):
        r=canvas_recipe(); h=recipe_hash(r)
        r['appearance'].update(artwork=None)
        r['appearance']['canvas'].update(tabCount=None,labels=None)
        self.assertEqual(recipe_hash(r),h)

    def test_labels_and_nested_combinations(self):
        for field,values in {'labels':[[],['a']*5,['a']*7,['x\n']*6,['x'*129]*6],
                             'tabCount':[None,True,1,6,9], 'selectedIndex':[None,-1,2,True]}.items():
            for v in values:
                r=nested();r['appearance']['canvas'][field]=v
                with self.subTest(field=field,value=v),self.assertRaises(SidecarError):recipe_hash(r)
        r=nested();r['appearance']['canvas']['presentation']='tabs'
        with self.assertRaises(SidecarError):recipe_hash(r)

    def test_swift_utf8_slash_identity(self):
        self.assertEqual(swift_json(['é/a']),b'["\xc3\xa9\\/a"]')

    def test_hierarchy_selection_not_focus_and_reordered_elements(self):
        s=hierarchy();validate_hierarchy(s,require)
        self.assertFalse(s['elements'][1]['is_focused'])
        self.assertTrue(s['elements'][3]['is_focused'])
        s['elements'].reverse();validate_hierarchy(s,require)

    def test_hierarchy_bad_parent_selection_labels_membership(self):
        for key,v in [('parent_element_id','missing'),('parent_element_id','grid_cell_1_0'),
                      ('parent_element_id',None),('accessibility_traits',['isSelected']),
                      ('text_content','wrong'),('element_id','alien')]:
            s=hierarchy();s['elements'][3][key]=v
            with self.subTest(key=key,value=v),self.assertRaises(SidecarError):validate_hierarchy(s,require)
        s=hierarchy();s['elements'][1]['parent_element_id']='grid_cell_1_0'
        with self.assertRaises(SidecarError):validate_hierarchy(s,require)

    def test_artwork_invalid_descriptor(self):
        for key,v in [('version',True),('seed',-1),('familyID','../escape'),('split','test'),
                      ('motifs',['unknown']),('motifs',['flat','flat']),('motifs',['imported']),
                      ('assets',[{}])]:
            a=artwork();a[key]=v
            with self.subTest(key=key,value=v),self.assertRaises(SidecarError):artwork_identity(a,require)

    def test_embedded_asset_actual_hash_and_negative_cases(self):
        png='iVBORw0KGgoAAAANSUhEUgAAACAAAAAYCAYAAACbU/80AAAAAXNSR0IArs4c6QAAAERlWElmTU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAAAIKADAAQAAAABAAAAGAAAAAA915G0AAAAMUlEQVRIDWOMWXXtP8MAAqYBtBts9agDRkNgNARGQ2A0BEZDYDQERkNgNARGQ2A0BACwvwMLpDhY3gAAAABJRU5ErkJggg=='
        h='b86ef16dab2d8216d6d0e1ea8dd6bff17172680cf19ea2350d998bf53736ca9d'
        asset=dict(id='owned-test',familyID='test-family',sha256=h,width=32,height=24,png=png,
            source='generated-test-fixture',creator='TVTestRig',license='owned',
            attribution='TVTestRig generated calibration fixture',redistributionAllowed=True,
            derivativesAllowed=True,fit='fit',transformedSHA256=h,preprocessing='original_png_v1',colorSpace='sRGB')
        a=dict(version=1,familyID='test-family',seed=1,split='calibration',motifs=['imported'],assets=[asset])
        artwork_identity(a,require)
        r=canvas_recipe();r.update(element_count=4,theme='dark')
        r['appearance']['canvas'].update(pairing='competitor_v1')
        r['appearance'].update(focus={'version':1,'kind':'native_image'},artwork=a)
        self.assertEqual(recipe_hash(r),'1d9bc91ffac1913c7cd9cb8a3d9e262b49c5c7beb5c341298622c2d0ea973937')
        for key,v in [('png','garbage'),('width',33),('sha256','0'*64),('familyID','another'),
                      ('derivativesAllowed',False),('license','unknown'),('transformedSHA256','0'*64)]:
            b=copy.deepcopy(a);b['assets'][0][key]=v
            with self.subTest(key=key),self.assertRaises(SidecarError):artwork_identity(b,require)

    def test_archive_root_only_directory_exception(self):
        root=tarfile.TarInfo('./');root.type=tarfile.DIRTYPE
        file=tarfile.TarInfo('./a');file.size=2
        members,size=bounded_members([root,file]);self.assertEqual(size,2);self.assertEqual(len(members),1)
        for bad in [tarfile.TarInfo('.'),tarfile.TarInfo('../a'),tarfile.TarInfo('/a')]:
            with self.assertRaises(ValueError):bounded_members([bad])
        link=tarfile.TarInfo('link');link.type=tarfile.SYMTYPE
        with self.assertRaises(ValueError):bounded_members([link])
        with self.assertRaises(ValueError):bounded_members([root,root])
        with self.assertRaises(ValueError):bounded_members([file,file])

    def test_real_importer_artwork_split_and_changed_bytes(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.build/debug-output') as temp:
            root=Path(temp)/'bundle';meta=write_bundle(root)
            r=canvas_recipe();r['appearance']['artwork']=artwork()
            r['recipe_hash']=recipe_hash(r);replace_recipes(meta,r)
            (root/'m.json').write_text(json.dumps(meta));reindex(root)
            self.assertEqual(validate_bundle(root)['acceptedRowCount'],1)
            r['appearance']['artwork']['split']='training';r['recipe_hash']=recipe_hash(r)
            replace_recipes(meta,r);(root/'m.json').write_text(json.dumps(meta));reindex(root)
            with self.assertRaisesRegex(HarvestValidationError,'artwork_split_reservation'):validate_bundle(root)
            (root/'u.png').write_bytes(b'corrupt')
            with self.assertRaisesRegex(HarvestValidationError,'integrity_failed'):validate_bundle(root)

    def test_manifest_missing_changed_unlisted_and_duplicate(self):
        import hashlib
        with tempfile.TemporaryDirectory(dir=ROOT/'.build/debug-output') as temp:
            root=Path(temp);file=root/'a';file.write_bytes(b'a')
            entry={'path':'a','bytes':1,'sha256':hashlib.sha256(b'a').hexdigest()}
            manifest=root/'manifest.json';manifest.write_text(json.dumps({'files':[entry]}))
            self.assertEqual(verify_package(manifest)['membersVerified'],1)
            file.write_bytes(b'b')
            with self.assertRaisesRegex(ValueError,'member_integrity'):verify_package(manifest)
            file.unlink()
            with self.assertRaisesRegex(ValueError,'member_integrity'):verify_package(manifest)
            file.write_bytes(b'a');(root/'extra').write_bytes(b'x')
            with self.assertRaisesRegex(ValueError,'unlisted_capture_member'):verify_package(manifest)
            manifest.write_text(json.dumps({'files':[entry,entry]}))
            with self.assertRaisesRegex(ValueError,'manifest_member_path'):verify_package(manifest)


if __name__=='__main__':unittest.main()
