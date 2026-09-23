import copy
import unittest
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from focus_appearance_proposal import components, balanced_weights
from focus_dataset_contract import ROOT, FocusDataError


def sample(i,source='native',split='train',group=None,label=0,scene='one'):
    return {'id':str(i),'sourceID':source,'pairID':str(i),'sourceKind':source,
            'split':split,'relatedGroup':group or str(i),'intrinsicGroup':str(i),
            'recipeSeed':None,'label':label,'scene':scene,'style':'dark','control':'button',
            'crop':{'pixelSHA256':'crop'+str(i)},'frame':{'pixelSHA256':'frame'+str(i)},
            'proposedRole':'train-candidate' if split=='train' else 'retention-validation'}


class ProposalTests(unittest.TestCase):
    def test_actual_cli_rejects_changed_inputs_and_output_collision(self):
        scratch=ROOT/'.build/debug-output/appearance-proposal-tests'; scratch.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as tmp:
            root=Path(tmp); raw=root/'input.json'; raw.write_text(json.dumps({'protocolSHA256':'wrong'}))
            out=root/'result.json'
            args=[sys.executable,str(ROOT/'scripts/focus_appearance_proposal.py'),
                  '--previous',str(raw.relative_to(ROOT)),'--appearance',str(raw.relative_to(ROOT)),
                  '--comparison-protocol',str(raw.relative_to(ROOT)),'--output',str(out.relative_to(ROOT))]
            result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,2); self.assertIn('changed_previous_protocol',result.stderr)
            self.assertFalse(out.exists())
            out.write_text('preserve')
            result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,2); self.assertIn('output_collision',result.stderr)
            self.assertEqual(out.read_text(),'preserve')

    def test_transitive_pixels_and_lineage_preserve_protected_roles(self):
        a=sample(1,group='journey'); b=sample(2,group='journey')
        c=sample(3,source='fixture',split='development'); c['crop']=copy.deepcopy(b['crop'])
        groups=components([a,b,c])['components']
        self.assertEqual(len(groups),1); self.assertFalse(groups[0]['crossPartitionConflict'])
        c['split']='validation'
        self.assertTrue(components([a,b,c])['components'][0]['crossPartitionConflict'])
        self.assertEqual(components([c,b,a]),components([a,b,c]))

    def test_labels_duplicates_and_seed_groups(self):
        a=sample(1); b=sample(2,label=1); b['crop']=a['crop']
        with self.assertRaisesRegex(FocusDataError,'contradictory_crop'): components([a,b])
        with self.assertRaisesRegex(FocusDataError,'duplicate_sample'): components([a,a])
        b=sample(2); a['recipeSeed']=b['recipeSeed']=7
        self.assertEqual(len(components([a,b])['components']),1)

    def test_hierarchical_mass_ignores_validation_and_strata_count(self):
        rows=[sample(1,label=0),sample(2,label=1)]
        for i in range(3,15): rows.append(sample(i,source='fixture',label=i%2,scene=str((i-3)//2)))
        rows.append(sample(15,split='validation'))
        report=balanced_weights(rows)
        self.assertAlmostEqual(report['sourceMass']['native'],.5)
        self.assertAlmostEqual(report['sourceMass']['fixture'],.5)
        self.assertNotIn('15',report['probabilities'])
        self.assertEqual(report,balanced_weights(list(reversed(rows))))
        with self.assertRaisesRegex(FocusDataError,'missing_label_support'): balanced_weights([sample(1)])

if __name__=='__main__': unittest.main()
