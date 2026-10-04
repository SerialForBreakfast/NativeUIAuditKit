import copy
import json
import subprocess
import sys
import unittest
from PIL import Image
from test_focus_corrected_transition_audit import CorrectedEndpointTests
import focus_corrected_transition_audit as audit
import human_annotation_review as h
from diagnose_transfer62 import transform


class TransformTests(unittest.TestCase):
    def test_retired_publishers_never_write(self):
        from unittest.mock import patch
        import update_nuiak_status
        import sync_shared_status
        with patch('pathlib.Path.write_text',side_effect=AssertionError('unexpected write')):
            for module in (update_nuiak_status,sync_shared_status):
                with self.assertRaisesRegex(SystemExit,'No files were written'):module.main()

    def test_reverse_shift_rejection_and_immutability(self):
        images=[Image.new('RGB',(100,100),'red'),Image.new('RGB',(100,100),'blue')]
        boxes=[[10,10,20,20],[50,50,20,20]]
        pair,truth=transform(images,boxes,'reverse')
        self.assertEqual(truth,boxes[::-1]);self.assertEqual(pair[0].getpixel((0,0)),(0,0,255))
        pair,truth=transform(images,boxes,'right')
        self.assertEqual(truth[0],[14,10,20,20]);self.assertEqual(pair[0].getpixel((0,0)),(0,0,0))
        self.assertEqual(boxes[0],[10,10,20,20])
        self.assertEqual(transform(images,[[0,0,5,5]]*2,'left'),(None,None))
        with self.assertRaises(ValueError):transform(images,boxes,'invented')


class StationaryTests(CorrectedEndpointTests):
    def fixture(self):
        from test_fixture_semantic_inventory import inventory
        before=self.record();after=copy.deepcopy(before)
        after.update(role='after',image='after.png');after['receipt']['sequence']=3
        after['capture_endpoint'].update(before_scene_received_host_ns=5,frame_received_host_ns=6,after_scene_received_host_ns=7)
        for e in (before,after):
            for k in ('before_scene','after_scene'):
                s=e['capture_endpoint'][k];s['fixture_run_id']='run'
                s['semantic_inventory']=inventory(s)
                for item in s['semantic_inventory']['elements']:
                    item.update(scroll_container_id='list',scroll_offset_points=[0,0])
        recipe=before['capture_endpoint']['after_scene']['recipe']
        case=dict(case_id='test',recipe=recipe,independence_group='fixture_procedural_renderer_v1',
            transition=dict(condition='boundary_noop',initial_focus='e',expected_focus='e',version=1))
        raw=dict(version=1,case_id='test',specification=case['transition'],recipe_hash=recipe['recipe_hash'],
            ancestry_exclusion=case['independence_group'],evidence_kind='controlled_transition_not_direct_focus_pair',
            endpoints=[before,after],run_id='run',simulator_id='sim',cleanup='verified',
            action_receipt={**before['receipt'],'sequence':2})
        return case,raw

    def persist(self,case,raw):
        for e in raw['endpoints']:
            (self.root/e['image']).write_bytes((self.root/'frame.png').read_bytes())
            (self.root/(e['role']+'.json')).write_text(json.dumps(e))
        (self.root/'case.json').write_text(json.dumps(case))
        evidence=self.root/'transition-case.json';evidence.write_text(json.dumps(raw));return evidence

    def test_cli_and_legacy_isolation(self):
        case,raw=self.fixture();evidence=self.persist(case,raw)
        self.assertEqual(audit.validate_case(self.root,evidence,case,stationary=True)[1]['focus'],'e')
        with self.assertRaisesRegex(ValueError,'case_condition'):audit.validate_case(self.root,evidence,case)
        cmd=[sys.executable,str(h.ROOT/'scripts/intake_stationary_transition.py'),'--root',str(self.root),
             '--case','case.json','--evidence','transition-case.json','--output',str(self.root/'result.json')]
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertFalse(h.read(self.root/'result.json')['trainingEligible'])
        self.assertNotEqual(subprocess.run(cmd,capture_output=True,timeout=30).returncode,0)

    def test_negative_evidence(self):
        for mutation in (
            lambda d:d.update(cleanup='partial'),
            lambda d:d.update(mutation_receipt={}),
            lambda d:d['action_receipt'].update(sequence=3),
            lambda d:d['endpoints'][1]['capture_endpoint'].update(frame_png_sha256='0'*64),
            lambda d:d['endpoints'][0]['capture_endpoint']['before_scene'].update(fixture_run_id='other'),
            lambda d:d['endpoints'][1]['capture_endpoint']['after_scene']['focus_observation'].update(verified=False),
            lambda d:d['endpoints'][0]['capture_endpoint']['before_scene']['semantic_inventory']['elements'][0].pop('scroll_offset_points'),
            lambda d:d['endpoints'][1]['capture_endpoint']['after_scene']['semantic_inventory']['elements'][0].update(scroll_offset_points=[0,3]),
            lambda d:d['specification'].update(condition='interior_switch'),
        ):
            case,raw=self.fixture();mutation(raw);case['transition']=copy.deepcopy(raw['specification'])
            evidence=self.persist(case,raw)
            with self.assertRaises(ValueError):audit.validate_case(self.root,evidence,case,stationary=True)

    def test_interior_switch(self):
        case,raw=self.fixture()
        # Two observed endpoints with distinct native owners; never requested-only truth.
        after=raw['endpoints'][1]
        for key in ('before_scene','after_scene'):
            scene=after['capture_endpoint'][key]
            after['capture_endpoint'][key]=json.loads(json.dumps(scene).replace('"e"','"f"'))
        from test_fixture_semantic_inventory import inventory
        for e in raw['endpoints']:
            for key in ('before_scene','after_scene'):
                scene=e['capture_endpoint'][key];owner=scene['focused_element_id']
                other='f' if owner=='e' else 'e'
                extra=json.loads(json.dumps(scene['elements'][0]).replace('"'+owner+'"','"'+other+'"'))
                extra['is_focused']=False;scene['elements'].append(extra)
                scene['focus_observation']['plannedFocusIDs']=['e','f']
                scene['observation_diagnostics'].update(requiredIDs=['e','f'],measuredIDs=['e','f'])
                scene['semantic_inventory']=inventory(scene)
                for item in scene['semantic_inventory']['elements']:
                    item.update(scroll_container_id='list',scroll_offset_points=[0,0])
        case['transition'].update(condition='interior_switch',expected_focus='f')
        raw['specification']=copy.deepcopy(case['transition'])
        evidence=self.persist(case,raw)
        self.assertEqual(audit.validate_case(self.root,evidence,case,stationary=True)[2]['focus'],'f')
        # Current producer wire name is accepted without changing its original bytes.
        case['transition']['condition']='focus_moved';raw['specification']=copy.deepcopy(case['transition'])
        evidence=self.persist(case,raw);original=evidence.read_bytes()
        self.assertEqual(audit.validate_case(self.root,evidence,case,stationary=True)[2]['focus'],'f')
        self.assertEqual(evidence.read_bytes(),original)

    def test_producer_boundary_wire_and_scroll_rejection(self):
        from intake_stationary_transition import run
        case,raw=self.fixture();case['transition']['condition']='boundary_unchanged'
        raw['specification']=copy.deepcopy(case['transition']);evidence=self.persist(case,raw)
        report=run(self.root,'case.json',evidence.name,self.root/'wire-intake.json')
        self.assertEqual(report['condition'],'boundary_unchanged')
        self.assertEqual(report['normalizedCondition'],'boundary_noop')
        raw['endpoints'][1]['capture_endpoint']['after_scene']['semantic_inventory']['elements'][0]['scroll_offset_points']=[0,3]
        evidence=self.persist(case,raw)
        with self.assertRaises(ValueError):audit.validate_case(self.root,evidence,case,stationary=True)


if __name__=='__main__':unittest.main()
