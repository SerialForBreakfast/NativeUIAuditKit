# Plozz controlled build for B405-298 captures

Source: `dataset/real_apps/sources/plozz` at revision `278ba3ade0a2734a81641aff771146cf506147a0`.
The 2 earlier `Info.plist` changes in the checkout are not part of this patch.
Joe approved this patch on 2026-11-25 ("Yes, patch both"). It is a capture build only. Do not ship or publish it.

## What `controlled-signin.patch` changes

SHA-256: `d6c596fbf6d82fc5356cd0fd3b74d713a8d0cd9c7201fd78244f529d2805cb9c`.

1. `ServerPickerView`: if the launch environment sets `NUIAK_SERVER_URL`, the view submits it as the manual server address.
2. `PasswordSignInView`: if the launch environment sets `NUIAK_USER` and `NUIAK_PASSWORD`, the view sends the normal `submit()` action.
3. `CoreSecureStore/Keychain.swift`: file-local wrappers around the 4 `SecItem` calls. Only for -34018, items go to app-local `UserDefaults`.
4. `CloudConfigSyncService`: CloudKit also needs a signed-in iCloud identity.
   The existing check allows CloudKit when the app has no provisioning profile, so the unsigned build trapped at launch in `CKContainer(identifier:)`.
   This crash is the likely cause of the Plozz XCTest error 10009 in capture pass 1.

## Use

1. Start the local Jellyfin server and launch once with the 3 `SIMCTL_CHILD_NUIAK_*` variables (see the Strimr README).
2. Route `Jellyfin`, then `Sign in with username & password`, each with a matching `AX_ALLOW_SELECT`.
3. First-run setup: keep defaults. Select `Continue` (libraries), `Looks good` (profile), `Not Now` (Seerr), `Continue` (theme), `Continue` (navigation style).
4. Sidebar sections need `AX_MENU_FIRST=1` (column 6 of the batch list).

Rollback copy of the previous app: `.build/rc561-plozz-pre-b405298/Plozz.app`.
