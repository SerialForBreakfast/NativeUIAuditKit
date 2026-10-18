"""Native profile duplication does not permit label conflicts or split leaks."""
import copy
import unittest
from pathlib import Path
import tempfile
from unittest.mock import patch
import native_control_admission as n
import research_queue as q


def row(ident='a', role='train', group='g', pixels='pixels', focus='item-0'):
    return dict(id=ident, role=role, group=group, decodedSHA256=pixels,
                focus=focus, boxes={'item-0':[0,0,10,10]}, profile='standard')


class PartitionTests(unittest.TestCase):
    def test_empty_fails(self):
        with self.assertRaisesRegex(ValueError,'native_empty_membership'):
            n.validate_partition([])
    def test_identical_profile_pixels(self):
        a=row(); b=dict(a,id='b',profile='hcf')
        self.assertEqual(n.validate_partition([a,b])['uniqueFrames'],1)

    def test_separate_groups(self):
        value=n.validate_partition([row(),row('b','development','other','different')])
        self.assertEqual(value['groups'],dict(train=1,development=1))

    def test_conflicts(self):
        cases=[(row('b','development'), 'native_group_leak'),
               (row('b','development','other'), 'native_pixel_leak'),
               (row('b',focus='item-1'), 'native_pixel_label_conflict'),
               (row(), 'native_duplicate_id'),
               (row('b','audit'), 'native_role_invalid')]
        for b,reason in cases:
            with self.subTest(reason=reason),self.assertRaisesRegex(ValueError,reason):
                n.validate_partition([row(),b])

    def test_geometry_conflict(self):
        b=row('b');b['boxes']['item-0'][2]=11
        with self.assertRaisesRegex(ValueError,'native_pixel_label_conflict'):
            n.validate_partition([row(),b])

    def test_layout_leak(self):
        a=dict(row(),layoutSHA256='same-layout')
        b=dict(row('b','development','other','different'),layoutSHA256='same-layout')
        with self.assertRaisesRegex(ValueError,'native_layout_leak'):n.validate_partition([a,b])

    def test_content_does_not_change_layout_identity(self):
        import native_coverage402 as coverage
        a=coverage.controls_case('button','a','g',1)
        b=coverage.controls_case('button','b','h',2)
        self.assertEqual(n.layout_identity(a),n.layout_identity(b))


class RetainedAdmissionTests(unittest.TestCase):
    """Use verified retained captures; do not operate a device or train a model."""
    def setUp(self):
        self.path=q.QUEUE/'jobs/b405-042-button/attempts/1/out/artifact.json'
        if not self.path.exists():self.skipTest('Retained native source unavailable')
        self.artifact=q.load(self.path)
        self.roles={c['group']:'train' for c in self.artifact['plan']['cases']}
        self.root=Path(self.artifact['storage']['root'])

    def test_actual_source(self):
        rows=n.admit_artifact(self.artifact,self.roles,self.root,'b405-042-button')
        self.assertEqual(len(rows),8)
        self.assertEqual(n.validate_partition(rows)['groups']['train'],1)

    def test_capture_failures(self):
        original=q.load(Path(self.artifact['path']))
        changes=[('native_capture_incomplete',lambda d:d.update(cleanup=False)),
                 ('native_frame_membership',lambda d:d['frames'].append(d['frames'][0])),
                 ('native_recipe_changed',lambda d:d['frames'][0]['before']['scene']['recipe'].update(seed=1)),
                 ('native_capture_interval',lambda d:d['frames'][0].update(start=0)),
                 ('native_image_changed',lambda d:d['frames'][0].update(sha256='0'*64))]
        for reason,change in changes:
            value=copy.deepcopy(original);change(value)
            with self.subTest(reason=reason),patch.object(q,'load',return_value=value):
                with self.assertRaisesRegex(ValueError,reason):
                    n.admit_artifact(self.artifact,self.roles,self.root,'source')

    def test_isolated_queue_and_second_description(self):
        import hcf_templates395 as templates
        import research_approval as approval
        from experiment_templates import pin
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='native-admission-') as directory:
            root=Path(directory);queue=root/'queue'
            config=dict(version=n.VERSION,sources=[dict(id='b405-042-button',artifact=pin(self.path),roles=self.roles)])
            q.save(root/'config.json',config)
            decision=q.ROOT/'reports/work/NATIVE-CONTROLS-20261017/role-decision.json'
            doc=dict(version='hcf-template-description-v1',id='native-admission-first',owner='test-NUIAK',template='T53',
                     question='Can verified native captures pass the role overlay?',decision='Require exact rows and source checks.',
                     inputs=dict(configuration=pin(root/'config.json'),decision=pin(decision)),parameters={},dependencies=[])
            for ident in ['native-admission-first','native-admission-second']:
                doc=dict(doc,id=ident);templates.register(doc,queue);templates.register(doc,queue)
                approval.approve(queue,ident,'test','Isolated admission qualification using approved retained inputs.')
                self.assertEqual(q.run(queue,max_jobs=1,lock=root/'lock',job_ids=[ident]),[(ident,'complete')])
                actual=q.load(queue/'jobs'/ident/'attempts/1/out/admission.json')['rows']
                expected=n.admit_artifact(self.artifact,self.roles,self.root,'b405-042-button')
                self.assertEqual(actual,expected)


if __name__=='__main__':unittest.main()
