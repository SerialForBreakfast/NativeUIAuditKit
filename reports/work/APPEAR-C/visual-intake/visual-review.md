# Independent appearance visual review

2026-09-23. Reviewed all ten focused states, three reference states, measured
control overlays and twenty production `makeCrop` outputs. Contact sheets in
this directory record grid-artwork, dock-bright and media-placeholder.

All intended native target IDs agree with the visible white border. Reference
cards lack that border; bright dock cards remain bright while unfocused. Gray
media cards contain neutral bars and are genuine interactive cards, not excluded
taxonomy placeholders. Native measured rectangles enclose the rendered controls.
The existing 16% expansion/256×256 crop path retains the complete border, titles
and some neighboring context; no target border is cut off in these samples.
The square resize visibly compresses the tall media cards as expected from the
existing runtime preprocessing; no alternate crop policy was introduced.

Grid/dock have three enabled targets and one disabled card each; media has four
targets. Thus ten pairs account for all supported targets, not twelve successes.
The grid/dock caption still says 2×2 although both have one row here. Media's long
title is truncated. These are bounded visual limitations, not missing targets.

Accept for simulator development only. All recipes are dark/regular/seed7, with
the same white-border focus treatment; changing preset/layout is not proof of
independent evaluation families. No physical rendering, model accuracy, training
approval, multirow/scroll coverage, high-contrast distinction or Photos-like
qualification is established. Requested focus was not used in place of native
observations. Byte integrity and bracket correlation do not authenticate hardware.
