# Strimr controlled build for B405-298 captures

Source: `dataset/real_apps/sources/strimr` at revision `3c876fbad12859e56cea0cc1430e9bb7220d0e35`.
Joe approved this patch on 2026-11-25 ("Yes, patch both"). It is a capture build only. Do not ship or publish it.

## What `controlled-signin.patch` changes

SHA-256: `4d883e8d1efd206e47347b6306b7d0ad5085117b64057bcb9f1409fb0864cb55`.

1. `JellyfinAuthenticationView`: if the launch environment sets `NUIAK_SERVER_URL`, the view validates that server.
   If it also sets `NUIAK_USER` and `NUIAK_PASSWORD`, it then sends the normal `signIn()` action.
2. `Keychain.swift`: only when the keychain returns -34018 (no entitlement in an unsigned build), values go to app-local `UserDefaults`.

Without the environment variables, the sign-in view behaves as before.

## Use

1. Start the local Jellyfin server with `.build/rc561/run-jellyfin.sh` (loopback only).
2. Build with the RC561 command (derived data `.build/rc561/strimr`, `CODE_SIGNING_ALLOWED=NO`).
3. Launch once with `SIMCTL_CHILD_NUIAK_SERVER_URL`, `SIMCTL_CHILD_NUIAK_USER` and `SIMCTL_CHILD_NUIAK_PASSWORD` from `.build/rc561/swiftfin-setup.json`. Do not print them.
4. Route `Jellyfin` (`AX_ALLOW_SELECT=Jellyfin`), then `Continue` (`AX_ALLOW_SELECT=Continue`).

Rollback copy of the previous app: `.build/rc561-strimr-pre-b405298/Strimr-tvOS.app`.
