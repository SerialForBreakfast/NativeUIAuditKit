// tvOSCoordSpikeHostedTests.swift
// CoordinateSpike/tvOS
//
// Hosted XCTest verifying coordinate alignment and focus-state measurements on tvOS.

import XCTest
import UIKit
import SwiftUI
@testable import CoordSpikeRunner

final class tvOSCoordSpikeHostedTests: XCTestCase {

    // MARK: - Tolerance

    /// Phase 1 and tvOS acceptance criteria: <= 2.0 pt delta on all edges.
    private let tolerancePoints: Double = 2.0

    // MARK: - Test Methods

    /// Tests that GeometryReader reports element frames matching declared ground truth at <=2pt tolerance.
    @MainActor
    func testtvOSGeometryReaderAlignment() async throws {
        let expectation = expectation(description: "Frames captured from tvOSCoordSpikeView")
        var capturedFrames: [String: CGRect] = [:]

        let view = tvOSCoordSpikeView(isTileFocused: false) { frames in
            if frames.count >= 4 {
                capturedFrames = frames
                expectation.fulfill()
            }
        }

        let host = UIHostingController(rootView: view)
        let window = UIWindow(frame: CGRect(x: 0, y: 0, width: 1920, height: 1080))
        window.rootViewController = host
        window.makeKeyAndVisible()
        host.view.frame = window.bounds
        host.view.layoutIfNeeded()

        await fulfillment(of: [expectation], timeout: 5.0)

        // Validate button
        let buttonMeasured = try XCTUnwrap(capturedFrames["tvos_button"])
        assertRectAlignment(buttonMeasured, expected: tvOSCoordSpikeGroundTruth.button, label: "tvos_button")

        // Validate label
        let labelMeasured = try XCTUnwrap(capturedFrames["tvos_label"])
        assertRectAlignment(labelMeasured, expected: tvOSCoordSpikeGroundTruth.label, label: "tvos_label")

        // Validate app tile (unfocused)
        let tileMeasured = try XCTUnwrap(capturedFrames["tvos_app_tile"])
        assertRectAlignment(tileMeasured, expected: tvOSCoordSpikeGroundTruth.appTileUnfocused, label: "tvos_app_tile")

        // Validate settings row
        let rowMeasured = try XCTUnwrap(capturedFrames["tvos_settings_row"])
        assertRectAlignment(rowMeasured, expected: tvOSCoordSpikeGroundTruth.settingsRow, label: "tvos_settings_row")
    }

    /// Tests how focus scale effect affects GeometryReader frame vs visual bounds.
    ///
    /// Finding: GeometryReader measures layout frame (308×175 pt).
    /// When visual focus applies .scaleEffect(1.15), the visual bounding box expands around
    /// its center to (308 * 1.15) x (175 * 1.15) = 354.2 x 201.25 pt.
    @MainActor
    func testtvOSFocusStateFrameBehavior() async throws {
        let expectation = expectation(description: "Focused frames captured")
        var capturedFrames: [String: CGRect] = [:]

        let view = tvOSCoordSpikeView(isTileFocused: true) { frames in
            if frames.count >= 4 {
                capturedFrames = frames
                expectation.fulfill()
            }
        }

        let host = UIHostingController(rootView: view)
        let window = UIWindow(frame: CGRect(x: 0, y: 0, width: 1920, height: 1080))
        window.rootViewController = host
        window.makeKeyAndVisible()
        host.view.frame = window.bounds
        host.view.layoutIfNeeded()

        await fulfillment(of: [expectation], timeout: 5.0)

        let layoutFrame = try XCTUnwrap(capturedFrames["tvos_app_tile"])
        assertRectAlignment(layoutFrame, expected: tvOSCoordSpikeGroundTruth.appTileUnfocused, label: "layout_frame")

        // Calculate visual transformed frame
        let scale: CGFloat = 1.15
        let center = CGPoint(x: layoutFrame.midX, y: layoutFrame.midY)
        let visualWidth = layoutFrame.width * scale
        let visualHeight = layoutFrame.height * scale
        let visualFrame = CGRect(
            x: center.x - visualWidth / 2.0,
            y: center.y - visualHeight / 2.0,
            width: visualWidth,
            height: visualHeight
        )

        XCTAssertEqual(Double(visualFrame.width), 354.2, accuracy: 0.1)
        XCTAssertEqual(Double(visualFrame.height), 201.25, accuracy: 0.1)
    }

    // MARK: - Helper

    private func assertRectAlignment(_ measured: CGRect, expected: CGRect, label: String) {
        let dx = abs(Double(measured.minX - expected.minX))
        let dy = abs(Double(measured.minY - expected.minY))
        let dw = abs(Double(measured.width - expected.width))
        let dh = abs(Double(measured.height - expected.height))
        let maxDelta = max(dx, dy, dw, dh)

        XCTAssertLessThanOrEqual(
            maxDelta,
            tolerancePoints,
            "[\(label)] max edge delta \(maxDelta)pt exceeds tolerance \(tolerancePoints)pt. Measured: \(measured), Expected: \(expected)"
        )
    }
}
