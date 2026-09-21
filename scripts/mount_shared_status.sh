#!/bin/zsh
# Mount and verify the authorized TVTestRig–NUIAK shared-status SMB folder.
#
# This intentionally delegates authentication to macOS/Finder. It does not store
# credentials and does not create /Volumes/SharedStatusFile when the share is absent.
#
# Usage: scripts/mount_shared_status.sh

set -euo pipefail

mount_point="/Volumes/SharedStatusFile"
share_url="smb://sillycon.local/SharedStatusFile"
wait_seconds=20

is_real_mount() {
  /sbin/mount | /usr/bin/grep -F " on ${mount_point} " >/dev/null
}

if is_real_mount; then
  print "Shared status is already mounted: ${mount_point}"
  exit 0
fi

if [[ -e "${mount_point}" ]]; then
  print -u2 "Refusing to use ${mount_point}: it exists but is not an SMB mount."
  print -u2 "Do not write status there; remove or resolve that local directory manually, then retry."
  exit 2
fi

print "Opening the macOS SMB mount flow for ${share_url}..."
/usr/bin/open "${share_url}"
print "Complete any Finder authentication prompt; waiting up to ${wait_seconds}s for the mount."

for _ in {1..20}; do
  if is_real_mount; then
    print "Shared status mounted and verified: ${mount_point}"
    exit 0
  fi
  /bin/sleep 1
done

print -u2 "The share was not mounted. No local fallback directory was created."
print -u2 "Check Finder's connection/authentication message, then rerun this script."
exit 1
