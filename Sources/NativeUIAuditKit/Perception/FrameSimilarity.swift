// FrameSimilarity.swift
// NativeUIAuditKit
//
// Cheapest gate in the detection pipeline (Track 4, TASK-PERCEP-01): compare the current
// frame against the last verified frame using Vision feature prints before spending OCR or
// CoreML inference on it. A near-zero distance means the screen is visually unchanged.
//
// This wraps a similarity *measurement*, not a policy. `FrameSimilarityCache` supplies the
// stateful "is this still the same screen" convenience; callers own the threshold, because the
// right cutoff is corpus-dependent (see `scripts/derive_frame_similarity_threshold.swift`) and
// must never be a guessed constant baked into the library.

import CoreGraphics
import Foundation
import Vision

/// Errors surfaced while computing a Vision feature-print distance.
public enum FrameSimilarityError: Error, Sendable, Equatable {
    /// `VNGenerateImageFeaturePrintRequest` produced no usable observation for an image.
    case noFeaturePrint
}

/// Computes a Vision feature-print distance between two images.
///
/// Lower distance means more visually similar; a same-pixel image compared to itself is at or
/// extremely close to `0.0`. This measures perceptual similarity, not pixel-exact equality —
/// two frames that differ only in a moved focus ring will register as more different than two
/// truly identical frames, but by how much is empirical, not assumed.
public struct FrameSimilarity: Sendable {
    public init() {}

    /// Vision feature-print distance between `lhs` and `rhs`. Symmetric:
    /// `distance(a, to: b) == distance(b, to: a)`.
    public func distance(_ lhs: CGImage, to rhs: CGImage) throws -> Float {
        let lhsPrint = try featurePrint(for: lhs)
        let rhsPrint = try featurePrint(for: rhs)
        var result: Float = 0
        try lhsPrint.computeDistance(&result, to: rhsPrint)
        return result
    }

    /// Extracted so `FrameSimilarityCache` can store the observation instead of the source
    /// image, and so `distance(_:to:)` only computes each side once.
    func featurePrint(for image: CGImage) throws -> VNFeaturePrintObservation {
        let request = VNGenerateImageFeaturePrintRequest()
        let handler = VNImageRequestHandler(cgImage: image, options: [:])
        try handler.perform([request])
        guard let observation = request.results?.first as? VNFeaturePrintObservation else {
            throw FrameSimilarityError.noFeaturePrint
        }
        return observation
    }
}

/// Per-navigation-state cache of the last verified frame's feature print.
///
/// `stateKey` is caller-defined — typically a navigation-graph node identifier. This does not
/// classify *where* a frame changed (see the planned change-region localizer, TASK-PERCEP-02);
/// it only answers "is this still the same screen I already processed."
public actor FrameSimilarityCache {
    private let similarity: FrameSimilarity
    private var lastFeaturePrint: [String: VNFeaturePrintObservation] = [:]

    public init(similarity: FrameSimilarity = FrameSimilarity()) {
        self.similarity = similarity
    }

    /// Compares `image` against the cached frame for `stateKey` (if any), then updates the
    /// cache to `image` regardless of the result — the caller doesn't need a separate `update`
    /// call, since a "changed" verdict still means `image` is now the new reference frame.
    ///
    /// A `stateKey` seen for the first time always returns `false` (nothing to compare against
    /// yet) and seeds the cache.
    ///
    /// - Parameters:
    ///   - image: The newly captured frame.
    ///   - stateKey: Identifies the navigation state this frame belongs to.
    ///   - threshold: Maximum distance still considered "unchanged." Caller-supplied —
    ///     see `scripts/derive_frame_similarity_threshold.swift` before picking one.
    @discardableResult
    public func isUnchanged(_ image: CGImage, forState stateKey: String, threshold: Float) throws -> Bool {
        let newPrint = try similarity.featurePrint(for: image)
        defer { lastFeaturePrint[stateKey] = newPrint }

        guard let previousPrint = lastFeaturePrint[stateKey] else {
            return false
        }
        var distance: Float = 0
        try newPrint.computeDistance(&distance, to: previousPrint)
        return distance <= threshold
    }

    /// Drops the cached frame for `stateKey`, forcing the next `isUnchanged` call for it to
    /// return `false`. Useful when a caller knows a state's expected content changed (e.g. a
    /// live data refresh) independent of anything this cache observed.
    public func invalidate(stateKey: String) {
        lastFeaturePrint.removeValue(forKey: stateKey)
    }
}
