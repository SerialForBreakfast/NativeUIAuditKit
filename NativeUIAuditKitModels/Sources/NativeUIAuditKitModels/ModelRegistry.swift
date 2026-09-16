// ModelRegistry.swift
// NativeUIAuditKitModels
//
// Central registry of available CoreML model descriptors.
// Import NativeUIAuditKitModels to resolve model metadata at runtime.

import CoreML
import Foundation

// MARK: - Model Manifest & Contract

/// An explicit mapping entry for a single output channel of the model's confidence tensor.
public enum TensorChannelAssignment: Sendable, Codable, Equatable {
    case taxonomyClass(String)
    case padding

    private enum CodingKeys: String, CodingKey {
        case type, label
    }

    public init(from decoder: any Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        let type = try container.decode(String.self, forKey: .type)
        switch type {
        case "class", "taxonomyClass":
            let label = try container.decode(String.self, forKey: .label)
            self = .taxonomyClass(label)
        case "padding":
            self = .padding
        default:
            self = .padding
        }
    }

    public func encode(to encoder: any Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        switch self {
        case .taxonomyClass(let label):
            try container.encode("taxonomyClass", forKey: .type)
            try container.encode(label, forKey: .label)
        case .padding:
            try container.encode("padding", forKey: .type)
        }
    }
}

/// Declares expected tensor shape and type for inputs or outputs.
public struct ModelTensorShapeContract: Sendable, Codable, Equatable {
    public let name: String
    /// Expected dimensions. -1 indicates a dynamic or proposal dimension (e.g. N).
    public let dimensions: [Int]
    public let dataType: String

    public init(name: String, dimensions: [Int], dataType: String = "Float32") {
        self.name = name
        self.dimensions = dimensions
        self.dataType = dataType
    }
}

/// A validated manifest declaring tensor shapes and explicit channel-to-taxonomy assignments.
public struct ModelManifest: Sendable, Codable, Equatable {
    public let modelId: String
    public let modelSHA256: String?
    public let architecture: String
    public let inputWidth: Int
    public let inputHeight: Int
    public let expectedInputs: [ModelTensorShapeContract]
    public let expectedOutputs: [ModelTensorShapeContract]
    public let tensorChannelMapping: [TensorChannelAssignment]

    public init(
        modelId: String,
        modelSHA256: String? = nil,
        architecture: String = "YOLO11n",
        inputWidth: Int = 640,
        inputHeight: Int = 640,
        expectedInputs: [ModelTensorShapeContract] = [],
        expectedOutputs: [ModelTensorShapeContract] = [],
        tensorChannelMapping: [TensorChannelAssignment]
    ) {
        self.modelId = modelId
        self.modelSHA256 = modelSHA256
        self.architecture = architecture
        self.inputWidth = inputWidth
        self.inputHeight = inputHeight
        self.expectedInputs = expectedInputs
        self.expectedOutputs = expectedOutputs
        self.tensorChannelMapping = tensorChannelMapping
    }

    public func label(forChannel channel: Int) -> String? {
        guard channel >= 0 && channel < tensorChannelMapping.count else { return nil }
        if case .taxonomyClass(let label) = tensorChannelMapping[channel] {
            return label
        }
        return nil
    }

    public var activeClassChannels: [(channel: Int, label: String)] {
        tensorChannelMapping.enumerated().compactMap { idx, assignment in
            if case .taxonomyClass(let label) = assignment {
                return (channel: idx, label: label)
            }
            return nil
        }
    }
}

/// Error thrown when a loaded MLModel does not conform to its expected manifest.
public struct ModelContractError: Error, Sendable, Equatable {
    public let reason: String
    public init(_ reason: String) { self.reason = reason }
}

/// Validates loaded MLModel instances against a declared ModelManifest.
public enum ModelManifestValidator {
    public static func validate(model: MLModel, against manifest: ModelManifest) throws {
        let desc = model.modelDescription
        let outputs = desc.outputDescriptionsByName

        // Verify all expected output tensors are present and have matching shapes
        for expected in manifest.expectedOutputs {
            guard let feature = outputs[expected.name] else {
                throw ModelContractError("Missing expected output tensor '\(expected.name)'")
            }

            if let constraint = feature.multiArrayConstraint {
                let shape = constraint.shape.map { $0.intValue }
                if expected.dimensions.count == shape.count {
                    for (dimIdx, expectedDim) in expected.dimensions.enumerated() {
                        if expectedDim != -1 && shape[dimIdx] != -1 && expectedDim != shape[dimIdx] {
                            throw ModelContractError("Output tensor '\(expected.name)' dimension \(dimIdx) mismatch: expected \(expectedDim), got \(shape[dimIdx])")
                        }
                    }
                }
            }
        }

        // Verify channel count matches manifest tensorChannelMapping
        if let confFeature = outputs["confidence"], let constraint = confFeature.multiArrayConstraint {
            let shape = constraint.shape.map { $0.intValue }
            if shape.count >= 2 {
                let channels = shape[1]
                if channels != -1 && channels != manifest.tensorChannelMapping.count {
                    throw ModelContractError("Confidence tensor channels (\(channels)) does not match manifest channel mapping count (\(manifest.tensorChannelMapping.count))")
                }
            }
        }
    }
}

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

    /// tvOS OS UI detector — YOLO11n, Phase 6b (v2.0).
    ///
    /// Evaluated on 300 held-out test images: mAP@0.5 = 0.971, Precision = 0.994, Recall = 0.975.
    /// Visual focus determination accuracy = 100.0%.
    /// Tailored for Apple TV automation and navigation with TVTestRig.
    /// Detects Home Screen tiles, Settings navigation, split views, modal alerts, tab bars,
    /// context menus, Control Center, AVKit playback controls, audio/subtitles dialogs,
    /// SharePlay cards, onscreen keyboards, and Siri overlays.
    public static let tvOS = ModelDescriptor(
        modelId: "nativeui-tvos-v2.0",
        calibrationOsRange: OSVersionRange(min: "tvOS 17.0", max: "tvOS 26.x"),
        trainedClasses: [
            "alert", "cancelAction", "collectionItem", "contextMenu",
            "destructiveButton", "imageView", "label", "listRow",
            "navigationBar", "popover", "primaryButton", "searchField",
            "secondaryButton", "segmentedControl", "sheet", "sidebar",
            "slider", "stepperControl", "tabBar", "toggle",
            "toolbar"
        ],
        trainingDatasetVersion: "run011-tvos-v2",
        minimumDeploymentTarget: "tvOS 17.0"
    )

    /// Superseded tvOS OS UI detector v1.0 prototype. Kept for consumers pinned to it.
    public static let tvOS_v1 = ModelDescriptor(
        modelId: "nativeui-tvos-v1.0",
        calibrationOsRange: OSVersionRange(min: "tvOS 17.0", max: "tvOS 26.x"),
        trainedClasses: [
            "alert", "cancelAction", "collectionItem", "imageView",
            "label", "listRow", "navigationBar", "primaryButton",
            "tabBar", "toggle"
        ],
        trainingDatasetVersion: "run010-tvos-v0",
        minimumDeploymentTarget: "tvOS 17.0"
    )

    /// Tensor-level contract for the tvOS OS UI model (`tvOS`, v2.0).
    public static let tvOSMetadata = ModelMetadata(
        modelId: "nativeui-tvos-v2.0",
        architecture: "YOLO11n",
        inputWidth: 640,
        inputHeight: 640,
        classLabels: [
            "actionSheet", "activityIndicator", "alert", "cancelAction",
            "collectionItem", "colorWell", "contextMenu", "destructiveButton",
            "disclosureGroup", "dynamicIsland", "homeIndicator", "imageView",
            "label", "link", "listRow", "mapView", "menuButton", "navigationBar",
            "pageControl", "picker", "popover", "primaryButton", "progressView",
            "refreshControl", "scrollIndicator", "searchField", "secondaryButton",
            "secureField", "segmentedControl", "sheet", "sidebar", "slider",
            "statusBar", "stepperControl", "tabBar", "textField", "toggle",
            "toolbar", "tooltip", "unknown", "webContent"
        ],
        defaultConfidenceThreshold: 0.25,
        recommendedNMSIoUThreshold: 0.30,
        mAP50: 0.9712
    )
}
