"""T46 iOS native capture: render a pinned recipe with the pinned GeneratorRunner build and record per-class support.

Inputs: a recipe (ios-native-capture-recipe-v1) and a build receipt (ios-generator-build-v1, made by `build`).
The recipe names template families, content seeds, devices, Dynamic Type sizes, appearances, the group rule,
the data role of each family, and whether training eligibility applies. Every variant of 1 scene stays in 1 group
and 1 role. The adapter fails on a class outside the frozen taxonomy. It does not infer or rename labels.

Outputs: frames/<id>.png and .json (frozen schema 1.0), manifest.json (hashes, groups, roles, eligibility),
benchmark_summary.json (per-class support table, variant checks, rendered-body gate), bodies.json (each exported
rectangle against its visible body in pixels), xcodebuild.log, artifact-receipt.json.
No model is accepted. Training eligibility comes only from the recipe.
"""
import argparse
from collections import Counter, defaultdict
import itertools
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import time
import uuid

import research_queue as q

OUT = None
TARGET = 'F3EF9DB8-0B0F-4757-B653-D1628269F6FF'
BUNDLE = 'com.nativeuiauditkit.generatorrunner'
METHOD = 'testRecipeCapture46'
GENERATOR_VERSION = 't46-recipe-v1'
BUILD = q.ROOT / '.build/ios-capture-t46'
SCRATCH = q.ROOT / '.build/debug-output/t46'
SCHEMA = q.ROOT / 'Research/schemas/annotation.schema.json'
CATEGORY_MAP = q.ROOT / 'Research/schemas/category_map.json'
SWIFT_TESTS = q.ROOT / 'GeneratorRunner/GeneratorRunnerTests/GenerateDatasetTests.swift'
# Device profiles that GenerateDatasetTests.makeConfig already uses: name -> pixel scale.
DEVICES = {'iPhone 17 Pro': 3, 'iPhone SE (3rd generation)': 2}
DYNAMIC_TYPE = ('xSmall', 'small', 'medium', 'large', 'xLarge', 'xxLarge', 'xxxLarge', 'accessibilityMedium',
                'accessibilityLarge', 'accessibilityExtraLarge', 'accessibilityExtraExtraLarge',
                'accessibilityExtraExtraExtraLarge')
APPEARANCE = ('light', 'dark')
ROLES = ('training', 'development', 'calibration', 'audit-reserved')
GROUP_RULES = ('family-seed', 'family')
# Known-bad families carry intentional defects. They are not native class sources.
KNOWN_BAD = {'TruncatedLabel', 'ClippedContent', 'OverlappingControls', 'SmallHitTarget', 'DynamicTypeOverflow',
             'RTLMirroringFailure', 'OffScreenElement', 'OccludedElement', 'HardNegative_1', 'HardNegative_3'}
FAMILIES = (
    'AccountProfileForm', 'ActionSheet', 'Alert', 'AlertWithTextField', 'CardDetail', 'ChromeCoverage', 'ColorPicker',
    'ContextMenu', 'EmptyState', 'FormValidation', 'GalleryPage', 'InteractiveControlPalette', 'KitchenSink',
    'LinkRichText', 'LiquidGlassNav', 'LiquidGlassTab', 'LoadingSkeleton', 'LoginForm', 'MapOverlays', 'MediaCardGrid',
    'MenuButton', 'ModalDialogueFlow', 'MultiSectionForm', 'NotificationCenter', 'OnboardingPage', 'PickerDateEntry',
    'Popover', 'ProgressActivity', 'RTLMirror', 'RefreshControl', 'RichContentFeed', 'SearchResults', 'SegmentedFilter',
    'SettingsDisclosure', 'SettingsList', 'SettingsToggleDense', 'Sheet', 'SliderPanel', 'Stepper',
    'SystemNavigationShell', 'TabViewNavigation', 'ToolbarActions', 'UIKitControls', 'UIKitForm', 'UIKitList',
    'UIKitToggleForm', 'WizardStepFlow', 'iPadSidebar')
RECIPE_FIELDS = {'version', 'families', 'seeds', 'devices', 'dynamicType', 'appearance', 'groups', 'roles',
                 'trainingEligible', 'supportedClasses', 'maxFrames'}
# A dark frame must be this much darker (mean luma, 0..1) than its matched light frame.
APPEARANCE_MARGIN = .05
POINT_TOLERANCE = .51
NORMALIZED_TOLERANCE = 1e-4


def taxonomy():
    """The frozen 41 classes. `unknown` is a frozen class: a native-looking element without a confident class."""
    return [c['name'] for c in sorted(q.load(CATEGORY_MAP)['categories'], key=lambda c: c['id'])]


def parameters(value):
    """Return (target, timeoutSeconds) or raise. Only the qualified generator Simulator is accepted."""
    q.require(isinstance(value, dict) and set(value) == {'target', 'timeoutSeconds'}, 'capture_parameters')
    q.require(value['target'] == TARGET, 'capture_target')
    q.require(type(value['timeoutSeconds']) is int and 60 <= value['timeoutSeconds'] <= 700, 'capture_timeout')
    return value['target'], value['timeoutSeconds']


def _ordered(values, allowed, reason, limit=None):
    q.require(isinstance(values, list) and values and len(values) == len(set(map(json.dumps, values))), reason)
    q.require(all(v in allowed for v in values), reason)
    q.require(limit is None or len(values) <= limit, reason)
    return values


def recipe(doc):
    """Validate a recipe and return (settings, frames). Frames are the explicit render list in a fixed order."""
    q.require(isinstance(doc, dict) and set(doc) == RECIPE_FIELDS, 'recipe_fields')
    q.require(doc['version'] == 'ios-native-capture-recipe-v1', 'recipe_version')
    families = _ordered(doc['families'], FAMILIES, 'recipe_families', 48)
    seeds = doc['seeds']
    q.require(isinstance(seeds, list) and seeds and len(seeds) == len(set(seeds)) and
              all(type(s) is int and 1 <= s < 2 ** 40 for s in seeds), 'recipe_seeds')
    devices = _ordered(doc['devices'], DEVICES, 'recipe_devices')
    sizes = _ordered(doc['dynamicType'], DYNAMIC_TYPE, 'recipe_dynamic_type')
    looks = _ordered(doc['appearance'], APPEARANCE, 'recipe_appearance')
    q.require(doc['groups'] in GROUP_RULES, 'recipe_groups')
    roles = doc['roles']
    # Roles are per family, so related variants and seeds of 1 family never cross a role.
    q.require(isinstance(roles, dict) and set(roles) == set(families) and all(r in ROLES for r in roles.values()),
              'recipe_roles')
    q.require(type(doc['trainingEligible']) is bool, 'recipe_training_eligible')
    q.require(not doc['trainingEligible'] or 'training' in roles.values(), 'recipe_training_role')
    classes = doc['supportedClasses']
    names = taxonomy()
    if classes == 'taxonomy':
        classes = names
    q.require(isinstance(classes, list) and classes and len(classes) == len(set(classes)) and
              set(classes) <= set(names), 'recipe_supported_classes')
    q.require(type(doc['maxFrames']) is int and 1 <= doc['maxFrames'] <= 200, 'recipe_max_frames')
    frames = []
    for family, seed, device, size, look in itertools.product(families, seeds, devices, sizes, looks):
        short = 'pro' if device == 'iPhone 17 Pro' else 'se'
        group = f'{family}:{seed}' if doc['groups'] == 'family-seed' else family
        frames.append(dict(id=f'{family}-s{seed}-{short}-{size}-{look}', family=family, seed=seed, device=device,
                           dynamicType=size, appearance=look, group=group, role=roles[family],
                           trainingEligible=doc['trainingEligible'] and roles[family] == 'training'))
    q.require(len(frames) <= doc['maxFrames'], 'recipe_frame_limit')
    settings = dict(groups=doc['groups'], trainingEligible=doc['trainingEligible'], supportedClasses=classes,
                    roles=roles)
    return settings, frames


def render_list(frames):
    """The JSON the Swift test decodes. Group and role stay on the host side."""
    keys = ('id', 'family', 'seed', 'device', 'dynamicType', 'appearance')
    return json.dumps([{k: f[k] for k in keys} for f in frames], separators=(',', ':'), sort_keys=True)


# ---------------------------------------------------------------- build pinning

def sources():
    """Hash of the Swift and project files that make the generator build."""
    paths = set()
    for folder in ('GeneratorRunner', 'NativeUIDatasetGenerator'):
        paths.update(p for p in (q.ROOT / folder).rglob('*')
                     if p.is_file() and p.suffix in ('.swift', '.pbxproj', '.plist', '.xcscheme', '.xctestplan')
                     and 'xcuserdata' not in p.parts)
    return {q.relative(p): q.digest(p) for p in sorted(paths)}


def app_hashes(app):
    return {str(p.relative_to(app)): q.digest(p) for p in sorted(app.rglob('*')) if p.is_file() and not p.is_symlink()}


def build(receipt_path):
    """Build GeneratorRunner for testing into .build and write the build receipt. No Simulator change."""
    receipt_path = Path(receipt_path).absolute()
    q.require(receipt_path.is_relative_to(q.ROOT) and not receipt_path.exists(), 'build_receipt_path')
    derived = BUILD / 'DerivedData'
    log = BUILD / ('build-' + time.strftime('%Y%m%dT%H%M%S') + '.log')
    BUILD.mkdir(parents=True, exist_ok=True)
    tmp = BUILD / 'tmp'; tmp.mkdir(exist_ok=True)
    started = time.monotonic()
    with log.open('x') as stream:
        code = subprocess.run(['xcodebuild', 'build-for-testing', '-project', 'GeneratorRunner/GeneratorRunner.xcodeproj',
                               '-scheme', 'GeneratorRunnerTests', '-destination', 'generic/platform=iOS Simulator',
                               '-configuration', 'Debug', '-derivedDataPath', str(derived),
                               'CODE_SIGNING_ALLOWED=NO', 'CODE_SIGNING_REQUIRED=NO'],
                              cwd=q.ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=1800,
                              env=dict(os.environ, TMPDIR=str(tmp))).returncode
    q.require(code == 0, 'build_failed:' + q.relative(log))
    products = derived / 'Build/Products'
    runs = sorted(products.glob('GeneratorRunnerTests_iphonesimulator*.xctestrun'))
    q.require(len(runs) == 1, 'xctestrun_ambiguous')
    app = products / 'Debug-iphonesimulator/GeneratorRunner.app'
    q.require(plistlib.loads((app / 'Info.plist').read_bytes())['CFBundleIdentifier'] == BUNDLE, 'app_identity')
    q.require((app / 'PlugIns/GeneratorRunnerTests.xctest').is_dir(), 'test_bundle_missing')
    value = dict(version='ios-generator-build-v1', bundle=BUNDLE, method=METHOD,
                 xcode=subprocess.check_output(['xcodebuild', '-version'], text=True).strip(),
                 xctestrun=dict(path=q.relative(runs[0]), sha256=q.digest(runs[0])),
                 app=dict(path=q.relative(app), files=app_hashes(app)),
                 sources=sources(), buildSeconds=round(time.monotonic() - started, 1), log=q.relative(log))
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    q.save(receipt_path, value)
    return dict(receipt=q.relative(receipt_path), sha256=q.digest(receipt_path), seconds=value['buildSeconds'])


def check_build(doc):
    """Verify the pinned build bytes before any Simulator work. Return the app and xctestrun paths."""
    q.require(isinstance(doc, dict) and doc.get('version') == 'ios-generator-build-v1' and doc.get('bundle') == BUNDLE
              and doc.get('method') == METHOD, 'build_receipt')
    run = q.local_path(q.ROOT, doc['xctestrun']['path'])
    q.require(run.is_file() and q.digest(run) == doc['xctestrun']['sha256'], 'build_xctestrun_changed')
    app = q.local_path(q.ROOT, doc['app']['path'])
    q.require(app.is_dir() and app_hashes(app) == doc['app']['files'], 'build_app_changed')
    return app, run


# ---------------------------------------------------------------- simulator run

def runtime(target):
    devices = json.loads(subprocess.check_output(['xcrun', 'simctl', 'list', 'devices', 'available', '-j'],
                                                 text=True, timeout=60))
    found = [(r, d) for r, ds in devices['devices'].items() for d in ds if d['udid'] == target]
    q.require(len(found) == 1, 'target_missing')
    name, device = found[0]
    q.require(device['state'] == 'Booted', 'target_not_booted')
    q.require(device['deviceTypeIdentifier'].endswith('iPhone-17-Pro'), 'target_device_type')
    return dict(runtime=name, name=device['name'], udid=target)


def container(target):
    path = Path(subprocess.check_output(['xcrun', 'simctl', 'get_app_container', target, BUNDLE, 'data'],
                                        text=True, timeout=60).strip())
    expected = Path.home() / 'Library/Developer/CoreSimulator/Devices' / target / 'data/Containers/Data/Application'
    q.require(path.is_absolute() and path.resolve() == path and path.parent == expected and path.is_dir(),
              'container_invalid')
    return path


def installed_app(target):
    return Path(subprocess.check_output(['xcrun', 'simctl', 'get_app_container', target, BUNDLE, 'app'],
                                        text=True, timeout=60).strip())


def simulate(frames, build_doc, target, timeout, out):
    """Run the pinned test once. Copy and verify each frame. Never retry and never delete native originals."""
    app, xctestrun = check_build(build_doc)
    device = runtime(target)
    q.require(shutil.disk_usage(q.ROOT).free > 2_000_000_000, 'storage_reserve')
    name = 't46_' + uuid.uuid4().hex[:16]
    scratch = SCRATCH / name
    scratch.mkdir(parents=True)
    (scratch / 'tmp').mkdir()
    plan = plistlib.loads(xctestrun.read_bytes())
    target_run = plan['GeneratorRunnerTests']
    target_run['OnlyTestIdentifiers'] = ['GenerateDatasetTests/' + METHOD]
    target_run.setdefault('EnvironmentVariables', {}).update(NUIAK_T46_RECIPE=render_list(frames),
                                                             NUIAK_T46_OUTPUT=name)
    # The modified run file must sit next to the products it references.
    config = xctestrun.parent / (name + '.xctestrun')
    with config.open('xb') as stream:
        plistlib.dump(plan, stream)
    log = out / 'xcodebuild.log'
    started = time.monotonic()
    try:
        with log.open('x') as stream:
            process = subprocess.Popen(['xcodebuild', 'test-without-building', '-xctestrun', str(config),
                                        '-destination', 'platform=iOS Simulator,id=' + target,
                                        '-parallel-testing-enabled', 'NO',
                                        '-only-testing:GeneratorRunnerTests/GenerateDatasetTests/' + METHOD,
                                        '-resultBundlePath', str(scratch / 'result.xcresult')],
                                       cwd=q.ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                       env=dict(os.environ, TMPDIR=str(scratch / 'tmp')))
            try:
                code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.terminate()  # Only the xcodebuild process that this call started.
                process.wait(timeout=30)
                raise ValueError('capture_timeout_no_retry')
    finally:
        config.unlink()
    seconds = time.monotonic() - started
    text = log.read_text(errors='replace')
    q.require(code == 0 and re.search(r'Test Case .*' + METHOD + r'.* passed', text) and
              not re.search(r'Test Case .*' + METHOD + r'.* skipped', text), 'test_not_passed')
    q.require(app_hashes(installed_app(target)) == build_doc['app']['files'], 'installed_build_changed')
    source = container(target) / 'Documents' / name
    receipt = q.load(source / 'receipt.json')
    q.require(receipt.get('schemaVersion') == 'ios-native-capture-receipt-v1' and receipt.get('complete') is True,
              'native_receipt_incomplete')
    q.require(receipt['recipeSHA256'] == __import__('hashlib').sha256(render_list(frames).encode()).hexdigest(),
              'native_recipe_changed')
    q.require([r['id'] for r in receipt['frames']] == [f['id'] for f in frames], 'native_frame_membership')
    folder = out / 'frames'
    folder.mkdir()
    total = 0
    for record in receipt['frames']:
        for suffix, key in (('.png', 'imageSHA256'), ('.json', 'sidecarSHA256')):
            original = source / (record['id'] + suffix)
            q.require(not original.is_symlink() and q.digest(original) == record[key], 'native_frame_changed')
            total += original.stat().st_size
            q.require(total <= 80_000_000, 'capture_copy_budget')
            shutil.copyfile(original, folder / original.name)
            q.require(q.digest(folder / original.name) == record[key], 'copy_hash')
    return dict(device=device, osVersion=receipt['osVersion'], nativeSeconds=receipt['seconds'],
                testSeconds=round(seconds, 1), nativeOutput=str(source), result=q.relative(scratch / 'result.xcresult'),
                restoration='No status bar or settings change. Test windows released. Native originals retained.')


# ---------------------------------------------------------------- validation and support

def luma(path):
    from PIL import Image
    with Image.open(path) as image:
        values = image.convert('L').resize((64, 64)).tobytes()
    return sum(values) / len(values) / 255


def check_sidecar(frame, sidecar, png, schema, supported, check_schema):
    """Return (admitted labels, rejected labels). Raise on a schema, binding, or class failure."""
    from annotation_schema_validation import validate_sidecar_structure
    from PIL import Image
    # Name an unsupported class before the generic schema enum check rejects it.
    unsupported = sorted({str(e.get('elementType')) for e in sidecar.get('elements', [])
                          if e.get('elementType') not in supported})
    q.require(not unsupported, 'unsupported_class:' + frame['family'] + ':' + ','.join(unsupported))
    validate_sidecar_structure(sidecar)
    check_schema(sidecar, schema, schema)
    meta, profile = sidecar['image'], sidecar['generatorProfile']
    with Image.open(png) as image:
        size = image.size
    q.require(sidecar['imageSHA256'] == q.digest(png) and meta['fileName'] == png.name and
              (meta['pixelWidth'], meta['pixelHeight']) == size, 'sidecar_image_binding')
    q.require(meta['deviceName'] == frame['device'] and meta['scale'] == DEVICES[frame['device']] and
              meta['colorScheme'] == frame['appearance'] and meta['dynamicTypeSize'] == frame['dynamicType'] and
              meta['platform'] == 'iOS', 'sidecar_recipe_binding')
    q.require(profile['templateFamily'] == frame['family'] and profile['seed'] == frame['seed'] and
              profile['generatorVersion'] == GENERATOR_VERSION, 'sidecar_generator_binding')
    width, height, scale = size[0] / meta['scale'], size[1] / meta['scale'], meta['scale']
    admitted, rejected = [], []
    for element in sidecar['elements']:
        points, pixels, vision = element['boundsPoints'], element['boundsPixels'], element['boundsVisionNormalized']
        # BP-10 and BP-11: pixels = points x scale; Vision y origin is bottom-left; Vision bounds are clipped.
        q.require(all(abs(pixels[k] - points[k] * scale) <= POINT_TOLERANCE for k in ('x', 'y', 'width', 'height')),
                  'pixel_scale:' + element['id'])
        left, right = max(0, min(width, points['x'])), max(0, min(width, points['x'] + points['width']))
        top, bottom = max(0, min(height, points['y'])), max(0, min(height, points['y'] + points['height']))
        expected = dict(x=left / width, y=1 - bottom / height, width=(right - left) / width,
                        height=(bottom - top) / height)
        q.require(all(abs(vision[k] - expected[k]) <= NORMALIZED_TOLERANCE for k in expected),
                  'vision_coordinates:' + element['id'])
        row = dict(id=element['id'], elementType=element['elementType'], pixels=pixels)
        if element['excluded']:
            rejected.append(dict(row, reason='excluded:' + str(element.get('exclusionReason'))))
        elif element['knownIssues']:
            rejected.append(dict(row, reason='known-issue'))
        elif points['width'] <= 0 or points['height'] <= 0:
            rejected.append(dict(row, reason='zero-area'))
        else:
            admitted.append(dict(row, occluded=element['occluded']))
    return admitted, rejected


def variant_checks(frames, folder):
    """Matched pairs inside 1 group. A dark frame that is not darker than its light pair did not render dark."""
    by_key = {(f['family'], f['seed'], f['device'], f['dynamicType'], f['appearance']): f for f in frames}
    reasons, pairs = defaultdict(list), []
    for (family, seed, device, size, look), frame in by_key.items():
        if look != 'light' or (family, seed, device, size, 'dark') not in by_key:
            continue
        dark = by_key[(family, seed, device, size, 'dark')]
        light_value, dark_value = luma(folder / (frame['id'] + '.png')), luma(folder / (dark['id'] + '.png'))
        rendered = light_value - dark_value >= APPEARANCE_MARGIN
        pairs.append(dict(kind='appearance', light=frame['id'], dark=dark['id'], lightLuma=round(light_value, 4),
                          darkLuma=round(dark_value, 4), rendered=rendered))
        if not rendered:
            reasons[frame['id']].append('appearance-not-rendered')
            reasons[dark['id']].append('appearance-not-rendered')
    return pairs, reasons


def layout_checks(frames, labels):
    """Report whether a Dynamic Type change moved any admitted label. It is a measurement, not a rejection."""
    by_key = defaultdict(list)
    for f in frames:
        by_key[(f['family'], f['seed'], f['device'], f['appearance'])].append(f)
    rows = []
    for key, members in sorted(by_key.items()):
        if len(members) < 2:
            continue
        boxes = {f['id']: sorted((l['id'], tuple(l['pixels'].values())) for l in labels[f['id']]) for f in members}
        first = members[0]
        for other in members[1:]:
            rows.append(dict(kind='dynamicType', base=first['id'], variant=other['id'],
                             baseSize=first['dynamicType'], variantSize=other['dynamicType'],
                             labelsChanged=boxes[first['id']] != boxes[other['id']]))
    return rows


def assess(frames, settings, folder):
    """Validate every sidecar, reject unproven frames, and build the manifest rows and support table."""
    from validate_reconstructed_corpus import check_schema
    schema = q.load(SCHEMA)
    supported = set(settings['supportedClasses'])
    labels, rejected = {}, {}
    for frame in frames:
        png, side = folder / (frame['id'] + '.png'), folder / (frame['id'] + '.json')
        labels[frame['id']], rejected[frame['id']] = check_sidecar(frame, q.load(side), png, schema, supported,
                                                                   check_schema)
    pairs, reasons = variant_checks(frames, folder)
    seen = {}
    for frame in frames:
        digest = q.digest(folder / (frame['id'] + '.png'))
        if digest in seen:
            reasons[frame['id']].append('duplicate-pixels:' + seen[digest])
        else:
            seen[digest] = frame['id']
        if not labels[frame['id']]:
            reasons[frame['id']].append('no-admitted-labels')
    # Only a rendered light/dark pair proves the appearance. SwiftUI templates can set their own scheme.
    proven = {p[k] for p in pairs if p['rendered'] for k in ('light', 'dark')}
    failed = {p[k] for p in pairs if not p['rendered'] for k in ('light', 'dark')}
    rows = []
    for frame in frames:
        png, side = folder / (frame['id'] + '.png'), folder / (frame['id'] + '.json')
        status = 'rejected' if reasons[frame['id']] else 'eligible'
        appearance = 'paired-rendered' if frame['id'] in proven else 'not-rendered' if frame['id'] in failed \
            else 'unverified'
        rows.append(dict(id=frame['id'], image=dict(path='frames/' + png.name, sha256=q.digest(png)),
                         sidecar=dict(path='frames/' + side.name, sha256=q.digest(side)),
                         group=frame['group'], role=frame['role'], family=frame['family'], seed=frame['seed'],
                         device=frame['device'], dynamicType=frame['dynamicType'], appearance=frame['appearance'],
                         appearanceVerified=appearance, status=status, reasons=reasons[frame['id']],
                         trainingEligible=frame['trainingEligible'] and status == 'eligible',
                         labels=len(labels[frame['id']]), rejectedLabels=len(rejected[frame['id']])))
    table = support(rows, labels, rejected, settings['supportedClasses'])
    return rows, table, pairs + layout_checks(frames, labels)


def support(rows, labels, rejected, supported):
    """Per-class native support over the frozen taxonomy. Only eligible frames count as support."""
    eligible = {r['id']: r for r in rows if r['status'] == 'eligible'}
    table = {}
    for name in taxonomy():
        objects, frames, groups, families, by_role = 0, set(), set(), set(), Counter()
        for ident, row in eligible.items():
            found = [l for l in labels[ident] if l['elementType'] == name]
            if found:
                objects += len(found); frames.add(ident); groups.add(row['group']); families.add(row['family'])
                by_role[row['role']] += len(found)
        lost = sum(l['elementType'] == name for r in rows for l in rejected[r['id']])
        table[name] = dict(supportedByRecipe=name in supported, objects=objects, frames=len(frames),
                           groups=len(groups), families=sorted(families), byRole=dict(by_role),
                           rejectedLabels=lost, status='supported' if groups else 'absent')
    return table


def summarize(rows, table, checks, settings, meta):
    eligible = [r for r in rows if r['status'] == 'eligible']
    requested = settings['supportedClasses']
    present = [c for c in requested if table[c]['status'] == 'supported']
    return dict(version='ios-native-capture-summary-v1', template='T46', **meta,
                frames=len(rows), eligibleFrames=len(eligible), uniqueGroups=len({r['group'] for r in eligible}),
                rejectedFrames={r['id']: r['reasons'] for r in rows if r['status'] != 'eligible'},
                rejectedLabels=sum(r['rejectedLabels'] for r in rows), unavailableGeometry=0,
                roles=dict(Counter(r['role'] for r in eligible)),
                appearanceVerified=dict(Counter(r['appearanceVerified'] for r in rows)),
                trainingEligibleFrames=sum(r['trainingEligible'] for r in rows),
                coverage=dict(requested=len(requested), supported=len(present),
                              absent=[c for c in requested if c not in present]),
                variantChecks=checks, slices=table, gains=[], lostPriorSuccesses=[], modelAccepted=False,
                trainingAdmission='recipe-stated' if settings['trainingEligible'] else 'not-eligible',
                limitation='Generated geometry is the generator layout, not a reviewed label. Support counts admitted '
                           'labels in eligible frames. Variants of 1 group are not independent examples.')


# ---------------------------------------------------------------- rendered-body measurement
# The gate is fixed before results are read. Units are points; pixels = points x scale.
BODY_MARGIN = 3          # window = label box expanded by this many points on each side
BODY_TOLERANCE = 1       # an edge may differ by this many points (plus 1 px rounding)
RING_UNIFORM = .85       # fraction of ring pixels that must match the ring median
RING_MATCH = 12          # max channel difference for a ring pixel to match the background
FOREGROUND = 24          # max channel difference above which a window pixel is body
EMPTY_LIMIT = .10        # a family passes with at most this fraction of empty measurable labels


def measure_bodies(png, sidecar):
    """Compare each admitted exported rectangle with the visible body in pixels. Top-left pixel coordinates (BP-10).

    The background is the median of a ring around the box. A non-uniform ring makes the label ambiguous, because a
    neighbour or a gradient can then look like body. The body is the bounding box of pixels that differ from it.
    """
    import numpy as np
    from PIL import Image
    with Image.open(png) as image:
        pixels = np.asarray(image.convert('RGB'), dtype=np.int16)
    height, width = pixels.shape[:2]
    scale = sidecar['image']['scale']
    margin, tolerance = BODY_MARGIN * scale, BODY_TOLERANCE * scale + 1
    rows = []
    for element in sidecar['elements']:
        if element['excluded'] or element['knownIssues']:
            continue
        b = element['boundsPixels']
        x0, y0 = max(0, int(round(b['x']))), max(0, int(round(b['y'])))
        x1, y1 = min(width, int(round(b['x'] + b['width']))), min(height, int(round(b['y'] + b['height'])))
        row = dict(id=element['id'], elementType=element['elementType'], box=[x0, y0, x1, y1])
        if x1 - x0 < 1 or y1 - y0 < 1:
            rows.append(dict(row, status='ambiguous', reason='outside-image')); continue
        wx0, wy0 = max(0, x0 - margin), max(0, y0 - margin)
        wx1, wy1 = min(width, x1 + margin), min(height, y1 + margin)
        window = pixels[wy0:wy1, wx0:wx1]
        inside = np.zeros(window.shape[:2], bool)
        inside[y0 - wy0:y1 - wy0, x0 - wx0:x1 - wx0] = True
        ring = window[~inside]
        if len(ring) < 20:
            rows.append(dict(row, status='ambiguous', reason='no-ring')); continue
        background = np.median(ring, axis=0)
        uniform = float((np.abs(ring - background).max(axis=1) <= RING_MATCH).mean())
        row['ringUniform'] = round(uniform, 3)
        if uniform < RING_UNIFORM:
            rows.append(dict(row, status='ambiguous', reason='non-uniform-ring')); continue
        mask = np.abs(window - background).max(axis=2) > FOREGROUND
        if not mask[inside].any():
            rows.append(dict(row, status='empty')); continue
        ys, xs = np.nonzero(mask)
        body = [int(xs.min()) + wx0, int(ys.min()) + wy0, int(xs.max()) + 1 + wx0, int(ys.max()) + 1 + wy0]
        # Positive offset: the body is inside the box on that side. Negative: the body passes the box.
        offsets = [body[0] - x0, body[1] - y0, x1 - body[2], y1 - body[3]]
        status = 'tight' if all(abs(o) <= tolerance for o in offsets) else \
            'outside' if any(o < -tolerance for o in offsets) else 'inset'
        inter = max(0, min(x1, body[2]) - max(x0, body[0])) * max(0, min(y1, body[3]) - max(y0, body[1]))
        union = (x1 - x0) * (y1 - y0) + (body[2] - body[0]) * (body[3] - body[1]) - inter
        rows.append(dict(row, status=status, body=body, offsetsPixels=offsets, iou=round(inter / union, 4)))
    return rows


def body_summary(frames, rows, folder):
    """Per-family gate and per-class distribution. Only frames that passed the other checks count."""
    eligible = {r['id'] for r in rows if r['status'] == 'eligible'}
    measured = {}
    for frame in frames:
        if frame['id'] in eligible:
            sidecar = q.load(folder / (frame['id'] + '.json'))
            measured[frame['id']] = measure_bodies(folder / (frame['id'] + '.png'), sidecar)
    statuses = ('tight', 'inset', 'outside', 'empty', 'ambiguous')
    by_family, by_class = defaultdict(Counter), defaultdict(Counter)
    for frame in frames:
        for item in measured.get(frame['id'], []):
            by_family[frame['family']][item['status']] += 1
            by_class[item['elementType']][item['status']] += 1
    families = {}
    for name, counts in sorted(by_family.items()):
        usable = sum(counts[s] for s in ('tight', 'inset', 'outside', 'empty'))
        families[name] = dict({s: counts[s] for s in statuses}, measurable=usable,
                              passes=usable > 0 and counts['outside'] == 0 and counts['empty'] <= EMPTY_LIMIT * usable)
    gate = dict(marginPoints=BODY_MARGIN, tolerancePoints=BODY_TOLERANCE, ringUniform=RING_UNIFORM,
                ringMatch=RING_MATCH, foreground=FOREGROUND, emptyLimit=EMPTY_LIMIT,
                rule='A family passes with 0 outside labels and at most 10% empty labels among measurable labels.')
    summary = dict(gate=gate, families=families,
                   classes={name: {s: counts[s] for s in statuses} for name, counts in sorted(by_class.items())},
                   passingFamilies=sorted(n for n, v in families.items() if v['passes']),
                   failingFamilies=sorted(n for n, v in families.items() if not v['passes']))
    return summary, measured


def write_outputs(out, frames, settings, recipe_ref, build_ref, meta):
    rows, table, checks = assess(frames, settings, out / 'frames')
    manifest = dict(version='ios-native-capture-manifest-v1', schemaVersion='1.0', recipe=recipe_ref, build=build_ref,
                    groupRule=settings['groups'], rows=rows)
    q.save(out / 'manifest.json', manifest)
    report = summarize(rows, table, checks, settings, meta)
    report['bytes'] = sum(p.stat().st_size for p in (out / 'frames').iterdir())
    report['bodyChecks'], measured = body_summary(frames, rows, out / 'frames')
    q.save(out / 'bodies.json', dict(version='ios-rendered-bodies-v1', gate=report['bodyChecks']['gate'], frames=measured))
    q.save(out / 'benchmark_summary.json', report)
    names = ['manifest.json', 'benchmark_summary.json', 'bodies.json'] + \
        ['frames/' + p.name for p in sorted((out / 'frames').iterdir())]
    q.save(out / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=name, sha256=q.digest(out / name)) for name in names]))
    return report


def run():
    from template_adapters395 import document, resolve_inputs
    cfg = q.load(OUT.parents[2] / 'spec.json')['template']
    target, timeout = parameters(cfg['parameters'])
    refs = resolve_inputs(cfg, OUT)
    settings, frames = recipe(document(refs['recipe']))
    build_doc = document(refs['generator'])
    started = time.monotonic()
    meta = simulate(frames, build_doc, target, timeout, OUT)
    meta.update(recipe=refs['recipe'], generator=refs['generator'], sourcesMatchBuild=sources() == build_doc['sources'],
                seconds=round(time.monotonic() - started, 1))
    write_outputs(OUT, frames, settings, refs['recipe'], refs['generator'], meta)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    b = sub.add_parser('build', help='build-for-testing and write the pinned build receipt')
    b.add_argument('receipt', type=Path)
    p = sub.add_parser('preview', help='validate a recipe and print the frame list')
    p.add_argument('recipe', type=Path)
    args = parser.parse_args()
    if args.command == 'build':
        print(json.dumps(build(args.receipt), indent=2))
    else:
        settings, frames = recipe(q.load(args.recipe))
        print(json.dumps(dict(frames=len(frames), groups=len({f['group'] for f in frames}),
                              roles=dict(Counter(f['role'] for f in frames)), first=frames[:2]), indent=2))
