"""Tests for `framework_projection604` against `tvos-framework-projection-v1` and the hand-written keys."""
import copy
import json
import unittest

import framework_projection604 as fp
import research_queue as q

KEYS = q.ROOT / 'reports/work/RESET604/contract/keys'


def obj(oid, framework=None, primitive=None, style=None, source='applied_instance', role=None, purpose=None,
        parent=None, relation=None, focusable=True, affordance=None, bounds=(10, 10, 110, 60), rev='r1', shot='s1'):
    c = dict(instance_id=oid, primitive=primitive, style=style, style_source=source, role=role, source='test')
    if framework:
        c['framework'] = framework
    if purpose:
        c['purpose'] = purpose
    o = dict(instance_id=oid, uikit_class='UIView', visible_bounds_px=list(bounds), focusable=focusable,
             scene_revision=rev, screenshot_sha256=shot)
    if affordance is not None:
        o['affordance_visible'] = affordance
    return dict(id=oid, construction=c, observation=o, parent_id=parent, owner_relation=relation)


def frame(*objects, focus=None):
    return dict(scene_revision='r1', screenshot_sha256='s1', width=1920, height=1080, objects=list(objects), focus=focus)


def one(o):
    return fp.project_frame(frame(o))['objects'][0]


class ProjectionRuleTests(unittest.TestCase):
    def test_class_order_is_10_roles_without_adjustable_or_container(self):
        classes = fp.tvos_classes()
        self.assertEqual(len(classes), 10)
        self.assertNotIn('adjustable', classes)
        self.assertNotIn('container', classes)
        contract = fp.load_contract()[0]
        self.assertTrue({r['class'] for r in contract['rules'] if r.get('class')} <= set(classes))
        self.assertEqual(len({r['rule_id'] for r in contract['rules']}), len(contract['rules']))

    def test_each_target_rule(self):
        cases = [
            (obj('a', 'UIKit', 'UIButton', 'borderedProminent'), 'button', 'button.uikit'),
            (obj('b', 'SwiftUI', 'Button', 'bordered'), 'button', 'button.swiftui'),
            (obj('c', 'SwiftUI', 'Button', 'card'), 'cell', 'cell.swiftui-card'),
            (obj('d', 'SwiftUI', 'Link'), 'button', 'button.link'),
            (obj('e', 'SwiftUI', 'Menu'), 'button', 'button.menu'),
            (obj('f', 'UIKit', 'UICollectionViewCell'), 'cell', 'cell.collection'),
            (obj('g', 'UIKit', 'UICollectionViewListCell'), 'cell', 'cell.collection'),
            (obj('h', 'UIKit', 'UITableViewCell'), 'cell', 'cell.table'),
            (obj('i', 'SwiftUI', 'ListRow'), 'cell', 'cell.list'),
            (obj('j', 'UIKit', 'UIImageView', focusable=False), 'picture', 'picture.image'),
            (obj('k', 'UIKit', 'UITextField'), 'textField', 'textField.input'),
            (obj('l', 'UIKit', 'UISearchBar', affordance=True), 'textField', 'textField.search'),
            (obj('m', 'SwiftUI', 'Toggle'), 'toggle', 'toggle.swiftui'),
            (obj('n', 'UIKit', 'UISegmentedControl'), 'segmentedControl', 'segmentedControl.uikit'),
            (obj('o', 'SwiftUI', 'Picker', 'segmented'), 'segmentedControl', 'segmentedControl.swiftui'),
            (obj('p', 'UIKit', 'UIPageControl'), 'pageControl', 'pageControl.uikit'),
            (obj('r', 'SwiftUI', 'TabView', 'page', affordance=True), 'pageControl', 'pageControl.page'),
            (obj('s', 'UIKit', 'UITabBar'), 'bar', 'bar.tab'),
            (obj('t', 'UIKit', 'UINavigationBar'), 'bar', 'bar.navigation'),
            (obj('u', 'UIKit', 'UIAlertController'), 'dialog', 'dialog.alert'),
            (obj('v', 'SwiftUI', 'sheet', affordance=True), 'dialog', 'dialog.sheet'),
            (obj('w', 'UIKit', 'UIProgressView', focusable=False), 'indicator', 'indicator.progress'),
        ]
        for o, cls, rule in cases:
            r = one(o)
            self.assertEqual((r['disposition'], r['class'], r['rule_id']), ('target', cls, rule), o['construction'])

    def test_card_exception_beats_generic_button_with_same_title_and_art(self):
        card = obj('x', 'SwiftUI', 'Button', 'card')
        plain = obj('x', 'SwiftUI', 'Button', 'bordered')
        self.assertEqual(one(card)['class'], 'cell')
        self.assertEqual(one(plain)['class'], 'button')
        declared_only = obj('x', 'SwiftUI', 'Button', 'card', source='declared_recipe')
        self.assertEqual(one(declared_only)['reason'], 'style_evidence_missing')
        self.assertEqual(one(obj('x', 'SwiftUI', 'Button', None))['reason'], 'style_evidence_missing')

    def test_out_of_scope_and_unresolved_reasons(self):
        self.assertEqual(one(obj('t', 'UIKit', 'UILabel', focusable=False))['disposition'], 'out_of_scope')
        self.assertEqual(one(obj('d', 'UIKit', 'UIView', purpose='decorative', focusable=False))['reason'], 'declared_decoration')
        self.assertEqual(one(obj('c', 'UIKit', 'UIControl'))['reason'], 'ttr_convention_not_admitted')
        self.assertEqual(one(obj('v', 'UIKit', 'UIView', focusable=False))['reason'], 'ttr_convention_not_admitted')
        self.assertEqual(one(obj('p', 'SwiftUI', 'Picker', 'menu'))['reason'], 'unprojected_framework_facts')
        self.assertEqual(one(obj('s', 'UIKit', 'UISearchBar', affordance=False))['reason'], 'affordance_hidden')
        self.assertEqual(one(obj('s', 'UIKit', 'UISearchBar'))['reason'], 'affordance_evidence_missing')
        missing = obj('m', 'UIKit', 'UIButton'); missing['construction'] = None
        self.assertEqual(one(missing)['reason'], 'framework_facts_missing')

    def test_ttr_a1_interpretations(self):
        # 1: owned means a parent_id exists (covered by test_ownership).
        # 2: a rule failing only on style evidence gives style_evidence_missing; a different known style does not.
        self.assertEqual(one(obj('p', 'SwiftUI', 'Picker', 'segmented', source='declared_recipe'))['reason'], 'style_evidence_missing')
        self.assertEqual(one(obj('p', 'SwiftUI', 'Picker', None))['reason'], 'style_evidence_missing')
        self.assertEqual(one(obj('p', 'SwiftUI', 'Picker', 'menu'))['reason'], 'unprojected_framework_facts')
        self.assertEqual(one(obj('t', 'SwiftUI', 'TabView', 'page', source='declared_recipe', affordance=True))['reason'], 'style_evidence_missing')
        # 3: button.swiftui admits a declared non-card style (v1.0 table has no style_source on that rule).
        self.assertEqual(one(obj('b', 'SwiftUI', 'Button', 'bordered', source='declared_recipe'))['rule_id'], 'button.swiftui')
        # 4: construction without observation -> join_mismatch; observation without construction -> framework_facts_missing.
        no_obs = obj('b', 'UIKit', 'UIButton', 'bordered'); no_obs['observation'] = None
        self.assertEqual(one(no_obs)['reason'], 'join_mismatch')
        no_con = obj('b', 'UIKit', 'UIButton', 'bordered'); no_con['construction'] = None
        self.assertEqual(one(no_con)['reason'], 'framework_facts_missing')
        # 5: an unresolved object stays unresolved under same_action ownership.
        card = obj('card', 'UIKit', 'UICollectionViewCell')
        custom_art = obj('art', 'UIKit', 'UIView', parent='card', relation='same_action', focusable=False)
        res = fp.project_frame(frame(card, custom_art))
        self.assertEqual(res['objects'][1]['disposition'], 'unresolved')
        self.assertFalse(res['eligible'])

    def test_canonical_ttr_frame_normalization(self):
        import ttr_detector_ingest604 as ingest
        o = obj('b', 'UIKit', 'UIButton', 'bordered')
        side = dict(schema='tvos-framework-frame-v1', status='settled', withheld_reasons=[],
                    frame=dict(scene_revision='r1', screenshot_sha256='s1', png_width=1920, png_height=1080),
                    focus=dict(state='focused', object_id='b', scene_revision='r1', screenshot_sha256='s1'),
                    objects=[dict(object=o, content_id='movie-0', reuse_generation=1)])
        flat, reasons = ingest.normalize_framework_frame(side)
        self.assertEqual(reasons, [])
        self.assertEqual(flat['objects'][0]['content_id'], 'movie-0')
        res = fp.project_frame(flat)
        self.assertEqual((res['focus_state'], res['focus_id'], res['targets'][0]['class']), ('focused', 'b', 'button'))
        stale = copy.deepcopy(side); stale['focus']['scene_revision'] = 'r0'
        self.assertIn('focus_identity_mismatch', ingest.normalize_framework_frame(stale)[1])
        for state in ('transition', 'unavailable'):
            moving = copy.deepcopy(side); moving['focus']['state'] = state
            self.assertEqual(ingest.normalize_framework_frame(moving)[0]['focus']['state'], 'unknown')
        withheld = copy.deepcopy(side); withheld['status'] = 'diagnostic_sequence'; withheld['withheld_reasons'] = ['before_after_disagree']
        self.assertEqual(sorted(ingest.normalize_framework_frame(withheld)[1]), ['frame_not_settled:diagnostic_sequence', 'withheld:before_after_disagree'])

    def test_covered_child_requires_consistent_native_geometry_and_focus(self):
        owner = obj('owner', 'UIKit', 'UIButton', bounds=(0, 0, 100, 50))
        owner['observation']['full_bounds_px'] = [0, 0, 200, 50]
        child = obj('trailing', 'UIKit', 'UIButton', parent='owner', relation='separate_action',
                    focusable=False, bounds=(0, 0, 0, 0))
        child['observation']['full_bounds_px'] = [100, 10, 180, 40]
        scene = frame(owner, child, focus={'state': 'focused', 'id': 'owner'})
        self.assertFalse(fp.project_frame(scene)['eligible'])
        projected = fp.project_frame(scene, diagnostic_covered_children=True)
        self.assertTrue(projected['eligible'])
        self.assertEqual(projected['objects'][1]['reason'], 'fully_covered_child')
        self.assertEqual([x['id'] for x in projected['targets']], ['owner'])
        self.assertEqual(projected['focus_id'], 'owner')

        for field, value in [('full_bounds_px', None), ('full_bounds_px', [99, 10, 180, 40]),
                             ('visible_bounds_px', [100, 10, 101, 40]),
                             ('visible_bounds_px', [1, 1, 0, 0]), ('instance_id', 'unrelated'),
                             ('screenshot_sha256', 'stale')]:
            with self.subTest(field=field, value=value):
                changed = copy.deepcopy(scene)
                changed['objects'][1]['observation'][field] = value
                self.assertFalse(fp.project_frame(changed, diagnostic_covered_children=True)['eligible'])
        scene['focus']['id'] = 'trailing'
        self.assertFalse(fp.project_frame(scene, diagnostic_covered_children=True)['eligible'])

    def test_fact_conflict_and_join_mismatch(self):
        self.assertEqual(one(obj('b', 'UIKit', 'UIButton', 'bordered', focusable=False))['reason'], 'fact_conflict')
        joined = obj('b', 'UIKit', 'UIButton', 'bordered'); joined['observation']['instance_id'] = 'other'
        self.assertEqual(one(joined)['reason'], 'join_mismatch')

    def test_conflicting_rules_are_rejected_not_first_match(self):
        contract = copy.deepcopy(fp.load_contract()[0])
        contract['rules'].append(dict(rule_id='test.dup', specificity=2, match=dict(framework='UIKit', primitive='UIButton'),
                                      disposition='target', **{'class': 'cell'}, box='interactive_body'))
        r = fp.project_frame(frame(obj('b', 'UIKit', 'UIButton', 'bordered')), contract)['objects'][0]
        self.assertEqual(r['reason'], 'conflicting_rules')
        self.assertIn('test.dup', r['rule_id'])

    def test_invariance_to_id_title_tint_locale_and_family(self):
        base = obj('action_watch', 'UIKit', 'UIButton', 'bordered')
        variants = []
        for oid in ('primaryButton_play', 'secondaryButton_x', 'collectionItem_key_a'):
            v = copy.deepcopy(base); v['id'] = oid; v['construction']['instance_id'] = oid; v['observation']['instance_id'] = oid
            variants.append(v)
        for extra in (dict(title='Delete'), dict(title='Löschen', locale='de'), dict(tint='red'), dict(family='plain:media_shelf'), dict(component_kind='card')):
            v = copy.deepcopy(base); v['construction'].update(extra); variants.append(v)
        for v in variants:
            self.assertEqual((one(v)['class'], one(v)['rule_id']), ('button', 'button.uikit'), v)

    def test_ownership(self):
        card = obj('card', 'UIKit', 'UICollectionViewCell')
        art = obj('art', 'UIKit', 'UIImageView', parent='card', relation='same_action', focusable=False)
        title = obj('title', 'UIKit', 'UILabel', parent='card', relation='same_action', focusable=False)
        child_action = obj('more', 'UIKit', 'UIButton', 'plain', parent='card', relation='separate_action')
        res = fp.project_frame(frame(card, art, title, child_action))
        d = {r['id']: (r['disposition'], r['class']) for r in res['objects']}
        self.assertEqual(d, {'card': ('target', 'cell'), 'art': ('owned_metadata', None), 'title': ('owned_metadata', None), 'more': ('target', 'button')})
        self.assertTrue(res['eligible'])
        orphan = obj('art', 'UIKit', 'UIImageView', parent='nowhere', relation='same_action', focusable=False)
        self.assertEqual(fp.project_frame(frame(orphan))['objects'][0]['reason'], 'missing_parent')
        norel = obj('art', 'UIKit', 'UIImageView', parent='card', focusable=False)
        self.assertEqual(fp.project_frame(frame(card, norel))['objects'][1]['reason'], 'ownership_relation_missing')

    def test_tab_item_focus_names_item_not_bar(self):
        bar = obj('tabs', 'UIKit', 'UITabBar', focusable=False)
        item = obj('tab_home', 'UIKit', 'UITabBarItem', parent='tabs', relation='same_action')
        res = fp.project_frame(frame(bar, item, focus=dict(state='focused', id='tab_home')))
        self.assertEqual(res['focus_state'], 'focused')
        self.assertEqual(res['focus_id'], 'tab_home')
        self.assertEqual([t['id'] for t in res['targets']], ['tabs'])

    def test_frame_identity_and_focus_evidence(self):
        stale = obj('b', 'UIKit', 'UIButton', 'bordered', rev='r0')
        res = fp.project_frame(frame(stale))
        self.assertFalse(res['eligible'])
        self.assertEqual(res['objects'][0]['reason'], 'frame_identity_mismatch')
        empty = fp.project_frame(frame(obj('b', 'UIKit', 'UIButton', 'bordered'), focus=dict(state='known_no_focus', source='empty_registry')))
        self.assertEqual(empty['focus_state'], 'unknown')
        text_focus = fp.project_frame(frame(obj('t', 'UIKit', 'UILabel', focusable=False), focus=dict(state='focused', id='t')))
        self.assertEqual(text_focus['focus_state'], 'unknown')

    def test_hand_written_keys_project_as_expected(self):
        for path in sorted(KEYS.glob('q*.json')):
            key = json.loads(path.read_text())
            objects = []
            for i, k in enumerate(key['objects']):
                c = dict(k['construction'], instance_id=k['id'], source='key')
                focusable = c['primitive'] not in ('UILabel', 'Text', 'UIImageView', 'Image', 'UIAlertController', 'UIView')
                objects.append(dict(id=k['id'], construction=c, parent_id=k.get('parent_id'), owner_relation=k.get('owner_relation'),
                                    observation=dict(instance_id=k['id'], uikit_class='UIView', visible_bounds_px=[10 + 50 * i, 10, 50 + 50 * i, 40],
                                                     focusable=focusable, scene_revision='r1', screenshot_sha256='s1')))
            res = fp.project_frame(frame(*objects))
            for k, r in zip(key['objects'], res['objects']):
                exp = k['expected']
                self.assertEqual(r['disposition'], exp['disposition'], (path.name, k['id']))
                if 'class' in exp:
                    self.assertEqual(r['class'], exp['class'], (path.name, k['id']))
                if 'rule_id' in exp:
                    self.assertEqual(r['rule_id'], exp['rule_id'], (path.name, k['id']))
                if 'reason' in exp:
                    self.assertEqual(r['reason'], exp['reason'], (path.name, k['id']))
                self.assertEqual(r['attributes']['role'], k['construction'].get('role'))
            counts = key['count_assertions']
            self.assertEqual(len(res['targets']), counts['targets'], path.name)
            self.assertEqual(sum(r['disposition'] == 'unresolved' for r in res['objects']), counts['unresolved'], path.name)
            if 'targets_with_role' in counts:
                self.assertEqual(sum(t['attributes']['role'] is not None for t in res['targets']), counts['targets_with_role'], path.name)


if __name__ == '__main__':
    unittest.main()
