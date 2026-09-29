import copy
import json
import unittest
from pathlib import Path

from focus_gap_corpus import plan, prepare, audit
from harvest_sidecar_v2 import recipe_hash
from test_ttr_appearance import replace_recipes
from test_ttr_competitor import competitor_meta
import test_ttr_appearance as fixtures


class GapCorpusTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.AppearanceTests(); self.f.setUp()
    def tearDown(self): self.f.tearDown()

    def test_actual_prepare_cli_and_determinism(self):
        out = self.f.root/'pack'
        r = self.f.cli('focus_gap_corpus.py', 'prepare', '--output', out)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads((out/'plan.json').read_text()), plan())
        self.assertEqual(len(list((out/'recipes').glob('*.json'))), 8)
        self.assertEqual(len(plan()['slots']), 12)
        with self.assertRaisesRegex(ValueError,'collision'): prepare(out)
        for slot in plan()['slots']:
            self.assertFalse(slot['trainingAdmission'])
            if slot['recipe']: self.assertEqual(recipe_hash(slot['recipe']), slot['recipeSHA256'])

    def test_missing_and_unsupported_are_not_complete(self):
        result = audit(plan(), {})
        self.assertFalse(result['complete']); self.assertEqual(result['acceptedPairs'], 0)
        self.assertEqual(sum(r['state']=='unsupported-contract' for r in result['slots']), 4)
        with self.assertRaisesRegex(ValueError, 'unsupported_slot'):
            audit(plan(), {'selected-tabs-01': str(self.f.bundle)})

    def test_actual_bundle_matching_and_insufficient_count(self):
        m = competitor_meta(self.f.meta)
        slot = plan()['slots'][0]; r = copy.deepcopy(slot['recipe']); r['recipe_hash']=slot['recipeSHA256']
        replace_recipes(m,r); self.f.publish(m)
        result = audit(plan(), {slot['id']:str(self.f.bundle)})
        got = result['slots'][0]
        self.assertEqual(got['pairs'],1)
        self.assertTrue(got['competitorRequirementMet'])
        self.assertFalse(got['requestedCountMet'])
        self.assertEqual(got['state'],'partial-diagnostic')
        self.assertEqual(result['distinctFramePixels'],2)
        self.assertFalse(result['complete'])

    def test_wrong_recipe_changed_plan_and_duplicate_assignments(self):
        got = audit(plan(), {'button-appearance-01':str(self.f.bundle)})
        self.assertEqual(got['slots'][0]['state'],'blocked')
        self.assertIn('recipe_membership',got['slots'][0]['error'])
        changed = plan(); changed['slots'][0]['recipe']['seed']+=1
        with self.assertRaisesRegex(ValueError,'changed_collection_plan'):audit(changed,{})
        with self.assertRaisesRegex(ValueError,'duplicate_bundle'):
            audit(plan(), {'button-appearance-01':str(self.f.bundle),'settings-rows-01':str(self.f.bundle)})
        with self.assertRaisesRegex(ValueError,'unknown_assignment'):audit(plan(),{'extra':str(self.f.bundle)})

    def test_corrupt_missing_and_wrong_class_do_not_count(self):
        m=competitor_meta(self.f.meta); r=copy.deepcopy(plan()['slots'][0]['recipe']);r['recipe_hash']=recipe_hash(r)
        replace_recipes(m,r);self.f.publish(m)
        (self.f.bundle/'f.png').write_bytes(b'corrupt')
        result=audit(plan(),{'button-appearance-01':str(self.f.bundle)})
        self.assertEqual(result['acceptedPairs'],0);self.assertEqual(result['slots'][0]['state'],'blocked')
        result=audit(plan(),{'button-appearance-01':str(self.f.root/'absent')})
        self.assertEqual(result['slots'][0]['state'],'blocked')

    def test_complete_receipt_and_wrong_class(self):
        from test_ttr_sidecar_v2 import reindex, sha
        f=self.f;slot=plan()['slots'][0];rows=[]
        for i in range(4):
            m=competitor_meta(f.meta);r=copy.deepcopy(slot['recipe']);r['recipe_hash']=recipe_hash(r)
            replace_recipes(m,r)
            target=f'e{i}';other=f'e{(i+1)%4}'
            def remap(value):
                if isinstance(value,dict):
                    if 'focus_observation' in value:
                        observed=target if value['focused_element_id']=='e' else other
                        value['focused_element_id']=observed
                        for e in value['elements']:e['element_id']=target if e['element_id']=='e' else other
                        value['focus_observation'].update(requestedID=observed,observedID=observed,plannedFocusIDs=[f'e{j}' for j in range(4)])
                        value['observation_diagnostics'].update(requestedID=observed,observedID=observed,requiredIDs=[target,other],measuredIDs=[target,other])
                        for j in range(4):
                            if f'e{j}' not in (target,other):
                                e=copy.deepcopy(value['elements'][1]);e.update(element_id=f'e{j}',is_focused=False);value['elements'].append(e)
                    for child in value.values():remap(child)
                elif isinstance(value,list):
                    for child in value:remap(child)
            remap(m);m.update(id=f'pair{i}',competitor_element_id=other)
            (f.bundle/f'm{i}.json').write_text(json.dumps(m))
            rows.append(dict(id=f'pair{i}',path='f.png',sha256=sha(f.bundle/'f.png'),expectedFocus=target,
                             box=m['elements'][0]['pixel_bounds'],split='calibration',
                             metadata=dict(unfocusedPath='u.png',focusedPath='f.png',metadataPath=f'm{i}.json',recipeFile='recipe.json')))
        for name,data in [('manifest',rows),('calibration',rows),('training',[]),('held-out',[])]:
            (f.bundle/(name+'.json')).write_text(json.dumps(data))
        receipt=dict(schemaVersion=1,outcome='completed',acceptedRowCount=4,
                     targetCoverage=dict(targets=[dict(recipe='recipe.json',elementID=f'e{i}',outcome='accepted') for i in range(4)],unavailableRecipes=[]))
        (f.bundle/'harvest-receipt.json').write_text(json.dumps(receipt))
        (f.bundle/'m.json').unlink()  # Replace only this generated test fixture's index member.
        reindex(f.bundle)
        result=audit(plan(),{slot['id']:str(f.bundle)})
        self.assertEqual(result['slots'][0]['state'],'ready-for-crop-review',result)
        self.assertEqual(result['acceptedPairs'],4);self.assertFalse(result['complete'])
        # Pixel reuse is explicit even for four correctly accounted target rows.
        self.assertEqual(result['distinctFramePixels'],2)
        for path in (f.bundle/f'm{i}.json' for i in range(4)):
            path.write_text(path.read_text().replace('"collectionItem"', '"imageView"'))
        reindex(f.bundle)
        result=audit(plan(),{slot['id']:str(f.bundle)})
        self.assertEqual(result['slots'][0]['error'],'unexpected_target_class')

    def test_actual_audit_cli_accounts_for_all_slots(self):
        out=self.f.root/'pack';prepare(out)
        assignments=self.f.root/'assignments.json';assignments.write_text('{}')
        result=self.f.cli('focus_gap_corpus.py','audit','--plan',out/'plan.json',
                         '--assignments',assignments,'--output',self.f.root/'audit.json')
        self.assertEqual(result.returncode,0,result.stderr)
        doc=json.loads((self.f.root/'audit.json').read_text())
        self.assertEqual(len(doc['slots']),12);self.assertFalse(doc['trainingAdmission'])


if __name__=='__main__':unittest.main()
