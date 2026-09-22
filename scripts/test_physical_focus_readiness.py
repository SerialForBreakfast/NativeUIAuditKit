import unittest

from physical_focus_readiness import PhysicalReadinessError, validate


def pair(**changes):
    value = {
        "pairID": "p1", "sourceKind": "physicalFixture", "source": {"producerRevision": "abc123", "captureID": "capture-1", "frameID": "frame-1", "imageSHA256": "a" * 64},
        "focusLabelOrigin": "fixtureCallback", "focusFrameID": "frame-1", "focusedCrop": "crops/p1-focused.png", "unfocusedCrop": "crops/p1-unfocused.png",
        "cropSize": [256, 256], "expansion": .16, "recipeGroup": "mediaShelf-101", "partition": "development",
        "scene": "mediaShelf", "theme": "highContrast", "control": "collectionItem", "hardNegative": True, "unfocusedEvidence": {"sha256": "b" * 64},
    }
    value.update(changes); return value


class PhysicalReadinessTests(unittest.TestCase):
    def test_empty_and_metadata_only_never_establish_eligibility(self):
        self.assertEqual(validate({"formatVersion": "focus-ring-physical-readiness-v1", "pairs": []})["reason"], "no_physical_pairs")
        report = validate({"formatVersion": "focus-ring-physical-readiness-v1", "pairs": [pair()]})
        self.assertFalse(report["eligible"])
        self.assertTrue(report["metadataValid"])
        self.assertFalse(report["integrityVerified"])
        self.assertEqual(report["coverage"]["mediaShelf/highContrast/collectionItem"], 1)

    def test_rejects_false_source_stale_callback_and_crop_drift(self):
        for changes, error in (({"sourceKind": "simulatorFixture"}, "false_or_missing_physical_source"), ({"focusFrameID": "old"}, "stale_or_untrusted_focus_label"), ({"expansion": .15}, "crop_parity_mismatch")):
            with self.subTest(error=error), self.assertRaisesRegex(PhysicalReadinessError, error):
                validate({"formatVersion": "focus-ring-physical-readiness-v1", "pairs": [pair(**changes)]})

    def test_rejects_nonhex_hash(self):
        p=pair(); p["source"]["imageSHA256"]="z"*64
        with self.assertRaisesRegex(PhysicalReadinessError,"invalid_source_hash"):
            validate({"formatVersion":"focus-ring-physical-readiness-v1","pairs":[p]})

    def test_rejects_recipe_group_leakage_and_unsupported_hard_negative(self):
        conflicting = pair(pairID="p2", partition="test")
        with self.assertRaisesRegex(PhysicalReadinessError, "recipe_group_leakage"):
            validate({"formatVersion": "focus-ring-physical-readiness-v1", "pairs": [pair(), conflicting]})
        with self.assertRaisesRegex(PhysicalReadinessError, "missing_hard_negative_evidence"):
            validate({"formatVersion": "focus-ring-physical-readiness-v1", "pairs": [pair(unfocusedEvidence=None)]})


if __name__ == "__main__": unittest.main()
