import CoreGraphics
import Foundation
import Testing
@testable import NativeUIAuditKitRuntime

@Test func fallbackReplayPreservesRuntimeDecisions() throws {
    let context = try #require(CGContext(data: nil, width: 64, height: 64,
        bitsPerComponent: 8, bytesPerRow: 256, space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue))
    let image = try #require(context.makeImage())
    let observations = [NativeUIElementObservation(elementType: .primaryButton,
        boundingBox: .init(x: 0.2, y: 0.2, width: 0.5, height: 0.5),
        boundingBoxPixels: .init(x: 12, y: 12, width: 32, height: 32),
        confidence: 0.9, confidenceSource: .pixelModel)]
    let expected = NativeUIDetectionRequest.resolveTVOSFocus(in: image, observations: observations)
    let actual = FocusFallbackReplay.resolve(image: image, observations: observations)
    let encoder = JSONEncoder()
    encoder.outputFormatting = .sortedKeys
    #expect(try encoder.encode(actual) == encoder.encode(expected))
    #expect(FocusFallbackReplay.resolve(image: image, observations: []).isEmpty)
}
