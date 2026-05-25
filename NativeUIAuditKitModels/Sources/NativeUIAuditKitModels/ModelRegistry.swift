// ModelRegistry.swift
// NativeUIAuditKitModels
//
// Central registry of available CoreML model descriptors.
// Import NativeUIAuditKitModels to resolve model metadata at runtime.

import Foundation

/// A descriptor for one trained CoreML model in the NativeUIAuditKit family.
public struct ModelDescriptor: Sendable, Codable, Equatable {
    /// Stable identifier used for caching and version comparisons.
    public let modelId: String
    /// Inclusive OS version range this model was calibrated against.
    public let calibrationOsRange: OSVersionRange
    /// Alphabetically sorted list of element type rawValues the model detects.
    public let trainedClasses: [String]
    /// Semver string of the dataset used for training (from manifest.json).
    public let trainingDatasetVersion: String
    /// Minimum OS version required to run this model.
    public let minimumDeploymentTarget: String

    public init(
        modelId: String,
        calibrationOsRange: OSVersionRange,
        trainedClasses: [String],
        trainingDatasetVersion: String,
        minimumDeploymentTarget: String
    ) {
        self.modelId = modelId
        self.calibrationOsRange = calibrationOsRange
        self.trainedClasses = trainedClasses.sorted()
        self.trainingDatasetVersion = trainingDatasetVersion
        self.minimumDeploymentTarget = minimumDeploymentTarget
    }
}

/// An inclusive OS version range, e.g. ("iOS 17.0", "iOS 26.x").
public struct OSVersionRange: Sendable, Codable, Equatable {
    public let min: String
    public let max: String

    public init(min: String, max: String) {
        self.min = min
        self.max = max
    }
}

/// Registry of shipped model descriptors.
///
/// Add new descriptors here as additional platform models (tvOS, macOS) are trained.
public enum ModelRegistry {

    /// iOS + iPadOS 5-class prototype (alert, navigationBar, primaryButton, textField, toggle).
    ///
    /// v1.0 training notes:
    /// - Trained with horizontal strip tiling (22% height, 50% overlap) to fix anchor-assignment
    ///   failure for navigationBar and textField (BP-26).
    /// - Full-image entries also included for alert and toggle coverage.
    public static let iOS = ModelDescriptor(
        modelId: "nativeui-ios-v1.0",
        calibrationOsRange: OSVersionRange(min: "iOS 17.0", max: "iOS 26.x"),
        trainedClasses: ["alert", "navigationBar", "primaryButton", "textField", "toggle"],
        trainingDatasetVersion: "unknown",   // updated when manifest.json datasetVersion is set
        minimumDeploymentTarget: "iOS 17.0"
    )
}
