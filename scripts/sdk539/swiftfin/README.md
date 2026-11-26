# Swiftfin controlled build for B405-298 captures

Source: `.build/sdk539-apps/Swiftfin` at revision `10629aba`, with the earlier SDK539 instrumentation in place.
Joe approved this patch on 2026-11-25 ("Patch Swiftfin build"). It is a capture build only. Do not ship or publish it.

## What `controlled-signin.patch` changes

SHA-256: `34344cb26a9428666ad21300b2ecb076945d69d384c6e6f3befde853ae915626`.

1. `ConnectToServerView`: if the launch environment sets `NUIAK_SERVER_URL`, the view sends the normal `connect(url:)` action on first appearance.
2. `UserSignInView`: if the launch environment sets `NUIAK_USER` and `NUIAK_PASSWORD`, the view sends the normal `signIn(username:password:)` action on first appearance.
3. `Keychain.swift`: an unsigned Simulator build has no keychain entitlement (`errSecMissingEntitlement`, -34018).
   Only for that error, the token goes to app-local `UserDefaults` (suite `nuiak.unsigned-keychain-fallback`).
   Without this, the app crashes after sign-in at `SwiftfinStore.State.User.accessToken` ("access token missing in keychain").

Without the environment variables, the connect and sign-in views behave as before.

## Use

1. Start the local Jellyfin server with `.build/rc561/run-jellyfin.sh` (loopback only).
2. Build with the SDK539 command (`CODE_SIGNING_ALLOWED=NO`, derived data `.build/sdk539-app-derived`).
3. Install on the research Simulator. Launch once with `SIMCTL_CHILD_NUIAK_SERVER_URL`, `SIMCTL_CHILD_NUIAK_USER` and `SIMCTL_CHILD_NUIAK_PASSWORD`.
   Read the values from `.build/rc561/swiftfin-setup.json` (ignored, mode 600). Do not print them.
4. Route `Connect` with `AX_ALLOW_SELECT=Connect`, then route `Add user` with `AX_ALLOW_SELECT="Add user"`.
5. The session persists. Later launches without the variables open Home.

The rollback copy of the previous app is `.build/sdk539-swiftfin-pre-b405298/Swiftfin.app`.
