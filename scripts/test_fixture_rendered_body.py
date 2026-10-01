"""Exact body contract and versioned consumer projection; offline fixtures only."""
import json
import unittest
from fixture_rendered_body import validate
import fixture_batch_review as b
import human_annotation_review as h
import test_fixture_batch_review as review_fixtures


def body(eid='a', generation=7):
    return dict(version=1,role='rendered_control_body',coordinate_space='image_top_left_pixels',
        element_id=eid,generation=generation,source='uikit_focused_frame_guide',availability='measured',
        full_pixel_bounds=[5,5,90,90],visible_pixel_bounds=[5,5,90,90],visible_normalized_bounds=[.05,.05,.95,.95])


class BodyTests(unittest.TestCase):
    def test_measured_and_legacy(self):
        self.assertEqual(validate(body(),[100,100],'a',7),[5,5,90,90])
        self.assertIsNone(validate(None,[100,100],'a',7))

    def test_invalid_identity_protocol_and_geometry(self):
        for key,value in [('version',True),('version',2),('generation',8),('element_id','b'),
                ('source','guessed_scale'),('full_pixel_bounds',[0,0,float('nan'),5]),
                ('visible_pixel_bounds',[0,0,110,90]),('visible_normalized_bounds',[0,0,1,1]),
                ('clipping','partially_clipped')]:
            with self.subTest(key=key,value=value), self.assertRaises(ValueError):
                doc=body();doc[key]=value;validate(doc,[100,100],'a',7)

    def test_clipping(self):
        doc=body();doc.update(full_pixel_bounds=[-5,5,100,90],clipping='partially_clipped')
        self.assertEqual(validate(doc,[100,100],'a',7),[5,5,90,90])
        doc.update(clipping='fully_clipped',visible_pixel_bounds=None,visible_normalized_bounds=None)
        self.assertIsNone(validate(doc,[100,100],'a',7))

    def test_unavailable_and_moving(self):
        doc=body();doc.update(availability='unavailable',source='unsupported_native_control',
            unavailable_reason='unsupported_native_control')
        for key in ('full_pixel_bounds','visible_pixel_bounds','visible_normalized_bounds'):doc.pop(key)
        self.assertIsNone(validate(doc,[100,100],'a',7))
        doc['unavailable_reason']='animation_in_progress'
        with self.assertRaisesRegex(ValueError,'moving'):validate(doc,[100,100],'a',7)


class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.fixture=review_fixtures.ReviewTests();self.fixture.setUp();self.fixture.attach()

    def tearDown(self):self.fixture.tearDown()

    def test_v1_unchanged_v2_has_no_fallback(self):
        s,c=b.source_record(self.fixture.bundle,set())
        old=b.project([s],[c]); new=b.project([s],[c],body_geometry=True)
        self.assertTrue(old['frames'][0]['proposals'])
        self.assertTrue(all(f['disposition']=='blocked' for f in new['frames']))
        self.assertEqual(b.project([s],[c]),old)

    def test_body_crop_editor_and_sealed_validation(self):
        def walk(value):
            if isinstance(value,dict):
                for child in list(value.values()):walk(child)
                if 'scene_width' in value:
                    for e in value['elements']:
                        x,y,w,ht=e['pixel_bounds'];W,H=value['scene_width'],value['scene_height']
                        doc=body(e['element_id'],value['focus_observation']['generation'])
                        doc.update(full_pixel_bounds=[x,y,w,ht],visible_pixel_bounds=[x,y,w,ht],
                            visible_normalized_bounds=[x/W,y/H,(x+w)/W,(y+ht)/H])
                        e['rendered_body_geometry']=doc
            elif isinstance(value,list):
                for child in value:walk(child)
        walk(self.fixture.f.meta);self.fixture.f.mutate(lambda m:None)
        result=self.fixture.prepare(body_geometry=True,count=1)
        self.assertEqual(result['crops'],{'expected':2,'completed':2})
        path=self.fixture.root/'qa/native-review/batch.json'
        batch=h.validate_batch(path)
        self.assertEqual(batch['version'],b.BODY_VERSION)
        self.assertEqual(batch['frames'][0]['proposals'][0]['geometryRole'],'rendered_control_body')
        batch['frames'][0]['proposals'][0]['bounds'][0]+=1
        batch.pop('seal');batch['seal']=h.digest(batch);path.write_text(json.dumps(batch))
        with self.assertRaisesRegex(ValueError,'projection_changed'):h.validate_batch(path)

    def test_scene_binding_rejects_stale_or_moving_body(self):
        from harvest_sidecar_v2 import scene_check
        s,c=b.source_record(self.fixture.bundle,set())
        scene=c['usableRows'][0]['observationBinding']['focusedScene']
        e=scene['elements'][0];gen=scene['focus_observation']['generation']
        e['rendered_body_geometry']=body(e['element_id'],gen+1)
        with self.assertRaisesRegex(ValueError,'rendered_body:identity'):
            scene_check(scene,(scene['scene_width'],scene['scene_height']),scene['focused_element_id'])
        scene['is_settled']=False
        with self.assertRaisesRegex(ValueError,'scene_focus'):
            scene_check(scene,(scene['scene_width'],scene['scene_height']),scene['focused_element_id'])


if __name__=='__main__':unittest.main()
