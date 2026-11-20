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
}
