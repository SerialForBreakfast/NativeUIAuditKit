"""Readiness accounting fixtures, isolated from retained human data and models."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import focus_generation_readiness as g
import human_annotation_review as h


class LedgerTests(unittest.TestCase):
    def setUp(self):
        control=dict(id='c',state='focused',bounds=[1,2,30,40],**{'class':'collectionItem'})
        frame=dict(id='f',disposition='imported',proposals=[control],duplicateOf=None,
            nativeUnresolved=False,pixelSHA256='frame',sourceRoot='root',sourcePairID='pair')
        self.batch=dict(frames=[frame]);self.crops=[dict(id='f:c',crop={},pixelSHA256='crop')]
        self.revision=dict(frames=[dict(id='f',disposition='reviewed',controls=[dict(control,disposition='reviewed')])])

    def ledger(self):return g.candidate_ledger(self.batch,self.revision,self.crops,[],set())

    def test_review_does_not_admit_or_infer_population_accuracy(self):
        rows=self.ledger();self.assertEqual(rows[0]['humanReview'],'accepted')
        self.assertFalse(rows[0]['trainingEligible'])
        self.revision['frames']=[]
        self.assertEqual(self.ledger()[0]['humanReview'],'not_individually_reviewed')

    def test_missing_duplicate_and_unknown_crop(self):
        for replacement in ([],self.crops*2,[dict(self.crops[0],id='wrong')]):
            with self.subTest(replacement=replacement),self.assertRaises(ValueError):
                g.candidate_ledger(self.batch,self.revision,replacement,[],set())

    def test_changed_review_requires_fresh_crop_qa(self):
        for key,value in [('bounds',[2,3,4,5]),('state','unfocused'),('class','primaryButton')]:
            doc=copy.deepcopy(self.revision);doc['frames'][0]['controls'][0][key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'new_crop_QA'):
                g.candidate_ledger(self.batch,doc,self.crops,[],set())

    def test_exact_overlap_and_unknowns_stay_explicit(self):
        f=self.batch['frames'][0];f.update(duplicateOf='original',nativeUnresolved=True)
        rows=g.candidate_ledger(self.batch,self.revision,self.crops,
            [dict(framePixels='other',cropPixels='crop',role='development')],set())
        self.assertEqual(rows[0]['retainedOverlapRoles'],['development'])
        for reason in ('exact_retained_pixel_overlap','incomplete_body_inventory','exact_frame_alias'):
            self.assertIn(reason,rows[0]['reasons'])

    def test_protected_and_conflicting_labels(self):
        with self.assertRaisesRegex(ValueError,'protected_candidate'):
            g.candidate_ledger(self.batch,self.revision,self.crops,[],{'crop'})
        other=copy.deepcopy(self.batch['frames'][0]);other['id']='g';other['proposals'][0]['state']='unfocused'
        self.batch['frames'].append(other);self.crops.append(dict(self.crops[0],id='g:c'))
        self.assertTrue(all('same_crop_pixels_conflicting_focus' in r['reasons'] for r in self.ledger()))

    def test_body_proof_membership_and_family_scope(self):
        self.batch['version']=g.native.BODY_VERSION
        self.batch['frames'][0]['recipe']={'appearance':{'canvas':{'presentation':'settings_rows'}}}
        report={'counts':{'accepted_for_diagnostic_QA':1},'cropQA':{}}
        qa={'batch':{},'expected':1,'completed':1,'crops':[{'id':'f:c','crop':{}}]}
        with patch.object(g.h,'sealed',side_effect=lambda p,v:report if v=='fixture-batch-QA-v1' else qa), \
             patch.object(g.h,'checked',return_value=Path('unused')), \
             patch.object(g.h,'ref',return_value={}),patch.object(g.native,'validate',return_value=self.batch):
            result=g.body_proof(Path('unused'))
            self.assertEqual(result['families'],{'rows':1});self.assertFalse(result['humanReviewed'])
            qa['crops'][0]['id']='wrong'
            with self.assertRaisesRegex(ValueError,'body_proof_crop_membership'):g.body_proof(Path('unused'))

    def test_family_uses_declared_composition(self):
        self.assertEqual(g.family({'archetype':'action_dialog'}),'buttons')
        self.assertEqual(g.family({'appearance':{'canvas':{'presentation':'nested_tabs_v1'}}}),'tabs')
        self.assertEqual(g.family({'appearance':{'canvas':{'presentation':'buttons'}}}),'buttons')
        self.assertEqual(g.family({'archetype':'grid_matrix'}),'artwork')


class LineageTests(unittest.TestCase):
    def setUp(self):
        root=h.ROOT/'.build/debug-output';root.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=root);self.root=Path(self.tmp.name)
        self.recipe=self.root/'recipe.json';self.recipe.write_text(json.dumps({'seed':1,'theme':'dark','archetype':'grid_matrix'}))
        self.entry=dict(path='recipe.json',bytes=self.recipe.stat().st_size,sha256=h.sha(self.recipe),
            current_syn04=True,layout_signature='layout',content={'tokens':['motif:1']},split='unreserved',independence='unreviewed')
        self.doc=dict(version=1,purpose='source_overlap_review_not_split_assignment',recipes=[self.entry],
            related_to_current={'recipe.json':[]},policy={},summary=dict(recipe_files=1,current_recipes=1,current_layout_signatures=1,reservations=0))
        self.path=self.root/'lineage.json'

    def tearDown(self):self.tmp.cleanup()

    def run_review(self,samples=()):
        self.path.write_text(json.dumps(self.doc));return g.lineage_review(self.path,self.root,samples)

    def test_exact_match_and_unknown_ancestry(self):
        recipe=json.loads(self.recipe.read_text());recipe['step_index']=3
        result=self.run_review([dict(id='retained',sourceID='s',use='validation',recipe=recipe)])
        self.assertEqual(result['retainedRecipeMatches'],1)
        self.assertIsNone(result['recipes'][0]['reservedRole'])
        recipe['seed']=2
        self.assertEqual(self.run_review([dict(id='retained',use='validation',recipe=recipe)])['retainedRecipeMatches'],0)

    def test_changed_bytes_duplicate_missing_edges_and_roles(self):
        original=copy.deepcopy(self.doc)
        for edit in (lambda d:d['recipes'].append(copy.deepcopy(self.entry)),
                     lambda d:d['recipes'][0].update(sha256='bad'),
                     lambda d:d.update(related_to_current={}),
                     lambda d:d['recipes'][0].update(split='training'),
                     lambda d:d['summary'].update(reservations=1)):
            self.doc=copy.deepcopy(original);edit(self.doc)
            with self.assertRaises(ValueError):self.run_review()


if __name__=='__main__':unittest.main()
