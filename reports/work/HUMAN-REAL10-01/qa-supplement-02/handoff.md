# Corrected revision — crop QA

Revision20260929T192241Z-aabb2be6 supersedes191036Z; both preserved.
Existing production crop CLI and human_review_audit.py each exited0.
8 reviewed frames,155 controls;155/155 distinct256×256 crops,16% production
expansion. All155 crop byte hashes identical to prior QA: no geometry changed.
Audit found no structural issues. Revision/snapshot/batch bindings verified.

Exactly two state changes: recorded-742:new-1 and recorded-653:new-1 changed
unfocused→focused. Totals8 focused/147 unfocused, one per frame. No other control
field changed. Complete-frame candidate coverage remains unattested.

Human clarification resolved: maintainer explicitly confirms recorded-742:new-1,
the first Top Stories collection item, IS focused; Watch Now (control6) is NOT
focused. The saved revision already represents this correctly; no label or crop
changes are needed. The agent's prior outline-based suggestion was incorrect.
Lioness control1 in recorded-653 also matches the targeted correction.

Software: production crop and structural audit passed.
Data: diagnostic-only; target clarification resolved, no admission.
Integration: local reviewed-revision-to-crop path passed; no new TTR action.
Model gate: unassessed; no model execution, training or export.

Reports: crops/crop-qa.json and audit/audit.json; visual contexts/crop sheets and
audit/review.html retained. No source code changed, no Swift rebuild necessary.
Coordination not applicable: local annotation clarification only.
