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
/// - Manually positioned fullscreen canvases use `.ignoresSafeArea(.all)`;
///   content inside native navigation containers respects their safe area (BP-02).
/// - All element positioning uses padding — never `.offset()`.
/// - Frame collection uses `GeometryReader` inside a `.captureFrame(id:)` modifier.
public enum ScreenshotCapture {

    /// T46 recipe captures set this to render `config.colorScheme` and `config.dynamicTypeSize`.
    /// The default `false` keeps the historical behavior: both values are metadata only.
    @TaskLocal public static var rendersPresentationTraits = false

    /// T46 recipe captures set this to the requested appearance. SwiftUI template factories
    /// apply their own `.colorScheme(...)`, so a trait override alone cannot change them (BP-117).
    /// The default `nil` keeps the seeded scheme. Factories still draw the seeded value,
    /// so the other seeded fields do not change.
    @TaskLocal public static var requestedColorScheme: ColorScheme? = nil

    /// T46 recipe captures set this to apply the ACTIONS417 geometry repairs (`GeometryRepair`).
    /// The default `false` keeps the historical geometry and pixels.
    @TaskLocal public static var repairsGeometry = false

    /// The scheme that a template factory stores: the requested scheme if a task sets one, else `seeded`.
    static func colorScheme(seeded: ColorScheme) -> ColorScheme {
        requestedColorScheme ?? seeded
    }

    /// Apply the configured appearance and text size to `controller` when the task opts in.
    @MainActor
    static func applyPresentationTraits(_ config: GeneratorRunConfig, to controller: UIViewController) {
        guard rendersPresentationTraits else { return }
        controller.traitOverrides.userInterfaceStyle = config.colorScheme == .dark ? .dark : .light
        controller.traitOverrides.preferredContentSizeCategory = contentSizeCategory(config.dynamicTypeSize)
    }

    private static func contentSizeCategory(_ size: GeneratorDynamicTypeSize) -> UIContentSizeCategory {
        switch size {
        case .xSmall: return .extraSmall
        case .small: return .small
        case .medium: return .medium
        case .large: return .large
        case .xLarge: return .extraLarge
        case .xxLarge: return .extraExtraLarge
        case .xxxLarge: return .extraExtraExtraLarge
        case .accessibilityMedium: return .accessibilityMedium
        case .accessibilityLarge: return .accessibilityLarge
        case .accessibilityExtraLarge: return .accessibilityExtraLarge
        case .accessibilityExtraExtraLarge: return .accessibilityExtraExtraLarge
        case .accessibilityExtraExtraExtraLarge: return .accessibilityExtraExtraExtraLarge
        }
    }

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
        config: GeneratorRunConfig,
        nativePageEvidence: ((Data, CGRect, CGRect) -> Void)? = nil,
        nativePageConfiguration: ((UIView) throws -> Void)? = nil
    ) async throws -> CaptureResult {
        // Use the canonical device screen size from the OS profile when no explicit
        // windowSize is provided. UIScreen.main.bounds is unreliable in hosted test
        // contexts — the simulator may report an unexpected logical resolution that
        // causes UIKit chrome (UINavigationBar, UITabBar) to be positioned incorrectly.
        let canonicalSize = windowSize ?? config.osProfile.screenSize
        let bounds = CGRect(origin: .zero, size: canonicalSize)

        // Off-screen window — not part of the visible window hierarchy.
        let window = UIWindow(frame: bounds)
        window.isHidden = false
        defer { window.isHidden = true; window.rootViewController = nil }
        window.makeKeyAndVisible()

        var capturedFrames: [String: CGRect] = [:]
        var framesReceived = false

        let wrappedView = view
            .onPreferenceChange(FramePreference.self) { frames in
                capturedFrames = frames
                framesReceived = true
            }

        // Templates read the revision when they must change their own layout. Revision 1 is the historical layout.
        let hosting = UIHostingController(rootView: wrappedView
            .environment(\.generatorGeometryRevision, repairsGeometry ? 2 : 1))
        hosting.view.frame = bounds
        hosting.view.backgroundColor = .clear
        applyPresentationTraits(config, to: hosting)
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

        try nativePageConfiguration?(hosting.view)
        let repairing = repairsGeometry
        if repairing {
            GeometryRepair.hideScrollIndicators(in: hosting.view)
        }

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
        if repairing {
            capturedFrames = GeometryRepair.switchBodies(capturedFrames, in: hosting.view)
            capturedFrames = GeometryRepair.searchFieldBody(capturedFrames, in: hosting.view)
            capturedFrames = try GeometryRepair.nativeListRows(capturedFrames, in: hosting.view)
        }

        // Render at the profile's intended pixel scale, not the simulator's physical scale.
        // This ensures ios17-profile images come out @2x (750×1334px for iPhone SE) and
        // ios26-profile images come out @3x (1179×2556px for iPhone 17 Pro), regardless
        // of which simulator hardware runs the tests.
        let renderScale = CGFloat(config.pixelScale)
        let restoreClock = nativePageEvidence == nil ? nil : NativePageVisualBounds.freezeClock(hosting.view)
        defer { restoreClock?() }
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

        if let evidence = nativePageEvidence {
            let (hidden, container, body) = try NativePageVisualBounds.contextual(in: hosting.view, visible: image, scale: renderScale)
            let ids = capturedFrames.keys.filter { $0.components(separatedBy: "_").first == "pageControl" }
            guard ids.count == 1, let id = ids.first else { throw CocoaError(.fileReadCorruptFile) }
            capturedFrames[id] = body
            evidence(hidden, container, body)
        }
        window.isHidden = true

        let sha = SHA256.hash(data: pngData)
        let hex = sha.map { String(format: "%02x", $0) }.joined()

        let pixelW = bounds.width * renderScale
        let pixelH = bounds.height * renderScale
        let scaleInt = config.pixelScale

        let covers = repairing ? GeometryRepair.covers(capturedFrames, canvas: bounds) : [:]
        let elements = capturedFrames.map { id, frame in
            // elementType is the class prefix of the captureFrame id.
            // Convention: id = "{elementType}_{suffix}" (e.g. "slider_0", "label_title").
            // Strip the suffix so classDistribution records canonical types ("slider", "label").
            let elementType = id.components(separatedBy: "_").first ?? id
            let isFocused: Bool? = id.contains("_focused") ? true : (id.contains("_unfocused") ? false : nil)
            guard let cover = covers[id] else {
                return AnnotatedElement(id: id, elementType: elementType, frame: frame, isFocused: isFocused)
            }
            return AnnotatedElement(id: id, elementType: elementType, frame: cover.visible, isFocused: isFocused,
                                    occlusionType: cover.excluded ? nil : "scroll",
                                    exclusionReason: cover.excluded ? "coveredByChrome" : nil)
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
    @MainActor
    static func detectChromeFrames(in hostingView: UIView) -> [String: CGRect] {
        var result: [String: CGRect] = [:]
        func walk(_ view: UIView) {
            guard !view.isHidden, view.alpha > 0.01 else { return }
            switch view {
            case let searchField as UISearchTextField:
                let rect = searchField.convert(searchField.bounds, to: hostingView)
                if result["searchField_0"] == nil,
                   !rect.isEmpty, rect.intersects(hostingView.bounds) {
                    result["searchField_0"] = rect
                }
            case let navBar as UINavigationBar:
                if result["navigationBar"] == nil {
                    result["navigationBar"] = navBar.convert(navBar.bounds, to: hostingView)
                }
            case let toolbar as UIToolbar:
                // Bottom toolbar (from .toolbar { ToolbarItemGroup(placement: .bottomBar) }).
                // Distinct from UITabBar — narrower height, content-editing context.
                if result["toolbar"] == nil {
                    result["toolbar"] = toolbar.convert(toolbar.bounds, to: hostingView)
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

// MARK: - Geometry revision (ACTIONS417)

private struct GeneratorGeometryRevisionKey: EnvironmentKey {
    static let defaultValue = 1
}

public extension EnvironmentValues {
    /// Layout revision for templates. 1 is the historical layout. `ScreenshotCapture` sets 2 when
    /// `repairsGeometry` is on. A template reads it only to change its own layout for revision 2.
    var generatorGeometryRevision: Int {
        get { self[GeneratorGeometryRevisionKey.self] }
        set { self[GeneratorGeometryRevisionKey.self] = newValue }
    }
}

/// Geometry repairs for T46 recipe captures (ACTIONS417, B405-032 successors). Not used by default captures.
///
/// - A SwiftUI `Toggle` reports a 61 pt layout frame, but its native switch draws 63 pt (iOS 26).
///   The repair uses the drawn switch extent for the toggle and for each box that contains the toggle.
/// - iOS 26 draws the search field platter outside the `UISearchTextField` frame. The repair uses the platter.
/// - Native scroll indicators flash after layout. No template labels them, so the repair hides them.
/// - Content under a tab bar, a toolbar, or the top strip above a navigation bar is covered.
///   The repair clips the box to the visible part and marks it occluded (`scroll`), or excludes it
///   (`coveredByChrome`) when less than 20 % stays visible. Research/NativeUIElementDetection.md
///   asks for the visible rectangle and an occlusion flag for partly hidden content.
enum GeometryRepair {

    /// A box after the cover pass.
    struct Cover {
        let visible: CGRect
        let excluded: Bool
    }

    /// Classes that are chrome. Chrome and the content inside chrome are not covered by chrome.
    static let chromeClasses: Set<String> = [
        "navigationBar", "tabBar", "toolbar", "statusBar", "homeIndicator", "dynamicIsland", "tabBarItem",
    ]
    /// Overlays draw above bars, so they and their content are not covered by bars.
    static let overlayClasses: Set<String> = [
        "sheet", "alert", "actionSheet", "popover", "contextMenu", "tooltip",
    ]
    /// Below this visible fraction an element is excluded (the schema's 20 % rule).
    static let minimumVisibleFraction: CGFloat = 0.2

    @MainActor
    static func hideScrollIndicators(in root: UIView) {
        func walk(_ view: UIView) {
            if let scroll = view as? UIScrollView {
                scroll.showsVerticalScrollIndicator = false
                scroll.showsHorizontalScrollIndicator = false
            }
            view.subviews.forEach(walk)
        }
        walk(root)
        root.setNeedsLayout()
        root.layoutIfNeeded()
    }

    /// The union of a view and its visible subviews, in `root` coordinates.
    @MainActor
    static func visualExtent(of view: UIView, in root: UIView) -> CGRect {
        var rect = view.convert(view.bounds, to: root)
        for sub in view.subviews where !sub.isHidden && sub.alpha > 0.01 {
            rect = rect.union(visualExtent(of: sub, in: root))
        }
        return rect
    }

    /// Replace each `toggle_*` box with the union of its layout frame and the drawn native switch.
    /// Each box that contained the original toggle box grows by the same amount.
    @MainActor
    static func switchBodies(_ frames: [String: CGRect], in root: UIView) -> [String: CGRect] {
        var switches: [CGRect] = []
        func walk(_ view: UIView) {
            guard !view.isHidden, view.alpha > 0.01 else { return }
            if let control = view as? UISwitch {
                switches.append(visualExtent(of: control, in: root))
                return
            }
            view.subviews.forEach(walk)
        }
        walk(root)
        func area(_ rect: CGRect) -> CGFloat { rect.isNull ? 0 : rect.width * rect.height }
        var repaired = frames
        for (id, frame) in frames where id.hasPrefix("toggle_") {
            let candidates = switches.filter { area($0.intersection(frame)) > 0 }
            guard let body = candidates.max(by: { area($0.intersection(frame)) < area($1.intersection(frame)) }) else {
                print("T46_SWITCH \(id) layout=\(frame) body=none")
                continue
            }
            print("T46_SWITCH \(id) layout=\(frame) body=\(body)")
            let grown = frame.union(body)
            guard grown != frame else { continue }
            repaired[id] = grown
            for (other, outer) in frames where other != id && outer.contains(frame) {
                repaired[other] = (repaired[other] ?? outer).union(body)
            }
        }
        return repaired
    }

    /// The largest search field margin that still counts as the field's own platter.
    static let searchPlatterMargin: CGFloat = 8

    /// Replace `searchField_0` with the drawn platter around the native `UISearchTextField`.
    /// iOS 26 draws a glass capsule up to a few points outside the text field; dark mode shows its edge.
    @MainActor
    static func searchFieldBody(_ frames: [String: CGRect], in root: UIView) -> [String: CGRect] {
        guard let frame = frames["searchField_0"] else { return frames }
        var field: UISearchTextField?
        func walk(_ view: UIView) {
            guard field == nil, !view.isHidden, view.alpha > 0.01 else { return }
            if let candidate = view as? UISearchTextField, candidate.convert(candidate.bounds, to: root) == frame {
                field = candidate
                return
            }
            view.subviews.forEach(walk)
        }
        walk(root)
        guard let field else { return frames }
        var body = frame
        var ancestor = field.superview
        var chain: [String] = []
        for _ in 0..<4 {
            guard let view = ancestor, view !== root else { break }
            let rect = view.convert(view.bounds, to: root)
            chain.append("\(type(of: view))=\(rect)")
            let margins = [frame.minX - rect.minX, frame.minY - rect.minY, rect.maxX - frame.maxX, rect.maxY - frame.maxY]
            if margins.allSatisfy({ $0 >= 0 && $0 <= searchPlatterMargin }) {
                body = body.union(rect)
            }
            ancestor = view.superview
        }
        print("T46_SEARCH layout=\(frame) body=\(body) chain=\(chain.joined(separator: " "))")
        var repaired = frames
        repaired["searchField_0"] = body
        return repaired
    }

    enum RowEvidenceError: Error {
        case missingOrAmbiguousCell(String)
    }

    /// Replace aliased text measurements with the containing native cell bounds.
    /// Keep label bounds unchanged. Missing or ambiguous cells fail capture.
    static func nativeListRows(_ frames: [String: CGRect], in root: UIView) throws -> [String: CGRect] {
        var cells: [CGRect] = []
        func walk(_ view: UIView) {
            guard !view.isHidden, view.alpha > 0.01 else { return }
            if view is UITableViewCell || view is UICollectionViewCell {
                let rect = view.convert(view.bounds, to: root)
                if !rect.isEmpty, !rect.isNull, !rect.isInfinite, !cells.contains(rect) {
                    cells.append(rect)
                }
            }
            view.subviews.forEach(walk)
        }
        walk(root)
        var result = frames
        for (id, label) in frames where id.hasPrefix("label_row_") {
            let suffix = String(id.dropFirst("label_row_".count))
            guard Int(suffix) != nil else { continue }
            let rowID = "listRow_" + suffix
            guard frames[rowID] == label else { continue }
            let matches = cells.filter {
                $0.insetBy(dx: -0.5, dy: -0.5).contains(label) && $0 != label
            }
            guard matches.count == 1, let body = matches.first else {
                throw RowEvidenceError.missingOrAmbiguousCell(rowID)
            }
            result[rowID] = body
            print("T46_NATIVE_ROW id=\(rowID) label=\(label) nativeCell=\(body)")
        }
        return result
    }

    /// Cover results for content under bars. Elements that are not covered are absent from the result.
    static func covers(_ frames: [String: CGRect], canvas: CGRect) -> [String: Cover] {
        func type(_ id: String) -> String { id.components(separatedBy: "_").first ?? id }
        var regions: [CGRect] = []
        if let bar = frames["navigationBar"], bar.minY > canvas.minY {
            // iOS 26 blurs scroll content in the top strip above the bar.
            regions.append(CGRect(x: canvas.minX, y: canvas.minY, width: canvas.width, height: bar.minY - canvas.minY))
        }
        for key in ["tabBar", "toolbar"] {
            if let bar = frames[key] { regions.append(bar) }
        }
        guard !regions.isEmpty else { return [:] }
        let exempt = frames.filter { chromeClasses.contains(type($0.key)) || overlayClasses.contains(type($0.key)) }
        var result: [String: Cover] = [:]
        for (id, frame) in frames where frame.width > 0 && frame.height > 0 {
            if exempt.contains(where: { $0.value.contains(frame) }) { continue }
            let hits = regions.filter { $0.intersects(frame) && !frame.contains($0) }
            guard !hits.isEmpty else { continue }
            var visible = frame
            var hidden: CGFloat = 0
            for region in hits {
                let spans = region.minX <= visible.minX && region.maxX >= visible.maxX
                if spans && region.minY <= visible.minY && region.maxY > visible.minY {
                    visible = CGRect(x: visible.minX, y: region.maxY, width: visible.width,
                                     height: max(0, visible.maxY - region.maxY))
                } else if spans && region.maxY >= visible.maxY && region.minY < visible.maxY {
                    visible = CGRect(x: visible.minX, y: visible.minY, width: visible.width,
                                     height: max(0, region.minY - visible.minY))
                } else {
                    let overlap = region.intersection(visible)
                    hidden += overlap.isNull ? 0 : overlap.width * overlap.height
                }
            }
            let fraction = max(0, visible.width * visible.height - hidden) / (frame.width * frame.height)
            let excluded = fraction < minimumVisibleFraction
            result[id] = Cover(visible: excluded ? frame : visible, excluded: excluded)
        }
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

    /// `captureFrame(id:)` when `condition` is true; otherwise the view is unchanged.
    @ViewBuilder
    func captureFrame(id: String, when condition: Bool) -> some View {
        if condition {
            captureFrame(id: id)
        } else {
            self
        }
    }
}
