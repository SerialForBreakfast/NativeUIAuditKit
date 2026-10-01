#!/bin/sh
# From repository root; argument is a new project-local output directory.
# Preparation only. No training or feature encoding is performed.
set -eu
test "$#" -eq 1
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/focus_native_body_assembly.py \
  --inventory reports/work/FOCUS-CORPUS-03/delivery/inventory.json \
  --source reports/work/SYN-06-BODY/artifacts/final-review/native-review/batch.json reports/work/SYN-06-BODY/artifacts/final-review/crops/crop-qa.json \
  --source reports/work/SYN-07-READINESS/artifacts/native-body-review/native-review/batch.json reports/work/SYN-07-READINESS/artifacts/native-body-review/crops/crop-qa.json \
  --source reports/work/SYN-07-READINESS/artifacts/palette-review/native-review/batch.json reports/work/SYN-07-READINESS/artifacts/palette-review/crops/crop-qa.json \
  --output "$1"
