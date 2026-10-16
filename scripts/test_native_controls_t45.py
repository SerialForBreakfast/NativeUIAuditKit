"""T45: native button, row, and tab recipe version. Offline; no Fixture or Simulator."""
import copy
import unittest
import native343
import native_coverage402 as coverage


def plan(*families):
    cases=[coverage.controls_case(f,f't45-{f}-case-0',f't45-{f}-group-0',745000+i) for i,f in enumerate(families)]
    return dict(version=coverage.CONTROLS_VERSION,
        binding=dict(simulatorUDID=native343.TARGET,endpoint='http://127.0.0.1:8080'),
        role='study-pending',trainingEligible=False,profiles=['standard','hcf'],repeats=1,
        expectedFrames=2*sum(len(c['targets']) for c in cases),captureBudgetBytes=100_000_000,
        qualification=dict(complete=True,restoration='verified'),cases=cases)


def body(bounds, availability='measured', reason=None):
    if availability!='measured':
        return dict(availability='unavailable',unavailable_reason=reason)
    return dict(availability='measured',visible_pixel_bounds=bounds)


def frame(case, focus, value):
    scene=dict(elements=[dict(element_id=focus,is_focused=True,rendered_body_geometry=value)])
    return dict(case=case,focus=focus,before=dict(scene=scene),after=dict(scene=copy.deepcopy(scene)))


class ControlRecipeTests(unittest.TestCase):
    def test_each_family_is_admitted(self):
        for family in coverage.CONTROL_FAMILIES:
            value=plan(family);coverage.validate_controls(value)
            self.assertEqual(value['expectedFrames'],8)
        coverage.validate_controls(plan('button','row','tab'))

    def test_old_version_is_unchanged(self):
        value=plan('button');value['version']='native-hcf402-v1'
        with self.assertRaisesRegex(ValueError,'coverage_cases|authored_focus|focused_recipe|native'):
            coverage.validate(value)
        with self.assertRaisesRegex(ValueError,'controls_version'):
            coverage.validate_controls(dict(plan('button'),version='native-hcf402-v1'))

    def test_capture_dispatch_uses_new_version(self):
        import hcf_capture362
        hcf_capture362.validate_plan(plan('row'))
        bad=plan('row');bad['trainingEligible']=True
        with self.assertRaisesRegex(ValueError,'controls_role'):hcf_capture362.validate_plan(bad)

    def assertRejects(self, reason, change, families=('button',)):
        value=plan(*families);change(value)
        with self.assertRaisesRegex(ValueError,reason):coverage.validate_controls(value)

    def test_rejections(self):
        comp=lambda v:v['cases'][0]['recipe']['appearance']['composition']
        self.assertRejects('controls_focus|composition_button_focus',
            lambda v:comp(v)['styles']['control']['focus'].update(kind='native_image'))
        self.assertRejects('controls_role',lambda v:v.update(role='train'))
        self.assertRejects('controls_identity',lambda v:v['cases'][0].update(role='train'))
        self.assertRejects('controls_family',lambda v:v['cases'][0].update(family='poster'))
        self.assertRejects('controls_kinds',lambda v:v['cases'][0].update(family='row'))
        self.assertRejects('requested_geometry_forbidden',lambda v:v['cases'][0].update(bounds=[[0,0,1,1]]))
        self.assertRejects('controls_condition',lambda v:v['cases'][0].update(condition='no-focus'))
        self.assertRejects('controls_targets',lambda v:v['cases'][0].update(targets=['item-0','item-1','item-2','item-9']))
        self.assertRejects('controls_targets',lambda v:v['cases'][0].update(targets=['item-0']*4))
        self.assertRejects('controls_frames',lambda v:v.update(expectedFrames=10))
        self.assertRejects('controls_budget',lambda v:v.update(captureBudgetBytes=200_000_000))
        self.assertRejects('composition_selected',
            lambda v:comp(v)['regions'][0]['items'][0].update(selected=True))
        # Attempt t45 qualify-r1: the Fixture returned HTTP 400 for a settings_list composition.
        self.assertRejects('controls_archetype',
            lambda v:v['cases'][0]['recipe'].update(archetype='settings_list'))
        self.assertRejects('composition_recipe',
            lambda v:v['cases'][0]['recipe'].update(element_count=5))

    def test_group_keeps_one_family(self):
        def shared(v):
            v['cases'][1]['group']=v['cases'][0]['group']
        self.assertRejects('controls_group_ancestry',shared,('button','row'))

    def test_selected_tab_is_allowed(self):
        value=plan('tab')
        value['cases'][0]['recipe']['appearance']['composition']['regions'][0]['items'][1]['selected']=True
        coverage.validate_controls(value)


class MeasuredBodyTests(unittest.TestCase):
    def doc(self, value):
        frames=[frame('t45-button-case-0','item-0',value),frame('t45-button-case-0','item-1',body([10,10,560,140]))]
        return dict(version=coverage.CONTROLS_VERSION,complete=True,cleanup=True,frames=frames)

    def test_measured_aspect_by_family(self):
        summary=coverage.measured_bodies(self.doc(body([0,0,533,142])),plan('button'))
        self.assertEqual(summary['families']['button']['frames'],2)
        self.assertEqual(summary['families']['button']['minimumAspect'],3.754)
        self.assertFalse(summary['trainingEligible'])

    def test_unavailable_geometry_stays_a_failure(self):
        for reason in ('non_affine_transform','unsupported_native_control'):
            with self.assertRaisesRegex(ValueError,'unmeasured_body:'+reason):
                coverage.measured_bodies(self.doc(body(None,'unavailable',reason)),plan('button'))

    def test_moving_body_fails(self):
        doc=self.doc(body([0,0,533,142]))
        doc['frames'][0]['after']['scene']['elements'][0]['rendered_body_geometry']=body([0,0,540,142])
        with self.assertRaisesRegex(ValueError,'body_changed_during_capture'):
            coverage.measured_bodies(doc,plan('button'))


class CapturePlanTests(unittest.TestCase):
    def test_plan_carries_capture_contract(self):
        import backlog_pipeline as pipeline
        recipe=lambda f:dict(recipe=dict(file='reports/work/T45/'+f+'.json'))
        record=dict(id='B405-042',hypothesis='Native effect visibility differs by control family.',
            comparison='Standard versus HCF by family.',plan=dict(template='T03',owner='research-host-NUIAK',
            jobPrefix='t45-effect',rule='manual',control='button',
            question='Do native button, row, and tab bodies show a visible Standard and HCF focus effect?',
            decision='Restrict effect labels to families with observed visible evidence.',
            outcomes=dict(supported='Restrict labels.',contradicted='Keep labels.',inconclusive='Qualify more.'),
            shared=dict(capture=dict(plan=dict(input='recipe'),endpoint='http://127.0.0.1:8080',
                                     target=native343.TARGET,approval='test')),
            arms=[dict(id='button',inputs=recipe('button')),dict(id='row',inputs=recipe('row'))]))
        docs=pipeline.descriptions(record)
        self.assertEqual([d['id'] for d in docs],['t45-effect-button','t45-effect-row'])
        self.assertTrue(all(d['capture']['plan']=={'input':'recipe'} for d in docs))


if __name__=='__main__':unittest.main()
