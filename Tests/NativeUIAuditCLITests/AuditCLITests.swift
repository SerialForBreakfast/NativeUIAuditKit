import Testing
import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers
import NativeUIAuditKit
@testable import NativeUIAuditCLI

private struct TestWorkspace: Sendable {
    let root: URL
    init() throws {
        let repo = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
        root = repo.appendingPathComponent(".build/debug-output/cli-tests-\(UUID().uuidString)")
        try FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)
    }
    func image(_ name: String = "image.png") throws -> URL {
        let context = CGContext(data: nil, width: 32, height: 24, bitsPerComponent: 8,
            bytesPerRow: 128, space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
        let data = NSMutableData()
        let dest = CGImageDestinationCreateWithData(data, UTType.png.identifier as CFString, 1, nil)!
        CGImageDestinationAddImage(dest, context.makeImage()!, nil)
        #expect(CGImageDestinationFinalize(dest))
        let url = root.appendingPathComponent(name)
        try (data as Data).write(to: url)
        return url
    }
}

private actor FakeBackend: AuditBackend {
    var calls = 0
    let fail: Bool
    let degraded: Bool
    init(fail: Bool = false, degraded: Bool = false) { self.fail = fail; self.degraded = degraded }
    func doctor() -> JSON { .object(["schemaVersion": .number(1), "inferencePerformed": .bool(false)]) }
    func scan(_ image: CGImage, options: ScanOptions) throws -> RuntimeScan {
        calls += 1
        if fail { throw AuditError("model_unavailable", "fixture unavailable") }
        let health = ModalityHealth(ocr: degraded ? .failed(reason: "fixture OCR failed") : .empty, focus: .notRequested)
        return RuntimeScan(detector: ArtifactIdentity(modelID: "fixture", treeSHA256: "fixture", fileCount: 1, bytes: 1),
            platform: "iOS", cacheState: calls == 1 ? "cold" : "warm", modelLoadMs: 0,
            result: NativeUIDetailedDetectionResult(elements: [NativeUIElementObservation(
                elementType: .label, boundingBox: .init(x: 0, y: 0, width: 1, height: 1),
                boundingBoxPixels: .init(x: 0, y: 0, width: 32, height: 24), confidence: 0.9,
                issues: [.init(kind: .truncatedText, description: "heuristic fixture", confidence: 0.85)],
                confidenceSource: .pixelModel)], modalityHealth: health))
    }
}

@Test func argumentValidation() throws {
    #expect(try CLIArguments.parse(["scan", "a.png", "--platform", "tvOS", "--no-ocr"]).options.ocr == false)
    #expect(throws: (any Error).self) { try CLIArguments.parse(["mcp"]) }
    for args in [["scan"], ["scan", "a", "--min-confidence", "nan"], ["scan", "a", "--min-confidence", "1.1"],
                 ["scan", "a", "--platform", "linux"], ["doctor", "--strict"], ["scan", "a", "--root", ".", "--root", "."],
                 ["scan", "a", "--wat"], ["scan", "a", "--format", "xml"]] {
        #expect(throws: (any Error).self) { try CLIArguments.parse(args) }
    }
}

@Test func pathsAndImagesFailClosed() throws {
    let ws = try TestWorkspace(); let image = try ws.image(); let scope = try FileScope(ws.root.path)
    let (_, data) = try scope.read(image.path)
    #expect(try decodeImage(data).width == 32)
    #expect(throws: (any Error).self) { try scope.read("../outside.png") }
    #expect(throws: (any Error).self) { try scope.read("missing.png") }
    #expect(throws: (any Error).self) { try scope.read(".") }
    #expect(throws: (any Error).self) { try decodeImage(Data("bad".utf8)) }
    let other = try TestWorkspace(); let otherImage = try other.image()
    let link = ws.root.appendingPathComponent("escape.png")
    try FileManager.default.createSymbolicLink(at: link, withDestinationURL: otherImage)
    #expect(throws: (any Error).self) { try scope.read(link.path) }
    #expect(throws: (any Error).self) { try scope.resolve(ws.root.path + "-sibling/file.png") }
}

@Test func completeBatchAndModelFailure() async throws {
    let ws = try TestWorkspace(); _ = try ws.image("b.png")
    try Data("corrupt".utf8).write(to: ws.root.appendingPathComponent("a.png"))
    let backend = FakeBackend()
    let service = AuditService(scope: try FileScope(ws.root.path), backend: backend)
    let report = try await service.batch(".", options: ScanOptions())
    #expect(report["count"]?.number == 2)
    #expect(report["failed"]?.number == 1)
    #expect(report["strictFailure"]?.boolean == true)
    #expect(await backend.calls == 1)
    let warm = await service.scan("b.png", options: ScanOptions())
    #expect(warm["runtime"]?["cacheState"]?.string == "warm")
    let warningsOnly = await service.scan("b.png", options: ScanOptions(strict: true))
    #expect(warningsOnly["strictFailure"]?.boolean == false)
    let failed = await AuditService(scope: try FileScope(ws.root.path), backend: FakeBackend(fail: true)).scan("b.png", options: ScanOptions())
    #expect(failed["error"]?["code"]?.string == "model_unavailable")
    let bad = await service.scan("missing.png", options: ScanOptions())
    #expect(bad["status"]?.string == "failed")
}

@Test func strictDegradationAndEmptyBatch() async throws {
    let ws = try TestWorkspace(); let service = AuditService(scope: try FileScope(ws.root.path), backend: FakeBackend(degraded: true))
    #expect(try await service.batch(".", options: ScanOptions())["status"]?.string == "empty")
    _ = try ws.image()
    let permissive = await service.scan("image.png", options: ScanOptions())
    #expect(permissive["status"]?.string == "degraded")
    #expect(permissive["strictFailure"]?.boolean == false)
    let strict = await service.scan("image.png", options: ScanOptions(strict: true))
    #expect(strict["strictFailure"]?.boolean == true)
}

@Test func batchLimit() throws {
    let ws = try TestWorkspace()
    for i in 0..<129 { try Data().write(to: ws.root.appendingPathComponent("\(i).png")) }
    #expect(throws: (any Error).self) { try FileScope(ws.root.path).batch(".") }
}

@Test func oversizedAndSpecialFilesAreRejected() throws {
    let ws = try TestWorkspace(); let scope = try FileScope(ws.root.path)
    let large = ws.root.appendingPathComponent("large.png")
    try Data().write(to: large)
    let handle = try FileHandle(forWritingTo: large)
    try handle.truncate(atOffset: UInt64(FileScope.byteLimit + 1)); try handle.close()
    #expect(throws: (any Error).self) { try scope.read(large.path) }
    let fifo = ws.root.appendingPathComponent("fifo.png")
    #expect(mkfifo(fifo.path, 0o600) == 0)
    #expect(throws: (any Error).self) { try scope.read(fifo.path) }
    #expect(throws: (any Error).self) { try FileScope("") }
}

@Test func mcpLifecycleAndErrors() async throws {
    let ws = try TestWorkspace(); _ = try ws.image()
    let backend = FakeBackend()
    let server = MCPServer(service: AuditService(scope: try FileScope(ws.root.path), backend: backend))
    func call(_ text: String) async -> JSON? { await server.handle(Data(text.utf8)) }
    #expect(await call("{")?["error"]?["code"]?.number == -32700)
    #expect(await call("[]")?["error"]?["code"]?.number == -32600)
    #expect(await call(#"{"jsonrpc":"2.0","id":1,"method":"tools/list"}"#)?["error"]?["code"]?.number == -32002)
    let initReply = await call(#"{"jsonrpc":"2.0","id":"init","method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"tests","version":"1"}}}"#)
    #expect(initReply?["result"]?["protocolVersion"]?.string == MCPServer.version)
    #expect(await call(#"{"jsonrpc":"2.0","method":"notifications/initialized"}"#) == nil)
    let tools = await call(#"{"jsonrpc":"2.0","id":2,"method":"tools/list"}"#)
    if case .array(let list) = tools?["result"]?["tools"] { #expect(list.count == 2) } else { Issue.record("Missing tool list") }
    #expect(await call(#"{"jsonrpc":"2.0","id":3,"method":"other"}"#)?["error"]?["code"]?.number == -32601)
    #expect(await call(#"{"jsonrpc":"2.0","method":"other"}"#) == nil)
    #expect(await call(#"{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"audit_screenshot","arguments":{"imagePath":"image.png","ocr":"yes"}}}"#)?["error"]?["code"]?.number == -32602)
    let good = await call(#"{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"audit_screenshot","arguments":{"imagePath":"image.png"}}}"#)
    #expect(good?["result"]?["isError"]?.boolean == false)
    let escape = await call(#"{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"audit_screenshot","arguments":{"imagePath":"../secret.png"}}}"#)
    #expect(escape?["result"]?["isError"]?.boolean == true)
    #expect(await backend.calls == 1)
}

@Test func artifactIdentityIsDeterministicAndRejectsAbsent() throws {
    let ws = try TestWorkspace()
    #expect(throws: (any Error).self) { try ArtifactIdentity.measure(ws.root, modelID: "empty") }
    try Data("weight".utf8).write(to: ws.root.appendingPathComponent("model.bin"))
    let a = try ArtifactIdentity.measure(ws.root, modelID: "test")
    let b = try ArtifactIdentity.measure(ws.root, modelID: "test")
    #expect(a.treeSHA256 == b.treeSHA256)
    try Data("changed".utf8).write(to: ws.root.appendingPathComponent("model.bin"))
    #expect(try ArtifactIdentity.measure(ws.root, modelID: "test").treeSHA256 != a.treeSHA256)
}
