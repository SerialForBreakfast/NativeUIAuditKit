# Focus-review roles v1 (diagnostic only)

2026-09-28 maintainer-approved annotation unblock. Detector taxonomy remains the
unchanged 41-class category map. Local editor choices `focus:tabItem` and
`focus:otherFocusable` encode focus-only roles, never new detector class IDs.
The first is an individual tab/navigation destination (including an icon-only tab
such as App Store Search). The fallback is a visibly focusable control without an
accurate existing detector class; an optional note helps later taxonomy review.
Existing detector choices remain unchanged. Do not label containers as focusable
merely because they contain a focused child.

New controls serialize `class: null`, `focusRole: tabItem|otherFocusable` and
`roleSchema: human-focus-roles-v1`. The editor label is only a convenient selector;
the revision stores the role separately from detector class. Revisions containing
these roles use `human-review-revision-v2`; all-legacy revisions remain byte-shape
compatible v1. Diagnostic consumers validate both; unrecognized versions fail.
Presets containing these labels use rectangle-preset-v2 and bind roleSchema.
Legacy presets remain supported. No automatic label migration or guessed mapping.

Finish review, complete-frame checks, diagnostic coverage, audit and production
crop QA support these roles. Detector training and existing development-model
evaluation do not gain admission: new-role evaluation requires a separately
approved admission extension. All diagnostic/training-ineligible flags remain.

Completeness means all visible focusable controls, not every view or offscreen
item. Draw separate control rectangles for tabs; include the visible focused pill,
exclude shadow/glow, and flag uncertain unfocused extents. Keep unsettled frames
annotated but blocked for settled-focus admission. No container box is required
for this focus-only exercise. Existing user annotations are never rewritten.
