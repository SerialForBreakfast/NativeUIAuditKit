// NativeUIDetectionSession.swift
// NativeUIAuditKit
//
// An actor-backed detection session that maintains warm, in-memory MLModel instances
// across sequential detection calls to eliminate repeated model loading latency.

import CoreGraphics
import CoreML
import Foundation
import ImageIO
import NativeUIModelContracts

/// A stateful detection session that pre-warms and caches CoreML models in memory,
/// providing thread-safe, low-latency UI element inspection across sequential frames.
public actor NativeUIDetectionSession: NativeUIRecognizing {
    public let configuration: NativeUIDetectionConfiguration
    public let modelProvider: any NativeUIModelProviding
    internal let textRecognitionHandler: (@Sendable (CGImage) async throws -> [RecognizedTextRegion])?

    private var cachedModels: [String: PreloadedModel] = [:]
    private var cachedFocusClassifier: FocusRingClassifier?

    public init(
        modelProvider: any NativeUIModelProviding,
        configuration: NativeUIDetectionConfiguration = .default,
        textRecognitionHandler: (@Sendable (CGImage) async throws -> [RecognizedTextRegion])? = nil
    ) {
        self.configuration = configuration
        self.modelProvider = modelProvider
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
        guard let key = try? modelProvider.detectorCacheIdentity(for: platform) else { return false }
        return cachedModels[key] != nil
    }

    /// Evicts loaded models from memory to free resources when idle.
    public func clearCache() {
        cachedModels.removeAll()
        cachedFocusClassifier = nil
    }

    /// Loads the Stage 2 focus classifier once per session when configured and bundled.
    private func getFocusClassifier() async -> FocusClassifierLoad {
        guard configuration.useFocusClassifier else { return FocusClassifierLoad(classifier: nil, fallbackReason: "disabled") }
        if let cachedFocusClassifier {
            return FocusClassifierLoad(classifier: cachedFocusClassifier, fallbackReason: nil)
        }
        let loaded = await modelProvider.loadFocusWithEvidence()
        cachedFocusClassifier = loaded.classifier
        return loaded
    }

    /// Retrieves or loads the model for the requested platform.
    private func getOrLoadModel(for platform: NativeUIPlatform) async throws -> PreloadedModel {
        let key = try modelProvider.detectorCacheIdentity(for: platform)
        if let key, let existing = cachedModels[key] {
            return existing
        }

        let loaded: PreloadedModel
        do {
            loaded = try await modelProvider.loadDetector(for: platform)
        } catch let error as ModelContractError {
            throw NativeUIDetectionError.incompatibleModelContract(reason: error.reason)
        }

        guard try modelProvider.detectorCacheIdentity(for: platform) == key else {
            throw NativeUIModelAvailabilityError.changedArtifact
        }

        if let key { cachedModels[key] = loaded }
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
            modelProvider: modelProvider,
            configuration: configuration,
            textRecognitionHandler: textRecognitionHandler
        )
        return try await request.performDetailed(
            on: screenshot,
            sidecar: sidecar,
            preloadedModel: loaded,
            preloadedFocusLoad: platform == .tvOS ? await getFocusClassifier() : nil
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
                timings: detailed.timings,
                focusExecution: detailed.focusExecution
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
