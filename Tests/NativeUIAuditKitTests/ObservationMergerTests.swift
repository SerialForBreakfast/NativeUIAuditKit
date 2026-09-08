// ObservationMergerTests.swift
// NativeUIAuditKitTests

import CoreGraphics
import Foundation
import Testing
@testable import NativeUIAuditKit

@Suite("ObservationMerger OCR Fusion Policy")
struct ObservationMergerTests {

    @Test("Assigns multiple OCR text regions to elements based on highest IoU")
    func mergerMultipleTextRegions() {
        // Element A: primaryButton at [0.1, 0.7, 0.4, 0.1]
        let elemA = NativeUIElementObservation(
            id: UUID(),
            elementType: .primaryButton,
            boundingBox: NativeUIRect(x: 0.1, y: 0.7, width: 0.4, height: 0.1),
            boundingBoxPixels: NativeUIRect(x: 100, y: 200, width: 400, height: 100),
            confidence: 0.95,
            confidenceSource: .pixelModel
        )

        // Element B: secondaryButton at [0.1, 0.5, 0.4, 0.1]
        let elemB = NativeUIElementObservation(
            id: UUID(),
            elementType: .secondaryButton,
            boundingBox: NativeUIRect(x: 0.1, y: 0.5, width: 0.4, height: 0.1),
            boundingBoxPixels: NativeUIRect(x: 100, y: 400, width: 400, height: 100),
            confidence: 0.90,
            confidenceSource: .pixelModel
        )

        // Region 1 inside A: "Submit"
        let r1 = RecognizedTextRegion(
            text: "Submit",
            boundingBox: NativeUIRect(x: 0.15, y: 0.72, width: 0.15, height: 0.05)
        )
        // Region 2 inside A: "Order"
        let r2 = RecognizedTextRegion(
            text: "Order",
            boundingBox: NativeUIRect(x: 0.32, y: 0.72, width: 0.15, height: 0.05)
        )
        // Region 3 inside B: "Cancel"
        let r3 = RecognizedTextRegion(
            text: "Cancel",
            boundingBox: NativeUIRect(x: 0.15, y: 0.52, width: 0.2, height: 0.05)
        )

        let merged = ObservationMerger.associate(
            elements: [elemA, elemB],
            ocrRegions: [r1, r2, r3]
        )

        let mergedA = merged.first { $0.id == elemA.id }
        let mergedB = merged.first { $0.id == elemB.id }

        #expect(mergedA?.visibleText == "Submit Order")
        #expect(mergedB?.visibleText == "Cancel")
    }

    @Test("Exempt classes never receive text association even with direct overlap")
    func mergerNoTextElements() {
        let toggle = NativeUIElementObservation(
            id: UUID(),
            elementType: .toggle,
            boundingBox: NativeUIRect(x: 0.6, y: 0.7, width: 0.2, height: 0.1),
            boundingBoxPixels: NativeUIRect(x: 600, y: 200, width: 200, height: 100),
            confidence: 0.92,
            confidenceSource: .pixelModel
        )
        let slider = NativeUIElementObservation(
            id: UUID(),
            elementType: .slider,
            boundingBox: NativeUIRect(x: 0.1, y: 0.3, width: 0.8, height: 0.08),
            boundingBoxPixels: NativeUIRect(x: 100, y: 600, width: 800, height: 80),
            confidence: 0.88,
            confidenceSource: .pixelModel
        )
        let image = NativeUIElementObservation(
            id: UUID(),
            elementType: .imageView,
            boundingBox: NativeUIRect(x: 0.1, y: 0.1, width: 0.3, height: 0.2),
            boundingBoxPixels: NativeUIRect(x: 100, y: 700, width: 300, height: 200),
            confidence: 0.90,
            confidenceSource: .pixelModel
        )

        // Text directly on top of toggle
        let rToggle = RecognizedTextRegion(
            text: "ON",
            boundingBox: NativeUIRect(x: 0.62, y: 0.72, width: 0.1, height: 0.05)
        )
        // Text directly on slider
        let rSlider = RecognizedTextRegion(
            text: "50%",
            boundingBox: NativeUIRect(x: 0.45, y: 0.32, width: 0.1, height: 0.04)
        )
        // Text directly on imageView
        let rImage = RecognizedTextRegion(
            text: "LOGO",
            boundingBox: NativeUIRect(x: 0.15, y: 0.15, width: 0.2, height: 0.1)
        )

        let merged = ObservationMerger.associate(
            elements: [toggle, slider, image],
            ocrRegions: [rToggle, rSlider, rImage]
        )

        for obs in merged {
            #expect(obs.visibleText == nil, "\(obs.elementType) should never receive visibleText")
        }
    }

    @Test("Reading order aggregates text top-to-bottom and left-to-right")
    func mergerReadingOrderLTR() {
        let label = NativeUIElementObservation(
            id: UUID(),
            elementType: .label,
            boundingBox: NativeUIRect(x: 0.1, y: 0.6, width: 0.4, height: 0.25),
            boundingBoxPixels: NativeUIRect(x: 100, y: 100, width: 400, height: 250),
            confidence: 0.95,
            confidenceSource: .pixelModel
        )

        // Line 1: "First Line" (higher Vision Y)
        let line1 = RecognizedTextRegion(
            text: "First Line",
            boundingBox: NativeUIRect(x: 0.15, y: 0.75, width: 0.3, height: 0.05)
        )
        // Line 2: "Second Line" (lower Vision Y)
        let line2 = RecognizedTextRegion(
            text: "Second Line",
            boundingBox: NativeUIRect(x: 0.15, y: 0.65, width: 0.3, height: 0.05)
        )

        let merged = ObservationMerger.associate(
            elements: [label],
            ocrRegions: [line2, line1], // passed out of order
            layoutDirection: .leftToRight
        )

        #expect(merged.first?.visibleText == "First Line Second Line")
    }

    @Test("Quadrant filter rejects candidate in opposite quadrant")
    func mergerQuadrantFilterRejection() {
        // Element in bottom-left quadrant: x < 0.5, y < 0.5
        let button = NativeUIElementObservation(
            id: UUID(),
            elementType: .primaryButton,
            boundingBox: NativeUIRect(x: 0.1, y: 0.1, width: 0.3, height: 0.1),
            boundingBoxPixels: NativeUIRect(x: 100, y: 800, width: 300, height: 100),
            confidence: 0.90,
            confidenceSource: .pixelModel
        )

        // Text region in top-right quadrant: x > 0.5, y > 0.5
        let distantText = RecognizedTextRegion(
            text: "Top Right Text",
            boundingBox: NativeUIRect(x: 0.6, y: 0.7, width: 0.3, height: 0.1)
        )

        let merged = ObservationMerger.associate(
            elements: [button],
            ocrRegions: [distantText]
        )

        #expect(merged.first?.visibleText == nil, "Text in different quadrant must not associate")
    }

    @Test("Sidecar conflict resolution: distance <= 2 keeps sidecar, > 2 prefers OCR")
    func mergerSidecarConflictResolution() {
        let buttonA = NativeUIElementObservation(
            id: UUID(),
            elementType: .primaryButton,
            boundingBox: NativeUIRect(x: 0.1, y: 0.7, width: 0.4, height: 0.1),
            boundingBoxPixels: NativeUIRect(x: 100, y: 200, width: 400, height: 100),
            confidence: 0.95,
            confidenceSource: .pixelModel
        )

        // Sidecar matches buttonA with text "Continue"
        let sidecarEl = NativeUISidecarElement(
            id: "btn1",
            elementType: "primaryButton",
            framework: "SwiftUI",
            boundsPixels: buttonA.boundingBoxPixels,
            boundsPoints: NativeUIRect(x: 33, y: 66, width: 133, height: 33),
            boundsVisionNormalized: buttonA.boundingBox,
            visibleText: "Continue"
        )
        let sidecar = NativeUISidecar(
            imageSHA256: "test",
            pixelWidth: 1000,
            pixelHeight: 1000,
            scale: 3.0,
            platform: "iOS",
            osVersion: "17.0",
            deviceName: "iPhone 15 Pro",
            colorScheme: "light",
            dynamicTypeSize: "large",
            locale: "en-US",
            elements: [sidecarEl]
        )

        // Case 1: OCR is "Continve" (distance = 1 <= 2) -> Sidecar "Continue" is kept
        let ocrTypo = RecognizedTextRegion(
            text: "Continve",
            boundingBox: buttonA.boundingBox
        )
        let mergedKeepSidecar = ObservationMerger.associate(
            elements: [buttonA],
            ocrRegions: [ocrTypo],
            sidecar: sidecar
        )
        #expect(mergedKeepSidecar.first?.visibleText == "Continue")

        // Case 2: Rendered OCR is "Done" (distance > 2) -> OCR "Done" is preferred
        let ocrDifferent = RecognizedTextRegion(
            text: "Done",
            boundingBox: buttonA.boundingBox
        )
        let mergedPreferOCR = ObservationMerger.associate(
            elements: [buttonA],
            ocrRegions: [ocrDifferent],
            sidecar: sidecar
        )
        #expect(mergedPreferOCR.first?.visibleText == "Done")
    }
}
