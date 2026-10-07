"""Check the bounded schema 4 adapter without native capture or training."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from focus_dataset_contract import ROOT, digest
from focus_learning_experiment import load_protocol
from harvest_schema4_review import REPAIR_CONFIG, RETENTION_CONFIG, RETENTION_VERSION


class RepairTests(unittest.TestCase):
    def test_replay_role_and_protected_pixels(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.build/debug-output') as tmp:
            path=Path(tmp)/'protocol.json';admission=Path(tmp)/'admission.json';manifest=Path(tmp)/'manifest.json'
            rows=[dict(id=f'{role}-{label}',root=f'fake/{role}',metadata='meta.json',metadataSHA256='meta',
                bounds=[1,2,3,4],label=label,role=role,group=role,
                crop=dict(path=f'{role}-{label}.png',sha256='crop')) for role in ('train','reserved') for label in (0,1)]
            replay=[dict(id=f'replay-{label}',pairID='old',label=label,crop=dict(path=f'dataset/focus_ring/{label}.png',sha256='crop')) for label in (0,1)]
            source=dict(pairs=[dict(pair_id='old',split='train',unfocused_crop='0.png',focused_crop='1.png'),
                dict(pair_id='test',split='test',unfocused_crop='test0.png',focused_crop='test1.png')])
            doc=dict(version=RETENTION_VERSION,configuration=RETENTION_CONFIG,runtime={},warmCheckpoint={},
                admission={'kind':'admission'},replayManifest={'kind':'manifest'},releaseEligible=False,samples=rows,replay=replay)
            def execute(value,source_value):
                value['protocolSHA256']=digest({k:v for k,v in value.items() if k!='protocolSHA256'})
                path.write_text(json.dumps(value));manifest.write_text(json.dumps(source_value))
                admission.write_text(json.dumps(dict(approved=True,purpose='development-only',visualReview='test only',
                    campaign={},samplesSHA256=digest(value['samples']),replaySHA256=digest(value['replay']),legacyReplayDiagnosticOnly=True)))
                pair=dict(metadataSHA256='meta',endpoints=[dict(role=r,visibleBody=[1,2,3,4]) for r in ('unfocused','focused')])
                meta=dict(unfocused_png='u.png',focused_png='f.png',unfocused_sha256='u',focused_sha256='f')
                def checked(r):return manifest if r.get('kind')=='manifest' else admission
                with patch('focus_learning_experiment.checked',side_effect=checked),patch('focus_runtime.identity',return_value={}),\
                     patch('harvest_schema4_review.pair',return_value=pair),patch('harvest_schema4_review.read',return_value=json.dumps(meta).encode()),\
                     patch('focus_dataset_contract.image'),patch('focus_dataset_contract.pixel_digest',side_effect=lambda root,r:r['path']),\
                     patch('focus_dataset_contract.member',return_value=manifest):
                    return load_protocol(path,'schema4-repair','test-retention234')
            report,train=execute(copy.deepcopy(doc),source)
            self.assertEqual(len(train),4);self.assertEqual(report['configuration']['lr'],.00003)
            for mutate in (lambda d:d['replay'][0].update(label=2),lambda d:d['replay'][0].update(pairID='test'),
                           lambda d:d['replay'].pop(),lambda d:d['replay'].append(d['replay'][0]),
                           lambda d:d['replay'][0]['crop'].update(path='dataset/focus_ring/test0.png')):
                bad=copy.deepcopy(doc);mutate(bad)
                with self.assertRaises(ValueError):execute(bad,source)
            wrong=copy.deepcopy(source);wrong['pairs'][0]['split']='test'
            with self.assertRaises(ValueError):execute(copy.deepcopy(doc),wrong)

    def test_roles_and_input_failures(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.build/debug-output') as tmp:
            path=Path(tmp)/'protocol.json'
            rows=[dict(id=f'{role}-{label}',root=f'fake/{role}',metadata='meta.json',
                metadataSHA256='meta',bounds=[1,2,3,4],label=label,role=role,group=role,
                crop=dict(path=f'{role}-{label}.png',sha256='crop'))
                for role in ('train','reserved') for label in (0,1)]
            doc=dict(version='schema4-focus-repair-v1',configuration=REPAIR_CONFIG,
                runtime={},warmCheckpoint={},admission={},releaseEligible=False,samples=rows)
            def execute(value):
                value['protocolSHA256']=digest({k:v for k,v in value.items() if k!='protocolSHA256'})
                path.write_text(json.dumps(value))
                admission=Path(tmp)/'admission.json'
                admission.write_text(json.dumps(dict(approved=True,purpose='development-only',
                    visualReview='test fake only',samplesSHA256=digest(value['samples']),campaign={})))
                pair=dict(metadataSHA256='meta',endpoints=[dict(role=role,visibleBody=[1,2,3,4]) for role in ('unfocused','focused')])
                meta=dict(unfocused_png='u.png',focused_png='f.png',unfocused_sha256='u',focused_sha256='f')
                with patch('focus_learning_experiment.checked',return_value=admission), \
                     patch('focus_runtime.identity',return_value={}), \
                     patch('harvest_schema4_review.pair',return_value=pair), \
                     patch('harvest_schema4_review.read',return_value=json.dumps(meta).encode()), \
                     patch('focus_dataset_contract.image'), \
                     patch('focus_dataset_contract.pixel_digest',side_effect=lambda root,r:r['path']), \
                     patch('focus_dataset_contract.member',side_effect=lambda root,name:root/name):
                    return load_protocol(path,'schema4-repair','repair-offline-test')
            report,train=execute(copy.deepcopy(doc))
            self.assertEqual(len(train),2)
            self.assertTrue(report['terminalOnly'])
            self.assertTrue(all(r['split']=='train' for r in train))
            for change in (
                lambda d:d['samples'].append(d['samples'][0]),
                lambda d:d['samples'][2].update(group='train'),
                lambda d:d['samples'][0].update(label=2),
                lambda d:d['samples'][0].update(metadataSHA256='altered'),
                lambda d:d['samples'][0].update(bounds=[0,0,3,4]),
                lambda d:d['samples'].pop(),
                lambda d:d.update(configuration={}),
                lambda d:d.update(releaseEligible=True),
            ):
                bad=copy.deepcopy(doc);change(bad)
                with self.assertRaises((ValueError,KeyError,IndexError)):
                    execute(bad)


if __name__=='__main__':unittest.main()
