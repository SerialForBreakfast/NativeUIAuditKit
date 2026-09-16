// NativeUIDetectionSession.swift
// NativeUIAuditKit
//
// An actor-backed detection session that maintains warm, in-memory MLModel instances
// across sequential detection calls to eliminate repeated model loading latency.

import CoreGraphics
import CoreML
import Foundation
import ImageIO
import NativeUIAuditKitModels

/// A stateful detection session that pre-warms and caches CoreML models in memory,
/// providing thread-safe, low-latency UI element inspection across sequential frames.
public actor NativeUIDetectionSession: NativeUIRecognizing {
    public let configuration: NativeUIDetectionConfiguration
    internal let textRecognitionHandler: (@Sendable (CGImage) async throws -> [RecognizedTextRegion])?

    private var cachedModels: [NativeUIPlatform: PreloadedModel] = [:]

    public init(
        configuration: NativeUIDetectionConfiguration = .default,
        textRecognitionHandler: (@Sendable (CGImage) async throws -> [RecognizedTextRegion])? = nil
    ) {
        self.configuration = configuration
        self.textRecognitionHandler = textRecognitionHandler
    }

    /// Pre-warms model instances for the specified platforms so subsequent detection calls execute warm without cold-start delay.
    public func warm(platforms: [NativeUIPlatform] = [.tvOS, .iOS]) async throws {
        for platform in platforms {
            _ = try await getOrLoadModel(for: platform)
        }
    }

    /// Returns whether the model for a given platform is already loaded in memory.
    public func isWarmed(for platform: NativeUIPlatform) -> Bool {
        cachedModels[platform] != nil
    }

    /// Evicts loaded models from memory to free resources when idle.
    public func clearCache() {
        cachedModels.removeAll()
    }

    /// Retrieves or loads the model for the requested platform.
    private func getOrLoadModel(for platform: NativeUIPlatform) async throws -> PreloadedModel {
        if let existing = cachedModels[platform] {
            return existing
        }

        let loaded: PreloadedModel
        switch platform {
        case .tvOS:
            do {
                let m = try await NativeUIModelAsset.loadTVOSModel()
                loaded = PreloadedModel(model: m, metadata: NativeUIModelAsset.tvOSMetadata, manifest: NativeUIModelAsset.tvOSManifest)
            } catch let error as ModelContractError {
                throw NativeUIDetectionError.incompatibleModelContract(reason: error.reason)
            }
        case .iOS, .iPadOS, .macOS, .visionOS, .unknown:
            do {
                let m = try await NativeUIModelAsset.loadModel()
                loaded = PreloadedModel(model: m, metadata: NativeUIModelAsset.metadata, manifest: NativeUIModelAsset.iOSManifest)
            } catch let error as ModelContractError {
                throw NativeUIDetectionError.incompatibleModelContract(reason: error.reason)
            }
        }

        cachedModels[platform] = loaded
        return loaded
    }

    /// Determines the effective platform for a screenshot.
    private func resolvePlatform(for screenshot: CGImage, sidecar: NativeUISidecar?) -> NativeUIPlatform {
        switch configuration.platform {
        case .tvOS:
            return .tvOS
        case .iOS:
            return .iOS
        case .auto:
            if let p = sidecar?.platform, p.lowercased().contains("tv") {
                return .tvOS
            } else if (screenshot.width == 1920 && screenshot.height == 1080) ||
                      (screenshot.width == 3840 && screenshot.height == 2160) {
                return .tvOS
            } else {
                return .iOS
            }
        }
    }

    /// Performs detailed UI detection on a CGImage using the warm cached model runtime.
    public func performDetailed(
        on screenshot: CGImage,
        sidecar: NativeUISidecar? = nil
    ) async throws -> NativeUIDetailedDetectionResult {
        let platform = resolvePlatform(for: screenshot, sidecar: sidecar)
        let loaded = try await getOrLoadModel(for: platform)

        let request = NativeUIDetectionRequest(
            configuration: configuration,
            textRecognitionHandler: textRecognitionHandler
        )
        return try await request.performDetailed(
            on: screenshot,
            sidecar: sidecar,
            preloadedModel: loaded
        )
    }

    /// Performs UI detection on a CGImage, returning observations directly.
    public func perform(
        on screenshot: CGImage,
        sidecar: NativeUISidecar? = nil
    ) async throws -> [NativeUIElementObservation] {
        try await performDetailed(on: screenshot, sidecar: sidecar).elements
    }

    /// Conforms to `NativeUIRecognizing` for image data workflows.
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

        do {
            let detailed = try await performDetailed(on: cgImage, sidecar: sidecar)
            let overallStatus: NativeUIRecognitionStatus = (detailed.modalityHealth.hasAnyFailure && configuration.modalityPolicy == .strict)
                ? .failed("Required modality failed")
                : .success
            return NativeUIObservations(
                elements: detailed.elements,
                status: overallStatus,
                modalityHealth: detailed.modalityHealth,
                timings: detailed.timings
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
