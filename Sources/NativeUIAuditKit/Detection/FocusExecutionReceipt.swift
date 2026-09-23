import Foundation

/// Versioned execution diagnostics, not action authority or capture/label provenance.
public struct FocusExecutionReceipt: Sendable, Codable, Equatable {
    /// Receipt format; currently one.
    public let version: Int
    /// Selected resolver; this alone does not prove a prediction succeeded.
    public let backend: Backend
    /// Stable fallback reason (disabled, model_missing, or model_load_failed), when applicable.
    public let fallbackReason: String?
    /// Load-bracketed compiled-tree digest; nil for custom/unidentified models.
    public let modelDigest: String?
    /// Digest algorithm, separate from a descriptor or model metadata label.
    public let modelDigestAlgorithm: String?
    /// Actual selection policy identifier, not a model quality version.
    public let policy: String
    /// Model probability or heuristic score threshold for the selected policy.
    public let threshold: Double?
    /// Model ambiguity threshold or heuristic winner margin, according to policy.
    public let secondaryThreshold: Double?
    /// One disposition per focus-stage input observation; later OCR-only nodes are not included.
    public let candidates: [Candidate]
    /// Number of model calls attempted; crop failures are excluded.
    public var attemptedPredictions: Int { candidates.filter { [.scored, .predictionFailed].contains($0.disposition) }.count }
    /// Number of successful, finite model scores.
    public var successfulPredictions: Int { candidates.filter { $0.disposition == .scored }.count }
    /// Model calls that threw or returned invalid output; excludes rejected crops.
    public var failedPredictions: Int { candidates.filter { $0.disposition == .predictionFailed }.count }
    /// Only true for nonempty, fully scored model candidates. Never true for heuristics.
    public var modelScoringComplete: Bool {
        backend == .coreML && successfulPredictions > 0 &&
        candidates.allSatisfy { [.scored, .unsupportedRole].contains($0.disposition) }
    }

    /// Resolver selected by this request.
    public enum Backend: String, Sendable, Codable {
        /// Model-based crop classifier selected.
        case coreML
        /// Legacy visual heuristic selected.
        case heuristic
        /// Focus processing not requested for this platform.
        case notRequested
        /// Selected model policy is invalid; inference was not attempted.
        case unavailable
    }
    /// Scoring outcome independent of the final focus winner.
    public enum Disposition: String, Sendable, Codable {
        /// A finite model result was produced.
        case scored
        /// The crop could not be constructed; model was not invoked.
        case cropRejected
        /// Prediction threw or returned invalid values.
        case predictionFailed
        /// Role is outside the resolver's supported focusable set.
        case unsupportedRole
        /// Legacy heuristic output; not proof of a valid model score or valid heuristic crop.
        case heuristicResult
        /// No focus work for this observation/platform.
        case notRequested
        /// Invalid thresholds prevented inference; not a prediction attempt.
        case policyRejected
    }
    /// One observation's execution outcome, with output values when actually available.
    public struct Candidate: Sendable, Codable, Equatable {
        /// Corresponding observation ID.
        public let observationID: UUID
        /// Execution disposition.
        public let disposition: Disposition
        /// Model probability only, never heuristic score.
        public let probability: Double?
        /// Final focus decision; nil can mean ambiguous or unassessed.
        public let isFocused: Bool?
    }

    internal init(backend: Backend, fallbackReason: String? = nil, modelDigest: String? = nil,
                  policy: String, threshold: Double? = nil, secondaryThreshold: Double? = nil,
                  candidates: [Candidate]) {
        version = 1; self.backend = backend; self.fallbackReason = fallbackReason
        self.modelDigest = modelDigest
        modelDigestAlgorithm = modelDigest == nil ? nil : "compiled-tree-sha256-v1"
        self.policy = policy; self.threshold = threshold; self.secondaryThreshold = secondaryThreshold
        self.candidates = candidates
    }

    private enum CodingKeys: String, CodingKey {
        case version, backend, fallbackReason, modelDigest, modelDigestAlgorithm, policy
        case threshold, secondaryThreshold, candidates
        case attemptedPredictions, successfulPredictions, failedPredictions, modelScoringComplete
    }

    /// Decodes version-one evidence, rejecting inconsistent execution accounting.
    public init(from decoder: any Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        version = try c.decode(Int.self, forKey: .version)
        backend = try c.decode(Backend.self, forKey: .backend)
        fallbackReason = try c.decodeIfPresent(String.self, forKey: .fallbackReason)
        modelDigest = try c.decodeIfPresent(String.self, forKey: .modelDigest)
        modelDigestAlgorithm = try c.decodeIfPresent(String.self, forKey: .modelDigestAlgorithm)
        policy = try c.decode(String.self, forKey: .policy)
        threshold = try c.decodeIfPresent(Double.self, forKey: .threshold)
        secondaryThreshold = try c.decodeIfPresent(Double.self, forKey: .secondaryThreshold)
        candidates = try c.decode([Candidate].self, forKey: .candidates)
        let validCandidates = candidates.allSatisfy { candidate in
            let allowed: Bool
            switch backend {
            case .coreML: allowed = [.scored, .predictionFailed, .cropRejected, .unsupportedRole].contains(candidate.disposition)
            case .heuristic: allowed = [.heuristicResult, .unsupportedRole].contains(candidate.disposition)
            case .notRequested: allowed = candidate.disposition == .notRequested
            case .unavailable: allowed = candidate.disposition == .policyRejected
            }
            guard allowed else { return false }
            if candidate.disposition == .scored {
                guard let p = candidate.probability else { return false }
                return p.isFinite && (0...1).contains(p)
            }
            return candidate.probability == nil
        }
        let validDigest = modelDigest.map { digest in
            digest.count == 64 && digest.utf8.allSatisfy { (48...57).contains($0) || (97...102).contains($0) }
                && modelDigestAlgorithm == "compiled-tree-sha256-v1" && [.coreML, .unavailable].contains(backend)
        } ?? (modelDigestAlgorithm == nil)
        guard version == 1, validCandidates, validDigest,
              Set(candidates.map(\.observationID)).count == candidates.count,
              [threshold, secondaryThreshold].compactMap({ $0 }).allSatisfy({ $0.isFinite }),
              try c.decode(Int.self, forKey: .attemptedPredictions) == attemptedPredictions,
              try c.decode(Int.self, forKey: .successfulPredictions) == successfulPredictions,
              try c.decode(Int.self, forKey: .failedPredictions) == failedPredictions,
              try c.decode(Bool.self, forKey: .modelScoringComplete) == modelScoringComplete else {
            throw DecodingError.dataCorrupted(.init(codingPath: decoder.codingPath,
                debugDescription: "Unsupported or inconsistent focus execution receipt"))
        }
    }

    /// Encodes candidate-derived counts explicitly for non-Swift consumers.
    public func encode(to encoder: any Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        try c.encode(version, forKey: .version)
        try c.encode(backend, forKey: .backend)
        try c.encodeIfPresent(fallbackReason, forKey: .fallbackReason)
        try c.encodeIfPresent(modelDigest, forKey: .modelDigest)
        try c.encodeIfPresent(modelDigestAlgorithm, forKey: .modelDigestAlgorithm)
        try c.encode(policy, forKey: .policy)
        try c.encodeIfPresent(threshold, forKey: .threshold)
        try c.encodeIfPresent(secondaryThreshold, forKey: .secondaryThreshold)
        try c.encode(candidates, forKey: .candidates)
        try c.encode(attemptedPredictions, forKey: .attemptedPredictions)
        try c.encode(successfulPredictions, forKey: .successfulPredictions)
        try c.encode(failedPredictions, forKey: .failedPredictions)
        try c.encode(modelScoringComplete, forKey: .modelScoringComplete)
    }
}
