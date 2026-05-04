import Foundation
import Testing
import CoreGraphics
@testable import NativeUIAuditKit

@Suite("NativeUIAuditKit Scaffold")
struct NativeUIAuditKitTests {

    @Test("Package version is non-empty")
    func packageVersionNonEmpty() {
        #expect(!NativeUIAuditKit.version.isEmpty)
    }

    @Test("Detection request throws modelUnavailable before model ships")
    func detectionRequestThrowsModelUnavailable() async throws {
        let request = NativeUIDetectionRequest()
        let size = CGSize(width: 390, height: 844)
        let context = CGContext(
            data: nil,
            width: Int(size.width),
            height: Int(size.height),
            bitsPerComponent: 8,
            bytesPerRow: 0,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
        )!
        let image = context.makeImage()!
        await #expect(throws: NativeUIDetectionError.modelUnavailable) {
            _ = try await request.perform(on: image)
        }
    }

    @Test("NativeUIRect round-trips through CGRect")
    func nativeUIRectCGRectRoundTrip() {
        let rect = NativeUIRect(x: 10, y: 20, width: 100, height: 50)
        let cg = rect.cgRect
        #expect(cg.origin.x == 10)
        #expect(cg.origin.y == 20)
        #expect(cg.size.width == 100)
        #expect(cg.size.height == 50)
    }

    @Test("NativeUISidecar encodes and decodes correctly")
    func sidecarCodableRoundTrip() throws {
        let element = NativeUISidecarElement(
            id: "test_button",
            elementType: "primaryButton",
            framework: "SwiftUI",
            boundsPixels: NativeUIRect(x: 72, y: 1848, width: 1035, height: 156),
            boundsPoints: NativeUIRect(x: 24, y: 616, width: 345, height: 52),
            boundsVisionNormalized: NativeUIRect(x: 0.0611, y: 0.2159, width: 0.8779, height: 0.0610),
            visibleText: "Continue"
        )
        let sidecar = NativeUISidecar(
            imageSHA256: "abc123",
            pixelWidth: 1179,
            pixelHeight: 2556,
            scale: 3,
            platform: "iOS",
            osVersion: "26.3",
            deviceName: "iPhone 15 Pro",
            colorScheme: "light",
            dynamicTypeSize: "large",
            locale: "en_US",
            elements: [element]
        )
        let data = try JSONEncoder().encode(sidecar)
        let decoded = try JSONDecoder().decode(NativeUISidecar.self, from: data)
        #expect(decoded.imageSHA256 == "abc123")
        #expect(decoded.elements.count == 1)
        #expect(decoded.elements[0].elementType == "primaryButton")
        #expect(decoded.elements[0].visibleText == "Continue")
    }

    @Test("NativeUIElementType has stable raw values for taxonomy v0 classes")
    func elementTypeTaxonomyV0StableRawValues() {
        #expect(NativeUIElementType.primaryButton.rawValue == "primaryButton")
        #expect(NativeUIElementType.navigationBar.rawValue == "navigationBar")
        #expect(NativeUIElementType.alert.rawValue == "alert")
        #expect(NativeUIElementType.toggle.rawValue == "toggle")
        #expect(NativeUIElementType.textField.rawValue == "textField")
    }

    @Test("NativeUIElementObservation is Sendable and Codable")
    func observationCodableRoundTrip() throws {
        let obs = NativeUIElementObservation(
            elementType: .primaryButton,
            boundingBox: NativeUIRect(x: 0.06, y: 0.72, width: 0.88, height: 0.06),
            boundingBoxPixels: NativeUIRect(x: 72, y: 1848, width: 1035, height: 156),
            confidence: 0.97,
            visibleText: "Continue",
            confidenceSource: .pixelModel
        )
        let data = try JSONEncoder().encode(obs)
        let decoded = try JSONDecoder().decode(NativeUIElementObservation.self, from: data)
        #expect(decoded.elementType == NativeUIElementType.primaryButton)
        #expect(decoded.confidence == 0.97)
        #expect(decoded.visibleText == "Continue")
        #expect(decoded.confidenceSource == NativeUIConfidenceSource.pixelModel)
    }

    @Test("All 41 element type rawValues survive Codable round-trip")
    func allElementTypesRoundTrip() throws {
        #expect(NativeUIElementType.allCases.count == 41)
        for type_ in NativeUIElementType.allCases {
            let encoded = try JSONEncoder().encode(type_)
            let decoded = try JSONDecoder().decode(NativeUIElementType.self, from: encoded)
            #expect(decoded == type_, "rawValue round-trip failed for \(type_.rawValue)")
            // rawValue must not have changed from the canonical string
            let rawString = String(data: encoded, encoding: .utf8)!
                .trimmingCharacters(in: CharacterSet(charactersIn: "\""))
            #expect(rawString == type_.rawValue)
        }
    }

    @Test("NativeUIElementState optional fields round-trip when set")
    func newStateFieldsRoundTrip() throws {
        let state = NativeUIElementState(isFocused: true, isLoading: true, isSkeleton: true)
        let data = try JSONEncoder().encode(state)
        let decoded = try JSONDecoder().decode(NativeUIElementState.self, from: data)
        #expect(decoded.isLoading == true)
        #expect(decoded.isSkeleton == true)
        #expect(decoded.isFocused == true)
    }

    @Test("NativeUIElementState nil optional fields are omitted from JSON")
    func nilStateFieldsOmittedFromJSON() throws {
        let state = NativeUIElementState()
        let data = try JSONEncoder().encode(state)
        let json = String(data: data, encoding: .utf8)!
        #expect(!json.contains("isLoading"), "nil isLoading must not appear in JSON")
        #expect(!json.contains("isSkeleton"), "nil isSkeleton must not appear in JSON")
        #expect(!json.contains("isFocused"), "nil isFocused must not appear in JSON")
    }
}
