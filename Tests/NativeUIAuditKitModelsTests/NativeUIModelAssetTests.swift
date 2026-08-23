// NativeUIModelAssetTests.swift
// NativeUIAuditKitModelsTests
//
// Smoke tests confirming the bundled model resource actually resolves and loads for any
// consumer of this package — this is the guarantee ViewLens and other consumers depend on.

import CoreML
import XCTest
@testable import NativeUIAuditKitModels

final class NativeUIModelAssetTests: XCTestCase {

    func testDefaultModelURLResolves() throws {
        let url = NativeUIModelAsset.defaultModelURL
        XCTAssertTrue(FileManager.default.fileExists(atPath: url.path),
            "Bundled model resource not found at \(url.path)")
    }

    func testModelLoads() async throws {
        let model = try await NativeUIModelAsset.loadModel()
        XCTAssertNotNil(model)
    }

    func testMetadataMatchesModel() {
        let metadata = NativeUIModelAsset.metadata
        XCTAssertEqual(metadata.classLabels.count, 5)
        XCTAssertEqual(metadata.inputWidth, 640)
        XCTAssertEqual(metadata.inputHeight, 640)
        XCTAssertEqual(metadata.classLabels,
            ["alert", "navigationBar", "primaryButton", "textField", "toggle"])
    }
}
