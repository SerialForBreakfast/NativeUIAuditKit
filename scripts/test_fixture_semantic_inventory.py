"""Generated contract fixtures and actual harvest caller tests; no model/runtime."""
import copy
import json
import unittest

from fixture_semantic_inventory import validate
from harvest_bundle_validation import validate_bundle, HarvestValidationError
import test_ttr_sidecar_v2 as fixtures


def inventory(scene):
    result=dict(version=1, scope='instrumented_scene_components', coverage='partial',
        unavailable_roles=['pixel_occlusion'], generation=scene['focus_observation']['generation'],
        width=scene['scene_width'], height=scene['scene_height'], focus_known=True,
        focused_id=scene['focused_element_id'], expected_control_ids=['e'], exclusions={}, truncated=False,
        elements=[dict(id='e', role='control_wrapper', native_class='UIButton', source='uikit_post_layout_view',
            focusable=True, input_focused=scene['elements'][0]['is_focused'], text_truncated=False,
            accessibility_label='Example', is_accessibility_element=True, accessibility_traits_raw=1,
            full_pixel_bounds=scene['elements'][0]['pixel_bounds'],
            visible_pixel_bounds=scene['elements'][0]['pixel_bounds'],
            visible_normalized_bounds=scene['elements'][0]['normalized_bounds'])])
    template=result['elements'][0]; result['elements']=[]; result['expected_control_ids']=[]
    for e in scene['elements']:
        wrapper=copy.deepcopy(template)
        wrapper.update(id=e['element_id'],input_focused=e['is_focused'],full_pixel_bounds=e['pixel_bounds'],
            visible_pixel_bounds=e['pixel_bounds'],visible_normalized_bounds=e['normalized_bounds'])
        result['elements'].append(wrapper); result['expected_control_ids'].append(e['element_id'])
    return result


class SemanticTests(unittest.TestCase):
    def setUp(self):
        self.doc=inventory(fixtures.scene('e', 5))

    def test_valid_partial_not_training(self):
        result=validate(self.doc)
        self.assertFalse(result['trainingEligible'])
        self.assertFalse(result['completeScene'])

    def test_native_projection_tolerance_and_unknown_anchor_focusability(self):
        element=self.doc['elements'][0]
        element.pop('focusable'); element['full_pixel_bounds']=[12.4,8.4,28,20]
        validate(self.doc)
        element['full_pixel_bounds']=[14,8,28,20]
        with self.assertRaises(ValueError): validate(self.doc)

    def test_adversarial_records(self):
        mutations=[lambda d:d.update(version=True), lambda d:d.update(generation=-1),
            lambda d:d.update(width=float('nan')), lambda d:d.update(focused_id='missing'),
            lambda d:d.update(expected_control_ids=['e','missing']), lambda d:d.update(exclusions={'e':'hidden'}),
            lambda d:d['elements'].append(copy.deepcopy(d['elements'][0])),
            lambda d:d['elements'][0].update(parent_id='missing'),
            lambda d:d['elements'][0].update(parent_id='e'),
            lambda d:d['elements'][0].update(visible_normalized_bounds=[0,0,1,1]),
            lambda d:d['elements'][0].update(full_pixel_bounds=[0,0,0,1]),
            lambda d:d['elements'][0].update(role='unknown'),
            lambda d:d['elements'][0].update(is_accessibility_element=False),
            lambda d:d['elements'][0].update(accessibility_label=''),
            lambda d:d['elements'][0].update(accessibility_traits_raw=True),
            lambda d:d.update(focus_known=False)]
        for mutation in mutations:
            with self.subTest(mutation=mutations.index(mutation)):
                doc=copy.deepcopy(self.doc); mutation(doc)
                with self.assertRaises(ValueError): validate(doc)

    def test_optional_legacy_accessibility_and_declared_defect(self):
        self.doc['elements'][0].pop('is_accessibility_element')
        validate(self.doc)
        self.doc['elements'][0].update(is_accessibility_element=True,accessibility_label='',declared_defect='missing_label')
        validate(self.doc)

    def test_unknown_focus_and_partial_clipping(self):
        self.doc.update(focus_known=False,focused_id=None,truncated=True)
        self.doc['elements'][0].update(input_focused=None, full_pixel_bounds=[-2,0,12,10],
            visible_pixel_bounds=[0,0,10,10],visible_normalized_bounds=[0,0,10/64,10/48],clipping='partially_clipped')
        self.assertFalse(validate(self.doc)['focusKnown'])
        self.doc['elements'][0].update(clipping='fully_clipped',visible_pixel_bounds=None,visible_normalized_bounds=None)
        validate(self.doc)

    def test_parent_cycle_and_standalone_native_labels(self):
        label=copy.deepcopy(self.doc['elements'][0]); label.update(id='label',role='label_view',native_class='UILabel',focusable=False,input_focused=None)
        self.doc['elements'].append(label); validate(self.doc)
        self.doc['elements'][0]['parent_id']='label'; label['parent_id']='e'
        with self.assertRaisesRegex(ValueError,'parent_cycle'): validate(self.doc)


class BundleTests(unittest.TestCase):
    setUp=fixtures.V2Tests.setUp
    tearDown=fixtures.V2Tests.tearDown
    mutate=fixtures.V2Tests.mutate

    def attach(self):
        def walk(value):
            if isinstance(value,dict):
                for child in list(value.values()): walk(child)
                if 'scene_width' in value: value['semantic_inventory']=inventory(value)
            elif isinstance(value,list):
                for child in value: walk(child)
        walk(self.meta)
        self.meta['semantic_inventory_availability']='partial_instrumented_components'

    def test_actual_bundle_preserves_raw_semantics_and_legacy(self):
        validate_bundle(self.bundle)
        self.attach(); self.mutate(lambda m:None)
        result=validate_bundle(self.bundle)
        self.assertEqual(result['usableRows'][0]['observationBinding']['focusedScene']['semantic_inventory'],self.meta['focused_scene']['semantic_inventory'])
        self.assertFalse(result['usableRows'][0]['eligibleForTraining'])

    def test_changed_disappearing_and_bad_geometry_rejected(self):
        self.attach()
        for mutation in [
            lambda m:m['focused_capture']['before_scene']['semantic_inventory']['elements'][0].update(accessibility_label='Changed'),
            lambda m:m['reference_capture']['before_scene'].pop('semantic_inventory'),
            lambda m:m['focused_scene']['semantic_inventory'].update(generation=0),
            lambda m:m['focused_capture']['after_scene']['semantic_inventory']['elements'][0].update(visible_pixel_bounds=[0,0,1,1]),
            lambda m:m.update(semantic_inventory_availability='unavailable_legacy')]:
            self.mutate(mutation)
            with self.assertRaises(HarvestValidationError): validate_bundle(self.bundle)

    def test_flat_alias_conflict(self):
        self.attach()
        self.mutate(lambda m:m['semantic_inventory'].update(generation=99))
        with self.assertRaisesRegex(HarvestValidationError,'flat_alias'): validate_bundle(self.bundle)

    def test_competitor_v3_semantics(self):
        from test_ttr_competitor import competitor_meta
        self.meta=competitor_meta(self.meta); self.attach(); self.mutate(lambda m:None)
        result=validate_bundle(self.bundle)
        self.assertEqual(result['usableRows'][0]['observationBinding']['baselineScene']['semantic_inventory']['focused_id'],'x')


class LegacyTests(unittest.TestCase):
    def test_inventory_cannot_bypass_brackets(self):
        from test_harvest_bundle_validation import H1Tests
        f=H1Tests(); f.setUp()
        try:
            f.replace_metadata(lambda m:m.update(semantic_inventory={}))
            with self.assertRaisesRegex(HarvestValidationError,'requires_native_brackets'): validate_bundle(f.d)
        finally: f.tearDown()


if __name__=='__main__': unittest.main()
