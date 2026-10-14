#if os(macOS)
import Foundation
import Testing
@testable import NativeUIAuditKitRuntime

@Suite("Bounded model downloads", .serialized)
struct NativeModelDownloadTests {
    func fixture() throws -> (NativeModelDownloadEntry, Data) {
        let (bytes, members) = NativeModelInstallerTests().zip([("model.mlpackage/Manifest.json", Data("{}".utf8))])
        return (try entry(bytes, members), bytes)
    }
    func entry(_ bytes: Data, _ members: [ModelArchiveMember], version: String = "1.0.0") throws -> NativeModelDownloadEntry {
        try NativeModelDownloadEntry(url: URL(string: "https://github.com/example/models/releases/download/\(version)/model.zip")!,
            archiveSHA256: ModelArchive.hash(bytes), archiveBytes: bytes.count, members: members, sourceName: "model.mlpackage")
    }
    func response(_ entry: NativeModelDownloadEntry, status: Int = 200, tag: String = "\"one\"",
                  offset: Int = 0) -> HTTPURLResponse {
        HTTPURLResponse(url: entry.url, statusCode: status, httpVersion: "HTTP/1.1", headerFields: [
            "Content-Length": String(entry.archiveBytes - offset), "ETag": tag,
            "Content-Range": "bytes \(offset)-\(entry.archiveBytes - 1)/\(entry.archiveBytes)"])!
    }

    @Test func successAndOfflineReuse() async throws {
        let (entry, bytes) = try fixture()
        let root = try NativeModelInstallerTests().root()
        let transport = StubModelTransport { request, headers, chunk in
            #expect(request.value(forHTTPHeaderField: "Accept-Encoding") == "identity")
            try headers(response(entry)); try chunk(bytes)
        }
        let downloader = try NativeModelDownloader(root: root, transport: transport)
        #expect(try await downloader.download(entry).bytes == bytes)
        let offline = try NativeModelDownloader(root: root, transport: StubModelTransport { _, _, _ in
            Issue.record("A completed archive must not open another request")
            throw URLError(.notConnectedToInternet)
        })
        #expect(try await offline.download(entry).bytes == bytes)
    }

    @Test func truncatedTransferResumesOnlyWithMatchingEntity() async throws {
        let (entry, bytes) = try fixture()
        let root = try NativeModelInstallerTests().root()
        let count = bytes.count / 2
        let interrupted = try NativeModelDownloader(root: root, transport: StubModelTransport { _, headers, chunk in
            try headers(response(entry)); try chunk(bytes.prefix(count)); throw URLError(.networkConnectionLost)
        })
        await #expect(throws: URLError.self) { try await interrupted.download(entry) }
        let wrong = try NativeModelDownloader(root: root, transport: StubModelTransport { _, headers, _ in
            try headers(response(entry, status: 206, tag: "\"different\"", offset: count))
        })
        await #expect(throws: NativeModelDownloader.Failure.self) { try await wrong.download(entry, resume: true) }
        let partial = root.appendingPathComponent(entry.archiveSHA256 + "/archive.zip")
        #expect(try Data(contentsOf: partial) == bytes.prefix(count))
        let resumed = try NativeModelDownloader(root: root, transport: StubModelTransport { request, headers, chunk in
            #expect(request.value(forHTTPHeaderField: "Range") == "bytes=\(count)-")
            #expect(request.value(forHTTPHeaderField: "If-Range") == "\"one\"")
            try headers(response(entry, status: 206, offset: count)); try chunk(bytes.suffix(bytes.count - count))
        })
        #expect(try await resumed.download(entry, resume: true).bytes == bytes)
    }

    @Test func invalidStatusOversizeAndChangedHashDoNotComplete() async throws {
        let (entry, bytes) = try fixture()
        for status in [404, 429, 500, 206] {
            let downloader = try NativeModelDownloader(root: NativeModelInstallerTests().root(), transport: StubModelTransport { _, h, _ in
                try h(response(entry, status: status))
            })
            await #expect(throws: NativeModelDownloader.Failure.self) { try await downloader.download(entry) }
        }
        for body in [bytes + Data([0]), Data(repeating: 0, count: bytes.count), bytes.prefix(7)] {
            let root = try NativeModelInstallerTests().root()
            let downloader = try NativeModelDownloader(root: root, transport: StubModelTransport { _, h, c in
                try h(response(entry)); try c(body)
            })
            await #expect(throws: (any Error).self) { try await downloader.download(entry) }
            let preserved = try await downloader.discardPartial(entry)
            #expect(FileManager.default.fileExists(atPath: preserved.path))
        }
    }

    @Test func cancellationAndCrossInstanceClaimsStopNewRequests() async throws {
        let (entry, _) = try fixture()
        let root = try NativeModelInstallerTests().root()
        let downloader = try NativeModelDownloader(root: root, transport: StubModelTransport { _, _, _ in
            Issue.record("Preflight must stop this request")
        })
        let cancelled = Task {
            withUnsafeCurrentTask { $0?.cancel() }
            return try await downloader.download(entry)
        }
        await #expect(throws: CancellationError.self) { try await cancelled.value }
        try FileManager.default.createDirectory(at: root.appendingPathComponent("transfer-" + entry.archiveSHA256),
                                                withIntermediateDirectories: false)
        await #expect(throws: NativeModelDownloader.Failure.self) { try await downloader.download(entry) }
    }

    @Test func lowSpaceAndWeakETagFailWithoutRetry() async throws {
        let (entry, bytes) = try fixture()
        let root = try NativeModelInstallerTests().root()
        let noSpace = try NativeModelDownloader(root: root, transport: StubModelTransport { _, _, _ in
            Issue.record("Low space must prevent a request")
        }, availableBytes: { _ in 0 })
        await #expect(throws: NativeModelDownloader.Failure.self) { try await noSpace.download(entry) }
        #expect(try FileManager.default.contentsOfDirectory(atPath: root.path).isEmpty)
        let weak = try NativeModelDownloader(root: root, transport: StubModelTransport { _, h, c in
            try h(response(entry, tag: "W/\"weak\"")); try c(bytes.prefix(5))
        })
        await #expect(throws: NativeModelDownloader.Failure.self) { try await weak.download(entry) }
        await #expect(throws: NativeModelDownloader.Failure.self) { try await weak.download(entry, resume: true) }
        let failed = try await weak.discardPartial(entry)
        #expect(try Data(contentsOf: failed.appendingPathComponent("archive.zip")) == bytes.prefix(5))
    }

    @Test func selectionRejectsUnsafeURLsAndUnknownInventory() throws {
        let (entry, _) = try fixture()
        for url in ["http://github.com/a/b/releases/download/1.0.0/a.zip",
                    "https://evil.example/a/b/releases/download/1.0.0/a.zip",
                    "https://github.com/a/b/releases/download/latest/a.zip",
                    "https://user:password@github.com/a/b/releases/download/1.0.0/a.zip",
                    "https://github.com/a/b/releases/download/1.0.0/a.zip?token=x"] {
            #expect(throws: NativeModelDownloader.Failure.self) {
                try NativeModelDownloadEntry(url: URL(string: url)!, archiveSHA256: entry.archiveSHA256,
                    archiveBytes: entry.archiveBytes, members: entry.members, sourceName: entry.sourceName)
            }
        }
        #expect(!NativeModelURLTransport.allowed(URL(string: "https://github.com.evil.example/a")!))
        #expect(!NativeModelURLTransport.allowed(URL(string: "http://release-assets.githubusercontent.com/a")!))
    }

    @Test func realURLSessionUsesOfflineProtocol() async throws {
        let root = try NativeModelInstallerTests().root()
        let (entry, bytes) = try fixture()
        OfflineModelProtocol.set(response: response(entry), bytes: bytes)
        let transport = NativeModelURLTransport {
            let configuration = URLSessionConfiguration.ephemeral
            configuration.protocolClasses = [OfflineModelProtocol.self]
            return configuration
        }
        let downloader = try NativeModelDownloader(root: root, transport: transport)
        #expect(try await downloader.download(entry).bytes == bytes)
    }

    @Test func redirectsStripCredentialsAndBoundDestinations() throws {
        var original = URLRequest(url: URL(string: "https://github.com/a/b/releases/download/1.0.0/a.zip")!)
        original.setValue("secret", forHTTPHeaderField: "Authorization")
        original.setValue("private", forHTTPHeaderField: "Cookie")
        original.setValue("bytes=10-", forHTTPHeaderField: "Range")
        original.setValue("\"one\"", forHTTPHeaderField: "If-Range")
        let destination = URLRequest(url: URL(string: "https://release-assets.githubusercontent.com/test?signature=example")!)
        let clean = try NativeModelURLTransport.redirected(destination, original: original, count: 1)
        #expect(clean.value(forHTTPHeaderField: "Authorization") == nil)
        #expect(clean.value(forHTTPHeaderField: "Cookie") == nil)
        #expect(clean.value(forHTTPHeaderField: "Range") == "bytes=10-")
        #expect(clean.value(forHTTPHeaderField: "If-Range") == "\"one\"")
        #expect(throws: NativeModelDownloader.Failure.self) {
            try NativeModelURLTransport.redirected(destination, original: original, count: 4)
        }
        for path in ["http://github.com/a", "https://evil.example/a", "https://github.com:8443/a"] {
            #expect(throws: NativeModelDownloader.Failure.self) {
                try NativeModelURLTransport.redirected(URLRequest(url: URL(string: path)!), original: original, count: 1)
            }
        }
    }

    @Test func transportErrorsPreservePartialBytes() async throws {
        let (entry, bytes) = try fixture()
        for code in [URLError.timedOut, .secureConnectionFailed, .cancelled] {
            let root = try NativeModelInstallerTests().root()
            let downloader = try NativeModelDownloader(root: root, transport: StubModelTransport { _, h, c in
                try h(response(entry)); try c(bytes.prefix(9)); throw URLError(code)
            })
            await #expect(throws: URLError.self) { try await downloader.download(entry) }
            #expect(try Data(contentsOf: root.appendingPathComponent(entry.archiveSHA256 + "/archive.zip")) == bytes.prefix(9))
        }
    }

    @Test(.enabled(if: NativeModelInstallerTests.residentSourceExists, "Resident source is unavailable."))
    func twoPackagingVersionsUseRealInstallerAndReloadOffline() async throws {
        let support = NativeModelInstallerTests()
        let original = try support.residentArchive()
        let source = try support.root()
        // Extract the known archive through the existing path only during installation.
        // A second notice changes package identity without changing model weights.
        let root = try support.root()
        let installer = try NativeModelInstaller(root: source, compiler: support.compiler())
        for version in ["1.0.0", "1.0.1"] {
            var files: [(String, Data)] = []
            let project = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
            let resident = project.appendingPathComponent("NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.mlpackage")
            for member in original.members {
                files.append((member.path, try Data(contentsOf: resident.appendingPathComponent(String(member.path.dropFirst("model.mlpackage/".count))))))
            }
            files.append(("NOTICE.txt", Data("Offline test packaging \(version)".utf8)))
            let (bytes, members) = support.zip(files)
            let entry = try entry(bytes, members, version: version)
            let downloader = try NativeModelDownloader(root: root, transport: StubModelTransport { _, h, c in
                try h(response(entry)); try c(bytes)
            })
            let url = try await downloader.install(entry, using: installer) { try await support.requireParity(at: $0) }
            let offline = try NativeModelDownloader(root: root, transport: StubModelTransport { _, _, _ in
                throw URLError(.notConnectedToInternet)
            })
            #expect(try await offline.install(entry, using: installer, validate: { _ in }) == url)
        }
    }
}

private struct StubModelTransport: NativeModelTransport {
    let perform: @Sendable (URLRequest, @Sendable (HTTPURLResponse) throws -> Void, @Sendable (Data) throws -> Void) async throws -> Void
    init(_ perform: @escaping @Sendable (URLRequest, @Sendable (HTTPURLResponse) throws -> Void, @Sendable (Data) throws -> Void) async throws -> Void) {
        self.perform = perform
    }
    func transfer(_ request: URLRequest, response: @escaping @Sendable (HTTPURLResponse) throws -> Void,
                  chunk: @escaping @Sendable (Data) throws -> Void) async throws {
        try await perform(request, response, chunk)
    }
}

private final class OfflineModelProtocol: URLProtocol, @unchecked Sendable {
    static let lock = NSLock()
    nonisolated(unsafe) static var reply: HTTPURLResponse?
    nonisolated(unsafe) static var bytes = Data()
    static func set(response: HTTPURLResponse, bytes: Data) {
        lock.lock(); defer { lock.unlock() }; reply = response; self.bytes = bytes
    }
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        Self.lock.lock(); let reply = Self.reply!, bytes = Self.bytes; Self.lock.unlock()
        client?.urlProtocol(self, didReceive: reply, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: bytes)
        client?.urlProtocolDidFinishLoading(self)
    }
    override func stopLoading() {}
}
#endif
