# Experimental click-to-box

User-authorized optional local review aid, default off each editor launch. No model,
new dependency or external service. Toggle enables click proposal mode; disabling
restores manual behavior immediately. Use retained pixels and conservative bounded
color-region segmentation to propose rectangular control panels. Click inside a
plain area, not text/icon. Decline ambiguous/nonrectangular/large background regions.
This first experiment targets visible filled tiles/pills/rows, not invisible hit
areas, gradients or reliably reconstructing artwork boundaries.

Preview geometry before label acceptance. Cancel leaves annotations unchanged;
Follow-up: suggestions reuse the session's last accepted dialog label (including
manual rectangle/edit labels), with Enter accepting it. Cancel restores the prior
label default. This remembers only the label, never focus, confirmation or notes.
Suggestion preview must clear Labelme's transient manual-drawing guide: its canvas
paints both current and line together. Never clear saved shapes to hide that guide.
accepted proposals are unconfirmed, unchecked Focused/unfocused default, with local
IDs only. Clear frame reviewed flag, retain normal geometry editing and undo. Never
auto-promote. Test toggle off, cancel, no detection, proposal save, bounded runtime
and generated positives/negatives; probe retained reviewed examples without labels
being rewritten. Promotion depends on measured usefulness, not just unit tests.

Separate pending fix: normalize only floating-point edge excursions <=1e-7 pixels
in diagnostic rectangle parsing. Reject genuine out-of-image coordinates and
zero-area boxes. Preserve immutable snapshots and require explicit Finish review
to create a new revision; never amend previous approvals automatically.
