// UIKitCaptureSupport.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Protocol, supporting type, and ScreenshotCapture extension for UIKit-based
// template view controllers. Mirrors the SwiftUI capture path in ScreenshotCapture.swift
// but reads element frames via UIView.convert(_:to:) instead of GeometryReader.
//
// Architecture decision (Phase 4):
//   UIKit VCs express their annotated elements through the UIKitAnnotatable protocol.
//   captureUIKit() collects frames after layout, adds chrome via detectChromeFrames,
//   and renders a PNG — identical output shape to the SwiftUI path.
//
// Chrome detection: detectChromeFrames in ScreenshotCapture.swift walks the UIView
// hierarchy and finds UINavigationBar / UITabBar. UIKit templates add these views
// directly to their root view, so no special handling is required.
//
// Concurrency: All types and entry points are @MainActor — UIKit must run on the
// main thread.

import CryptoKit
import Foundation
import UIKit

// MARK: - UIKitAnnotatedView

/// Describes one annotated element in a UIKit template.
///
/// The `view` weak reference is resolved inside `captureUIKit` after layout
/// stabilises. The VC owns the view strongly; the weak reference here prevents
/// retain cycles if the protocol conformance is stored.
@MainActor
public struct UIKitAnnotatedView {
    /// Stable key used as the annotation element `id`.
    /// For multiple elements of the same type use a suffix: `"listRow_0"`, `"listRow_1"`, etc.
    public let id: String
    /// `NativeUIElementType.rawValue` — the semantic class for training.
    public let elementType: String
    /// The UIKit view whose frame is read via `convert(_:to:)` after layout.
    public weak var view: UIView?
    /// Visible text if the template knows it at capture time; `nil` otherwise.
    public let visibleText: String?
    /// Known UI issues present in this element (e.g. `["truncatedText"]`).
    /// Leave empty for all elements in "good" templates; set in known-bad generators.
    public let knownIssues: [String]

    public init(
        id: String,
        elementType: String,
        view: UIView,
        visibleText: String? = nil,
        knownIssues: [String] = []
    ) {
        self.id = id
        self.elementType = elementType
        self.view = view
        self.visibleText = visibleText
        self.knownIssues = knownIssues
    }
}

// MARK: - UIKitAnnotatable

/// Protocol adopted by UIKit template view controllers.
///
/// Conformers return their annotatable non-chrome elements. Chrome
/// (`navigationBar`, `tabBar`, `tabBarItem_N`) is auto-detected by
/// `ScreenshotCapture.detectChromeFrames` and must NOT appear here.
@MainActor
public protocol UIKitAnnotatable: UIViewController {
    /// Non-chrome annotated elements. Called after layout stabilises.
    var annotatedViews: [UIKitAnnotatedView] { get }
}

// MARK: - ScreenshotCapture.captureUIKit

extension ScreenshotCapture {

    /// Render a UIKit template VC in an off-screen UIWindow, collect element frames
    /// via `UIView.convert(_:to:)`, and capture a PNG at `config.pixelScale`.
    ///
    /// This is the UIKit counterpart to `capture(_:windowSize:config:)`. Output shape
    /// is identical — a `CaptureResult` with PNG, SHA-256, and annotated elements.
    ///
    /// - Parameters:
    ///   - viewController: A `UIKitAnnotatable` VC whose elements and layout are
    ///     ready after `viewDidLayoutSubviews`.
    ///   - config: `GeneratorRunConfig` driving this capture (window size, scale, etc.).
    /// - Returns: `CaptureResult` with PNG bytes, SHA-256, and frame-validated elements.
    /// - Throws: `ScreenshotCaptureError` on empty elements or rendering failure.
    @MainActor
    public static func captureUIKit(
        _ viewController: some UIKitAnnotatable,
        config: GeneratorRunConfig
    ) async throws -> CaptureResult {
        let canonicalSize = config.osProfile.screenSize
        let bounds = CGRect(origin: .zero, size: canonicalSize)

        let window = UIWindow(frame: bounds)
        window.rootViewController = viewController
        window.isHidden = false
        window.makeKeyAndVisible()

        window.setNeedsLayout()
        window.layoutIfNeeded()
        viewController.view.setNeedsLayout()
        viewController.view.layoutIfNeeded()

        // 150 ms stabilisation — same budget used for SwiftUI path (BP-04).
        try await Task.sleep(for: .milliseconds(150))

        // Collect non-chrome element frames.
        var elements: [AnnotatedElement] = []
        for annotated in viewController.annotatedViews {
            guard let v = annotated.view else { continue }
            let frame = v.convert(v.bounds, to: viewController.view)
            guard frame.width > 0, frame.height > 0 else { continue }
            elements.append(AnnotatedElement(
                id: annotated.id,
                elementType: annotated.elementType,
                framework: "UIKit",
                frame: frame,
                visibleText: annotated.visibleText,
                knownIssues: annotated.knownIssues
            ))
        }

        // Auto-detect UINavigationBar and UITabBar from the UIKit hierarchy.
        // Same logic used by the SwiftUI path — detectChromeFrames is internal.
        let chromeFrames = detectChromeFrames(in: viewController.view)
        for (id, frame) in chromeFrames {
            let elementType = id.hasPrefix("tabBarItem_") ? "tabBarItem" : id
            elements.append(AnnotatedElement(
                id: id,
                elementType: elementType,
                framework: "UIKit",
                frame: frame
            ))
        }

        // Note: elements may be intentionally empty for hard-negative templates
        // (loading overlay, decorative fill). Only throw if annotatedViews was
        // non-empty but frames were all zero — which would indicate a layout bug.
        let expectedElements = viewController.annotatedViews.count
        if expectedElements > 0, elements.isEmpty {
            window.isHidden = true
            throw ScreenshotCaptureError.frameStabilizationTimeout
        }

        // Render at the profile's intended pixel scale (same as SwiftUI path, BP-19).
        let renderScale = CGFloat(config.pixelScale)
        let format = UIGraphicsImageRendererFormat()
        format.scale = renderScale
        let renderer = UIGraphicsImageRenderer(bounds: bounds, format: format)
        let image = renderer.image { _ in
            viewController.view.drawHierarchy(in: bounds, afterScreenUpdates: true)
        }

        guard let pngData = image.pngData(), !pngData.isEmpty else {
            window.isHidden = true
            throw ScreenshotCaptureError.pngRenderingFailed
        }

        window.isHidden = true

        let sha = SHA256.hash(data: pngData)
        let hex = sha.map { String(format: "%02x", $0) }.joined()

        return CaptureResult(
            png: pngData,
            sha256: hex,
            elements: elements,
            pixelSize: CGSize(
                width: bounds.width * renderScale,
                height: bounds.height * renderScale
            ),
            pointSize: bounds.size,
            scale: config.pixelScale
        )
    }
}
