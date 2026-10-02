# FOCUS-ALIGNMENT-12 — translation without erasing growth

Assigned October 1, 2026, owner Codex: substantial offline experiment and usable
diagnostic CLI. No capture, new admission, neural training, export or promotion.
Reuse Paired11's exact 2,996 cases and original images; labels and after truth boxes
are evaluation-only. Prior failed results remain immutable.

Freeze before scoring: match the central 70% of the before-control body using
absolute image gradients, insensitive to text polarity. Use the same isotropic
image scale for both frames (before body width capped at256pixels). Search translation
within .25body widths horizontally and max(3body heights,.10viewport height)
vertically. Correlation >=.55, alternate-peak gap >=.08 outside a .3body-height
radius, minimum gradient standard deviation .01; reciprocal match within .15body
height (minimum2scaled pixels). No scale search, no after-label/bounds input.
Low texture, ambiguous match, viewport change or clipping-footprint change abstains.
Exactly identical frames may confirm unchanged pixels, not initial focus state.

Use existing native makeCrop for before bounds and translated bounds with identical
width/height and16%context. Require identical relative clipping footprints; do not
silently change scale at viewport edges. Reuse Paired11 growth/brightness thresholds
and its separate clipped-margin brightness handling. Add a fixed illumination
warning when median luma shift in the outer24pixel border exceeds .04. Report
raw and gated outputs separately. Content replacement with unchanged shape remains
a counterexample, not a problem to hide with annotation-family gates.

Complete: label-blind tracker, actual offline verify CLI with optional opt-in mode,
bounded corpus replay/native crops, frame/control/baseline comparison, translation
error audit using truth only after prediction, software/CLI negative tests, synthetic
motion/content/light/no-op stress, measured runtime, visual QA and evidence-backed
keep/reject decision. Context, settlement and identity claims remain supplied inputs,
not measured runtime services. Screen-level claims preserve prior eligibility.
No repeated scientific threshold search if this method fails.

Budget: CPU-only offline replay <=30minutes, <=2GiBnew outputs. Reuse resident OpenCV
and native helper, no install. An optional diagnostic interface is not production
qualification. If corpus or stress fails, keep the interface explicitly experimental,
return uncertainty and document why no runtime adoption is justified.
