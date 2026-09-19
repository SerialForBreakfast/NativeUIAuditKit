# FR-A handoff — FocusRing readiness software

The offline validator enforces 6,000-pair scene quotas, 20% light/highContrast
coverage where required, paired labels, seed isolation, rejection of model-prediction
labels, and all four held-out hard-negative strata with at least 100 samples total.
Metadata reconciliation confirms bundled `focus-ring-detector-v1.0` / `1.0.0`; FDR-001
remains the historical training-run label. Tests cover pair, split, quota and stratum failure.

Software verified: PASS. Data eligibility: FAIL (no new collected corpus). Integration/model
qualification: N/A. FR-B remains blocked on authorized Office capture.
