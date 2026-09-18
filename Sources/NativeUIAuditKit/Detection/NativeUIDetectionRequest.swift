// NativeUIDetectionRequest.swift
// NativeUIAuditKit
//
// Single-pass letterboxed inference against the YOLO11n model shipped by
// NativeUIAuditKitModels. The model is anchor-free, so — unlike the superseded Create ML
// v1 pipeline this replaced — no strip tiling or SAHI tiling is needed to cover thin or
// small classes; one 640×640 letterboxed pass handles every class (mAP@0.5 = 0.935 on the
// held-out validation set with zero tiling, see Research/ExperimentLog.md Run 006).
//
// Letterbox → CVPixelBuffer → MLModel.prediction → inverse-letterbox → greedy NMS,
// ported verbatim from scripts/eval_yolo_map.swift (validated against the shipped mAP
// figure). The model's own CoreML graph already applies NMS internally (iouThreshold
// input below); the greedy pass afterward catches any remaining near-duplicates, matching
// eval_yolo_map.swift's proven approach — not redundant, just a tighter second pass at a
// different threshold (0.30 vs the model's internal 0.45).

import CoreGraphics
import CoreML
import Foundation
import NativeUIAuditKitModels
import Vision

// MARK: - Configuration

public struct NativeUIDetectionConfiguration: Sendable {
    public enum PlatformSelection: String, Sendable, Codable {
        case auto
        case iOS
        case tvOS
    }

    public enum ModalityPolicy: String, Sendable, Codable {
        case strict
        case permissive
    }

    public var minimumConfidence: Double
    public var includesTextRecognition: Bool
    public var platform: PlatformSelection
    public var modalityPolicy: ModalityPolicy
    public var minFocusScoreThreshold: Double
    public var minFocusMargin: Double
    public var recordTimings: Bool
    /// When true, Stage 2 `FocusRingDetector` is used for tvOS focus if the compiled
    /// model is bundled. Missing weights fall back to `resolveTVOSFocus`.
    public var useFocusClassifier: Bool

    public init(
        minimumConfidence: Double = 0.5,
        includesTextRecognition: Bool = true,
        platform: PlatformSelection = .auto,
        modalityPolicy: ModalityPolicy = .permissive,
        minFocusScoreThreshold: Double = 0.25,
        minFocusMargin: Double = 0.12,
        recordTimings: Bool = false,
        useFocusClassifier: Bool = true
    ) {
        self.minimumConfidence = minimumConfidence
        self.includesTextRecognition = includesTextRecognition
        self.platform = platform
        self.modalityPolicy = modalityPolicy
        self.minFocusScoreThreshold = minFocusScoreThreshold
        self.minFocusMargin = minFocusMargin
        self.recordTimings = recordTimings
        self.useFocusClassifier = useFocusClassifier
    }

    public static let `default` = NativeUIDetectionConfiguration()
}

extension NativeUIDetectionConfiguration: Codable {
    private enum CodingKeys: String, CodingKey {
        case minimumConfidence, includesTextRecognition, platform, modalityPolicy
        case minFocusScoreThreshold, minFocusMargin, recordTimings, useFocusClassifier
    }

    public init(from decoder: any Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        minimumConfidence = try c.decodeIfPresent(Double.self, forKey: .minimumConfidence) ?? 0.5
        includesTextRecognition = try c.decodeIfPresent(Bool.self, forKey: .includesTextRecognition) ?? true
        platform = try c.decodeIfPresent(PlatformSelection.self, forKey: .platform) ?? .auto
        modalityPolicy = try c.decodeIfPresent(ModalityPolicy.self, forKey: .modalityPolicy) ?? .permissive
        minFocusScoreThreshold = try c.decodeIfPresent(Double.self, forKey: .minFocusScoreThreshold) ?? 0.25
        minFocusMargin = try c.decodeIfPresent(Double.self, forKey: .minFocusMargin) ?? 0.12
        recordTimings = try c.decodeIfPresent(Bool.self, forKey: .recordTimings) ?? false
        useFocusClassifier = try c.decodeIfPresent(Bool.self, forKey: .useFocusClassifier) ?? true
    }

    public func encode(to encoder: any Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        try c.encode(minimumConfidence, forKey: .minimumConfidence)
        try c.encode(includesTextRecognition, forKey: .includesTextRecognition)
        try c.encode(platform, forKey: .platform)
        try c.encode(modalityPolicy, forKey: .modalityPolicy)
        try c.encode(minFocusScoreThreshold, forKey: .minFocusScoreThreshold)
        try c.encode(minFocusMargin, forKey: .minFocusMargin)
        try c.encode(recordTimings, forKey: .recordTimings)
        try c.encode(useFocusClassifier, forKey: .useFocusClassifier)
    }
}

// MARK: - Detailed Result & Timings

/// Wall-clock milliseconds spent across detection pipeline stages.
public struct DetectionStageTimings: Sendable, Codable, Equatable {
    public let modelLoadMs: Double?
    public let modelInferenceMs: Double
    public let ocrMs: Double
    public let focusResolutionMs: Double
    public let auditRulesMs: Double
    public let totalMs: Double

    public init(
        modelLoadMs: Double? = nil,
        modelInferenceMs: Double = 0.0,
        ocrMs: Double = 0.0,
        focusResolutionMs: Double = 0.0,
        auditRulesMs: Double = 0.0,
        totalMs: Double = 0.0
    ) {
        self.modelLoadMs = modelLoadMs
        self.modelInferenceMs = modelInferenceMs
        self.ocrMs = ocrMs
        self.focusResolutionMs = focusResolutionMs
        self.auditRulesMs = auditRulesMs
        self.totalMs = totalMs
    }
}

/// An in-memory, thread-safe bundle containing a loaded MLModel and its associated metadata and manifest.
public struct PreloadedModel: @unchecked Sendable {
    public let model: MLModel
    public let metadata: ModelMetadata
    public let manifest: ModelManifest

    public init(model: MLModel, metadata: ModelMetadata, manifest: ModelManifest) {
        self.model = model
        self.metadata = metadata
        self.manifest = manifest
    }
}

/// Detailed outcome of a detection request containing observations, modality health, and optional stage timings.
public struct NativeUIDetailedDetectionResult: Sendable, Codable {
    public let elements: [NativeUIElementObservation]
    public let modalityHealth: ModalityHealth
    public let timings: DetectionStageTimings?

    public init(
        elements: [NativeUIElementObservation],
        modalityHealth: ModalityHealth,
        timings: DetectionStageTimings? = nil
    ) {
        self.elements = elements
        self.modalityHealth = modalityHealth
        self.timings = timings
    }
}

// MARK: - Request

public struct NativeUIDetectionRequest: Sendable {
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

    private static func durationToMs(_ duration: ContinuousClock.Instant.Duration) -> Double {
        let (seconds, attoseconds) = duration.components
        return Double(seconds) * 1000.0 + Double(attoseconds) / 1_000_000_000_000_000.0
    }

    /// Performs UI detection and returns observations along with honest subsystem health.
    public func performDetailed(
        on screenshot: CGImage,
        sidecar: NativeUISidecar? = nil
    ) async throws -> NativeUIDetailedDetectionResult {
        try await performDetailed(on: screenshot, sidecar: sidecar, preloadedModel: nil)
    }

    internal func performDetailed(
        on screenshot: CGImage,
        sidecar: NativeUISidecar? = nil,
        preloadedModel: PreloadedModel? = nil,
        preloadedFocusClassifier: FocusRingClassifier? = nil
    ) async throws -> NativeUIDetailedDetectionResult {
        let startTotal = ContinuousClock.now
        var health = ModalityHealth()

        let effectivePlatform: NativeUIPlatform
        switch configuration.platform {
        case .tvOS:
            effectivePlatform = .tvOS
        case .iOS:
            effectivePlatform = .iOS
        case .auto:
            if let p = sidecar?.platform, p.lowercased().contains("tv") {
                effectivePlatform = .tvOS
            } else if (screenshot.width == 1920 && screenshot.height == 1080) ||
                      (screenshot.width == 3840 && screenshot.height == 2160) {
                effectivePlatform = .tvOS
            } else {
                effectivePlatform = .iOS
            }
        }

        let activeModel: PreloadedModel
        var modelLoadMs: Double? = nil

        if let preloaded = preloadedModel {
            activeModel = preloaded
            modelLoadMs = 0.0
        } else {
            let startLoad = ContinuousClock.now
            if effectivePlatform == .tvOS {
                do {
                    let m = try await NativeUIModelAsset.loadTVOSModel()
                    activeModel = PreloadedModel(model: m, metadata: NativeUIModelAsset.tvOSMetadata, manifest: NativeUIModelAsset.tvOSManifest)
                } catch let error as ModelContractError {
                    throw NativeUIDetectionError.incompatibleModelContract(reason: error.reason)
                }
            } else {
                do {
                    let m = try await NativeUIModelAsset.loadModel()
                    activeModel = PreloadedModel(model: m, metadata: NativeUIModelAsset.metadata, manifest: NativeUIModelAsset.iOSManifest)
                } catch let error as ModelContractError {
                    throw NativeUIDetectionError.incompatibleModelContract(reason: error.reason)
                }
            }
            modelLoadMs = Self.durationToMs(startLoad.duration(to: .now))
        }

        let confThreshold = Float(configuration.minimumConfidence)
        let nmsIoU = Double(activeModel.metadata.recommendedNMSIoUThreshold)

        let startInfer = ContinuousClock.now
        let modelRef = activeModel
        let raw: [RawPrediction] = try await Task.detached(priority: .userInitiated) {
            try Self.runYOLO(screenshot, model: modelRef.model, manifest: modelRef.manifest, confFloor: confThreshold)
        }.value

        // Greedy same-class NMS as a second pass
        let kept = Self.nms(raw, iouThreshold: nmsIoU)
        let w = screenshot.width
        let h = screenshot.height
        let rawObservations = kept
            .sorted { $0.confidence > $1.confidence }
            .compactMap { Self.toObservation($0, imageWidth: w, imageHeight: h) }

        let inferMs = Self.durationToMs(startInfer.duration(to: .now))

        health.detector = rawObservations.isEmpty ? .empty : .available

        var observations = rawObservations

        // tvOS focus state resolution — Stage 2 classifier when bundled, else heuristic.
        var focusMs = 0.0
        if effectivePlatform == .tvOS {
            let startFocus = ContinuousClock.now
            let classifier: FocusRingClassifier?
            if configuration.useFocusClassifier {
                if let preloadedFocusClassifier {
                    classifier = preloadedFocusClassifier
                } else {
                    classifier = await Self.loadFocusClassifierIfAvailable()
                }
            } else {
                classifier = nil
            }
            if let classifier {
                observations = Self.resolveTVOSFocusML(
                    in: screenshot,
                    observations: observations,
                    classifier: classifier
                )
            } else {
                observations = Self.resolveTVOSFocus(
                    in: screenshot,
                    observations: observations,
                    minScoreThreshold: configuration.minFocusScoreThreshold,
                    minMargin: configuration.minFocusMargin
                )
            }
            focusMs = Self.durationToMs(startFocus.duration(to: .now))
            health.focus = observations.contains(where: { $0.state.isFocused == true }) ? .available : .empty
        } else {
            health.focus = .notRequested
        }

        // 1. Vision OCR text fusion (TASK-7-1, TASK-7-2, and TASK-6b-WP1-1)
        var ocrMs = 0.0
        if configuration.includesTextRecognition {
            let startOCR = ContinuousClock.now
            do {
                let ocrRegions: [RecognizedTextRegion]
                if let customHandler = textRecognitionHandler {
                    ocrRegions = try await customHandler(screenshot)
                } else {
                    ocrRegions = try await Self.recognizeText(in: screenshot)
                }
                health.ocr = ocrRegions.isEmpty ? .empty : .available
                observations = ObservationMerger.associate(
                    elements: observations,
                    ocrRegions: ocrRegions,
                    sidecar: sidecar
                )
            } catch {
                let nsError = error as NSError
                health.ocr = .failed(reason: error.localizedDescription, domain: nsError.domain, code: nsError.code)
                if configuration.modalityPolicy == .strict {
                    throw NativeUIDetectionError.modalityFailed(modality: "ocr", reason: error.localizedDescription)
                }
                if let sidecar = sidecar {
                    observations = ObservationMerger.associate(
                        elements: observations,
                        ocrRegions: [],
                        sidecar: sidecar
                    )
                }
            }
            ocrMs = Self.durationToMs(startOCR.duration(to: .now))
        } else {
            health.ocr = .notRequested
            if let sidecar = sidecar {
                observations = ObservationMerger.associate(
                    elements: observations,
                    ocrRegions: [],
                    sidecar: sidecar
                )
            }
        }

        // 2. Audit rules evaluation (TASK-7-3)
        let startAudit = ContinuousClock.now
        let imageSize = CGSize(width: w, height: h)
        observations = AuditRules.evaluate(
            observations: observations,
            imageSize: imageSize,
            scale: sidecar?.scale,
            platform: effectivePlatform
        )
        let auditMs = Self.durationToMs(startAudit.duration(to: .now))
        health.audit = .available

        let totalMs = Self.durationToMs(startTotal.duration(to: .now))
        let timings = configuration.recordTimings ? DetectionStageTimings(
            modelLoadMs: modelLoadMs,
            modelInferenceMs: inferMs,
            ocrMs: ocrMs,
            focusResolutionMs: focusMs,
            auditRulesMs: auditMs,
            totalMs: totalMs
        ) : nil

        return NativeUIDetailedDetectionResult(elements: observations, modalityHealth: health, timings: timings)
    }

    /// Convenience invocation returning observations directly.
    public func perform(
        on screenshot: CGImage,
        sidecar: NativeUISidecar? = nil
    ) async throws -> [NativeUIElementObservation] {
        try await performDetailed(on: screenshot, sidecar: sidecar).elements
    }

    /// Infers device model, platform, and OS version from image dimensions, detected UI elements, and optional sidecar metadata.
    public func inferDevice(
        for image: CGImage,
        observations: [NativeUIElementObservation] = [],
        sidecar: NativeUISidecar? = nil
    ) -> NativeUIDeviceInference {
        let size = CGSize(width: image.width, height: image.height)
        return DeviceInference.inferDevice(
            imageSize: size,
            observations: observations,
            sidecar: sidecar
        )
    }

    /// Runs Apple Vision OCR (`VNRecognizeTextRequest`) on the screenshot off the MainActor.
    ///
    /// - Parameter regionOfInterest: Vision-normalized (bottom-left origin, `[0,1]`) rect to
    ///   restrict the search to — e.g. from `ChangeRegionLocalizer` after converting its
    ///   top-left pixel-space ROI. Defaults to the full frame. Returned bounding boxes remain
    ///   in full-image-relative coordinates regardless of this restriction (Vision's own
    ///   `regionOfInterest` semantics — this is a search-space limit, not a crop).
    public static func recognizeText(
        in screenshot: CGImage,
        regionOfInterest: CGRect = CGRect(x: 0, y: 0, width: 1, height: 1)
    ) async throws -> [RecognizedTextRegion] {
        try await Task.detached(priority: .userInitiated) {
            let request = VNRecognizeTextRequest()
            request.recognitionLevel = .accurate
            request.usesLanguageCorrection = true
            request.recognitionLanguages = ["en-US", "en-GB"]
            request.regionOfInterest = regionOfInterest

            let handler = VNImageRequestHandler(cgImage: screenshot, options: [:])
            try handler.perform([request])

            guard let results = request.results else {
                return []
            }

            return results.compactMap { obs in
                guard let topCandidate = obs.topCandidates(1).first else { return nil }
                let box = obs.boundingBox // Vision normalized coords (bottom-left origin [0, 1])
                let rect = NativeUIRect(
                    x: Double(box.origin.x),
                    y: Double(box.origin.y),
                    width: Double(box.size.width),
                    height: Double(box.size.height)
                )
                return RecognizedTextRegion(
                    text: topCandidate.string,
                    boundingBox: rect,
                    confidence: topCandidate.confidence
                )
            }
        }.value
    }
}

// MARK: - Errors

public enum NativeUIDetectionError: Error, Sendable, Equatable {
    case imagePreprocessingFailed
    case unexpectedModelOutput(String)
    case modalityFailed(modality: String, reason: String)
    case incompatibleModelContract(reason: String)
}

// MARK: - Internal types

private struct RawPrediction: Sendable {
    let label: String
    let confidence: Float
    /// Center-form, top-left-origin normalized coords in ORIGINAL image space, [0,1]
    /// (standard YOLO/COCO convention — matches scripts/eval_yolo_map.swift's Prediction).
    let cx, cy, w, h: Double
}

// MARK: - Letterbox + inference (ported from scripts/eval_yolo_map.swift)

extension NativeUIDetectionRequest {

    private static let yoloImgSize = 640

    private struct LetterboxResult {
        let image: CGImage
        let newW, newH, padX, padY: Int
    }

    /// Letterbox-resize to 640×640, preserving aspect ratio. Padding filled with YOLO
    /// standard gray (114, 114, 114) — must match training preprocessing.
    private static func letterbox(_ source: CGImage) -> LetterboxResult? {
        let origW  = Double(source.width)
        let origH  = Double(source.height)
        let scale  = min(Double(yoloImgSize) / origW, Double(yoloImgSize) / origH)
        let newW   = Int(origW * scale)
        let newH   = Int(origH * scale)
        let padX   = (yoloImgSize - newW) / 2
        let padY   = (yoloImgSize - newH) / 2

        guard let ctx = CGContext(
            data: nil, width: yoloImgSize, height: yoloImgSize,
            bitsPerComponent: 8, bytesPerRow: 0,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
        ) else { return nil }

        ctx.setFillColor(CGColor(red: 114/255.0, green: 114/255.0, blue: 114/255.0, alpha: 1.0))
        ctx.fill(CGRect(x: 0, y: 0, width: yoloImgSize, height: yoloImgSize))
        ctx.draw(source, in: CGRect(x: padX, y: padY, width: newW, height: newH))

        guard let boxed = ctx.makeImage() else { return nil }
        return LetterboxResult(image: boxed, newW: newW, newH: newH, padX: padX, padY: padY)
    }

    private static func makePixelBuffer(_ image: CGImage) -> CVPixelBuffer? {
        let attrs = [
            kCVPixelBufferCGImageCompatibilityKey: true,
            kCVPixelBufferCGBitmapContextCompatibilityKey: true,
        ] as CFDictionary
        var buf: CVPixelBuffer?
        guard CVPixelBufferCreate(kCFAllocatorDefault, image.width, image.height,
                                  kCVPixelFormatType_32BGRA, attrs, &buf) == kCVReturnSuccess,
              let pixelBuf = buf else { return nil }

        CVPixelBufferLockBaseAddress(pixelBuf, [])
        defer { CVPixelBufferUnlockBaseAddress(pixelBuf, []) }

        guard let ctx = CGContext(
            data: CVPixelBufferGetBaseAddress(pixelBuf),
            width: image.width, height: image.height,
            bitsPerComponent: 8,
            bytesPerRow: CVPixelBufferGetBytesPerRow(pixelBuf),
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue
        ) else { return nil }

        ctx.draw(image, in: CGRect(x: 0, y: 0, width: image.width, height: image.height))
        return pixelBuf
    }

    /// Single letterboxed pass through the model. `iouThreshold: 0.45` is the model's
    /// internal NMS input (see scripts/eval_yolo_map.swift); `confFloor` gates which
    /// candidates are kept before the second, tighter greedy NMS pass in `perform(on:)`.
    private static func runYOLO(
        _ image: CGImage,
        model: MLModel,
        manifest: ModelManifest,
        confFloor: Float
    ) throws -> [RawPrediction] {
        guard let lb = letterbox(image), let pixelBuf = makePixelBuffer(lb.image) else {
            throw NativeUIDetectionError.imagePreprocessingFailed
        }

        let input = try MLDictionaryFeatureProvider(dictionary: [
            "image":               MLFeatureValue(pixelBuffer: pixelBuf),
            "iouThreshold":        MLFeatureValue(double: 0.45),
            "confidenceThreshold": MLFeatureValue(double: Double(confFloor)),
        ])
        let output = try model.prediction(from: input)

        guard let confArr  = output.featureValue(for: "confidence")?.multiArrayValue,
              let coordArr = output.featureValue(for: "coordinates")?.multiArrayValue else {
            throw NativeUIDetectionError.unexpectedModelOutput("missing confidence/coordinates output")
        }

        let n      = confArr.shape[0].intValue
        let nTotal = confArr.shape[1].intValue

        // Active taxonomy class channels from manifest (skips padding channels)
        let activeChannels = manifest.activeClassChannels.filter { $0.channel < nTotal }

        let cs0 = confArr.strides[0].intValue
        let cs1 = confArr.strides[1].intValue
        let xs0 = coordArr.strides[0].intValue

        let sz    = Double(yoloImgSize)
        let newWd = Double(lb.newW)
        let newHd = Double(lb.newH)
        let pxD   = Double(lb.padX)
        let pyD   = Double(lb.padY)

        var preds: [RawPrediction] = []
        for i in 0..<n {
            var bestConf: Float = 0
            var bestLabel: String? = nil
            for (channelIdx, label) in activeChannels {
                let v = confArr[i * cs0 + channelIdx * cs1].floatValue
                if v > bestConf {
                    bestConf = v
                    bestLabel = label
                }
            }
            guard let label = bestLabel, bestConf >= confFloor else { continue }

            // Raw coords normalized to the 640×640 letterboxed frame; inverse-letterbox
            // back to original-image-normalized, top-left-origin, center-form coords.
            let cx640 = coordArr[i * xs0 + 0].doubleValue
            let cy640 = coordArr[i * xs0 + 1].doubleValue
            let w640  = coordArr[i * xs0 + 2].doubleValue
            let h640  = coordArr[i * xs0 + 3].doubleValue

            let cxOrig = (cx640 * sz - pxD) / newWd
            let cyOrig = (cy640 * sz - pyD) / newHd
            let wOrig  = w640 * sz / newWd
            let hOrig  = h640 * sz / newHd

            preds.append(RawPrediction(
                label: label,
                confidence: bestConf,
                cx: cxOrig,
                cy: cyOrig,
                w: wOrig,
                h: hOrig
            ))
        }
        return preds
    }
}

// MARK: - NMS

extension NativeUIDetectionRequest {

    private static func nms(_ predictions: [RawPrediction], iouThreshold: Double) -> [RawPrediction] {
        let sorted = predictions.sorted { $0.confidence > $1.confidence }
        var kept: [RawPrediction] = []
        var suppressed = Set<Int>()

        for (i, pred) in sorted.enumerated() {
            guard !suppressed.contains(i) else { continue }
            kept.append(pred)
            for (j, other) in sorted.enumerated() where j > i {
                guard !suppressed.contains(j) else { continue }
                // Only suppress same-class detections
                if pred.label == other.label && iou(pred, other) >= iouThreshold {
                    suppressed.insert(j)
                }
            }
        }
        return kept
    }

    private static func iou(_ a: RawPrediction, _ b: RawPrediction) -> Double {
        let ax1 = a.cx - a.w/2, ax2 = a.cx + a.w/2, ay1 = a.cy - a.h/2, ay2 = a.cy + a.h/2
        let bx1 = b.cx - b.w/2, bx2 = b.cx + b.w/2, by1 = b.cy - b.h/2, by2 = b.cy + b.h/2
        let ix = max(0, min(ax2, bx2) - max(ax1, bx1))
        let iy = max(0, min(ay2, by2) - max(ay1, by1))
        let inter = ix * iy
        let union = a.w * a.h + b.w * b.h - inter
        return union > 0 ? inter / union : 0
    }
}

// MARK: - Convert to NativeUIElementObservation

extension NativeUIDetectionRequest {

    private static func toObservation(
        _ pred: RawPrediction,
        imageWidth: Int,
        imageHeight: Int
    ) -> NativeUIElementObservation? {
        guard let elementType = NativeUIElementType(rawValue: pred.label) else { return nil }

        // pred.{cx,cy,w,h} are top-left-origin, center-form, normalized [0,1].
        let topLeftX = pred.cx - pred.w / 2
        let topLeftY = pred.cy - pred.h / 2

        // Vision-normalized (bottom-left origin) — required for Phase 7 OCR fusion
        // alignment with VNRecognizeTextRequest output. x unaffected; y flips.
        let visionRect = NativeUIRect(
            x: topLeftX,
            y: 1.0 - pred.cy - pred.h / 2,
            width: pred.w,
            height: pred.h
        )

        let pixelRect = NativeUIRect(
            x:      topLeftX * Double(imageWidth),
            y:      topLeftY * Double(imageHeight),
            width:  pred.w * Double(imageWidth),
            height: pred.h * Double(imageHeight)
        )

        return NativeUIElementObservation(
            elementType:     elementType,
            boundingBox:     visionRect,
            boundingBoxPixels: pixelRect,
            confidence:      Double(pred.confidence),
            confidenceSource: .pixelModel
        )
    }
}

// MARK: - tvOS Focus Resolution

extension NativeUIDetectionRequest {

    /// Loads `FocusRingDetector` when bundled; returns nil so the heuristic can run.
    internal static func loadFocusClassifierIfAvailable() async -> FocusRingClassifier? {
        guard let model = try? await NativeUIModelAsset.loadFocusRingDetector() else {
            return nil
        }
        return FocusRingClassifier(model: model)
    }

    /// Stage 2: classify each focusable crop with the ML model.
    ///
    /// Winner-takes-all: if any crop exceeds the focus threshold, the highest-probability
    /// one is marked `isFocused = true`; all others are `isFocused = false`.
    /// Elements in the ambiguous band get `isFocused = nil, isAmbiguousFocus = true`.
    /// Non-focusable elements pass through unchanged.
    internal static func resolveTVOSFocusML(
        in screenshot: CGImage,
        observations: [NativeUIElementObservation],
        classifier: FocusRingClassifier
    ) -> [NativeUIElementObservation] {
        struct Scored {
            let id: UUID
            let prob: Float
            let conf: Float
            let isAmbiguous: Bool
        }

        // Classify each focusable element independently.
        var scores: [Scored] = []
        for obs in observations where FocusRingClassifier.focusableTypes.contains(obs.elementType) {
            let bbox = obs.boundingBoxPixels.cgRect
            guard let crop = FocusRingClassifier.makeCrop(from: screenshot, bbox: bbox),
                  let result = try? classifier.classify(crop: crop) else { continue }
            scores.append(Scored(
                id: obs.id,
                prob: result.isFocusedProbability,
                conf: result.confidence,
                isAmbiguous: result.isAmbiguous
            ))
        }

        guard !scores.isEmpty else { return observations }

        // Winner-takes-all: highest-probability candidate wins if it clears the threshold.
        let winner = scores.max(by: { $0.prob < $1.prob })
        let hasConfidentWinner = (winner?.prob ?? 0) >= classifier.focusThreshold
        let scoresByID: [UUID: Scored] = Dictionary(uniqueKeysWithValues: scores.map { ($0.id, $0) })

        return observations.map { obs in
            guard let scored = scoresByID[obs.id] else { return obs }
            var st = obs.state
            st.focusScore = Double(scored.prob)
            st.focusConfidence = Double(scored.conf)
            if hasConfidentWinner, let w = winner, w.id == obs.id {
                st.isFocused = true
                st.isAmbiguousFocus = false
            } else if scored.isAmbiguous {
                st.isFocused = nil
                st.isAmbiguousFocus = true
            } else {
                st.isFocused = false
                st.isAmbiguousFocus = false
            }
            return NativeUIElementObservation(
                id: obs.id,
                elementType: obs.elementType,
                boundingBox: obs.boundingBox,
                boundingBoxPixels: obs.boundingBoxPixels,
                confidence: obs.confidence,
                visibleText: obs.visibleText,
                inferredTraits: obs.inferredTraits,
                state: st,
                issues: obs.issues,
                confidenceSource: obs.confidenceSource
            )
        }
    }

    internal static func resolveTVOSFocus(
        in screenshot: CGImage,
        observations: [NativeUIElementObservation],
        minScoreThreshold: Double = 0.35,
        minMargin: Double = 0.12
    ) -> [NativeUIElementObservation] {
        let focusableObs = observations.filter { FocusRingClassifier.focusableTypes.contains($0.elementType) }
        guard !focusableObs.isEmpty else { return observations }

        // 1. Calculate raw visual scores
        let screenHeight = Double(screenshot.height)

        struct CandidateScore {
            let id: UUID
            let type: NativeUIElementType
            let baseScore: Double
            var finalScore: Double
        }

        var candidateScores: [CandidateScore] = []
        for obs in focusableObs {
            let px = obs.boundingBoxPixels
            let rect = CGRect(x: px.x, y: px.y, width: px.width, height: px.height)
            var baseScore = evaluateElementFocusScore(
                cgImage: screenshot,
                pixelRect: rect,
                elementType: obs.elementType
            )
            // tvOS Safe Area & Bezel Rule:
            // Focused elements are never placed flush against the extreme screen boundary.
            // When an element touches the top/bottom bezel (e.g. bottom shelf/indicator at y >= 0.98 * H),
            // it is background chrome or off-screen, not the active focus item.
            let isExtremeBezel = (px.y + px.height >= screenHeight * 0.98) || (px.y <= screenHeight * 0.015)
            if isExtremeBezel {
                baseScore *= 0.10
            }
            candidateScores.append(CandidateScore(id: obs.id, type: obs.elementType, baseScore: baseScore, finalScore: baseScore))
        }

        // 1b. Contextual VoiceOver Detection:
        // When VoiceOver caption bar is present, boost elements showing high VoiceOver border contrast.
        let hasVoiceOverBar = observations.contains { obs in
            obs.elementType == .sheet &&
            obs.boundingBoxPixels.width >= 700 &&
            obs.boundingBoxPixels.height <= 200 &&
            obs.boundingBoxPixels.y >= screenHeight * 0.70
        }
        if hasVoiceOverBar {
            for i in 0..<candidateScores.count {
                if candidateScores[i].baseScore >= 0.35 {
                    candidateScores[i].finalScore = max(candidateScores[i].finalScore, 0.95)
                }
            }
        }

        // 2. Peer-Relative Geometry Heuristic for collectionItem
        // Focused tvOS collection items physically expand by ~1.15x in dimensions (~1.32x area).
        let collectionItems = focusableObs.filter { $0.elementType == .collectionItem }
        for i in 0..<candidateScores.count {
            guard candidateScores[i].type == .collectionItem,
                  let obs = focusableObs.first(where: { $0.id == candidateScores[i].id }) else {
                continue
            }

            let ay = obs.boundingBoxPixels.y
            let ah = obs.boundingBoxPixels.height
            let rowPeers = collectionItems.filter { peer in
                guard peer.id != obs.id else { return false }
                let py = peer.boundingBoxPixels.y
                let ph = peer.boundingBoxPixels.height
                let overlapY = max(0.0, min(ay + ah, py + ph) - max(ay, py))
                return (overlapY / min(ah, ph)) > 0.40
            }

            let perimeterScore = candidateScores[i].baseScore
            let normalizedPerimeter = min(1.0, perimeterScore * 6.0)

            if !rowPeers.isEmpty {
                let candidateArea = obs.boundingBoxPixels.width * obs.boundingBoxPixels.height
                let peerAreas = rowPeers.map { $0.boundingBoxPixels.width * $0.boundingBoxPixels.height }
                let medPeerArea = median(peerAreas)
                let maxPeerArea = peerAreas.max() ?? candidateArea
                let scaleRatio = medPeerArea > 0 ? (candidateArea / medPeerArea) : 1.0

                if scaleRatio >= 1.12 {
                    // Confirmed geometric expansion (tvOS Parallax focus effect)
                    let geometryScore = min(1.0, max(0.0, (scaleRatio - 1.0) / 0.25))
                    candidateScores[i].finalScore = max(geometryScore * 0.85, (normalizedPerimeter * 0.30) + (geometryScore * 0.70))
                } else if (maxPeerArea / max(1.0, candidateArea)) >= 1.15 {
                    // Another peer in the same row is clearly expanded; penalize this unexpanded peer
                    candidateScores[i].finalScore = normalizedPerimeter * 0.25
                } else {
                    // No peer is expanded; rely on perimeter contrast
                    candidateScores[i].finalScore = normalizedPerimeter
                }
            } else {
                // Isolated or single collectionItem
                candidateScores[i].finalScore = normalizedPerimeter
            }
        }

        // 2b. Dominant Category Priority:
        // When collection items are present and an item shows confirmed geometric expansion (scaleRatio >= 1.15),
        // the active focus modality is grid content. Secondary chrome (such as listRow or tabBar) must not
        // hijack focus from an expanded content tile.
        let hasExpandedGridItem = candidateScores.contains {
            $0.type == .collectionItem && $0.finalScore >= 0.65
        }
        if hasExpandedGridItem {
            for i in 0..<candidateScores.count {
                if candidateScores[i].type != .collectionItem {
                    candidateScores[i].finalScore *= 0.20
                }
            }
        }

        // 3. Margin Analysis & Abstention Policy
        let sorted = candidateScores.sorted { $0.finalScore > $1.finalScore }
        guard let winner = sorted.first else { return observations }

        struct FocusResolution {
            let isFocused: Bool?
            let confidence: Double?
            let score: Double?
            let isAmbiguous: Bool?
        }

        var resolutionMap: [UUID: FocusResolution] = [:]

        if winner.finalScore < minScoreThreshold {
            // Case 1: Low overall score — abstain from asserting focus
            for c in sorted {
                resolutionMap[c.id] = FocusResolution(
                    isFocused: nil,
                    confidence: 0.0,
                    score: c.finalScore,
                    isAmbiguous: false
                )
            }
        } else {
            let runnerUpScore = sorted.count > 1 ? sorted[1].finalScore : 0.0
            let margin = winner.finalScore - runnerUpScore

            if margin < minMargin {
                // Case 2: Ambiguous competition — multiple candidates within margin threshold
                for c in sorted {
                    let isCompetitor = (c.finalScore >= winner.finalScore - minMargin)
                    resolutionMap[c.id] = FocusResolution(
                        isFocused: nil,
                        confidence: isCompetitor ? max(0.1, min(0.5, c.finalScore * 0.5)) : 0.0,
                        score: c.finalScore,
                        isAmbiguous: isCompetitor
                    )
                }
            } else {
                // Case 3: Confident winner
                let winnerConfidence = min(1.0, max(0.60, winner.finalScore * (1.0 + margin)))
                resolutionMap[winner.id] = FocusResolution(
                    isFocused: true,
                    confidence: winnerConfidence,
                    score: winner.finalScore,
                    isAmbiguous: false
                )
                for c in sorted.dropFirst() {
                    resolutionMap[c.id] = FocusResolution(
                        isFocused: false,
                        confidence: 0.0,
                        score: c.finalScore,
                        isAmbiguous: false
                    )
                }
            }
        }

        return observations.map { obs in
            guard let resolution = resolutionMap[obs.id] else {
                return obs
            }
            var updatedState = obs.state
            updatedState.isFocused = resolution.isFocused
            updatedState.focusConfidence = resolution.confidence
            updatedState.focusScore = resolution.score
            updatedState.isAmbiguousFocus = resolution.isAmbiguous
            return NativeUIElementObservation(
                id: obs.id,
                elementType: obs.elementType,
                boundingBox: obs.boundingBox,
                boundingBoxPixels: obs.boundingBoxPixels,
                confidence: obs.confidence,
                visibleText: obs.visibleText,
                inferredTraits: obs.inferredTraits,
                state: updatedState,
                issues: obs.issues,
                confidenceSource: obs.confidenceSource
            )
        }
    }

    private static func median(_ values: [Double]) -> Double {
        guard !values.isEmpty else { return 0.0 }
        let sorted = values.sorted()
        let count = sorted.count
        if count % 2 == 1 {
            return sorted[count / 2]
        } else {
            return (sorted[count / 2 - 1] + sorted[count / 2]) / 2.0
        }
    }

    private static func evaluateElementFocusScore(
        cgImage: CGImage,
        pixelRect: CGRect,
        elementType: NativeUIElementType
    ) -> Double {
        let w = cgImage.width
        let h = cgImage.height

        let cropRect = pixelRect.intersection(CGRect(x: 0, y: 0, width: w, height: h))
        guard cropRect.width >= 4, cropRect.height >= 4,
              let cropped = cgImage.cropping(to: cropRect) else {
            return 0.0
        }

        let cw = cropped.width
        let ch = cropped.height
        let bytesPerPixel = 4
        let bytesPerRow = cw * bytesPerPixel
        var rawData = [UInt8](repeating: 0, count: ch * bytesPerRow)

        let colorSpace = CGColorSpaceCreateDeviceRGB()
        guard let ctx = CGContext(
            data: &rawData,
            width: cw,
            height: ch,
            bitsPerComponent: 8,
            bytesPerRow: bytesPerRow,
            space: colorSpace,
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
        ) else { return 0.0 }

        ctx.draw(cropped, in: CGRect(x: 0, y: 0, width: cw, height: ch))

        // VoiceOver High-Contrast Border Detection (universal across all focusable tvOS elements):
        // In VoiceOver accessibility mode, the focused item has a high-contrast double boundary (both dark and light edges).
        let tVO = max(2, min(6, min(cw, ch) / 6))
        var darkBorderCount = 0
        var brightBorderCount = 0
        var totalVOEdges = 0

        for y in 0..<ch {
            let isBorderY = (y < tVO || y >= ch - tVO)
            for x in 0..<cw {
                let isBorderX = (x < tVO || x >= cw - tVO)
                if isBorderY || isBorderX {
                    let offset = (y * bytesPerRow) + (x * bytesPerPixel)
                    if offset + 3 < rawData.count {
                        let r = rawData[offset]
                        let g = rawData[offset + 1]
                        let b = rawData[offset + 2]
                        if r < 50 && g < 50 && b < 50 {
                            darkBorderCount += 1
                        } else if r > 200 && g > 200 && b > 200 {
                            brightBorderCount += 1
                        }
                        totalVOEdges += 1
                    }
                }
            }
        }
        let voDarkRatio = totalVOEdges > 0 ? (Double(darkBorderCount) / Double(totalVOEdges)) : 0.0
        let voBrightRatio = totalVOEdges > 0 ? (Double(brightBorderCount) / Double(totalVOEdges)) : 0.0
        let isVoiceOverBorder = (voDarkRatio >= 0.10 && voBrightRatio >= 0.10)
        let voScore = isVoiceOverBorder ? min(1.0, (voDarkRatio + voBrightRatio) * 1.5) : 0.0

        if elementType == .collectionItem {
            // In tvOS Home Screen, focused collectionItem has a radiant white perimeter border outline.
            // Check white pixel ratio along the outer perimeter.
            let t = max(1, min(4, min(cw, ch) / 8))
            var whiteCount = 0
            var totalBorderPixels = 0

            for y in 0..<ch {
                let isBorderY = (y < t || y >= ch - t)
                for x in 0..<cw {
                    let isBorderX = (x < t || x >= cw - t)
                    if isBorderY || isBorderX {
                        let offset = (y * bytesPerRow) + (x * bytesPerPixel)
                        if offset + 3 < rawData.count {
                            let r = rawData[offset]
                            let g = rawData[offset + 1]
                            let b = rawData[offset + 2]
                            if r > 200 && g > 200 && b > 200 {
                                whiteCount += 1
                            }
                            totalBorderPixels += 1
                        }
                    }
                }
            }
            let standardWhiteRatio = totalBorderPixels > 0 ? (Double(whiteCount) / Double(totalBorderPixels)) : 0.0
            return max(standardWhiteRatio, voScore)
        } else {
            // For listRow, primaryButton, tabBar, cancelAction, secureField, segmentedControl:
            // When focused, tvOS inverts to solid white high-luminance interior pill.
            let minX = Int(Double(cw) * 0.15)
            let maxX = Int(Double(cw) * 0.85)
            let minY = Int(Double(ch) * 0.15)
            let maxY = Int(Double(ch) * 0.85)

            let step = max(1, (maxX - minX) / 20)
            var totalLuminance = 0.0
            var count = 0

            for y in stride(from: minY, to: maxY, by: max(1, step)) {
                for x in stride(from: minX, to: maxX, by: max(1, step)) {
                    let offset = (y * bytesPerRow) + (x * bytesPerPixel)
                    if offset + 3 < rawData.count {
                        let r = Double(rawData[offset]) / 255.0
                        let g = Double(rawData[offset + 1]) / 255.0
                        let b = Double(rawData[offset + 2]) / 255.0
                        let lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
                        totalLuminance += lum
                        count += 1
                    }
                }
            }
            let interiorLuminance = count > 0 ? (totalLuminance / Double(count)) : 0.0
            return max(interiorLuminance, voScore)
        }
    }
}

// MARK: - Sidecar / supporting types (unchanged)

public struct NativeUISidecar: Codable, Sendable {
    public static let currentSchemaVersion = "1.0"
    public let schemaVersion: String
    public let imageSHA256: String
    public let pixelWidth: Int
    public let pixelHeight: Int
    public let scale: Double
    public let platform: String
    public let osVersion: String
    public let deviceName: String
    public let colorScheme: String
    public let dynamicTypeSize: String
    public let locale: String
    public let elements: [NativeUISidecarElement]

    private enum CodingKeys: String, CodingKey {
        case schemaVersion
        case imageSHA256
        case pixelWidth
        case pixelHeight
        case scale
        case platform
        case osVersion
        case deviceName
        case colorScheme
        case dynamicTypeSize
        case locale
        case elements
    }

    public init(
        schemaVersion: String = currentSchemaVersion,
        imageSHA256: String, pixelWidth: Int, pixelHeight: Int,
        scale: Double, platform: String, osVersion: String,
        deviceName: String, colorScheme: String,
        dynamicTypeSize: String, locale: String,
        elements: [NativeUISidecarElement]
    ) {
        self.schemaVersion = schemaVersion; self.imageSHA256 = imageSHA256
        self.pixelWidth = pixelWidth;       self.pixelHeight = pixelHeight
        self.scale = scale;                  self.platform = platform
        self.osVersion = osVersion;          self.deviceName = deviceName
        self.colorScheme = colorScheme;      self.dynamicTypeSize = dynamicTypeSize
        self.locale = locale;                self.elements = elements
    }

    public init(from decoder: any Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        let schemaVersion = try container.decode(String.self, forKey: .schemaVersion)
        guard schemaVersion == Self.currentSchemaVersion else {
            throw DecodingError.dataCorruptedError(
                forKey: .schemaVersion,
                in: container,
                debugDescription: "Unsupported NativeUISidecar schemaVersion '\(schemaVersion)'; expected '\(Self.currentSchemaVersion)'."
            )
        }

        self.schemaVersion = schemaVersion
        self.imageSHA256 = try container.decode(String.self, forKey: .imageSHA256)
        self.pixelWidth = try container.decode(Int.self, forKey: .pixelWidth)
        self.pixelHeight = try container.decode(Int.self, forKey: .pixelHeight)
        self.scale = try container.decode(Double.self, forKey: .scale)
        self.platform = try container.decode(String.self, forKey: .platform)
        self.osVersion = try container.decode(String.self, forKey: .osVersion)
        self.deviceName = try container.decode(String.self, forKey: .deviceName)
        self.colorScheme = try container.decode(String.self, forKey: .colorScheme)
        self.dynamicTypeSize = try container.decode(String.self, forKey: .dynamicTypeSize)
        self.locale = try container.decode(String.self, forKey: .locale)
        self.elements = try container.decode([NativeUISidecarElement].self, forKey: .elements)
    }
}

public struct NativeUISidecarElement: Codable, Sendable {
    public let id: String
    public let elementType: String
    public let framework: String
    public let boundsPixels: NativeUIRect
    public let boundsPoints: NativeUIRect
    public let boundsVisionNormalized: NativeUIRect
    public let visibleText: String?
    public let accessibilityLabel: String?
    public let traits: [String]
    public let knownIssues: [String]

    public init(
        id: String, elementType: String, framework: String,
        boundsPixels: NativeUIRect, boundsPoints: NativeUIRect,
        boundsVisionNormalized: NativeUIRect,
        visibleText: String? = nil, accessibilityLabel: String? = nil,
        traits: [String] = [], knownIssues: [String] = []
    ) {
        self.id = id; self.elementType = elementType; self.framework = framework
        self.boundsPixels = boundsPixels; self.boundsPoints = boundsPoints
        self.boundsVisionNormalized = boundsVisionNormalized
        self.visibleText = visibleText; self.accessibilityLabel = accessibilityLabel
        self.traits = traits; self.knownIssues = knownIssues
    }
}

public struct NativeUIRect: Codable, Sendable, Equatable {
    public let x: Double
    public let y: Double
    public let width: Double
    public let height: Double

    public init(x: Double, y: Double, width: Double, height: Double) {
        self.x = x; self.y = y; self.width = width; self.height = height
    }

    public var cgRect: CGRect { CGRect(x: x, y: y, width: width, height: height) }
}
