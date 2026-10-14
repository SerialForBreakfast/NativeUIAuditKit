import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import human_recording_audit as a


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.summary=dict(schema=1,session='session',source_manifest_sha256='a'*64,frames=2,unique_images=1,
            commands=2,commands_with_result=1,commands_without_result=1,
            frame_roles={'standalone':1,'postInputSettled':1},gap_reasons={'No fresh pre-input sample; input was not delayed.':2})
        self.cases=[dict(case_id='F001',frame_id='f1',sha256='b'*64,sequence=1,role='standalone'),
                    dict(case_id='F002',frame_id='f2',sha256='b'*64,sequence=3,role='postInputSettled')]
        self.diagram='\n'.join(['@startuml','state "F001 / standalone" as F001',
            'state "F002 / postInputSettled" as F002','state "C001 down / receipt failed" as C001',
            'C001 --> F002 : postInputSettled','state "C002 right / receipt completed" as C002',
            'C002 --> Missing1 : no retained endpoint','@enduml'])

    def run_audit(self):return a.analyze_summary(self.summary,self.cases,self.diagram)

    def test_reports_failure_without_inventing_labels(self):
        r=self.run_audit();self.assertEqual(len(r['failedCommandsWithSettledFrames']),1)
        self.assertEqual(r['duplicateImageGroups'],[['F001','F002']])
        self.assertIsNone(r['review'][0]['focusChanged']);self.assertFalse(r['trainingEligible'])
        pair=r['proposedVisualPairReview'][0]
        self.assertFalse(pair['actionLinked']);self.assertTrue(pair['repeatedImageHash'])
        self.assertIsNone(pair['focusChanged'])

    def test_count_conflict(self):
        self.summary['commands_with_result']=2
        with self.assertRaisesRegex(ValueError,'result_count'):self.run_audit()

    def test_duplicate_frame(self):
        self.cases[1]['frame_id']='f1'
        with self.assertRaisesRegex(ValueError,'duplicate_frame'):self.run_audit()

    def test_changed_role(self):
        self.diagram=self.diagram.replace('C001 --> F002 : postInputSettled','C001 --> F002 : postInputUnverified')
        with self.assertRaisesRegex(ValueError,'endpoint_role'):self.run_audit()

    def test_unsafe_diagram(self):
        self.diagram+='\n!include https://example.invalid/payload'
        with self.assertRaisesRegex(ValueError,'unsafe_diagram'):self.run_audit()

    def test_missing_command(self):
        self.diagram=self.diagram.replace('C002 --> Missing1 : no retained endpoint','')
        with self.assertRaisesRegex(ValueError,'command_count'):self.run_audit()

    def test_negative_counts_and_unknown_version(self):
        self.summary['schema']=2
        with self.assertRaisesRegex(ValueError,'unsupported_summary_schema'):self.run_audit()
        self.summary['schema']=1;self.summary['frames']=-1
        with self.assertRaisesRegex(ValueError,'invalid_summary_count'):self.run_audit()

    def test_real_cli_and_changed_file(self):
        with tempfile.TemporaryDirectory(dir=a.h.ROOT/'.build') as root:
            folder=Path(root);files=[]
            for suffix,value in [('evaluation-summary.json',json.dumps(self.summary)),
                                 ('case-index.json',json.dumps(self.cases)),('observed-navigation.puml',self.diagram)]:
                name='test-'+suffix;raw=value.encode();(folder/name).write_bytes(raw)
                files.append(dict(file='tvtestrig/'+name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
            offer=folder/'offer.json';offer.write_text(json.dumps(dict(version=2,files=files)))
            output=folder/'audit.json'
            result=subprocess.run([sys.executable,str(a.h.ROOT/'scripts/human_recording_audit.py'),
                str(offer),str(output),'--sanitized-summary'],capture_output=True,text=True,timeout=10,
                env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(output.read_text())['counts']['commands'],2)
            (folder/'test-case-index.json').write_text('[]')
            with self.assertRaisesRegex(ValueError,'size_or_type'):
                a.run_summary(offer,folder/'changed.json')


if __name__=='__main__':unittest.main()
