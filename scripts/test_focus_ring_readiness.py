import unittest
import json
from unittest.mock import patch

from focus_ring_readiness import ReadinessError, REQUIRED_ALIGNMENT_CASES, validate
from validate_focus_ring_readiness import main as readiness_main, normalize_pair


MIN = {
    "gridMatrix": 2000,
    "mediaShelf": 1500,
    "settingsList": 1000,
    "actionDialog": 500,
    "heroCarousel": 500,
    "focusMaze": 500,
}


def alignment(mode, relation, navigation, voice_over, source="fixtureGroundTruth"):
    value = {
        "version": "1.0",
        "interactionMode": mode,
        "expectedRelation": relation,
        "navigationFocusElementID": navigation,
        "voiceOverFocusElementID": voice_over,
    }
    if source is not None:
        value["source"] = source
    return value


def rows(with_matrix=True):
    out = []
    n = 0
    for scene, count in MIN.items():
        for i in range(count):
            theme = ("light", "highContrast")[i % 2] if scene in ("gridMatrix", "mediaShelf") else "light"
            hard = scene == "gridMatrix" and i < 100
            if hard:
                theme = ("light", "highContrast")[(i // 2) % 2]
            out.append(
                {
                    "focused": f"f{n}",
                    "unfocused": f"u{n}",
                    "labelSource": "fixtureGroundTruth",
                    "seed": f"{scene}-{i}",
                    "scene": scene,
                    "theme": theme,
                    "class": "imageView" if i % 2 else "collectionItem",
                    "hardNegative": hard,
                }
            )
            n += 1
    if with_matrix:
        out[0]["alignment"] = alignment("directionalNavigation", "aligned", "A", "A")
        out[1]["alignment"] = alignment("voiceOverExploration", "expectedDecoupled", "A", "B")
        out[2]["alignment"] = alignment("voiceOverTraversal", "expectedDecoupled", "A", "B")
        out[3]["alignment"] = alignment("directionalNavigation", "unexpectedMismatch", "A", "B")
        out[4]["alignment"] = alignment("unknown", "notAssessable", "A", None, None)
    return out


class Tests(unittest.TestCase):
    def test_valid_matrix(self):
        report = validate(rows(), require_alignment_matrix=True)
        self.assertEqual(report["pairs"], 6000)
        self.assertEqual(set(report["alignmentCaseCounts"]), REQUIRED_ALIGNMENT_CASES)

    def test_pair_seed_and_quota_rejections(self):
        data = rows()
        data[0]["focused"] = ""
        with self.assertRaisesRegex(ReadinessError, "invalid_pair"):
            validate(data)
        data = rows()
        data[1]["seed"] = data[0]["seed"]
        with self.assertRaisesRegex(ReadinessError, "seed_leakage"):
            validate(data)
        data = [row for row in rows() if row["scene"] != "focusMaze"]
        with self.assertRaisesRegex(ReadinessError, "underfilled_quota"):
            validate(data)

    def test_hard_negative_strata_rejection(self):
        data = rows()
        for row in data:
            row["hardNegative"] = False
        with self.assertRaisesRegex(ReadinessError, "empty_hard_negative_stratum"):
            validate(data)

    def test_alignment_requires_source_backed_known_target(self):
        data = rows()
        data[1]["alignment"].pop("source")
        with self.assertRaisesRegex(ReadinessError, "untrusted_alignment_source"):
            validate(data, require_alignment_matrix=True)
        data = rows()
        data[1]["alignment"]["version"] = "2.0"
        with self.assertRaisesRegex(ReadinessError, "unsupported_alignment_version"):
            validate(data, require_alignment_matrix=True)
        data = rows()
        data[1]["alignment"]["voiceOverFocusElementID"] = None
        with self.assertRaisesRegex(ReadinessError, "missing_alignment_target"):
            validate(data, require_alignment_matrix=True)
        data = rows()
        data[2]["alignment"]["voiceOverFocusElementID"] = "A"
        with self.assertRaisesRegex(ReadinessError, "invalid_alignment_relationship"):
            validate(data, require_alignment_matrix=True)

    def test_alignment_matrix_and_not_assessable_rejections(self):
        with self.assertRaisesRegex(ReadinessError, "missing_alignment_case"):
            validate(rows(with_matrix=False), require_alignment_matrix=True)
        data = rows()
        data[4]["alignment"]["source"] = "fixtureGroundTruth"
        with self.assertRaisesRegex(ReadinessError, "invalid_not_assessable_alignment"):
            validate(data, require_alignment_matrix=True)

    def test_manifest_cli_normalizes_real_pair_shape(self):
        pair = {
            "focused_crop": "crops/focused.png",
            "unfocused_crop": "crops/unfocused.png",
            "recipe_seed": 123,
            "fixture_scene": "gridMatrix",
            "theme": "light",
            "element_type": "collectionItem",
        }
        normalized = normalize_pair(pair)
        self.assertEqual(normalized["focused"], "crops/focused.png")
        self.assertEqual(normalized["seed"], "123")

        manifest = {
            "pairs": [
                {
                    "focused_crop": row["focused"],
                    "unfocused_crop": row["unfocused"],
                    "labelSource": row["labelSource"],
                    "recipe_seed": row["seed"],
                    "fixture_scene": row["scene"],
                    "theme": row["theme"],
                    "element_type": row["class"],
                    "hardNegative": row["hardNegative"],
                    **({"alignment": row["alignment"]} if "alignment" in row else {}),
                }
                for row in rows()
            ]
        }
        with patch("validate_focus_ring_readiness.Path.is_file", return_value=True), patch(
            "validate_focus_ring_readiness.Path.read_text", return_value=json.dumps(manifest)
        ), patch(
            "sys.argv",
            ["validate_focus_ring_readiness.py", "--manifest", "prospective.json", "--require-alignment-matrix"],
        ):
            self.assertEqual(readiness_main(), 0)
        with patch("validate_focus_ring_readiness.Path.is_file", return_value=False), patch(
            "sys.argv", ["validate_focus_ring_readiness.py", "--manifest", "missing.json"]
        ):
            self.assertEqual(readiness_main(), 2)


if __name__ == "__main__":
    unittest.main()
