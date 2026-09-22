// FocusRingClassifier.swift
// NativeUIAuditKit
//
// Stage 2 tvOS focus classifier: a 256×256 crop of one YOLO box in, `is_focused_prob`
// plus `confidence` out. Independent of the YOLO detector. See
// Research/FocusRingDetectorSpec.md.

import CoreGraphics
import CoreML
import CoreVideo
import Foundation

/// Classifies whether a 256×256 crop of a tvOS UI element shows active system focus.
///
/// `MLModel` is not `Sendable`; predictions are treated as thread-safe the same way
/// `PreloadedModel` wraps the YOLO graph (`@unchecked Sendable`).
package struct FocusRingClassifier: @unchecked Sendable {
    /// Compiled FocusRingDetector graph.
    let model: MLModel

    /// Probability at or above which `isFocused` is asserted. Read from model metadata when present.
    let focusThreshold: Float

    /// Lower bound of the ambiguous band (`focusThreshold` is exclusive upper bound).
    let ambiguityThreshold: Float

    /// Default focus threshold from `Research/FocusRingDetectorSpec.md`.
    internal static let defaultFocusThreshold: Float = 0.85

    /// Default ambiguity threshold from `Research/FocusRingDetectorSpec.md`.
    internal static let defaultAmbiguityThreshold: Float = 0.70

    /// Pixel size of the classifier input tensor.
    internal static let cropSize: Int = 256

    /// Extra padding applied to each side of the YOLO box before clamping and scaling.
    internal static let defaultExpansionFactor: Double = 0.16

    /// tvOS roles that can hold a focus ring. Shared with `resolveTVOSFocus`.
    internal static let focusableTypes: Set<NativeUIElementType> = [
        .collectionItem, .listRow, .primaryButton, .secondaryButton,
        .tabBar, .cancelAction, .toggle, .secureField, .textField,
        .segmentedControl, .stepperControl, .slider,
    ]

    /// One crop classification.
    package struct Result: Sendable {
        /// Model output `is_focused_prob`.
        package let isFocusedProbability: Float
        /// Model output `confidence` (distance from 0.5).
        let confidence: Float
        /// True when probability is at or above `focusThreshold`.
        let isFocused: Bool
        /// True when probability is in `[ambiguityThreshold, focusThreshold)`.
        let isAmbiguous: Bool
    }

    /// Creates a classifier, reading thresholds from CoreML user-defined metadata when present.
    package init(model: MLModel) {
        self.model = model
        self.focusThreshold = Self.metadataFloat(model, key: "focusThreshold", fallback: Self.defaultFocusThreshold)
        self.ambiguityThreshold = Self.metadataFloat(model, key: "ambiguityThreshold", fallback: Self.defaultAmbiguityThreshold)
    }

    /// Runs the compiled model on a 256×256 crop.
    ///
    /// Must not be called on the MainActor with a large batch; callers iterate crops off the
    /// UI thread (same pattern as YOLO `Task.detached` in `performDetailed`).
    package func classify(crop: CGImage) throws -> Result {
        guard crop.width == Self.cropSize, crop.height == Self.cropSize else {
            throw NativeUIDetectionError.imagePreprocessingFailed
        }
        guard let pixelBuf = Self.makePixelBuffer(crop) else {
            throw NativeUIDetectionError.imagePreprocessingFailed
        }
        let inputName = model.modelDescription.inputDescriptionsByName.keys.first ?? "image"
        let provider = try MLDictionaryFeatureProvider(dictionary: [
            inputName: MLFeatureValue(pixelBuffer: pixelBuf),
        ])
        let out = try model.prediction(from: provider)
        let prob = Self.scalar(out, names: ["is_focused_prob", "var_is_focused_prob"])
        let conf: Float
        if let c = Self.optionalScalar(out, names: ["confidence", "var_confidence"]) {
            conf = c
        } else {
            conf = abs(prob - 0.5) * 2
        }
        return Result(
            isFocusedProbability: prob,
            confidence: conf,
            isFocused: prob >= focusThreshold,
            isAmbiguous: prob >= ambiguityThreshold && prob < focusThreshold
        )
    }

    /// Expands `bbox` (pixel, top-left origin) by `expansionFactor` on each side, clamps to
    /// the screenshot, and scales the result to 256×256.
    package static func makeCrop(
        from image: CGImage,
        bbox: CGRect,
        expansionFactor: Double = 0.16,
        experimentalAspectFit: Bool = false
    ) -> CGImage? {
        let imageSize = CGSize(width: image.width, height: image.height)
        let rect = expandedCropRect(bbox: bbox, imageSize: imageSize, expansionFactor: expansionFactor)
        guard rect.width > 0, rect.height > 0 else { return nil }
        // Draw via CGContext using top-left pixel boxes (YOLO / boundingBoxPixels).
        // Avoid CGImage.cropping(to:) — its origin is bitmap-bottom-left and flips tvOS crops.
        return redrawCrop(image, rect: rect, aspectFit: experimentalAspectFit)
    }

    /// Expanded, clamped pixel rectangle used by `makeCrop`. Exposed for unit tests.
    internal static func expandedCropRect(
        bbox: CGRect,
        imageSize: CGSize,
        expansionFactor: Double = defaultExpansionFactor
    ) -> CGRect {
        let ex = bbox.width * expansionFactor
        let ey = bbox.height * expansionFactor
        let x1 = max(0, bbox.minX - ex)
        let y1 = max(0, bbox.minY - ey)
        let x2 = min(imageSize.width, bbox.maxX + ex)
        let y2 = min(imageSize.height, bbox.maxY + ey)
        return CGRect(x: x1, y: y1, width: max(0, x2 - x1), height: max(0, y2 - y1))
    }

    private static func redrawCrop(_ image: CGImage, rect: CGRect, aspectFit: Bool) -> CGImage? {
        let width = max(1, Int(rect.width.rounded()))
        let height = max(1, Int(rect.height.rounded()))
        guard let ctx = CGContext(
            data: nil,
            width: width,
            height: height,
            bitsPerComponent: 8,
            bytesPerRow: 0,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
        ) else { return nil }
        // The image draw uses bottom-left CGContext coordinates. Convert the
        // top-left box by positioning the image, not by flipping the bitmap.
        // Flipping here sampled/mirrored the opposite vertical region.
        ctx.interpolationQuality = .high
        ctx.draw(
            image,
            in: CGRect(
                x: -rect.origin.x,
                y: CGFloat(height - image.height) + rect.origin.y,
                width: CGFloat(image.width),
                height: CGFloat(image.height)
            )
        )
        guard let raw = ctx.makeImage() else { return nil }
        return scale(raw, to: cropSize, aspectFit: aspectFit)
    }

    private static func scale(_ image: CGImage, to size: Int, aspectFit: Bool) -> CGImage? {
        guard let ctx = CGContext(
            data: nil,
            width: size,
            height: size,
            bitsPerComponent: 8,
            bytesPerRow: 0,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
        ) else { return nil }
        ctx.interpolationQuality = .high
        if aspectFit {
            ctx.setFillColor(CGColor(gray: 0, alpha: 1))
            ctx.fill(CGRect(x: 0, y: 0, width: size, height: size))
            let ratio = min(CGFloat(size) / CGFloat(image.width), CGFloat(size) / CGFloat(image.height))
            let width = CGFloat(image.width) * ratio
            let height = CGFloat(image.height) * ratio
            ctx.draw(image, in: CGRect(x: (CGFloat(size) - width) / 2,
                                      y: (CGFloat(size) - height) / 2, width: width, height: height))
        } else {
            ctx.draw(image, in: CGRect(x: 0, y: 0, width: size, height: size))
        }
        return ctx.makeImage()
    }

    private static func makePixelBuffer(_ image: CGImage) -> CVPixelBuffer? {
        let attrs = [
            kCVPixelBufferCGImageCompatibilityKey: true,
            kCVPixelBufferCGBitmapContextCompatibilityKey: true,
        ] as CFDictionary
        var buf: CVPixelBuffer?
        guard CVPixelBufferCreate(
            kCFAllocatorDefault,
            image.width,
            image.height,
            kCVPixelFormatType_32BGRA,
            attrs,
            &buf
        ) == kCVReturnSuccess, let pixelBuf = buf else { return nil }

        CVPixelBufferLockBaseAddress(pixelBuf, [])
        defer { CVPixelBufferUnlockBaseAddress(pixelBuf, []) }
        guard let ctx = CGContext(
            data: CVPixelBufferGetBaseAddress(pixelBuf),
            width: image.width,
            height: image.height,
            bitsPerComponent: 8,
            bytesPerRow: CVPixelBufferGetBytesPerRow(pixelBuf),
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue
        ) else { return nil }
        ctx.draw(image, in: CGRect(x: 0, y: 0, width: image.width, height: image.height))
        return pixelBuf
    }

    private static func metadataFloat(_ model: MLModel, key: String, fallback: Float) -> Float {
        let meta = model.modelDescription.metadata
        if let raw = meta[MLModelMetadataKey(rawValue: key)] as? String, let value = Float(raw) {
            return value
        }
        if let dict = meta[.creatorDefinedKey] as? [String: String],
           let raw = dict[key],
           let value = Float(raw) {
            return value
        }
        return fallback
    }

    private static func scalar(_ out: MLFeatureProvider, names: [String]) -> Float {
        optionalScalar(out, names: names) ?? 0
    }

    private static func optionalScalar(_ out: MLFeatureProvider, names: [String]) -> Float? {
        for name in names {
            guard let value = out.featureValue(for: name) else { continue }
            if value.type == .double {
                return Float(value.doubleValue)
            }
            if let array = value.multiArrayValue, array.count > 0 {
                return Float(truncating: array[0])
            }
        }
        return nil
    }
}
