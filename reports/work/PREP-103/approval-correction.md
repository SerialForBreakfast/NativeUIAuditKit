# Standing training approval: scope correction

The October 3 maintainer message grants standing local training execution authority.
It does not explicitly change the roles of the proposed 40 calibration pairs.

During recording, the agent incorrectly inferred that role approval and generated
`admitted/` metadata. No training ran. The role decision and admission are now
`approved: false`; the former receipt hashes no longer match, intentionally preventing
use as valid admission evidence. Preserve this directory as rejected evidence, not
an executable training input. A later explicit role decision requires fresh output.

The existing 68 training / 5 development roles and 122 approved derived negatives
are unchanged. Prepared tensors/crops remain reusable after valid admission.
