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

// MARK: - Configuration

public struct NativeUIDetectionConfiguration: Sendable {
    public var minimumConfidence: Double
    public var includesTextRecognition: Bool

    public init(minimumConfidence: Double = 0.5, includesTextRecognition: Bool = true) {
        self.minimumConfidence = minimumConfidence
        self.includesTextRecognition = includesTextRecognition
    }

    public static let `default` = NativeUIDetectionConfiguration()
}

// MARK: - Request

public struct NativeUIDetectionRequest: Sendable {
    public let configuration: NativeUIDetectionConfiguration

    public init(configuration: NativeUIDetectionConfiguration = .default) {
        self.configuration = configuration
    }

    public func perform(
        on screenshot: CGImage,
        sidecar: NativeUISidecar? = nil
    ) async throws -> [NativeUIElementObservation] {

        let model = try await NativeUIModelAsset.loadModel()
        let confThreshold = Float(configuration.minimumConfidence)
        let classLabels = NativeUIModelAsset.metadata.classLabels
        let nmsIoU = Double(NativeUIModelAsset.metadata.recommendedNMSIoUThreshold)

        let raw: [RawPrediction] = try await Task.detached(priority: .userInitiated) {
            try Self.runYOLO(screenshot, model: model, classLabels: classLabels, confFloor: confThreshold)
        }.value

        // Greedy same-class NMS as a second pass, matching scripts/eval_yolo_map.swift —
        // the model's own CoreML graph already runs NMS internally (iouThreshold input
        // below), this catches any remaining near-duplicates at a tighter threshold.
        let kept = Self.nms(raw, iouThreshold: nmsIoU)
        let w = screenshot.width
        let h = screenshot.height
        return kept
            .sorted { $0.confidence > $1.confidence }
            .compactMap { Self.toObservation($0, imageWidth: w, imageHeight: h) }
    }
}

// MARK: - Errors

public enum NativeUIDetectionError: Error, Sendable, Equatable {
    case imagePreprocessingFailed
    case unexpectedModelOutput(String)
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
