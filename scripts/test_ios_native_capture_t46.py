"""T46 iOS native capture: offline unit checks, offline queue failures, and an opt-in live queue qualification.

Set NUIAK_T46_LIVE=<build receipt path> to run the live test. It renders on the generator Simulator.
"""
import json
import os
from pathlib import Path
import re
import tempfile
import unittest

from PIL import Image

import research_queue as q
import experiment_batch402 as batches
import ios_native_capture_t46 as t46

FAMILY_RECIPE = dict(version='ios-native-capture-recipe-v1', families=['SettingsList', 'UIKitControls'], seeds=[3, 4],
                     devices=['iPhone 17 Pro'], dynamicType=['large', 'accessibilityMedium'],
                     appearance=['light', 'dark'], groups='family-seed',
                     roles={'SettingsList': 'development', 'UIKitControls': 'development'},
                     trainingEligible=False, supportedClasses='taxonomy', maxFrames=16)


def make_recipe(**change):
    value = json.loads(json.dumps(FAMILY_RECIPE))
    value.update(change)
    return value


def sidecar(frame, png, elements):
    with Image.open(png) as image:
        width, height = image.size
    return {'schemaVersion': '1.0', 'imageSHA256': q.digest(png),
            'image': {'fileName': png.name, 'pixelWidth': width, 'pixelHeight': height, 'scale': 3, 'platform': 'iOS',
                      'osVersion': 'unknown', 'deviceName': frame['device'], 'interfaceIdiom': 'phone',
                      'orientation': 'portrait', 'colorScheme': frame['appearance'],
                      'dynamicTypeSize': frame['dynamicType'], 'locale': 'en_US', 'layoutDirection': 'ltr',
                      'safeAreaInsets': {'top': 0, 'left': 0, 'bottom': 0, 'right': 0}, 'reduceTransparency': False,
                      'increaseContrast': False, 'boldText': False, 'buttonShapes': False, 'onOffLabels': False,
                      'smartInvert': False},
            'generatorProfile': {'templateFamily': frame['family'], 'seed': frame['seed'],
                                 'generatorVersion': t46.GENERATOR_VERSION, 'isolationTemplate': False,
                                 'lowDensity': False,
                                 'simulatorState': {'time': '09:41', 'batteryLevel': 100, 'batteryState': 'charging',
                                                    'cellularBars': 5, 'wifiBars': 3, 'operatorName': ''}},
            'elements': elements}


def element(ident, kind, x, y, w, h, width=100, height=200, excluded=False):
    """A schema 1.0 element in a width x height point canvas at scale 3. Vision bounds are clipped."""
    left, right = max(0, min(width, x)), max(0, min(width, x + w))
    top, bottom = max(0, min(height, y)), max(0, min(height, y + h))
    return {'id': ident, 'elementType': kind, 'framework': 'SwiftUI',
            'boundsPixels': {'x': x * 3, 'y': y * 3, 'width': w * 3, 'height': h * 3},
            'boundsPoints': {'x': x, 'y': y, 'width': w, 'height': h},
            'boundsVisionNormalized': {'x': left / width, 'y': 1 - bottom / height, 'width': (right - left) / width,
                                       'height': (bottom - top) / height},
            'traits': [], 'state': {'isEnabled': True, 'isSelected': False}, 'occluded': False,
            'excluded': excluded, 'exclusionReason': 'outsideImage' if excluded else None, 'knownIssues': []}


def write_frame(folder, frame, gray, elements):
    png = folder / (frame['id'] + '.png')
    Image.new('RGB', (300, 600), (gray, gray, gray)).save(png)
    (folder / (frame['id'] + '.json')).write_text(json.dumps(sidecar(frame, png, elements)))


class RecipeTests(unittest.TestCase):
    def test_parameters(self):
        self.assertEqual(t46.parameters(dict(target=t46.TARGET, timeoutSeconds=600)), (t46.TARGET, 600))
        for value, error in [(dict(target='other', timeoutSeconds=600), 'capture_target'),
                             (dict(target=t46.TARGET, timeoutSeconds=900), 'capture_timeout'),
                             (dict(target=t46.TARGET), 'capture_parameters')]:
            with self.assertRaisesRegex(ValueError, error): t46.parameters(value)

    def test_expansion_groups_roles(self):
        settings, frames = t46.recipe(make_recipe())
        self.assertEqual(len(frames), 16)
        self.assertEqual(len({f['group'] for f in frames}), 4)
        self.assertEqual(len({f['id'] for f in frames}), 16)
        self.assertFalse(any(f['trainingEligible'] for f in frames))
        self.assertEqual(len(settings['supportedClasses']), 41)
        _, family = t46.recipe(make_recipe(groups='family'))
        self.assertEqual({f['group'] for f in family}, {'SettingsList', 'UIKitControls'})
        _, training = t46.recipe(make_recipe(roles={'SettingsList': 'training', 'UIKitControls': 'development'},
                                             trainingEligible=True))
        self.assertEqual({f['family'] for f in training if f['trainingEligible']}, {'SettingsList'})

    def test_recipe_failures(self):
        cases = [(dict(families=['TruncatedLabel']), 'recipe_families'),
                 (dict(families=['Nope']), 'recipe_families'),
                 (dict(roles={'SettingsList': 'development'}), 'recipe_roles'),
                 (dict(roles={'SettingsList': 'final-audit', 'UIKitControls': 'development'}), 'recipe_roles'),
                 (dict(trainingEligible=True), 'recipe_training_role'),
                 (dict(supportedClasses=['badge']), 'recipe_supported_classes'),
                 (dict(supportedClasses=['tabBarItem']), 'recipe_supported_classes'),
                 (dict(maxFrames=8), 'recipe_frame_limit'),
                 (dict(devices=['iPad Pro']), 'recipe_devices'),
                 (dict(dynamicType=['huge']), 'recipe_dynamic_type'),
                 (dict(seeds=[0]), 'recipe_seeds'),
                 (dict(extra=1), 'recipe_fields')]
        for change, error in cases:
            with self.assertRaisesRegex(ValueError, error, msg=str(change)): t46.recipe(make_recipe(**change))

    def test_families_match_swift_allocation(self):
        """The host list is the Swift family allocation without known-bad families."""
        text = t46.SWIFT_TESTS.read_text()
        block = re.search(r'allTemplateFamilies: Set<String> = \[(.*?)\]', text, re.S).group(1)
        swift = set(re.findall(r'"([^"]+)"', block))
        self.assertEqual(set(t46.FAMILIES), swift - t46.KNOWN_BAD)
        self.assertIn('func ' + t46.METHOD, text)

    def test_render_list_has_no_roles(self):
        _, frames = t46.recipe(make_recipe())
        rows = json.loads(t46.render_list(frames))
        self.assertEqual(set(rows[0]), {'id', 'family', 'seed', 'device', 'dynamicType', 'appearance'})


class AssessTests(unittest.TestCase):
    def frames(self, **change):
        recipe = make_recipe(families=['SettingsList'], seeds=[3], dynamicType=['large'],
                             roles={'SettingsList': 'development'}, maxFrames=4, **change)
        return t46.recipe(recipe)

    def test_support_and_variant_checks(self):
        settings, frames = self.frames()
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='t46-') as folder:
            folder = Path(folder)
            light, dark = frames
            write_frame(folder, light, 230, [element('listRow_0', 'listRow', 0, 20, 100, 10),
                                             element('label_0', 'label', 5, 22, 50, 6),
                                             element('toggle_0', 'toggle', 98, 195, 10, 10),
                                             element('label_gone', 'label', 0, 300, 10, 10, excluded=True)])
            write_frame(folder, dark, 30, [element('listRow_0', 'listRow', 0, 20, 100, 10)])
            rows, table, checks = t46.assess(frames, settings, folder)
        self.assertEqual([r['status'] for r in rows], ['eligible', 'eligible'])
        self.assertEqual(table['listRow']['groups'], 1); self.assertEqual(table['listRow']['objects'], 2)
        self.assertEqual(table['toggle']['status'], 'supported')
        self.assertEqual(table['pageControl']['status'], 'absent')
        self.assertEqual(table['label']['rejectedLabels'], 1)
        self.assertEqual(len(table), 41)
        self.assertTrue(checks[0]['rendered'])
        self.assertEqual({r['appearanceVerified'] for r in rows}, {'paired-rendered'})
        report = t46.summarize(rows, table, checks, settings, {})
        self.assertEqual(report['uniqueGroups'], 1); self.assertFalse(report['modelAccepted'])
        self.assertEqual(report['trainingAdmission'], 'not-eligible')

    def test_rejections(self):
        settings, frames = self.frames()
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='t46-') as folder:
            folder = Path(folder)
            # Same gray: the dark variant did not render dark, and the pixels are identical.
            for frame in frames:
                write_frame(folder, frame, 120, [element('listRow_0', 'listRow', 0, 20, 100, 10)])
            rows, _, checks = t46.assess(frames, settings, folder)
            self.assertEqual([r['status'] for r in rows], ['rejected', 'rejected'])
            self.assertIn('appearance-not-rendered', rows[0]['reasons'])
            self.assertTrue(any(r.startswith('duplicate-pixels') for r in rows[1]['reasons']))
            self.assertFalse(checks[0]['rendered'])
            self.assertEqual(rows[0]['appearanceVerified'], 'not-rendered')
            # A class outside the frozen taxonomy fails the job. It is not renamed.
            write_frame(folder, frames[0] | {'id': frames[0]['id']}, 200, [element('badge_0', 'badge', 0, 0, 10, 10)])
            with self.assertRaisesRegex(ValueError, 'unsupported_class:SettingsList:badge'):
                t46.assess(frames, settings, folder)
            # A class outside the recipe allow list also fails.
            write_frame(folder, frames[0], 200, [element('toggle_0', 'toggle', 0, 0, 10, 10)])
            limited, _ = self.frames(supportedClasses=['listRow'])
            with self.assertRaisesRegex(ValueError, 'unsupported_class'):
                t46.assess(frames, limited, folder)
            # Vision coordinates must follow BP-10.
            bad = element('listRow_0', 'listRow', 0, 20, 100, 10)
            bad['boundsVisionNormalized']['y'] = 20 / 200
            write_frame(folder, frames[0], 200, [bad])
            with self.assertRaisesRegex(ValueError, 'vision_coordinates'):
                t46.assess(frames, settings, folder)



class BodyTests(unittest.TestCase):
    """Rendered-body statuses on a drawn 100 x 200 pt canvas at scale 3 (300 x 600 px)."""

    def draw(self, folder, frame, boxes, elements):
        from PIL import ImageDraw
        png = folder / (frame['id'] + '.png')
        image = Image.new('RGB', (300, 600), (240, 240, 240))
        for box in boxes:
            ImageDraw.Draw(image).rectangle([v * 3 for v in box[:2]] + [v * 3 - 1 for v in box[2:]], fill=(20, 20, 20))
        image.save(png)
        side = sidecar(frame, png, elements)
        (folder / (frame['id'] + '.json')).write_text(json.dumps(side))
        return png, side

    def test_statuses(self):
        _, frames = t46.recipe(make_recipe(families=['SettingsList'], seeds=[3], dynamicType=['large'],
                                           appearance=['light'], roles={'SettingsList': 'development'}, maxFrames=1))
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='t46-body-') as folder:
            folder = Path(folder)
            boxes = [(10, 10, 30, 20),            # tight: body equals the box
                     (40, 10, 70, 30),            # inset: body 40-60 x 10-20 inside a 40-70 x 10-30 box
                     (10, 40, 40, 50),            # outside: body wider than its box (10-30)
                     (60, 100, 75, 110)]          # neighbour of the ambiguous box below
            elements = [element('primaryButton_0', 'primaryButton', 10, 10, 20, 10),
                        element('label_0', 'label', 40, 10, 30, 20),
                        element('toggle_0', 'toggle', 10, 40, 20, 10),
                        element('label_1', 'label', 10, 150, 30, 10),
                        element('slider_0', 'slider', 60, 111, 15, 4)]
            boxes[1] = (40, 10, 60, 20)
            png, side = self.draw(folder, frames[0], boxes, elements)
            rows = {r['id']: r for r in t46.measure_bodies(png, side)}
        self.assertEqual(rows['primaryButton_0']['status'], 'tight')
        self.assertEqual(rows['label_0']['status'], 'inset')
        self.assertEqual(rows['toggle_0']['status'], 'outside')
        self.assertEqual(rows['label_1']['status'], 'empty')
        self.assertEqual(rows['slider_0']['status'], 'ambiguous')
        self.assertEqual(rows['primaryButton_0']['iou'], 1.0)

    def test_family_gate(self):
        settings, frames = t46.recipe(make_recipe(families=['SettingsList', 'UIKitControls'], seeds=[3],
                                                  dynamicType=['large'], appearance=['light'], maxFrames=2))
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='t46-body-') as folder:
            folder = Path(folder)
            self.draw(folder, frames[0], [(10, 10, 30, 20)], [element('primaryButton_0', 'primaryButton', 10, 10, 20, 10)])
            self.draw(folder, frames[1], [(10, 10, 40, 20)], [element('toggle_0', 'toggle', 10, 10, 20, 10)])
            rows, _, _ = t46.assess(frames, settings, folder)
            summary, measured = t46.body_summary(frames, rows, folder)
        self.assertEqual(summary['passingFamilies'], ['SettingsList'])
        self.assertEqual(summary['failingFamilies'], ['UIKitControls'])
        self.assertEqual(summary['classes']['toggle']['outside'], 1)
        self.assertEqual(len(measured), 2)

def description(ident, recipe_path, build_path, timeout=600):
    return dict(version='hcf-template-description-v1', id=ident, owner='test-NUIAK', template='T46',
                question='Which frozen classes does the native iOS generator support for this recipe?',
                decision='Name each requested class without eligible grouped support.',
                inputs=dict(recipe=dict(file=q.relative(recipe_path)), generator=dict(file=q.relative(build_path))),
                parameters=dict(target=t46.TARGET, timeoutSeconds=timeout), dependencies=[])


class QueueTests(unittest.TestCase):
    """Failures that stop before any Simulator work, through the actual queue."""

    def test_offline_failures(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='t46-queue-') as folder:
            root = Path(folder); queue = root / 'queue'
            q.save(root / 'recipe.json', make_recipe())
            q.save(root / 'bad-recipe.json', make_recipe(families=['TruncatedLabel'], roles={'TruncatedLabel': 'development'}))
            # A receipt whose app file hash does not match the bytes on disk.
            app = root / 'GeneratorRunner.app'; app.mkdir()
            (app / 'GeneratorRunner').write_bytes(b'binary')
            run = root / 'x.xctestrun'; run.write_bytes(b'plist')
            q.save(root / 'build.json', dict(version='ios-generator-build-v1', bundle=t46.BUNDLE, method=t46.METHOD,
                                            xcode='x', xctestrun=dict(path=q.relative(run), sha256=q.digest(run)),
                                            app=dict(path=q.relative(app), files={'GeneratorRunner': '0' * 64}),
                                            sources={}, buildSeconds=0, log='x'))
            docs = [description('t46-build', root / 'recipe.json', root / 'build.json'),
                    description('t46-recipe', root / 'bad-recipe.json', root / 'build.json')]
            batches.register_batch(dict(version='experiment-batch-v1', jobs=docs), queue, [d['id'] for d in docs],
                                   approver='test')
            for ident, reason in (('t46-build', 'build_app_changed'), ('t46-recipe', 'recipe_families')):
                self.assertEqual(q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=[ident]), [(ident, 'failed')])
                attempt = queue / 'jobs' / ident / 'attempts/1'
                self.assertFalse((attempt / 'out/manifest.json').exists())
                self.assertIn(reason, (attempt / 'stderr.log').read_text())


@unittest.skipUnless(os.environ.get('NUIAK_T46_LIVE'), 'live Simulator qualification is opt-in')
class LiveQueueTests(unittest.TestCase):
    """Positive path on the generator Simulator. 2 recipes run through 1 harness."""

    def test_live_queue(self):
        build = q.ROOT / os.environ['NUIAK_T46_LIVE']
        keep = q.ROOT / '.build/debug-output/t46/live-queue'
        keep.mkdir(parents=True, exist_ok=True)
        root = Path(tempfile.mkdtemp(dir=keep, prefix='run-')); queue = root / 'queue'
        first = make_recipe(families=['SettingsList', 'UIKitControls'], seeds=[3], maxFrames=8)
        second = make_recipe(families=['InteractiveControlPalette'], seeds=[5], dynamicType=['large'],
                             roles={'InteractiveControlPalette': 'development'}, maxFrames=2)
        q.save(root / 'first.json', first); q.save(root / 'second.json', second)
        docs = [description('t46-live-first', root / 'first.json', build),
                description('t46-live-second', root / 'second.json', build)]
        batches.register_batch(dict(version='experiment-batch-v1', jobs=docs), queue, [d['id'] for d in docs],
                               approver='test')
        for doc in docs:
            self.assertEqual(q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=[doc['id']]), [(doc['id'], 'complete')])
            out = queue / 'jobs' / doc['id'] / 'attempts/1/out'
            report = q.load(out / 'benchmark_summary.json')
            manifest = q.load(out / 'manifest.json')
            self.assertFalse(report['modelAccepted'])
            self.assertEqual(len(report['slices']), 41)
            self.assertIn('passingFamilies', report['bodyChecks'])
            self.assertTrue((out / 'bodies.json').is_file())
            self.assertTrue(all(r['trainingEligible'] is False for r in manifest['rows']))
            for row in manifest['rows']:
                self.assertEqual(q.digest(out / row['image']['path']), row['image']['sha256'])
        print('T46_LIVE', root)


if __name__ == '__main__':
    unittest.main()
