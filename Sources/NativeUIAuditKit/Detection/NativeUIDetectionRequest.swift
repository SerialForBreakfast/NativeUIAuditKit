// NativeUIDetectionRequest.swift
// NativeUIAuditKit
//
// Three-pass inference pipeline:
//   Pass 1 — Full image (scaleFill): catches large elements (alert).
//   Pass 2 — SAHI square tiles 640×640 at 480px stride on a 2× upscaled image:
//            catches medium/small objects (toggle, primaryButton).
//   Pass 3 — Horizontal strips (22% height, 50% overlap): catches full-width thin
//            elements (navigationBar, textField) after retraining with strip data.
//            Returns 0 results with the v1 model trained on full images only.
//
// All passes produce Vision-normalized coordinates (bottom-left origin, [0,1]).
// Global NMS at IoU 0.45 merges duplicates across passes.
//
// See BP-25 (scaleFill), BP-26 (strip tiling) in Research/BestPractices.md.

import CoreGraphics
import CoreML
import Foundation
import Vision

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

        let model = try Self.loadModel()
        let confThreshold = Float(configuration.minimumConfidence)

        // Run all three passes off the main actor
        let raw: [RawPrediction] = try await Task.detached(priority: .userInitiated) {
            var preds: [RawPrediction] = []
            preds += try Self.fullImagePass(screenshot, model: model)
            preds += try Self.sahiTilePass(screenshot, model: model)
            preds += try Self.stripPass(screenshot, model: model)
            return preds
        }.value

        let kept = Self.nms(raw, iouThreshold: 0.45, confThreshold: confThreshold)
        let w = screenshot.width
        let h = screenshot.height
        return kept
            .sorted { $0.confidence > $1.confidence }
            .compactMap { Self.toObservation($0, imageWidth: w, imageHeight: h) }
    }
}

// MARK: - Errors

public enum NativeUIDetectionError: Error, Sendable, Equatable {
    case modelUnavailable
    case imagePreprocessingFailed
    case unexpectedModelOutput(String)
}

// MARK: - Internal types

private struct RawPrediction: Sendable {
    let label: String
    let confidence: Float
    /// Vision normalized coords: bottom-left origin, [0,1].
    let vx: Double   // minX (left edge)
    let vy: Double   // minY (bottom edge, from image bottom)
    let vw: Double
    let vh: Double
}

// MARK: - Model loading

extension NativeUIDetectionRequest {

    // Cached compiled model URL — set once, read-only thereafter.
    nonisolated(unsafe) private static var _compiledModelURL: URL? = nil
    nonisolated(unsafe) private static var _vnModel: VNCoreMLModel? = nil

    private static func loadModel() throws -> VNCoreMLModel {
        if let cached = _vnModel { return cached }

        // Search all bundles for a compiled .mlmodelc resource
        let allBundles = Bundle.allBundles + Bundle.allFrameworks
        var modelURL: URL?

        for bundle in allBundles {
            if let url = bundle.url(forResource: "NativeUIDetector_v1", withExtension: "mlmodelc") {
                modelURL = url
                break
            }
        }

        // Development fallback: uncompiled .mlmodel in the models package source tree
        if modelURL == nil {
            let devPath = URL(filePath: #filePath)   // this file
                .deletingLastPathComponent()          // Detection/
                .deletingLastPathComponent()          // NativeUIAuditKit/
                .deletingLastPathComponent()          // Sources/
                .deletingLastPathComponent()          // project root
                .appending(path: "NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIDetector_v1.mlpackage.mlmodel")
            if FileManager.default.fileExists(atPath: devPath.path) {
                modelURL = try MLModel.compileModel(at: devPath)
                _compiledModelURL = modelURL
            }
        }

        guard let url = modelURL else {
            throw NativeUIDetectionError.modelUnavailable
        }

        let mlModel = try MLModel(contentsOf: url)
        let vnModel = try VNCoreMLModel(for: mlModel)
        _vnModel = vnModel
        return vnModel
    }
}

// MARK: - Pass 1: Full image

extension NativeUIDetectionRequest {

    private static func fullImagePass(
        _ image: CGImage,
        model: VNCoreMLModel
    ) throws -> [RawPrediction] {
        let req = VNCoreMLRequest(model: model)
        req.imageCropAndScaleOption = .scaleFill   // BP-25: must match training preprocessing
        try VNImageRequestHandler(cgImage: image).perform([req])
        return (req.results as? [VNRecognizedObjectObservation] ?? [])
            .map { obs in
                let b = obs.boundingBox
                return RawPrediction(
                    label:      obs.labels.first?.identifier ?? "unknown",
                    confidence: obs.confidence,
                    vx: Double(b.minX),
                    vy: Double(b.minY),
                    vw: Double(b.width),
                    vh: Double(b.height)
                )
            }
    }
}

// MARK: - Pass 2: SAHI square tiles

extension NativeUIDetectionRequest {

    private static let sahiTileSize: Int = 640
    private static let sahiStride:   Int = 480   // 25% overlap
    private static let sahiScale:    Double = 2.0

    private static func sahiTilePass(
        _ image: CGImage,
        model: VNCoreMLModel
    ) throws -> [RawPrediction] {
        let origW = image.width
        let origH = image.height
        let scaledW = Int(Double(origW) * sahiScale)
        let scaledH = Int(Double(origH) * sahiScale)

        // Upscale image 2×
        guard let scaledCtx = CGContext(
            data: nil, width: scaledW, height: scaledH,
            bitsPerComponent: 8, bytesPerRow: 0,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
        ) else { return [] }
        // CGContext is bottom-left; draw fills [0, scaledH] in y
        scaledCtx.draw(image, in: CGRect(x: 0, y: 0, width: scaledW, height: scaledH))
        guard let scaledImage = scaledCtx.makeImage() else { return [] }

        var predictions: [RawPrediction] = []

        // Tile origin is in 2× pixel space (top-left for CGImage cropping)
        var tileOriginY = 0
        while tileOriginY < scaledH {
            let clampedTileH = min(sahiTileSize, scaledH - tileOriginY)
            var tileOriginX = 0
            while tileOriginX < scaledW {
                let clampedTileW = min(sahiTileSize, scaledW - tileOriginX)
                defer { tileOriginX += sahiStride }
                guard let tileImage = cropCGImage(
                    scaledImage,
                    originX: tileOriginX, originY: tileOriginY,
                    width: clampedTileW, height: clampedTileH
                ) else { continue }

                let req = VNCoreMLRequest(model: model)
                // Square tiles: scaleFill == scaleFit (no letterboxing). Use scaleFill for consistency.
                req.imageCropAndScaleOption = .scaleFill
                try VNImageRequestHandler(cgImage: tileImage).perform([req])

                let tileResults = req.results as? [VNRecognizedObjectObservation] ?? []
                for obs in tileResults {
                    let b = obs.boundingBox

                    // Convert tile-local Vision coords → full-2× image Vision coords → original image Vision coords.
                    // In 2× pixel space (top-left origin):
                    //   left_px   = tileOriginX + b.minX  * clampedTileW
                    //   bottom_px from image bottom = (scaledH - tileOriginY - clampedTileH) + b.minY * clampedTileH
                    let leftPx   = Double(tileOriginX) + Double(b.minX)  * Double(clampedTileW)
                    let bottomPx = Double(scaledH - tileOriginY - clampedTileH) + Double(b.minY) * Double(clampedTileH)
                    let boxW     = Double(b.width)  * Double(clampedTileW)
                    let boxH     = Double(b.height) * Double(clampedTileH)

                    // Normalize to 2× image (= original image content, same Vision coords)
                    let vx = leftPx   / Double(scaledW)
                    let vy = bottomPx / Double(scaledH)
                    let vw = boxW     / Double(scaledW)
                    let vh = boxH     / Double(scaledH)

                    predictions.append(RawPrediction(
                        label:      obs.labels.first?.identifier ?? "unknown",
                        confidence: obs.confidence,
                        vx: vx, vy: vy, vw: vw, vh: vh
                    ))
                }
            }
            tileOriginY += sahiStride
            if tileOriginY > scaledH - sahiStride && tileOriginY < scaledH {
                tileOriginY = scaledH - sahiTileSize  // ensure bottom row is always covered
            } else if tileOriginY >= scaledH { break }
        }

        return predictions
    }
}

// MARK: - Pass 3: Horizontal strips (matches training strip augmentation)

extension NativeUIDetectionRequest {

    /// Fraction of image height per strip — must match `TrainingConfig.default.stripFraction`.
    private static let stripFraction: Double = 0.22

    private static func stripPass(
        _ image: CGImage,
        model: VNCoreMLModel
    ) throws -> [RawPrediction] {
        let imageW = image.width
        let imageH = image.height
        let stripH = max(1, Int(Double(imageH) * stripFraction))
        let stride  = max(1, stripH / 2)

        var predictions: [RawPrediction] = []

        var stripY = 0
        while stripY + stripH <= imageH {
            defer { stripY += stride }

            guard let stripImage = cropCGImage(
                image,
                originX: 0, originY: stripY,
                width: imageW, height: stripH
            ) else { continue }

            let req = VNCoreMLRequest(model: model)
            req.imageCropAndScaleOption = .scaleFill
            try VNImageRequestHandler(cgImage: stripImage).perform([req])

            let stripResults = req.results as? [VNRecognizedObjectObservation] ?? []
            for obs in stripResults {
                let b = obs.boundingBox

                // Convert strip-local Vision coords → full-image Vision coords.
                // Strip in Vision space (bottom-left origin):
                //   stripBottomVision = distance from image bottom to strip's bottom edge
                //   = 1.0 - (stripY + stripH) / imageH
                let stripBottomVision = 1.0 - Double(stripY + stripH) / Double(imageH)
                let stripHeightVision = Double(stripH) / Double(imageH)

                // x is unchanged (full-width strip). y scales with stripHeightVision.
                let vx = Double(b.minX)
                let vy = stripBottomVision + Double(b.minY) * stripHeightVision
                let vw = Double(b.width)
                let vh = Double(b.height) * stripHeightVision

                predictions.append(RawPrediction(
                    label:      obs.labels.first?.identifier ?? "unknown",
                    confidence: obs.confidence,
                    vx: vx, vy: vy, vw: vw, vh: vh
                ))
            }
        }

        return predictions
    }
}

// MARK: - NMS

extension NativeUIDetectionRequest {

    private static func nms(
        _ predictions: [RawPrediction],
        iouThreshold: Double,
        confThreshold: Float
    ) -> [RawPrediction] {
        let filtered = predictions.filter { $0.confidence >= confThreshold }
        let sorted   = filtered.sorted { $0.confidence > $1.confidence }

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
        let ax1 = a.vx, ax2 = a.vx + a.vw, ay1 = a.vy, ay2 = a.vy + a.vh
        let bx1 = b.vx, bx2 = b.vx + b.vw, by1 = b.vy, by2 = b.vy + b.vh
        let ix = max(0, min(ax2, bx2) - max(ax1, bx1))
        let iy = max(0, min(ay2, by2) - max(ay1, by1))
        let inter = ix * iy
        let union = a.vw * a.vh + b.vw * b.vh - inter
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

        let visionRect = NativeUIRect(x: pred.vx, y: pred.vy, width: pred.vw, height: pred.vh)

        // Convert Vision (bottom-left) to pixel (top-left):
        //   px_x = vx × imageWidth
        //   px_y = (1 - vy - vh) × imageHeight   ← flip y, measure from top
        let pixelRect = NativeUIRect(
            x:      pred.vx * Double(imageWidth),
            y:      (1.0 - pred.vy - pred.vh) * Double(imageHeight),
            width:  pred.vw * Double(imageWidth),
            height: pred.vh * Double(imageHeight)
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

// MARK: - CGImage crop helper

/// Crops a CGImage to the given rectangle using a CGContext.
/// `originY` is measured from the TOP of the image (screen convention).
private func cropCGImage(
    _ source: CGImage,
    originX: Int,
    originY: Int,
    width: Int,
    height: Int
) -> CGImage? {
    guard let ctx = CGContext(
        data: nil,
        width: width, height: height,
        bitsPerComponent: 8, bytesPerRow: 0,
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
    ) else { return nil }

    // CGContext is bottom-left origin. To expose rows [originY, originY+height) from the top:
    // draw the full source so that source row (originY+height) from top lands at context y=0.
    // source.height - (originY + height) = distance of that row from the source bottom.
    let drawY = -(source.height - originY - height)
    ctx.draw(source, in: CGRect(x: -originX, y: drawY,
                                 width: source.width, height: source.height))
    return ctx.makeImage()
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
