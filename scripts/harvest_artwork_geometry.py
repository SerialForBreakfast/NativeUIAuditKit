"""Pinned FixtureArtworkGeometry v1; nominal layout, never native effect bounds."""
import math

ROLE = "artwork_layout_view_bounds"
STATUS = "unavailable_native_effect_not_measured"


def validate(value, size, require):
    # Swift's optional decodeIfPresent accepts absent and explicit null alike.
    if value is None:
        return
    required = {"version", "source", "presentation_bounds_status"}
    allowed = required | {"pixel_bounds", "normalized_bounds", "unavailable_reason"}
    require(isinstance(value, dict) and required <= set(value) <= allowed,
            "artwork_geometry_fields")
    require(type(value["version"]) is int and value["version"] == 1
            and value["source"] == ROLE and value["presentation_bounds_status"] == STATUS,
            "artwork_geometry_protocol")
    p, n, reason = (value.get(k) for k in
                    ("pixel_bounds", "normalized_bounds", "unavailable_reason"))
    if reason is not None:
        require(reason in ("not_rendered", "clipped", "projection_failed")
                and p is None and n is None, "artwork_geometry_unavailable_conflict")
        return
    require(isinstance(p, list) and isinstance(n, list) and len(p) == len(n) == 4
            and all(type(x) in (int, float) and math.isfinite(x) for x in p+n),
            "artwork_geometry_bounds")
    x, y, w, h = p
    require(x >= 0 and y >= 0 and w > 0 and h > 0 and x+w <= size[0] and y+h <= size[1]
            and 0 <= n[0] < n[2] <= 1 and 0 <= n[1] < n[3] <= 1,
            "artwork_geometry_bounds")
    projected = [n[0]*size[0], n[1]*size[1], (n[2]-n[0])*size[0], (n[3]-n[1])*size[1]]
    require(all(abs(a-b) <= 1 for a, b in zip(p, projected)), "artwork_geometry_coordinate_conflict")
