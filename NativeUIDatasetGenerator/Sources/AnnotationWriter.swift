// AnnotationWriter.swift
// NativeUIDatasetGenerator
//
// Converts a CaptureResult + GeneratorRunConfig into an annotation JSON file
// that validates against Research/schemas/annotation.schema.json v1.0.
//
// Concurrency: AnnotationWriter is a pure value-type namespace — all methods are
// static and operate on immutable inputs. Thread-safe by construction.

import CoreGraphics
import Foundation

// MARK: - AnnotationWriter

/// Serialises a `CaptureResult` into the annotation JSON format defined by
/// `annotation.schema.json v1.0`.
///
/// **Coordinate conversions (per schema spec):**
/// - `boundsPoints`: `element.frame` as-is from `GeometryReader` (top-left origin, points)
/// - `boundsPixels`: `boundsPoints × pixelScale` (top-left origin, integer pixels)
/// - `boundsVisionNormalized`: Vision bottom-left origin, values in [0, 1]
///   - `x_norm = frame.x / imageWidthPt`
///   - `y_norm = 1.0 − (frame.y + frame.height) / imageHeightPt`
///   - `w_norm = frame.width / imageWidthPt`
///   - `h_norm = frame.height / imageHeightPt`
public enum AnnotationWriter {

    // MARK: - Public API

    /// Write an annotation JSON file for a single captured image.
    ///
    /// - Parameters:
    ///   - result: The `CaptureResult` from `ScreenshotCapture.capture`.
    ///   - config: The `GeneratorRunConfig` that drove the capture.
    ///   - imageFileName: Base filename (e.g. `"img_0001.png"`) stored in the annotation.
    ///   - templateFamily: Template identifier (e.g. `"LoginForm"`).
    ///   - generatorVersion: Semantic version string of the generator binary.
    ///   - outputURL: File URL to write the JSON to (must be writable).
    /// - Throws: `AnnotationWriterError` or a file-system error.
    public static func write(
        result: CaptureResult,
        config: GeneratorRunConfig,
        imageFileName: String,
        templateFamily: String,
        generatorVersion: String,
        to outputURL: URL
    ) throws {
        let json = buildJSON(
            result: result,
            config: config,
            imageFileName: imageFileName,
            templateFamily: templateFamily,
            generatorVersion: generatorVersion
        )
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        encoder.dateEncodingStrategy = .iso8601
        let data = try encoder.encode(json)
        try data.write(to: outputURL, options: .atomic)
    }

    // MARK: - JSON construction

    static func buildJSON(
        result: CaptureResult,
        config: GeneratorRunConfig,
        imageFileName: String,
        templateFamily: String,
        generatorVersion: String
    ) -> AnnotationJSON {
        let widthPt  = Double(result.pointSize.width)
        let heightPt = Double(result.pointSize.height)
        let scale    = Double(result.scale)

        let imageInfo = AnnotationJSON.ImageInfo(
            fileName: imageFileName,
            pixelWidth: Int(result.pixelSize.width.rounded()),
            pixelHeight: Int(result.pixelSize.height.rounded()),
            scale: result.scale,
            platform: "iOS",
            osVersion: "unknown",    // populated by runner at generation time
            deviceName: config.deviceName,
            interfaceIdiom: "phone",
            orientation: "portrait",
            colorScheme: config.colorScheme.rawValue,
            dynamicTypeSize: config.dynamicTypeSize.rawValue,
            locale: config.locale,
            layoutDirection: config.layoutDirection.rawValue,
            safeAreaInsets: AnnotationJSON.EdgeInsets(
                top: Double(config.osProfile.safeAreaTopInset),
                leading: 0,
                bottom: Double(config.osProfile.safeAreaBottomInset),
                trailing: 0
            ),
            reduceTransparency: config.accessibilityFlags.reduceTransparency,
            increaseContrast: config.accessibilityFlags.increaseContrast,
            boldText: config.accessibilityFlags.boldText,
            buttonShapes: config.accessibilityFlags.buttonShapes,
            onOffLabels: config.accessibilityFlags.onOffLabels,
            smartInvert: config.accessibilityFlags.smartInvert
        )

        let generatorProfile = AnnotationJSON.GeneratorProfile(
            templateFamily: templateFamily,
            seed: config.seed,
            generatorVersion: generatorVersion,
            isolationTemplate: config.isolationTemplate,
            lowDensity: config.lowDensity,
            simulatorState: AnnotationJSON.SimulatorState(
                time: config.simulatorOverride.time,
                batteryLevel: config.simulatorOverride.batteryLevel,
                batteryState: config.simulatorOverride.batteryState,
                cellularBars: config.simulatorOverride.cellularBars,
                wifiBars: config.simulatorOverride.wifiBars,
                operatorName: config.simulatorOverride.operatorName
            )
        )

        let elements = result.elements.map { elem -> AnnotationJSON.Element in
            let f = elem.frame
            let boundsPoints = AnnotationJSON.BoundingRect(
                x: Double(f.minX),
                y: Double(f.minY),
                width: Double(f.width),
                height: Double(f.height)
            )
            let boundsPixels = AnnotationJSON.BoundingRect(
                x: (Double(f.minX) * scale).rounded(),
                y: (Double(f.minY) * scale).rounded(),
                width: (Double(f.width) * scale).rounded(),
                height: (Double(f.height) * scale).rounded()
            )
            // Vision coordinate system: x from left, y from bottom, values in [0,1].
            // Clamp to [0,1] per plan rule BP-P1: elements that overflow the screen
            // boundary are clipped to the image boundary (e.g. toolbar items near screen edge).
            let xNormRaw = Double(f.minX) / widthPt
            let yNormRaw = 1.0 - (Double(f.minY) + Double(f.height)) / heightPt
            let wNormRaw = Double(f.width) / widthPt
            let hNormRaw = Double(f.height) / heightPt
            let xNorm = max(0.0, min(1.0, xNormRaw))
            let yNorm = max(0.0, min(1.0, yNormRaw))
            // After clamping origin, shrink dimension so the far edge stays ≤ 1.
            let wNorm = max(0.0, min(wNormRaw, 1.0 - xNorm))
            let hNorm = max(0.0, min(hNormRaw, 1.0 - yNorm))
            let boundsVision = AnnotationJSON.BoundingRect(
                x: xNorm, y: yNorm, width: wNorm, height: hNorm
            )

            return AnnotationJSON.Element(
                id: elem.id,
                elementType: elem.elementType,
                framework: elem.framework,
                boundsPixels: boundsPixels,
                boundsPoints: boundsPoints,
                boundsVisionNormalized: boundsVision,
                visibleText: elem.visibleText,
                accessibilityLabel: nil,
                traits: [],
                state: AnnotationJSON.ElementState(),
                occluded: false,
                occlusionType: nil,
                excluded: false,
                exclusionReason: nil,
                knownIssues: elem.knownIssues
            )
        }

        return AnnotationJSON(
            schemaVersion: "1.0",
            imageSHA256: result.sha256,
            image: imageInfo,
            generatorProfile: generatorProfile,
            elements: elements
        )
    }
}

// MARK: - AnnotationWriterError

/// Errors surfaced by `AnnotationWriter`.
public enum AnnotationWriterError: Error, CustomStringConvertible {
    /// A Vision-normalized coordinate fell outside [0, 1].
    case coordinateOutOfBounds(elementID: String, coord: String, value: Double)

    public var description: String {
        switch self {
        case .coordinateOutOfBounds(let id, let coord, let val):
            return "Element '\(id)': \(coord) = \(val) is outside [0, 1]."
        }
    }
}

// MARK: - Codable JSON model

/// Full annotation JSON structure matching `annotation.schema.json v1.0`.
/// All fields are `Codable` so `JSONEncoder` produces the exact schema shape.
struct AnnotationJSON: Codable {

    let schemaVersion: String
    let imageSHA256: String
    let image: ImageInfo
    let generatorProfile: GeneratorProfile
    let elements: [Element]

    // MARK: Image metadata

    struct ImageInfo: Codable {
        let fileName: String
        let pixelWidth: Int
        let pixelHeight: Int
        let scale: Int
        let platform: String
        let osVersion: String
        let deviceName: String
        let interfaceIdiom: String
        let orientation: String
        let colorScheme: String
        let dynamicTypeSize: String
        let locale: String
        let layoutDirection: String
        let safeAreaInsets: EdgeInsets
        let reduceTransparency: Bool
        let increaseContrast: Bool
        let boldText: Bool
        let buttonShapes: Bool
        let onOffLabels: Bool
        let smartInvert: Bool
    }

    struct EdgeInsets: Codable {
        let top: Double
        let leading: Double
        let bottom: Double
        let trailing: Double
    }

    // MARK: Generator profile

    struct GeneratorProfile: Codable {
        let templateFamily: String
        let seed: UInt64
        let generatorVersion: String
        let isolationTemplate: Bool
        let lowDensity: Bool
        let simulatorState: SimulatorState
    }

    struct SimulatorState: Codable {
        let time: String
        let batteryLevel: Int
        let batteryState: String
        let cellularBars: Int
        let wifiBars: Int
        let operatorName: String
    }

    // MARK: Element

    struct Element: Codable {
        let id: String
        let elementType: String
        let framework: String
        let boundsPixels: BoundingRect
        let boundsPoints: BoundingRect
        let boundsVisionNormalized: BoundingRect
        let visibleText: String?
        let accessibilityLabel: String?
        let traits: [String]
        let state: ElementState
        let occluded: Bool
        let occlusionType: String?
        let excluded: Bool
        let exclusionReason: String?
        let knownIssues: [String]
    }

    struct BoundingRect: Codable {
        let x: Double
        let y: Double
        let width: Double
        let height: Double
    }

    struct ElementState: Codable {
        var isEnabled: Bool = true
        var isSelected: Bool = false
        var isFocused: Bool? = nil
        var isLoading: Bool? = nil
        var isSkeleton: Bool? = nil

        // Use encodeIfPresent for optionals so nil values are omitted from JSON.
        private enum CodingKeys: String, CodingKey {
            case isEnabled, isSelected, isFocused, isLoading, isSkeleton
        }

        func encode(to encoder: Encoder) throws {
            var c = encoder.container(keyedBy: CodingKeys.self)
            try c.encode(isEnabled,  forKey: .isEnabled)
            try c.encode(isSelected, forKey: .isSelected)
            try c.encodeIfPresent(isFocused,  forKey: .isFocused)
            try c.encodeIfPresent(isLoading,  forKey: .isLoading)
            try c.encodeIfPresent(isSkeleton, forKey: .isSkeleton)
        }

        init(from decoder: Decoder) throws {
            let c = try decoder.container(keyedBy: CodingKeys.self)
            isEnabled  = try c.decode(Bool.self, forKey: .isEnabled)
            isSelected = try c.decode(Bool.self, forKey: .isSelected)
            isFocused  = try c.decodeIfPresent(Bool.self, forKey: .isFocused)
            isLoading  = try c.decodeIfPresent(Bool.self, forKey: .isLoading)
            isSkeleton = try c.decodeIfPresent(Bool.self, forKey: .isSkeleton)
        }

        init() {}
    }
}
