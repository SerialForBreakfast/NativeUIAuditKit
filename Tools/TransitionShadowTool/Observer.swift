import Foundation
import CoreML
import ImageIO
import CoreGraphics
import CryptoKit

enum TransitionFailure: String, Error, Sendable {
    case invalidRequest, duplicateKey, invalidPath, changedBytes, unsupportedImage
    case viewportChanged, modelContract, nonfiniteOutput, outputCollision
}

enum TransitionContract {
    static let modelID = "focus-transition-experimental-dtm025-change-v1"
    static let checkpoint = "28f10dc5ac2c6a0fb324cabeb778b2acad2539c97f7f9cc48a20c8ff534a9409"
    static let encoding = "paired-rgb-letterbox192x128-pillow-bilinear-v1"
    static func supports(modelID: String, checkpoint: String) -> Bool {
        let allowed = [Self.modelID: Self.checkpoint,
            "focus-transition-experimental-dtm030-change-v1": "cc55f4e9e06605f00e511de01b09ea56707971aa753b20ac940438a50c841f43"]
        return allowed[modelID] == checkpoint
    }
    static func sha(_ data: Data) -> String {
        SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
    }
    static func decision(_ p: Double) throws -> String {
        guard p.isFinite, (0...1).contains(p) else { throw TransitionFailure.nonfiniteOutput }
        return p >= 0.85 ? "changed" : p <= 0.15 ? "unchanged" : "uncertain"
    }
    static func checkedURL(_ path: String, root: URL) throws -> URL {
        let url = URL(fileURLWithPath: path).standardizedFileURL
        guard root.path != "/", url.path.hasPrefix(root.path + "/"),
              root.resolvingSymlinksInPath() == root, url.resolvingSymlinksInPath() == url
        else { throw TransitionFailure.invalidPath }
        return url
    }
    static func tree(_ root: URL) throws -> String {
        guard let enumerator = FileManager.default.enumerator(at: root,
            includingPropertiesForKeys: [.isRegularFileKey, .isSymbolicLinkKey]) else { throw TransitionFailure.modelContract }
        var files: [URL] = []
        for case let url as URL in enumerator {
            let values = try url.resourceValues(forKeys: [.isRegularFileKey, .isSymbolicLinkKey])
            guard values.isSymbolicLink != true else { throw TransitionFailure.invalidPath }
            if values.isRegularFile == true { files.append(url) }
        }
        guard !files.isEmpty else { throw TransitionFailure.modelContract }
        var hash = SHA256()
        for url in files.sorted(by: { $0.path < $1.path }) {
            hash.update(data: Data(url.path.dropFirst(root.path.count + 1).utf8)); hash.update(data: Data([0]))
            hash.update(data: try Data(contentsOf: url))
        }
        return hash.finalize().map { String(format: "%02x", $0) }.joined()
    }
}

// JSONDecoder otherwise silently accepts duplicate keys. Scan containers before decoding.
struct StrictJSON: Sendable {
    var bytes: [UInt8]; var index = 0
    mutating func space() { while index < bytes.count && [9,10,13,32].contains(bytes[index]) { index += 1 } }
    mutating func string() throws -> String {
        let start = index; guard index < bytes.count, bytes[index] == 34 else { throw TransitionFailure.invalidRequest }
        index += 1
        while index < bytes.count {
            if bytes[index] == 92 { index += 2; continue }
            if bytes[index] == 34 {
                index += 1
                return try JSONDecoder().decode(String.self, from: Data(bytes[start..<index]))
            }
            index += 1
        }
        throw TransitionFailure.invalidRequest
    }
    mutating func value(_ depth: Int = 0) throws {
        space(); guard index < bytes.count, depth < 32 else { throw TransitionFailure.invalidRequest }
        if bytes[index] == 34 { _ = try string(); return }
        if bytes[index] == 123 || bytes[index] == 91 {
            let object = bytes[index] == 123; let end: UInt8 = object ? 125 : 93
            index += 1; space(); var keys = Set<String>()
            if index < bytes.count, bytes[index] == end { index += 1; return }
            while index < bytes.count {
                if object {
                    space(); let key = try string()
                    guard keys.insert(key).inserted else { throw TransitionFailure.duplicateKey }
                    space(); guard index < bytes.count, bytes[index] == 58 else { throw TransitionFailure.invalidRequest }; index += 1
                }
                try value(depth + 1); space()
                guard index < bytes.count else { throw TransitionFailure.invalidRequest }
                if bytes[index] == end { index += 1; return }
                guard bytes[index] == 44 else { throw TransitionFailure.invalidRequest }; index += 1
            }
            throw TransitionFailure.invalidRequest
        }
        let start = index
        while index < bytes.count && ![9,10,13,32,44,93,125].contains(bytes[index]) { index += 1 }
        guard index > start else { throw TransitionFailure.invalidRequest }
    }
    static func object(_ data: Data) throws -> [String: Any] {
        guard data.count <= 1_048_576 else { throw TransitionFailure.invalidRequest }
        var scan = StrictJSON(bytes: Array(data)); try scan.value(); scan.space()
        guard scan.index == scan.bytes.count, let result = try JSONSerialization.jsonObject(with: data) as? [String: Any]
        else { throw TransitionFailure.invalidRequest }
        return result
    }
}

struct TransitionFrame: Codable, Sendable { let path: String; let sha256: String }
struct TransitionPair: Codable, Sendable {
    let id: String; let actionID: String; let beforeObservationID: String; let afterObservationID: String
    let before: TransitionFrame; let after: TransitionFrame
}
struct RGBFrame: Sendable { let width: Int; let height: Int; let rgb: [UInt8] }

enum TransitionPixels {
    static func checkedBytes(_ frame: TransitionFrame, root: URL) throws -> Data {
        let url = try TransitionContract.checkedURL(frame.path, root: root)
        let length = try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0
        guard length > 0 && length <= 32 * 1024 * 1024 else { throw TransitionFailure.unsupportedImage }
        let bytes = try Data(contentsOf: url)
        guard bytes.count <= 32 * 1024 * 1024 else { throw TransitionFailure.unsupportedImage }
        guard TransitionContract.sha(bytes) == frame.sha256 else { throw TransitionFailure.changedBytes }
        return bytes
    }
    static func load(_ frame: TransitionFrame, root: URL) throws -> RGBFrame {
        try decode(checkedBytes(frame, root: root))
    }
    static func decode(_ bytes: Data) throws -> RGBFrame {
        guard bytes.starts(with: [137,80,78,71,13,10,26,10]),
              let source = CGImageSourceCreateWithData(bytes as CFData, nil), CGImageSourceGetCount(source) == 1,
              let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [CFString: Any],
              let w = properties[kCGImagePropertyPixelWidth] as? Int,
              let h = properties[kCGImagePropertyPixelHeight] as? Int,
              w > 0, h > 0, w <= 20_000_000 / h,
              (properties[kCGImagePropertyOrientation] as? Int ?? 1) == 1,
              let image = CGImageSourceCreateImageAtIndex(source, 0, [kCGImageSourceShouldCache: true] as CFDictionary),
              image.bitsPerComponent == 8, image.colorSpace?.model == .rgb,
              [24,32].contains(image.bitsPerPixel),
              let data = image.dataProvider?.data else { throw TransitionFailure.unsupportedImage }
        let raw = Array(data as Data); let stride = image.bitsPerPixel / 8
        let alpha = image.alphaInfo
        let little = image.bitmapInfo.intersection(.byteOrderMask) == .byteOrder32Little
        guard !little, stride == 3 || [.last,.premultipliedLast,.noneSkipLast].contains(alpha),
              raw.count >= image.bytesPerRow * h else { throw TransitionFailure.unsupportedImage }
        if stride == 3 && image.bytesPerRow == w*3 {
            return RGBFrame(width:w,height:h,rgb:Array(raw.prefix(w*h*3)))
        }
        var rgb = [UInt8](repeating: 0, count: w*h*3)
        for y in 0..<h { for x in 0..<w {
            let i = y*image.bytesPerRow+x*stride; let j = (y*w+x)*3
            if stride == 4 && alpha != .noneSkipLast && raw[i+3] != 255 { throw TransitionFailure.unsupportedImage }
            rgb[j] = raw[i]; rgb[j+1] = raw[i+1]; rgb[j+2] = raw[i+2]
        }}
        return RGBFrame(width: w, height: h, rgb: rgb)
    }
    // Separable antialiased bilinear with Pillow's 22bit coefficient quantization.
    static func coefficients(_ source: Int, _ target: Int) -> [(Int,[Int])] {
        let scale = Double(source)/Double(target), filter = max(1,Double(source)/Double(target))
        return (0..<target).map { output in
            let center = (Double(output)+0.5)*scale
            let start = max(0,Int(center-filter+0.5)), end = min(source,Int(center+filter+0.5))
            let weights = (start..<end).map { max(0,1-abs((Double($0)-center+0.5)/filter)) }
            let total = weights.reduce(0,+)
            return (start,weights.map { Int(($0/total)*Double(1<<22)+0.5) })
        }
    }
    static func resized(_ frame: RGBFrame, width: Int, height: Int) -> [UInt8] {
        var horizontal = frame.rgb
        if width != frame.width {
            let table = coefficients(frame.width,width)
            horizontal = [UInt8](repeating:0,count:width*frame.height*3)
            for y in 0..<frame.height { for x in 0..<width {
                let (start,weights) = table[x]; var r = 1<<21, g = 1<<21, b = 1<<21
                for (i,weight) in weights.enumerated() {
                    let j = (y*frame.width+start+i)*3
                    r += Int(frame.rgb[j])*weight; g += Int(frame.rgb[j+1])*weight; b += Int(frame.rgb[j+2])*weight
                }
                let j = (y*width+x)*3
                horizontal[j] = UInt8(clamping:r>>22); horizontal[j+1] = UInt8(clamping:g>>22); horizontal[j+2] = UInt8(clamping:b>>22)
            }}
        }
        if height == frame.height { return horizontal }
        let table = coefficients(frame.height,height)
        var output = [UInt8](repeating:0,count:width*height*3)
        for y in 0..<height { for x in 0..<width {
            let (start,weights) = table[y]; var r = 1<<21, g = 1<<21, b = 1<<21
            for (i,weight) in weights.enumerated() {
                let j = ((start+i)*width+x)*3
                r += Int(horizontal[j])*weight; g += Int(horizontal[j+1])*weight; b += Int(horizontal[j+2])*weight
            }
            let j = (y*width+x)*3
            output[j] = UInt8(clamping:r>>22); output[j+1] = UInt8(clamping:g>>22); output[j+2] = UInt8(clamping:b>>22)
        }}
        return output
    }
    static func encode(_ frame: RGBFrame) -> [Float] {
        let scale = min(192/Double(frame.width),128/Double(frame.height))
        let w = max(1,Int((Double(frame.width)*scale).rounded(.toNearestOrEven)))
        let h = max(1,Int((Double(frame.height)*scale).rounded(.toNearestOrEven)))
        let left = (192-w)/2, top = (128-h)/2; let rgb = resized(frame,width:w,height:h)
        var tensor = [Float](repeating:0,count:3*192*128)
        for y in 0..<h { for x in 0..<w { for c in 0..<3 {
            tensor[c*192*128+(top+y)*192+left+x] = Float(rgb[(y*w+x)*3+c])/255
        }}}
        return tensor
    }
    static func pair(_ pair: TransitionPair, root: URL) throws -> [Float] {
        let before = try load(pair.before,root:root)
        let after = pair.before == pair.after ? before : try load(pair.after,root:root)
        guard before.width == after.width && before.height == after.height else { throw TransitionFailure.viewportChanged }
        return encode(before)+encode(after)
    }
}
extension TransitionFrame: Equatable {}

// Own one encoder per bounded request/worker. No global state or full-frame retention.
struct TransitionEncoder: Sendable {
    private struct Entry: Sendable {
        let sha256: String; let width: Int; let height: Int; let values: [Float]
    }
    private var entries: [Entry] = []
    private(set) var hits = 0
    private(set) var misses = 0
    var retainedFrames: Int { entries.count }
    var retainedTensorBytes: Int { entries.reduce(0) { $0 + $1.values.count*MemoryLayout<Float>.size } }
    private mutating func frame(_ source: TransitionFrame, root: URL) throws -> Entry {
        // A filename, timestamp or previous hash is never sufficient for a hit.
        let bytes = try TransitionPixels.checkedBytes(source,root:root)
        if let index = entries.firstIndex(where: { $0.sha256 == source.sha256 }) {
            let entry = entries.remove(at:index); entries.append(entry); hits += 1; return entry
        }
        let image = try TransitionPixels.decode(bytes)
        let entry = Entry(sha256:source.sha256,width:image.width,height:image.height,values:TransitionPixels.encode(image))
        if entries.count == 8 { entries.removeFirst() }
        entries.append(entry); misses += 1; return entry
    }
    mutating func pair(_ pair: TransitionPair, root: URL) throws -> [Float] {
        let before = try frame(pair.before,root:root)
        let after = try frame(pair.after,root:root)
        guard before.width == after.width && before.height == after.height else { throw TransitionFailure.viewportChanged }
        return before.values + after.values
    }
}

actor TransitionChangeObserver {
    private let model: MLModel
    private let modelURL: URL
    private let manifestURL: URL
    private let manifestSHA256: String
    let modelTreeSHA256: String
    let modelID: String
    init(bundle: URL, manifestSHA256: String) throws {
        manifestURL = try TransitionContract.checkedURL(bundle.appendingPathComponent("contract.json").path, root: bundle)
        self.manifestSHA256 = manifestSHA256
        guard (try manifestURL.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? Int.max) <= 1_048_576
        else { throw TransitionFailure.modelContract }
        let manifest = try Data(contentsOf: manifestURL)
        guard TransitionContract.sha(manifest) == manifestSHA256 else { throw TransitionFailure.modelContract }
        let contract = try StrictJSON.object(manifest)
        guard Set(contract.keys) == ["schemaVersion", "modelID", "checkpointSHA256", "inputEncoding", "compiledTreeSHA256"],
              contract["schemaVersion"] as? Int == 1,
              let declaredID = contract["modelID"] as? String,
              let declaredCheckpoint = contract["checkpointSHA256"] as? String,
              TransitionContract.supports(modelID: declaredID, checkpoint: declaredCheckpoint),
              contract["inputEncoding"] as? String == TransitionContract.encoding,
              let expected = contract["compiledTreeSHA256"] as? String else { throw TransitionFailure.modelContract }
        let url = try TransitionContract.checkedURL(bundle.appendingPathComponent("FocusTransitionChange.mlmodelc").path,root:bundle)
        modelID = declaredID
        modelURL = url
        modelTreeSHA256 = try TransitionContract.tree(url)
        guard modelTreeSHA256 == expected else { throw TransitionFailure.modelContract }
        let configuration = MLModelConfiguration(); configuration.computeUnits = .cpuOnly
        model = try MLModel(contentsOf:url,configuration:configuration)
        let metadata = model.modelDescription.metadata[.creatorDefinedKey] as? [String:String] ?? [:]
        guard metadata["modelID"] == declaredID,
              metadata["checkpointSHA256"] == declaredCheckpoint,
              metadata["inputEncoding"] == TransitionContract.encoding,
              metadata["releaseEligible"] == "false",
              metadata["backend"] == "cpuOnly",
              model.modelDescription.inputDescriptionsByName["pair"]?.multiArrayConstraint?.shape.map(\.intValue) == [1,6,128,192],
              model.modelDescription.outputDescriptionsByName["focus_change_probability"] != nil
        else { throw TransitionFailure.modelContract }
        guard try TransitionContract.tree(url) == modelTreeSHA256 else { throw TransitionFailure.changedBytes }
    }
    func verifyUnchanged() throws {
        guard try TransitionContract.tree(modelURL) == modelTreeSHA256,
              TransitionContract.sha(try Data(contentsOf: manifestURL)) == manifestSHA256
        else { throw TransitionFailure.changedBytes }
    }
    func predict(_ values: [Float]) throws -> Double {
        guard values.count == 6*128*192, values.allSatisfy({ $0.isFinite && (0...1).contains($0) })
        else { throw TransitionFailure.invalidRequest }
        let input = try MLMultiArray(shape:[1,6,128,192],dataType:.float32)
        let pointer = input.dataPointer.bindMemory(to:Float.self,capacity:values.count)
        for i in values.indices { pointer[i] = values[i] }
        let output = try model.prediction(from:MLDictionaryFeatureProvider(dictionary:["pair":input]))
        guard let probability = output.featureValue(for:"focus_change_probability")?.multiArrayValue,
              probability.count == 1 else { throw TransitionFailure.nonfiniteOutput }
        let p = probability[0].doubleValue; _ = try TransitionContract.decision(p); return p
    }
}
