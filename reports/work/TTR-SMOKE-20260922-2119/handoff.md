# Local simulator dialog smoke — 2026-09-22 21:25 UTC

## Result

Capture passed; end-to-end consumer qualification remains blocked at export.
Exactly one action_dialog/high_contrast/regular/two-element/seed-7/step-0 job ran
on simulator `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`. No Office, training,
installation, restart, automatic retry, or broader harvest occurred.

Job `697018C6-FAB6-4524-A691-1BE4507C8F7F` completed with two accepted rows,
zero rejected rows, four PNGs and twelve indexed files. Both rows are calibration;
zero training or held-out rows. Producer completion is not independent pixel validation.

- Recipe SHA256: `212912df2cc545e50132f61fa6e09ed2ff427862d867cb28a723d9c9413dfa00`.
- Manifest SHA256: `fe4b259a2b8c7210dad6b3a7404fa0cbc57bd4299ac8c9f72c98e424480e04a8`.
- Index SHA256: `4466f5c7bf4c37877f1397bfee4eecb6bb9e2778cd2e01d154af53ad1d705307`.
- Receipt SHA256: `3612d1b433e65b784abfb1cb0bbbb28aa32e5234ec68c41b43d237e8a5209f68`.
- Exact app/helper/Fixture hashes: `runtime.json`; source checkout reference
  `ec7339918ce2839e4d9458d84f90cf53f064a8a9` is recorded separately from binaries.

## Evidence and remaining boundary

`start.json`, `status-01.json`, and `pre-export-status.json` retain the actual job
results. Export command and timing are in `export-execution.json`: exit 69,
`serviceUnavailable`, approximately 14 ms. Its stderr reports successful IPC
connection/request/response. The new project-local export parent remains empty.
`job-manifest.json` succeeds afterward; `receipt-chunk.json` also succeeds through
the documented `fixture read-job` API, with its chunk SHA256 verified. Receipt
reports completed/two accepted/no rejections. These metadata reads do not validate PNGs.

Read-only producer inspection locates caller-side destination inspection/staging
in `FixtureJobExporter.swift`; `StableCLIRunner` maps untyped errors to
`serviceUnavailable`. Destination access is a hypothesis, not an established errno.
A narrow system-log query returned no matching denial. No app-container scraping,
permission change, alternate helper, or unchanged export retry was performed.

Postflight HTTP/device/scene, readiness, and coordinator checks passed. The same
Fixture instance remained responsive, native focus verified and settled on
dialog_btn_1; both buttons and container have measured geometry. All eight
readiness checks pass, ownership is clear, coordinator idle. See `*-after.json`.
This supersedes the prior dialog reference-geometry blocker only, not all archetypes.

## Independent outcomes

| Outcome | State |
|---|---|
| Software verification | Existing software reused; no implementation change or new offline suite claim |
| Data eligibility | Not established: exported bytes, annotations, visual alignment and runtime crops unvalidated |
| Integration | Local dialog capture and postflight pass; export/intake blocked |
| Model gates | Not assessed; no inference, training or promotion |

## Training readiness and next actions

1. Repair/diagnose export **of this retained completed job only**, including actual
   writer and underlying error. A supported bounded caller-owned transfer is an
   architectural option, but no new receiver was implemented in this diagnostic scope.
2. After export, verify all twelve files against manifest hashes, decode all PNGs,
   validate receipt/index/annotations, inspect both pairs, and exercise production
   16%/256x256 crop extraction. Only then accept this narrow compatibility smoke.
3. Qualify the multi-family/theme development pilot before scaling; this dialog
   does not establish readiness for shelf/non-view focus or other families.
4. Freeze separate recipe-group 80/10/10 partitions, excluding development seeds,
   related variants and duplicate content from final evaluation. Obtain the qualified
   >=6,000-pair corpus: gridMatrix>=2,000; mediaShelf>=1,500; settingsList>=1,000;
   actionDialog/heroCarousel/focusMaze>=500 each. Light and high-contrast must each
   cover >=20% of actual grid/media totals. Require >=100 held-out verified hard
   negatives covering light/high-contrast x imageView/collectionItem, plus full
   crop/label/coverage/leakage audits and raw-data retention/recovery evidence.
5. Candidate training still requires corpus acceptance and separate authorization;
   preserve shipped model and evaluate all existing gates. Simulator acceptance
   does not establish physical-device performance.

Independent existing-data visual review and direct-lane software remain available.
No fresh capture was performed merely to retry export. Machine timings are retained
per operation in `*-execution.json`; no tests or external peer wait were run here.
