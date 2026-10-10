#if os(macOS)
import Darwin
import Foundation

/// The host creates this selection from its trusted, reviewed catalog. It is not a remote catalog parser.
struct NativeModelDownloadEntry: Sendable {
    let url: URL
    let archiveSHA256: String
    let archiveBytes: Int
    let members: [ModelArchiveMember]
    let sourceName: String

    init(url: URL, archiveSHA256: String, archiveBytes: Int, members: [ModelArchiveMember], sourceName: String) throws {
        let parts = url.path.components(separatedBy: "/")
        func component(_ value: String) -> Bool {
            !value.isEmpty && value != "." && value != ".."
                && value.utf8.allSatisfy { (65...90).contains($0) || (97...122).contains($0)
                    || (48...57).contains($0) || [45, 46, 95].contains($0) }
        }
        guard url.scheme == "https", url.host == "github.com", url.port == nil,
              url.user == nil, url.password == nil, url.query == nil, url.fragment == nil,
              !url.absoluteString.contains("%"), parts.count == 7, parts[3] == "releases", parts[4] == "download",
              [parts[1], parts[2], parts[5], parts[6]].allSatisfy(component),
              !["latest", "nightly"].contains(parts[5].lowercased()), parts[6].hasSuffix(".zip"),
              Self.isHash(archiveSHA256), (1...32 * 1024 * 1024).contains(archiveBytes),
              ModelArchive.validPath(sourceName), component(sourceName), sourceName.hasSuffix(".mlpackage"),
              !members.isEmpty, members.count <= 256,
              Set(members.map { $0.path.lowercased() }).count == members.count,
              members.allSatisfy({ ModelArchive.validPath($0.path) && $0.path.components(separatedBy: "/").allSatisfy(component)
                  && (0...64 * 1024 * 1024).contains($0.bytes)
                  && Self.isHash($0.sha256) }),
              members.reduce(0, { $0 + $1.bytes }) <= 64 * 1024 * 1024,
              members.contains(where: { $0.path == sourceName + "/Manifest.json" }) else {
            throw NativeModelDownloader.Failure.invalidSelection
        }
        self.url = url
        self.archiveSHA256 = archiveSHA256
        self.archiveBytes = archiveBytes
        self.members = members
        self.sourceName = sourceName
    }

    static func isHash(_ value: String) -> Bool {
        value.utf8.count == 64 && value.utf8.allSatisfy { (48...57).contains($0) || (97...102).contains($0) }
    }

    func verify(_ bytes: Data) throws -> ModelArchive {
        guard bytes.count == archiveBytes else { throw NativeModelDownloader.Failure.incomplete }
        return try ModelArchive(bytes: bytes, expectedSHA256: archiveSHA256, members: members)
    }
}

protocol NativeModelTransport: Sendable {
    func transfer(_ request: URLRequest,
                  response: @escaping @Sendable (HTTPURLResponse) throws -> Void,
                  chunk: @escaping @Sendable (Data) throws -> Void) async throws
}

/// Explicit transfer only. No work starts from initialization or application startup.
actor NativeModelDownloader {
    enum Failure: Error { case invalidSelection, unsafeStorage, busy, insufficientSpace, invalidResponse,
        changedResource, resumeUnavailable, incomplete, oversized, redirectDenied }
    struct Resume: Codable {
        let version: Int
        let url: String
        let hash: String
        let size: Int
        let etag: String?
    }
    let root: URL
    let transport: any NativeModelTransport
    let availableBytes: @Sendable (URL) throws -> Int
    private var busy = false

    init(root: URL, transport: any NativeModelTransport = NativeModelURLTransport(),
         availableBytes: @escaping @Sendable (URL) throws -> Int = {
             try $0.resourceValues(forKeys: [.volumeAvailableCapacityKey]).volumeAvailableCapacity ?? 0
         }) throws {
        guard root.isFileURL, root.standardizedFileURL.path == root.resolvingSymlinksInPath().path,
              try root.resourceValues(forKeys: [.isDirectoryKey]).isDirectory == true else { throw Failure.unsafeStorage }
        self.root = root.standardizedFileURL
        self.transport = transport
        self.availableBytes = availableBytes
    }

    /// Resume is explicit. A changed response never triggers an automatic new attempt.
    func download(_ entry: NativeModelDownloadEntry, resume: Bool = false) async throws -> ModelArchive {
        guard !busy else { throw Failure.busy }
        busy = true
        defer { busy = false }
        try Task.checkCancellation()
        guard root.path == root.resolvingSymlinksInPath().path else { throw Failure.unsafeStorage }
        let claim = root.appendingPathComponent("transfer-" + entry.archiveSHA256)
        guard claim.path.withCString({ Darwin.mkdir($0, 0o700) }) == 0 else { throw Failure.busy }
        defer { _ = claim.path.withCString { Darwin.rmdir($0) } }
        let folder = root.appendingPathComponent(entry.archiveSHA256)
        let file = folder.appendingPathComponent("archive.zip")
        let record = folder.appendingPathComponent("resume.json")
        guard folder.path == folder.resolvingSymlinksInPath().path else { throw Failure.unsafeStorage }
        var offset = 0, etag: String?
        if FileManager.default.fileExists(atPath: folder.path) {
            offset = try Self.fileSize(file, maximum: entry.archiveBytes)
            if offset == entry.archiveBytes { return try entry.verify(Data(contentsOf: file)) }
            guard resume else { throw Failure.resumeUnavailable }
            _ = try Self.fileSize(record, maximum: 16_384)
            let saved = try JSONDecoder().decode(Resume.self, from: Data(contentsOf: record))
            guard saved.version == 1, saved.url == entry.url.absoluteString, saved.hash == entry.archiveSHA256,
                  saved.size == entry.archiveBytes, let tag = saved.etag, Self.strongETag(tag) else {
                throw Failure.resumeUnavailable
            }
            etag = tag
        } else {
            guard !resume else { throw Failure.resumeUnavailable }
            let free = try availableBytes(root)
            guard free > entry.archiveBytes + 1024 * 1024 else { throw Failure.insufficientSpace }
            try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: false, attributes: [.posixPermissions: 0o700])
            try Data().write(to: file, options: .withoutOverwriting)
        }
        guard try availableBytes(root) > entry.archiveBytes - offset + 1024 * 1024 else { throw Failure.insufficientSpace }
        let sink = try NativeDownloadSink(entry: entry, file: file, record: record, offset: offset, etag: etag)
        defer { sink.close() }
        var request = URLRequest(url: entry.url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 30)
        request.setValue("identity", forHTTPHeaderField: "Accept-Encoding")
        if offset > 0 {
            request.setValue("bytes=\(offset)-", forHTTPHeaderField: "Range")
            request.setValue(etag, forHTTPHeaderField: "If-Range")
        }
        try await transport.transfer(request, response: { try sink.response($0) }, chunk: { try sink.chunk($0) })
        try Task.checkCancellation()
        sink.close()
        guard try Self.fileSize(file, maximum: entry.archiveBytes) == entry.archiveBytes else { throw Failure.incomplete }
        return try entry.verify(Data(contentsOf: file))
    }

    /// Use the same verified installation path. Downloading never selects an active model.
    func install(_ entry: NativeModelDownloadEntry, using installer: NativeModelInstaller, resume: Bool = false,
                 validate: @Sendable (URL) async throws -> Void) async throws -> URL {
        let archive = try await download(entry, resume: resume)
        let existing = installer.root.appendingPathComponent(entry.archiveSHA256)
        if FileManager.default.fileExists(atPath: existing.path) {
            let url = try await installer.recover(archive: archive, sourceName: entry.sourceName)
            try await validate(url)
            try Task.checkCancellation()
            return url
        }
        return try await installer.install(archive: archive, sourceName: entry.sourceName, validate: validate)
    }

    /// Preserve a failed transfer before the host explicitly starts again.
    func discardPartial(_ entry: NativeModelDownloadEntry) throws -> URL {
        guard !busy else { throw Failure.busy }
        guard root.path == root.resolvingSymlinksInPath().path else { throw Failure.unsafeStorage }
        let claim = root.appendingPathComponent("transfer-" + entry.archiveSHA256)
        guard claim.path.withCString({ Darwin.mkdir($0, 0o700) }) == 0 else { throw Failure.busy }
        defer { _ = claim.path.withCString { Darwin.rmdir($0) } }
        let folder = root.appendingPathComponent(entry.archiveSHA256)
        guard folder.path == folder.resolvingSymlinksInPath().path else { throw Failure.unsafeStorage }
        let file = folder.appendingPathComponent("archive.zip")
        _ = try Self.fileSize(file, maximum: entry.archiveBytes)
        guard (try? entry.verify(Data(contentsOf: file))) == nil else { throw Failure.invalidSelection }
        let destination = root.appendingPathComponent("rejected-" + entry.archiveSHA256 + "-" + UUID().uuidString)
        try FileManager.default.moveItem(at: folder, to: destination)
        return destination
    }

    static func fileSize(_ url: URL, maximum: Int) throws -> Int {
        var fresh = url
        fresh.removeAllCachedResourceValues()
        let info = try fresh.resourceValues(forKeys: [.isRegularFileKey, .isSymbolicLinkKey, .fileSizeKey])
        guard info.isRegularFile == true, info.isSymbolicLink != true,
              let size = info.fileSize, size <= maximum else { throw Failure.unsafeStorage }
        return size
    }

    static func strongETag(_ value: String) -> Bool {
        value.count >= 2 && value.count <= 256 && value.first == "\"" && value.last == "\""
            && value.utf8.allSatisfy { $0 >= 32 && $0 < 127 }
    }
}

/// Serialize file writes even if a test transport supplies concurrent callbacks.
private final class NativeDownloadSink: @unchecked Sendable {
    let lock = NSLock()
    let entry: NativeModelDownloadEntry
    let record: URL
    let offset: Int
    let etag: String?
    var handle: FileHandle?
    var count: Int
    var admitted = false
    init(entry: NativeModelDownloadEntry, file: URL, record: URL, offset: Int, etag: String?) throws {
        self.entry = entry; self.record = record; self.offset = offset; self.etag = etag; count = offset
        handle = try FileHandle(forWritingTo: file)
        try handle?.seekToEnd()
    }
    func response(_ response: HTTPURLResponse) throws {
        lock.lock(); defer { lock.unlock() }
        guard !admitted, response.statusCode == (offset == 0 ? 200 : 206),
              let url = response.url, NativeModelURLTransport.allowed(url),
              response.value(forHTTPHeaderField: "Content-Encoding").map({ $0.lowercased() == "identity" }) ?? true,
              response.expectedContentLength == -1 || response.expectedContentLength == entry.archiveBytes - offset else {
            throw NativeModelDownloader.Failure.invalidResponse
        }
        let tag = response.value(forHTTPHeaderField: "ETag")
        if offset > 0 {
            guard tag == etag,
                  response.value(forHTTPHeaderField: "Content-Range") == "bytes \(offset)-\(entry.archiveBytes - 1)/\(entry.archiveBytes)" else {
                throw NativeModelDownloader.Failure.changedResource
            }
        }
        let saved = NativeModelDownloader.Resume(version: 1, url: entry.url.absoluteString,
            hash: entry.archiveSHA256, size: entry.archiveBytes,
            etag: tag.flatMap { NativeModelDownloader.strongETag($0) ? $0 : nil })
        try JSONEncoder().encode(saved).write(to: record, options: .atomic)
        admitted = true
    }
    func chunk(_ bytes: Data) throws {
        lock.lock(); defer { lock.unlock() }
        guard admitted, let handle else { throw NativeModelDownloader.Failure.invalidResponse }
        guard bytes.count <= entry.archiveBytes - count else { throw NativeModelDownloader.Failure.oversized }
        try handle.write(contentsOf: bytes)
        count += bytes.count
    }
    func close() {
        lock.lock(); defer { lock.unlock() }
        try? handle?.close(); handle = nil
    }
}
#endif
