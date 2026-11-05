"""RC561-01: SDK qualification gates count kept, flagged, deleted and missed boxes, and focus agreement."""
import json
import tempfile
import unittest
from pathlib import Path
import research_queue as q
import sdk_qualification561 as s


def obj(i, box, cls='primaryButton', sdk=True, flag=None):
    o = dict(id=i, box=box, **{'class': cls}, provenance=('sdk-draft:x.' + i) if sdk else 'reviewer', visibility='unknown')
    if flag:
        o['flag'] = flag
    return o


class QualificationTests(unittest.TestCase):
    def write(self, root, name, draft, label):
        for folder, doc in (('drafts', draft), ('labels', label)):
            (root/folder).mkdir(exist_ok=True)
            (root/folder/f'{name}.json').write_text(json.dumps(doc))

    def test_flags_and_missing_boxes_fail_the_right_gates(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build', prefix='sdkq561-') as folder:
            root = Path(folder)
            focus = dict(state='focused', box=[0, 0, 100, 50])
            for n in range(10):
                draft = dict(focus=focus, objects=[obj('a', [0, 0, 100, 50]), obj('b', [200, 0, 100, 50]), obj('c', [400, 0, 100, 50])])
                label = dict(focus=focus, objects=[obj('a', [0, 0, 100, 50]), obj('b', [200, 0, 100, 50], flag='wrong-class' if n == 0 else None),
                                                   obj('c', [400, 0, 100, 50], flag='not-control' if n == 1 else None)])
                if n == 2:
                    label['objects'].append(obj('m', [600, 0, 100, 50], sdk=False, flag='missing'))
                self.write(root, f'app-flow{n % 5}-screen-{n}', draft, label)
            m = s.qualify(root/'drafts', root/'labels')['apps']['app']
            self.assertEqual((m['kept'], m['deleted'], m['missed']), (29, 1, 1))
            self.assertEqual(m['coverage'], round(29/30, 4))
            self.assertEqual(m['roleAgreement'], round(28/29, 4))
            self.assertEqual(m['focusAgreement'], '10/10')
            self.assertFalse(m['checks']['role'])
            self.assertTrue(m['checks']['coverage'])
            self.assertTrue(m['checks']['sample'])
            self.assertFalse(m['qualified'])

    def test_unknown_sdk_focus_fails_focus_gate(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build', prefix='sdkq561-') as folder:
            root = Path(folder)
            self.write(root, 'app-a-b-1', dict(focus=dict(state='unknown', box=None), objects=[obj('a', [0, 0, 10, 10])]),
                       dict(focus=dict(state='focused', box=[0, 0, 10, 10]), objects=[obj('a', [0, 0, 10, 10])]))
            m = s.qualify(root/'drafts', root/'labels')['apps']['app']
            self.assertEqual(m['focusAgreement'], '0/1')
            self.assertFalse(m['checks']['focus'])


    def test_unknown_reference_never_counts_as_focus_agreement(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='sdkq561-') as folder:
            root=Path(folder)
            for n in range(10):
                value=dict(focus=dict(state='unknown',box=None),objects=[obj('a',[0,0,10,10])])
                self.write(root,f'app-flow{n%5}-screen-{n}',value,value)
            result=s.qualify(root/'drafts',root/'labels');m=result['apps']['app']
            self.assertEqual(m['focusAgreement'],'0/0');self.assertEqual(m['unknownFocusReferences'],10)
            self.assertFalse(m['checks']['focus']);self.assertFalse(m['qualified'])
            self.assertEqual(result['metricsStatus'],'provisional')

    def test_verified_no_focus_is_distinct_from_unknown(self):
        draft=dict(focus=dict(state='no_focus'),objects=[])
        self.assertTrue(s.frame_result(draft,draft)['focusAgrees'])
        unknown=dict(focus=dict(state='unknown'),objects=[])
        self.assertFalse(s.frame_result(unknown,draft)['focusAgrees'])

    def test_matching_unknown_classes_are_unresolved_not_role_success(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build',prefix='sdkq561-') as folder:
            root=Path(folder);value=dict(focus=dict(state='no_focus'),objects=[obj('a',[0,0,10,10],cls='UnmappedNativeWidget')])
            self.write(root,'app-a-b-1',value,value)
            m=s.qualify(root/'drafts',root/'labels')['apps']['app']
            self.assertIsNone(m['roleAgreement']);self.assertEqual(m['unresolvedRoleReferences'],1)
            self.assertEqual(m['roleReferenceCount'],0);self.assertFalse(m['checks']['role'])

if __name__ == '__main__':
    unittest.main()
