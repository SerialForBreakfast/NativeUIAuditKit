import CoreGraphics
import Foundation
import Testing
@testable import NativeUIAuditKitRuntime
import NativeUIAuditKit

@Suite("ComparativeFocusSelector")
struct ComparativeFocusSelectorTests {
    private func makeSyntheticImage(focusedBox: CGRect?, allBoxes: [CGRect]) throws -> CGImage {
        let w = 320, h = 180
        let cs = CGColorSpace(name: CGColorSpace.sRGB) ?? CGColorSpaceCreateDeviceRGB()
        let ctx = try #require(CGContext(
            data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: w * 4,
            space: cs, bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
        ))
        ctx.setFillColor(CGColor(red: 0.12, green: 0.12, blue: 0.14, alpha: 1.0))
        ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
        ctx.setFillColor(CGColor(red: 0.28, green: 0.30, blue: 0.34, alpha: 1.0))
        for b in allBoxes {
            // CoreGraphics origin is bottom-left; flip Y for top-left pixel rects
            let cgRect = CGRect(x: b.origin.x, y: Double(h) - b.origin.y - b.size.height, width: b.size.width, height: b.size.height)
            ctx.fill(cgRect)
        }
        if let fb = focusedBox {
            ctx.setStrokeColor(CGColor(red: 0.98, green: 0.98, blue: 1.0, alpha: 1.0))
            ctx.setLineWidth(4.0)
            let cgRect = CGRect(x: fb.origin.x, y: Double(h) - fb.origin.y - fb.size.height, width: fb.size.width, height: fb.size.height)
            ctx.stroke(cgRect)
        }
        return try #require(ctx.makeImage())
    }

    @Test func rawAndComparativeFeaturesIsolateBrightRingCandidate() throws {
        let boxes = [
            CGRect(x: 20, y: 40, width: 80, height: 60),
            CGRect(x: 120, y: 40, width: 80, height: 60),
            CGRect(x: 220, y: 40, width: 80, height: 60),
        ]
        let img = try makeSyntheticImage(focusedBox: boxes[1], allBoxes: boxes)
        let raw = ComparativeFocusSelector.extractRawFeatures(from: img, boxes: boxes)
        #expect(raw.count == 3)
        #expect(raw[0].count == ComparativeFocusSelector.rawFeatureCount)
        let comp = ComparativeFocusSelector.buildComparativeFeatures(raw)
        #expect(comp.count == 3)
        #expect(comp[0].count == ComparativeFocusSelector.comparativeFeatureCount)
        // Candidate 1 has strongly positive rim-minus-halo z-score relative to siblings
        let zCol = 3 * ComparativeFocusSelector.rawFeatureCount + 10
        #expect(comp[1][zCol] > comp[0][zCol])
        #expect(comp[1][zCol] > comp[2][zCol])
    }

    @Test func configurationPreservesDefaultsWhenComparativeUnset() throws {
        let legacyJSON = #"{"minimumConfidence":0.25,"platform":"tvOS"}"#.data(using: .utf8)!
        let decoded = try JSONDecoder().decode(NativeUIDetectionConfiguration.self, from: legacyJSON)
        #expect(decoded.comparativeFocusDirectory == nil)
        #expect(decoded.comparativeFocusGateThreshold == 0.28)
    }

    // Same cases as scripts/test_nested_filter666.py (TRAIN666 H3 nested filter).
    @Test func nestedFilterRemovesChevronInsideRow() {
        let row = CGRect(x: 2120, y: 467, width: 1560, height: 132)
        let chevron = CGRect(x: 3575, y: 513, width: 42, height: 40)
        #expect(ComparativeFocusSelector.nestedCandidateIndices([row, chevron]) == [1])
    }

    @Test func nestedFilterKeepsSiblingsAndPartialOverlap() {
        let boxes = [CGRect(x: 0, y: 0, width: 100, height: 50), CGRect(x: 0, y: 60, width: 100, height: 50),
                     CGRect(x: 90, y: 0, width: 40, height: 40)]  // 25 % inside the first box
        #expect(ComparativeFocusSelector.nestedCandidateIndices(boxes).isEmpty)
    }

    @Test func nestedFilterKeepsSimilarSizeDuplicate() {
        let boxes = [CGRect(x: 0, y: 0, width: 100, height: 50), CGRect(x: 2, y: 2, width: 96, height: 46)]
        #expect(ComparativeFocusSelector.nestedCandidateIndices(boxes).isEmpty)
    }

    @Test func nestedFilterThresholdsMatchPython() {
        #expect(ComparativeFocusSelector.nestedContainment == 0.9)
        #expect(ComparativeFocusSelector.nestedAreaRatio == 2.0)
        // Exactly 90 % covered and exactly 2x area: removed (both comparisons are >=).
        let outer = CGRect(x: 0, y: 0, width: 200, height: 10)
        let inner = CGRect(x: 10, y: 0, width: 100, height: 10)
        let edge = CGRect(x: 110, y: 0, width: 100, height: 10)  // 90 % inside outer
        #expect(ComparativeFocusSelector.nestedCandidateIndices([outer, inner]) == [1])
        #expect(ComparativeFocusSelector.nestedCandidateIndices([outer, edge]) == [1])
    }

    @Test func nestedFilterConfigurationIsOffByDefaultAndRoundTrips() throws {
        let legacyJSON = #"{"minimumConfidence":0.25,"platform":"tvOS"}"#.data(using: .utf8)!
        let decoded = try JSONDecoder().decode(NativeUIDetectionConfiguration.self, from: legacyJSON)
        #expect(decoded.comparativeFocusDropsNestedCandidates == false)
        #expect(NativeUIDetectionConfiguration.default.comparativeFocusDropsNestedCandidates == false)
        let on = NativeUIDetectionConfiguration(comparativeFocusDropsNestedCandidates: true)
        let back = try JSONDecoder().decode(NativeUIDetectionConfiguration.self, from: JSONEncoder().encode(on))
        #expect(back.comparativeFocusDropsNestedCandidates)
    }

    @Test func nestedRemovedDispositionRoundTripsInCoreMLReceipt() throws {
        let receipt = FocusExecutionReceipt(backend: .coreML, policy: "comparative-armb-v2-nested-v1", threshold: 0.28,
            candidates: [.init(observationID: UUID(), disposition: .scored, probability: 0.9, isFocused: true),
                         .init(observationID: UUID(), disposition: .nestedCandidateRemoved, probability: nil, isFocused: false)])
        #expect(receipt.modelScoringComplete)
        let back = try JSONDecoder().decode(FocusExecutionReceipt.self, from: JSONEncoder().encode(receipt))
        #expect(back == receipt)
    }

    /// Opt-in parity check against `scripts/nested_filter666.py` on exported real screens.
    /// Set NUIAK_NESTED_PARITY_FIXTURE to the JSON from `reports/work/TRAIN666/h3-arm-s/swift_parity_export.py`.
    /// It writes `<fixture>.swift-result.json`. Skipped when the variable is unset, so default runs stay offline and data-free.
    @Test(.enabled(if: ProcessInfo.processInfo.environment["NUIAK_NESTED_PARITY_FIXTURE"] != nil))
    func nestedFilterMatchesPythonOnExportedScreens() throws {
        struct Screen: Decodable { let detector: String; let caseId: String; let boxes: [[Double]]; let pythonRemoved: [Int] }
        struct Fixture: Decodable { let containment: Double; let areaRatio: Double; let screens: [Screen] }
        let path = try #require(ProcessInfo.processInfo.environment["NUIAK_NESTED_PARITY_FIXTURE"])
        let fixture = try JSONDecoder().decode(Fixture.self, from: Data(contentsOf: URL(fileURLWithPath: path)))
        #expect(fixture.containment == ComparativeFocusSelector.nestedContainment)
        #expect(fixture.areaRatio == ComparativeFocusSelector.nestedAreaRatio)
        var mismatches: [[String: String]] = []
        var removed = 0
        for screen in fixture.screens {
            let rects = screen.boxes.map { CGRect(x: $0[0], y: $0[1], width: $0[2], height: $0[3]) }
            let swiftRemoved = ComparativeFocusSelector.nestedCandidateIndices(rects)
            removed += swiftRemoved.count
            if swiftRemoved != Set(screen.pythonRemoved) {
                mismatches.append(["detector": screen.detector, "caseId": screen.caseId,
                                   "python": "\(screen.pythonRemoved.sorted())", "swift": "\(swiftRemoved.sorted())"])
            }
        }
        let result: [String: Any] = ["screens": fixture.screens.count, "swiftRemovedBoxes": removed,
                                     "pythonRemovedBoxes": fixture.screens.reduce(0) { $0 + $1.pythonRemoved.count },
                                     "mismatchedScreens": mismatches]
        try JSONSerialization.data(withJSONObject: result, options: [.sortedKeys, .prettyPrinted])
            .write(to: URL(fileURLWithPath: path + ".swift-result.json"))
        #expect(mismatches.isEmpty, "nested filter mismatches: \(mismatches)")
    }
}
