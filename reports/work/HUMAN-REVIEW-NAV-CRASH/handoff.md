# Navigation key-release crash repair

Cause verified from retained GUI stderr: Canvas.keyReleaseEvent raises ValueError
at shapes.index(selectedShapes[0]); selection is stale after image switch. Native
report shows PyQt callback fatal/SIGABRT. Not an image-list index-range failure.

Repair resets selectedShapes/selectedShapesCopy/movingShape at image reset and
guards delayed key release against stale selection or missing undo snapshot. Valid
movement still stores undo and emits dirty. No vendor package edits or broad
exception swallowing.13 actual Qt tests and offline Swift build/test pass. Logs:
.build/human-review/navigation-crash-{qt,build,test}.log.

Saved batch02 JSON files readable:24,19,7,10,10,0,0,0 boxes. Unsaved changes cannot
be recovered from this evidence. Reopened at image6/recorded-951; process running
without error at startup check. Numbered controls included. No label edits made.

Software verified; saved data preserved, no new admission; local editor integration
reopened; model gate unassessed. No TTR/device actions, recapture or model work.

Shared FOCUS-HUMAN-OFFICE-01 metadata updated at
/Volumes/SharedStatusFile/nuiak/status.yaml on verified sillycon.local SMB mount.
Readback/unique-key YAML validation passed and unrelated-entry structural hash
preserved. No peer acknowledgment yet. Published consequence: local subset review
already works independently of export repair, consumer-owned editor failure, no
recapture needed; retain separate producer export acceptance and delivery-profile
requests. Producer22:16 report read, not a verified consumer export success.
