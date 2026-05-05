// BoundingBoxDebugRenderer.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Post-capture utility: draws labeled colored bounding boxes onto a CaptureResult PNG.
// Used exclusively in validation tests; never in production dataset generation.

import CoreGraphics
import UIKit

// MARK: - BoundingBoxDebugRenderer

public enum BoundingBoxDebugRenderer {

    /// Renders `result.png` with a colored stroke box and coordinate label over every
    /// captured element. Boxes are clamped to the canvas boundary; out-of-bounds elements
    /// are flagged with an "OOB" tag so they're immediately visible as broken.
    public static func render(_ result: CaptureResult) -> Data {
        guard let uiImage = UIImage(data: result.png) else { return result.png }

        let scale   = CGFloat(result.scale)
        let size    = uiImage.size
        let canvas  = CGRect(origin: .zero, size: size)

        // Sort: chrome elements drawn first (background) so content boxes render on top.
        let sorted = result.elements.sorted { a, b in
            chromeOrder(elementType(from: a.id)) < chromeOrder(elementType(from: b.id))
        }

        let renderer = UIGraphicsImageRenderer(size: size)
        return renderer.pngData { ctx in
            uiImage.draw(in: canvas)

            let cgCtx = ctx.cgContext
            cgCtx.setShouldAntialias(false)

            // Draw a thin white border around the canvas so the screen edge is visible.
            cgCtx.setStrokeColor(UIColor.white.withAlphaComponent(0.6).cgColor)
            cgCtx.setLineWidth(1)
            cgCtx.stroke(canvas.insetBy(dx: 0.5, dy: 0.5))

            for element in sorted {
                let type  = elementType(from: element.id)
                let color = groupColor(for: type)

                // Convert point-space frame to pixel-space.
                let pxFrame = CGRect(
                    x:      element.frame.minX * scale,
                    y:      element.frame.minY * scale,
                    width:  element.frame.width  * scale,
                    height: element.frame.height * scale
                )

                let isOOB = !canvas.intersects(pxFrame)
                    || pxFrame.width < 1 || pxFrame.height < 1

                // Clamp the drawn stroke to the canvas so out-of-bounds boxes still
                // produce a visible indicator rather than an invisible off-screen rect.
                let drawnFrame = pxFrame.intersection(canvas)
                if !drawnFrame.isNull && drawnFrame.width > 0 && drawnFrame.height > 0 {
                    drawBox(in: cgCtx, frame: drawnFrame, color: color,
                            dashed: isOOB, scale: scale)
                }

                // Label shows: id + pixel coordinates + OOB flag if applicable.
                let coordStr = String(format: "(%d,%d) %d×%d",
                                     Int(element.frame.minX), Int(element.frame.minY),
                                     Int(element.frame.width), Int(element.frame.height))
                let labelText = isOOB
                    ? "⚠ \(element.id) \(coordStr)"
                    : "\(element.id) \(coordStr)"

                // Anchor the label to wherever the drawn frame top-left is.
                let anchorX = isOOB ? 2 * scale : drawnFrame.minX
                let anchorY = isOOB ? (2 * scale + CGFloat(sorted.firstIndex(where: { $0.id == element.id }) ?? 0) * 14 * scale)
                                    : drawnFrame.minY
                drawLabel(in: cgCtx, text: labelText,
                          anchorX: anchorX, anchorY: anchorY,
                          color: isOOB ? .systemRed : color,
                          canvas: canvas, scale: scale)
            }
        }
    }

    // MARK: - Box

    private static func drawBox(
        in ctx: CGContext,
        frame: CGRect,
        color: UIColor,
        dashed: Bool,
        scale: CGFloat
    ) {
        ctx.setStrokeColor(color.cgColor)
        ctx.setLineWidth(2 * scale)

        if dashed {
            let dash: [CGFloat] = [6 * scale, 4 * scale]
            ctx.setLineDash(phase: 0, lengths: dash)
        } else {
            ctx.setLineDash(phase: 0, lengths: [])
        }

        // White shadow behind the stroke for visibility over light backgrounds.
        ctx.saveGState()
        ctx.setShadow(offset: .zero, blur: 3 * scale,
                      color: UIColor.black.withAlphaComponent(0.7).cgColor)
        ctx.stroke(frame)
        ctx.restoreGState()
    }

    // MARK: - Label

    private static func drawLabel(
        in ctx: CGContext,
        text: String,
        anchorX: CGFloat,
        anchorY: CGFloat,
        color: UIColor,
        canvas: CGRect,
        scale: CGFloat
    ) {
        let fontSize = 8.5 * scale
        let font = UIFont.monospacedSystemFont(ofSize: fontSize, weight: .semibold)
        let attrs: [NSAttributedString.Key: Any] = [
            .font: font,
            .foregroundColor: UIColor.white
        ]
        let textSize = (text as NSString).size(withAttributes: attrs)
        let hPad = 3 * scale
        let vPad = 2 * scale

        let tagW = textSize.width  + hPad * 2
        let tagH = textSize.height + vPad * 2

        // Place tag above the box; if that clips the top edge, place it below instead.
        var tagY = anchorY - tagH - scale
        if tagY < 0 { tagY = anchorY + scale }

        // Clamp X so the tag doesn't run off the right edge.
        let tagX = min(anchorX, canvas.maxX - tagW - scale)

        let tagRect = CGRect(x: tagX, y: tagY, width: tagW, height: tagH)

        // Filled pill background — slightly rounded for legibility.
        UIGraphicsPushContext(ctx)
        let pill = UIBezierPath(roundedRect: tagRect, cornerRadius: 2 * scale)

        // Semi-transparent pill: low enough alpha to see the underlying pixel content,
        // high enough for the label text to remain legible. Dark halo adds contrast.
        ctx.saveGState()
        ctx.setShadow(offset: .zero, blur: 2 * scale,
                      color: UIColor.black.withAlphaComponent(0.6).cgColor)
        color.withAlphaComponent(0.55).setFill()
        pill.fill()
        ctx.restoreGState()

        (text as NSString).draw(
            at: CGPoint(x: tagRect.minX + hPad, y: tagRect.minY + vPad),
            withAttributes: attrs
        )
        UIGraphicsPopContext()
    }

    // MARK: - Helpers

    private static func elementType(from id: String) -> String {
        String(id.split(separator: "_", maxSplits: 1).first ?? Substring(id))
    }

    /// Chrome elements sort first so content boxes are drawn on top of them.
    private static func chromeOrder(_ type: String) -> Int {
        switch type {
        case "navigationBar", "tabBar", "tabBarItem", "statusBar", "homeIndicator": return 0
        default: return 1
        }
    }

    // MARK: - Group colors

    private static func groupColor(for elementType: String) -> UIColor {
        switch elementType {
        case "statusBar", "navigationBar", "tabBar", "tabBarItem", "toolbar",
             "sidebar", "homeIndicator", "dynamicIsland":
            return UIColor(red: 0.20, green: 0.50, blue: 1.00, alpha: 1)   // blue
        case "primaryButton", "secondaryButton", "destructiveButton", "cancelAction",
             "textField", "secureField", "toggle", "slider", "segmentedControl",
             "picker", "stepperControl", "searchField", "menuButton", "colorWell":
            return UIColor(red: 0.10, green: 0.75, blue: 0.35, alpha: 1)   // green
        case "label", "imageView", "link", "mapView":
            return UIColor(red: 1.00, green: 0.55, blue: 0.10, alpha: 1)   // orange
        case "activityIndicator", "progressView", "pageControl",
             "scrollIndicator", "refreshControl":
            return UIColor(red: 0.65, green: 0.30, blue: 0.95, alpha: 1)   // purple
        case "alert", "actionSheet", "sheet", "popover",
             "listRow", "collectionItem", "disclosureGroup", "tooltip", "contextMenu":
            return UIColor(red: 1.00, green: 0.25, blue: 0.25, alpha: 1)   // red
        default:
            return UIColor(white: 0.55, alpha: 1)                           // gray
        }
    }
}
