import Foundation
import ImageIO
import CoreGraphics
import Darwin

struct Node: Decodable {
    let id: String
    let isFocused: Bool
    let unfocusedBounds: [Double]
    let focusedBounds: [Double]
}

struct Annotation: Decodable {
    let schemaVersion: String
    let layoutType: String
    let canvasWidth: Int
    let canvasHeight: Int
    let focusedNodeID: String
    let nodes: [Node]
    let unfocusedImageSHA256: String
    let focusedImageSHA256: String
}

public struct ResultReceipt: Codable {
    public let schema: String
    public let jobID: String
    public let ancestry: String
    public let attemptID: String
    public let files: [Artifact]
    public let decodedPixelHashes: [String]
    public let width: Int
    public let height: Int
    public let focusID: String
    public let sourceDomain: String
    public let dataRole: String
    public let trainingEligible: Bool
    public let rendererSHA256: String
    public let rendererSourceSHA256: String
    public let runnerSHA256: String
    public let operatingSystem: String
    public let renderSeconds: Double
    public let validationSeconds: Double
    public let totalSeconds: Double
    public let cleanup: String
}

public struct JobState: Codable {
    public var state: String
    public var attempts: [String]
    public var receiptSHA256: String?
    public var error: String?
}

public struct Checkpoint: Codable {
    public var schema = "fixture-checkpoint-v1"
    public var experimentSHA256: String
    public var hostSHA256: String
    public var runnerSHA256: String
    public var state: String
    public var jobs: [String: JobState]
    public var error: String?
}

public struct OperationResult: Codable {
    public let state: String
    public let reason: String?
    public let completed: Int
    public let total: Int
    public var exitCode: Int32 {
        switch state {
        case "complete", "valid", "ready", "cancel_requested": return 0
        case "deferred_resources", "paused_batch": return 75
        case "cancelled": return 130
        case "needs_reconciliation": return 76
        default: return 1
        }
    }
}

/// Cancellation does not require intact renderer or bundle inputs.
public func requestCancellation(workspace: URL, experimentID: String) throws -> OperationResult {
    try require(validID(experimentID), "invalid_identity")
    try noLinks(workspace)
    let campaign = try safePath(workspace, experimentID)
    let state = try read(Checkpoint.self, campaign.appendingPathComponent("checkpoint.json"))
    try require(state.schema == "fixture-checkpoint-v1", "unsupported_checkpoint")
    let path = campaign.appendingPathComponent("STOP"); try noLinks(path)
    if !FileManager.default.fileExists(atPath: path.path) { try Data().write(to: path, options: .withoutOverwriting) }
    return OperationResult(state: "cancel_requested", reason: nil,
                           completed: state.jobs.values.filter { $0.state == "complete" }.count, total: state.jobs.count)
}

final class ResourceLock {
    let fd: Int32
    init(_ url: URL) throws {
        try noLinks(url)
        fd = open(url.path, O_CREAT | O_RDWR | O_NOFOLLOW, 0o600)
        try require(fd >= 0, "lock_open_failed")
        if flock(fd, LOCK_EX | LOCK_NB) != 0 { close(fd); throw ExperimentError("resource_busy") }
        // The renderer inherits this descriptor until it exits.
        _ = fcntl(fd, F_SETFD, 0)
    }
    deinit { close(fd) }
}

func pixelHash(_ url: URL) throws -> String {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          CGImageSourceGetType(source) as String? == "public.png",
          let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [CFString: Any],
          properties[kCGImagePropertyPixelWidth] as? Int == 1920,
          properties[kCGImagePropertyPixelHeight] as? Int == 1080,
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else { throw ExperimentError("invalid_png") }
    try require(image.width == 1920 && image.height == 1080, "wrong_dimensions")
    var bytes = [UInt8](repeating: 0, count: 1920 * 1080 * 4)
    try bytes.withUnsafeMutableBytes { buffer in
        guard let space = CGColorSpace(name: CGColorSpace.sRGB),
              let context = CGContext(data: buffer.baseAddress, width: 1920, height: 1080, bitsPerComponent: 8,
                  bytesPerRow: 1920 * 4, space: space,
                  bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue | CGBitmapInfo.byteOrder32Big.rawValue)
        else { throw ExperimentError("decode_failed") }
        context.draw(image, in: CGRect(x: 0, y: 0, width: 1920, height: 1080))
    }
    return digest(Data(bytes))
}

func validateRender(_ folder: URL, job: Job) throws -> (files: [Artifact], pixels: [String], focus: String) {
    let annotationName = job.layout + "_annotations.json"
    let a = try read(Annotation.self, folder.appendingPathComponent(annotationName))
    try require(a.schemaVersion == "contract-v1-headless-focus" && a.layoutType == job.layout &&
                a.canvasWidth == 1920 && a.canvasHeight == 1080 && validID(a.focusedNodeID), "render_contract")
    try require(!a.nodes.isEmpty && a.nodes.count <= 256 && Set(a.nodes.map(\.id)).count == a.nodes.count, "invalid_nodes")
    try require(a.nodes.filter(\.isFocused).map(\.id) == [a.focusedNodeID], "ambiguous_focus")
    if let expected = job.focusID { try require(expected == a.focusedNodeID, "wrong_focus") }
    for node in a.nodes {
        for bounds in [node.unfocusedBounds, node.focusedBounds] {
            try require(bounds.count == 4 && bounds.allSatisfy(\.isFinite) && bounds[2] > 0 && bounds[3] > 0, "invalid_bounds")
        }
    }
    let before = job.layout + "_unfocused.png"
    let after = job.layout + "_focused_" + a.focusedNodeID + ".png"
    let files = try inventory(folder)
    try require(Set(files.map(\.path)) == [annotationName, before, after], "unexpected_output")
    try require(try fileDigest(folder.appendingPathComponent(before)) == a.unfocusedImageSHA256, "image_hash_mismatch")
    try require(try fileDigest(folder.appendingPathComponent(after)) == a.focusedImageSHA256, "image_hash_mismatch")
    let pixels = try [pixelHash(folder.appendingPathComponent(before)), pixelHash(folder.appendingPathComponent(after))]
    try require(pixels[0] != pixels[1], "no_visible_effect")
    return (files, pixels, a.focusedNodeID)
}

func outputSize(_ root: URL) throws -> Int64 {
    guard let walker = FileManager.default.enumerator(at: root, includingPropertiesForKeys: nil) else { return 0 }
    var total: Int64 = 0; var count = 0
    for case let url as URL in walker {
        try noLinks(url)
        let attrs = try FileManager.default.attributesOfItem(atPath: url.path)
        count += 1; try require(count <= 10000, "output_file_limit")
        if attrs[.type] as? FileAttributeType == .typeRegular { total += (attrs[.size] as! NSNumber).int64Value }
        else { try require(attrs[.type] as? FileAttributeType == .typeDirectory, "special_output") }
    }
    return total
}

// This adapter launches a pinned executable without a shell or arbitrary job commands.
func execute(_ executable: String, arguments: [String], log: URL, tmp: URL, seconds: Double,
             shouldStop: () throws -> String?) throws {
    let logFD = open(log.path, O_CREAT | O_EXCL | O_WRONLY | O_NOFOLLOW, 0o600)
    try require(logFD >= 0, "log_collision")
    defer { close(logFD) }
    var actions: posix_spawn_file_actions_t?; var attributes: posix_spawnattr_t?
    posix_spawn_file_actions_init(&actions); posix_spawnattr_init(&attributes)
    defer { posix_spawn_file_actions_destroy(&actions); posix_spawnattr_destroy(&attributes) }
    posix_spawn_file_actions_addopen(&actions, STDIN_FILENO, "/dev/null", O_RDONLY, 0)
    posix_spawn_file_actions_adddup2(&actions, logFD, STDOUT_FILENO)
    posix_spawn_file_actions_adddup2(&actions, logFD, STDERR_FILENO)
    posix_spawnattr_setflags(&attributes, Int16(POSIX_SPAWN_SETPGROUP))
    posix_spawnattr_setpgroup(&attributes, 0)
    let argv = ([executable] + arguments).map { strdup($0) } + [nil]
    let environment = ["PATH=/usr/bin:/bin", "TMPDIR=\(tmp.path)", "OMP_NUM_THREADS=2", "OPENBLAS_NUM_THREADS=2"]
    let env = environment.map { strdup($0) } + [nil]
    defer { argv.forEach { free($0) }; env.forEach { free($0) } }
    var pid: pid_t = 0
    let code = argv.withUnsafeBufferPointer { av in env.withUnsafeBufferPointer { ev in
        posix_spawn(&pid, executable, &actions, &attributes, av.baseAddress!, ev.baseAddress!)
    }}
    try require(code == 0, "spawn_failed_\(code)")
    var reaped = false
    defer {
        if !reaped {
            _ = kill(-pid, SIGTERM)
            let deadline = Date().addingTimeInterval(3)
            var status: Int32 = 0
            while Date() < deadline {
                if waitpid(pid, &status, WNOHANG) == pid { reaped = true; break }
                Thread.sleep(forTimeInterval: 0.05)
            }
            if !reaped { _ = kill(-pid, SIGKILL); _ = waitpid(pid, &status, 0) }
        }
    }
    try require(setpriority(PRIO_PROCESS, UInt32(pid), 10) == 0 || errno == ESRCH, "priority_denied")
    let start = ProcessInfo.processInfo.systemUptime
    while true {
        var status: Int32 = 0
        let ended = waitpid(pid, &status, WNOHANG)
        if ended == pid {
            reaped = true
            try require(status == 0, "renderer_exit_\(status)")
            if let reason = try shouldStop() { throw ExperimentError(reason) }
            return
        }
        try require(ended >= 0, "wait_failed")
        if let reason = try shouldStop() { throw ExperimentError(reason) }
        try require(ProcessInfo.processInfo.systemUptime - start < seconds, "operation_timeout")
        Thread.sleep(forTimeInterval: 0.1)
    }
}

public final class Runner {
    public let bundle: URL
    public let host: Host
    public let campaign: URL
    let hostHash: String
    let runnerHash: String
    let workspace: URL
    let experiment: Experiment
    let experimentHash: String

    public init(bundle: URL, hostFile: URL, runnerIdentity: String) throws {
        self.bundle = bundle.standardizedFileURL
        experiment = try validateBundle(self.bundle)
        experimentHash = try fileDigest(self.bundle.appendingPathComponent("experiment.json"))
        host = try read(Host.self, hostFile); hostHash = try fileDigest(hostFile)
        try require(host.schema == "fixture-host-v1" && validHash(runnerIdentity), "invalid_host")
        try require(host.workspace.hasPrefix("/") && host.renderer.hasPrefix("/") && host.rendererSource.hasPrefix("/"), "host_paths_not_absolute")
        workspace = URL(fileURLWithPath: host.workspace).standardizedFileURL
        try noLinks(workspace)
        var isDir: ObjCBool = false
        try require(FileManager.default.fileExists(atPath: workspace.path, isDirectory: &isDir) && isDir.boolValue, "workspace_missing")
        try require(host.minFreeBytes >= experiment.limits.maxOutputBytes && host.maxLoad.isFinite && host.maxLoad > 0, "invalid_host_limits")
        try require(host.rendererSourceSHA256 == experiment.rendererSourceSHA256, "source_contract_mismatch")
        runnerHash = runnerIdentity
        campaign = workspace.appendingPathComponent(experiment.id)
        try noLinks(campaign)
        try checkHost()
    }

    func checkHost() throws {
        for (path, hash) in [(host.renderer, host.rendererSHA256), (host.rendererSource, host.rendererSourceSHA256)] {
            let url = URL(fileURLWithPath: path); try noLinks(url)
            try require(validHash(hash) && (try fileDigest(url)) == hash, "host_artifact_changed")
        }
        try require(FileManager.default.isExecutableFile(atPath: host.renderer), "renderer_not_executable")
    }

    func checkInputs() throws {
        try require(try fileDigest(bundle.appendingPathComponent("experiment.json")) == experimentHash, "experiment_changed")
        _ = try validateBundle(bundle)
        try checkHost()
    }

    func resourceReason() throws -> String? {
        let attrs = try FileManager.default.attributesOfFileSystem(forPath: workspace.path)
        if (attrs[.systemFreeSize] as! NSNumber).int64Value < host.minFreeBytes { return "insufficient_space" }
        var load: Double = 0
        try require(getloadavg(&load, 1) == 1, "load_unavailable")
        return load > host.maxLoad ? "host_busy" : nil
    }

    public func preflight() throws -> OperationResult {
        let reason = try resourceReason()
        return OperationResult(state: reason == nil ? "ready" : "deferred_resources", reason: reason, completed: 0, total: experiment.jobs.count)
    }

    func checkpoint(create: Bool = false) throws -> Checkpoint {
        let file = campaign.appendingPathComponent("checkpoint.json")
        if !FileManager.default.fileExists(atPath: campaign.path) && create {
            try FileManager.default.createDirectory(at: campaign, withIntermediateDirectories: false)
            let state = Checkpoint(experimentSHA256: experimentHash, hostSHA256: hostHash, runnerSHA256: runnerHash, state: "ready", jobs: [:])
            try write(state, file)
        }
        let value = try read(Checkpoint.self, file)
        try require(value.schema == "fixture-checkpoint-v1" && value.experimentSHA256 == experimentHash &&
                    value.hostSHA256 == hostHash && value.runnerSHA256 == runnerHash, "checkpoint_identity_changed")
        try require(Set(value.jobs.keys).isSubset(of: Set(experiment.jobs.map(\.id))), "unknown_checkpoint_job")
        return value
    }

    func persist(_ state: Checkpoint) throws { try write(state, campaign.appendingPathComponent("checkpoint.json"), replace: true) }

    func verifyCompleted(_ state: Checkpoint) throws {
        for (id, row) in state.jobs where row.state == "complete" {
            guard let attempt = row.attempts.last, validID(attempt), let expectedHash = row.receiptSHA256 else {
                throw ExperimentError("missing_receipt")
            }
            let root = try safePath(campaign, attempt)
            let path = root.appendingPathComponent("receipt.json")
            try require(try fileDigest(path) == expectedHash, "receipt_changed")
            let receipt = try read(ResultReceipt.self, path)
            try require(receipt.jobID == id && receipt.attemptID == attempt && receipt.sourceDomain == "authored_headless" &&
                        !receipt.trainingEligible && receipt.rendererSHA256 == host.rendererSHA256 && receipt.runnerSHA256 == runnerHash,
                        "receipt_identity")
            try require(try inventory(root.appendingPathComponent("output")) == receipt.files, "completed_output_changed")
        }
    }

    func result(_ state: Checkpoint) -> OperationResult {
        OperationResult(state: state.state, reason: state.error, completed: state.jobs.values.filter { $0.state == "complete" }.count,
                        total: experiment.jobs.count)
    }

    public func status() throws -> OperationResult { let s = try checkpoint(); try verifyCompleted(s); return result(s) }

    public func cancel() throws -> OperationResult {
        try requestCancellation(workspace: workspace, experimentID: experiment.id)
    }

    public func reconcile() throws -> OperationResult {
        let lock = try ResourceLock(workspace.appendingPathComponent(".authored-renderer.lock")); defer { withExtendedLifetime(lock) {} }
        var s = try checkpoint(); try verifyCompleted(s)
        for (id, row) in s.jobs where row.state == "running" {
            // No native operations exist in this adapter. Preserve uncertain output and require an explicit retry.
            var updated = row; updated.state = "interrupted"; updated.error = "interrupted_requires_retry"
            s.jobs[id] = updated
        }
        s.state = "ready"; s.error = nil; try persist(s); return result(s)
    }

    public func run(maxJobs: Int = 100, retryFailed: Bool = false, clearCancel: Bool = false) throws -> OperationResult {
        try require((1...100).contains(maxJobs), "invalid_batch_limit")
        let lock = try ResourceLock(workspace.appendingPathComponent(".authored-renderer.lock")); defer { withExtendedLifetime(lock) {} }
        var s = try checkpoint(create: true); try verifyCompleted(s)
        let stop = campaign.appendingPathComponent("STOP")
        if s.jobs.values.contains(where: { $0.state == "running" }) {
            s.state = "needs_reconciliation"; s.error = "previous_attempt_unresolved"; try persist(s); return result(s)
        }
        if clearCancel && FileManager.default.fileExists(atPath: stop.path) { try noLinks(stop); try FileManager.default.removeItem(at: stop) }
        if FileManager.default.fileExists(atPath: stop.path) {
            s.state = "cancelled"; s.error = nil; try persist(s); return result(s)
        }
        var finished = 0
        for job in experiment.jobs {
            var row = s.jobs[job.id] ?? JobState(state: "pending", attempts: [])
            if row.state == "complete" { continue }
            if FileManager.default.fileExists(atPath: stop.path) {
                s.state = "cancelled"; s.error = nil; try persist(s); return result(s)
            }
            if finished == maxJobs { s.state = "paused_batch"; s.error = nil; try persist(s); return result(s) }
            if !row.attempts.isEmpty && !retryFailed { s.state = "failed"; s.error = "explicit_retry_required"; try persist(s); return result(s) }
            if row.attempts.count >= experiment.limits.maxAttempts { s.state = "failed"; s.error = "attempt_limit"; try persist(s); return result(s) }
            if let reason = try resourceReason() { s.state = "deferred_resources"; s.error = reason; try persist(s); return result(s) }
            try require(try outputSize(campaign) < experiment.limits.maxOutputBytes, "output_limit")
            let attempt = UUID().uuidString.lowercased()
            let folder = try safePath(campaign, attempt)
            try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: false)
            try FileManager.default.createDirectory(at: folder.appendingPathComponent("tmp"), withIntermediateDirectories: false)
            row.state = "running"; row.attempts.append(attempt); row.error = nil
            s.jobs[job.id] = row; s.state = "running"; s.error = nil; try persist(s)
            let started = ProcessInfo.processInfo.systemUptime
            do {
                try checkInputs()
                var arguments = ["--layout", job.layout, "--resolution", "1080p", "--assets-dir", bundle.appendingPathComponent("assets").path,
                                 "--output-dir", folder.appendingPathComponent("output").path]
                if let focus = job.focusID { arguments += ["--focus-id", focus] }
                let renderStart = ProcessInfo.processInfo.systemUptime
                try execute(host.renderer, arguments: arguments, log: folder.appendingPathComponent("renderer.log"),
                            tmp: folder.appendingPathComponent("tmp"), seconds: experiment.limits.timeoutSeconds) {
                    if FileManager.default.fileExists(atPath: stop.path) { return "cancelled" }
                    if try outputSize(campaign) > self.experiment.limits.maxOutputBytes { return "output_limit" }
                    return nil
                }
                let renderSeconds = ProcessInfo.processInfo.systemUptime - renderStart
                let validationStart = ProcessInfo.processInfo.systemUptime
                try checkInputs()
                let validated = try validateRender(folder.appendingPathComponent("output"), job: job)
                let receipt = ResultReceipt(schema: "fixture-result-v1", jobID: job.id, ancestry: job.ancestry, attemptID: attempt,
                    files: validated.files, decodedPixelHashes: validated.pixels, width: 1920, height: 1080, focusID: validated.focus,
                    sourceDomain: "authored_headless", dataRole: "development", trainingEligible: false,
                    rendererSHA256: host.rendererSHA256, rendererSourceSHA256: host.rendererSourceSHA256, runnerSHA256: runnerHash,
                    operatingSystem: ProcessInfo.processInfo.operatingSystemVersionString, renderSeconds: renderSeconds,
                    validationSeconds: ProcessInfo.processInfo.systemUptime - validationStart,
                    totalSeconds: ProcessInfo.processInfo.systemUptime - started, cleanup: "owned_renderer_reaped_no_native_resources")
                let path = folder.appendingPathComponent("receipt.json"); try write(receipt, path)
                try require(try outputSize(campaign) <= experiment.limits.maxOutputBytes, "output_limit")
                row.state = "complete"; row.receiptSHA256 = try fileDigest(path); s.jobs[job.id] = row
                try persist(s); finished += 1
            } catch {
                row.state = "failed"; row.error = String(describing: error); s.jobs[job.id] = row
                s.state = row.error == "cancelled" ? "cancelled" : "failed"; s.error = row.error
                try write(["state": s.state, "error": s.error ?? "unknown", "attemptID": attempt], folder.appendingPathComponent("failure.json"))
                try persist(s); return result(s)
            }
        }
        s.state = "complete"; s.error = nil; try persist(s); return result(s)
    }
}
