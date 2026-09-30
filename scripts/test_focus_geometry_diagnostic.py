"""Real intake + production crop CLI, with isolated source-shaped geometry fixtures."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from focus_dataset_contract import ROOT, validate_manifest
from focus_geometry_diagnostic import ROLE, WRAPPER, derive, plan, sha, validate_report
from harvest_artwork_geometry import STATUS
from harvest_bundle_validation import validate_bundle
from test_ttr_sidecar_v2 import write_bundle, reindex
from ttr_focus_manifest import derive as intake


def geometry():
    return {'version': 1, 'source': ROLE, 'presentation_bounds_status': STATUS,
            'pixel_bounds': [16,12,16,8], 'normalized_bounds': [.25,.25,.5,20/48]}


def change_geometry(meta, value):
    # Each flat/scene/bracket alias is independently serialized in producer JSON.
    def walk(v):
        if isinstance(v, dict):
            if 'element_id' in v:
                v['artwork_geometry'] = copy.deepcopy(value)
            for child in list(v.values()): walk(child)
        elif isinstance(v, list):
            for child in v: walk(child)
    walk(meta)


class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(dir=ROOT/'.build/debug-output', prefix='geometry-test-'))
        self.bundle = self.root/'bundle'
        self.meta = write_bundle(self.bundle)

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, meta):
        (self.bundle/'m.json').write_text(json.dumps(meta))
        reindex(self.bundle)

    def source(self, value=None, name='intake'):
        if value is not None:
            change_geometry(self.meta, value)
            self.write(self.meta)
        output = self.root/name
        intake(self.bundle, output, 'geometry-test-only', 'source-pinned-offline', test_only=True)
        return output/'focus_dataset_manifest.json'

    def test_cli_valid_geometry_role_identity_and_legacy_pixel_parity(self):
        manifest = self.source(geometry())
        original = json.loads(manifest.read_text())
        source_hashes = {p.name: sha(p) for p in self.bundle.iterdir()}
        for role in (WRAPPER, ROLE):
            output = self.root/role
            result = subprocess.run([sys.executable, str(ROOT/'scripts/focus_geometry_diagnostic.py'),
                '--manifest', str(manifest), '--manifest-sha256', sha(manifest),
                '--geometry-role', role, '--output', str(output)], capture_output=True, text=True,
                timeout=120, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((output/'geometry-diagnostic.json').read_text())
            self.assertEqual(validate_report(report, output), {'rendered':2,'blocked':0,'failed':0})
            self.assertFalse((output/'focus_dataset_manifest.json').exists())
            with self.assertRaises(ValueError): validate_manifest(report, output)
            if role == WRAPPER:
                wrapper = report
                for row in report['records']:
                    state = row['binding']['state']
                    self.assertEqual(row['crop']['sha256'], original['pairs'][0][state+'_crop_sha256'])
            else:
                self.assertNotEqual([r['id'] for r in wrapper['records']], [r['id'] for r in report['records']])
                self.assertTrue(all(r['binding']['selectedBounds'] == [16,12,16,8] for r in report['records']))
        self.assertEqual(source_hashes, {p.name: sha(p) for p in self.bundle.iterdir()})

    def test_absent_null_and_explicit_unavailable_do_not_fallback(self):
        for i, value in enumerate((None, {'version':1,'source':ROLE,'presentation_bounds_status':STATUS,
                                         'unavailable_reason':'clipped'})):
            if value is None: change_geometry(self.meta, None); self.write(self.meta)
            manifest = self.source(value, 'intake'+str(i))
            report = derive(manifest, sha(manifest), self.root/('out'+str(i)), ROLE)
            self.assertEqual(report['counts'], {'rendered':0,'blocked':2,'failed':0})
            self.assertTrue(all(r['binding']['selectedBounds'] is None and 'crop' not in r for r in report['records']))
        # Legacy absence also stays valid and unavailable.
        def remove(v):
            if isinstance(v,dict):
                v.pop('artwork_geometry',None)
                for c in v.values(): remove(c)
            elif isinstance(v,list):
                for c in v: remove(c)
        remove(self.meta); self.write(self.meta)
        self.assertEqual(validate_bundle(self.bundle)['acceptedRowCount'],1)

    def test_invalid_geometry_matrix_and_bracket_binding(self):
        variants = [dict(version=2), dict(version=True), dict(source='visible_pixels'),
                    dict(presentation_bounds_status='measured'), dict(presentation_bounds=[1,2,3,4]),
                    dict(pixel_bounds=[0,0,float('nan'),1]), dict(pixel_bounds=[0,0,65,1]),
                    dict(pixel_bounds=[True,0,1,1]), dict(normalized_bounds=[0,0,1,1]),
                    dict(unavailable_reason='clipped'), dict(pixel_bounds=None),
                    dict(unavailable_reason='unknown',pixel_bounds=None,normalized_bounds=None)]
        for changes in variants:
            with self.subTest(changes=changes):
                meta = copy.deepcopy(self.meta)
                value = geometry(); value.update(changes); change_geometry(meta, value); self.write(meta)
                with self.assertRaises(ValueError): validate_bundle(self.bundle)
        for kind in ('geometry','element'):
            meta = copy.deepcopy(self.meta); change_geometry(meta, geometry())
            e = meta['focused_capture']['before_scene']['elements'][0]
            if kind == 'geometry': e['artwork_geometry'] = None
            else: e['element_id'] = 'wrong'
            self.write(meta)
            with self.assertRaises(ValueError): validate_bundle(self.bundle)

    def test_changed_hash_membership_protocol_and_crop_rejected(self):
        manifest = self.source(geometry())
        output = self.root/'out'
        report = derive(manifest, sha(manifest), output, ROLE)
        for change in (lambda d:d.update(version='future'), lambda d:d['records'].pop(),
                       lambda d:d['records'].append(copy.deepcopy(d['records'][0])),
                       lambda d:d['records'][0]['binding'].update(elementID='wrong'),
                       lambda d:d['runtime'].update(helperSHA256='0'*64),
                       lambda d:d.update(errors=['failed'])):
            bad=copy.deepcopy(report); change(bad)
            with self.assertRaises(ValueError): validate_report(bad, output)
        with self.assertRaisesRegex(ValueError,'changed_source_manifest'):
            plan(manifest, '0'*64, ROLE)
        crop=output/report['records'][0]['crop']['path']; crop.write_bytes(b'bad')
        with self.assertRaises(ValueError): validate_report(report,output)
        (self.bundle/'f.png').write_bytes(b'bad')
        with self.assertRaises(ValueError): plan(manifest,sha(manifest),ROLE)

    def test_protected_manifest_and_changed_member_rejected_before_crop(self):
        manifest=self.source()
        doc=json.loads(manifest.read_text())
        for role in ('test','held-out','final-challenge'):
            bad=copy.deepcopy(doc); bad['pairs'][0]['original_split']=role
            manifest.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError,'protected_or_unsupported'):
                plan(manifest,sha(manifest),WRAPPER)
        doc['pairs'][0]['elementID']='wrong'; manifest.write_text(json.dumps(doc))
        with self.assertRaises(ValueError): plan(manifest,sha(manifest),WRAPPER)

    def test_geometry_cannot_bypass_brackets_in_legacy_sidecar(self):
        change_geometry(self.meta, geometry()); self.meta.pop('schema_version'); self.write(self.meta)
        with self.assertRaisesRegex(ValueError,'artwork_geometry_requires_v2_brackets'):
            validate_bundle(self.bundle)

    def test_producer_wire_vector_and_admission_rejection(self):
        from harvest_artwork_geometry import validate
        from harvest_sidecar_v2 import require
        from focus_training_preflight import preflight
        from focus_ring_baseline import prepare_protocol
        # Exact numeric vector from producer Scripts/check-native-focus-observation.swift,
        # archive a8d7d219...6059. Dimensions implied by normalized geometry: 100square.
        value={'version':1,'source':ROLE,'presentation_bounds_status':STATUS,
               'pixel_bounds':[10,20,80,40],'normalized_bounds':[.1,.2,.9,.6]}
        validate(value,(100,100),require)
        manifest=self.source(geometry()); output=self.root/'diagnostics'
        report=derive(manifest,sha(manifest),output,ROLE)
        # Even renaming the diagnostic report cannot admit it to the trainer.
        (output/'focus_dataset_manifest.json').write_text(json.dumps(report))
        check=preflight(output,'geometry-test-not-a-run')
        self.assertFalse(check['launchEligible'])
        self.assertIn('unsupported_crop_manifest',check['blockers'])
        with self.assertRaisesRegex(ValueError,'unsupported_crop_manifest'):
            prepare_protocol(report,output,None)

    def test_rehashed_wrong_crop_still_fails_production_parity(self):
        from PIL import Image
        manifest=self.source(geometry()); output=self.root/'diagnostics'
        report=derive(manifest,sha(manifest),output,ROLE)
        crop=output/report['records'][0]['crop']['path']
        Image.new('RGB',(256,256),'black').save(crop)
        report['records'][0]['crop']['sha256']=sha(crop)
        with self.assertRaisesRegex(ValueError,'geometry_crop_parity_mismatch'):
            validate_report(report,output)

    def test_geometry_tolerance_matches_producer_and_unavailable_reasons(self):
        for reason in ('not_rendered','clipped','projection_failed'):
            value={'version':1,'source':ROLE,'presentation_bounds_status':STATUS,
                   'unavailable_reason':reason, 'pixel_bounds':None, 'normalized_bounds':None}
            change_geometry(self.meta,value); self.write(self.meta)
            self.assertEqual(validate_bundle(self.bundle)['acceptedRowCount'],1)
        for delta, valid in ((1,True),(1.01,False)):
            value=geometry(); value['pixel_bounds'][0]+=delta
            change_geometry(self.meta,value); self.write(self.meta)
            if valid: validate_bundle(self.bundle)
            else:
                with self.assertRaisesRegex(ValueError,'coordinate_conflict'): validate_bundle(self.bundle)

    def test_crop_failure_is_accounted_and_output_not_accepted(self):
        manifest=self.source(geometry()); output=self.root/'failed'
        with patch('focus_geometry_diagnostic.invoke',side_effect=ValueError('test-runtime-failed')):
            with self.assertRaisesRegex(ValueError,'geometry_diagnostic_failed'):
                derive(manifest,sha(manifest),output,ROLE)
        report=json.loads((output/'geometry-diagnostic.json').read_text())
        self.assertEqual(report['counts']['failed'],2)
        with self.assertRaises(ValueError): validate_report(report,output)


if __name__ == '__main__': unittest.main()
