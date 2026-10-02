import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import corpus_lifecycle as c


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        parent=c.ROOT/'.build/debug-output/lifecycle-tests';parent.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=parent);self.root=Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.rows=[]
        for ident,split,kind in [('train','train','synthetic'),('eval','evaluation','synthetic'),
                                 ('recipe','reference','metadata'),('old','train','synthetic'),
                                 ('private','reference','real-device')]:
            p=self.root/(ident+'.txt');p.write_text(ident)
            self.rows.append(dict(id=ident,path=p.name,bytes=p.stat().st_size,sha256=c.sha256(p),
                sourceGroup=ident,split=split,sourceKind=kind,humanCorrected=False,dependencies=[],
                recreationInputs=['recipe'] if kind=='synthetic' else [],
                provenance=dict(platform='tvOS',osVersion='26.5',runtimeIdentity='build-1',
                    annotationVersion='3',generatorRevision='abc',uiFamily='row',recipeSHA256='a'*64,
                    seed=0,assetLicenseIdentity='owned')))
        self.catalog=c.seal(dict(version='corpus-lifecycle-catalog-v1',members=self.rows))
        self.policy=dict(version='corpus-lifecycle-policy-v1',supportedOS={'tvOS':['26.5']},
            dispositions=dict(train='active-training',eval='evaluation-only',recipe='historical-reference',
                              old='retired',private='retired'))

    def test_filter_preserves_roles_and_replay(self):
        m=c.select(self.catalog,self.policy,self.root)
        self.assertEqual([(r['id'],r['split']) for r in m['selected']],[('train','train'),('eval','evaluation')])
        self.assertEqual(c.replay(m,self.catalog,self.root)['members'],2)
        self.policy['supportedOS']={'tvOS':['27.0']}
        self.assertEqual(len(c.select(self.catalog,self.policy,self.root)['selected']),0)
        self.assertEqual(c.replay(m,self.catalog,self.root)['members'],2)

    def test_os_unknown_and_missing_provenance(self):
        self.rows[0]['provenance']['osVersion']='unknown'
        self.catalog=c.seal(dict(version='corpus-lifecycle-catalog-v1',members=self.rows))
        m=c.select(self.catalog,self.policy,self.root)
        reasons=next(r['reasons'] for r in m['excluded'] if r['id']=='train')
        self.assertIn('unsupported_os',reasons);self.assertIn('missing_provenance:osVersion',reasons)

    def test_no_eval_promotion(self):
        self.policy['dispositions']['eval']='active-training'
        m=c.select(self.catalog,self.policy,self.root)
        self.assertIn('cannot_promote_split',next(r['reasons'] for r in m['excluded'] if r['id']=='eval'))

    def test_group_leakage(self):
        self.rows[1]['sourceGroup']='train'
        self.catalog=c.seal(dict(version='corpus-lifecycle-catalog-v1',members=self.rows))
        with self.assertRaisesRegex(ValueError,'cross_split_source_group'):c.select(self.catalog,self.policy,self.root)

    def test_cleanup_preserves_private_and_rebuild_inputs(self):
        r=c.cleanup_report(self.catalog,self.policy,self.root)
        self.assertFalse(r['deletionAuthorized'])
        self.assertEqual([x['id'] for x in r['rows'] if x['candidate']],['old'])
        self.assertTrue((self.root/'old.txt').exists())

    def test_transitive_dependency_and_human_protection(self):
        self.rows[0]['dependencies']=['old'];self.rows[3]['humanCorrected']=True
        self.catalog=c.seal(dict(version='corpus-lifecycle-catalog-v1',members=self.rows))
        r=c.cleanup_report(self.catalog,self.policy,self.root)
        old=next(x for x in r['rows'] if x['id']=='old')
        self.assertFalse(old['candidate']);self.assertIn('retained_dependency',old['reasons'])
        self.assertIn('human_correction',old['reasons'])

    def test_hash_and_missing_file(self):
        m=c.select(self.catalog,self.policy,self.root)
        (self.root/'train.txt').write_text('changed')
        with self.assertRaisesRegex(ValueError,'changed_member'):c.replay(m,self.catalog,self.root)

    def test_historical_replay_does_not_need_retired_pixels(self):
        m=c.select(self.catalog,self.policy,self.root)
        (self.root/'old.txt').unlink()
        self.assertTrue(c.replay(m,self.catalog,self.root)['replayVerified'])

    def test_unsafe_path_and_unmounted_storage(self):
        self.rows[0]['path']='../escape';self.catalog=c.seal(dict(version='corpus-lifecycle-catalog-v1',members=self.rows))
        with self.assertRaisesRegex(ValueError,'unsafe_path'):c.select(self.catalog,self.policy,self.root)
        with patch.object(Path,'is_dir',return_value=True),patch.object(Path,'is_mount',return_value=False):
            with self.assertRaisesRegex(ValueError,'external_mount_unavailable'):
                c.root_path('/Volumes/missing/data','/Volumes/missing')

    def test_cli_and_immutable_output(self):
        catalog=self.root/'catalog.json';policy=self.root/'policy.json';out=self.root/'selection.json'
        catalog.write_text(json.dumps(self.catalog));policy.write_text(json.dumps(self.policy))
        cmd=[sys.executable,str(c.ROOT/'scripts/corpus_lifecycle.py'),'select','--catalog',str(catalog),
            '--policy',str(policy),'--root',str(self.root),'--output',str(out)]
        self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
        self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)


if __name__=='__main__':unittest.main()
