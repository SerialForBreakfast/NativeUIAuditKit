"""Validate and project the two construction-instrumented iOS forms."""
from collections import Counter
from PIL import Image
import research_queue as q

RULES = {
    ("UIKit", "UIButton"): "button", ("SwiftUI", "Button"): "button",
    ("UIKit", "UITextField"): "textField", ("SwiftUI", "TextField"): "textField",
    ("SwiftUI", "SecureField"): "textField", ("UIKit", "UINavigationBar"): "bar",
    ("UIKit", "UILabel"): "text", ("SwiftUI", "Text"): "text",
}
FAMILIES = {"UIKitForm": "UIKit", "SwiftUIForm607": "SwiftUI"}


def project(doc, png):
    q.require(doc.get("version") == "ios-form-facts-1" and doc.get("family") in FAMILIES, "form_schema")
    q.require(doc["image"] == q.digest(png) and doc.get("scene"), "frame_identity")
    with Image.open(png) as im:
        width, height = im.size
    q.require([width, height] == [doc["width"], doc["height"]], "frame_size")
    objects = doc["objects"]
    by_id = {o["id"]: o for o in objects}
    q.require(len(by_id) == len(objects) and all(isinstance(i, str) and i for i in by_id), "duplicate_identity")
    result = []
    for o in objects:
        q.require((o["image"], o["scene"]) == (doc["image"], doc["scene"]), "observation_identity")
        framework, primitive = o["framework"], o["primitive"]
        role = RULES.get((framework, primitive))
        q.require(role and (role == "bar" or framework == FAMILIES[doc["family"]]), "unknown_construction")
        secure = o["secure"]
        q.require(type(secure) is bool and (not secure or role == "textField") and
                  (framework != "SwiftUI" or secure == (primitive == "SecureField")), "secure_conflict")
        x, y, right, bottom = o["edges"]
        q.require(all(type(v) is int for v in o["edges"]) and 0 <= x < right <= width
                  and 0 <= y < bottom <= height, "body_geometry")
        owner = o["owner"]
        if owner is not None:
            parent = by_id.get(owner)
            q.require(role == "text" and parent and RULES.get((parent["framework"], parent["primitive"])) == "button",
                      "invalid_owner")
            l, t, r, b = parent["edges"]
            q.require(l <= x and t <= y and right <= r and bottom <= b, "owner_geometry")
        disposition = ("owned_metadata" if owner else "out_of_scope") if role == "text" else "target"
        result.append(dict(id=o["id"], rule_id=f"{framework}.{primitive}", disposition=disposition,
                           parent_id=owner, secure=secure, bounds=[x,y,right-x,bottom-y],
                           **{"class": role if disposition == "target" else None}))
    targets = [o for o in result if o["disposition"] == "target"]
    q.require(Counter(o["class"] for o in targets) == {"button":2,"bar":1,"textField":2}
              and sum(o["secure"] for o in targets)==1, "target_inventory")
    q.require(Counter(o["parent_id"] for o in result if o["disposition"]=="owned_metadata")
              == Counter(o["id"] for o in targets if o["class"]=="button"), "caption_inventory")
    q.require(sum(o["disposition"]=="out_of_scope" for o in result)==2, "static_inventory")
    return result
