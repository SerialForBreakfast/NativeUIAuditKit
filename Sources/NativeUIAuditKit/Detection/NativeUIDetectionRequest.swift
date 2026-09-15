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

    public init(
        minimumConfidence: Double = 0.5,
        includesTextRecognition: Bool = true,
        platform: PlatformSelection = .auto,
        modalityPolicy: ModalityPolicy = .permissive
    ) {
        self.minimumConfidence = minimumConfidence
        self.includesTextRecognition = includesTextRecognition
        self.platform = platform
        self.modalityPolicy = modalityPolicy
    }

    public static let `default` = NativeUIDetectionConfiguration()
}

// MARK: - Detailed Result

/// Detailed outcome of a detection request containing observations and per-modality health status.
public struct NativeUIDetailedDetectionResult: Sendable, Codable {
    public let elements: [NativeUIElementObservation]
    public let modalityHealth: ModalityHealth

    public init(elements: [NativeUIElementObservation], modalityHealth: ModalityHealth) {
        self.elements = elements
        self.modalityHealth = modalityHealth
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

    /// Performs UI detection and returns observations along with honest subsystem health.
    public func performDetailed(
        on screenshot: CGImage,
        sidecar: NativeUISidecar? = nil
    ) async throws -> NativeUIDetailedDetectionResult {

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

        let model: MLModel
        let metadata: ModelMetadata
        if effectivePlatform == .tvOS {
            model = try await NativeUIModelAsset.loadTVOSModel()
            metadata = NativeUIModelAsset.tvOSMetadata
        } else {
            model = try await NativeUIModelAsset.loadModel()
            metadata = NativeUIModelAsset.metadata
        }

        let confThreshold = Float(configuration.minimumConfidence)
        let classLabels = metadata.classLabels
        let nmsIoU = Double(metadata.recommendedNMSIoUThreshold)

        let raw: [RawPrediction] = try await Task.detached(priority: .userInitiated) {
            try Self.runYOLO(screenshot, model: model, classLabels: classLabels, confFloor: confThreshold)
        }.value

        // Greedy same-class NMS as a second pass
        let kept = Self.nms(raw, iouThreshold: nmsIoU)
        let w = screenshot.width
        let h = screenshot.height
        let rawObservations = kept
            .sorted { $0.confidence > $1.confidence }
            .compactMap { Self.toObservation($0, imageWidth: w, imageHeight: h) }

        health.detector = rawObservations.isEmpty ? .empty : .available

        var observations = rawObservations

        // tvOS focus state resolution
        if effectivePlatform == .tvOS {
            observations = Self.resolveTVOSFocus(in: screenshot, observations: observations)
            health.focus = observations.contains(where: { $0.state.isFocused == true }) ? .available : .empty
        } else {
            health.focus = .notRequested
        }

        // 1. Vision OCR text fusion (TASK-7-1, TASK-7-2, and TASK-6b-WP1-1)
        if configuration.includesTextRecognition {
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
        let imageSize = CGSize(width: w, height: h)
        observations = AuditRules.evaluate(
            observations: observations,
            imageSize: imageSize,
            scale: sidecar?.scale,
            platform: effectivePlatform
        )
        health.audit = .available

        return NativeUIDetailedDetectionResult(elements: observations, modalityHealth: health)
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
    public static func recognizeText(in screenshot: CGImage) async throws -> [RecognizedTextRegion] {
        try await Task.detached(priority: .userInitiated) {
            let request = VNRecognizeTextRequest()
            request.recognitionLevel = .accurate
            request.usesLanguageCorrection = true
            request.recognitionLanguages = ["en-US", "en-GB"]

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
        classLabels: [String],
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
        let nCheck = min(classLabels.count, nTotal)

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
            var bestClass = 0
            for c in 0..<nCheck {
                let v = confArr[i * cs0 + c * cs1].floatValue
                if v > bestConf { bestConf = v; bestClass = c }
            }
            guard bestConf >= confFloor else { continue }

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
                label: classLabels[bestClass],
                confidence: bestConf,
                cx: cxOrig, cy: cyOrig, w: wOrig, h: hOrig
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

    private static func resolveTVOSFocus(
        in screenshot: CGImage,
        observations: [NativeUIElementObservation]
    ) -> [NativeUIElementObservation] {
        let focusableTypes: Set<NativeUIElementType> = [
            .collectionItem, .listRow, .primaryButton, .secondaryButton,
            .tabBar, .cancelAction, .toggle
        ]

        var candidateScores: [(id: UUID, type: NativeUIElementType, score: Double)] = []
        for obs in observations where focusableTypes.contains(obs.elementType) {
            let px = obs.boundingBoxPixels
            let rect = CGRect(x: px.x, y: px.y, width: px.width, height: px.height)
            let score = evaluateElementFocusScore(
                cgImage: screenshot,
                pixelRect: rect,
                elementType: obs.elementType
            )
            candidateScores.append((id: obs.id, type: obs.elementType, score: score))
        }

        let focusWinnerId: UUID? = candidateScores
            .filter { item in
                if item.type == .collectionItem {
                    return item.score > 0.03
                } else {
                    return item.score > 0.45
                }
            }
            .max(by: { $0.score < $1.score })?
            .id

        return observations.map { obs in
            guard focusableTypes.contains(obs.elementType) else {
                return obs
            }
            let isFocused = (focusWinnerId != nil && obs.id == focusWinnerId!)
            var updatedState = obs.state
            updatedState.isFocused = isFocused
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

        if elementType == .collectionItem {
            // In tvOS Home Screen, focused collectionItem has a radiant white perimeter border outline.
            // Check white pixel ratio along the outer perimeter.
            let t = max(1, min(6, min(cw, ch) / 4))
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
            return totalBorderPixels > 0 ? (Double(whiteCount) / Double(totalBorderPixels)) : 0.0
        } else {
            // For listRow, primaryButton, tabBar, cancelAction:
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
            return count > 0 ? (totalLuminance / Double(count)) : 0.0
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
