import Foundation
import CoreGraphics
import ImageIO
import CryptoKit
import NativeUIAuditKit
import Darwin

// Offline measurements only: no labels, policy, model or output files.
struct Frame: Decodable, Sendable { let path: String; let sha256: String }
struct Pair: Decodable, Sendable { let id: String; let previous: Frame; let current: Frame }
struct Request: Decodable, Sendable {
    let version: Int; let root: String; let noiseThreshold: UInt8; let pairs: [Pair]
}
struct Measurement: Encodable, Sendable {
    let id: String; let distance: Float; let regions: [[Double]]; let milliseconds: Double
}
struct Reply: Encodable, Sendable {
    let version: Int; let host: String; let results: [Measurement]
}
enum Invalid: Error { case request, path, image, changedBytes }

func load(_ frame: Frame, root: URL) throws -> CGImage {
    let url = URL(fileURLWithPath: frame.path).standardizedFileURL
    guard url.resolvingSymlinksInPath() == url, url.path.hasPrefix(root.path + "/") else { throw Invalid.path }
    let size = try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0
    guard size > 0, size <= 32 * 1024 * 1024 else { throw Invalid.image }
    let data = try Data(contentsOf: url)
    guard SHA256.hash(data: data).map({ String(format: "%02x", $0) }).joined() == frame.sha256 else { throw Invalid.changedBytes }
    guard let source = CGImageSourceCreateWithData(data as CFData, nil),
          CGImageSourceGetType(source) as String? == "public.png",
          let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any],
          let w = properties[kCGImagePropertyPixelWidth as String] as? Int,
          let h = properties[kCGImagePropertyPixelHeight as String] as? Int,
          w > 0, h > 0, w <= 16_000_000 / h,
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else { throw Invalid.image }
    return image
}

func run(_ output: FileHandle) throws {
    var bytes = Data()
    while let chunk = try FileHandle.standardInput.read(upToCount: 65536), !chunk.isEmpty {
        bytes.append(chunk)
        guard bytes.count <= 8_388_608 else { throw Invalid.request }
    }
    let request = try JSONDecoder().decode(Request.self, from: bytes)
    let root = URL(fileURLWithPath: request.root).standardizedFileURL
    guard root.resolvingSymlinksInPath() == root, request.version == 1,
          !request.pairs.isEmpty, request.pairs.count <= 2048,
          Set(request.pairs.map(\.id)).count == request.pairs.count else { throw Invalid.request }
    let localizer = ChangeRegionLocalizer(noiseThreshold: request.noiseThreshold)
    let similarity = FrameSimilarity()
    var results: [Measurement] = []
    for pair in request.pairs {
        let result = try autoreleasepool {
            let start = ProcessInfo.processInfo.systemUptime
            let a = try load(pair.previous, root: root), b = try load(pair.current, root: root)
            let change = try localizer.localize(a, current: b)
            let distance = try similarity.distance(a, to: b)
            guard distance.isFinite else { throw Invalid.image }
            // Bound noisy component output conservatively; never drop small changes.
            let regions = change.regions.count <= 128 ? change.regions :
                [CGRect(x: 0, y: 0, width: a.width, height: a.height)]
            return Measurement(id: pair.id, distance: distance,
                regions: regions.map { [Double($0.minX), Double($0.minY), Double($0.width), Double($0.height)] },
                milliseconds: (ProcessInfo.processInfo.systemUptime - start) * 1000)
        }
        results.append(result)
    }
    let encoder = JSONEncoder(); encoder.outputFormatting = [.sortedKeys]
    output.write(try encoder.encode(Reply(version: 1, host: ProcessInfo.processInfo.operatingSystemVersionString, results: results)))
}
let protocolFD = dup(STDOUT_FILENO)
dup2(STDERR_FILENO, STDOUT_FILENO)
do { try run(FileHandle(fileDescriptor: protocolFD, closeOnDealloc: true)) }
catch {
    FileHandle.standardError.write(Data("TransitionTool failed: \(error)\n".utf8)); exit(2)
}
