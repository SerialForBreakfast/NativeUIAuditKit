import Foundation
import CryptoKit
import Darwin
import ImageIO
import NativeUIAuditKit
import NativeUIAuditKitModels

enum JSON: Codable, Sendable, Equatable {
    case object([String: JSON]), array([JSON]), string(String), number(Double), bool(Bool), null
    init(from decoder: any Decoder) throws {
        let c = try decoder.singleValueContainer()
        if c.decodeNil() { self = .null }
        else if let b = try? c.decode(Bool.self) { self = .bool(b) }
        else if let s = try? c.decode(String.self) { self = .string(s) }
        else if let n = try? c.decode(Double.self), n.isFinite { self = .number(n) }
        else if let a = try? c.decode([JSON].self) { self = .array(a) }
        else { self = .object(try c.decode([String: JSON].self)) }
    }
    func encode(to encoder: any Encoder) throws {
        var c = encoder.singleValueContainer()
        switch self {
        case .object(let v): try c.encode(v)
        case .array(let v): try c.encode(v)
        case .string(let v): try c.encode(v)
        case .number(let v): try c.encode(v)
        case .bool(let v): try c.encode(v)
        case .null: try c.encodeNil()
        }
    }
    subscript(_ key: String) -> JSON? { if case .object(let v) = self { return v[key] }; return nil }
    var string: String? { if case .string(let v) = self { return v }; return nil }
    var number: Double? { if case .number(let v) = self { return v }; return nil }
    var boolean: Bool? { if case .bool(let v) = self { return v }; return nil }
    var object: [String: JSON]? { if case .object(let v) = self { return v }; return nil }
    static func encoded<T: Encodable>(_ value: T) throws -> JSON {
        try JSONDecoder().decode(JSON.self, from: JSONEncoder().encode(value))
    }
    func data() throws -> Data {
        let e = JSONEncoder(); e.outputFormatting = [.sortedKeys, .withoutEscapingSlashes]
        return try e.encode(self)
    }
}

struct AuditError: Error, Sendable, LocalizedError {
    let code: String
    let message: String
    init(_ code: String, _ message: String) { self.code = code; self.message = message }
    var errorDescription: String? { message }
    var json: JSON { .object(["code": .string(code), "message": .string(message)]) }
    static func wrap(_ error: any Error) -> AuditError {
        error as? AuditError ?? AuditError("processing_failed", error.localizedDescription)
    }
}

struct ScanOptions: Codable, Sendable, Equatable, Hashable {
    var platform = "auto"
    var minConfidence = 0.5
    var ocr = true
    var strict = false
    func validate() throws {
        guard ["auto", "iOS", "tvOS"].contains(platform),
              minConfidence.isFinite, (0...1).contains(minConfidence) else {
            throw AuditError("invalid_options", "platform must be auto/iOS/tvOS; minConfidence must be finite in [0,1].")
        }
    }
}

struct FileScope: Sendable {
    let root: URL
    static let byteLimit = 50 * 1024 * 1024
    init(_ path: String) throws {
        guard !path.isEmpty, !path.contains("\0"), !path.contains("://") else {
            throw AuditError("invalid_root", "Expected a nonempty local directory path.")
        }
        let url = URL(fileURLWithPath: path).standardizedFileURL.resolvingSymlinksInPath()
        guard try url.resourceValues(forKeys: [.isDirectoryKey]).isDirectory == true else {
            throw AuditError("invalid_root", "The allowed root must be an existing directory.")
        }
        root = url
    }
    func contains(_ path: String) -> Bool { path == root.path || path.hasPrefix(root.path == "/" ? "/" : root.path + "/") }
    func resolve(_ path: String) throws -> URL {
        guard !path.isEmpty, !path.contains("\0"), !path.contains("://") else {
            throw AuditError("invalid_path", "Expected a local file path.")
        }
        let url = (path.hasPrefix("/") ? URL(fileURLWithPath: path) : root.appendingPathComponent(path))
            .standardizedFileURL.resolvingSymlinksInPath()
        guard contains(url.path) else { throw AuditError("outside_root", "Input is outside the configured root.") }
        return url
    }
    func read(_ path: String) throws -> (URL, Data) {
        let url = try resolve(path)
        // O_NONBLOCK avoids hanging on FIFOs. Verify the opened file, not just its name.
        let fd = open(url.path, O_RDONLY | O_NOFOLLOW | O_NONBLOCK | O_CLOEXEC)
        guard fd >= 0 else { throw AuditError("unreadable_input", "Cannot open input: \(String(cString: strerror(errno))).") }
        let handle = FileHandle(fileDescriptor: fd, closeOnDealloc: true)
        defer { try? handle.close() }
        var info = stat()
        guard fstat(fd, &info) == 0, (info.st_mode & S_IFMT) == S_IFREG else {
            throw AuditError("invalid_file", "Input must be a regular file.")
        }
        var actual = [CChar](repeating: 0, count: Int(MAXPATHLEN))
        guard fcntl(fd, F_GETPATH, &actual) == 0 else {
            throw AuditError("unreadable_input", "Cannot verify opened-file path.")
        }
        let opened = actual.prefix { $0 != 0 }.map { UInt8(bitPattern: $0) }
        let openedPath = URL(fileURLWithPath: String(decoding: opened, as: UTF8.self)).resolvingSymlinksInPath().path
        guard contains(openedPath) else { throw AuditError("outside_root", "Opened input escaped the configured root.") }
        guard info.st_size >= 0, info.st_size <= Self.byteLimit else {
            throw AuditError("input_too_large", "Input exceeds 50 MiB.")
        }
        var bytes = Data()
        while let chunk = try handle.read(upToCount: min(65536, Self.byteLimit + 1 - bytes.count)), !chunk.isEmpty {
            bytes.append(chunk)
            guard bytes.count <= Self.byteLimit else { throw AuditError("input_too_large", "Input exceeds 50 MiB.") }
        }
        return (url, bytes)
    }
    func batch(_ path: String) throws -> [String] {
        let dir = try resolve(path)
        guard try dir.resourceValues(forKeys: [.isDirectoryKey]).isDirectory == true else {
            throw AuditError("invalid_directory", "scan-batch needs a directory.")
        }
        // Nonrecursive, bounded enumeration; unsupported extensions are explicitly out of scope.
        guard let enumerator = FileManager.default.enumerator(at: dir, includingPropertiesForKeys: nil,
            options: [.skipsSubdirectoryDescendants, .skipsHiddenFiles]) else {
            throw AuditError("unreadable_directory", "Cannot enumerate directory.")
        }
        var paths: [String] = []
        var seen = 0
        for case let url as URL in enumerator {
            seen += 1
            guard seen <= 4096 else { throw AuditError("batch_too_large", "Directory has more than 4096 entries.") }
            if ["png", "jpg", "jpeg"].contains(url.pathExtension.lowercased()) {
                paths.append(url.path)
                guard paths.count <= 128 else { throw AuditError("batch_too_large", "Batch exceeds 128 image entries.") }
            }
        }
        return paths.sorted()
    }
}

func decodeImage(_ data: Data) throws -> CGImage {
    guard let source = CGImageSourceCreateWithData(data as CFData, nil),
          ["public.png", "public.jpeg"].contains(CGImageSourceGetType(source) as String? ?? ""),
          CGImageSourceGetCount(source) == 1,
          let p = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [CFString: Any],
          let w = p[kCGImagePropertyPixelWidth] as? Int, let h = p[kCGImagePropertyPixelHeight] as? Int,
          w > 0, h > 0, w <= 24000, h <= 24000, w <= 24_000_000 / h else {
        throw AuditError("invalid_image", "Expected a single PNG/JPEG image no larger than 24 megapixels.")
    }
    guard (p[kCGImagePropertyOrientation] as? Int ?? 1) == 1 else {
        throw AuditError("unsupported_orientation", "Normalize EXIF orientation before scanning.")
    }
    guard let image = CGImageSourceCreateImageAtIndex(source, 0, nil),
          CGImageSourceGetStatusAtIndex(source, 0) == .statusComplete else {
        throw AuditError("invalid_image", "Image decoding failed or data is incomplete.")
    }
    return image
}

func sha256(_ data: Data) -> String { SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined() }

struct ArtifactIdentity: Encodable, Sendable {
    let modelID: String
    let digestAlgorithm = "relative-name-nul-file-sha256-newline-v1"
    let treeSHA256: String
    let fileCount: Int
    let bytes: Int
    // Stable tree format: sorted relative name, NUL, file SHA256, newline.
    static func measure(_ url: URL, modelID: String) throws -> ArtifactIdentity {
        guard let e = FileManager.default.enumerator(at: url, includingPropertiesForKeys:
            [.isRegularFileKey, .isSymbolicLinkKey, .fileSizeKey]) else {
            throw AuditError("model_unavailable", "Cannot enumerate model artifact.")
        }
        var entries: [(String, URL)] = []
        for case let child as URL in e {
            let v = try child.resourceValues(forKeys: [.isRegularFileKey, .isSymbolicLinkKey])
            guard v.isSymbolicLink != true else { throw AuditError("model_unavailable", "Symlink in model artifact.") }
            if v.isRegularFile == true { entries.append((String(child.path.dropFirst(url.path.count + 1)), child)) }
            guard entries.count <= 4096 else { throw AuditError("model_unavailable", "Model artifact has too many files.") }
        }
        guard !entries.isEmpty else { throw AuditError("model_unavailable", "Model artifact is empty.") }
        var index = Data(); var bytes = 0
        for (name, file) in entries.sorted(by: { $0.0 < $1.0 }) {
            let h = try FileHandle(forReadingFrom: file); defer { try? h.close() }
            var digest = SHA256()
            while let chunk = try h.read(upToCount: 1_048_576), !chunk.isEmpty {
                bytes += chunk.count
                guard bytes <= 2_000_000_000 else { throw AuditError("model_unavailable", "Model exceeds bounded inspection size.") }
                digest.update(data: chunk)
            }
            let hex = digest.finalize().map { String(format: "%02x", $0) }.joined()
            index.append(Data("\(name)\0\(hex)\n".utf8))
        }
        return ArtifactIdentity(modelID: modelID, treeSHA256: sha256(index), fileCount: entries.count, bytes: bytes)
    }
}
