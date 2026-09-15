// NativeUIRecognizing.swift
// NativeUIAuditKit
//
// Public protocol and integration contracts for consuming frameworks (e.g. ScreenAuditKit).

import CoreGraphics
import Foundation
import ImageIO

/// A recognition protocol for detecting native UI elements in screenshot data.
public protocol NativeUIRecognizing: Sendable {
    func recognizeNativeUI(
        inPNGData data: Data,
        path: String,
        sidecar: NativeUISidecar?
    ) async throws -> NativeUIObservations
}

/// The structured result of native UI element recognition.
public struct NativeUIObservations: Sendable, Codable {
    public let elements: [NativeUIElementObservation]
    public let status: NativeUIRecognitionStatus

    public init(elements: [NativeUIElementObservation], status: NativeUIRecognitionStatus) {
        self.elements = elements
        self.status = status
    }
}

/// Status of a native UI element recognition operation.
public enum NativeUIRecognitionStatus: Sendable, Equatable {
    case success
    case notRequested
    case notAvailable   // model not installed / unavailable
    case failed(String)
}

extension NativeUIRecognitionStatus: Codable {
    private enum CodingKeys: String, CodingKey {
        case type, message
    }

    public init(from decoder: any Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        let type = try container.decode(String.self, forKey: .type)
        switch type {
        case "success":
            self = .success
        case "notRequested":
            self = .notRequested
        case "notAvailable":
            self = .notAvailable
        case "failed":
            let msg = try container.decodeIfPresent(String.self, forKey: .message) ?? "Unknown failure"
            self = .failed(msg)
        default:
            self = .notRequested
        }
    }

    public func encode(to encoder: any Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        switch self {
        case .success:
            try container.encode("success", forKey: .type)
        case .notRequested:
            try container.encode("notRequested", forKey: .type)
        case .notAvailable:
            try container.encode("notAvailable", forKey: .type)
        case .failed(let msg):
            try container.encode("failed", forKey: .type)
            try container.encode(msg, forKey: .message)
        }
    }
}

/// A no-op recognizer that always returns `status: .notRequested` without performing inference.
public struct NativeUINoOpRecognizer: NativeUIRecognizing {
    public init() {}

    public func recognizeNativeUI(
        inPNGData data: Data,
        path: String,
        sidecar: NativeUISidecar?
    ) async throws -> NativeUIObservations {
        NativeUIObservations(elements: [], status: .notRequested)
    }
}

/// The standard CoreML + Vision native UI element recognizer.
public struct NativeUIDetectorRecognizer: NativeUIRecognizing {
    public let configuration: NativeUIDetectionConfiguration

    public init(configuration: NativeUIDetectionConfiguration = .default) {
        self.configuration = configuration
    }

    public func recognizeNativeUI(
        inPNGData data: Data,
        path: String,
        sidecar: NativeUISidecar?
    ) async throws -> NativeUIObservations {
        guard let source = CGImageSourceCreateWithData(data as CFData, nil),
              let cgImage = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
            return NativeUIObservations(elements: [], status: .failed("Invalid or corrupt image data"))
        }

        let request = NativeUIDetectionRequest(configuration: configuration)
        do {
            let elements = try await request.perform(on: cgImage, sidecar: sidecar)
            return NativeUIObservations(elements: elements, status: .success)
        } catch NativeUIDetectionError.imagePreprocessingFailed {
            return NativeUIObservations(elements: [], status: .failed("Image preprocessing failed"))
        } catch {
            return NativeUIObservations(elements: [], status: .failed(error.localizedDescription))
        }
    }
}
