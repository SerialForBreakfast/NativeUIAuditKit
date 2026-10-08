#if os(macOS)
import Darwin
import Foundation

/// Internal selection store. The host supplies the trusted archives and owns storage access.
actor NativeModelSelection {
    enum Failure: Error { case busy, unknownArtifact, invalidState, unavailable, inUse, protectedVersion }
    struct Entry: Sendable {
        let archive: ModelArchive
        let sourceName: String
        var identity: String { ModelArchive.hash(archive.bytes) }
    }
    struct Selection: Codable, Sendable, Equatable {
        let schemaVersion: Int
        let active: String?
        let previous: String?
    }
    private let root: URL
    private let installer: NativeModelInstaller
    private let entries: [String: Entry]
    private let writer: NativeModelSelectionLock
    private var selection = Selection(schemaVersion: 1, active: nil, previous: nil)
    private var restored = false
    private var changing = false
    private var users: [String: Int] = [:]

    init(root: URL, compiler: NativeModelCompiler, entries: [Entry]) throws {
        self.installer = try NativeModelInstaller(root: root, compiler: compiler)
        self.root = root.standardizedFileURL
        var catalog: [String: Entry] = [:]
        for entry in entries {
            guard catalog.updateValue(entry, forKey: entry.identity) == nil else { throw Failure.invalidState }
        }
        self.entries = catalog
        self.writer = try NativeModelSelectionLock(root: root)
    }

    func current() -> Selection { selection }

    /// Restore only selections whose installations still pass all checks.
    func restore() async throws {
        guard !changing, users.isEmpty else { throw Failure.busy }
        changing = true
        defer { changing = false }
        restored = false
        selection = Selection(schemaVersion: 1, active: nil, previous: nil)
        let record = root.appendingPathComponent("selection.json")
        let candidate: Selection
        try checkRoot()
        if FileManager.default.fileExists(atPath: record.path) {
            let info = try record.resourceValues(forKeys: [.isRegularFileKey, .isSymbolicLinkKey, .fileSizeKey])
            guard info.isRegularFile == true, info.isSymbolicLink != true,
                  let bytes = info.fileSize, bytes <= 16_384 else { throw Failure.invalidState }
            candidate = try JSONDecoder().decode(Selection.self, from: Data(contentsOf: record))
            guard candidate.schemaVersion == 1, candidate.previous == nil || candidate.active != candidate.previous else {
                throw Failure.invalidState
            }
        } else {
            candidate = Selection(schemaVersion: 1, active: nil, previous: nil)
        }
        for identity in [candidate.active, candidate.previous].compactMap({ $0 }) {
            _ = try await checkedURL(identity)
        }
        try Task.checkCancellation()
        selection = candidate
        restored = true
    }

    func activate(_ identity: String) async throws {
        try beginChange()
        defer { changing = false }
        _ = try await checkedURL(identity)
        try Task.checkCancellation()
        if selection.active == identity { return }
        try save(Selection(schemaVersion: 1, active: identity, previous: selection.active))
    }

    func rollback() async throws {
        try beginChange()
        defer { changing = false }
        guard let previous = selection.previous else { throw Failure.unavailable }
        _ = try await checkedURL(previous)
        try Task.checkCancellation()
        try save(Selection(schemaVersion: 1, active: previous, previous: selection.active))
    }

    /// Disable later calls. Existing calls keep their protected selection until they return.
    func deactivate() throws {
        try beginChange()
        defer { changing = false }
        try save(Selection(schemaVersion: 1, active: nil, previous: selection.active ?? selection.previous))
    }

    /// The host must explicitly release the retained rollback selection before removal.
    func releasePrevious() throws {
        try beginChange()
        defer { changing = false }
        try save(Selection(schemaVersion: 1, active: selection.active, previous: nil))
    }

    /// Keep the installation protected throughout loading and inference, including cancellation cleanup.
    func withSelectedModel<T: Sendable>(_ operation: @Sendable (URL) async throws -> T) async throws -> T {
        guard restored, !changing else { throw Failure.busy }
        guard let identity = selection.active else { throw Failure.unavailable }
        users[identity, default: 0] += 1
        defer {
            users[identity, default: 1] -= 1
            if users[identity] == 0 { users.removeValue(forKey: identity) }
        }
        let url = try await checkedURL(identity)
        try Task.checkCancellation()
        return try await operation(url)
    }

    /// Move an unused installation out of service. Preserve its bytes for explicit host cleanup.
    func remove(_ identity: String) async throws -> URL {
        try beginChange()
        defer { changing = false }
        guard identity != selection.active, identity != selection.previous else { throw Failure.protectedVersion }
        guard users[identity, default: 0] == 0 else { throw Failure.inUse }
        let compiled = try await checkedURL(identity)
        try Task.checkCancellation()
        try checkRoot()
        let destination = root.appendingPathComponent("removed-" + identity + "-" + UUID().uuidString)
        try FileManager.default.moveItem(at: compiled.deletingLastPathComponent(), to: destination)
        return destination
    }

    private func beginChange() throws {
        guard restored, !changing else { throw Failure.busy }
        try checkRoot()
        changing = true
    }

    private func checkedURL(_ identity: String) async throws -> URL {
        guard let entry = entries[identity] else { throw Failure.unknownArtifact }
        try checkRoot()
        return try await installer.recover(archive: entry.archive, sourceName: entry.sourceName)
    }

    private func checkRoot() throws {
        guard root.path == root.resolvingSymlinksInPath().path else { throw Failure.invalidState }
        try writer.check()
    }

    private func save(_ value: Selection) throws {
        try Task.checkCancellation()
        try checkRoot()
        try JSONEncoder().encode(value).write(to: root.appendingPathComponent("selection.json"), options: .atomic)
        selection = value
    }
}

/// Hold one writer per storage root. The OS releases the lock when the process exits.
private final class NativeModelSelectionLock: Sendable {
    let descriptor: Int32
    let path: String
    init(root: URL) throws {
        path = root.appendingPathComponent("selection.lock").path
        let fd = path.withCString { Darwin.open($0, O_RDWR | O_CREAT | O_NOFOLLOW | O_CLOEXEC, 0o600) }
        guard fd >= 0 else { throw NativeModelSelection.Failure.invalidState }
        guard flock(fd, LOCK_EX | LOCK_NB) == 0 else {
            Darwin.close(fd)
            throw NativeModelSelection.Failure.busy
        }
        do { try Self.check(fd, path) } catch { Darwin.close(fd); throw error }
        descriptor = fd
    }
    func check() throws {
        try Self.check(descriptor, path)
    }
    private static func check(_ descriptor: Int32, _ path: String) throws {
        var owned = stat(), current = stat()
        guard fstat(descriptor, &owned) == 0, lstat(path, &current) == 0,
              owned.st_ino == current.st_ino, owned.st_dev == current.st_dev,
              current.st_mode & S_IFMT == S_IFREG else { throw NativeModelSelection.Failure.invalidState }
    }
    deinit { Darwin.close(descriptor) }
}
#endif
