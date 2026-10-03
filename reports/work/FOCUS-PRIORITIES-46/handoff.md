# Focus priorities46 — fix alignment and scale sensitivity first

**We found an actionable weakness without changing annotations:** a small shift in
where identical pixels land on the detector's internal grid can make its focus
detections disappear. Training with position/scale variation is now the strongest
next hypothesis. Improvement from that training remains to be tested.

## Three comparisons and the necessary alignment control

Frozen sample:12human-approved reference images (7guide,5catalog) and18previously
exposed native development images, six per focused-control ID. Selection used labels
and sorted image hashes, not model results. Same fixed FSF001/FSF002weights and
.25operating/.001retained-candidate confidence/.7NMS; full-body match atIoU≥.50.
All300inferences use MPS and resident weights. Roles/labels remain unchanged.

| Native18comparison | Focused bodies found |
|---|---:|
| One epoch, ordinary640input | 15/18 |
| One epoch, ordinary1280input | 0/18 |
| One epoch, centered640square | 15/18 |
| Ten epochs, same centered640square | 8/18 |

Reference12full-body matches are0/12atboth ordinary resolutions. More detail alone
does not rescue transfer. Doubling resolution also doubles object scale in model
coordinates, so this does not prove that fine focus cues are unimportant.

The position comparison resizes each source once to640×360, then places those exact
pixels in a640square gray canvas. Bounds move by exactly the same offset.

| Top padding | Relationship to center | Native focused bodies found |
|---:|---|---:|
| 0px | −140px; changed32px-grid phase | 0/18 |
| 12px | −128px; same phase | 15/18 |
| 140px | centered baseline | 15/18 |
| 268px | +128px; same phase | 16/18 |
| 280px | +140px; changed phase | 0/18 |

This corrects the initial interpretation: the failure is strongly alignment-dependent,
not a simple center-only position rule. Native focused candidates remain detectable
at the.001floor in all18unaligned FSF001cases, but their scores collapse. Longer-fit
FSF002finds only3/18atthat floor for each unaligned shift, and does worse centered.
The extra60passes were a confound control within the position comparison, not a new
training sweep. Padding shifts are artificial diagnostic inputs, not native app renders.

![Identical content, different padding alignment](audit-verified/alignment-example.png)

The example was selected by frozen membership order, not largest effect. Green marks
known focus, red marks predictions≥.25. Its focused-body score changes~.007→.918
between0and12pxpadding. Content, scale and labels are otherwise identical.

## Training evidence and revised priorities

Both retained training `args.yaml` files confirm `rect: true`, `translate: 0.0`,
`scale: 0.0`, `multi_scale: 0.0`; the existing runner explicitly sets zero translation
and scale. This supplies a concrete intervention, not proof that it will fix everything.

1. **First: controlled training variation on existing admitted data.** Add tested
   translation/scale options to the current runner; compare translation-only and
   translation+scale at one epoch from the same original initialization. Preserve
   correct transformed boxes, label visibility, data membership and evaluation isolation.
   Measure ordinary accuracy AND grid-alignment robustness/wrong selections.
2. **Second: appearance and control-family coverage.** Reference guide/catalog transfer
   remains poor even at favorable alignment. Expand native row/tab bodies, tall/wide
   artwork and focus contrasts after isolating the training-invariance effect.
3. **Lower priority:** unchanged longer fitting, higher inference resolution, another
   blanket annotation review. Retain occasional sampling and investigate specific
   annotation disagreements; repeated clean reviews make labels a low-priority suspect.

This tranche supplies a practical diagnosis, not a better released model or an
independent accuracy benchmark. No training admission decision is needed for the
already admitted original2,000images; reference calibration images stay out of fitting.
The next training tranche still freezes its own exact configuration/budget before launch.

## Verification and evidence

- [Initial protocol](run/protocol.json), [initial results](run/summary.json),
  [aligned control](alignment/summary.json), [reconstruction audit](audit-verified/audit.json).
- All300result geometries/scoring reconstructed from source pixels and raw predictions.
  Identical content preserved across offsets. All30ordinary640results reproduce earlier
  independent retained decisions and focused-body scores within1e-5.
- 5newtransform/selection/scoring tests and28reference tests pass. Offline Swift build,
  14XCTest and120SwiftTesting checks pass. `git diff --check` passes.
- Initial240pass execution17.5276s, follow-up60pass execution6.1831s, including each
  measured loop's model setup/I/O; imports/preflight are outside those clocks. Individual
  prediction timings include cold/dynamic-shape effects and are not a controlled latency
  benchmark. Outputs remain below128MiB, project-local; USB source images read only.
- First audit attempts failed on encoded-PNG alias lookup and incompatible historical
  pixel-hash prefixes. The final audit recomputes through one decoder and verifies
  alias identity; logs/failed empty output directories remain as evidence.

Software verified: pass. Data eligible: existing diagnostic/calibration scope only.
Integration qualified: local fixed-model experiment/replay pass. Model release gate:
not assessed. Coordination: not applicable; local model diagnosis does not change a
producer contract or require a shared-status publication.

Next substantial tranche: implement and validate augmentation controls, execute the
two justified one-epoch comparisons on unchanged admitted training membership, and
score the fixed synthetic/reference/real development challenges to choose the next
model/data investment. TTR availability and new annotation review do not block that work.
