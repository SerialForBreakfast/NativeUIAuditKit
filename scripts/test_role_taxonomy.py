"""Offline tests: taxonomy 1.2 role map is append-only, matches roles559 and reproduces the Swift identity."""
import hashlib
import json
import re
import sys
import unittest
from pathlib import Path

R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R / 'scripts'))
from roles559 import ROLES  # noqa: E402

S = R / 'Research/schemas'


def identity(version, categories):
    doc = {'version': version, 'categories': categories}
    return hashlib.sha256(json.dumps(doc, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()).hexdigest()


class RoleTaxonomyTests(unittest.TestCase):
    def setUp(self):
        self.base = json.loads((S / 'category_map.json').read_text())['categories']
        self.v11 = json.loads((S / 'category_map.v1.1.json').read_text())['append']
        self.v12 = json.loads((S / 'category_map.v1.2.json').read_text())

    def test_append_only_ids(self):
        self.assertEqual(self.v12['extends'], 'category_map.v1.1.json')
        self.assertEqual([c['id'] for c in self.v12['append']], list(range(42, 50)))

    def test_roles_are_roles559_without_legacy_raw_values(self):
        legacy = {c['name'] for c in self.base + self.v11}
        self.assertEqual([c['name'] for c in self.v12['append']], [r for r in ROLES if r not in legacy])

    def test_swift_identity_and_label_list_match(self):
        swift = (R / 'NativeUIAuditKitModels/Sources/NativeUIModelContracts/ModelTaxonomyBinding.swift').read_text()
        digest = re.search(r'case "1\.2": return "([0-9a-f]{64})"', swift).group(1)
        self.assertEqual(digest, identity('1.2', self.base + self.v11 + self.v12['append']))
        labels = re.search(r'roleLabels: \[String\] = \[(.*?)\]', swift, re.S).group(1)
        self.assertEqual(re.findall(r'"(\w+)"', labels), [c['name'] for c in self.v12['append']])


if __name__ == '__main__':
    unittest.main()
