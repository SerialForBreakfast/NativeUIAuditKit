from copy import deepcopy
import unittest

from perception_benchmark import BenchmarkError, inventory, recommendation, validate_manifest
from test_perception_benchmark import case


def native_case():
    value = case(source="reviewedNativeCapture")
    value.update(trainingEligible=False, sourceIdentityStatus="unverified",
        journeyEvidence="unknown-conservatively-grouped", privacyReview="local-review-cleared", reviewer="test reviewer")
    value["labels"]["focus"]["basis"] = "visualAppearanceOnly"
    return value


class NativeReviewTests(unittest.TestCase):
    def validate(self, value):
        return validate_manifest({"formatVersion": "perception-benchmark-v1", "cases": [value]})

    def test_development_only_and_visual_focus(self):
        cases = self.validate(native_case())
        self.assertEqual(inventory(cases)["coverage"]["focus:reviewedAppearance"], 1)
        self.assertNotIn("focus:observed", inventory(cases)["coverage"])
        self.assertEqual(recommendation(cases, {"status": "available"})["action"], "no_training")

    def test_rejects_false_eligibility_and_provenance(self):
        for key, value in (("partition", "test"), ("trainingEligible", True),
                           ("sourceIdentityStatus", "verified"), ("privacyReview", "pending"),
                           ("journeyEvidence", "known"), ("reviewer", "")):
            with self.subTest(key=key):
                item = native_case(); item[key] = value
                with self.assertRaisesRegex(BenchmarkError, "native_review_not_development_eligible"): self.validate(item)

    def test_missing_or_malformed_focus_basis(self):
        for focus in ([], "nativeCallback", {"elementID": "cancel", "frameID": "c1", "basis": "nativeCallback"}):
            item = native_case(); item["labels"]["focus"] = focus
            with self.assertRaisesRegex(BenchmarkError, "unsupported_native_focus_claim"): self.validate(item)

    def test_missing_modalities_are_not_absence(self):
        for key in ("chevrons", "dialog"):
            item = native_case(); del item["labels"][key]
            with self.assertRaisesRegex(BenchmarkError, "incomplete_review_modalities"): self.validate(item)

    def test_unknown_relation_not_gold(self):
        item = native_case(); item["labels"]["chevrons"][0]["rowID"] = "unknown"
        with self.assertRaisesRegex(BenchmarkError, "ambiguous_chevron_relation"): self.validate(item)

    def test_cannot_reclassify_visual_labels_as_fixture_truth(self):
        item = native_case(); item["labels"]["origin"] = "fixtureGroundTruth"
        with self.assertRaisesRegex(BenchmarkError, "native_review_not_development_eligible"): self.validate(item)
