"""Generated corrected-export contracts; no retained captures required."""
import copy
import json
import unittest
from test_focus_structural_transition_audit import EndpointTests
from test_fixture_composition import recipe
from test_fixture_semantic_inventory import inventory
from harvest_sidecar_v2 import scene_check, recipe_hash
import focus_corrected_transition_audit as audit


class CorrectedEndpointTests(EndpointTests):
    def record(self):
        c=copy.deepcopy(self.capture)
        receipt=c.pop('action_capture_receipt');c['frame_png_sha256']=c.pop('sha256');c.pop('image')
        c.update(frame_width=64,frame_height=48,correlation='validated_capture_bracket')
        return dict(role='before',image='before.png',capture_endpoint=c,receipt=receipt)

    def corrected(self,r):
        (self.root/'before.png').write_bytes((self.root/'frame.png').read_bytes())
        (self.root/'before.json').write_text(json.dumps(r))
        return audit.endpoint(self.root,self.root/'transition-case.json',r,'before')

    def test_corrected_endpoint_and_failures(self):
        r=self.record();self.assertEqual(self.corrected(r)['focus'],'e')
        for mutation in [lambda d:d.update(role='after'),
                         lambda d:d['capture_endpoint'].update(frame_width=60),
                         lambda d:d['capture_endpoint'].update(frame_png_sha256='0'*64),
                         lambda d:d['capture_endpoint']['after_scene'].update(is_settled=False)]:
            bad=copy.deepcopy(r);mutation(bad)
            with self.assertRaises(ValueError):self.corrected(bad)

    def test_actual_case_binding_and_action_sequence(self):
        before=self.record();after=copy.deepcopy(before)
        after.update(role='after',image='after.png');after['receipt']['sequence']=3
        after['capture_endpoint'].update(before_scene_received_host_ns=5,frame_received_host_ns=6,after_scene_received_host_ns=7)
        for endpoint in (before,after):
            for key in ('before_scene','after_scene'):endpoint['capture_endpoint'][key]['fixture_run_id']='run'
        r=before['capture_endpoint']['after_scene']['recipe']
        case=dict(case_id='test',recipe=r,independence_group='fixture_procedural_renderer_v1',
                  transition=dict(condition='boundary_unchanged',initial_focus='e',expected_focus='e',version=1))
        d=dict(version=1,case_id='test',specification=case['transition'],recipe_hash=r['recipe_hash'],
               ancestry_exclusion=case['independence_group'],evidence_kind='controlled_transition_not_direct_focus_pair',
               endpoints=[before,after],run_id='run',simulator_id='sim',action_receipt={**before['receipt'],'sequence':2})
        for e in (before,after):
            (self.root/e['image']).write_bytes((self.root/'frame.png').read_bytes())
            (self.root/(e['role']+'.json')).write_text(json.dumps(e))
        evidence=self.root/'transition-case.json';evidence.write_text(json.dumps(d))
        self.assertEqual(audit.validate_case(self.root,evidence,case)[1]['focus'],'e')
        for mutate in [lambda d:d.update(recipe_hash='0'*64),
                       lambda d:d['action_receipt'].update(sequence=1),
                       lambda d:d['action_receipt'].update(operationID='other'),
                       lambda d:d.update(run_id='other')]:
            bad=copy.deepcopy(d);mutate(bad);evidence.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):audit.validate_case(self.root,evidence,case)


class VisibilityTests(unittest.TestCase):
    def scene(self):
        from test_ttr_sidecar_v2 import scene
        s=scene('e',4);r=recipe();r['element_count']=2
        r['appearance']['composition']['regions'][0]['frame'][2]=300
        r['appearance']['composition']['regions'][0]['items'].append(dict(id='clipped',component='d',content='c',selected=False))
        r['recipe_hash']=recipe_hash(r);s['recipe']=r;s['elements'][0]['parent_element_id']='region'
        s['focus_observation']['plannedFocusIDs']=['e','clipped']
        d=inventory(s);d.update(coverage='incomplete_declared_composition',expected_control_ids=['e','clipped'],
            visible_control_ids=['e'],exclusions={'clipped':'partially_clipped_bounds'},
            control_exclusions={'clipped':'partially_clipped_bounds'})
        e=copy.deepcopy(d['elements'][0]);e.update(id='clipped',input_focused=False,clipping='partially_clipped',
            full_pixel_bounds=[60,8,28,20],visible_pixel_bounds=[60,8,4,20],visible_normalized_bounds=[60/64,8/48,1,28/48])
        d['elements'].append(e);s['semantic_inventory']=d
        return s

    def test_explicit_opt_in_preserves_exclusions(self):
        s=self.scene();original=copy.deepcopy(s)
        self.assertEqual(scene_check(s,(64,48),'e',transition_visibility=True),4)
        self.assertEqual(s,original)
        with self.assertRaisesRegex(ValueError,'planned_focus'):scene_check(s,(64,48),'e')

    def test_visibility_cannot_hide_contract_failures(self):
        for mutate in [lambda s:s['semantic_inventory'].update(visible_control_ids=['e','clipped']),
                       lambda s:s['semantic_inventory']['control_exclusions'].update(clipped='hidden'),
                       lambda s:s['semantic_inventory']['elements'][1].pop('clipping'),
                       lambda s:s['semantic_inventory']['elements'].append(copy.deepcopy(s['semantic_inventory']['elements'][0])),
                       lambda s:s.update(is_settled=False),
                       lambda s:s['focus_observation'].update(verified=False),
                       lambda s:s['semantic_inventory'].update(expected_control_ids=['e','clipped','invented'])]:
            s=self.scene();mutate(s)
            with self.assertRaises(ValueError):scene_check(s,(64,48),'e',transition_visibility=True)


if __name__=='__main__':unittest.main()
