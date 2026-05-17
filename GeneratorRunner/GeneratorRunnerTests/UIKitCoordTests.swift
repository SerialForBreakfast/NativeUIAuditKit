// UIKitCoordTests.swift
// GeneratorRunnerTests
//
// TASK-4-1: Validates that UIView.convert(_:to:) produces accurate element frames
// for use in UIKit annotation. All assertions use ±2pt tolerance (same bar as the
// Phase 1 coordinate spike for SwiftUI).
//
// Acceptance criteria:
//   AC-1: Direct subview frame — convert(bounds, to: root) matches assigned .frame ±2pt
//   AC-2: Nested view frame — multi-level convert chain accurate ±2pt
//   AC-3: Mid-table UITableViewCell frame — accurate ±2pt (key for UIKitListViewController)
//   AC-4: clipsToBounds = true on parent does NOT alter reported child frame
//
// All tests are @MainActor because UIKit must be used on the main thread.

import XCTest
import UIKit

// MARK: - UIKitCoordTests

@MainActor
final class UIKitCoordTests: XCTestCase {

    // MARK: - Helpers

    private func makeWindow(size: CGSize) -> (UIWindow, UIViewController) {
        let bounds = CGRect(origin: .zero, size: size)
        let vc = UIViewController()
        vc.view.frame = bounds
        let window = UIWindow(frame: bounds)
        window.rootViewController = vc
        window.isHidden = false
        window.makeKeyAndVisible()
        window.setNeedsLayout()
        window.layoutIfNeeded()
        return (window, vc)
    }

    // MARK: - AC-1: Direct subview frame accuracy

    func testDirectSubviewFrameAccuracy() {
        let (window, vc) = makeWindow(size: CGSize(width: 393, height: 852))
        defer { window.isHidden = true }

        let expected = CGRect(x: 20, y: 120, width: 353, height: 44)
        let testView = UIView(frame: expected)
        vc.view.addSubview(testView)
        vc.view.setNeedsLayout()
        vc.view.layoutIfNeeded()

        let reported = testView.convert(testView.bounds, to: vc.view)

        XCTAssertEqual(reported.origin.x, expected.origin.x, accuracy: 2, "x origin")
        XCTAssertEqual(reported.origin.y, expected.origin.y, accuracy: 2, "y origin")
        XCTAssertEqual(reported.width,    expected.width,    accuracy: 2, "width")
        XCTAssertEqual(reported.height,   expected.height,   accuracy: 2, "height")
    }

    // MARK: - AC-2: Nested view frame accuracy (multi-level)

    func testNestedViewFrameAccuracy() {
        let (window, vc) = makeWindow(size: CGSize(width: 393, height: 852))
        defer { window.isHidden = true }

        // Container at (16, 200) size 361×56
        let container = UIView(frame: CGRect(x: 16, y: 200, width: 361, height: 56))
        vc.view.addSubview(container)

        // Child inside container at (16, 12) size 200×32
        let child = UIView(frame: CGRect(x: 16, y: 12, width: 200, height: 32))
        container.addSubview(child)

        // Grand-child inside child at (4, 4) size 80×24
        let grandchild = UIView(frame: CGRect(x: 4, y: 4, width: 80, height: 24))
        child.addSubview(grandchild)

        vc.view.setNeedsLayout()
        vc.view.layoutIfNeeded()

        // Expected grandchild origin in root space: x=16+16+4=36, y=200+12+4=216
        let reported = grandchild.convert(grandchild.bounds, to: vc.view)

        XCTAssertEqual(reported.origin.x, 36,  accuracy: 2, "grandchild x")
        XCTAssertEqual(reported.origin.y, 216, accuracy: 2, "grandchild y")
        XCTAssertEqual(reported.width,    80,  accuracy: 2, "grandchild width")
        XCTAssertEqual(reported.height,   24,  accuracy: 2, "grandchild height")
    }

    // MARK: - AC-3: UITableViewCell frame accuracy at mid-table position

    func testTableViewCellFrameAccuracy() {
        let (window, vc) = makeWindow(size: CGSize(width: 393, height: 852))
        defer { window.isHidden = true }

        let rowHeight: CGFloat = 56
        let tableOriginY: CGFloat = 100
        let rowCount = 8

        let helper = TableViewHelper(rowCount: rowCount, rowHeight: rowHeight)
        let tableView = UITableView(frame: CGRect(x: 0, y: tableOriginY, width: 393, height: CGFloat(rowCount) * rowHeight))
        tableView.rowHeight = rowHeight
        tableView.dataSource = helper
        tableView.delegate = helper
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "cell")
        tableView.reloadData()
        vc.view.addSubview(tableView)

        vc.view.setNeedsLayout()
        vc.view.layoutIfNeeded()

        // Verify mid-table row 4 (0-indexed) frame
        let midRow = 4
        let expectedY = tableOriginY + CGFloat(midRow) * rowHeight
        guard let cell = tableView.cellForRow(at: IndexPath(row: midRow, section: 0)) else {
            XCTFail("Cell at row \(midRow) not visible — table may not have laid out yet")
            return
        }
        let reported = cell.convert(cell.bounds, to: vc.view)

        XCTAssertEqual(reported.origin.x, 0,         accuracy: 2, "cell x")
        XCTAssertEqual(reported.origin.y, expectedY, accuracy: 2, "cell y at row \(midRow)")
        XCTAssertEqual(reported.width,    393,        accuracy: 2, "cell width")
        XCTAssertEqual(reported.height,   rowHeight,  accuracy: 2, "cell height")
    }

    // MARK: - AC-4: clipsToBounds = true does NOT alter reported frame

    func testClipsToBoundsDoesNotAffectFrame() {
        let (window, vc) = makeWindow(size: CGSize(width: 393, height: 852))
        defer { window.isHidden = true }

        // Container that clips children (parent occupies 50pt height at y=100)
        let container = UIView(frame: CGRect(x: 0, y: 100, width: 393, height: 50))
        container.clipsToBounds = true
        vc.view.addSubview(container)

        // Child whose frame extends beyond the container's bounds — visually clipped but
        // its full logical frame must still be reported by convert(_:to:).
        let child = UIView(frame: CGRect(x: 10, y: 10, width: 200, height: 80))
        container.addSubview(child)

        vc.view.setNeedsLayout()
        vc.view.layoutIfNeeded()

        // Expected in root space: x=10, y=110, w=200, h=80
        // (NOT y=100, h=40 — the clipped visual rect must not influence annotation)
        let reported = child.convert(child.bounds, to: vc.view)

        XCTAssertEqual(reported.origin.x, 10,  accuracy: 2, "child x unaffected by clipsToBounds")
        XCTAssertEqual(reported.origin.y, 110, accuracy: 2, "child y unaffected by clipsToBounds")
        XCTAssertEqual(reported.width,    200, accuracy: 2, "child width unaffected by clipsToBounds")
        XCTAssertEqual(reported.height,   80,  accuracy: 2, "child height unaffected by clipsToBounds")
    }

    // MARK: - Bonus: @2x and @3x profile canonical sizes produce correct pixel dimensions

    func testCanonicalScreenSizeAtTwoX() {
        let profile = OSVisualProfile.ios17  // 375×667pt @2x → 750×1334px
        XCTAssertEqual(profile.screenSize.width,  375, accuracy: 1)
        XCTAssertEqual(profile.screenSize.height, 667, accuracy: 1)
    }

    func testCanonicalScreenSizeAtThreeX() {
        let profile = OSVisualProfile.ios26  // 393×852pt @3x → 1179×2556px
        XCTAssertEqual(profile.screenSize.width,  393, accuracy: 1)
        XCTAssertEqual(profile.screenSize.height, 852, accuracy: 1)
    }
}

// MARK: - TableViewHelper

/// Minimal UITableViewDataSource + Delegate for UIKitCoordTests.testTableViewCellFrameAccuracy.
private final class TableViewHelper: NSObject, UITableViewDataSource, UITableViewDelegate, @unchecked Sendable {
    let rowCount: Int
    let rowHeight: CGFloat

    init(rowCount: Int, rowHeight: CGFloat) {
        self.rowCount = rowCount
        self.rowHeight = rowHeight
    }

    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int { rowCount }

    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "cell", for: indexPath)
        cell.textLabel?.text = "Row \(indexPath.row)"
        return cell
    }

    func tableView(_ tableView: UITableView, heightForRowAt indexPath: IndexPath) -> CGFloat { rowHeight }
}
