// AuditRules.swift
// NativeUIAuditKit
//
// Automated UI and accessibility audit rules evaluating detected elements.

import CoreGraphics
import Foundation

/// Pure functional audit rules evaluating detected native UI elements against screenshot geometry.
public enum AuditRules {

    /// Interactive element types that require at least a 44×44 pt touch target per Apple HIG.
    public static let interactiveControlClasses: Set<NativeUIElementType> = [
        .primaryButton,
        .secondaryButton,
        .destructiveButton,
        .cancelAction,
        .toggle,
        .textField,
        .secureField,
        .searchField,
        .menuButton,
        .link,
        .colorWell
    ]

    /// Edge-to-edge chrome elements that naturally touch the screenshot boundary and are exempt from clipping.
    public static let edgeChromeClasses: Set<NativeUIElementType> = [
        .navigationBar,
        .tabBar,
        .statusBar,
        .toolbar,
        .homeIndicator,
        .dynamicIsland
    ]

    /// Container element types that legitimately enclose nested child elements.
    public static let containerClasses: Set<NativeUIElementType> = [
        .navigationBar,
        .tabBar,
        .toolbar,
        .listRow,
        .collectionItem,
        .alert,
        .actionSheet,
        .sheet,
        .popover,
        .disclosureGroup
    ]

    /// Terminal punctuation characters that indicate a completed sentence or clause.
    private static let terminalPunctuation: Set<Character> = [".", "!", "?", ",", ":", ";", ")", "\"", "'", "”", "’"]

    /// Evaluates all audit rules for an array of observations in a screenshot of given size.
    public static func evaluate(
        observations: [NativeUIElementObservation],
        imageSize: CGSize,
        scale: Double? = nil
    ) -> [NativeUIElementObservation] {

        let effectiveScale = scale ?? (imageSize.width >= 1000 ? 3.0 : 2.0)
        var issuesByObservationId: [UUID: [NativeUIIssue]] = [:]

        // 1. Single-element rules: Truncation, Clipping, Target Size
        for obs in observations {
            var elementIssues: [NativeUIIssue] = []

            if let truncIssue = checkTruncation(obs) {
                elementIssues.append(truncIssue)
            }

            if let clipIssue = checkClipping(obs, imageSize: imageSize) {
                elementIssues.append(clipIssue)
            }

            if let sizeIssue = checkTappableTargetSize(obs, scale: effectiveScale) {
                elementIssues.append(sizeIssue)
            }

            issuesByObservationId[obs.id] = elementIssues
        }

        // 2. Multi-element rules: Overlapping Elements
        let overlapIssues = checkOverlappingElements(observations)
        for (id, issue) in overlapIssues {
            issuesByObservationId[id, default: []].append(issue)
        }

        // 3. Return reconstructed observations with issues attached
        return observations.map { obs in
            let combinedIssues = obs.issues + (issuesByObservationId[obs.id] ?? [])
            return NativeUIElementObservation(
                id: obs.id,
                elementType: obs.elementType,
                boundingBox: obs.boundingBox,
                boundingBoxPixels: obs.boundingBoxPixels,
                confidence: obs.confidence,
                visibleText: obs.visibleText,
                inferredTraits: obs.inferredTraits,
                state: obs.state,
                issues: combinedIssues,
                confidenceSource: obs.confidenceSource
            )
        }
    }

    // MARK: - Rule 1: Text Truncation

    /// Evaluates whether visible text inside an element appears prematurely truncated.
    public static func checkTruncation(_ obs: NativeUIElementObservation) -> NativeUIIssue? {
        guard let text = obs.visibleText?.trimmingCharacters(in: .whitespacesAndNewlines),
              !text.isEmpty else {
            return nil
        }

        // Exempt classes never have text truncation evaluated
        if ObservationMerger.exemptFromTextAssociation.contains(obs.elementType) {
            return nil
        }

        // Condition B (Textual): Ends with ellipsis (U+2026) OR last word < 3 chars without terminal punctuation
        let endsWithEllipsis = text.hasSuffix("…") || text.hasSuffix("...")
        var suspiciousWordEnding = false

        if !endsWithEllipsis {
            let words = text.components(separatedBy: .whitespacesAndNewlines).filter { !$0.isEmpty }
            if let lastWord = words.last {
                if lastWord.count < 3 {
                    if let lastChar = lastWord.last, !terminalPunctuation.contains(lastChar) {
                        suspiciousWordEnding = true
                    }
                }
            }
        }

        guard endsWithEllipsis || suspiciousWordEnding else {
            return nil
        }

        // Confidence: 0.85 when ending with ellipsis, 0.60 when suspicious word ending
        let confidence = endsWithEllipsis ? 0.85 : 0.60
        let reason = endsWithEllipsis
            ? "Visible text terminates with an ellipsis ('\(text)')."
            : "Visible text terminates with a partial token ('\(text)')."

        return NativeUIIssue(kind: .truncatedText, description: reason, confidence: confidence)
    }

    // MARK: - Rule 2: Element Clipping

    /// Evaluates whether an element's bounding box is cut off by the screenshot boundary.
    public static func checkClipping(_ obs: NativeUIElementObservation, imageSize: CGSize) -> NativeUIIssue? {
        // Edge-to-edge chrome is designed to touch the borders
        if edgeChromeClasses.contains(obs.elementType) {
            return nil
        }

        let b = obs.boundingBoxPixels
        let tolerance = 2.0

        let clippedLeft   = b.x <= tolerance
        let clippedTop    = b.y <= tolerance
        let clippedRight  = (b.x + b.width) >= (Double(imageSize.width) - tolerance)
        let clippedBottom = (b.y + b.height) >= (Double(imageSize.height) - tolerance)

        if clippedLeft || clippedTop || clippedRight || clippedBottom {
            var edges: [String] = []
            if clippedLeft { edges.append("left") }
            if clippedTop { edges.append("top") }
            if clippedRight { edges.append("right") }
            if clippedBottom { edges.append("bottom") }

            return NativeUIIssue(
                kind: .clippedElement,
                description: "Element bounds touch the screenshot boundary (\(edges.joined(separator: ", ")) edge).",
                confidence: 0.90
            )
        }

        return nil
    }

    // MARK: - Rule 3: Tappable Target Too Small

    /// Evaluates whether an interactive element meets Apple's 44×44 pt minimum touch target guideline.
    public static func checkTappableTargetSize(_ obs: NativeUIElementObservation, scale: Double) -> NativeUIIssue? {
        guard interactiveControlClasses.contains(obs.elementType) else {
            return nil
        }

        let pointWidth = obs.boundingBoxPixels.width / scale
        let pointHeight = obs.boundingBoxPixels.height / scale

        if pointWidth < 44.0 || pointHeight < 44.0 {
            let wStr = String(format: "%.0f", pointWidth)
            let hStr = String(format: "%.0f", pointHeight)
            return NativeUIIssue(
                kind: .tappableTargetTooSmall,
                description: "Touch target is \(wStr)×\(hStr) pt (minimum recommended is 44×44 pt).",
                confidence: 0.95
            )
        }

        return nil
    }

    // MARK: - Rule 4: Overlapping Elements

    /// Detects unexpected spatial overlap between peer elements in the UI.
    public static func checkOverlappingElements(_ observations: [NativeUIElementObservation]) -> [(UUID, NativeUIIssue)] {
        var issues: [(UUID, NativeUIIssue)] = []
        let n = observations.count
        guard n >= 2 else { return [] }

        for i in 0..<n {
            for j in (i + 1)..<n {
                let a = observations[i]
                let b = observations[j]

                let iouVal = ObservationMerger.iou(a.boundingBox, b.boundingBox)
                guard iouVal > 0.10 else { continue }

                // Check for legitimate parent/child container containment
                if isContainerChildRelationship(a, b) {
                    continue
                }

                let descA = "Overlaps with \(b.elementType.rawValue) (IoU: \(String(format: "%.2f", iouVal)))."
                let descB = "Overlaps with \(a.elementType.rawValue) (IoU: \(String(format: "%.2f", iouVal)))."

                issues.append((a.id, NativeUIIssue(kind: .overlappingElements, description: descA, confidence: 0.80)))
                issues.append((b.id, NativeUIIssue(kind: .overlappingElements, description: descB, confidence: 0.80)))
            }
        }

        return issues
    }

    /// Determines if one element is a recognized container legitimately enclosing another element.
    private static func isContainerChildRelationship(
        _ a: NativeUIElementObservation,
        _ b: NativeUIElementObservation
    ) -> Bool {
        let aIsContainer = containerClasses.contains(a.elementType)
        let bIsContainer = containerClasses.contains(b.elementType)

        if aIsContainer && !bIsContainer {
            return isEnclosed(child: b.boundingBox, within: a.boundingBox)
        }
        if bIsContainer && !aIsContainer {
            return isEnclosed(child: a.boundingBox, within: b.boundingBox)
        }
        return false
    }

    /// True if child rectangle's area is substantially inside container (>= 75% of child area).
    private static func isEnclosed(child: NativeUIRect, within container: NativeUIRect) -> Bool {
        let x1 = max(child.x, container.x)
        let y1 = max(child.y, container.y)
        let x2 = min(child.x + child.width, container.x + container.width)
        let y2 = min(child.y + child.height, container.y + container.height)

        let interWidth = max(0.0, x2 - x1)
        let interHeight = max(0.0, y2 - y1)
        let interArea = interWidth * interHeight

        let childArea = child.width * child.height
        if childArea <= 0 { return false }

        return (interArea / childArea) >= 0.75
    }
}
