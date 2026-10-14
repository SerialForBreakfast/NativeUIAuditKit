import CoreGraphics
import Foundation
import NativeUIAuditKitModels
@_exported import NativeUIAuditKitRuntime

/// The compatibility product keeps the existing bundled defaults.
public struct NativeUIBundledModelProvider: NativeUIModelProviding {
    public let allowsHeuristicFocusFallback = true
    public init() {}

    public func loadDetector(for platform: NativeUIPlatform) async throws -> PreloadedModel {
        let tv = platform == .tvOS
        let model = try await (tv ? NativeUIModelAsset.loadTVOSModel() : NativeUIModelAsset.loadModel())
        return PreloadedModel(model: model,
            metadata: tv ? NativeUIModelAsset.tvOSMetadata : NativeUIModelAsset.metadata,
            manifest: try NativeUIModelAsset.requiredManifest(forTVOS: tv))
    }

    public func focusModelURL() throws -> URL? { NativeUIModelAsset.focusRingDetectorURL }

    // The signed resource selection stays fixed for this process.
    private static let iosSelection = Result { try selection(tv: false) }
    private static let tvSelection = Result { try selection(tv: true) }
    private static func selection(tv: Bool) throws -> NativeUILocalDetector {
        let url = try NativeUIModelAsset.requiredModelURL(forTVOS: tv)
        return try NativeUILocalDetector(url: url, expectedDigest: NativeUILocalDetector.digest(at: url),
            manifest: NativeUIModelAsset.requiredManifest(forTVOS: tv),
            metadata: tv ? NativeUIModelAsset.tvOSMetadata : NativeUIModelAsset.metadata)
    }
    public func detectorCacheIdentity(for platform: NativeUIPlatform) throws -> String? {
        try (platform == .tvOS ? Self.tvSelection : Self.iosSelection).get().cacheIdentity()
    }
}

extension NativeUIDetectionRequest {
    public init(configuration: NativeUIDetectionConfiguration = .default,
                textRecognitionHandler: (@Sendable (CGImage) async throws -> [RecognizedTextRegion])? = nil) {
        self.init(modelProvider: NativeUIBundledModelProvider(), configuration: configuration,
                  textRecognitionHandler: textRecognitionHandler)
    }
}

extension NativeUIDetectionSession {
    public init(configuration: NativeUIDetectionConfiguration = .default,
                textRecognitionHandler: (@Sendable (CGImage) async throws -> [RecognizedTextRegion])? = nil) {
        self.init(modelProvider: NativeUIBundledModelProvider(), configuration: configuration,
                  textRecognitionHandler: textRecognitionHandler)
    }
}

extension NativeUIDetectorRecognizer {
    public init(configuration: NativeUIDetectionConfiguration = .default,
                textRecognitionHandler: (@Sendable (CGImage) async throws -> [RecognizedTextRegion])? = nil) {
        self.init(modelProvider: NativeUIBundledModelProvider(), configuration: configuration,
                  textRecognitionHandler: textRecognitionHandler)
    }
}
