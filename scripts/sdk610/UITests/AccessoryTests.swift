import XCTest

final class AccessoryTests: XCTestCase {
    func testAccessoryAndDismissal() {
        continueAfterFailure = false
        let app = XCUIApplication()
        app.launch()
        let accessory = app.buttons["info-0"]
        let row = app.buttons["row-action-0"]
        let sheetTitle = app.staticTexts["Episode information"]
        XCTAssertTrue(accessory.waitForExistence(timeout: 8))
        XCTAssertTrue(row.isHittable)
        row.tap()
        XCTAssertFalse(sheetTitle.exists)
        for _ in 0..<2 {
            accessory.tap()
            XCTAssertTrue(sheetTitle.waitForExistence(timeout: 5))
            let start = sheetTitle.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.2))
            let end = app.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.97))
            start.press(forDuration: 0.12, thenDragTo: end, withVelocity: .fast, thenHoldForDuration: 0.1)
            XCTAssertTrue(sheetTitle.waitForNonExistence(timeout: 5))
            XCTAssertTrue(accessory.isHittable)
            XCTAssertTrue(row.isHittable)
        }
    }
}
