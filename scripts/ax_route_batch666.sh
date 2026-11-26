#!/bin/zsh
# TRAIN666 B405-298: run a list of routed captures; relaunch the app before each so every route starts from its root.
# Usage: ax_route_batch666.sh LIST_FILE RESULTS_JSONL
# LIST_FILE lines: BUNDLE<TAB>SCREEN_ID<TAB>ROUTE<TAB>SWEEP<TAB>NO_RETURN(0|1)[<TAB>MENU_FIRST(0-2)]. MENU_FIRST reaches tvOS 26 sidebar tabs. Write - for an empty ROUTE or SWEEP (zsh collapses empty tab fields). Blank lines and lines starting with # are skipped.
set -u
ROOT="${0:A:h:h}"; SIM="${AX_UDID:-9026ECA9-77DB-4AE6-8FE6-BB239E9571FA}"
DRAFTS="$ROOT/reports/work/TRAIN666/fresh-flow-b405-298/route-drafts"
while IFS=$'\t' read -r bundle screen route sweep noreturn menufirst; do
  [[ -z "${bundle:-}" || "$bundle" == \#* ]] && continue
  [[ "${route:-}" == "-" ]] && route=""; [[ "${sweep:-}" == "-" ]] && sweep=""
  R="$ROOT/reports/work/TRAIN666/ax-capture/$screen.xcresult"; start=$(date +%s)
  if [ -e "$R" ]; then
    # Never repeat a completed capture: summarize the existing result instead.
    out=$(xcrun xcresulttool get test-results summary --path "$R" 2>/dev/null | grep -q '"result" : "Passed"' && echo "TEST EXECUTE SUCCEEDED (existing)" || echo "error: existing result failed")
  else
    xcrun simctl terminate "$SIM" "$bundle" 2>/dev/null; sleep 2
    xcrun simctl launch "$SIM" "$bundle" >/dev/null 2>&1; sleep 6
    out=$(AX_NO_RETURN="${noreturn:-0}" AX_MENU_FIRST="${menufirst:-0}" zsh "$ROOT/scripts/ax_capture666.sh" "$bundle" "$screen" "${route:-}" "${sweep:-}" 2>&1)
  fi
  secs=$(( $(date +%s) - start ))
  st=$(echo "$out" | grep -q "TEST EXECUTE SUCCEEDED" && echo passed || echo failed)
  "$ROOT/.venv-yolo/bin/python" "$ROOT/scripts/ax_snapshot_drafts666.py" --xcresult "$ROOT/reports/work/TRAIN666/ax-capture/$screen.xcresult" --out "$DRAFTS/$screen" >/dev/null 2>&1
  "$ROOT/.venv-yolo/bin/python" - "$DRAFTS/$screen" "$bundle" "$screen" "${route:-}" "$st" "$secs" "$(echo "$out" | grep -m1 'error:' | sed 's/.*error: //' | cut -c1-200)" >> "$2" <<'PY'
import json, glob, sys, collections
folder, bundle, screen, route, status, secs, error = sys.argv[1:8]
frames = []
for f in sorted(glob.glob(folder + '/*.draft.json')):
    d = json.load(open(f))
    frames.append(dict(draft=f.split('/')[-1], targets=len(d['objects']), classes=dict(collections.Counter(o.get('class') for o in d['objects'])),
                       focus=d.get('focus', {}).get('state')))
print(json.dumps(dict(bundle=bundle, screen=screen, route=route, status=status, seconds=int(secs), error=error or None, frames=frames)))
PY
  tail -1 "$2" | cut -c1-240
done < "$1"
