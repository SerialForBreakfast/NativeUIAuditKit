#!/bin/bash
# Run the portable authored test in a new approved directory.
set -euo pipefail
if [ "$#" -lt 2 ] || [ "$#" -gt 4 ]; then
  echo 'Usage: bash Scripts/qualify.sh /absolute/render-headless-screen.swift /absolute/new-work-directory [max-load] [/absolute/reference-bundle]' >&2
  exit 64
fi
renderer_source="$1"
work="$2"
max_load="${3:-8}"
case "$renderer_source" in /*) ;; *) exit 64 ;; esac
case "$work" in /*) ;; *) exit 64 ;; esac
[ -f "$renderer_source" ] && [ ! -e "$work" ] || exit 65
package_root="$(cd "$(dirname "$0")/.." && pwd -P)"
mkdir -p "$work/tmp" "$work/cache" "$work/tests" "$work/host-a" "$work/host-b"
export TMPDIR="$work/tmp"
export CLANG_MODULE_CACHE_PATH="$work/cache"
export FIXTURE_EXPERIMENT_TEST_ROOT="$work/tests"
swift build --build-system native --package-path "$package_root" --scratch-path "$work/build" \
  --disable-automatic-resolution --jobs 2 > "$work/build.log" 2>&1
swift test --build-system native --package-path "$package_root" --scratch-path "$work/build" \
  --disable-automatic-resolution --jobs 2 --no-parallel > "$work/tests.log" 2>&1
/usr/bin/swiftc -module-cache-path "$work/cache" "$renderer_source" -o "$work/renderer" > "$work/renderer-build.log" 2>&1
tool="$work/build/debug/fixture-experiment"
source_hash="$(/usr/bin/shasum -a 256 "$renderer_source" | /usr/bin/awk '{print $1}')"
if [ "$#" -eq 4 ]; then
  case "$4" in /*) ;; *) exit 64 ;; esac
  "$tool" validate --bundle "$4" > "$work/prepare.json"
  /bin/cp -R "$4" "$work/bundle-a"
else
  "$tool" make-reference --output "$work/bundle-a" --renderer-source-sha256 "$source_hash" > "$work/prepare.json"
fi
/bin/cp -R "$work/bundle-a" "$work/bundle-b"
for host in a b; do
  "$tool" configure --workspace "$work/host-$host" --renderer "$work/renderer" \
    --renderer-source "$renderer_source" --output "$work/config-$host.json" --max-load "$max_load" > "$work/configured-$host.json"
  "$tool" validate --bundle "$work/bundle-$host" > "$work/validated-$host.json"
  "$tool" preflight --bundle "$work/bundle-$host" --host "$work/config-$host.json" > "$work/preflight-$host.json"
  code=0
  "$tool" run --bundle "$work/bundle-$host" --host "$work/config-$host.json" --max-jobs 2 > "$work/first-$host.json" || code=$?
  [ "$code" -eq 75 ] || exit 1
  /usr/bin/grep -q '"state" : "paused_batch"' "$work/first-$host.json" || exit 1
  /bin/cp "$work/host-$host/hcf336-reference/checkpoint.json" "$work/first-checkpoint-$host.json"
  "$tool" run --bundle "$work/bundle-$host" --host "$work/config-$host.json" --max-jobs 2 > "$work/second-$host.json"
  "$tool" status --bundle "$work/bundle-$host" --host "$work/config-$host.json" > "$work/status-$host.json"
done
echo 'Two relocated campaigns complete. Preserve the work directory for receipt comparison.'
