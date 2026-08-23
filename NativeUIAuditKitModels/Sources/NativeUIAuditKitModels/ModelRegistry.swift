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

/// Tensor-level contract for a model that ships with `NativeUIAuditKitModels` — the single
/// source of truth for input size, class label order, and recommended inference thresholds.
/// Consumers should read these values rather than hardcoding them, so a future model update
/// (different input size, reordered classes) can't silently produce wrong bounding boxes.
public struct ModelMetadata: Sendable, Codable, Equatable {
    public let modelId: String
    public let architecture: String
    public let inputWidth: Int
    public let inputHeight: Int
    /// Class labels in the exact order the model's output tensor uses — NOT sorted.
    public let classLabels: [String]
    public let defaultConfidenceThreshold: Float
    public let recommendedNMSIoUThreshold: Float
    public let mAP50: Double

    public init(
        modelId: String,
        architecture: String,
        inputWidth: Int,
        inputHeight: Int,
        classLabels: [String],
        defaultConfidenceThreshold: Float,
        recommendedNMSIoUThreshold: Float,
        mAP50: Double
    ) {
        self.modelId = modelId
        self.architecture = architecture
        self.inputWidth = inputWidth
        self.inputHeight = inputHeight
        self.classLabels = classLabels
        self.defaultConfidenceThreshold = defaultConfidenceThreshold
        self.recommendedNMSIoUThreshold = recommendedNMSIoUThreshold
        self.mAP50 = mAP50
    }
}

/// Registry of shipped model descriptors.
///
/// Add new descriptors here as additional platform models (tvOS, macOS) are trained.
public enum ModelRegistry {

    /// iOS + iPadOS 5-class prototype — YOLO11n, current default (v2.0).
    ///
    /// Evaluated on 1,394 held-out validation images: mAP@0.5 = 0.935 (CoreML) / 0.968 (.pt).
    /// Anchor-free architecture; no strip tiling or per-class pass routing required (unlike v1).
    /// See Research/ExperimentLog.md Run 006 for full training/eval history.
    public static let iOS = ModelDescriptor(
        modelId: "nativeui-ios-v2.0",
        calibrationOsRange: OSVersionRange(min: "iOS 17.0", max: "iOS 26.x"),
        trainedClasses: ["alert", "navigationBar", "primaryButton", "textField", "toggle"],
        trainingDatasetVersion: "run006-20632entries",
        minimumDeploymentTarget: "iOS 17.0"
    )

    /// Tensor-level contract for the current default model (`iOS`, v2.0). Use this — not
    /// hardcoded constants — for input size, class order, and inference thresholds.
    public static let v2Metadata = ModelMetadata(
        modelId: "nativeui-ios-v2.0",
        architecture: "YOLO11n",
        inputWidth: 640,
        inputHeight: 640,
        classLabels: ["alert", "navigationBar", "primaryButton", "textField", "toggle"],
        defaultConfidenceThreshold: 0.25,
        recommendedNMSIoUThreshold: 0.30,
        mAP50: 0.9346
    )

    /// Superseded Create ML objectPrint model (trained 2026-05-28). Kept for consumers
    /// pinned to it; `iOS` now points at the YOLO11n v2.0 model by default.
    public static let iOS_v1 = ModelDescriptor(
        modelId: "nativeui-ios-v1.0",
        calibrationOsRange: OSVersionRange(min: "iOS 17.0", max: "iOS 26.x"),
        trainedClasses: ["alert", "navigationBar", "primaryButton", "textField", "toggle"],
        trainingDatasetVersion: "unknown",
        minimumDeploymentTarget: "iOS 17.0"
    )
}
