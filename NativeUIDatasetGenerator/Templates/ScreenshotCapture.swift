// ScreenshotCapture.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// UIKit-based screenshot capture pipeline. Compiled exclusively into the iOS
// GeneratorRunner Xcode target; never compiled into the macOS NativeUIDatasetGenerator
// orchestrator. No #if guards are needed because this file only lives in the iOS target.
//
// Concurrency: All public entry points are @MainActor — UIKit layout and rendering
// must happen on the main thread. Async callers hop to @MainActor automatically.

import CryptoKit
import Foundation
import SwiftUI
import UIKit

// MARK: - ScreenshotCapture

/// Per-image screenshot capture pipeline.
///
/// Renders a SwiftUI view inside a `UIHostingController`, waits 150 ms for layout
/// stability (Phase 1 finding), reads element frames via `FramePreference`, then
/// captures a PNG via `UIGraphicsImageRenderer` at the device's native screen scale.
///
/// **Layout rules (Phase 1 mandate):**
/// - Root `ZStack` of every template must carry `.ignoresSafeArea(.all)`.
/// - All element positioning uses padding — never `.offset()`.
/// - Frame collection uses `GeometryReader` inside a `.captureFrame(id:)` modifier.
public enum ScreenshotCapture {

    /// Render `view` in an off-screen `UIWindow`, collect element frames via
    /// `FramePreference`, and capture a PNG at the device's native scale.
    ///
    /// - Parameters:
    ///   - view: Any SwiftUI view whose elements are annotated with `.captureFrame(id:)`.
    ///   - windowSize: Point size of the rendering canvas. Defaults to the main screen bounds.
    ///   - config: The `GeneratorRunConfig` driving this capture (used for metadata only).
    /// - Returns: A `CaptureResult` with PNG bytes, SHA-256, and frame-validated elements.
    /// - Throws: `ScreenshotCaptureError` on layout timeout or rendering failure.
    @MainActor
    public static func capture<V: View>(
        _ view: V,
        windowSize: CGSize? = nil,
        config: GeneratorRunConfig
    ) async throws -> CaptureResult {
        let screen = UIScreen.main
        let bounds = CGRect(origin: .zero, size: windowSize ?? screen.bounds.size)

        // Off-screen window — not part of the visible window hierarchy.
        let window = UIWindow(frame: bounds)
        window.isHidden = false
        window.makeKeyAndVisible()

        var capturedFrames: [String: CGRect] = [:]
        var framesReceived = false

        let wrappedView = view
            .onPreferenceChange(FramePreference.self) { frames in
                capturedFrames = frames
                framesReceived = true
            }

        let hosting = UIHostingController(rootView: wrappedView)
        hosting.view.frame = bounds
        hosting.view.backgroundColor = .clear
        window.rootViewController = hosting

        window.setNeedsLayout()
        window.layoutIfNeeded()
        hosting.view.setNeedsLayout()
        hosting.view.layoutIfNeeded()

        // 150 ms stabilization — see Research/BestPractices.md BP-04.
        // Task.sleep is the correct primitive inside an async function (BP-06).
        try await Task.sleep(for: .milliseconds(150))

        guard framesReceived else {
            window.isHidden = true
            throw ScreenshotCaptureError.frameStabilizationTimeout
        }

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

/// Propagates element bounding rects (in `.global` coordinate space) up to
/// the root view via SwiftUI's preference system.
///
/// Templates attach `.captureFrame(id:)` to each annotated element. The iOS runner
/// listens at the root with `.onPreferenceChange(FramePreference.self)`.
public struct FramePreference: PreferenceKey {
    // Computed property avoids nonisolated global mutable state (Swift 6 requirement).
    // PreferenceKey.defaultValue only needs `get`, so a computed var satisfies the protocol.
    public static var defaultValue: [String: CGRect] { [:] }
    public static func reduce(value: inout [String: CGRect], nextValue: () -> [String: CGRect]) {
        value.merge(nextValue()) { _, new in new }
    }
}

// MARK: - captureFrame modifier

public extension View {
    /// Attaches a transparent `GeometryReader` that reads this view's `.global`
    /// frame and propagates it through `FramePreference`.
    ///
    /// Every annotated element in a template must call this modifier with a unique `id`
    /// that matches a `NativeUIElementType.rawValue` (or a qualified variant like
    /// `"primaryButton_submit"`).
    ///
    /// - Parameter id: Stable string key for this element in the captured frame map.
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
