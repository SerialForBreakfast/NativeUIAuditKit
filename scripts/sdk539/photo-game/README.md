# Photo Guessing Game controlled content

Pin source revision `d1cfe353667c124672e9b7bf929feab35c69a46f`.
Apply `controlled-content.patch` after `git apply --check`. Preserve the GPL-3.0-or-later license.
The patch changes data preparation. It preserves view layouts and native focus behavior.

For Debug builds, `--real543-controlled-content` fixes dates, identities, answer order, photo order, and placeholder colors.
It uses a Gregorian calendar in UTC. The reference year is 2026.
The photo-library action supplies demo data in this mode. It does not request personal photos or geocoding.
Starting the game extracts the controlled location choices before play.
Normal runs retain their original behavior. Release builds ignore this flag.

`ContentChecks.swift` tests year support, location order, leap days, weekday mapping, IDs, and stable hues.
Two separate Debug processes produce identical output. Debug without the flag and Release with the flag remain disabled.
The tvOS Simulator source build passes. No installation or app launch occurs in this tranche.

Confetti and animations remain unchanged. Do not treat animated frames as reproducible static screens.
Runtime language, locale, settling, SDK registration, and observed focus still need qualification.
This patch does not qualify labels or grant training admission.
