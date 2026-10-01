import copy
import unittest
from fixture_recipe_coverage import map_membership, map_catalog, STRUCTURES
from focus_corpus_planner import slots


class MappingTests(unittest.TestCase):
    def doc(self):
        return dict(version=1,families=[dict(recipe_path='example.json',recipe_file_sha256='a'*64,
            independence_group='shared',recipe=dict(theme='dark',appearance=dict(focus=dict(kind='native_image'))))])

    def test_family_only_never_reservation(self):
        doc=self.doc(); second=copy.deepcopy(doc['families'][0]); second['recipe_path']='other.json'; doc['families'].append(second)
        result=map_membership(doc)
        self.assertEqual(result['independentGroupsEstablished'],0)
        self.assertEqual(len(result['declaredGroups']),1)
        self.assertEqual(result['recipes'][0]['family'],'artwork')
        self.assertEqual(len(result['recipes'][0]['candidateSlots']),8)
        self.assertFalse(result['recipes'][0]['originalRecipeBytesVerified'])
        self.assertEqual(result,map_membership(doc))

    def test_unknown_and_duplicate(self):
        doc=self.doc(); doc['families'][0]['recipe']['appearance']={}
        self.assertEqual(map_membership(doc)['recipes'][0]['candidateSlots'],[])
        doc['families'].append(copy.deepcopy(doc['families'][0]))
        with self.assertRaises(ValueError): map_membership(doc)

    def test_declared_presentation_not_filename(self):
        for presentation,family in [('settings_rows','rows'),('nested_tabs_v1','tabs')]:
            doc=self.doc(); doc['families'][0]['recipe']['appearance']['canvas']={'presentation':presentation}
            self.assertEqual(map_membership(doc)['recipes'][0]['family'],family)

    def test_exact_catalog_all_slots_and_negative_paths(self):
        structures={v:k for k,v in STRUCTURES.items()}
        doc=dict(version=1,purpose='source_review_catalog_not_capture_manifest',
            recipes=[dict(path='r.json',sha256='a'*64,recipe={},split_membership='unreserved',shared_source_group='shared')],
            sources=[], totals=dict(slots=60,requested_pairs=480,bound=0),slots=[dict(id=s['id'],family=s['family'],
                structure=structures[s['requestedVariation']],requested_role=s['intendedRole'],
                requested_appearance=s['theme'],candidate_recipe='r.json',candidate_sha256='a'*64,
                requested_pairs=8,binding='unbound',support='candidate',remaining=['rendering pending']) for s in slots()])
        result=map_catalog(doc,lambda r:{})
        self.assertEqual(len(result['mappedSlots']),60)
        self.assertEqual(result['exactSlotsBound'],0)
        for mutation in [lambda d:d['slots'].pop(),lambda d:d['slots'].append(d['slots'][0]),
            lambda d:d['slots'][0].update(candidate_sha256='b'*64),
            lambda d:d['slots'][0].update(binding='reserved'),
            lambda d:d['recipes'][0].update(recipe={'different':True})]:
            candidate=copy.deepcopy(doc); mutation(candidate)
            with self.assertRaises(ValueError): map_catalog(candidate,lambda r:{})


if __name__=='__main__': unittest.main()
