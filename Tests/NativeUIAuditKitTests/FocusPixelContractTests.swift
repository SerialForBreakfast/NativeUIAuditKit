import Foundation
import CoreGraphics
import CoreVideo
import ImageIO
import Testing
import NativeUIAuditKit
@testable import NativeUIAuditKitRuntime

@Suite("Focus input pixel contract")
struct FocusPixelContractTests {
    private func image(alpha: UInt8, premultiplied: Bool = false) throws -> CGImage {
        var bytes = [UInt8]()
        for y in 0..<3 { for x in 0..<5 {
            let colors: [UInt8] = [UInt8(30 + 20*x), UInt8(40 + 50*y), 180]
            bytes += colors.map { premultiplied ? UInt8(Int($0)*Int(alpha)/255) : $0 }
            bytes.append(alpha)
        } }
        let provider = try #require(CGDataProvider(data: Data(bytes) as CFData))
        return try #require(CGImage(width: 5, height: 3, bitsPerComponent: 8, bitsPerPixel: 32,
            bytesPerRow: 20, space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGBitmapInfo(rawValue: premultiplied ? CGImageAlphaInfo.premultipliedLast.rawValue : CGImageAlphaInfo.last.rawValue),
            provider: provider, decode: nil, shouldInterpolate: false, intent: .defaultIntent))
    }
    private func rgb(_ buffer: CVPixelBuffer) -> [UInt8] {
        CVPixelBufferLockBaseAddress(buffer, .readOnly)
        defer { CVPixelBufferUnlockBaseAddress(buffer, .readOnly) }
        let bytes = CVPixelBufferGetBaseAddress(buffer)!.assumingMemoryBound(to: UInt8.self)
        var result = [UInt8]()
        for y in 0..<CVPixelBufferGetHeight(buffer) { for x in 0..<CVPixelBufferGetWidth(buffer) {
            let i = y * CVPixelBufferGetBytesPerRow(buffer) + x*4
            result += [bytes[i+2], bytes[i+1], bytes[i]]
        } }
        return result
    }
    private func pngRGB(_ image: CGImage) throws -> [UInt8] {
        let data = NSMutableData()
        let destination = try #require(CGImageDestinationCreateWithData(data, "public.png" as CFString, 1, nil))
        CGImageDestinationAddImage(destination, image, nil)
        #expect(CGImageDestinationFinalize(destination))
        let source = try #require(CGImageSourceCreateWithData(data, nil))
        let decoded = try #require(CGImageSourceCreateImageAtIndex(source, 0, [kCGImageSourceShouldCache:false] as CFDictionary))
        let bytes = try #require(decoded.dataProvider?.data) as Data
        var result = [UInt8]()
        for y in 0..<decoded.height { for x in 0..<decoded.width {
            let i = y*decoded.bytesPerRow+x*(decoded.bitsPerPixel/8)
            result += bytes[i..<i+3]
        } }
        return result
    }
    @Test(arguments: [UInt8(0), 1, 127, 254, 255])
    func straightAndPremultipliedMatchSavedRGB(alpha: UInt8) throws {
        for premultiplied in [false, true] {
            let im = try image(alpha: alpha, premultiplied: premultiplied)
            let expected = try pngRGB(im)
            for _ in 0..<3 {
                let buffer = try #require(FocusRingClassifier.makePixelBuffer(im, contract: FocusRingClassifier.straightRGBContract))
                #expect(rgb(buffer) == expected)
            }
        }
    }
    @Test func opaqueAgreesWithLegacyAndPreservesOrientation() throws {
        let im = try image(alpha: 255)
        let old = try #require(FocusRingClassifier.makePixelBuffer(im))
        let new = try #require(FocusRingClassifier.makePixelBuffer(im, contract: FocusRingClassifier.straightRGBContract))
        #expect(rgb(old) == rgb(new))
        #expect(Array(rgb(new).prefix(3)) == [30,40,180])
        #expect(Array(rgb(new).suffix(3)) == [110,140,180])
    }
    @Test func unknownContractFailsClosed() throws {
        #expect(FocusRingClassifier.makePixelBuffer(try image(alpha: 127), contract: "future-unknown") == nil)
    }
}
