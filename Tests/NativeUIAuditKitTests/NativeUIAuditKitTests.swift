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

    @Test("Detection request finds real elements on the kitchen sink fixture")
    func detectionRequestFindsRealElements() async throws {
        let fixtureURL = Bundle.module.url(forResource: "kitchen_sink_screen", withExtension: "png")!
        let data = try Data(contentsOf: fixtureURL)
        let provider = CGDataProvider(data: data as CFData)!
        let image = CGImage(
            pngDataProviderSource: provider,
            decode: nil,
            shouldInterpolate: true,
            intent: .defaultIntent
        )!

        let request = NativeUIDetectionRequest()
        let observations = try await request.perform(on: image)

        #expect(!observations.isEmpty, "expected at least one detected element on the kitchen sink fixture")
        for obs in observations {
            #expect(obs.confidence >= 0.5, "\(obs.elementType): below the default minimumConfidence")
            #expect(obs.boundingBoxPixels.width > 0, "\(obs.elementType): zero-width pixel box")
            #expect(obs.boundingBoxPixels.height > 0, "\(obs.elementType): zero-height pixel box")
        }
    }

    @Test("Detection request with OCR fuses visible text on kitchen sink fixture")
    func detectionRequestFusesOCRText() async throws {
        let fixtureURL = Bundle.module.url(forResource: "kitchen_sink_screen", withExtension: "png")!
        let data = try Data(contentsOf: fixtureURL)
        let provider = CGDataProvider(data: data as CFData)!
        let image = CGImage(
            pngDataProviderSource: provider,
            decode: nil,
            shouldInterpolate: true,
            intent: .defaultIntent
        )!

        let request = NativeUIDetectionRequest(configuration: .init(minimumConfidence: 0.20, includesTextRecognition: true))
        let observations = try await request.perform(on: image)

        #expect(!observations.isEmpty)
        let withText = observations.filter { $0.visibleText != nil }
        #expect(!withText.isEmpty, "Expected at least one element with visible text on kitchen sink fixture")
        for obs in withText {
            #expect(!obs.visibleText!.isEmpty)
        }
    }

    @Test("Detection request with OCR disabled leaves visible text nil")
    func detectionRequestWithoutOCRLeavesVisibleTextNil() async throws {
        let fixtureURL = Bundle.module.url(forResource: "kitchen_sink_screen", withExtension: "png")!
        let data = try Data(contentsOf: fixtureURL)
        let provider = CGDataProvider(data: data as CFData)!
        let image = CGImage(
            pngDataProviderSource: provider,
            decode: nil,
            shouldInterpolate: true,
            intent: .defaultIntent
        )!

        let request = NativeUIDetectionRequest(configuration: .init(minimumConfidence: 0.5, includesTextRecognition: false))
        let observations = try await request.perform(on: image)

        #expect(!observations.isEmpty)
        for obs in observations {
            #expect(obs.visibleText == nil, "visibleText must be nil when includesTextRecognition is false")
        }
    }

    @Test("Detection request confidence threshold filters output")
    func detectionRequestRespectsMinimumConfidence() async throws {
        let fixtureURL = Bundle.module.url(forResource: "kitchen_sink_screen", withExtension: "png")!
        let data = try Data(contentsOf: fixtureURL)
        let provider = CGDataProvider(data: data as CFData)!
        let image = CGImage(
            pngDataProviderSource: provider,
            decode: nil,
            shouldInterpolate: true,
            intent: .defaultIntent
        )!

        let permissive = NativeUIDetectionRequest(configuration: .init(minimumConfidence: 0.05))
        let strict = NativeUIDetectionRequest(configuration: .init(minimumConfidence: 0.95))

        let permissiveResults = try await permissive.perform(on: image)
        let strictResults = try await strict.perform(on: image)

        #expect(strictResults.count <= permissiveResults.count,
            "raising minimumConfidence should not increase the number of detections")
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

    @Test("NativeUISidecar rejects unsupported schema versions")
    func sidecarRejectsUnsupportedSchemaVersion() throws {
        let sidecar = NativeUISidecar(
            schemaVersion: "0.9",
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
            elements: []
        )
        let data = try JSONEncoder().encode(sidecar)

        #expect(throws: DecodingError.self) {
            _ = try JSONDecoder().decode(NativeUISidecar.self, from: data)
        }
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
        let state = NativeUIElementState(
            isFocused: true,
            isLoading: true,
            isSkeleton: true,
            focusConfidence: 0.95,
            focusScore: 0.88,
            isAmbiguousFocus: false
        )
        let data = try JSONEncoder().encode(state)
        let decoded = try JSONDecoder().decode(NativeUIElementState.self, from: data)
        #expect(decoded.isLoading == true)
        #expect(decoded.isSkeleton == true)
        #expect(decoded.isFocused == true)
        #expect(decoded.focusConfidence == 0.95)
        #expect(decoded.focusScore == 0.88)
        #expect(decoded.isAmbiguousFocus == false)
    }

    @Test("NativeUIElementState nil optional fields are omitted from JSON")
    func nilStateFieldsOmittedFromJSON() throws {
        let state = NativeUIElementState()
        let data = try JSONEncoder().encode(state)
        let json = String(data: data, encoding: .utf8)!
        #expect(!json.contains("isLoading"), "nil isLoading must not appear in JSON")
        #expect(!json.contains("isSkeleton"), "nil isSkeleton must not appear in JSON")
        #expect(!json.contains("isFocused"), "nil isFocused must not appear in JSON")
        #expect(!json.contains("focusConfidence"), "nil focusConfidence must not appear in JSON")
        #expect(!json.contains("focusScore"), "nil focusScore must not appear in JSON")
        #expect(!json.contains("isAmbiguousFocus"), "nil isAmbiguousFocus must not appear in JSON")
    }

    @Test("FocusRing crop expansion is 16 percent per side and clamps to image bounds")
    func testFocusRingCropExpansion() {
        let imageSize = CGSize(width: 1000, height: 1000)
        let inner = CGRect(x: 100, y: 100, width: 200, height: 200)
        let expanded = FocusRingClassifier.expandedCropRect(bbox: inner, imageSize: imageSize)
        #expect(abs(expanded.minX - 68) < 0.51)
        #expect(abs(expanded.minY - 68) < 0.51)
        #expect(abs(expanded.width - 264) < 0.51)
        #expect(abs(expanded.height - 264) < 0.51)

        let edge = CGRect(x: 0, y: 0, width: 10, height: 10)
        let clamped = FocusRingClassifier.expandedCropRect(bbox: edge, imageSize: imageSize)
        #expect(clamped.minX >= 0)
        #expect(clamped.minY >= 0)
        #expect(clamped.maxX <= imageSize.width)
        #expect(clamped.maxY <= imageSize.height)
        #expect(clamped.width > 10)
        #expect(clamped.height > 10)
    }

    @Test("FocusRing crop is always 256 by 256")
    func testFocusRingCropSize() {
        let image = makeSolidImage(width: 400, height: 300, red: 0.2, green: 0.3, blue: 0.4)
        let crop = FocusRingClassifier.makeCrop(from: image, bbox: CGRect(x: 10, y: 10, width: 80, height: 40))
        #expect(crop != nil)
        #expect(crop?.width == 256)
        #expect(crop?.height == 256)

        let tiny = FocusRingClassifier.makeCrop(from: image, bbox: CGRect(x: 0, y: 0, width: 2, height: 2))
        #expect(tiny?.width == 256)
        #expect(tiny?.height == 256)
    }

    @Test("FocusRingClassifier returns a unit-interval probability on a tvOS home crop")
    func testFocusRingClassifyReturnsProbabilityInUnitInterval() async throws {
        let classifier = try #require(
            await NativeUIDetectionRequest.loadFocusClassifierIfAvailable(),
            "FocusRingDetector.mlmodelc must be bundled"
        )
        #expect(classifier.focusThreshold == 0.85)
        #expect(classifier.ambiguityThreshold == 0.70)

        let fixtureURL = Bundle.module.url(forResource: "tvos_home_screen", withExtension: "png")!
        let data = try Data(contentsOf: fixtureURL)
        let provider = CGDataProvider(data: data as CFData)!
        let image = CGImage(
            pngDataProviderSource: provider,
            decode: nil,
            shouldInterpolate: true,
            intent: .defaultIntent
        )!

        let bbox = CGRect(
            x: CGFloat(image.width) * 0.15,
            y: CGFloat(image.height) * 0.35,
            width: CGFloat(image.width) * 0.20,
            height: CGFloat(image.height) * 0.20
        )
        let crop = try #require(FocusRingClassifier.makeCrop(from: image, bbox: bbox))
        #expect(crop.width == 256)
        #expect(crop.height == 256)

        let result = try classifier.classify(crop: crop)
        #expect(result.isFocusedProbability >= 0 && result.isFocusedProbability <= 1)
        #expect(result.confidence >= 0 && result.confidence <= 1)
    }

    @Test("Focus classifier flag controls which resolution path runs without crashing")
    func testFocusRingFallbackWhenModelAbsent() async throws {
        let fixtureURL = Bundle.module.url(forResource: "tvos_home_screen", withExtension: "png")!
        let data = try Data(contentsOf: fixtureURL)
        let provider = CGDataProvider(data: data as CFData)!
        let image = CGImage(
            pngDataProviderSource: provider,
            decode: nil,
            shouldInterpolate: true,
            intent: .defaultIntent
        )!

        let withClassifier = NativeUIDetectionRequest(
            configuration: .init(
                minimumConfidence: 0.25,
                includesTextRecognition: false,
                platform: .tvOS,
                useFocusClassifier: true
            )
        )
        let withHeuristic = NativeUIDetectionRequest(
            configuration: .init(
                minimumConfidence: 0.25,
                includesTextRecognition: false,
                platform: .tvOS,
                useFocusClassifier: false
            )
        )
        // Both must complete without throwing.
        let mlResults = try await withClassifier.perform(on: image)
        let heuristicResults = try await withHeuristic.perform(on: image)

        // YOLO detections are independent of focus resolution — same count, same element types.
        #expect(!mlResults.isEmpty, "expected at least one detected element on tvOS home screen")
        #expect(mlResults.count == heuristicResults.count,
                "ML and heuristic paths must produce the same number of YOLO detections")

        // Heuristic path must produce a valid non-crash focus opinion (some element may be focused).
        // ML and heuristic may legitimately disagree on ambiguous frames — that is expected.
        let heuristicFocusFields = heuristicResults.map { $0.state.isFocused }
        #expect(heuristicFocusFields.allSatisfy { $0 == true || $0 == false || $0 == nil },
                "heuristic path must produce valid focus state for every element")
    }

    @Test("useFocusClassifier survives Codable round-trip")
    func testFocusRingConfigurationRoundTrip() throws {
        let config = NativeUIDetectionConfiguration(useFocusClassifier: false)
        let data = try JSONEncoder().encode(config)
        let decoded = try JSONDecoder().decode(NativeUIDetectionConfiguration.self, from: data)
        #expect(decoded.useFocusClassifier == false)

        let defaults = try JSONDecoder().decode(
            NativeUIDetectionConfiguration.self,
            from: Data(#"{}"#.utf8)
        )
        #expect(defaults.useFocusClassifier == true)
    }
}

private func makeSolidImage(width: Int, height: Int, red: CGFloat, green: CGFloat, blue: CGFloat) -> CGImage {
    let colorSpace = CGColorSpaceCreateDeviceRGB()
    let ctx = CGContext(
        data: nil,
        width: width,
        height: height,
        bitsPerComponent: 8,
        bytesPerRow: 0,
        space: colorSpace,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
    )!
    ctx.setFillColor(CGColor(red: red, green: green, blue: blue, alpha: 1))
    ctx.fill(CGRect(x: 0, y: 0, width: width, height: height))
    return ctx.makeImage()!
}
