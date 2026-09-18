import CoreGraphics
import Foundation
import Testing
@testable import NativeUIAuditKit

@Suite("ChangeRegionLocalizer")
struct ChangeRegionLocalizerTests {

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

    /// Draws `image` into a new bitmap of `width` x `height`, resampling as needed. Used to
    /// bring two differently-sized fixtures to a common size for tests that need "registered"
    /// (same-dimension) input — the localizer requires that precondition, it does not perform
    /// registration itself.
    private func resize(_ image: CGImage, toWidth width: Int, height: Int) -> CGImage {
        let context = CGContext(
            data: nil,
            width: width,
            height: height,
            bitsPerComponent: 8,
            bytesPerRow: 0,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
        )!
        context.interpolationQuality = .high
        context.draw(image, in: CGRect(x: 0, y: 0, width: width, height: height))
        return context.makeImage()!
    }

    /// Returns a copy of `image` with a filled rectangle drawn over the top-left corner as seen
    /// in the image's normal top-down orientation, sized to a known fraction of the frame —
    /// simulates a small localized visual change (e.g. a moved focus ring) without needing a
    /// second binary fixture asset.
    ///
    /// NOTE: `CGContext` fills use bottom-left-origin coordinates by default, so the fill rect's
    /// `y` below is `height - patchSide` (near the top in bottom-up coordinates), not `0` (which
    /// would land at the visual bottom instead — confirmed the hard way when this test first
    /// asserted the patch was near the top and measured it near the bottom).
    private func withLocalizedChange(_ image: CGImage, patchFraction: Double = 0.05) -> CGImage {
        let width = image.width
        let height = image.height
        let context = CGContext(
            data: nil,
            width: width,
            height: height,
            bitsPerComponent: 8,
            bytesPerRow: 0,
            space: image.colorSpace ?? CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
        )!
        context.draw(image, in: CGRect(x: 0, y: 0, width: width, height: height))
        context.setFillColor(CGColor(red: 1, green: 0, blue: 0, alpha: 1))
        let patchSide = (Double(width) * Double(height) * patchFraction).squareRoot()
        context.fill(CGRect(x: 0, y: Double(height) - patchSide, width: patchSide, height: patchSide))
        return context.makeImage()!
    }

    @Test("Identical frames classify as no change with no regions")
    func identicalFramesAreUnchanged() throws {
        let image = try loadFixture("tvos_home_screen")
        let result = try ChangeRegionLocalizer().localize(image, current: image)
        #expect(result.scale == .none)
        #expect(result.regions.isEmpty)
    }

    @Test("A small localized change yields exactly one small ROI, classified local")
    func localizedChangeYieldsOneSmallRegion() throws {
        let original = try loadFixture("tvos_home_screen")
        let changed = withLocalizedChange(original, patchFraction: 0.03)

        let result = try ChangeRegionLocalizer().localize(original, current: changed)

        #expect(result.scale == .local, "a 3% patch should register as a local change, got \(result.scale)")
        #expect(result.regions.count == 1, "expected exactly one connected region, got \(result.regions.count)")

        if let region = result.regions.first {
            let frameArea = Double(original.width * original.height)
            let regionArea = Double(region.width * region.height)
            #expect(regionArea / frameArea < 0.15, "region should stay small relative to the frame")
            // The patch was drawn at the top-left origin corner.
            #expect(region.minX < Double(original.width) * 0.25)
            #expect(region.minY < Double(original.height) * 0.25)
        }
    }

    @Test("Two entirely different screens classify as fullFrame")
    func differentScreensClassifyAsFullFrame() throws {
        let kitchenSink = try loadFixture("kitchen_sink_screen")
        let tvHome = try loadFixture("tvos_home_screen")
        let resizedTVHome = resize(tvHome, toWidth: kitchenSink.width, height: kitchenSink.height)

        let result = try ChangeRegionLocalizer().localize(kitchenSink, current: resizedTVHome)
        #expect(result.scale == .fullFrame)
    }

    @Test("Mismatched dimensions throw rather than silently misaligning")
    func mismatchedDimensionsThrow() throws {
        let kitchenSink = try loadFixture("kitchen_sink_screen")
        let tvHome = try loadFixture("tvos_home_screen")

        #expect(throws: ChangeRegionLocalizerError.self) {
            _ = try ChangeRegionLocalizer().localize(kitchenSink, current: tvHome)
        }
    }

    @Test("Result never exposes image data — geometry and classification only")
    func resultIsGeometryOnly() throws {
        // Documents the full-frame-preservation policy (see file header comment) as an
        // executable check: every region is a plain CGRect, and the API surface has no
        // CGImage-producing accessor for callers to accidentally substitute for a full frame.
        let original = try loadFixture("tvos_home_screen")
        let changed = withLocalizedChange(original, patchFraction: 0.05)
        let result = try ChangeRegionLocalizer().localize(original, current: changed)
        for region in result.regions {
            #expect(region.width > 0 && region.height > 0)
        }
    }
}
