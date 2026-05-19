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
        // Use the canonical device screen size from the OS profile when no explicit
        // windowSize is provided. UIScreen.main.bounds is unreliable in hosted test
        // contexts — the simulator may report an unexpected logical resolution that
        // causes UIKit chrome (UINavigationBar, UITabBar) to be positioned incorrectly.
        let canonicalSize = windowSize ?? config.osProfile.screenSize
        let bounds = CGRect(origin: .zero, size: canonicalSize)

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

        // Apply accessibility trait overrides so UIKit chrome (nav bar material,
        // font weight) and SwiftUI elements render with the requested accessibility
        // appearance without changing system-wide UIAccessibility settings.
        // `traitOverrides` is available on iOS 17+; the generator target requires iOS 17.
        if #available(iOS 17.0, *) {
            let flags = config.accessibilityFlags
            // Bold text: UIKit and SwiftUI render system fonts at bold weight.
            if flags.boldText {
                hosting.traitOverrides.legibilityWeight = .bold
            }
            // Increase contrast / reduce transparency: both cases benefit from
            // UIKit's high-contrast rendering (nav bar uses opaque material instead
            // of blur; system colors use higher-contrast variants).
            if flags.increaseContrast || flags.reduceTransparency {
                hosting.traitOverrides.accessibilityContrast = .high
            }
        }

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

        // Auto-detect UINavigationBar and UITabBar from the UIKit hierarchy.
        // Templates use .captureFrame on container views (NavigationStack, TabView) which
        // yields the full container frame — not the chrome strip. Walking the UIView tree
        // finds the actual UIKit chrome views and reads their real frames.
        let chromeFrames = detectChromeFrames(in: hosting.view)
        capturedFrames.merge(chromeFrames) { _, detected in detected }

        // Render at the profile's intended pixel scale, not the simulator's physical scale.
        // This ensures ios17-profile images come out @2x (750×1334px for iPhone SE) and
        // ios26-profile images come out @3x (1179×2556px for iPhone 17 Pro), regardless
        // of which simulator hardware runs the tests.
        let renderScale = CGFloat(config.pixelScale)
        let format = UIGraphicsImageRendererFormat()
        format.scale = renderScale
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

        let pixelW = bounds.width * renderScale
        let pixelH = bounds.height * renderScale
        let scaleInt = config.pixelScale

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

// MARK: - Chrome detection

extension ScreenshotCapture {

    /// Walks the UIView hierarchy rooted at `hostingView` and returns the frames of
    /// the first visible `UINavigationBar` and `UITabBar` found, converted into the
    /// hosting view's coordinate space (= SwiftUI `.global` space).
    ///
    /// Called after layout stabilises so the bars are positioned and sized correctly.
    /// Internal (not private) so `UIKitCaptureSupport.swift` can call it on the same
    /// module boundary — all sources compile into a single test bundle.
    static func detectChromeFrames(in hostingView: UIView) -> [String: CGRect] {
        var result: [String: CGRect] = [:]
        func walk(_ view: UIView) {
            guard !view.isHidden, view.alpha > 0.01 else { return }
            switch view {
            case let navBar as UINavigationBar:
                if result["navigationBar"] == nil {
                    result["navigationBar"] = navBar.convert(navBar.bounds, to: hostingView)
                }
            case let tabBar as UITabBar:
                if result["tabBar"] == nil {
                    result["tabBar"] = tabBar.convert(tabBar.bounds, to: hostingView)
                }
                // Detect individual tab items using UITabBar.items?.count.
                // iOS always distributes tab items uniformly across the bar width, so
                // dividing the bar rect evenly gives accurate bounding boxes without
                // navigating private UIKit view hierarchies (which changed in iOS 26).
                let tabBarGlobalFrame = result["tabBar"]!
                let itemCount = tabBar.items?.count ?? 0
                if itemCount > 0 {
                    let itemWidth = tabBarGlobalFrame.width / CGFloat(itemCount)
                    for i in 0..<itemCount {
                        result["tabBarItem_\(i)"] = CGRect(
                            x: tabBarGlobalFrame.minX + CGFloat(i) * itemWidth,
                            y: tabBarGlobalFrame.minY,
                            width: itemWidth,
                            height: tabBarGlobalFrame.height
                        )
                    }
                }
            default:
                break
            }
            view.subviews.forEach { walk($0) }
        }
        walk(hostingView)
        return result
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
