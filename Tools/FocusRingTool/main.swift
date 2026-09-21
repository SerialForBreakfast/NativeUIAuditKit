import Foundation
import CoreGraphics
import CoreML
import ImageIO
import CryptoKit
import NativeUIAuditKit
import Darwin

// Package-only diagnostic; no public library API, downloads or output files.
struct Item: Decodable, Sendable {
    let id: String
    let path: String
    let sha256: String
    let bounds: [Double]
}
struct Request: Decodable, Sendable {
    let version: Int
    let root: String
    let mode: String
    let model: String?
    let items: [Item]
}
struct ItemResult: Encodable, Sendable {
    let id: String
    let png: String?
    let probability: Float?
    let cropMilliseconds: Double
    let inferenceMilliseconds: Double?
}
struct Reply: Encodable, Sendable {
    let version: Int
    let results: [ItemResult]
    let modelLoadMilliseconds: Double?
    let host: String
    let computeUnits: String
}
enum ToolError: Error { case invalidRequest, outsideRoot, changedImage, invalidImage, invalidModel }
func checked(_ path: String, root: URL) throws -> URL {
    let url = URL(fileURLWithPath: path).standardizedFileURL
    let resolved = url.resolvingSymlinksInPath()
    guard resolved.path.hasPrefix(root.path + "/"), resolved.path == url.path else { throw ToolError.outsideRoot }
    return url
}
func milliseconds(_ start: TimeInterval) -> Double { (ProcessInfo.processInfo.systemUptime - start) * 1000 }
func run(output: FileHandle) throws {
    let data = FileHandle.standardInput.readDataToEndOfFile()
    guard data.count <= 4_194_304 else { throw ToolError.invalidRequest }
    let r = try JSONDecoder().decode(Request.self, from: data)
    let root = URL(fileURLWithPath: r.root).standardizedFileURL.resolvingSymlinksInPath()
    guard FileManager.default.fileExists(atPath: root.appendingPathComponent("Package.swift").path),
          r.version == 1, ["crop", "infer"].contains(r.mode), !r.items.isEmpty,
          r.items.count <= 128, Set(r.items.map(\.id)).count == r.items.count else { throw ToolError.invalidRequest }
    var inputs: [(Item, CGImage)] = []
    var totalPixels = 0
    for item in r.items {
        guard !item.id.isEmpty, item.bounds.count == 4, item.bounds.allSatisfy(\.isFinite) else { throw ToolError.invalidRequest }
        let url = try checked(item.path, root: root)
        let size = try url.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0
        guard size > 0, size <= 32 * 1024 * 1024 else { throw ToolError.invalidImage }
        let bytes = try Data(contentsOf: url)
        guard SHA256.hash(data: bytes).map({ String(format: "%02x", $0) }).joined() == item.sha256 else { throw ToolError.changedImage }
        guard let src = CGImageSourceCreateWithData(bytes as CFData, nil),
              CGImageSourceGetType(src) as String? == "public.png",
              let props = CGImageSourceCopyPropertiesAtIndex(src, 0, nil) as? [String: Any],
              let width = props[kCGImagePropertyPixelWidth as String] as? Int,
              let height = props[kCGImagePropertyPixelHeight as String] as? Int,
              width > 0, height > 0, width <= 40_000_000 / height,
              let image = CGImageSourceCreateImageAtIndex(src, 0, nil) else { throw ToolError.invalidImage }
        let b = item.bounds
        totalPixels += width * height
        guard totalPixels <= 80_000_000 else { throw ToolError.invalidImage }
        guard b[0] >= 0, b[1] >= 0, b[2] > 0, b[3] > 0,
              b[0]+b[2] <= Double(width), b[1]+b[3] <= Double(height) else { throw ToolError.invalidImage }
        inputs.append((item, image))
    }
    var classifier: FocusRingClassifier?
    var loadTime: Double?
    if r.mode == "infer" {
        guard let path = r.model else { throw ToolError.invalidModel }
        let url = try checked(path, root: root)
        let config = MLModelConfiguration(); config.computeUnits = .cpuOnly
        let start = ProcessInfo.processInfo.systemUptime
        let model = try MLModel(contentsOf: url, configuration: config)
        guard model.modelDescription.outputDescriptionsByName["is_focused_prob"] != nil else { throw ToolError.invalidModel }
        classifier = FocusRingClassifier(model: model)
        loadTime = milliseconds(start)
    }
    var results: [ItemResult] = []
    for (item, image) in inputs {
        let start = ProcessInfo.processInfo.systemUptime
        let b = item.bounds
        guard let crop = FocusRingClassifier.makeCrop(from: image, bbox: CGRect(x: b[0], y: b[1], width: b[2], height: b[3])) else { throw ToolError.invalidImage }
        let cropTime = milliseconds(start)
        if let classifier {
            let inferenceStart = ProcessInfo.processInfo.systemUptime
            let p = try classifier.classify(crop: crop).isFocusedProbability
            guard p.isFinite, (0...1).contains(p) else { throw ToolError.invalidModel }
            results.append(ItemResult(id: item.id, png: nil, probability: p, cropMilliseconds: cropTime, inferenceMilliseconds: milliseconds(inferenceStart)))
        } else {
            let png = NSMutableData()
            guard let destination = CGImageDestinationCreateWithData(png, "public.png" as CFString, 1, nil) else { throw ToolError.invalidImage }
            CGImageDestinationAddImage(destination, crop, nil)
            guard CGImageDestinationFinalize(destination) else { throw ToolError.invalidImage }
            results.append(ItemResult(id: item.id, png: (png as Data).base64EncodedString(), probability: nil, cropMilliseconds: cropTime, inferenceMilliseconds: nil))
        }
    }
    let reply = Reply(version: 1, results: results, modelLoadMilliseconds: loadTime,
                      host: ProcessInfo.processInfo.operatingSystemVersionString, computeUnits: "cpuOnly")
    output.write(try JSONEncoder().encode(reply))
}
// Some CoreML backends log to stdout, even after prediction. Keep the protocol
// on its own original descriptor; route framework diagnostics to stderr.
let protocolFD = dup(STDOUT_FILENO)
dup2(STDERR_FILENO, STDOUT_FILENO)
do { try run(output: FileHandle(fileDescriptor: protocolFD, closeOnDealloc: true)) } catch {
    FileHandle.standardError.write(Data("FocusRingTool failed: \(error)\n".utf8))
    exit(2)
}
