"""Isolated native-export summary compatibility; no retained data dependency."""
import copy
import json
import unittest
from harvest_bundle_validation import validate_bundle, HarvestValidationError
from test_harvest_bundle_validation import H1Tests


class ViewTests(H1Tests):
    def views(self):
        r=self.row()
        return {'focus-view.json':dict(schema_version=1,role='focus_appearance',admission='consumer_pending',
            entries=[dict(id=r['id'],before_image='u.png',after_image='f.png',after_sha256=r['sha256'],
                evidence_sidecar='m.json',bounds=r['box'],focus_label='e',split='training',
                control_mode='direct_focus_assignment',temporal_settlement='not_established',
                provenance='use_original_capture_brackets; not_atomic_callback_identity')]),
            'intent-action-view.json':dict(schema_version=1,role='intent_action',admission='unavailable',
                entries=[],excluded_ids=['synth-0'],reason='direct_focus_assignment_is_not_directional_action')}

    def save_views(self, views):
        for name,doc in views.items():(self.d/name).write_text(json.dumps(doc))
        self.reindex()

    def test_optional_views_preserve_legacy_labels_and_originals(self):
        before=validate_bundle(self.d)
        self.save_views(self.views())
        self.assertEqual(validate_bundle(self.d),before)

    def test_summary_mismatch_and_invented_action_rejected(self):
        for key,value in [('id','wrong'),('after_sha256','0'*64),('bounds',[0,0,2,2]),
                          ('focus_label','other'),('split','held-out'),('control_mode','directional')]:
            views=self.views();views['focus-view.json']['entries'][0][key]=value;self.save_views(views)
            with self.assertRaises(HarvestValidationError):validate_bundle(self.d)
        views=self.views();views['intent-action-view.json']['entries']=[{'action':'right'}];self.save_views(views)
        with self.assertRaises(HarvestValidationError):validate_bundle(self.d)

    def test_unknown_version_artifact_and_changed_hash_rejected(self):
        views=self.views();views['focus-view.json']['schema_version']=2;self.save_views(views)
        with self.assertRaises(HarvestValidationError):validate_bundle(self.d)
        self.save_views(self.views());(self.d/'focus-view.json').write_text('{}')
        with self.assertRaisesRegex(HarvestValidationError,'integrity_failed'):validate_bundle(self.d)
        self.save_views(self.views());(self.d/'unknown.json').write_text('{}');self.reindex()
        with self.assertRaises(HarvestValidationError):validate_bundle(self.d)


if __name__=='__main__':unittest.main()
