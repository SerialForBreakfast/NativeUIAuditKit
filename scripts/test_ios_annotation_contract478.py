import unittest
import ios_annotation_contract478 as worker


def element(ident, kind):
    return dict(id=ident, elementType=kind, excluded=False)


class AnnotationContractTests(unittest.TestCase):
    def controls(self):
        return [element(k, v) for k, v in worker.CONTROL_TYPES.items()] + [
            element(k, "label") for k in worker.CONTROL_LABELS]

    def toggles(self):
        return [element("navigationBar", "navigationBar"), element("ctaButton", "primaryButton")] + [
            element(f"toggle_{i}", "toggle") for i in range(4)] + [
            element(f"rowLabel_{i}", "label") for i in range(4)] + [
            element(f"sectionHeader_{i}", "label") for i in range(2)]

    def test_two_families_use_same_contract(self):
        self.assertEqual(worker.completeness("UIKitControls", self.controls()), [])
        self.assertEqual(worker.completeness("UIKitToggleForm", self.toggles()), [])

    def test_missing_standalone_labels_fail(self):
        for family, rows in [("UIKitControls", self.controls()), ("UIKitToggleForm", self.toggles())]:
            findings = worker.completeness(family, [r for r in rows if r["elementType"] != "label"])
            self.assertGreater(len(findings), 0)
            self.assertTrue(all(r["expected"] == "label" for r in findings))

    def test_wrong_class_fails(self):
        rows = self.controls()
        rows[-1]["elementType"] = "textField"
        self.assertEqual(worker.completeness("UIKitControls", rows)[0]["actual"], "textField")

    def test_duplicate_and_unknown_family_fail(self):
        with self.assertRaisesRegex(ValueError, "duplicate_id"):
            worker.completeness("UIKitControls", self.controls() * 2)
        with self.assertRaisesRegex(ValueError, "family"):
            worker.completeness("Unknown", [])

    def test_excluded_label_does_not_satisfy_contract(self):
        rows = self.controls()
        rows[-1]["excluded"] = True
        self.assertEqual(len(worker.completeness("UIKitControls", rows)), 1)

    def test_gap_in_toggle_ids_fails(self):
        rows = self.toggles()
        rows[2]["id"] = "toggle_99"
        with self.assertRaisesRegex(ValueError, "toggle_identity"):
            worker.completeness("UIKitToggleForm", rows)


if __name__ == "__main__":
    unittest.main()
