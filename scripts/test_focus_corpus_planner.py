"""Generated metadata/pixel fixtures; no prior reports, runtime, training or device."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from PIL import Image
import human_annotation_review as h
import focus_corpus_inventory as inventory
import focus_corpus_planner as planner


class PlannerTests(unittest.TestCase):
    def setUp(self):
        parent = h.ROOT/'.build/corpus-planner-tests'
        parent.mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(dir=parent))
        self.rows = []
        for n, use in enumerate(('train-candidate', 'train-candidate', 'representative-selection', 'retention-validation')):
            image = self.root/f'{n}.png'
            Image.new('RGB', (256, 256), (n*40, 15, 100)).save(image)
            ref = h.ref(image)
            self.rows.append(dict(id=f'row-{n}', use=use, label=1 if n in (0, 2) else 0,
                             split='train' if n < 2 else 'validation', sourceID=f'source-{0 if n < 2 else n}',
                             relatedGroup=f'group-{0 if n < 2 else n}', control='collectionItem',
                             scene='gridMatrix', frame=ref, crop=dict(ref),
                             **(dict(pairID='pair-1') if n < 2 else {})))
        self.protocol = self.root/'protocol.json'
        self.dump(self.protocol, dict(version='focus-reviewed-full-fit-v1', samples=self.rows), 'protocolSHA256')
        protected = self.root/'protected.json'
        self.dump(protected, dict(sha256='a'*64, path='not-opened.png'))
        admission = self.root/'admission.json'
        self.dump(admission, dict(protectedMetadata=h.ref(protected), heldMembers=[dict(recipeHash='b'*64)],
                                 excludedSelection=[]), 'assemblySHA256')
        self.audit = inventory.audit_rows(self.rows, {'a'*64}, lambda ref, size: h.pixel_digest(h.ROOT, ref))
        self.report = dict(version=inventory.VERSION, protocol=h.ref(self.protocol), admission=h.ref(admission),
                           protectedMetadata=h.ref(protected), **self.audit, coverage=inventory.coverage(self.audit['records']),
                           heldPairs=1, excludedSelection=0)
        self.input = self.root/'inventory.json'
        self.dump(self.input, self.report)
        self.review = self.root/'review.md'
        self.review.write_text('Generated source-relationship review for tests only.')

    def tearDown(self):
        shutil.rmtree(self.root)

    def dump(self, path, doc, seal=None):
        doc = copy.deepcopy(doc)
        if seal:
            doc.pop(seal, None); doc[seal] = h.digest(doc)
        path.write_text(json.dumps(doc))

    def entry(self, name='recipe-a', role='training', **changes):
        recipe = self.root/(name+'.json')
        self.dump(recipe, dict(example=name))
        slot = next(s for s in planner.slots() if s['family']=='artwork' and s['intendedRole']==role)
        return dict(id=name, slotID=slot['id'], intendedRole=role, priorUse='new', recipe=h.ref(recipe),
                    relationshipsKnown=True, sourceGroups=[name+'-source'], layoutGroups=[name+'-layout'],
                    review=h.ref(self.review), **changes)

    def catalog(self, entries):
        return dict(version=planner.CATALOG, baselineProtocol=h.ref(self.protocol), recipes=entries)

    def reserve(self, entries, protected=None):
        return planner.reservations(self.catalog(entries), planner.slots(), h.ref(self.protocol), self.rows,
                                    self.audit['records'], protected or set())

    def test_real_cli_default_report_preserves_every_source_and_gate(self):
        before = {p:h.sha(p) for p in self.root.iterdir() if p.is_file()}
        out = self.root/'output'
        result = subprocess.run([sys.executable, str(h.ROOT/'scripts/focus_corpus_planner.py'),
                                 '--inventory', str(self.input), '--output', str(out)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        plan = h.read(out/'plan.json')
        self.assertEqual(plan['counts'], dict(requestedSlots=60,targetPairs=480,proposedRecipes=0,blockedRecipes=0,unboundSlots=60))
        self.assertEqual(plan['baselineSamples'], 4)
        self.assertEqual(plan['nativePairs'], 1)
        self.assertEqual({r['scene']:r['existingMinimum'] for r in plan['productionSceneGates']}, planner.MIN)
        self.assertFalse(plan['trainingEligible']); self.assertFalse(plan['captureAuthorized'])
        self.assertEqual(before, {p:h.sha(p) for p in before})
        self.assertIn('480', json.dumps(plan))
        self.assertTrue((out/'collection.md').is_file())
        self.assertEqual(h.read(out/'lineage-catalog-template.json')['recipes'], [])
        with self.assertRaises(ValueError): planner.run(self.input, out)

    def test_repeat_is_deterministic_and_catalog_flows_through_real_entrypoint(self):
        cat = self.root/'catalog.json'; self.dump(cat, self.catalog([self.entry()]))
        a = planner.run(self.input, self.root/'one', cat)
        b = planner.run(self.input, self.root/'two', cat)
        self.assertEqual(a, b)
        self.assertEqual(a['counts']['proposedRecipes'], 1)
        self.assertEqual(a['reservations'][0]['status'], 'proposed-source-separated')
        self.assertFalse(a['reservations'][0]['sourceIndependenceEstablished'])

    def test_transitive_source_layout_and_near_duplicate_links_hold_both_roles(self):
        a,b,c = self.entry('a'),self.entry('b'),self.entry('c','validation')
        a['sourceGroups'] = b['sourceGroups'] = ['same-source']
        b['nearDuplicateGroups'] = c['nearDuplicateGroups'] = ['reviewed-similar-layout']
        rows, groups = self.reserve([c,a,b])
        self.assertEqual({r['status'] for r in rows}, {'blocked'})
        self.assertTrue(all('cross_role_relationship' in r['reasons'] for r in rows))
        self.assertEqual(len({r['component'] for r in rows}), 1)
        self.assertEqual((rows,groups), self.reserve([a,b,c]))

    def test_unknown_source_propagates_to_related_peer_without_fabricating_independence(self):
        a,b = self.entry('a'),self.entry('b')
        a['relationshipsKnown']=False; b['relatedRecipeIDs']=['a']
        rows,_ = self.reserve([a,b])
        self.assertTrue(all(r['status']=='blocked' for r in rows))
        self.assertTrue(all('unknown_source_or_layout_relationships' in r['reasons'] for r in rows))

    def test_corrupt_recipe_does_not_remove_a_relationship_bridge(self):
        a,b=self.entry('a'),self.entry('b','validation')
        a['sourceGroups']=b['sourceGroups']=['shared-source']
        (self.root/'a.json').write_text('{}')
        rows,_=self.reserve([a,b])
        self.assertTrue(all(r['status']=='blocked' for r in rows))
        self.assertTrue(all('cross_role_relationship' in r['reasons'] for r in rows))

    def test_existing_validation_cannot_be_reassigned_through_pixels_or_sample_relation(self):
        for changes in ({'relatedSampleIDs':['row-2']}, {'contentSHA256':[self.rows[2]['frame']['sha256']]},
                        {'sourceGroups':['source-2']}):
            entry = self.entry(); entry.update(changes)
            rows,_ = self.reserve([entry])
            self.assertIn('cross_role_relationship', rows[0]['reasons'])
            self.assertEqual(rows[0]['status'], 'blocked')

    def test_protected_and_held_hash_metadata_only(self):
        entry = self.entry(contentSHA256=['a'*64])
        rows,_ = self.reserve([entry], {'a'*64})
        self.assertIn('protected_or_held_content_overlap', rows[0]['reasons'])
        _,_,_,protected,_ = planner.verified_inventory(self.input)
        self.assertEqual(protected, {'a'*64,'b'*64})

    def test_prior_reservations_and_unknowns_are_not_new_training(self):
        for prior in ('development','protected','held','retention','unknown'):
            entry = self.entry(); entry['priorUse']=prior
            self.assertEqual(self.reserve([entry])[0][0]['status'], 'blocked')
        entry = self.entry(); entry['layoutGroups']=[]
        self.assertEqual(self.reserve([entry])[0][0]['status'], 'blocked')
        entry = self.entry(); entry.pop('review')
        self.assertIn('missing_lineage_review', self.reserve([entry])[0][0]['reasons'])
        entry = self.entry(role='validation'); entry['priorUse']='training'
        self.assertIn('training_source_cannot_become_validation', self.reserve([entry])[0][0]['reasons'])

    def test_duplicate_recipe_bytes_cannot_cross_roles(self):
        a,b=self.entry('a'),self.entry('b','validation'); b['recipe']=a['recipe']
        rows,_=self.reserve([a,b])
        self.assertTrue(all(r['status']=='blocked' for r in rows))

    def test_invalid_recipe_accounting_unknown_roles_and_unchanged_output(self):
        for change in ({'slotID':'not-a-slot'}, {'relatedSampleIDs':['missing']},
                       {'relatedRecipeIDs':['missing']}, {'contentSHA256':['oops']},
                       {'intendedRole':'final-challenge'}, {'relationshipsKnown':'yes'}):
            entry=self.entry(); entry.update(change)
            rows,_=self.reserve([entry])
            self.assertEqual(len(rows),1); self.assertEqual(rows[0]['status'],'blocked')
        entry=self.entry(); (self.root/'recipe-a.json').write_text('{}')
        self.assertEqual(self.reserve([entry])[0][0]['status'],'blocked')
        entry=self.entry()
        with self.assertRaisesRegex(ValueError,'duplicate_recipe'):
            self.reserve([entry,entry])
        cat=self.catalog([]); cat['baselineProtocol']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'unbound_lineage'):
            planner.reservations(cat,planner.slots(),h.ref(self.protocol),self.rows,self.audit['records'],set())

    def test_changed_pixels_inventory_protocol_or_protected_metadata_rejected(self):
        original=self.input.read_bytes()
        changed=copy.deepcopy(self.report); changed['coverage'][0]['focused']+=1
        self.dump(self.input,changed)
        with self.assertRaisesRegex(ValueError,'coverage_drift'): planner.verified_inventory(self.input)
        self.input.write_bytes(original)
        image=self.root/'0.png'; before=image.read_bytes(); image.write_bytes(b'bad')
        with self.assertRaises(ValueError): planner.verified_inventory(self.input)
        image.write_bytes(before)
        protected=self.root/'protected.json'; protected.write_text('{}')
        with self.assertRaises(ValueError): planner.verified_inventory(self.input)

    def test_failed_input_leaves_no_output(self):
        self.protocol.write_text('{}')
        with self.assertRaises(ValueError): planner.run(self.input,self.root/'failed')
        self.assertFalse((self.root/'failed').exists())

    def test_collection_quantities_are_configurable_not_gate_overrides(self):
        self.assertEqual(sum(s['targetPairs'] for s in planner.slots(2)),120)
        for count in (0,-1,True,65,1.5):
            with self.assertRaises(ValueError): planner.slots(count)


if __name__ == '__main__':
    unittest.main()
