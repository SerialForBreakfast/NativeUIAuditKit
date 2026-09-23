# Direct dialog visual review

Reviewed all three original 3840x2160 frames in
`dataset/tvos_captures/direct-dialog-20260922-2147` on 2026-09-22.
Reference shows the separate reference control focused, neither dialog button
enlarged. Target0 shows Authorize enlarged; target1 shows Cancel enlarged.
The primary button is white even when unfocused; color alone is not label evidence.
No cropped-off target, dialog occlusion or unexpected app/context was observed.
Native interval labels agree with these visible states.

The reported native-view boxes are nominal bounds, identical across focus states;
focus decoration extends beyond them. Existing 16% crop expansion contains the
visible button effects in the corresponding TTR inspection crops; no new cropper,
box adjustment or synthetic frame identity is introduced. Wide buttons become
distorted under the established 256x256 production preprocessing, a baseline
limitation to measure rather than silently correct here.

Accept this two-pair direct capture for development-only crop intake. It is not
training corpus acceptance, independent holdout evidence, or physical qualification.
