// TextAnchorVerifier.swift
// NativeUIAuditKit
//
// Third perception primitive (Track 4, TASK-PERCEP-03): lets a caller assert "this is the
// General screen" from required/optional/forbidden text anchors. A thin wrapper over the OCR
// pass this package already ships (Phase 7, `NativeUIDetectionRequest.recognizeText`) — this
// does not add a second Vision integration, and it returns `RecognizedTextRegion`/`NativeUIRect`
// unchanged, so callers never juggle two coordinate systems for OCR results.

import CoreGraphics
import Foundation

/// Required/optional/forbidden text anchors for one navigation-state assertion.
///
/// Matching is case-insensitive substring containment against each OCR line — "General"
/// matches a recognized line of "General" or "› General Settings", not just an exact string.
public struct TextAnchorRequirements: Sendable, Equatable {
    public let required: [String]
    public let optional: [String]
    public let forbidden: [String]

    public init(required: [String] = [], optional: [String] = [], forbidden: [String] = []) {
        self.required = required
        self.optional = optional
        self.forbidden = forbidden
    }
}

/// One anchor string paired with the OCR region that satisfied it.
public struct TextAnchorMatch: Sendable, Equatable {
    public let anchor: String
    public let region: RecognizedTextRegion
}

/// Outcome of checking a screenshot against `TextAnchorRequirements`.
public enum TextAnchorVerificationStatus: Sendable, Equatable {
    /// Every required anchor was found and no forbidden anchor was found.
    case verified
    /// At least one required anchor is missing, or a forbidden anchor is present — a confident
    /// negative signal, not a guess.
    case unverified
    /// Not enough signal to decide either way: no required anchors were supplied, or OCR found
    /// no text at all in the searched region (e.g. a blank or still-loading screen).
    case ambiguous
}

/// Full result of a text-anchor verification, including *why* — never just a bare status,
/// since "unverified" and "ambiguous" both need their evidence to be actionable.
public struct TextAnchorVerificationResult: Sendable, Equatable {
    public let status: TextAnchorVerificationStatus
    public let matchedRequired: [TextAnchorMatch]
    public let matchedOptional: [TextAnchorMatch]
    public let matchedForbidden: [TextAnchorMatch]
    public let missingRequired: [String]
}

/// Verifies a screenshot against text anchors using the package's existing OCR pass.
public struct TextAnchorVerifier: Sendable {
    public init() {}

    /// Runs OCR (optionally scoped to `regionOfInterest`, e.g. from
    /// `ChangeRegionLocalizer`) and checks the result against `requirements`.
    ///
    /// - Parameter regionOfInterest: Top-left-origin pixel-space rect (matching
    ///   `ChangeRegionLocalizer`'s and this package's `boundsPixels` convention). `nil` searches
    ///   the full frame. Converted internally to Vision's bottom-left-origin normalized space —
    ///   callers never need to think in Vision coordinates.
    public func verify(
        _ requirements: TextAnchorRequirements,
        in screenshot: CGImage,
        regionOfInterest: CGRect? = nil
    ) async throws -> TextAnchorVerificationResult {
        let visionROI = regionOfInterest.map {
            Self.pixelRectToVisionNormalized($0, imageWidth: screenshot.width, imageHeight: screenshot.height)
        } ?? CGRect(x: 0, y: 0, width: 1, height: 1)

        let regions = try await NativeUIDetectionRequest.recognizeText(in: screenshot, regionOfInterest: visionROI)
        return Self.evaluate(requirements, against: regions)
    }

    /// Pure evaluation, split out from `verify` so anchor-matching logic is testable without
    /// running live OCR.
    static func evaluate(
        _ requirements: TextAnchorRequirements,
        against regions: [RecognizedTextRegion]
    ) -> TextAnchorVerificationResult {
        func matches(_ anchor: String) -> [TextAnchorMatch] {
            regions
                .filter { $0.text.localizedCaseInsensitiveContains(anchor) }
                .map { TextAnchorMatch(anchor: anchor, region: $0) }
        }

        let matchedRequired = requirements.required.flatMap(matches)
        let matchedOptional = requirements.optional.flatMap(matches)
        let matchedForbidden = requirements.forbidden.flatMap(matches)
        let foundRequiredAnchors = Set(matchedRequired.map(\.anchor))
        let missingRequired = requirements.required.filter { !foundRequiredAnchors.contains($0) }

        let status: TextAnchorVerificationStatus
        if requirements.required.isEmpty || regions.isEmpty {
            status = .ambiguous
        } else if !missingRequired.isEmpty || !matchedForbidden.isEmpty {
            status = .unverified
        } else {
            status = .verified
        }

        return TextAnchorVerificationResult(
            status: status,
            matchedRequired: matchedRequired,
            matchedOptional: matchedOptional,
            matchedForbidden: matchedForbidden,
            missingRequired: missingRequired
        )
    }

    /// `ChangeRegionLocalizer`'s top-left pixel rect -> Vision's bottom-left normalized rect.
    /// Same formula already used for element bounds elsewhere in this package (see
    /// `NativeUIDetectionRequest.toObservation`'s `visionRect` — x unaffected, y flips).
    static func pixelRectToVisionNormalized(_ pixelRect: CGRect, imageWidth: Int, imageHeight: Int) -> CGRect {
        let width = Double(imageWidth)
        let height = Double(imageHeight)
        let normalizedX = pixelRect.minX / width
        let normalizedWidth = pixelRect.width / width
        let normalizedHeight = pixelRect.height / height
        let normalizedY = 1.0 - (pixelRect.minY + pixelRect.height) / height
        return CGRect(x: normalizedX, y: normalizedY, width: normalizedWidth, height: normalizedHeight)
    }
}
