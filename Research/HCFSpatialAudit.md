# Check whether native HCF differences follow focus

High Contrast Focus (HCF) changes the native focus appearance.
A successful setting change does not prove that the visible difference follows focus.
This diagnostic checks that distinction before larger capture campaigns.

## Inputs

Use a `native-hcf362-v1` capture manifest with these records:

- Standard and HCF frames for at least 2 focused controls.
- 2 repeated frames for each profile and focused control.
- Verified native focus observations before and after each capture.
- Measured visible body bounds in image pixels.
- Image hashes and verified OS profile receipts.
- A completed capture with verified cleanup.
- The original development role and related scene group.

The script uses the union of Standard and HCF body bounds for each control.
It adds a fixed 64 px margin at the original image resolution.
Overlapping windows fail the check because they would make attribution unclear.
The script does not resize the frames or estimate labels from image differences.

## Measurements

The script sums absolute RGB differences between matched profiles.
It reports differences inside each body, near each body, and outside all control windows.
It also reports repeated-frame differences and the fraction of profile difference near focus.

The diagnostic criterion requires these conditions:

- At least 90% of the profile difference falls near the focused control.
- Its mean difference exceeds every unfocused control by more than 10 times.
- Repeated frames within each profile match exactly.
- Every tested focus position passes.

These limits qualify this diagnostic, not a detector or deployment policy.
Zero profile difference does not pass. A global appearance change does not pass.
Related frames remain one related group, not independent statistical trials.
Changing artwork or position requires new matched captures under the same rules.

## Use

Use the resident Python environment with NumPy and Pillow.

```sh
python scripts/hcf_spatial_audit.py path/to/capture.json
PYTHONPATH=scripts python -m unittest scripts/test_hcf_spatial_audit.py
```

The command prints JSON. It does not change the capture, admit training data, or control a device.
The caller can save the report through its existing experiment queue.
The tool needs no private worker configuration or queue module.

## Limits and next decisions

A passing result supports further native capture across positions and artwork.
It does not prove outline detection, focused-control accuracy, body-box accuracy, or physical-device parity.
The 64 px window is a declared analysis choice, not an estimate of the native effect width.
Use separate labeled data to compare rules, a crop classifier, and a full-screen detector.
Keep Standard counterparts, capture receipts, failures, and original image dimensions.
