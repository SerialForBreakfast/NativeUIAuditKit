#if os(macOS)
import Foundation
import Testing
@testable import NativeUIAuditKitRuntime

@Suite("Model selection lifecycle", .serialized)
struct NativeModelSelectionTests {
    // These records test storage behavior. They do not represent loadable Core ML models.
    func prepared() throws -> (URL, NativeModelCompiler, [NativeModelSelection.Entry]) {
        let support = NativeModelInstallerTests()
        let root = try support.root(), compiler = try support.compiler()
        var entries: [NativeModelSelection.Entry] = []
        for byte in UInt8(1)...3 {
            let archive = try support.archive([("model.mlpackage/item", Data([byte]))])
            let entry = NativeModelSelection.Entry(archive: archive, sourceName: "model.mlpackage")
            let folder = root.appendingPathComponent(entry.identity)
            let source = folder.appendingPathComponent("payload/model.mlpackage")
            let compiled = folder.appendingPathComponent("model.mlmodelc")
            try FileManager.default.createDirectory(at: source, withIntermediateDirectories: true)
            try FileManager.default.createDirectory(at: compiled, withIntermediateDirectories: true)
            try Data([byte]).write(to: source.appendingPathComponent("item"))
            try Data([byte, 7]).write(to: compiled.appendingPathComponent("item"))
            let receipt = try NativeModelInstaller.Receipt(schemaVersion: 2, state: .ready,
                archiveSHA256: entry.identity, sourceDigest: NativeUILocalDetector.digest(at: source),
                compiledDigest: NativeUILocalDetector.digest(at: compiled), host: NativeModelInstaller.hostIdentity,
                sourceName: entry.sourceName, compilerDigest: compiler.expectedDigest)
            try JSONEncoder().encode(receipt).write(to: folder.appendingPathComponent("receipt.json"))
            entries.append(entry)
        }
        return (root, compiler, entries)
    }

    @Test func selectionRollbackAndRestartUseVerifiedRecords() async throws {
        let (root, compiler, entries) = try prepared()
        let store = try NativeModelSelection(root: root, compiler: compiler, entries: entries)
        await #expect(throws: NativeModelSelection.Failure.self) { try await store.activate(entries[0].identity) }
        try await store.restore()
        await #expect(throws: NativeModelSelection.Failure.self) {
            try await store.withSelectedModel { _ in 1 }
        }
        try await store.activate(entries[0].identity)
        try await store.activate(entries[1].identity)
        #expect(await store.current().previous == entries[0].identity)
        try await store.rollback()
        #expect(await store.current().active == entries[0].identity)
        await #expect(throws: NativeModelSelection.Failure.self) { try await store.activate("unknown") }
        #expect(await store.current().active == entries[0].identity)
        let record = root.appendingPathComponent("selection.json")
        let saved = try Data(contentsOf: record)
        try await store.restore()
        #expect(await store.current().active == entries[0].identity)
        try Data("{\"schemaVersion\":99}".utf8).write(to: record)
        await #expect(throws: (any Error).self) { try await store.restore() }
        await #expect(throws: (any Error).self) { try await store.withSelectedModel { _ in 1 } }
        try saved.write(to: record)
        try await store.restore()
        let removed = try await store.remove(entries[2].identity)
        #expect(FileManager.default.fileExists(atPath: removed.appendingPathComponent("model.mlmodelc/item").path))
        #expect(!FileManager.default.fileExists(atPath: root.appendingPathComponent(entries[2].identity).path))
        await #expect(throws: (any Error).self) { try await store.activate(entries[2].identity) }
        #expect(await store.current().active == entries[0].identity)
    }

    @Test func activePreviousAndInFlightModelsCannotBeRemoved() async throws {
        let (root, compiler, entries) = try prepared()
        let store = try NativeModelSelection(root: root, compiler: compiler, entries: entries)
        try await store.restore()
        try await store.activate(entries[0].identity)
        let gate = OperationGate()
        let request = Task {
            try await store.withSelectedModel { url in
                await gate.enter()
                return try Data(contentsOf: url.appendingPathComponent("item"))
            }
        }
        await gate.waitForEntry()
        try await store.activate(entries[1].identity)
        await #expect(throws: NativeModelSelection.Failure.self) { try await store.remove(entries[0].identity) }
        await #expect(throws: NativeModelSelection.Failure.self) { try await store.remove(entries[1].identity) }
        try await store.releasePrevious()
        await #expect(throws: NativeModelSelection.Failure.self) { try await store.remove(entries[0].identity) }
        await gate.release()
        #expect(try await request.value == Data([1, 7]))
        _ = try await store.remove(entries[0].identity)
        try await store.deactivate()
        await #expect(throws: NativeModelSelection.Failure.self) { try await store.withSelectedModel { _ in 1 } }
        await #expect(throws: NativeModelSelection.Failure.self) { try await store.remove(entries[1].identity) }
        try await store.rollback()
        #expect(await store.current().active == entries[1].identity)
    }

    @Test func cancellationReleasesUseAndFailedActivationPreservesSelection() async throws {
        let (root, compiler, entries) = try prepared()
        let store = try NativeModelSelection(root: root, compiler: compiler, entries: entries)
        try await store.restore()
        try await store.activate(entries[0].identity)
        let original = try Data(contentsOf: root.appendingPathComponent("selection.json"))
        try Data([9]).write(to: root.appendingPathComponent(entries[1].identity + "/model.mlmodelc/item"))
        await #expect(throws: (any Error).self) { try await store.activate(entries[1].identity) }
        #expect(try Data(contentsOf: root.appendingPathComponent("selection.json")) == original)
        await #expect(throws: CancellationError.self) {
            try await store.withSelectedModel { _ in throw CancellationError() }
        }
        try await store.deactivate()
        try await store.releasePrevious()
        _ = try await store.remove(entries[0].identity)
    }

    @Test func secondWriterAndReplacedLockAreRejected() async throws {
        let (root, compiler, entries) = try prepared()
        let store = try NativeModelSelection(root: root, compiler: compiler, entries: entries)
        #expect(throws: NativeModelSelection.Failure.self) {
            try NativeModelSelection(root: root, compiler: compiler, entries: entries)
        }
        try await store.restore()
        let path = root.appendingPathComponent("selection.lock")
        try FileManager.default.moveItem(at: path, to: root.appendingPathComponent("old-lock"))
        try Data().write(to: path)
        await #expect(throws: NativeModelSelection.Failure.self) { try await store.activate(entries[0].identity) }
    }

    @Test func newStoreRestoresSelectionAndWriteFailurePreservesMemory() async throws {
        let (root, compiler, entries) = try prepared()
        func firstSession() async throws {
            let store = try NativeModelSelection(root: root, compiler: compiler, entries: entries)
            try await store.restore()
            try await store.activate(entries[0].identity)
        }
        try await firstSession()
        let restarted = try NativeModelSelection(root: root, compiler: compiler, entries: entries)
        try await restarted.restore()
        #expect(await restarted.current().active == entries[0].identity)
        let record = root.appendingPathComponent("selection.json")
        try FileManager.default.moveItem(at: record, to: root.appendingPathComponent("saved-selection.json"))
        try FileManager.default.createDirectory(at: record, withIntermediateDirectories: false)
        // A nonempty directory makes the atomic file replacement fail without permission changes.
        try Data([1]).write(to: record.appendingPathComponent("marker"))
        await #expect(throws: (any Error).self) { try await restarted.activate(entries[1].identity) }
        #expect(await restarted.current().active == entries[0].identity)
    }
}

private actor OperationGate {
    private var entered = false
    private var started: CheckedContinuation<Void, Never>?
    private var finish: CheckedContinuation<Void, Never>?
    func enter() async {
        entered = true
        started?.resume()
        started = nil
        await withCheckedContinuation { finish = $0 }
    }
    func waitForEntry() async {
        if entered { return }
        await withCheckedContinuation { started = $0 }
    }
    func release() { finish?.resume(); finish = nil }
}
#endif
