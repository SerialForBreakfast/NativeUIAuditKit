// NativeUIPageControlView.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Shared page-indicator views for train templates (TASK-6a-8 / BP-32).
// Holdout OnboardingPage and GalleryPage use isolated SwiftUI dots; KitchenSink
// previously packed 7pt circles and Run 007 missed 97.5% of holdout pageControl.

import SwiftUI
import UIKit

/// Opt-in generator-only styling. Existing templates retain their defaults.
public struct NativePageTrainingStyle: Sendable {
    public let placement: String
    public let tint: String
    public let rtl: Bool
    public let sceneWidth: CGFloat
    public init(placement: String, tint: String, rtl: Bool, sceneWidth: CGFloat) throws {
        guard ["leading", "center", "trailing"].contains(placement),
              ["system-blue", "semantic-label"].contains(tint), sceneWidth.isFinite, sceneWidth > 48 else { throw CocoaError(.fileReadCorruptFile) }
        self.placement = placement; self.tint = tint; self.rtl = rtl; self.sceneWidth = sceneWidth
    }
    public func center(width: CGFloat, controlWidth: CGFloat) -> CGFloat {
        let left = 24 + controlWidth / 2, right = width - 24 - controlWidth / 2
        return placement == "center" ? width / 2 : placement == "leading" ? (rtl ? right : left) : (rtl ? left : right)
    }
    @MainActor func applyTint(_ control: UIPageControl) {
        control.currentPageIndicatorTintColor = tint == "system-blue" ? .systemBlue : .label
        control.pageIndicatorTintColor = tint == "system-blue" ? .systemFill : .tertiaryLabel
    }
}

/// Development qualification helper. No existing annotation path uses this yet.
/// Measures the public control's rendered alpha, never private UIKit subviews.
@MainActor
enum NativePageVisualBounds {
    /// Controlled training variation; never applied by the default capture path.
    static func configure(_ scene: UIView, placement: String, tint: String, rtl: Bool) throws -> [String: Any] {
        guard ["leading", "center", "trailing"].contains(placement),
              ["system-blue", "semantic-label"].contains(tint) else { throw CocoaError(.fileReadCorruptFile) }
        var controls: [UIPageControl] = []
        func walk(_ view: UIView) {
            if let control = view as? UIPageControl, !control.isHidden { controls.append(control) }
            view.subviews.forEach(walk)
        }
        walk(scene)
        guard controls.count == 1, let control = controls.first, scene.window != nil else { throw CocoaError(.fileReadCorruptFile) }
        let width = control.size(forNumberOfPages: control.numberOfPages).width
        let margin: CGFloat = 24
        let left = max(margin, scene.safeAreaInsets.left) + width / 2
        let right = scene.bounds.width - max(margin, scene.safeAreaInsets.right) - width / 2
        guard width > 0, left < right else { throw CocoaError(.fileReadCorruptFile) }
        let leading = rtl ? right : left, trailing = rtl ? left : right
        let target = placement == "center" ? scene.bounds.midX : placement == "leading" ? leading : trailing
        func rgba(_ color: UIColor?) throws -> [CGFloat] {
            guard let resolved = color?.resolvedColor(with: control.traitCollection) else { throw CocoaError(.fileReadCorruptFile) }
            var r: CGFloat = 0, g: CGFloat = 0, b: CGFloat = 0, a: CGFloat = 0
            guard resolved.getRed(&r, green: &g, blue: &b, alpha: &a) else { throw CocoaError(.fileReadCorruptFile) }
            return [r,g,b,a]
        }
        return ["placement": placement, "tint": tint, "rtl": rtl, "requestedCenterX": target,
                "activeRGBA": try rgba(control.currentPageIndicatorTintColor),
                "inactiveRGBA": try rgba(control.pageIndicatorTintColor)]
    }

    /// Freeze time, not pixels or animation definitions, for this owned scene only.
    static func freezeClock(_ scene: UIView) -> () -> Void {
        let layer = scene.layer
        let speed = layer.speed, offset = layer.timeOffset, begin = layer.beginTime
        let time = layer.convertTime(CACurrentMediaTime(), from: nil)
        layer.speed = 0; layer.timeOffset = time
        return { layer.speed = speed; layer.timeOffset = offset; layer.beginTime = begin }
    }

    /// Opt-in contextual measurement, preserving the exported visible image.
    static func contextual(in scene: UIView, visible: UIImage, scale: CGFloat) throws -> (Data, CGRect, CGRect) {
        guard scale.isFinite, scale > 0, scale <= 3, scene.bounds.width > 0, scene.bounds.height > 0,
              scene.bounds.width * scale <= 4096, scene.bounds.height * scale <= 4096 else { throw CocoaError(.fileReadCorruptFile) }
        var controls: [UIPageControl] = []
        func walk(_ v: UIView) {
            guard !v.isHidden, v.alpha > 0.01 else { return }
            if let page = v as? UIPageControl { controls.append(page) }
            v.subviews.forEach(walk)
        }
        walk(scene)
        guard controls.count == 1, let control = controls.first, scene.window != nil else { throw CocoaError(.fileReadCorruptFile) }
        let frame = control.convert(control.bounds, to: scene)
        let previous = control.isHidden; control.isHidden = true
        defer { control.isHidden = previous }
        let format = UIGraphicsImageRendererFormat(); format.scale = scale
        var rendered = false
        let hidden = UIGraphicsImageRenderer(bounds: scene.bounds, format: format).image { _ in
            rendered = scene.drawHierarchy(in: scene.bounds, afterScreenUpdates: true)
        }
        guard rendered, let a = visible.cgImage, let b = hidden.cgImage,
              a.width == b.width, a.height == b.height, let data = hidden.pngData() else { throw CocoaError(.fileReadCorruptFile) }
        func pixels(_ image: CGImage) throws -> [UInt8] {
            var bytes = [UInt8](repeating: 0, count: image.width * image.height * 4)
            let valid = bytes.withUnsafeMutableBytes { storage -> Bool in
                guard let ctx = CGContext(data: storage.baseAddress, width: image.width, height: image.height,
                    bitsPerComponent: 8, bytesPerRow: image.width * 4, space: CGColorSpaceCreateDeviceRGB(),
                    bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue | CGBitmapInfo.byteOrder32Big.rawValue) else { return false }
                ctx.draw(image, in: CGRect(x: 0, y: 0, width: image.width, height: image.height)); return true
            }
            guard valid else { throw CocoaError(.fileReadCorruptFile) }; return bytes
        }
        let av = try pixels(a), bv = try pixels(b)
        var left = a.width, top = a.height, right = -1, bottom = -1
        let allowed = frame.insetBy(dx: -1, dy: -1)
        for y in 0..<a.height {
            for x in 0..<a.width {
                let i = (y * a.width + x) * 4
                if (0..<3).contains(where: { abs(Int(av[i+$0])-Int(bv[i+$0])) > 4 }) {
                    guard allowed.contains(CGPoint(x: (CGFloat(x)+0.5)/scale, y: (CGFloat(y)+0.5)/scale)) else {
                        throw NSError(domain: "NativePageBounds", code: 1, userInfo: [
                            NSLocalizedDescriptionKey: "Change outside control at pixel \(x),\(y); container \(frame)",
                            "visiblePNG": visible.pngData() ?? Data(), "hiddenPNG": data])
                    }
                    left = min(left,x); top = min(top,y); right = max(right,x); bottom = max(bottom,y)
                }
            }
        }
        guard right >= left, bottom >= top else { throw CocoaError(.fileReadCorruptFile) }
        return (data, frame, CGRect(x: CGFloat(left)/scale,y: CGFloat(top)/scale,
            width: CGFloat(right-left+1)/scale,height: CGFloat(bottom-top+1)/scale))
    }

    static func measure(_ control: UIPageControl, scale: CGFloat) throws -> CGRect {
        guard control.window != nil, scale > 0, scale <= 3,
              control.bounds.width > 0, control.bounds.height > 0,
              control.bounds.width * scale < 4096, control.bounds.height * scale < 4096 else {
            throw CocoaError(.fileReadCorruptFile)
        }
        let format = UIGraphicsImageRendererFormat()
        format.scale = scale
        format.opaque = false
        var rendered = false
        let image = UIGraphicsImageRenderer(bounds: control.bounds, format: format).image { _ in
            rendered = control.drawHierarchy(in: control.bounds, afterScreenUpdates: true)
        }
        guard rendered, let cg = image.cgImage else { throw CocoaError(.fileReadCorruptFile) }
        let width = cg.width, height = cg.height
        var rgba = [UInt8](repeating: 0, count: width * height * 4)
        let ok = rgba.withUnsafeMutableBytes { storage -> Bool in
            guard let context = CGContext(data: storage.baseAddress, width: width, height: height,
                bitsPerComponent: 8, bytesPerRow: width * 4, space: CGColorSpaceCreateDeviceRGB(),
                bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue | CGBitmapInfo.byteOrder32Big.rawValue) else { return false }
            context.draw(cg, in: CGRect(x: 0, y: 0, width: width, height: height))
            return true
        }
        guard ok else { throw CocoaError(.fileReadCorruptFile) }
        var left = width, top = height, right = -1, bottom = -1
        for y in 0..<height {
            for x in 0..<width where rgba[(y * width + x) * 4 + 3] > 4 {
                left = min(left, x); right = max(right, x)
                top = min(top, y); bottom = max(bottom, y)
            }
        }
        guard right >= left, bottom >= top else { throw CocoaError(.fileReadCorruptFile) }
        return CGRect(x: CGFloat(left) / scale, y: CGFloat(top) / scale,
                      width: CGFloat(right - left + 1) / scale, height: CGFloat(bottom - top + 1) / scale)
    }
}

/// Isolated `UIPageControl` at onboarding scale. Use this in train families so
/// the detector sees real UIKit dots, not packed kitchen-sink circles.
struct NativeUIPageControlView: UIViewRepresentable {
    var numberOfPages: Int
    var currentPage: Int
    var trainingStyle: NativePageTrainingStyle? = nil

    func makeUIView(context: Context) -> UIPageControl {
        let control = UIPageControl()
        control.numberOfPages = max(2, numberOfPages)
        control.currentPage = max(0, min(currentPage, control.numberOfPages - 1))
        control.currentPageIndicatorTintColor = .label
        control.pageIndicatorTintColor = .tertiaryLabel
        control.isUserInteractionEnabled = false
        trainingStyle?.applyTint(control)
        return control
    }

    func updateUIView(_ uiView: UIPageControl, context: Context) {
        uiView.numberOfPages = max(2, numberOfPages)
        uiView.currentPage = max(0, min(currentPage, uiView.numberOfPages - 1))
        trainingStyle?.applyTint(uiView)
    }
}

/// Isolated SwiftUI page dots matching OnboardingPage / GalleryPage holdout chrome
/// (HStack of 7pt/10pt circles, 8pt spacing). Train families that never showed
/// this style caused the Run 007 pageControl miss.
struct NativeUIPageDotsView: View {
    var pageCount: Int
    var currentPage: Int

    var body: some View {
        let count = max(2, pageCount)
        let current = max(0, min(currentPage, count - 1))
        HStack(spacing: 8) {
            ForEach(0..<count, id: \.self) { idx in
                Circle()
                    .fill(idx == current
                          ? Color.accentColor
                          : Color.secondary.opacity(0.3))
                    .frame(
                        width: idx == current ? 10 : 7,
                        height: idx == current ? 10 : 7
                    )
            }
        }
    }
}
