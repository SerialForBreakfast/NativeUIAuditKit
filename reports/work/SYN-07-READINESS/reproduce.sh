#!/bin/sh
# Run from the repository root; give a new project-local output path.
set -eu
test "$#" -eq 1
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/focus_generation_readiness.py \
  --batch reports/work/SYN-06-BODY/artifacts/final-review/native-review/batch.json \
  --revision reports/work/SYN-06-BODY/artifacts/final-review/audit/review/review-revisions/20261001T060348Z-4076c5db/revision/revision.json \
  --crops reports/work/SYN-06-BODY/artifacts/final-review/crops/crop-qa.json \
  --lineage reports/work/SYN-07-READINESS/artifacts/received/ttr-syn04-native20-lineage-20261001-r1/source/Docs/Contracts/fixture-semantic-inventory-v1/source-lineage.json \
  --lineage-root reports/work/SYN-07-READINESS/artifacts/received/ttr-syn04-native20-lineage-20261001-r1/source \
  --inventory reports/work/FOCUS-CORPUS-03/delivery/inventory.json \
  --catalog reports/work/SYN-03/artifacts/received/ttr-semantic-proof-repair-20261001-r1/Docs/Contracts/fixture-semantic-inventory-v1/syn04-membership.json \
  --catalog-root reports/work/SYN-03/artifacts/received/ttr-semantic-proof-repair-20261001-r1 \
  --body-proof reports/work/SYN-07-READINESS/artifacts/native-body-review/report.json \
  --output "$1"
