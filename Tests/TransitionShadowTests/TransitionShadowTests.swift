import Testing
import Foundation
import CoreGraphics
import ImageIO
@testable import TransitionShadowTool

@Suite struct TransitionShadowTests {
    @Test func boundedEncoderRevalidatesBytesAndPaths() throws {
        let root = URL(fileURLWithPath:#filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
            .appendingPathComponent(".build/shadow-cache-test-"+UUID().uuidString)
        try FileManager.default.createDirectory(at:root,withIntermediateDirectories:true)
        defer { try? FileManager.default.removeItem(at:root) }
        var frames: [TransitionFrame] = []
        for i in 0..<9 {
            let bytes = Data([UInt8(i*20),UInt8(255-i*20),33,255])
            let provider = try #require(CGDataProvider(data:bytes as CFData))
            let image = try #require(CGImage(width:1,height:1,bitsPerComponent:8,bitsPerPixel:32,bytesPerRow:4,
                space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:CGBitmapInfo(rawValue:CGImageAlphaInfo.last.rawValue),
                provider:provider,decode:nil,shouldInterpolate:false,intent:.defaultIntent))
            let url = root.appendingPathComponent("frame-\(i).png")
            let destination = try #require(CGImageDestinationCreateWithURL(url as CFURL,"public.png" as CFString,1,nil))
            CGImageDestinationAddImage(destination,image,nil)
            #expect(CGImageDestinationFinalize(destination))
            frames.append(TransitionFrame(path:url.path,sha256:TransitionContract.sha(try Data(contentsOf:url))))
        }
        func pair(_ index: Int) -> TransitionPair {
            TransitionPair(id:"p",actionID:"a",beforeObservationID:"b",afterObservationID:"c",before:frames[index],after:frames[index])
        }
        var encoder = TransitionEncoder()
        for i in 0..<9 {
            #expect(try encoder.pair(pair(i),root:root) == TransitionPixels.pair(pair(i),root:root))
        }
        #expect(encoder.misses == 9 && encoder.hits == 9)
        #expect(encoder.retainedFrames == 8 && encoder.retainedTensorBytes == 2_359_296)
        _ = try encoder.pair(pair(0),root:root)
        #expect(encoder.misses == 10) // Evicted oldest entry must be decoded again.
        var separate = TransitionEncoder()
        _ = try separate.pair(pair(0),root:root)
        #expect(separate.misses == 1 && separate.retainedFrames == 1)
        try Data([1,2,3]).write(to:URL(fileURLWithPath:frames[0].path))
        #expect(throws:TransitionFailure.changedBytes) { try encoder.pair(pair(0),root:root) }
        let target = URL(fileURLWithPath:frames[8].path)
        let link = root.appendingPathComponent("link.png")
        try FileManager.default.createSymbolicLink(at:link,withDestinationURL:target)
        let bad = TransitionFrame(path:link.path,sha256:frames[8].sha256)
        #expect(throws:TransitionFailure.invalidPath) {
            try encoder.pair(TransitionPair(id:"p",actionID:"a",beforeObservationID:"b",afterObservationID:"c",before:bad,after:bad),root:root)
        }
    }
    @Test func exactModelPairsOnly() {
        let newer = "focus-transition-experimental-dtm030-change-v1"
        let hash = "cc55f4e9e06605f00e511de01b09ea56707971aa753b20ac940438a50c841f43"
        #expect(TransitionContract.supports(modelID: TransitionContract.modelID, checkpoint: TransitionContract.checkpoint))
        #expect(TransitionContract.supports(modelID: newer, checkpoint: hash))
        #expect(!TransitionContract.supports(modelID: newer, checkpoint: TransitionContract.checkpoint))
        #expect(!TransitionContract.supports(modelID: "unknown", checkpoint: hash))
    }
    @Test func strictJSONRejectsDuplicateAndDeepOrInvalidInput() throws {
        #expect(throws: (any Error).self) { try StrictJSON.object(Data("{\"x\":1,\"x\":2}".utf8)) }
        #expect(throws: (any Error).self) { try StrictJSON.object(Data("{\"x\":{\"a\":1,\"a\":2}}".utf8)) }
        #expect(throws: (any Error).self) { try StrictJSON.object(Data("{\"x\":NaN}".utf8)) }
        #expect(try StrictJSON.object(Data("{\"x\": [1,true,null]}".utf8))["x"] != nil)
    }
    @Test func decisionsAndFiniteGuard() throws {
        #expect(try TransitionContract.decision(0.15) == "unchanged")
        #expect(try TransitionContract.decision(0.85) == "changed")
        #expect(try TransitionContract.decision(0.5) == "uncertain")
        #expect(throws: (any Error).self) { try TransitionContract.decision(.nan) }
        #expect(throws: (any Error).self) { try TransitionContract.decision(1.1) }
    }
    @Test func encoderIsPlanarAndLetterboxed() {
        let frame = RGBFrame(width:2,height:1,rgb:[255,0,0,0,255,0])
        let values = TransitionPixels.encode(frame)
        #expect(values.count == 3*128*192)
        #expect(values[0] == 0)
        #expect(values[16*192] == 1)
        #expect(values[128*192+16*192+191] == 1)
        #expect(values[2*128*192+16*192] == 0)
        #expect(TransitionPixels.resized(frame,width:2,height:1) == frame.rgb)
    }
}
