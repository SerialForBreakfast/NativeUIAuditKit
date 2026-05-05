// ScreenshotCapture.swift
// NativeUIDatasetGenerator
//
// Per-image capture pipeline for the dataset generator.
// Must run inside an iOS Simulator context (UIHostingController + UIGraphicsImageRenderer).
// This file compiles only on platforms that have UIKit (iOS/iPadOS/tvOS) and is a
// compile-time stub on macOS. The macOS orchestrator drives the iOS app target via xcrun.
//
// Concurrency: All public entry points are @MainActor because UIKit layout and rendering
// must occur on the main thread. Callers from async contexts must hop to @MainActor first.

import CoreGraphics
import CryptoKit
import Foundation
import SwiftUI

// MARK: - Shared types (available on all platforms)

/// A single annotated element produced during a screenshot capture pass.
///
/// `frame` is the element's bounding rectangle in SwiftUI points,
/// measured from the top-left corner of the screen (`.global` coordinate space,
/// with `ignoresSafeArea(.all)` applied to the root ZStack per Phase 1 findings).
public struct AnnotatedElement: Sendable {
    public let id: String
    public let elementType: String     // NativeUIElementType.rawValue
    public let framework: String       // "SwiftUI" | "UIKit"
    public let frame: CGRect           // points, GeometryReader global space
    public let visibleText: String?

    public init(
        id: String,
        elementType: String,
        framework: String = "SwiftUI",
        frame: CGRect,
        visibleText: String? = nil
    ) {
        self.id = id
        self.elementType = elementType
        self.framework = framework
        self.frame = frame
        self.visibleText = visibleText
    }
}

/// The output of a single `ScreenshotCapture.capture` call.
public struct CaptureResult: Sendable {
    /// Raw PNG bytes captured via `UIGraphicsImageRenderer`.
    public let png: Data
    /// Lowercase hex SHA-256 of `png`. Stable identifier for the image file.
    public let sha256: String
    /// Elements with validated frame data from `GeometryReader`.
    public let elements: [AnnotatedElement]
    /// Pixel dimensions of the captured PNG.
    public let pixelSize: CGSize
    /// Point size at which the view was rendered (pixelSize / scale).
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

// MARK: - Capture errors

/// Errors that can arise during a screenshot capture pass.
public enum ScreenshotCaptureError: Error, CustomStringConvertible {
    /// The view's `PreferenceKey` did not fire within the stabilization timeout.
    case frameStabilizationTimeout
    /// `UIGraphicsImageRenderer` produced no data.
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

// MARK: - UIKit-only capture implementation

#if canImport(UIKit)
import UIKit

/// Per-image screenshot capture pipeline.
///
/// Renders a SwiftUI view inside a `UIHostingController`, waits 150 ms for layout
/// stability (per Phase 1 Phase 1 findings), reads element frames via `GeometryReader`
/// `PreferenceKey` callbacks, then captures a PNG via `UIGraphicsImageRenderer`.
///
/// **Threading:** All methods are `@MainActor`. Call from async tests or the main
/// run loop of the iOS runner app. Never call from a background queue.
///
/// **Layout rules (Phase 1 mandate):**
/// - Root `ZStack` of the provided view must carry `.ignoresSafeArea(.all)`.
/// - All element positioning must use padding, never `.offset()`.
/// - Frame collection must use `GeometryReader` inside a `PreferenceKey` chain.
public enum ScreenshotCapture {

    /// Render `view` in an off-screen `UIWindow`, collect element frames, and
    /// capture a PNG at the device's native scale.
    ///
    /// - Parameters:
    ///   - view: A SwiftUI view conforming to ``CaptureableView`` — i.e., it must
    ///     propagate element frames via `FramePreference` and accept an `onFramesCaptured`
    ///     callback.
    ///   - windowSize: Point dimensions of the rendering window (defaults to screen bounds).
    ///   - onFramesCaptured: Injected by the template; called by the view's
    ///     `onPreferenceChange` with the full `[String: CGRect]` map.
    ///   - config: The generator run configuration for this image.
    /// - Returns: A `CaptureResult` containing the PNG, its SHA-256, and annotated elements.
    /// - Throws: `ScreenshotCaptureError` if layout stabilization times out or rendering fails.
    @MainActor
    public static func capture<V: View>(
        _ view: V,
        windowSize: CGSize? = nil,
        config: GeneratorRunConfig
    ) async throws -> CaptureResult {
        let screen = UIScreen.main
        let bounds = CGRect(origin: .zero, size: windowSize ?? screen.bounds.size)

        // Off-screen UIWindow — not added to the main window hierarchy.
        let window = UIWindow(frame: bounds)
        window.isHidden = false
        window.makeKeyAndVisible()

        var capturedFrames: [String: CGRect] = [:]
        var framesReceived = false

        // Wrap the caller's view to intercept FramePreference updates.
        let wrappedView = view
            .onPreferenceChange(FramePreference.self) { frames in
                capturedFrames = frames
                framesReceived = true
            }

        let hosting = UIHostingController(rootView: wrappedView)
        hosting.view.frame = bounds
        hosting.view.backgroundColor = .clear

        window.rootViewController = hosting

        // Force an immediate layout pass.
        window.setNeedsLayout()
        window.layoutIfNeeded()
        hosting.view.setNeedsLayout()
        hosting.view.layoutIfNeeded()

        // Phase 1 finding: 150 ms is sufficient for SwiftUI layout to stabilize.
        // RunLoop.main.run(until:) is used here because this may be called from a
        // synchronous context inside the iOS runner app; for async tests, prefer
        // `Task.sleep(for:)` as used in CoordSpikeHostedTests.
        RunLoop.main.run(until: Date(timeIntervalSinceNow: 0.15))

        guard framesReceived else {
            window.isHidden = true
            throw ScreenshotCaptureError.frameStabilizationTimeout
        }

        // Capture PNG at native screen scale.
        let format = UIGraphicsImageRendererFormat()
        format.scale = screen.scale
        let renderer = UIGraphicsImageRenderer(bounds: bounds, format: format)
        let image = renderer.image { _ in
            hosting.view.drawHierarchy(in: bounds, afterScreenUpdates: true)
        }

        guard let pngData = image.pngData(), !pngData.isEmpty else {
            window.isHidden = true
            throw ScreenshotCaptureError.pngRenderingFailed
        }

        window.isHidden = true

        let sha = SHA256.hash(data: pngData)
        let hex = sha.map { String(format: "%02x", $0) }.joined()

        let pixelW = bounds.width * screen.scale
        let pixelH = bounds.height * screen.scale
        let scaleInt = Int(screen.scale.rounded())

        let elements = capturedFrames.map { id, frame in
            AnnotatedElement(id: id, elementType: id, frame: frame)
        }

        return CaptureResult(
            png: pngData,
            sha256: hex,
            elements: elements,
            pixelSize: CGSize(width: pixelW, height: pixelH),
            pointSize: bounds.size,
            scale: scaleInt
        )
    }
}

// MARK: - FramePreference

/// Propagates element bounding rects (in `.global` coordinate space) from
/// child views to the root view via SwiftUI's preference system.
///
/// Templates set frames using `GeometryReader` inside a `.background` modifier,
/// reading `.frame(in: .global)` and passing the result through this preference.
/// The root `ZStack` listens with `.onPreferenceChange(FramePreference.self)`.
public struct FramePreference: PreferenceKey {
    public static var defaultValue: [String: CGRect] = [:]
    public static func reduce(value: inout [String: CGRect], nextValue: () -> [String: CGRect]) {
        value.merge(nextValue()) { _, new in new }
    }
}

/// Convenience modifier that attaches a `GeometryReader` background to a view,
/// capturing the view's global frame and propagating it via `FramePreference`.
///
/// Usage:
/// ```swift
/// Button("OK") { }
///     .captureFrame(id: "okButton")
/// ```
public extension View {
    /// Attaches a transparent `GeometryReader` that reads the view's `.global`
    /// frame and sends it to `FramePreference` with the given identifier.
    ///
    /// - Parameter id: Unique string identifier matching an `AnnotatedElement.id`.
    func captureFrame(id: String) -> some View {
        background(
            GeometryReader { geo in
                Color.clear
                    .preference(
                        key: FramePreference.self,
                        value: [id: geo.frame(in: .global)]
                    )
            }
        )
    }
}

#else

// MARK: - FramePreference stub (macOS compilation only)

/// Propagates element bounding rects from child views to the root. macOS stub — no-op at runtime;
/// real implementation lives in the `#if canImport(UIKit)` block above.
public struct FramePreference: PreferenceKey {
    // Computed property satisfies PreferenceKey's `static var defaultValue: Value { get }`
    // requirement without introducing mutable global state (Swift 6 compliant).
    public static var defaultValue: [String: CGRect] { [:] }
    public static func reduce(value: inout [String: CGRect], nextValue: () -> [String: CGRect]) {
        value.merge(nextValue()) { _, new in new }
    }
}

/// No-op `captureFrame` for macOS builds. Templates use this modifier;
/// the real implementation runs only inside the iOS Simulator.
public extension View {
    func captureFrame(id: String) -> some View { self }
}

#endif // canImport(UIKit)
