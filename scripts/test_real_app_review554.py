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


class ReviewServerHandlerTests(unittest.TestCase):
    def test_cases_hints_and_adjusted_accept_roundtrip(self):
        import json
        import tempfile
        import threading
        import urllib.request
        from http.server import ThreadingHTTPServer
        from pathlib import Path
        from PIL import Image

        with tempfile.TemporaryDirectory(dir=r.q.ROOT/'.build') as td:
            root = Path(td)/'pack'
            (root/'drafts').mkdir(parents=True); (root/'labels').mkdir(); (root/'hints').mkdir()
            img_path = root/'frame.png'
            Image.new('RGB', (160, 120), (10, 20, 30)).save(img_path)
            sha = r.q.digest(img_path)
            r.q.save(root/'cases.json', dict(version='realapp554-review-v1', classes=r.CLASSES, cases=[
                dict(id='c1', app='com.example.App', flow='f1', image=str(img_path), sha256=sha, width=160, height=120)
            ]))
            r.q.save(root/'drafts/c1.json', dict(
                imageSHA256=sha, complete=False,
                objects=[{'id': 'draft-00', 'class': 'secondaryButton', 'box': [10, 10, 40, 20], 'visibility': 'unknown', 'provenance': 'nonmodel-draft:vision-geometry'}],
                focus=dict(state='unknown', box=None),
                review=dict(blinded=True, reviewer='', status='pending'),
            ))
            r.q.save(root/'hints/c1.json', dict(focusCandidates=[{'index': 0, 'id': 'draft-00', 'class': 'secondaryButton', 'box': [10, 10, 40, 20], 'score': 9.2}]))

            r.Handler.root = root.resolve()
            srv = ThreadingHTTPServer(('127.0.0.1', 0), r.Handler)
            port = srv.server_address[1]
            th = threading.Thread(target=srv.serve_forever, daemon=True)
            th.start()
            try:
                cases_doc = json.loads(urllib.request.urlopen(f'http://127.0.0.1:{port}/api/cases').read())
                self.assertEqual(cases_doc['cases'][0]['draftCount'], 1)
                self.assertEqual(cases_doc['cases'][0]['focusState'], 'unknown')

                case_doc = json.loads(urllib.request.urlopen(f'http://127.0.0.1:{port}/api/case/c1').read())
                self.assertEqual(len(case_doc['hints']['focusCandidates']), 1)

                hints_doc = json.loads(urllib.request.urlopen(f'http://127.0.0.1:{port}/api/hints/c1').read())
                self.assertEqual(hints_doc['focusCandidates'][0]['score'], 9.2)

                post_payload = dict(
                    imageSHA256=sha, complete=True,
                    objects=[{'id': 'draft-00', 'class': 'primaryButton', 'box': [12, 12, 42, 22], 'visibility': 'visible',
                              'provenance': 'nonmodel-draft:vision-geometry;reviewer:adjusted-class;reviewer:adjusted-box'}],
                    focus=dict(state='focused', box=[12, 12, 42, 22]),
                    review=dict(blinded=True, reviewer='Joe', status='accepted'),
                )
                req = urllib.request.Request(
                    f'http://127.0.0.1:{port}/api/case/c1',
                    data=json.dumps(post_payload).encode(),
                    headers={'Content-Type': 'application/json'},
                    method='POST',
                )
                reply = json.loads(urllib.request.urlopen(req).read())
                self.assertEqual(reply, dict(saved=True, status='accepted'))
                self.assertTrue((root/'labels/c1.json').is_file())
            finally:
                srv.shutdown()
                srv.server_close()

    def test_prepare_uses_capture_geometry_explicit_roles_focus_known_and_filters_static_text(self):
        import json
        import tempfile
        from pathlib import Path
        from PIL import Image
        with tempfile.TemporaryDirectory(dir=r.q.ROOT / '.build', prefix='prep554-') as td:
            root = Path(td)
            img1 = root / 'ok.png'
            img2 = root / 'ax.png'
            Image.new('RGB', (3840, 2160), (20, 20, 20)).save(img1)
            Image.new('RGB', (3840, 2160), (30, 30, 30)).save(img2)
            sha1, sha2 = r.q.digest(img1), r.q.digest(img2)
            sess_path = root / 'session.json'
            r.q.save(sess_path, dict(
                bundle='com.example.RealApp',
                cases=[
                    dict(
                        id='c_drift', status='transitional', transitional=True, flow='f1',
                        image=str(img1), sha256=sha1,
                    ),
                    dict(
                        id='c_ok', status='captured', transitional=False, flow='f1',
                        image=str(img1), sha256=sha1, focusKnown=True, focusID='btn_watch',
                        sdkBefore=dict(
                            generation=5, truncated=False, focusKnown=True, focusID='btn_watch',
                            captureGeometry=dict(displayScale=2.0, screenBounds=dict(width=1920, height=1080), toScreenPoints=[1, 0, 0, 1, 10, 20]),
                            richElements=[
                                dict(id='btn_watch', role='primaryButton', bounds=dict(x=100, y=200, width=150, height=50), hidden=False),
                                dict(id='synopsis_copy', role='staticText', bounds=dict(x=400, y=200, width=600, height=200), hidden=False),
                            ],
                        ),
                    ),
                    dict(
                        id='c_ax_exception', status='captured', transitional=False, flow='f2',
                        image=str(img2), sha256=sha2, focusKnown=True, focusID=None,
                        sdkBefore=dict(
                            generation=6, truncated=False, focusKnown=True, focusID=None,
                            captureGeometry=dict(displayScale=2.0, screenBounds=dict(width=1920, height=1080)),
                            richElements=[],
                            accessibilityDrafts=dict(
                                truncated=False,
                                elements=[
                                    dict(draftID='ax-btn', bounds=[50, 60, 120, 40], traits=r.AX_TRAIT_BUTTON),
                                    dict(draftID='ax-syn', bounds=[50, 150, 400, 120], traits=r.AX_TRAIT_STATIC_TEXT),
                                ],
                            ),
                        ),
                    ),
                ],
            ))
            out_dir = root / 'out'
            cases = r.prepare([sess_path], out_dir)
            # Exception case sorts first; transitional frame quarantined
            self.assertEqual([c['id'] for c in cases], ['c_ax_exception', 'c_ok'])
            self.assertTrue(cases[0]['needsReview'])
            self.assertFalse(cases[1]['needsReview'])
            manifest = json.loads((out_dir / 'cases.json').read_text())
            self.assertEqual(manifest['skippedTransitional'], ['c_drift'])

            d_ok = r.q.load(out_dir / 'drafts/c_ok.json')
            self.assertEqual(len(d_ok['objects']), 1)  # staticText synopsis skipped
            self.assertEqual(d_ok['objects'][0]['class'], 'primaryButton')
            self.assertEqual(d_ok['objects'][0]['box'], [220.0, 440.0, 300.0, 100.0])  # +toScreenPoints(10,20) * scale 2
            self.assertEqual(d_ok['focus'], dict(state='focused', box=[220.0, 440.0, 300.0, 100.0]))
            r.check(d_ok, cases[1])

            d_ax = r.q.load(out_dir / 'drafts/c_ax_exception.json')
            self.assertEqual(len(d_ax['objects']), 1)  # static text AX skipped; AX button preserved
            self.assertEqual(d_ax['objects'][0]['class'], 'secondaryButton')
            self.assertEqual(d_ax['focus'], dict(state='no_focus', box=None))
            r.check(d_ax, cases[0])
            self.assertTrue((out_dir / 'metadata/c_ok.json').is_file())


class ContractReviewTests(unittest.TestCase):
    def test_contract_pack_http_roundtrip_and_legacy_rejection(self):
        import hashlib
        import json
        import tempfile
        import threading
        import urllib.request
        import urllib.error
        from pathlib import Path
        from http.server import ThreadingHTTPServer
        from PIL import Image
        import framework_projection604 as fp
        with tempfile.TemporaryDirectory(dir=r.q.ROOT/'.build') as td:
            root = Path(td)
            image = root/'screen.png'
            Image.new('RGB', (100, 80)).save(image)
            draft = dict(version='tvbench-ax-draft-v1', imageSHA256=r.q.digest(image), width=100, height=80,
                         bundleIdentifier='com.example.App', screenID='route', settled=True, classes=fp.tvos_classes(),
                         objects=[dict(id='ax-000', **{'class': 'button'}, box=[1, 2, 10, 10], visibility='unknown',
                                       roleSource='ax_element_type', node=5)],
                         focus=dict(state='unknown', observed='none_observed'))
            source = root/'screen.draft.json'; r.q.save(source, draft)
            before = source.read_bytes()
            bad = copy.deepcopy(draft); bad['imageSHA256'] = '0'*64
            r.q.save(source, bad, replace=True)
            with self.assertRaisesRegex(ValueError, 'image_changed'):
                r.prepare_ax([source], root/'bad-hash')
            self.assertFalse((root/'bad-hash').exists())
            r.q.save(source, draft, replace=True)
            with self.assertRaisesRegex(ValueError, 'duplicate_case_id'):
                r.prepare_ax([source, source], root/'duplicate')
            self.assertFalse((root/'duplicate').exists())
            pack = root/'pack'; r.prepare_ax([source], pack)
            self.assertEqual(before, source.read_bytes())
            self.assertEqual(r.q.load(pack/'metadata/screen.json'), draft)
            pending = r.q.load(pack/'drafts/screen.json')
            self.assertEqual(pending['focus'], dict(state='unknown', box=None))
            self.assertFalse(pending['complete'])
            r.Handler.root = pack
            srv = ThreadingHTTPServer(('127.0.0.1', 0), r.Handler)
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            url = f'http://127.0.0.1:{srv.server_port}'
            def post(value):
                req = urllib.request.Request(url+'/api/case/screen', data=json.dumps(value).encode(),
                                             headers={'Content-Type':'application/json'}, method='POST')
                return json.loads(urllib.request.urlopen(req).read())
            try:
                meta = json.loads(urllib.request.urlopen(url+'/api/cases').read())
                self.assertEqual(meta['classes'], fp.tvos_classes())
                self.assertEqual(meta['focusStates'], ['focused', 'known_no_focus', 'unknown'])
                current = json.loads(urllib.request.urlopen(url+'/api/case/screen').read())
                current.pop('hints')
                self.assertEqual(current.pop('source'), draft)
                current['review'] = dict(blinded=True, reviewer='test-fixture', status='accepted')
                current['focus'] = dict(state='known_no_focus', box=None)
                self.assertTrue(post(current)['saved'])
                self.assertEqual(r.q.load(pack/'labels/screen.json')['objects'][0]['roleSource'], 'ax_element_type')
                current['focus'] = dict(state='unknown', box=None)
                self.assertTrue(post(current)['saved'])
                self.assertEqual(len(list((pack/'labels').glob('screen.*.json'))), 1)
                current['objects'][0]['class'] = 'primaryButton'
                with self.assertRaises(urllib.error.HTTPError) as error:
                    post(current)
                self.assertEqual(error.exception.code, 400)
            finally:
                srv.shutdown(); srv.server_close()

    def test_contract_checks_reject_legacy_focus_and_allow_unknown_role(self):
        import framework_projection604 as fp
        value = label()
        value['objects'][0]['class'] = None
        value['focus'] = dict(state='unknown', box=None)
        r.check(value, CASE, fp.tvos_classes(), ('focused', 'known_no_focus', 'unknown'))
        value['focus']['state'] = 'no_focus'
        with self.assertRaisesRegex(ValueError, 'focus_state'):
            r.check(value, CASE, fp.tvos_classes(), ('focused', 'known_no_focus', 'unknown'))


if __name__ == '__main__':
    unittest.main()
