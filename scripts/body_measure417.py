"""Rendered-body rule v2 for T46 (ACTIONS417). Rule v1 stays the frozen B405-032 gate in ios_native_capture_t46.py.

Rule v1 takes the bounding box of every foreground pixel in the window (the box plus 3 pt). A separator, a divider,
a scroll indicator, or a neighbour label that only enters the window then counts as body.
Rule v2 keeps the v1 window, ring, background, uniformity, and foreground thresholds. It changes 2 things:

1. A window pixel outside the box is ignored if it lies inside the box of another admitted label that neither
   contains nor is contained by this box. That pixel belongs to a sibling or to content under an overlay.
2. The body is the union of 8-connected foreground components that touch the box interior, plus components within
   GAP points of that union (for example the next glyph of a word). A component that never comes near the box
   interior is a neighbour.

A body that extends past its box (for example a switch drawn 2 pt wider than its frame) still fails, because that
component touches the box interior. The rule was fixed before any v2 result was read.
"""
import numpy as np

GAP = 2  # points


def _components(mask):
    """Label 8-connected components. Return (labels, count). Pure numpy flood fill on small windows."""
    labels = np.zeros(mask.shape, np.int32)
    count = 0
    height, width = mask.shape
    ys, xs = np.nonzero(mask)
    for y, x in zip(ys, xs):
        if labels[y, x]:
            continue
        count += 1
        stack = [(y, x)]
        labels[y, x] = count
        while stack:
            cy, cx = stack.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] and not labels[ny, nx]:
                        labels[ny, nx] = count
                        stack.append((ny, nx))
    return labels, count


def _dilate(mask, radius):
    out = mask.copy()
    for _ in range(radius):
        grown = out.copy()
        grown[1:, :] |= out[:-1, :]
        grown[:-1, :] |= out[1:, :]
        grown[:, 1:] |= out[:, :-1]
        grown[:, :-1] |= out[:, 1:]
        out = grown
    return out


def body_v2(mask, inside, ignored, scale):
    """Return the body bounding box [x0, y0, x1, y1] in window pixels, or None if no component touches the box.

    mask: foreground pixels of the window. inside: the box interior. ignored: pixels to drop (outside the box only).
    """
    mask = mask & ~(ignored & ~inside)
    labels, count = _components(mask)
    if not count:
        return None
    keep = set(np.unique(labels[inside & mask])) - {0}
    if not keep:
        return None
    radius = max(1, int(round(GAP * scale)))
    while True:
        near = _dilate(np.isin(labels, list(keep)), radius)
        found = set(np.unique(labels[near & mask])) - {0}
        if found <= keep:
            break
        keep |= found
    ys, xs = np.nonzero(np.isin(labels, list(keep)))
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def contains(a, b):
    """True if pixel box a = [x0, y0, x1, y1] contains b."""
    return a[0] <= b[0] and a[1] <= b[1] and a[2] >= b[2] and a[3] >= b[3]


def sibling_mask(box, others, window):
    """Pixels of the window inside an overlapping or adjacent box that is not nested with box."""
    wx0, wy0, wx1, wy1 = window
    out = np.zeros((wy1 - wy0, wx1 - wx0), bool)
    for other in others:
        if other == box or contains(other, box) or contains(box, other):
            continue
        x0, y0 = max(wx0, other[0]), max(wy0, other[1])
        x1, y1 = min(wx1, other[2]), min(wy1, other[3])
        if x1 > x0 and y1 > y0:
            out[y0 - wy0:y1 - wy0, x0 - wx0:x1 - wx0] = True
    return out
