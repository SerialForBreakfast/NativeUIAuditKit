// CaptureTypes.swift
// NativeUIDatasetGenerator
//
// Shared value types produced by the iOS capture pipeline and consumed by
// the macOS annotation writer. No UIKit or SwiftUI dependency — compiles on
// any Apple platform.
//
// These types form the data contract between the iOS GeneratorRunner app
// (which renders and captures) and the macOS NativeUIDatasetGenerator
// orchestrator (which writes annotation JSON and the dataset manifest).

import CoreGraphics
import Foundation

// MARK: - AnnotatedElement

/// A single annotated UI element produced during a screenshot capture pass.
///
/// `frame` is the bounding rectangle in SwiftUI points measured from the
/// top-left corner of the screen (`GeometryReader` `.global` space, with
/// `.ignoresSafeArea(.all)` on the root `ZStack` — see Phase 1 findings).
public struct AnnotatedElement: Sendable {
    /// Identifier that matches the `id` passed to `.captureFrame(id:)` in the template.
    public let id: String
    /// `NativeUIElementType.rawValue` string (e.g. `"primaryButton"`).
    public let elementType: String
    /// Rendering framework: `"SwiftUI"` or `"UIKit"`.
    public let framework: String
    /// Bounding rect in SwiftUI points, top-left origin.
    public let frame: CGRect
    /// Visible text inside the element, if the template knows it at capture time.
    public let visibleText: String?
    /// Known UI issues present in this element (e.g. `["truncatedText"]`).
    /// Empty for all elements in "good" templates; populated by known-bad generators.
    public let knownIssues: [String]

    public init(
        id: String,
        elementType: String,
        framework: String = "SwiftUI",
        frame: CGRect,
        visibleText: String? = nil,
        knownIssues: [String] = []
    ) {
        self.id = id
        self.elementType = elementType
        self.framework = framework
        self.frame = frame
        self.visibleText = visibleText
        self.knownIssues = knownIssues
    }
}

// MARK: - CaptureResult

/// The complete output of a single `ScreenshotCapture.capture` call.
///
/// Passed from the iOS runner app to `AnnotationWriter` on the macOS side
/// (serialised as JSON over the file system between the two processes).
public struct CaptureResult: Sendable {
    /// Raw PNG bytes captured via `UIGraphicsImageRenderer`.
    public let png: Data
    /// Lowercase 64-character hex SHA-256 of `png`. Stable image identity.
    public let sha256: String
    /// Elements with frame data validated by `GeometryReader`.
    public let elements: [AnnotatedElement]
    /// Pixel dimensions of the captured PNG (`pointSize × scale`).
    public let pixelSize: CGSize
    /// Point dimensions at which the view was rendered.
    public let pointSize: CGSize
    /// Screen scale factor used during capture (2 or 3).
    public let scale: Int

    public init(
        png: Data,
        sha256: String,
        elements: [AnnotatedElement],
        pixelSize: CGSize,
        pointSize: CGSize,
        scale: Int
    ) {
        self.png = png
        self.sha256 = sha256
        self.elements = elements
        self.pixelSize = pixelSize
        self.pointSize = pointSize
        self.scale = scale
    }
}

// MARK: - ScreenshotCaptureError

/// Errors that can arise during a screenshot capture pass inside the iOS runner.
public enum ScreenshotCaptureError: Error, CustomStringConvertible {
    /// The view's `PreferenceKey` did not deliver frames within the stabilization window.
    case frameStabilizationTimeout
    /// `UIGraphicsImageRenderer` produced empty or nil PNG data.
    case pngRenderingFailed

    public var description: String {
        switch self {
        case .frameStabilizationTimeout:
            return "Frame stabilization timed out after 150 ms — no PreferenceKey update received."
        case .pngRenderingFailed:
            return "UIGraphicsImageRenderer produced empty PNG data."
        }
    }
}
