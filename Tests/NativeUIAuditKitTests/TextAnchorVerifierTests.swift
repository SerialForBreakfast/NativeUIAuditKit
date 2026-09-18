import CoreGraphics
import Foundation
import Testing
@testable import NativeUIAuditKit

@Suite("TextAnchorVerifier")
struct TextAnchorVerifierTests {

    private func loadFixture(_ name: String) throws -> CGImage {
        let fixtureURL = Bundle.module.url(forResource: name, withExtension: "png")!
        let data = try Data(contentsOf: fixtureURL)
        let provider = CGDataProvider(data: data as CFData)!
        return CGImage(
            pngDataProviderSource: provider,
            decode: nil,
            shouldInterpolate: true,
            intent: .defaultIntent
        )!
    }

    private func region(_ text: String, x: Double = 0.1, y: Double = 0.1, width: Double = 0.3, height: Double = 0.05) -> RecognizedTextRegion {
        RecognizedTextRegion(text: text, boundingBox: NativeUIRect(x: x, y: y, width: width, height: height))
    }

    // MARK: - Pure evaluation logic (no live OCR)

    @Test("All required anchors present, no forbidden anchors -> verified")
    func allRequiredPresentIsVerified() {
        let regions = [region("General"), region("About"), region("Appearance")]
        let requirements = TextAnchorRequirements(required: ["General", "About"])
        let result = TextAnchorVerifier.evaluate(requirements, against: regions)

        #expect(result.status == .verified)
        #expect(result.matchedRequired.count == 2)
        #expect(result.missingRequired.isEmpty)
    }

    @Test("A missing required anchor -> unverified, not a best guess")
    func missingRequiredIsUnverified() {
        let regions = [region("General"), region("Appearance")]
        let requirements = TextAnchorRequirements(required: ["General", "Network"])
        let result = TextAnchorVerifier.evaluate(requirements, against: regions)

        #expect(result.status == .unverified)
        #expect(result.missingRequired == ["Network"])
    }

    @Test("A forbidden anchor present -> unverified even if all required anchors matched")
    func forbiddenAnchorForcesUnverified() {
        let regions = [region("General"), region("Reset Video Settings")]
        let requirements = TextAnchorRequirements(required: ["General"], forbidden: ["Reset"])
        let result = TextAnchorVerifier.evaluate(requirements, against: regions)

        #expect(result.status == .unverified)
        #expect(result.matchedForbidden.count == 1)
        #expect(result.missingRequired.isEmpty, "required anchors were satisfied — the forbidden match is what flips this")
    }

    @Test("No required anchors supplied -> ambiguous, not a silent pass")
    func noRequiredAnchorsIsAmbiguous() {
        let regions = [region("General")]
        let requirements = TextAnchorRequirements(optional: ["General"])
        let result = TextAnchorVerifier.evaluate(requirements, against: regions)

        #expect(result.status == .ambiguous)
    }

    @Test("No OCR text found at all -> ambiguous, not unverified")
    func noTextFoundIsAmbiguous() {
        let requirements = TextAnchorRequirements(required: ["General"])
        let result = TextAnchorVerifier.evaluate(requirements, against: [])

        #expect(result.status == .ambiguous, "a blank/loading screen is genuinely unknown, not a confident negative")
        #expect(result.missingRequired == ["General"])
    }

    @Test("Matching is case-insensitive substring containment")
    func matchingIsCaseInsensitiveSubstring() {
        let regions = [region("› General Settings")]
        let requirements = TextAnchorRequirements(required: ["general"])
        let result = TextAnchorVerifier.evaluate(requirements, against: regions)

        #expect(result.status == .verified)
    }

    @Test("Optional anchors are reported but never affect status")
    func optionalAnchorsDoNotAffectStatus() {
        let regionsWithOptional = [region("General")]
        let requirementsWithOptional = TextAnchorRequirements(required: ["General"], optional: ["Appearance"])
        let withOptionalMissing = TextAnchorVerifier.evaluate(requirementsWithOptional, against: regionsWithOptional)
        #expect(withOptionalMissing.status == .verified)
        #expect(withOptionalMissing.matchedOptional.isEmpty)
    }

    // MARK: - Coordinate conversion

    @Test("Pixel ROI to Vision-normalized conversion matches the package's existing y-flip convention")
    func pixelRectToVisionNormalizedConversion() {
        // A box in the top-left quarter of a 1000x1000 image: pixel (0,0)-(250,250).
        let pixelRect = CGRect(x: 0, y: 0, width: 250, height: 250)
        let vision = TextAnchorVerifier.pixelRectToVisionNormalized(pixelRect, imageWidth: 1000, imageHeight: 1000)

        // Top-left in pixel space is near the Vision-normalized top (y close to 1), matching
        // NativeUIDetectionRequest.toObservation's `visionRect` formula (x unaffected, y flips).
        #expect(abs(vision.origin.x - 0.0) < 0.001)
        #expect(abs(vision.origin.y - 0.75) < 0.001)
        #expect(abs(vision.width - 0.25) < 0.001)
        #expect(abs(vision.height - 0.25) < 0.001)
    }

    // MARK: - Integration: real OCR against the bundled fixture

    @Test("Real OCR on the kitchen-sink fixture verifies against its own discovered text")
    func realOCRVerifiesAgainstOwnDiscoveredText() async throws {
        let image = try loadFixture("kitchen_sink_screen")
        let discovered = try await NativeUIDetectionRequest.recognizeText(in: image)
        #expect(!discovered.isEmpty, "fixture should contain some OCR-recognizable text")

        guard let anchorText = discovered.first(where: { $0.text.count >= 3 })?.text else {
            Issue.record("no usable anchor text discovered on the fixture")
            return
        }

        let verifier = TextAnchorVerifier()
        let verified = try await verifier.verify(
            TextAnchorRequirements(required: [anchorText]),
            in: image
        )
        #expect(verified.status == .verified, "the fixture's own text must verify against itself")

        let mismatched = try await verifier.verify(
            TextAnchorRequirements(required: ["ZZZ_NOT_PRESENT_ON_THIS_SCREEN_ZZZ"]),
            in: image
        )
        #expect(mismatched.status == .unverified, "a clearly absent anchor must not be waved through as a best guess")
    }

    @Test("ROI-scoped OCR still finds an anchor known to be inside the region")
    func roiScopedOCRFindsAnchorInsideRegion() async throws {
        let image = try loadFixture("kitchen_sink_screen")
        let fullFrameRegions = try await NativeUIDetectionRequest.recognizeText(in: image)
        guard let target = fullFrameRegions.first(where: { $0.text.count >= 3 }) else {
            Issue.record("no usable anchor text discovered on the fixture")
            return
        }

        // target.boundingBox is Vision-normalized (bottom-left origin); convert to this
        // package's top-left pixel convention and pad generously so the ROI still contains the
        // whole text line despite any OCR box-tightness variance.
        let width = Double(image.width)
        let height = Double(image.height)
        let visionBox = target.boundingBox
        let pixelX = visionBox.x * width
        let pixelY = (1.0 - visionBox.y - visionBox.height) * height
        let pixelWidth = visionBox.width * width
        let pixelHeight = visionBox.height * height
        let pad = 20.0
        let roi = CGRect(
            x: max(0, pixelX - pad), y: max(0, pixelY - pad),
            width: pixelWidth + pad * 2, height: pixelHeight + pad * 2
        )

        let verifier = TextAnchorVerifier()
        let result = try await verifier.verify(
            TextAnchorRequirements(required: [target.text]),
            in: image,
            regionOfInterest: roi
        )
        #expect(result.status == .verified, "the anchor's own region, padded, must still find it when OCR is scoped to it")
    }
}
