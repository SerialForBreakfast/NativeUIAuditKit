import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from PIL import Image
import intake_shadow111 as c


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR',Path(__file__).resolve().parents[1]/'.build'))
        self.root=Path(self.tmp.name);self.addCleanup(self.tmp.cleanup)
        rows=[]
        for n in (1,2):
            p=self.root/f'{n}.png';Image.new('RGB',(4,4),(n*20,0,0)).save(p)
            rows.append(dict(sequence=n,operation_id='op',clock_domain='runner_monotonic',native_bracket_agrees=True,
                pixel_stable=True,capture_started_monotonic_ns=n*10,capture_completed_monotonic_ns=n*10+1,
                image=p.name,image_sha256=c.sha(p),image_width=4,image_height=4,
                native_evidence=dict(screenID='Settings>General>Region',focusedRowLabel=str(n))))
        t=dict(from_sequence=1,to_sequence=2,single_input_association=True,pixel_stable=True,
            input=[dict(clock_domain='runner_monotonic',input_index=1,invoked_monotonic_ns=12,returned_monotonic_ns=13)],
            endpoints=[r['native_evidence'] for r in rows],focus_changed=True)
        self.survey=dict(schema_version=1,records=rows,transitions=[t])
        self.peer=dict(modelID='focus-transition-experimental-dtm025-change-v1',failed=0,results=[dict(
            id='op:1:2',actionID='op:1',beforeObservationID='op:1',afterObservationID='op:2',
            beforeSHA256=rows[0]['image_sha256'],afterSHA256=rows[1]['image_sha256'])])
        (self.root/'feedback/transition').mkdir(parents=True)

    def freeze(self):
        (self.root/'survey.json').write_text(json.dumps(self.survey))
        (self.root/'feedback/transition/predictions.json').write_text(json.dumps(self.peer))
        files=[dict(path=p.relative_to(self.root).as_posix(),bytes=p.stat().st_size,sha256=c.sha(p))
            for p in self.root.rglob('*') if p.is_file() and p.name!='manifest.json']
        m=dict(schema_version=1,operation_id='op',role='diagnostic_unassigned',training_admission=False,
               split_group='tvos-settings-native-layout-family',frames=2,intervals=1,files=files)
        (self.root/'manifest.json').write_text(json.dumps(m))

    def test_success_does_not_admit(self):
        self.freeze();request,report=c.audit(self.root)
        self.assertEqual(len(request['pairs']),1);self.assertFalse(report['training_admitted'])

    def test_changed_bytes_and_extra_file(self):
        self.freeze();(self.root/'1.png').write_bytes(b'bad')
        with self.assertRaisesRegex(ValueError,'member_integrity'):c.audit(self.root)

    def test_unknown_extra_member(self):
        self.freeze();(self.root/'extra').write_text('not listed')
        with self.assertRaisesRegex(ValueError,'unlisted'):c.audit(self.root)

    def test_action_after_capture(self):
        self.survey['transitions'][0]['input'][0]['returned_monotonic_ns']=22;self.freeze()
        with self.assertRaisesRegex(ValueError,'action_clock'):c.audit(self.root)

    def test_false_relation(self):
        self.survey['transitions'][0]['focus_changed']=False;self.freeze()
        with self.assertRaisesRegex(ValueError,'native_relation'):c.audit(self.root)

    def test_peer_wrong_frame(self):
        self.peer['results'][0]['beforeSHA256']='0'*64;self.freeze()
        with self.assertRaisesRegex(ValueError,'peer_image_binding'):c.audit(self.root)

    def test_unsafe_member(self):
        for name in ('../escape','/absolute','a\\b'):
            with self.assertRaises(ValueError):c.member(self.root,name)

    def test_missing_endpoint(self):
        self.survey['transitions'][0]['endpoints'].pop();self.freeze()
        with self.assertRaisesRegex(ValueError,'action_membership'):c.audit(self.root)


if __name__=='__main__':unittest.main()
