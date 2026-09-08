// AuditRulesTests.swift
// NativeUIAuditKitTests

import CoreGraphics
import Foundation
import Testing
@testable import NativeUIAuditKit

@Suite("AuditRules Automated UI Auditing")
struct AuditRulesTests {

    let sampleSize = CGSize(width: 1179, height: 2556)
    let sampleScale = 3.0

    // MARK: - Rule 1: Text Truncation

    @Test("Detects truncated text ending with ellipsis")
    func truncationWithEllipsis() {
        let obs = NativeUIElementObservation(
            id: UUID(),
            elementType: .label,
            boundingBox: NativeUIRect(x: 0.1, y: 0.5, width: 0.5, height: 0.05),
            boundingBoxPixels: NativeUIRect(x: 100, y: 500, width: 500, height: 50),
            confidence: 0.95,
            visibleText: "Please accept the terms and…",
            confidenceSource: .pixelModel
        )

        let issue = AuditRules.checkTruncation(obs)
        #expect(issue != nil)
        #expect(issue?.kind == .truncatedText)
        #expect(issue?.confidence == 0.85)
    }

    @Test("Detects truncated text ending with partial token")
    func truncationWithPartialToken() {
        let obs = NativeUIElementObservation(
            id: UUID(),
            elementType: .label,
            boundingBox: NativeUIRect(x: 0.1, y: 0.5, width: 0.5, height: 0.05),
            boundingBoxPixels: NativeUIRect(x: 100, y: 500, width: 500, height: 50),
            confidence: 0.95,
            visibleText: "Account Ba",
            confidenceSource: .pixelModel
        )

        let issue = AuditRules.checkTruncation(obs)
        #expect(issue != nil)
        #expect(issue?.kind == .truncatedText)
        #expect(issue?.confidence == 0.60)
    }

    @Test("Does not flag complete text as truncated")
    func completeTextNotTruncated() {
        let obs = NativeUIElementObservation(
            id: UUID(),
            elementType: .label,
            boundingBox: NativeUIRect(x: 0.1, y: 0.5, width: 0.5, height: 0.05),
            boundingBoxPixels: NativeUIRect(x: 100, y: 500, width: 500, height: 50),
            confidence: 0.95,
            visibleText: "Account Balance",
            confidenceSource: .pixelModel
        )

        let issue = AuditRules.checkTruncation(obs)
        #expect(issue == nil)
    }

    @Test("Exempt elements never receive truncation issue")
    func exemptElementNoTruncation() {
        let obs = NativeUIElementObservation(
            id: UUID(),
            elementType: .toggle,
            boundingBox: NativeUIRect(x: 0.1, y: 0.5, width: 0.2, height: 0.05),
            boundingBoxPixels: NativeUIRect(x: 100, y: 500, width: 200, height: 50),
            confidence: 0.95,
            visibleText: "On…",
            confidenceSource: .pixelModel
        )

        let issue = AuditRules.checkTruncation(obs)
        #expect(issue == nil)
    }

    // MARK: - Rule 2: Element Clipping

    @Test("Detects element clipping against screenshot boundary")
    func clippedElementTouchingBoundary() {
        let obs = NativeUIElementObservation(
            id: UUID(),
            elementType: .primaryButton,
            boundingBox: NativeUIRect(x: 0.0, y: 0.5, width: 0.3, height: 0.05),
            boundingBoxPixels: NativeUIRect(x: 1.0, y: 500, width: 300, height: 100), // x=1.0 is <= 2.0 tolerance
            confidence: 0.95,
            confidenceSource: .pixelModel
        )

        let issue = AuditRules.checkClipping(obs, imageSize: sampleSize)
        #expect(issue != nil)
        #expect(issue?.kind == .clippedElement)
    }

    @Test("Does not flag elements properly inset from boundary")
    func elementProperlyInsetNotClipped() {
        let obs = NativeUIElementObservation(
            id: UUID(),
            elementType: .primaryButton,
            boundingBox: NativeUIRect(x: 0.1, y: 0.5, width: 0.8, height: 0.05),
            boundingBoxPixels: NativeUIRect(x: 100, y: 500, width: 800, height: 100),
            confidence: 0.95,
            confidenceSource: .pixelModel
        )

        let issue = AuditRules.checkClipping(obs, imageSize: sampleSize)
        #expect(issue == nil)
    }

    @Test("Exempts edge-to-edge chrome from clipping rules")
    func chromeExemptFromClipping() {
        let navBar = NativeUIElementObservation(
            id: UUID(),
            elementType: .navigationBar,
            boundingBox: NativeUIRect(x: 0.0, y: 0.9, width: 1.0, height: 0.1),
            boundingBoxPixels: NativeUIRect(x: 0.0, y: 0.0, width: 1179, height: 200),
            confidence: 0.98,
            confidenceSource: .pixelModel
        )

        let issue = AuditRules.checkClipping(navBar, imageSize: sampleSize)
        #expect(issue == nil, "navigationBar naturally touches top, left, and right edges")
    }

    // MARK: - Rule 3: Tappable Target Size

    @Test("Flags undersized interactive control")
    func undersizedTouchTarget() {
        // 90px @ 3x = 30pt (< 44pt HIG minimum)
        let smallButton = NativeUIElementObservation(
            id: UUID(),
            elementType: .primaryButton,
            boundingBox: NativeUIRect(x: 0.1, y: 0.5, width: 0.08, height: 0.04),
            boundingBoxPixels: NativeUIRect(x: 100, y: 500, width: 90, height: 90),
            confidence: 0.90,
            confidenceSource: .pixelModel
        )

        let issue = AuditRules.checkTappableTargetSize(smallButton, scale: sampleScale)
        #expect(issue != nil)
        #expect(issue?.kind == .tappableTargetTooSmall)
    }

    @Test("Passes adequately sized interactive control")
    func adequatelySizedTouchTarget() {
        // 150px @ 3x = 50pt (>= 44pt HIG minimum)
        let validButton = NativeUIElementObservation(
            id: UUID(),
            elementType: .primaryButton,
            boundingBox: NativeUIRect(x: 0.1, y: 0.5, width: 0.8, height: 0.06),
            boundingBoxPixels: NativeUIRect(x: 100, y: 500, width: 900, height: 150),
            confidence: 0.95,
            confidenceSource: .pixelModel
        )

        let issue = AuditRules.checkTappableTargetSize(validButton, scale: sampleScale)
        #expect(issue == nil)
    }

    @Test("Does not flag non-interactive elements for touch target size")
    func nonInteractiveElementExemptFromTouchTarget() {
        // Small icon or text label
        let smallLabel = NativeUIElementObservation(
            id: UUID(),
            elementType: .label,
            boundingBox: NativeUIRect(x: 0.1, y: 0.5, width: 0.05, height: 0.02),
            boundingBoxPixels: NativeUIRect(x: 100, y: 500, width: 60, height: 30),
            confidence: 0.90,
            confidenceSource: .pixelModel
        )

        let issue = AuditRules.checkTappableTargetSize(smallLabel, scale: sampleScale)
        #expect(issue == nil, "Labels are not interactive controls and should not be flagged for touch target size")
    }

    // MARK: - Rule 4: Overlapping Elements

    @Test("Flags colliding peer elements symmetrically")
    func overlappingPeerElements() {
        // Two buttons directly overlapping with IoU > 0.10
        let btn1 = NativeUIElementObservation(
            id: UUID(),
            elementType: .primaryButton,
            boundingBox: NativeUIRect(x: 0.1, y: 0.5, width: 0.4, height: 0.1),
            boundingBoxPixels: NativeUIRect(x: 100, y: 500, width: 400, height: 100),
            confidence: 0.95,
            confidenceSource: .pixelModel
        )
        let btn2 = NativeUIElementObservation(
            id: UUID(),
            elementType: .secondaryButton,
            boundingBox: NativeUIRect(x: 0.2, y: 0.52, width: 0.4, height: 0.1),
            boundingBoxPixels: NativeUIRect(x: 200, y: 520, width: 400, height: 100),
            confidence: 0.90,
            confidenceSource: .pixelModel
        )

        let issues = AuditRules.checkOverlappingElements([btn1, btn2])
        #expect(issues.count == 2, "Both elements must receive an overlappingElements issue symmetrically")

        let ids = Set(issues.map { $0.0 })
        #expect(ids.contains(btn1.id))
        #expect(ids.contains(btn2.id))
    }

    @Test("Ignores legitimate container-child nesting")
    func containerChildNestingNotFlaggedAsOverlap() {
        let navBar = NativeUIElementObservation(
            id: UUID(),
            elementType: .navigationBar,
            boundingBox: NativeUIRect(x: 0.0, y: 0.85, width: 1.0, height: 0.15),
            boundingBoxPixels: NativeUIRect(x: 0, y: 0, width: 1179, height: 300),
            confidence: 0.98,
            confidenceSource: .pixelModel
        )

        // Button positioned neatly inside the navigation bar
        let navButton = NativeUIElementObservation(
            id: UUID(),
            elementType: .primaryButton,
            boundingBox: NativeUIRect(x: 0.8, y: 0.88, width: 0.15, height: 0.08),
            boundingBoxPixels: NativeUIRect(x: 900, y: 50, width: 200, height: 100),
            confidence: 0.95,
            confidenceSource: .pixelModel
        )

        let issues = AuditRules.checkOverlappingElements([navBar, navButton])
        #expect(issues.isEmpty, "Buttons inside navigationBar must not be flagged as an overlap defect")
    }
}
