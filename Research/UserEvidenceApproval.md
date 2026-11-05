# Explicit user review

Owner: Maximum-mini-NUIAK. Updated November 4, 2026.

Run experiments and compute provisional metrics through the existing workflow.
Before updating headline metrics, README accuracy claims, or accepted model status, present the evidence to Joe.
Show what changed, the evaluation scope, counts, regressions, limitations, and the exact proposed update.
Wait for explicit approval in this chat before publishing those changes.
Request explicit approval before promoting a model. Approval to publish metrics does not automatically approve promotion.

After approval, record the actual user message and chat reference with the report hash or exact release identity.
Do not invent, infer, or self-authorize the user's decision.
Changed results or a changed release require renewed review of the changed proposal.
Routine experiments, diagnostic reports, and predefined research follow-ups continue while review is pending.

Use a small JSON record under ignored `reports/work/user-approvals/`.
Fields: version `user-review-v1`, decision `approved`, action `publish-metrics` or `promotion`, userMessage, chatReference, and scope.
Metric records include reportSHA256. Promotion records include releaseEntrySHA256.
These records document the conversation. They do not authenticate users cryptographically.

No signing keys, protected directories, enrollment, or separate accounts are required by this approval process.
The earlier signing design is withdrawn as unnecessary for the maintainer's requested workflow.
