// NativeUIModelAsset.swift
// NativeUIAuditKitModels
//
// The zero-config entry point for consumers: resolves the bundled CoreML model and its
// tensor-level metadata without any --model flag, environment variable, or sibling-directory
// discovery. Import NativeUIAuditKitModels, call loadModel() (or defaultModelURL if you need
// the URL for your own MLModel(contentsOf:) call), read `metadata` for input size / class
// order / thresholds instead of hardcoding them.

import CoreML
import Foundation

public enum NativeUIModelAsset {

    /// URL of the compiled (.mlmodelc) model bundled with this package.
    public static var defaultModelURL: URL {
        guard let url = Bundle.module.url(forResource: "NativeUIDetector_v2", withExtension: "mlmodelc") else {
            fatalError("NativeUIDetector_v2.mlmodelc missing from NativeUIAuditKitModels bundle resources")
        }
        return url
    }

    /// Tensor-level contract (input size, class label order, thresholds) for the bundled model.
    public static var metadata: ModelMetadata { ModelRegistry.v2Metadata }

    /// A `MLModelConfiguration` pre-configured for Apple Neural Engine + GPU acceleration.
    public static func makeConfiguration(
        computeUnits: MLComputeUnits = .all,
        allowLowPrecision: Bool = true
    ) -> MLModelConfiguration {
        let config = MLModelConfiguration()
        config.computeUnits = computeUnits
        config.allowLowPrecisionAccumulationOnGPU = allowLowPrecision
        return config
    }

    /// Manifest for the default (iOS) model loaded from bundled resources.
    public static var iOSManifest: ModelManifest {
        loadManifest(named: "model_manifest_ios_v2")
    }

    /// Loads the bundled model with the given configuration (defaults to ANE/GPU) and validates against its manifest.
    public static func loadModel(
        configuration: MLModelConfiguration = makeConfiguration()
    ) async throws -> MLModel {
        let manifest = try requiredManifest(forTVOS: false)
        let model = try await MLModel.load(contentsOf: requiredModelURL(forTVOS: false), configuration: configuration)
        try ModelManifestValidator.validate(model: model, against: manifest)
        return model
    }

    /// URL of the compiled (.mlmodelc) tvOS model bundled with this package.
    public static var tvOSModelURL: URL {
        guard let url = Bundle.module.url(forResource: "NativeUIModel_tvOS", withExtension: "mlmodelc") else {
            fatalError("NativeUIModel_tvOS.mlmodelc missing from NativeUIAuditKitModels bundle resources")
        }
        return url
    }

    /// Tensor-level contract (input size, class label order, thresholds) for the bundled tvOS model.
    public static var tvOSMetadata: ModelMetadata { ModelRegistry.tvOSMetadata }

    /// Manifest for the tvOS model loaded from bundled resources.
    public static var tvOSManifest: ModelManifest {
        loadManifest(named: "model_manifest_tvos_v1")
    }

    /// Loads the bundled tvOS model with the given configuration (defaults to ANE/GPU) and validates against its manifest.
    public static func loadTVOSModel(
        configuration: MLModelConfiguration = makeConfiguration()
    ) async throws -> MLModel {
        let manifest = try requiredManifest(forTVOS: true)
        let model = try await MLModel.load(contentsOf: requiredModelURL(forTVOS: true), configuration: configuration)
        try ModelManifestValidator.validate(model: model, against: manifest)
        return model
    }

    // MARK: - FocusRingDetector (Stage 2)

    /// URL of the compiled FocusRingDetector v0.1 graph, or `nil` if the resource was stripped.
    ///
    /// v0.1 is bundled (`Package.swift` copies `FocusRingDetector.mlmodelc`). Call sites still
    /// handle `nil` and fall back to the heuristic `resolveTVOSFocus`.
    public static var focusRingDetectorURL: URL? {
        Bundle.module.url(forResource: "FocusRingDetector", withExtension: "mlmodelc")
    }

    /// Loads the FocusRingDetector model, or returns `nil` when the compiled
    /// resource is absent. Never throws on absence — only throws on a corrupted
    /// file that exists but cannot be loaded.
    public static func loadFocusRingDetector(
        configuration: MLModelConfiguration = makeConfiguration()
    ) async throws -> MLModel? {
        guard let url = focusRingDetectorURL else { return nil }
        return try await MLModel.load(contentsOf: url, configuration: configuration)
    }

    /// Resolves the bundled model URL for a given descriptor, if bundled.
    public static func modelURL(for descriptor: ModelDescriptor) -> URL? {
        switch descriptor.modelId {
        case ModelRegistry.tvOS.modelId, ModelRegistry.tvOS_v2.modelId, ModelRegistry.tvOS_v1.modelId:
            return try? requiredModelURL(forTVOS: true)
        case ModelRegistry.iOS.modelId, ModelRegistry.iOS_v1.modelId:
            return try? requiredModelURL(forTVOS: false)
        default:
            return nil
        }
    }

    /// Resolves the bundled manifest for a given descriptor, if bundled.
    public static func manifest(for descriptor: ModelDescriptor) -> ModelManifest? {
        switch descriptor.modelId {
        case ModelRegistry.tvOS.modelId, ModelRegistry.tvOS_v2.modelId, ModelRegistry.tvOS_v1.modelId:
            return try? requiredManifest(forTVOS: true)
        case ModelRegistry.iOS.modelId, ModelRegistry.iOS_v1.modelId:
            return try? requiredManifest(forTVOS: false)
        default:
            return nil
        }
    }

    /// Loads a bundled model by its ModelDescriptor and validates against its manifest if available.
    public static func loadModel(
        descriptor: ModelDescriptor,
        configuration: MLModelConfiguration = makeConfiguration()
    ) async throws -> MLModel {
        guard let url = modelURL(for: descriptor) else {
            throw NSError(
                domain: "NativeUIAuditKitModels",
                code: 404,
                userInfo: [NSLocalizedDescriptionKey: "No bundled model asset found for descriptor '\(descriptor.modelId)'"]
            )
        }
        let model = try await MLModel.load(contentsOf: url, configuration: configuration)
        let tvOS = [ModelRegistry.tvOS.modelId, ModelRegistry.tvOS_v2.modelId, ModelRegistry.tvOS_v1.modelId].contains(descriptor.modelId)
        try ModelManifestValidator.validate(model: model, against: requiredManifest(forTVOS: tvOS))
        return model
    }

    /// Recoverable lookup for mandatory detector resources; never returns empty detections.
    public static func requiredModelURL(forTVOS: Bool) throws -> URL {
        let name = forTVOS ? "NativeUIModel_tvOS" : "NativeUIDetector_v2"
        guard let url = Bundle.module.url(forResource: name, withExtension: "mlmodelc") else {
            throw NSError(domain: "NativeUIAuditKitModels", code: 404,
                userInfo: [NSLocalizedDescriptionKey: "Required detector resource is missing"])
        }
        return url
    }

    /// Recoverable manifest access. Legacy nonthrowing properties remain source-compatible.
    public static func requiredManifest(forTVOS: Bool) throws -> ModelManifest {
        let name = forTVOS ? "model_manifest_tvos_v1" : "model_manifest_ios_v2"
        return try readRequiredManifest(at: Bundle.module.url(forResource: name, withExtension: "json"))
    }

    internal static func readRequiredManifest(at url: URL?) throws -> ModelManifest {
        guard let url else {
            throw NSError(domain: "NativeUIAuditKitModels", code: 404,
                userInfo: [NSLocalizedDescriptionKey: "Required detector manifest is missing"])
        }
        do {
            let size = try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? Int.max
            guard size <= 65_536 else { throw CocoaError(.fileReadCorruptFile) }
            return try JSONDecoder().decode(ModelManifest.self, from: Data(contentsOf: url))
        } catch {
            throw NSError(domain: "NativeUIAuditKitModels", code: 422,
                userInfo: [NSLocalizedDescriptionKey: "Required detector manifest is invalid or unreadable"])
        }
    }

    private static func loadManifest(named name: String) -> ModelManifest {
        guard let url = Bundle.module.url(forResource: name, withExtension: "json") else {
            fatalError("\(name).json missing from NativeUIAuditKitModels bundle resources")
        }
        do {
            let data = try Data(contentsOf: url)
            return try JSONDecoder().decode(ModelManifest.self, from: data)
        } catch {
            fatalError("Failed to decode \(name).json: \(error.localizedDescription)")
        }
    }
}
