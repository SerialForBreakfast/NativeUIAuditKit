import CoreML
import CryptoKit
import Foundation
@_exported import NativeUIModelContracts

/// A provider selects models explicitly. The runtime never downloads models.
/// Keep the selected models unchanged for the lifetime of a session.
public protocol NativeUIModelProviding: Sendable {
    var allowsHeuristicFocusFallback: Bool { get }
    func loadDetector(for platform: NativeUIPlatform) async throws -> PreloadedModel
    func focusModelURL() throws -> URL?
    func detectorCacheIdentity(for platform: NativeUIPlatform) throws -> String?
}

public enum NativeUIModelAvailabilityError: Error, Sendable, Equatable {
    case unavailable(String)
    case changedArtifact
    case unsupportedPreprocessing
}

/// A local model selection with a checked identity.
public struct NativeUILocalDetector: Sendable {
    public let url: URL
    public let artifactDigest: String
    public let manifest: ModelManifest
    public let metadata: ModelMetadata
    public let preprocessing: String

    public init(url: URL, expectedDigest: String, manifest: ModelManifest,
                metadata: ModelMetadata, preprocessing: String = "yolo-letterbox-v1") throws {
        guard preprocessing == "yolo-letterbox-v1" else {
            throw NativeUIModelAvailabilityError.unsupportedPreprocessing
        }
        guard try FocusModelIdentity.digest(url) == expectedDigest else {
            throw NativeUIModelAvailabilityError.changedArtifact
        }
        try manifest.validateTaxonomyBinding()
        guard manifest.modelId == metadata.modelId,
              manifest.inputWidth == metadata.inputWidth,
              manifest.inputHeight == metadata.inputHeight else {
            throw ModelContractError("Model metadata does not match the manifest")
        }
        self.url = url
        self.artifactDigest = expectedDigest
        self.manifest = manifest
        self.metadata = metadata
        self.preprocessing = preprocessing
    }

    public static func digest(at url: URL) throws -> String {
        try FocusModelIdentity.digest(url)
    }

    public func cacheIdentity() throws -> String {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.sortedKeys]
        let contract = try encoder.encode(manifest) + encoder.encode(metadata) + Data(preprocessing.utf8)
        return artifactDigest + ":" + SHA256.hash(data: contract).map { String(format: "%02x", $0) }.joined()
    }

    fileprivate func load() async throws -> PreloadedModel {
        guard try Self.digest(at: url) == artifactDigest else {
            throw NativeUIModelAvailabilityError.changedArtifact
        }
        let configuration = MLModelConfiguration()
        configuration.allowLowPrecisionAccumulationOnGPU = true
        let model = try await MLModel.load(contentsOf: url, configuration: configuration)
        guard try Self.digest(at: url) == artifactDigest else {
            throw NativeUIModelAvailabilityError.changedArtifact
        }
        try ModelManifestValidator.validate(model: model, against: manifest)
        return PreloadedModel(model: model, metadata: metadata, manifest: manifest)
    }
}

/// Models stay fixed for this provider. Create a new session to select another version.
public struct NativeUILocalModelProvider: NativeUIModelProviding {
    public let allowsHeuristicFocusFallback: Bool
    public let iOS: NativeUILocalDetector?
    public let tvOS: NativeUILocalDetector?
    private let focusURL: URL?
    private let focusDigest: String?

    public init(iOS: NativeUILocalDetector? = nil, tvOS: NativeUILocalDetector? = nil,
                focusURL: URL? = nil, focusDigest: String? = nil,
                allowsHeuristicFocusFallback: Bool = false) throws {
        guard (focusURL == nil) == (focusDigest == nil) else {
            throw NativeUIModelAvailabilityError.unavailable("Focus model identity")
        }
        guard iOS == nil || iOS?.manifest.modelId == "nativeui-ios-v2.0",
              tvOS == nil || tvOS?.manifest.modelId == "nativeui-tvos-v3.0" else {
            throw ModelContractError("The selected detector does not match the screenshot domain")
        }
        if let focusURL, let focusDigest {
            guard try FocusModelIdentity.digest(focusURL) == focusDigest else {
                throw NativeUIModelAvailabilityError.changedArtifact
            }
        }
        self.iOS = iOS
        self.allowsHeuristicFocusFallback = allowsHeuristicFocusFallback
        self.tvOS = tvOS
        self.focusURL = focusURL
        self.focusDigest = focusDigest
    }

    public func loadDetector(for platform: NativeUIPlatform) async throws -> PreloadedModel {
        guard let selected = platform == .tvOS ? tvOS : iOS else {
            throw NativeUIModelAvailabilityError.unavailable(platform == .tvOS ? "tvOS detector" : "iOS detector")
        }
        return try await selected.load()
    }

    public func focusModelURL() throws -> URL? {
        if let focusURL, let focusDigest {
            guard try FocusModelIdentity.digest(focusURL) == focusDigest else {
                throw NativeUIModelAvailabilityError.changedArtifact
            }
        }
        return focusURL
    }

    public func detectorCacheIdentity(for platform: NativeUIPlatform) throws -> String? {
        try (platform == .tvOS ? tvOS : iOS)?.cacheIdentity()
    }
}

extension NativeUIModelProviding {
    public var allowsHeuristicFocusFallback: Bool { false }
    public func detectorCacheIdentity(for platform: NativeUIPlatform) throws -> String? { nil }
    func loadFocusWithEvidence() async -> FocusClassifierLoad {
        do {
            let result = await NativeUIDetectionRequest.loadFocusClassifierWithEvidence(url: try focusModelURL())
            _ = try focusModelURL()
            return result
        } catch {
            return FocusClassifierLoad(classifier: nil, fallbackReason: "model_identity_failed")
        }
    }
}
