"""TRAIN666 H3 arm S: drop focus candidates that lie inside a larger focus candidate.

On the reviewed Settings screens, 22 of 26 comparative wrong picks were a small box (often a false `toggle` on a
chevron) inside the focused row. The small box inherits the row's focus highlight, so its rim features look focused.
tvOS moves focus to the outer focusable element, so a nested candidate is removed before scoring.
Rule: remove candidate i if another candidate j has area_j >= AREA_RATIO * area_i and covers at least
CONTAINMENT of candidate i's area. Non-focusable detections are kept unchanged.
"""

CONTAINMENT = 0.9
AREA_RATIO = 2.0


def _area(b):
    return max(b[2], 0.0) * max(b[3], 0.0)


def covered(inner, outer):
    """Fraction of `inner` [x, y, w, h] that lies inside `outer`."""
    ix = max(0.0, min(inner[0] + inner[2], outer[0] + outer[2]) - max(inner[0], outer[0]))
    iy = max(0.0, min(inner[1] + inner[3], outer[1] + outer[3]) - max(inner[1], outer[1]))
    return ix * iy / max(_area(inner), 1e-6)


def drop_nested(detections, is_focusable):
    """Return (kept detections in input order, removed detections). `is_focusable(det) -> bool`."""
    focus = [d for d in detections if is_focusable(d)]
    removed = []
    for d in focus:
        a = _area(d['box'])
        if any(o is not d and _area(o['box']) >= AREA_RATIO * a and covered(d['box'], o['box']) >= CONTAINMENT for o in focus):
            removed.append(d)
    ids = {id(d) for d in removed}
    return [d for d in detections if id(d) not in ids], removed
