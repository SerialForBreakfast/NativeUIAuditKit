"""Project the audited native UIKitForm recipe onto the common detector roles."""
from pathlib import Path

import research_queue as q

SOURCE = Path("NativeUIDatasetGenerator/Templates/UIKitFormViewController.swift")
SOURCE_SHA = "abfd8d29447af5de31de5d17df77cd3261775b7ba3cffd2c6e8fa0d932d66c84"
# Keys follow the actual constructor and annotated view in the pinned template.
FORM = {
    "textField": ("textField", "textField"), "secureField": ("secureField", "textField"),
    "primaryButton": ("primaryButton", "button"), "secondaryButton": ("secondaryButton", "button"),
    "navigationBar": ("navigationBar", "bar"), "label_email": ("label", None),
    "label_password": ("label", None),
}


def project(side, png, receipt):
    q.require(q.digest(q.ROOT / SOURCE) == SOURCE_SHA, "form_source_changed")
    q.require(side["generatorProfile"]["templateFamily"] == "UIKitForm" and
              side["image"]["platform"] == "iOS", "form_scope")
    q.require(png.stem == receipt["id"] and side["image"]["fileName"] == png.name and
              q.digest(png) == receipt["imageSHA256"] == side["imageSHA256"] and
              q.digest(png.with_suffix(".json")) == receipt["sidecarSHA256"], "form_binding")
    elements = side["elements"]
    q.require(len(elements) == len(FORM) and {e["id"] for e in elements} == set(FORM), "form_inventory")
    controls = []
    for elem in elements:
        legacy, role = FORM[elem["id"]]
        q.require(elem["framework"] == "UIKit" and elem["elementType"] == legacy, "form_role")
        q.require(not (elem["excluded"] or elem["occluded"] or elem["knownIssues"]), "form_visibility")
        if role:
            box = [elem["boundsPixels"][k] for k in ("x", "y", "width", "height")]
            x, y, w, h = box
            q.require(w > 0 and h > 0 and x >= 0 and y >= 0 and
                      x+w <= side["image"]["pixelWidth"] and y+h <= side["image"]["pixelHeight"], "form_box")
            controls.append({"id": elem["id"], "class": role, "bounds": box, "sourceClass": legacy})
    return controls
