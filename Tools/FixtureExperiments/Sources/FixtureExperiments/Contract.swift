import Foundation
import CryptoKit
import Darwin

public struct ExperimentError: Error, CustomStringConvertible {
    public let description: String
    public init(_ message: String) { description = message }
}

func require(_ condition: Bool, _ message: String) throws {
    if !condition { throw ExperimentError(message) }
}

public func digest(_ data: Data) -> String {
    SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
}

public func fileDigest(_ url: URL) throws -> String {
    let handle = try FileHandle(forReadingFrom: url)
    defer { try? handle.close() }
    var hash = SHA256()
    while let data = try handle.read(upToCount: 1024 * 1024), !data.isEmpty { hash.update(data: data) }
    return hash.finalize().map { String(format: "%02x", $0) }.joined()
}

func validID(_ value: String) -> Bool {
    value.range(of: "^[A-Za-z0-9_-]{1,64}$", options: .regularExpression) != nil
}

func validHash(_ value: String) -> Bool {
    value.range(of: "^[a-f0-9]{64}$", options: .regularExpression) != nil
}

func safePath(_ root: URL, _ name: String) throws -> URL {
    let parts = name.split(separator: "/", omittingEmptySubsequences: false)
    try require(!name.hasPrefix("/") && !parts.isEmpty &&
                parts.allSatisfy { !$0.isEmpty && $0 != "." && $0 != ".." && !$0.contains("\\") }, "unsafe_path")
    let url = root.appendingPathComponent(name)
    try noLinks(url)
    return url
}

func noLinks(_ url: URL) throws {
    var item = url.standardizedFileURL
    while item.path != "/" {
        if let attrs = try? FileManager.default.attributesOfItem(atPath: item.path) {
            try require(attrs[.type] as? FileAttributeType != .typeSymbolicLink, "symlink_refused")
        }
        item.deleteLastPathComponent()
    }
}

func read<T: Decodable>(_ type: T.Type, _ url: URL) throws -> T {
    try noLinks(url)
    let attrs = try FileManager.default.attributesOfItem(atPath: url.path)
    try require((attrs[.size] as? NSNumber)?.intValue ?? Int.max <= 2 * 1024 * 1024, "json_limit")
    return try JSONDecoder().decode(type, from: Data(contentsOf: url))
}

func write<T: Encodable>(_ value: T, _ url: URL, replace: Bool = false) throws {
    try noLinks(url)
    let encoder = JSONEncoder(); encoder.outputFormatting = [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]
    let data = try encoder.encode(value)
    if replace { try data.write(to: url, options: .atomic) }
    else { try data.write(to: url, options: .withoutOverwriting) }
    let fd = open(url.path, O_RDONLY)
    if fd >= 0 { _ = fsync(fd); close(fd) }
    let directory = open(url.deletingLastPathComponent().path, O_RDONLY)
    if directory >= 0 { _ = fsync(directory); close(directory) }
}

public struct Artifact: Codable, Equatable {
    public let path: String
    public let bytes: Int64
    public let sha256: String
    public init(path: String, bytes: Int64, sha256: String) {
        self.path = path; self.bytes = bytes; self.sha256 = sha256
    }
}

func inventory(_ root: URL, limit: Int64 = 268435456) throws -> [Artifact] {
    try noLinks(root)
    guard let walker = FileManager.default.enumerator(at: root, includingPropertiesForKeys: [.isRegularFileKey]) else {
        throw ExperimentError("directory_missing")
    }
    var result = [Artifact](); var total: Int64 = 0
    for case let url as URL in walker {
        try noLinks(url)
        let attrs = try FileManager.default.attributesOfItem(atPath: url.path)
        if attrs[.type] as? FileAttributeType == .typeDirectory { continue }
        try require(attrs[.type] as? FileAttributeType == .typeRegular, "special_file_refused")
        let size = (attrs[.size] as! NSNumber).int64Value; total += size
        try require(total <= limit && result.count < 4096, "artifact_limit")
        result.append(Artifact(path: String(url.path.dropFirst(root.path.count + 1)), bytes: size, sha256: try fileDigest(url)))
    }
    return result.sorted { $0.path < $1.path }
}

public struct Job: Codable, Equatable {
    public let id: String
    public let layout: String
    public let focusID: String?
    public let ancestry: String
    public init(id: String, layout: String, focusID: String? = nil, ancestry: String) {
        self.id = id; self.layout = layout; self.focusID = focusID; self.ancestry = ancestry
    }
}

public struct Limits: Codable {
    public var timeoutSeconds: Double = 60
    public var maxOutputBytes: Int64 = 268435456
    public var maxAttempts: Int = 2
    public init() {}
}

public struct Experiment: Codable {
    public var schema = "fixture-experiment-v1"
    public let id: String
    public var adapter = "ttr-authored-1080p-v1"
    public var sourceDomain = "authored_headless"
    public var dataRole = "development"
    public var trainingEligible = false
    public let rendererSourceSHA256: String
    public let files: [Artifact]
    public let jobs: [Job]
    public var limits: Limits
    public init(id: String, rendererSourceSHA256: String, files: [Artifact], jobs: [Job], limits: Limits = Limits()) {
        self.id = id; self.rendererSourceSHA256 = rendererSourceSHA256
        self.files = files; self.jobs = jobs; self.limits = limits
    }
}

struct Expected: Codable {
    let schema: String
    let framesPerJob: Int
    let width: Int
    let height: Int
}

public struct Host: Codable {
    public var schema = "fixture-host-v1"
    public let workspace: String
    public let renderer: String
    public let rendererSHA256: String
    public let rendererSource: String
    public let rendererSourceSHA256: String
    public var minFreeBytes: Int64 = 2147483648
    public var maxLoad: Double = 8
    public init(workspace: String, renderer: String, rendererSHA256: String, rendererSource: String, rendererSourceSHA256: String) {
        self.workspace = workspace; self.renderer = renderer; self.rendererSHA256 = rendererSHA256
        self.rendererSource = rendererSource; self.rendererSourceSHA256 = rendererSourceSHA256
    }
}

public func validateBundle(_ root: URL) throws -> Experiment {
    try noLinks(root)
    let e = try read(Experiment.self, root.appendingPathComponent("experiment.json"))
    try require(e.schema == "fixture-experiment-v1" && e.adapter == "ttr-authored-1080p-v1", "unsupported_contract")
    try require(e.sourceDomain == "authored_headless" && e.dataRole == "development" && !e.trainingEligible, "unsupported_data_role")
    try require(validID(e.id) && validHash(e.rendererSourceSHA256), "invalid_identity")
    try require((1...100).contains(e.jobs.count) && Set(e.jobs.map(\.id)).count == e.jobs.count, "invalid_jobs")
    for job in e.jobs {
        try require(validID(job.id) && validID(job.ancestry) && ["shelf", "grid", "hero_detail", "top_nav_shelf"].contains(job.layout), "invalid_job")
        if let focus = job.focusID { try require(validID(focus), "invalid_focus") }
    }
    try require(e.limits.timeoutSeconds.isFinite && (0.05...600).contains(e.limits.timeoutSeconds) &&
                (1...2147483648).contains(e.limits.maxOutputBytes) && (1...3).contains(e.limits.maxAttempts), "invalid_limits")
    try require(Set(e.files.map { $0.path.lowercased() }).count == e.files.count, "duplicate_paths")
    for file in e.files {
        _ = try safePath(root, file.path)
        try require(file.path == "expected.json" || file.path.hasPrefix("assets/") || file.path.hasPrefix("LICENSES/"), "undeclared_file_kind")
        try require(file.bytes >= 0 && validHash(file.sha256), "invalid_artifact")
        let url = try safePath(root, file.path)
        let mode = (try FileManager.default.attributesOfItem(atPath: url.path)[.posixPermissions] as! NSNumber).intValue
        try require(mode & 0o111 == 0, "executable_input_refused")
    }
    let actual = try inventory(root).filter { $0.path != "experiment.json" }
    try require(actual == e.files.sorted { $0.path < $1.path }, "bundle_files_changed")
    let expected = try read(Expected.self, root.appendingPathComponent("expected.json"))
    try require(expected.schema == "authored-pair-v1" && expected.framesPerJob == 2 && expected.width == 1920 && expected.height == 1080, "unsupported_expected")
    var isDir: ObjCBool = false
    try require(FileManager.default.fileExists(atPath: root.appendingPathComponent("assets").path, isDirectory: &isDir) && isDir.boolValue, "assets_missing")
    return e
}

public func makeReference(at root: URL, rendererSourceSHA256: String) throws {
    try noLinks(root); try require(validHash(rendererSourceSHA256), "invalid_hash")
    try require(!FileManager.default.fileExists(atPath: root.path), "output_collision")
    try FileManager.default.createDirectory(at: root.appendingPathComponent("assets"), withIntermediateDirectories: true)
    try write(Expected(schema: "authored-pair-v1", framesPerJob: 2, width: 1920, height: 1080), root.appendingPathComponent("expected.json"))
    let jobs = ["shelf", "grid", "hero_detail", "top_nav_shelf"].map { Job(id: $0, layout: $0, ancestry: "hcf336-" + $0) }
    let e = Experiment(id: "hcf336-reference", rendererSourceSHA256: rendererSourceSHA256, files: try inventory(root), jobs: jobs)
    try write(e, root.appendingPathComponent("experiment.json"))
}

public func configureHost(workspace: URL, renderer: URL, source: URL, output: URL, maxLoad: Double = 8) throws {
    for path in [workspace, renderer, source, output] { try noLinks(path) }
    try require(maxLoad.isFinite && maxLoad > 0, "invalid_load_limit")
    var isDir: ObjCBool = false
    try require(FileManager.default.fileExists(atPath: workspace.path, isDirectory: &isDir) && isDir.boolValue, "workspace_missing")
    try require(FileManager.default.isExecutableFile(atPath: renderer.path), "renderer_not_executable")
    var host = Host(workspace: workspace.path, renderer: renderer.path, rendererSHA256: try fileDigest(renderer),
                    rendererSource: source.path, rendererSourceSHA256: try fileDigest(source))
    host.maxLoad = maxLoad
    try write(host, output)
}
