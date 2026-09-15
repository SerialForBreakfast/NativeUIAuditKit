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

// MARK: - Modality Health

/// Granular status of an individual recognition modality (detector, OCR, focus, audit).
public enum ModalityStatus: Sendable, Equatable, Codable {
    case available
    case notRequested
    case empty
    case failed(reason: String, domain: String?, code: Int?)

    public static func failed(reason: String) -> ModalityStatus {
        .failed(reason: reason, domain: nil, code: nil)
    }

    public var isFailed: Bool {
        if case .failed = self { return true }
        return false
    }

    public var failureReason: String? {
        if case .failed(let reason, _, _) = self { return reason }
        return nil
    }

    private enum CodingKeys: String, CodingKey {
        case status, reason, domain, code
    }

    public init(from decoder: any Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        let status = try container.decode(String.self, forKey: .status)
        switch status {
        case "available":
            self = .available
        case "notRequested":
            self = .notRequested
        case "empty":
            self = .empty
        case "failed":
            let reason = try container.decodeIfPresent(String.self, forKey: .reason) ?? "Unknown failure"
            let domain = try container.decodeIfPresent(String.self, forKey: .domain)
            let code = try container.decodeIfPresent(Int.self, forKey: .code)
            self = .failed(reason: reason, domain: domain, code: code)
        default:
            self = .notRequested
        }
    }

    public func encode(to encoder: any Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        switch self {
        case .available:
            try container.encode("available", forKey: .status)
        case .notRequested:
            try container.encode("notRequested", forKey: .status)
        case .empty:
            try container.encode("empty", forKey: .status)
        case .failed(let reason, let domain, let code):
            try container.encode("failed", forKey: .status)
            try container.encode(reason, forKey: .reason)
            try container.encodeIfPresent(domain, forKey: .domain)
            try container.encodeIfPresent(code, forKey: .code)
        }
    }
}

/// Truthful health evaluation for each subsystem participating in a detection request.
public struct ModalityHealth: Sendable, Equatable, Codable {
    public var detector: ModalityStatus
    public var ocr: ModalityStatus
    public var focus: ModalityStatus
    public var audit: ModalityStatus

    public init(
        detector: ModalityStatus = .available,
        ocr: ModalityStatus = .available,
        focus: ModalityStatus = .available,
        audit: ModalityStatus = .available
    ) {
        self.detector = detector
        self.ocr = ocr
        self.focus = focus
        self.audit = audit
    }

    public static let `default` = ModalityHealth()

    public var hasAnyFailure: Bool {
        detector.isFailed || ocr.isFailed || focus.isFailed || audit.isFailed
    }
}

/// The structured result of native UI element recognition.
public struct NativeUIObservations: Sendable, Codable {
    public let elements: [NativeUIElementObservation]
    public let status: NativeUIRecognitionStatus
    public let modalityHealth: ModalityHealth

    public init(
        elements: [NativeUIElementObservation],
        status: NativeUIRecognitionStatus,
        modalityHealth: ModalityHealth = .default
    ) {
        self.elements = elements
        self.status = status
        self.modalityHealth = modalityHealth
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
        NativeUIObservations(
            elements: [],
            status: .notRequested,
            modalityHealth: ModalityHealth(
                detector: .notRequested,
                ocr: .notRequested,
                focus: .notRequested,
                audit: .notRequested
            )
        )
    }
}

/// The standard CoreML + Vision native UI element recognizer.
public struct NativeUIDetectorRecognizer: NativeUIRecognizing {
    public let configuration: NativeUIDetectionConfiguration
    internal let textRecognitionHandler: (@Sendable (CGImage) async throws -> [RecognizedTextRegion])?

    public init(configuration: NativeUIDetectionConfiguration = .default) {
        self.configuration = configuration
        self.textRecognitionHandler = nil
    }

    internal init(
        configuration: NativeUIDetectionConfiguration = .default,
        textRecognitionHandler: (@Sendable (CGImage) async throws -> [RecognizedTextRegion])? = nil
    ) {
        self.configuration = configuration
        self.textRecognitionHandler = textRecognitionHandler
    }

    public func recognizeNativeUI(
        inPNGData data: Data,
        path: String,
        sidecar: NativeUISidecar?
    ) async throws -> NativeUIObservations {
        guard let source = CGImageSourceCreateWithData(data as CFData, nil),
              let cgImage = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
            let health = ModalityHealth(
                detector: .failed(reason: "Invalid or corrupt image data"),
                ocr: .notRequested,
                focus: .notRequested,
                audit: .notRequested
            )
            return NativeUIObservations(elements: [], status: .failed("Invalid or corrupt image data"), modalityHealth: health)
        }

        let request = NativeUIDetectionRequest(
            configuration: configuration,
            textRecognitionHandler: textRecognitionHandler
        )
        do {
            let detailed = try await request.performDetailed(on: cgImage, sidecar: sidecar)
            let overallStatus: NativeUIRecognitionStatus = (detailed.modalityHealth.hasAnyFailure && configuration.modalityPolicy == .strict)
                ? .failed("Required modality failed")
                : .success
            return NativeUIObservations(
                elements: detailed.elements,
                status: overallStatus,
                modalityHealth: detailed.modalityHealth
            )
        } catch NativeUIDetectionError.imagePreprocessingFailed {
            let health = ModalityHealth(detector: .failed(reason: "Image preprocessing failed"), ocr: .notRequested, focus: .notRequested, audit: .notRequested)
            return NativeUIObservations(elements: [], status: .failed("Image preprocessing failed"), modalityHealth: health)
        } catch NativeUIDetectionError.modalityFailed(let mod, let reason) {
            var health = ModalityHealth()
            if mod == "ocr" { health.ocr = .failed(reason: reason) }
            else if mod == "detector" { health.detector = .failed(reason: reason) }
            return NativeUIObservations(elements: [], status: .failed("Modality '\(mod)' failed: \(reason)"), modalityHealth: health)
        } catch {
            let health = ModalityHealth(detector: .failed(reason: error.localizedDescription))
            return NativeUIObservations(elements: [], status: .failed(error.localizedDescription), modalityHealth: health)
        }
    }
}
