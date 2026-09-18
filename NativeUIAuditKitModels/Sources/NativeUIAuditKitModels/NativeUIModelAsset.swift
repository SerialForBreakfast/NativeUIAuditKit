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
        let model = try await MLModel.load(contentsOf: defaultModelURL, configuration: configuration)
        try ModelManifestValidator.validate(model: model, against: iOSManifest)
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
        let model = try await MLModel.load(contentsOf: tvOSModelURL, configuration: configuration)
        try ModelManifestValidator.validate(model: model, against: tvOSManifest)
        return model
    }

    // MARK: - FocusRingDetector (Stage 2)

    /// URL of the compiled FocusRingDetector model, or `nil` when not yet bundled.
    ///
    /// The `.mlmodelc` is not committed until quality gates pass
    /// (`Research/FocusRingDetectorSpec.md §5`). Call sites must handle `nil`
    /// and fall back to the heuristic `resolveTVOSFocus`.
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
            return tvOSModelURL
        case ModelRegistry.iOS.modelId, ModelRegistry.iOS_v1.modelId:
            return defaultModelURL
        default:
            return nil
        }
    }

    /// Resolves the bundled manifest for a given descriptor, if bundled.
    public static func manifest(for descriptor: ModelDescriptor) -> ModelManifest? {
        switch descriptor.modelId {
        case ModelRegistry.tvOS.modelId, ModelRegistry.tvOS_v2.modelId, ModelRegistry.tvOS_v1.modelId:
            return tvOSManifest
        case ModelRegistry.iOS.modelId, ModelRegistry.iOS_v1.modelId:
            return iOSManifest
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
        if let manifest = manifest(for: descriptor) {
            try ModelManifestValidator.validate(model: model, against: manifest)
        }
        return model
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
