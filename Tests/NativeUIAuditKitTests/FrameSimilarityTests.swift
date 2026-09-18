import CoreGraphics
import Foundation
import Testing
@testable import NativeUIAuditKit

@Suite("FrameSimilarity")
struct FrameSimilarityTests {

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

    /// Returns a copy of `image` with a filled rectangle drawn over one corner — simulates a
    /// small localized visual change (e.g. a moved focus ring) without needing a second binary
    /// fixture asset.
    private func withLocalizedChange(_ image: CGImage) -> CGImage {
        let width = image.width
        let height = image.height
        let colorSpace = image.colorSpace ?? CGColorSpaceCreateDeviceRGB()
        let context = CGContext(
            data: nil,
            width: width,
            height: height,
            bitsPerComponent: 8,
            bytesPerRow: 0,
            space: colorSpace,
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
        )!
        context.draw(image, in: CGRect(x: 0, y: 0, width: width, height: height))
        context.setFillColor(CGColor(red: 1, green: 0, blue: 0, alpha: 1))
        let patchSide = Double(min(width, height)) * 0.12
        context.fill(CGRect(x: 0, y: 0, width: patchSide, height: patchSide))
        return context.makeImage()!
    }

    @Test("Same image compared to itself has near-zero distance")
    func sameImageIsNearZeroDistance() throws {
        let image = try loadFixture("kitchen_sink_screen")
        let distance = try FrameSimilarity().distance(image, to: image)
        #expect(distance < 0.05, "identical content should score far below any real change; got \(distance)")
    }

    @Test("Distance is symmetric")
    func distanceIsSymmetric() throws {
        let lhs = try loadFixture("kitchen_sink_screen")
        let rhs = try loadFixture("tvos_home_screen")
        let similarity = FrameSimilarity()
        let forward = try similarity.distance(lhs, to: rhs)
        let backward = try similarity.distance(rhs, to: lhs)
        #expect(abs(forward - backward) < 0.001)
    }

    @Test("Two entirely different screens score further apart than the same screen")
    func differentScreensScoreFurtherThanSameScreen() throws {
        let kitchenSink = try loadFixture("kitchen_sink_screen")
        let tvHome = try loadFixture("tvos_home_screen")
        let similarity = FrameSimilarity()

        let sameScreenDistance = try similarity.distance(kitchenSink, to: kitchenSink)
        let differentScreenDistance = try similarity.distance(kitchenSink, to: tvHome)

        #expect(differentScreenDistance > sameScreenDistance)
    }

    @Test("A localized visual change is never reported as identical (changed-focus true-negative)")
    func localizedChangeIsDetectedAsDifferent() throws {
        let original = try loadFixture("kitchen_sink_screen")
        let changed = withLocalizedChange(original)

        let distance = try FrameSimilarity().distance(original, to: changed)
        #expect(distance > 0, "a real, if small, localized change must not collapse to the identical-frame distance")
    }

    @Test("Cache reports unchanged on first sight only after seeding, then true for a repeat frame")
    func cacheTracksRepeatFrames() async throws {
        let image = try loadFixture("kitchen_sink_screen")
        let cache = FrameSimilarityCache()

        let firstSight = try await cache.isUnchanged(image, forState: "root", threshold: 0.05)
        #expect(firstSight == false, "nothing cached yet for this state — must not claim unchanged")

        let repeatFrame = try await cache.isUnchanged(image, forState: "root", threshold: 0.05)
        #expect(repeatFrame == true, "identical frame against the now-seeded cache should hit")
    }

    @Test("Cache does not false-hit on a localized change under a tight threshold")
    func cacheDoesNotFalseHitOnLocalizedChange() async throws {
        let original = try loadFixture("kitchen_sink_screen")
        let changed = withLocalizedChange(original)
        let cache = FrameSimilarityCache()

        _ = try await cache.isUnchanged(original, forState: "root", threshold: 0.001)
        let afterChange = try await cache.isUnchanged(changed, forState: "root", threshold: 0.001)
        #expect(afterChange == false, "a tight threshold must not absorb a real localized change")
    }

    @Test("Cache states are independent")
    func cacheStatesAreIndependent() async throws {
        let kitchenSink = try loadFixture("kitchen_sink_screen")
        let tvHome = try loadFixture("tvos_home_screen")
        let cache = FrameSimilarityCache()

        _ = try await cache.isUnchanged(kitchenSink, forState: "screenA", threshold: 0.05)
        // First sight of an unrelated state must not be polluted by screenA's cached frame.
        let firstSightOfOtherState = try await cache.isUnchanged(tvHome, forState: "screenB", threshold: 0.05)
        #expect(firstSightOfOtherState == false)
    }

    @Test("Invalidate forces the next call to report changed")
    func invalidateForcesChangedOnNextCall() async throws {
        let image = try loadFixture("kitchen_sink_screen")
        let cache = FrameSimilarityCache()

        _ = try await cache.isUnchanged(image, forState: "root", threshold: 0.05)
        await cache.invalidate(stateKey: "root")
        let afterInvalidate = try await cache.isUnchanged(image, forState: "root", threshold: 0.05)
        #expect(afterInvalidate == false, "invalidated state must behave like first sight even with the same image")
    }
}
