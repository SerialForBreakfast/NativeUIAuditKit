"""SDK producer contract tests. Generated packets are not native model evidence."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import research_queue as q
import sdk_capture527 as m
from experiment_templates import pin
from test_sdk_packet502 import sample

class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=q.ROOT/'.build');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.ttr=self.root/'TTR';self.local=self.ttr/'.local-work';self.local.mkdir(parents=True)
        self.patch=patch.object(m,'TTR',self.ttr);self.patch.start();self.addCleanup(self.patch.stop)
        helper=self.local/'App/Helpers/aatv';helper.parent.mkdir(parents=True);helper.write_text('software-test')
        enrollment=self.local/'enrollment.json';q.save(enrollment,dict(appID='example.ttr.navigation.consumer',processID='p',runID='r',secretBase64='software-test'));enrollment.chmod(0o600)
        self.config=dict(version='sdk-capture-request-v1',id='sdk-capture-test',target=m.TARGET,endpoint=m.ENDPOINT,
            helper=dict(path=str(helper),sha256=q.digest(helper)),enrollment=dict(path=str(enrollment),sha256=q.digest(enrollment)),
            output=str(self.local/'packet'),expectedAppID='example.ttr.navigation.consumer',group='software-test',sourceRevision='a'*40)
        self.path=self.root/'request.json';q.save(self.path,self.config)

    def test_versioned_contract_accepts_config_only_successors(self):
        for ident in ('sdk-capture-test','sdk-capture-other'):
            r=copy.deepcopy(self.config);r['id']=ident;p=self.root/(ident+'.json');q.save(p,r)
            s=m.build(p);q.validate(s);self.assertEqual(s['authority'],'capture')

    def test_identity_budget_and_endpoint_reject(self):
        s=m.build(self.path)
        for field,value,error in [('id','other','sdk_capture_spec_identity')]:
            bad=copy.deepcopy(s);bad[field]=value
            with self.assertRaisesRegex(ValueError,error):q.validate(bad)
        bad=copy.deepcopy(s);bad['limits']['maxOutputBytes']=100000001
        with self.assertRaisesRegex(ValueError,'sdk_capture_budget'):q.validate(bad)
        bad=copy.deepcopy(s);bad['capture']['endpoint']='http://127.0.0.1:8080'
        with self.assertRaisesRegex(ValueError,'capture_endpoint'):q.validate(bad)

    def test_world_readable_enrollment_rejects(self):
        Path(self.config['enrollment']['path']).chmod(0o644)
        with self.assertRaisesRegex(ValueError,'sdk_capture_private_enrollment'):m.validate_config(self.config)

    def test_bundled_helper_link_is_allowed_but_escape_is_rejected(self):
        helper=Path(self.config['helper']['path']);real=helper.parent.parent/'MacOS/TVTestRig'
        real.parent.mkdir();real.write_text(helper.read_text());helper.unlink();helper.symlink_to(real)
        m.validate_config(self.config)
        escaped=self.root/'outside';escaped.write_text('software-test');helper.unlink();helper.symlink_to(escaped)
        with self.assertRaisesRegex(ValueError,'sdk_capture_path'):m.validate_config(self.config)

    def test_helper_changes_reject(self):
        Path(self.config['helper']['path']).write_text('changed')
        with self.assertRaisesRegex(ValueError,'sdk_capture_source_changed'):m.validate_config(self.config)

    def test_occupied_target_does_not_capture(self):
        with patch.object(m.Client,'call',return_value=dict(can_run=True,ownership=[dict(state='occupied')])) as call:
            with self.assertRaisesRegex(ValueError,'sdk_capture_target_busy'):m.readiness(self.config,self.root)
            self.assertEqual(call.call_count,1)

    def test_readiness_and_capture_keep_separate_call_receipts(self):
        import json
        from types import SimpleNamespace
        response=SimpleNamespace(returncode=0,stdout=json.dumps(dict(success=True,data=dict(value={'_0':dict(can_run=True,ownership=[dict(state='clear')])}))),stderr='')
        with patch.object(m.subprocess,'run',return_value=response) as call:
            m.readiness(self.config,self.root)
            self.assertNotIn('--project',call.call_args.args[0])
            m.Client(self.config,self.root).call('sdk','packet')
            self.assertEqual(call.call_args.args[0][1:3],['--project',str(self.ttr)])
        self.assertTrue((self.root/'readiness-01.json').is_file())
        self.assertTrue((self.root/'call-01.json').is_file())

    def test_bounded_timeline_reply_exceeds_old_limit(self):
        import json
        from types import SimpleNamespace
        response=SimpleNamespace(returncode=0,stdout=json.dumps(dict(success=True,data=dict(value={'_0':dict(history='x'*300000)}))),stderr='')
        with patch.object(m.subprocess,'run',return_value=response):
            self.assertEqual(len(m.Client(self.config,self.root).call('sdk','snapshot')['history']),300000)

    def test_collection_preserves_unknown_profile_and_pins_bytes(self):
        spec=m.build(self.path);job=self.root/'job';out=job/'attempts/1/out';out.mkdir(parents=True);q.save(job/'spec.json',spec)
        def call(client,*args):
            if args[0]=='simulator':return dict(can_run=True,ownership=[dict(state='clear')])
            self.assertEqual(args[:2],('sdk','packet'))
            dest=Path(self.config['output']);dest.mkdir();image=dest/'frame.png';Image.new('RGB',(16,16)).save(image)
            evidence=sample(image);evidence.update(width=16,height=16,sourceID=m.TARGET)
            for side in ('before','after'):evidence[side].update(appID=self.config['expectedAppID'],processID='p',runID='r')
            q.save(dest/'evidence.json',evidence);return dict(state='collected')
        with patch.object(m,'OUT',out),patch.object(m.Client,'call',call):m.run()
        d=q.load(out/'benchmark_summary.json');self.assertFalse(d['trainingEligible']);self.assertEqual(d['profile'],'unknown')
        receipt=q.load(out/'artifact-receipt.json');self.assertIn('frame.png',[x['path'] for x in receipt['outputs']])
        self.assertEqual(q.digest(out/'frame.png'),q.digest(Path(self.config['output'])/'frame.png'))
        with patch.object(m,'OUT',out),patch.object(m.Client,'call',call):
            with self.assertRaises(ValueError):m.run()

if __name__=='__main__':unittest.main()
