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

    /// Loads the bundled model with the given configuration (defaults to ANE/GPU).
    public static func loadModel(
        configuration: MLModelConfiguration = makeConfiguration()
    ) async throws -> MLModel {
        try await MLModel.load(contentsOf: defaultModelURL, configuration: configuration)
    }
}
