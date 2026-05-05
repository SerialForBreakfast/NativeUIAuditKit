"""
tests/test_confusion_matrix.py

Run with:
    pytest tests/test_confusion_matrix.py -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

# Make scripts/ importable regardless of working directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from confusion_matrix import (  # noqa: E402
    build_confusion_matrix,
    load_category_map,
    load_gt_annotations,
    per_class_metrics,
    vision_to_yolo,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tiny_category_map(tmp_path: Path) -> Path:
    """Write a minimal 3-class category_map.json and return its path."""
    data = {
        "version": "1.0",
        "categories": [
            {"id": 0, "name": "button", "supercategory": "controls"},
            {"id": 1, "name": "label",  "supercategory": "content"},
            {"id": 2, "name": "image",  "supercategory": "content"},
        ],
    }
    p = tmp_path / "category_map.json"
    p.write_text(json.dumps(data))
    return p


@pytest.fixture()
def gt_dir(tmp_path: Path) -> Path:
    """Create a gt directory with two annotation JSON files."""
    d = tmp_path / "annotations"
    d.mkdir()

    # File 1: two elements
    ann1 = {
        "elements": [
            {
                "elementType": "button",
                "boundsVisionNormalized": {"x": 0.1, "y": 0.1, "width": 0.2, "height": 0.1},
            },
            {
                "elementType": "label",
                "boundsVisionNormalized": {"x": 0.5, "y": 0.6, "width": 0.3, "height": 0.05},
            },
        ]
    }
    (d / "img001.json").write_text(json.dumps(ann1))

    # File 2: one element
    ann2 = {
        "elements": [
            {
                "elementType": "image",
                "boundsVisionNormalized": {"x": 0.2, "y": 0.3, "width": 0.4, "height": 0.2},
            },
        ]
    }
    (d / "img002.json").write_text(json.dumps(ann2))

    return d


def _make_pred_line(class_id: int, cx: float, cy: float, w: float, h: float, conf: float = 0.99) -> str:
    return f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f} {conf:.2f}"


def _vision_box_to_pred_line(class_id: int, x: float, y: float, w: float, h: float) -> str:
    cx, cy, bw, bh = vision_to_yolo(x, y, w, h)
    return _make_pred_line(class_id, cx, cy, bw, bh)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCoordinateConversion:
    def test_center_box(self) -> None:
        """A box centered in the image should remain centered after conversion."""
        x, y, w, h = 0.375, 0.375, 0.25, 0.25
        cx, cy, bw, bh = vision_to_yolo(x, y, w, h)
        assert abs(cx - 0.5) < 1e-9
        assert abs(cy - 0.5) < 1e-9
        assert abs(bw - 0.25) < 1e-9
        assert abs(bh - 0.25) < 1e-9

    def test_top_left_vision_maps_to_top_left_yolo(self) -> None:
        """Vision box at bottom-left corner should map to YOLO bottom-left."""
        # Vision: x=0, y=0 means left edge, bottom edge
        # After flip: YOLO cy should be near 1.0 (bottom of image)
        x, y, w, h = 0.0, 0.0, 0.1, 0.1
        cx, cy, bw, bh = vision_to_yolo(x, y, w, h)
        assert abs(cx - 0.05) < 1e-9
        # cy should be 0.95 (bottom-most)
        assert abs(cy - 0.95) < 1e-9

    def test_width_height_preserved(self) -> None:
        x, y, w, h = 0.3, 0.4, 0.15, 0.08
        cx, cy, bw, bh = vision_to_yolo(x, y, w, h)
        assert abs(bw - 0.15) < 1e-9
        assert abs(bh - 0.08) < 1e-9


class TestLoadGtAnnotations:
    def test_loads_all_elements(self, gt_dir: Path, tiny_category_map: Path) -> None:
        name_to_id, _ = load_category_map(tiny_category_map)
        gt = load_gt_annotations(gt_dir, name_to_id)
        assert "img001" in gt
        assert "img002" in gt
        assert len(gt["img001"]) == 2
        assert len(gt["img002"]) == 1

    def test_unknown_element_type_skipped(self, tmp_path: Path, tiny_category_map: Path) -> None:
        d = tmp_path / "ann"
        d.mkdir()
        ann = {"elements": [{"elementType": "unknownWidget", "boundsVisionNormalized": {"x": 0, "y": 0, "width": 0.1, "height": 0.1}}]}
        (d / "x.json").write_text(json.dumps(ann))
        name_to_id, _ = load_category_map(tiny_category_map)
        gt = load_gt_annotations(d, name_to_id)
        assert gt["x"] == []

    def test_empty_elements_array(self, tmp_path: Path, tiny_category_map: Path) -> None:
        d = tmp_path / "ann"
        d.mkdir()
        (d / "empty.json").write_text(json.dumps({"elements": []}))
        name_to_id, _ = load_category_map(tiny_category_map)
        gt = load_gt_annotations(d, name_to_id)
        assert gt["empty"] == []


class TestConfusionMatrixDiagonal:
    """A perfect prediction set should produce a diagonal confusion matrix."""

    def test_perfect_predictions_diagonal(
        self, tmp_path: Path, gt_dir: Path, tiny_category_map: Path
    ) -> None:
        name_to_id, id_to_name = load_category_map(tiny_category_map)
        num_classes = len(id_to_name)
        gt_by_stem = load_gt_annotations(gt_dir, name_to_id)

        # Build a pred_dir with exact copies of GT boxes
        pred_dir = tmp_path / "preds"
        pred_dir.mkdir()

        # img001: button at (0.1, 0.1, 0.2, 0.1) Vision; label at (0.5, 0.6, 0.3, 0.05) Vision
        lines_img001 = [
            _vision_box_to_pred_line(name_to_id["button"], 0.1, 0.1, 0.2, 0.1),
            _vision_box_to_pred_line(name_to_id["label"],  0.5, 0.6, 0.3, 0.05),
        ]
        (pred_dir / "img001.txt").write_text("\n".join(lines_img001))

        # img002: image at (0.2, 0.3, 0.4, 0.2) Vision
        lines_img002 = [
            _vision_box_to_pred_line(name_to_id["image"], 0.2, 0.3, 0.4, 0.2),
        ]
        (pred_dir / "img002.txt").write_text("\n".join(lines_img002))

        cm = build_confusion_matrix(gt_by_stem, pred_dir, num_classes, iou_threshold=0.5)

        # The diagonal (class x class) sub-matrix should have all TPs, no FP/FN
        class_cm = cm[:num_classes, :num_classes]
        off_diagonal = class_cm - np.diag(np.diag(class_cm))
        assert off_diagonal.sum() == 0, (
            f"Expected no off-diagonal entries, got:\n{class_cm}"
        )

        # Check specific TPs
        metrics = per_class_metrics(cm, num_classes)
        for m in metrics:
            if m["support"] > 0:
                assert m["precision"] == pytest.approx(1.0), (
                    f"Class {id_to_name[m['class_id']]} precision should be 1.0"
                )
                assert m["recall"] == pytest.approx(1.0), (
                    f"Class {id_to_name[m['class_id']]} recall should be 1.0"
                )


class TestMissingPredictionFiles:
    """Missing prediction files should be handled gracefully (zero predictions)."""

    def test_missing_pred_file_no_crash(
        self, tmp_path: Path, gt_dir: Path, tiny_category_map: Path
    ) -> None:
        name_to_id, id_to_name = load_category_map(tiny_category_map)
        num_classes = len(id_to_name)
        gt_by_stem = load_gt_annotations(gt_dir, name_to_id)

        # Empty pred dir — no prediction files exist
        pred_dir = tmp_path / "empty_preds"
        pred_dir.mkdir()

        # Should not raise
        cm = build_confusion_matrix(gt_by_stem, pred_dir, num_classes, iou_threshold=0.5)

        # All GT boxes are unmatched -> all should be in FN column
        fn_col = cm[:num_classes, num_classes]
        total_gt = sum(len(v) for v in gt_by_stem.values())
        assert fn_col.sum() == total_gt, (
            f"Expected {total_gt} FNs, got {fn_col.sum()}"
        )

    def test_partial_pred_coverage(
        self, tmp_path: Path, gt_dir: Path, tiny_category_map: Path
    ) -> None:
        """Only one of two GT files has a prediction file."""
        name_to_id, id_to_name = load_category_map(tiny_category_map)
        num_classes = len(id_to_name)
        gt_by_stem = load_gt_annotations(gt_dir, name_to_id)

        pred_dir = tmp_path / "partial_preds"
        pred_dir.mkdir()

        # Only predict for img002
        lines_img002 = [
            _vision_box_to_pred_line(name_to_id["image"], 0.2, 0.3, 0.4, 0.2),
        ]
        (pred_dir / "img002.txt").write_text("\n".join(lines_img002))

        cm = build_confusion_matrix(gt_by_stem, pred_dir, num_classes, iou_threshold=0.5)

        # img001 has 2 GT boxes, none predicted -> 2 FNs
        fn_total = cm[:num_classes, num_classes].sum()
        assert fn_total == 2


class TestCLIExitOnMissingGtDir:
    def test_exit_on_missing_gt_dir(self, tmp_path: Path, tiny_category_map: Path) -> None:
        from confusion_matrix import main

        args = [
            "--gt-dir", str(tmp_path / "nonexistent"),
            "--pred-dir", str(tmp_path / "preds"),
            "--category-map", str(tiny_category_map),
            "--version", "1",
        ]
        with pytest.raises(SystemExit) as exc_info:
            main(args)
        assert exc_info.value.code == 1
