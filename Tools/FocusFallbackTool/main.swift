import Foundation
import CoreGraphics
import ImageIO
import CryptoKit
import NativeUIAuditKitRuntime
import Darwin

struct Request: Decodable {
    let version: Int
    let root: String
    let path: String
    let sha256: String
    let observations: [NativeUIElementObservation]
}
struct Reply: Encodable {
    let version: Int
    let sha256: String
    let policy: String
    let milliseconds: Double
    let observations: [NativeUIElementObservation]
}
enum Invalid: Error { case request, path, hash, image, geometry }

func run() throws {
    let input = try FileHandle.standardInput.read(upToCount: 4_194_305) ?? Data()
    guard input.count <= 4_194_304 else { throw Invalid.request }
    let request = try JSONDecoder().decode(Request.self, from: input)
    guard request.version == 1, request.observations.count <= 512,
          Set(request.observations.map(\.id)).count == request.observations.count else { throw Invalid.request }
    let root = URL(fileURLWithPath: request.root).standardizedFileURL
    let path = URL(fileURLWithPath: request.path).standardizedFileURL
    guard root.path != "/", root == root.resolvingSymlinksInPath(),
          path == path.resolvingSymlinksInPath(), path.path.hasPrefix(root.path + "/") else { throw Invalid.path }
    let size = try path.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0
    guard size > 0, size <= 33_554_432 else { throw Invalid.image }
    let bytes = try Data(contentsOf: path)
    guard SHA256.hash(data: bytes).map({ String(format: "%02x", $0) }).joined() == request.sha256 else { throw Invalid.hash }
    guard let source = CGImageSourceCreateWithData(bytes as CFData, nil),
          CGImageSourceGetType(source) as String? == "public.png",
          let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any],
          let width = properties[kCGImagePropertyPixelWidth as String] as? Int,
          let height = properties[kCGImagePropertyPixelHeight as String] as? Int,
          height > 0, width > 0, width <= 40_000_000 / height,
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else { throw Invalid.image }
    for observation in request.observations {
        let box = observation.boundingBoxPixels
        guard [box.x, box.y, box.width, box.height, observation.confidence].allSatisfy(\.isFinite),
              box.width > 0, box.height > 0,
              abs(box.x) <= Double(width) * 2, abs(box.y) <= Double(height) * 2,
              box.width <= Double(width) * 2, box.height <= Double(height) * 2,
              (0...1).contains(observation.confidence) else { throw Invalid.geometry }
    }
    let start = ProcessInfo.processInfo.systemUptime
    let observations = FocusFallbackReplay.resolve(image: image, observations: request.observations)
    let elapsed = (ProcessInfo.processInfo.systemUptime - start) * 1000
    let reply = Reply(version: 1, sha256: request.sha256, policy: "legacy-visual-heuristic-v1",
                      milliseconds: elapsed, observations: observations)
    try FileHandle.standardOutput.write(contentsOf: JSONEncoder().encode(reply))
}
do { try run() }
catch {
    FileHandle.standardError.write(Data("Focus fallback rejected input: \(error)\n".utf8))
    exit(1)
}
