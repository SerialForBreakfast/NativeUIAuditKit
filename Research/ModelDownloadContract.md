# Bounded model transfer — internal preview

Owner: Maximum-mini-NUIAK. Related task: 293-D.
This code remains internal. It does not start downloads during package initialization or application startup.

## Inputs and trust

The host creates `NativeModelDownloadEntry` from its trusted, reviewed catalog.
The entry fixes the HTTPS URL, archive size, archive hash, source root, and each member's size and hash.
Initial URLs name GitHub release assets. Mutable `latest` and `nightly` aliases are rejected.
Credentials, query strings, fragments, unknown hosts, and custom ports are rejected in initial URLs.
Archives remain limited to 32 MiB, 256 files, and 64 MiB expanded content.

These checks validate a selected transfer. They do not replace the complete release catalog checks.
The host still verifies model ID, version, task, host eligibility, preprocessing, rights, and release approval before selecting an entry.
The current runtime does not parse or authenticate a remote catalog.
Do not infer training approval or distribution rights from a matching hash.

## Transfer behavior

`NativeModelDownloader.download` starts only after an explicit caller request.
It uses `URLSession` through an injectable transport. Tests inject responses without network access.
The production configuration has no cookie store, credential store, or response cache.
Request timeout is 30 s. Resource timeout is 120 s.
Redirects remain HTTPS and use only `github.com` or `release-assets.githubusercontent.com`.
The transport permits at most 3 redirects. It forwards only encoding and range headers.
TLS uses the platform trust checks. Authentication requests do not use stored credentials.

Response status, declared length, encoding, and actual byte counts have separate checks.
The receiver stops oversized content before writing that chunk.
Every completed archive passes the existing ZIP and member checks before installation.
One actor rejects concurrent transfers. An exclusive directory claim also prevents another receiver for the same archive.
Interrupted claims require explicit review. The downloader does not take them over automatically.

## Resume and failure

Resume requires an explicit call with `resume: true`.
The saved record fixes the original URL, expected size, expected hash, and a strong ETag.
The request uses `Range` and `If-Range`.
The response must return 206, the same ETag, and the exact remaining byte range.
An ignored range or changed entity stops the attempt without appending its content.
Weak ETags cannot authorize resume. The final hash still checks the complete archive.
The receiver reads fresh file metadata after appending bytes. Cached URL metadata cannot establish completion.

Failed and cancelled transfers retain their partial bytes.
`discardPartial` moves an invalid transfer into a recovery folder before an explicit new attempt.
It does not delete bytes or replace a valid completed archive.
Completed archives pass verification again before offline reuse. Corrupt cached bytes fail; they do not trigger an automatic download.

## Installation and test limits

`install` reuses the existing `NativeModelInstaller` and its validation callback.
An existing installation passes recovery checks and the caller's current validation callback.
Downloading, installing, and selecting an active model remain separate actions.
A failed transfer does not change the active selection.

The real-path test uses 2 packaging versions of the same resident tvOS model.
Different notices produce different archive identities. The test does not claim 2 distinct trained models.
Both packages compile, match the retained 25-detection reference, and reload without network requests.
The actual `URLSession` adapter also receives an offline `URLProtocol` response.
Other tests cover truncation, changed entities, weak ETags, byte limits, hashes, low space, claims, and transport errors.

Remaining checks include an approved live endpoint, signed TTR execution, active network cancellation, and elapsed network timeout behavior.
Complete the trusted catalog adapter and public host interface before an application release.
The current tests do not qualify GitHub's live redirect behavior or actual macOS 14 model execution.
