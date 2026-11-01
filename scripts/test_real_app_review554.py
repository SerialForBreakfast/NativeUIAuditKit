import copy
import unittest
import real_app_review554 as r

CASE = dict(id='c', sha256='a'*64, width=100, height=80)
LABEL = dict(imageSHA256='a'*64, complete=False, objects=[{'id': 'o1', 'class': 'primaryButton', 'box': [1, 2, 10, 10], 'visibility': 'visible', 'provenance': 'reviewer'}],
             focus=dict(state='focused', box=[1, 2, 10, 10]), review=dict(blinded=True, reviewer='', status='pending'))


def label(**changes):
    value = copy.deepcopy(LABEL); value.update(changes); return value


class ReviewLabelTests(unittest.TestCase):
    def test_valid_pending_label(self):
        r.check(label(), CASE)

    def test_accept_needs_reviewer(self):
        with self.assertRaisesRegex(ValueError, 'reviewer'):
            r.check(label(review=dict(blinded=True, reviewer=' ', status='accepted')), CASE)

    def test_flagged_objects_can_be_accepted(self):
        objects = copy.deepcopy(LABEL['objects']); objects[0].update({'class': None, 'flag': 'not-control'})
        r.check(label(objects=objects, review=dict(blinded=True, reviewer='R', status='accepted')), CASE)

    def test_unknown_flag_rejected(self):
        objects = copy.deepcopy(LABEL['objects']); objects[0]['flag'] = 'maybe'
        with self.assertRaisesRegex(ValueError, 'object_flag'):
            r.check(label(objects=objects), CASE)

    def test_unknown_class_rejected(self):
        objects = copy.deepcopy(LABEL['objects']); objects[0]['class'] = 'button'
        with self.assertRaisesRegex(ValueError, 'label_class'):
            r.check(label(objects=objects), CASE)

    def test_box_out_of_frame_rejected(self):
        objects = copy.deepcopy(LABEL['objects']); objects[0]['box'] = [95, 2, 10, 10]
        with self.assertRaisesRegex(ValueError, 'box_out_of_frame'):
            r.check(label(objects=objects), CASE)

    def test_no_focus_has_no_box(self):
        r.check(label(focus=dict(state='no_focus', box=None)), CASE)
        with self.assertRaisesRegex(ValueError, 'focus_box'):
            r.check(label(focus=dict(state='unknown', box=[1, 2, 3, 4])), CASE)

    def test_wrong_image_rejected(self):
        with self.assertRaisesRegex(ValueError, 'label_shape'):
            r.check(label(imageSHA256='b'*64), CASE)


class RecheckTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        from pathlib import Path
        self.tmp = tempfile.TemporaryDirectory(dir=r.q.ROOT/'.build'); self.root = Path(self.tmp.name)/'review'
        (self.root/'labels').mkdir(parents=True)
        r.q.save(self.root/'cases.json', dict(cases=[dict(CASE, app='com.jordankoch.NewsTV')]))
        r.q.save(self.root/'labels/c.json', label(review=dict(blinded=True, reviewer='R', status='accepted')))

    def tearDown(self):
        self.tmp.cleanup()

    def answer(self, item, value):
        (self.root/'recheck/answers').mkdir(parents=True, exist_ok=True)
        r.q.save(self.root/'recheck/answers'/f'{item}.json', value)

    def test_items_cover_completeness_and_focus(self):
        kinds = {i['kind'] for i in r.recheck_items(self.root)}
        self.assertEqual(kinds, {'complete', 'clip', 'focusbox'})  # The fixture box is within 8 px of the edge.

    def test_answer_rules(self):
        item = dict(kind='focusbox', objects=[])
        r.check_answer(item, dict(result='correct', reviewer='R'), CASE)
        with self.assertRaisesRegex(ValueError, 'reviewer'):
            r.check_answer(item, dict(result='correct', reviewer=''), CASE)
        with self.assertRaisesRegex(ValueError, 'answer_shape'):
            r.check_answer(item, dict(result='keep', reviewer='R'), CASE)
        with self.assertRaisesRegex(ValueError, 'box_out_of_frame'):
            r.check_answer(item, dict(result='replace', reviewer='R', box=[90, 0, 20, 5]), CASE)

    def test_apply_writes_version_two_and_keeps_first(self):
        r.recheck_items(self.root)
        with self.assertRaisesRegex(ValueError, 'recheck_unanswered'):
            r.apply_recheck(self.root, self.root/'v2-early')
        self.answer('c--complete', dict(result='missing', reviewer='R', boxes=[{'class': 'listRow', 'box': [20, 20, 10, 10]}]))
        self.answer('c--focusbox', dict(result='no_focus', reviewer='R'))
        self.answer('c--clip', dict(result='done', reviewer='R', clipped=['o1']))
        r.apply_recheck(self.root, self.root/'v2')
        v2 = r.q.load(self.root/'v2/c.json'); v1 = r.q.load(self.root/'labels/c.json')
        self.assertFalse(v2['complete']); self.assertEqual(v2['focus'], dict(state='no_focus', box=None))
        self.assertEqual(len(v2['objects']), 2); self.assertEqual(v1['focus']['state'], 'focused')
        self.assertEqual(v2['objects'][0]['visibility'], 'clipped')


if __name__ == '__main__':
    unittest.main()
