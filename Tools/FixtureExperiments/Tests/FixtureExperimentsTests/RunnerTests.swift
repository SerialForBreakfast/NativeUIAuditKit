import XCTest
import Foundation
import CoreGraphics
import ImageIO
import Darwin
@testable import FixtureExperiments

final class RunnerTests: XCTestCase {
    var root: URL!
    var bundle: URL!
    var hostFile: URL!
    var source: URL!
    let identity = String(repeating: "a", count: 64)

    override func setUpWithError() throws {
        guard let location = ProcessInfo.processInfo.environment["FIXTURE_EXPERIMENT_TEST_ROOT"] else {
            throw XCTSkip("Set FIXTURE_EXPERIMENT_TEST_ROOT to an approved test directory.")
        }
        root = URL(fileURLWithPath: location).appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)
        bundle = root.appendingPathComponent("bundle"); source = root.appendingPathComponent("renderer.swift")
        try Data("// Test source".utf8).write(to: source)
        try makeReference(at: bundle, rendererSourceSHA256: fileDigest(source))
        let workspace = root.appendingPathComponent("workspace")
        try FileManager.default.createDirectory(at: workspace, withIntermediateDirectories: false)
        var host = Host(workspace: workspace.path, renderer: "/usr/bin/true", rendererSHA256: try fileDigest(URL(fileURLWithPath: "/usr/bin/true")),
                        rendererSource: source.path, rendererSourceSHA256: try fileDigest(source))
        host.maxLoad = 10000
        hostFile = root.appendingPathComponent("host.json"); try write(host, hostFile)
    }

    override func tearDownWithError() throws { if let root { try FileManager.default.removeItem(at: root) } }
    func runner() throws -> Runner { try Runner(bundle: bundle, hostFile: hostFile, runnerIdentity: identity) }

    func mutate(_ update: (inout Experiment) -> Void) throws {
        let file = bundle.appendingPathComponent("experiment.json")
        var e = try read(Experiment.self, file); update(&e); try write(e, file, replace: true)
    }

    func testReferenceAndRelocation() throws {
        XCTAssertEqual(try validateBundle(bundle).jobs.count, 4)
        let copy = root.appendingPathComponent("unrelated-name")
        try FileManager.default.copyItem(at: bundle, to: copy)
        XCTAssertEqual(try fileDigest(bundle.appendingPathComponent("experiment.json")), try fileDigest(copy.appendingPathComponent("experiment.json")))
        XCTAssertEqual(try validateBundle(copy).jobs, try validateBundle(bundle).jobs)
    }

    func testUnknownVersion() throws {
        try mutate { $0.schema = "future" }; XCTAssertThrowsError(try validateBundle(bundle))
    }

    func testNativeAdapterRefused() throws {
        try mutate { $0.adapter = "native-hcf" }; XCTAssertThrowsError(try validateBundle(bundle))
    }

    func testTrainingRoleRefused() throws {
        try mutate { $0.trainingEligible = true }; XCTAssertThrowsError(try validateBundle(bundle))
    }

    func testChangedAsset() throws {
        try Data("changed".utf8).write(to: bundle.appendingPathComponent("expected.json"))
        XCTAssertThrowsError(try validateBundle(bundle))
    }

    func testUndeclaredFile() throws {
        try Data().write(to: bundle.appendingPathComponent("surprise"))
        XCTAssertThrowsError(try validateBundle(bundle))
    }

    func testSymlink() throws {
        try FileManager.default.createSymbolicLink(at: bundle.appendingPathComponent("assets/link"), withDestinationURL: source)
        XCTAssertThrowsError(try validateBundle(bundle))
    }

    func testTraversal() throws {
        XCTAssertThrowsError(try safePath(root, "../outside"))
        XCTAssertThrowsError(try safePath(root, "/absolute"))
        XCTAssertThrowsError(try safePath(root, "a//b"))
    }

    func testCollision() throws { XCTAssertThrowsError(try makeReference(at: bundle, rendererSourceSHA256: identity)) }

    func testChangedHostSource() throws {
        try Data("new".utf8).write(to: source)
        XCTAssertThrowsError(try runner())
    }

    func testResourceDeferral() throws {
        var host = try read(Host.self, hostFile); host.minFreeBytes = Int64.max
        try write(host, hostFile, replace: true)
        XCTAssertEqual(try runner().run().state, "deferred_resources")
    }

    func testSharedLock() throws {
        let r = try runner(); let file = r.workspace.appendingPathComponent(".authored-renderer.lock")
        do {
            let held = try ResourceLock(file)
            defer { withExtendedLifetime(held) {} }
            XCTAssertThrowsError(try r.run())
        }
        XCTAssertNoThrow(try ResourceLock(file))
    }

    func testFailedOutputRequiresExplicitRetryAndLimit() throws {
        let r = try runner()
        XCTAssertEqual(try r.run().state, "failed")
        XCTAssertEqual(try r.run().reason, "explicit_retry_required")
        XCTAssertEqual(try r.run(retryFailed: true).state, "failed")
        XCTAssertEqual(try r.run(retryFailed: true).reason, "attempt_limit")
        XCTAssertEqual(try r.checkpoint().jobs["shelf"]?.attempts.count, 2)
    }

    func testInterruptedStateRequiresReconcile() throws {
        let r = try runner(); var s = try r.checkpoint(create: true)
        s.jobs["shelf"] = JobState(state: "running", attempts: [UUID().uuidString.lowercased()])
        try r.persist(s)
        XCTAssertEqual(try r.run().state, "needs_reconciliation")
        XCTAssertEqual(try r.reconcile().state, "ready")
        XCTAssertEqual(try r.run().reason, "explicit_retry_required")
    }

    func testCancelAndExplicitClear() throws {
        let r = try runner(); _ = try r.checkpoint(create: true)
        XCTAssertEqual(try r.cancel().state, "cancel_requested")
        XCTAssertEqual(try r.run().state, "cancelled")
        XCTAssertEqual(try r.run(clearCancel: true).state, "failed")
        XCTAssertFalse(FileManager.default.fileExists(atPath: r.campaign.appendingPathComponent("STOP").path))
    }

    func testChangedCheckpointIdentity() throws {
        let r = try runner(); var s = try r.checkpoint(create: true); s.runnerSHA256 = "wrong"
        try r.persist(s); XCTAssertThrowsError(try r.run())
    }

    func testTimeoutAndCancelReapChild() throws {
        let start = Date()
        XCTAssertThrowsError(try execute("/bin/sleep", arguments: ["10"], log: root.appendingPathComponent("timeout.log"),
                                        tmp: root, seconds: 0.1, shouldStop: { nil })) {
            XCTAssertEqual(String(describing: $0), "operation_timeout")
        }
        XCTAssertLessThan(Date().timeIntervalSince(start), 5)
        XCTAssertThrowsError(try execute("/bin/sleep", arguments: ["10"], log: root.appendingPathComponent("cancel.log"),
                                        tmp: root, seconds: 10, shouldStop: { "cancelled" })) {
            XCTAssertEqual(String(describing: $0), "cancelled")
        }
    }

    func testOutputLimit() throws {
        XCTAssertThrowsError(try execute("/bin/sleep", arguments: ["10"], log: root.appendingPathComponent("limit.log"),
                                        tmp: root, seconds: 10, shouldStop: { "output_limit" })) {
            XCTAssertEqual(String(describing: $0), "output_limit")
        }
    }

    func testCorruptPNG() throws {
        let path = root.appendingPathComponent("bad.png"); try Data("bad".utf8).write(to: path)
        XCTAssertThrowsError(try pixelHash(path))
    }

    func testCancellationAfterInputChange() throws {
        let r = try runner(); _ = try r.checkpoint(create: true)
        try Data("changed".utf8).write(to: source)
        XCTAssertEqual(try requestCancellation(workspace: r.workspace, experimentID: "hcf336-reference").state, "cancel_requested")
    }

    func testPreflightDoesNotCreateCampaign() throws {
        let r = try runner(); XCTAssertEqual(try r.preflight().state, "ready")
        XCTAssertFalse(FileManager.default.fileExists(atPath: r.campaign.path))
    }

    func testRenderValidationAndMissingPNG() throws {
        let folder = root.appendingPathComponent("output")
        try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: false)
        for (name, shade) in [("grid_unfocused.png", 0.0), ("grid_focused_cell.png", 1.0)] {
            let ctx = CGContext(data: nil, width: 1920, height: 1080, bitsPerComponent: 8, bytesPerRow: 1920 * 4,
                                space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
            ctx.setFillColor(CGColor(gray: shade, alpha: 1)); ctx.fill(CGRect(x: 0, y: 0, width: 1920, height: 1080))
            let destination = CGImageDestinationCreateWithURL(folder.appendingPathComponent(name) as CFURL, "public.png" as CFString, 1, nil)!
            CGImageDestinationAddImage(destination, ctx.makeImage()!, nil); XCTAssertTrue(CGImageDestinationFinalize(destination))
        }
        let annotation: [String: Any] = ["schemaVersion": "contract-v1-headless-focus", "layoutType": "grid",
            "canvasWidth": 1920, "canvasHeight": 1080, "focusedNodeID": "cell",
            "nodes": [["id": "cell", "isFocused": true, "unfocusedBounds": [10, 10, 100, 100], "focusedBounds": [5, 5, 110, 110]]],
            "unfocusedImageSHA256": try fileDigest(folder.appendingPathComponent("grid_unfocused.png")),
            "focusedImageSHA256": try fileDigest(folder.appendingPathComponent("grid_focused_cell.png"))]
        try JSONSerialization.data(withJSONObject: annotation).write(to: folder.appendingPathComponent("grid_annotations.json"))
        let job = Job(id: "grid", layout: "grid", ancestry: "test")
        XCTAssertEqual(try validateRender(folder, job: job).files.count, 3)
        XCTAssertThrowsError(try validateRender(folder, job: Job(id: "grid", layout: "grid", focusID: "wrong", ancestry: "test")))
        try FileManager.default.removeItem(at: folder.appendingPathComponent("grid_unfocused.png"))
        XCTAssertThrowsError(try validateRender(folder, job: job))
    }
}
