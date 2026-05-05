// BoundingBoxDebugRenderer.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Post-capture utility: draws labeled colored bounding boxes onto a CaptureResult PNG
// so you can visually inspect that captured frames align with rendered elements.
//
// This file is NEVER used in production dataset generation — only in validation tests.
// Output is a debug-annotated PNG written to Documents/debug/ for manual inspection.

import CoreGraphics
import UIKit

// MARK: - BoundingBoxDebugRenderer

public enum BoundingBoxDebugRenderer {

    /// Renders `result.png` with a colored stroke box and type label over every captured element.
    ///
    /// - Parameter result: The capture result whose `.elements` frames will be drawn.
    /// - Returns: PNG data with the debug overlay burned in.
    public static func render(_ result: CaptureResult) -> Data {
        guard let uiImage = UIImage(data: result.png) else { return result.png }

        let scale = CGFloat(result.scale)
        let size  = uiImage.size  // already in pixel units when loaded from PNG

        let renderer = UIGraphicsImageRenderer(size: size)
        return renderer.pngData { ctx in
            // Draw the original screenshot
            uiImage.draw(in: CGRect(origin: .zero, size: size))

            let cgCtx = ctx.cgContext
            cgCtx.setShouldAntialias(false)  // crisp pixel-aligned boxes

            for element in result.elements {
                let type  = elementType(from: element.id)
                let color = groupColor(for: type)

                // Frame from GeometryReader is in points; convert to pixels
                let pxFrame = CGRect(
                    x: element.frame.minX * scale,
                    y: element.frame.minY * scale,
                    width:  element.frame.width  * scale,
                    height: element.frame.height * scale
                )

                drawBox(in: cgCtx, frame: pxFrame, color: color, scale: scale)
                drawLabel(in: cgCtx, text: element.id, frame: pxFrame, color: color, scale: scale)
            }
        }
    }

    // MARK: - Box drawing

    private static func drawBox(
        in ctx: CGContext,
        frame: CGRect,
        color: UIColor,
        scale: CGFloat
    ) {
        guard frame.width > 0, frame.height > 0 else { return }
        ctx.setStrokeColor(color.cgColor)
        ctx.setLineWidth(1.5 * scale)
        ctx.stroke(frame)
    }

    // MARK: - Label tag drawing

    private static func drawLabel(
        in ctx: CGContext,
        text: String,
        frame: CGRect,
        color: UIColor,
        scale: CGFloat
    ) {
        let fontSize  = 9.0 * scale
        let font      = UIFont.monospacedSystemFont(ofSize: fontSize, weight: .bold)
        let attrs: [NSAttributedString.Key: Any] = [
            .font: font,
            .foregroundColor: UIColor.white
        ]
        let labelSize = (text as NSString).size(withAttributes: attrs)
        let hPad = 3.0 * scale
        let vPad = 2.0 * scale

        let tagW = labelSize.width  + hPad * 2
        let tagH = labelSize.height + vPad * 2

        // Place tag above the box, clamped to the image top edge
        let tagY = max(0, frame.minY - tagH - scale)
        // Clamp tag to the right edge of the image too (approximate; enough for debugging)
        let tagX = frame.minX

        let tagRect = CGRect(x: tagX, y: tagY, width: tagW, height: tagH)

        // Filled background
        ctx.setFillColor(color.cgColor)
        ctx.fill(tagRect)

        // Text
        UIGraphicsPushContext(ctx)
        (text as NSString).draw(
            at: CGPoint(x: tagRect.minX + hPad, y: tagRect.minY + vPad),
            withAttributes: attrs
        )
        UIGraphicsPopContext()
    }

    // MARK: - Element type extraction

    /// Extracts the NativeUIElementType rawValue from a captureFrame id.
    /// IDs follow the convention `{elementType}_{qualifier}`, e.g. `"textField_email"`.
    private static func elementType(from id: String) -> String {
        String(id.split(separator: "_", maxSplits: 1).first ?? Substring(id))
    }

    // MARK: - Group colors

    private static func groupColor(for elementType: String) -> UIColor {
        switch elementType {
        case "statusBar", "navigationBar", "tabBar", "toolbar",
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
