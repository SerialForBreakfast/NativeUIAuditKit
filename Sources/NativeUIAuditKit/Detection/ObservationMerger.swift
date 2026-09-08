// ObservationMerger.swift
// NativeUIAuditKit
//
// Implements the text-to-element association algorithm defined in Research/OCRFusionPolicy.md.

import CoreGraphics
import Foundation

/// A text region recognized by Apple Vision OCR.
public struct RecognizedTextRegion: Sendable, Equatable {
    public let text: String
    /// Bounding box in Vision's normalized coordinate system (bottom-left origin, [0, 1]).
    public let boundingBox: NativeUIRect
    public let confidence: Float

    public init(text: String, boundingBox: NativeUIRect, confidence: Float = 1.0) {
        self.text = text
        self.boundingBox = boundingBox
        self.confidence = confidence
    }
}

/// Reading layout direction for OCR text aggregation.
public enum NativeUILayoutDirection: String, Sendable, Codable {
    case leftToRight
    case rightToLeft
}

/// Merges OCR text observations and sidecar ground truth with detected native UI elements.
public enum ObservationMerger {

    /// 9 element classes that must never receive associated text per OCRFusionPolicy.md §5.
    public static let exemptFromTextAssociation: Set<NativeUIElementType> = [
        .toggle,
        .slider,
        .imageView,
        .mapView,
        .activityIndicator,
        .progressView,
        .pageControl,
        .scrollIndicator,
        .colorWell
    ]

    /// Associates OCR text regions with element observations, resolving conflicts and reading order.
    public static func associate(
        elements: [NativeUIElementObservation],
        ocrRegions: [RecognizedTextRegion],
        sidecar: NativeUISidecar? = nil,
        layoutDirection: NativeUILayoutDirection = .leftToRight
    ) -> [NativeUIElementObservation] {

        // 1. Group text regions by element ID
        var elementTextRegions: [UUID: [RecognizedTextRegion]] = [:]

        for ocr in ocrRegions {
            let ocrCentroid = centroid(rect: ocr.boundingBox)

            // Find all eligible candidate elements
            var candidates: [(element: NativeUIElementObservation, iou: Double, dist: Double)] = []

            for elem in elements {
                // Rule: Exempt classes never receive text association
                if exemptFromTextAssociation.contains(elem.elementType) {
                    continue
                }

                let iouVal = iou(ocr.boundingBox, elem.boundingBox)
                // Candidate filter: IoU >= 0.10
                guard iouVal >= 0.10 else { continue }

                // Candidate filter: Centroid in same image quadrant
                let elemCentroid = centroid(rect: elem.boundingBox)
                guard sameQuadrant(ocrCentroid, elemCentroid) else { continue }

                let dist = euclideanDistance(ocrCentroid, elemCentroid)
                candidates.append((elem, iouVal, dist))
            }

            // Winner selection: Highest IoU; break ties by closest centroid distance
            if let winner = candidates.sorted(by: { a, b in
                let iouDiff = a.iou - b.iou
                if abs(iouDiff) > 0.001 {
                    return a.iou > b.iou
                }
                return a.dist < b.dist
            }).first {
                elementTextRegions[winner.element.id, default: []].append(ocr)
            }
        }

        // 2. Map sidecar elements for conflict resolution
        let sidecarElements = sidecar?.elements ?? []

        // 3. Reconstruct elements with visibleText populated
        return elements.map { elem in
            let regions = elementTextRegions[elem.id] ?? []
            let ocrText = constructVisibleText(from: regions, layoutDirection: layoutDirection)

            // Match sidecar element by highest IoU
            let matchedSidecar = findMatchingSidecarElement(for: elem, in: sidecarElements)
            let sidecarText = matchedSidecar?.visibleText

            let finalVisibleText: String?
            if let sidecarText = sidecarText, !sidecarText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                if let ocrText = ocrText, !ocrText.isEmpty {
                    // Conflict resolution: Levenshtein distance <= 2 keeps sidecar, > 2 prefers OCR
                    let dist = levenshteinDistance(sidecarText.lowercased(), ocrText.lowercased())
                    if dist <= 2 {
                        finalVisibleText = sidecarText
                    } else {
                        finalVisibleText = ocrText
                    }
                } else {
                    finalVisibleText = sidecarText
                }
            } else {
                finalVisibleText = ocrText
            }

            return NativeUIElementObservation(
                id: elem.id,
                elementType: elem.elementType,
                boundingBox: elem.boundingBox,
                boundingBoxPixels: elem.boundingBoxPixels,
                confidence: elem.confidence,
                visibleText: finalVisibleText,
                inferredTraits: elem.inferredTraits,
                state: elem.state,
                issues: elem.issues,
                confidenceSource: matchedSidecar != nil ? .sidecar : elem.confidenceSource
            )
        }
    }

    // MARK: - Reading Order & Text Construction

    /// Sorts OCR text regions in reading order and concatenates into a single string.
    public static func constructVisibleText(
        from regions: [RecognizedTextRegion],
        layoutDirection: NativeUILayoutDirection
    ) -> String? {
        guard !regions.isEmpty else { return nil }

        // Vision normalized Y: bottom is 0.0, top is 1.0.
        // Top-left origin Y is: (1.0 - (y + height)).
        // We sort top-to-bottom (ascending in top-left Y, or descending in Vision top edge).
        let sorted = regions.sorted { a, b in
            let topA = a.boundingBox.y + a.boundingBox.height
            let topB = b.boundingBox.y + b.boundingBox.height
            // Bands within 0.015 (~10pt on typical screen) are treated as the same line
            if abs(topA - topB) < 0.015 {
                if layoutDirection == .rightToLeft {
                    return a.boundingBox.x > b.boundingBox.x
                } else {
                    return a.boundingBox.x < b.boundingBox.x
                }
            }
            return topA > topB // higher in Vision coords = higher on screen
        }

        let combined = sorted.map { $0.text }.joined(separator: " ")
        // Whitespace normalization: collapse multiple spaces, trim edges
        let normalized = combined
            .components(separatedBy: .whitespacesAndNewlines)
            .filter { !$0.isEmpty }
            .joined(separator: " ")

        return normalized.isEmpty ? nil : normalized
    }

    // MARK: - Geometry & Metrics

    public static func centroid(rect: NativeUIRect) -> (x: Double, y: Double) {
        (rect.x + rect.width / 2.0, rect.y + rect.height / 2.0)
    }

    public static func sameQuadrant(_ a: (x: Double, y: Double), _ b: (x: Double, y: Double)) -> Bool {
        let sameX = (a.x < 0.5) == (b.x < 0.5)
        let sameY = (a.y < 0.5) == (b.y < 0.5)
        return sameX && sameY
    }

    public static func euclideanDistance(_ a: (x: Double, y: Double), _ b: (x: Double, y: Double)) -> Double {
        let dx = a.x - b.x
        let dy = a.y - b.y
        return (dx * dx + dy * dy).squareRoot()
    }

    public static func iou(_ a: NativeUIRect, _ b: NativeUIRect) -> Double {
        let x1 = max(a.x, b.x)
        let y1 = max(a.y, b.y)
        let x2 = min(a.x + a.width, b.x + b.width)
        let y2 = min(a.y + a.height, b.y + b.height)

        let interWidth = max(0.0, x2 - x1)
        let interHeight = max(0.0, y2 - y1)
        let interArea = interWidth * interHeight
        if interArea <= 0 { return 0.0 }

        let areaA = a.width * a.height
        let areaB = b.width * b.height
        let unionArea = areaA + areaB - interArea
        return unionArea > 0 ? interArea / unionArea : 0.0
    }

    // MARK: - String Distance

    /// Standard Levenshtein edit distance between two strings.
    public static func levenshteinDistance(_ s1: String, _ s2: String) -> Int {
        let a = Array(s1)
        let b = Array(s2)
        let m = a.count
        let n = b.count

        if m == 0 { return n }
        if n == 0 { return m }

        var d = Array(repeating: Array(repeating: 0, count: n + 1), count: m + 1)

        for i in 0...m { d[i][0] = i }
        for j in 0...n { d[0][j] = j }

        for i in 1...m {
            for j in 1...n {
                let cost = (a[i - 1] == b[j - 1]) ? 0 : 1
                d[i][j] = min(
                    d[i - 1][j] + 1,      // deletion
                    d[i][j - 1] + 1,      // insertion
                    d[i - 1][j - 1] + cost // substitution
                )
            }
        }
        return d[m][n]
    }

    // MARK: - Sidecar Matching

    private static func findMatchingSidecarElement(
        for element: NativeUIElementObservation,
        in sidecarElements: [NativeUISidecarElement]
    ) -> NativeUISidecarElement? {
        var bestMatch: (element: NativeUISidecarElement, iou: Double)?

        for s in sidecarElements {
            let v = iou(element.boundingBox, s.boundsVisionNormalized)
            if v >= 0.50 {
                if bestMatch == nil || v > bestMatch!.iou {
                    bestMatch = (s, v)
                }
            }
        }
        return bestMatch?.element
    }
}
