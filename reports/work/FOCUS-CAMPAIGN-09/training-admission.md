# Six pairs admitted for the matched training comparison

The maintainer explicitly designated these six pairs for training after approving
all six sampled screens. The earlier sample-acceptance record remains immutable;
its pending source-role statement is superseded by this decision and the
[assigned comparison](../../../Research/Plans/FocusArtwork09.md).

- Original TTR records still say calibration; consumer use is development-training.
- Admitted:12unique target crops, six focused and six unfocused, from white-mark-1,
  pale-mark-1 and placeholder-1 in light/dark scenes. All other controls excluded
  from additions. Native focus, measured rendered bounds and source hashes retained.
- All312post-review crops exactly match their original accepted crop hashes.
  Sampled156controls across six screens required no correction. The sample does
  not establish a universal annotation-error bound or independently review all12frames.
- 1550training controls become1562;315development+18retention remain byte-for-byte
  unchanged. Related synthetic layouts are not independent test data.
- Nonfixture276training weights remain exact. Total fixture weight for each label
  stays fixed;12new controls receive0.695%of total training weight under the
  predeclared continuity policy. No extra oversampling or threshold tuning.
- Prefix encoding processed12controls in1.83seconds, reusing1883existing entries;
  the pretrained prefix identity matches. No download or new capture.

Evidence: `artifacts/admitted/admission.json`, `artifacts/sample-acceptance.json`,
`artifacts/post-review-crop-parity.json`, `artifacts/weight-comparison.json`,
`artifacts/encoded/receipt.json`. These are local artifacts, not shared raw data.

TTR role-migration receipt published/read back at
`nuiak/responses/nuiak-20261001-campaign09-training-designation.yaml`.
Producer22:14:46UTC independently requests exactly this explicit migration after
human review. Its remaining42cases are not admitted by this receipt. New repair
archive was announced but not copied or executed as part of this local comparison.
