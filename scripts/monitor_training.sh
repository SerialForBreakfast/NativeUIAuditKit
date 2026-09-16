#!/bin/bash
# monitor_training.sh — Quick progress monitor for tvOS model training

RUNS_DIR="NativeUITrainer/yolo_runs/phase6b_tvos_v2"

echo "=== NativeUIAuditKit tvOS Training Monitor ==="

# Check process status
PID=$(pgrep -f "scripts/train_tvos_model.py" | head -n 1)
if [ -n "$PID" ]; then
    echo "Status: RUNNING (PID: $PID)"
    ps -p "$PID" -o %cpu,%mem,time,command | head -n 2
else
    echo "Status: NOT RUNNING"
fi

# Show latest metrics from results.csv if present
if [ -f "$RUNS_DIR/results.csv" ]; then
    echo ""
    echo "--- Latest Epoch Metrics ($RUNS_DIR/results.csv) ---"
    python3 -c "
import csv
with open('$RUNS_DIR/results.csv') as f:
    rows = list(csv.DictReader(f))
    if rows:
        last = rows[-1]
        epoch = last.get('epoch', '').strip()
        map50 = float(last.get('metrics/mAP50(B)', 0))
        map50_95 = float(last.get('metrics/mAP50-95(B)', 0))
        prec = float(last.get('metrics/precision(B)', 0))
        rec = float(last.get('metrics/recall(B)', 0))
        loss = float(last.get('train/box_loss', 0))
        print(f'Completed Epoch  : {epoch}/100')
        print(f'Train Box Loss   : {loss:.4f}')
        print(f'Precision        : {prec:.4f} ({prec*100:.1f}%)')
        print(f'Recall           : {rec:.4f} ({rec*100:.1f}%)')
        print(f'Validation mAP50 : {map50:.4f} ({map50*100:.1f}%)')
        print(f'Val mAP50-95     : {map50_95:.4f} ({map50_95*100:.1f}%)')
"
fi

