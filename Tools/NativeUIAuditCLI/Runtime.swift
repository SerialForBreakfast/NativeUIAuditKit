import Foundation
import CoreGraphics
import NativeUIAuditKit
import NativeUIAuditKitModels

struct RuntimeScan: Encodable, Sendable {
    let detector: ArtifactIdentity
    let platform: String
    let cacheState: String
    let modelLoadMs: Double
    let result: NativeUIDetailedDetectionResult
}

protocol AuditBackend: Sendable {
    func doctor() async -> JSON
    func scan(_ image: CGImage, options: ScanOptions) async throws -> RuntimeScan
}

actor ProductionBackend: AuditBackend {
    struct Cached: Sendable {
        let session: NativeUIDetectionSession
        let identity: ArtifactIdentity
    }
    private var sessions: [ScanOptions: Cached] = [:]

    func doctor() -> JSON {
        var inventory: [JSON] = []
        for tv in [false, true] {
            do {
                let manifest = try NativeUIModelAsset.requiredManifest(forTVOS: tv)
                let url = try NativeUIModelAsset.requiredModelURL(forTVOS: tv)
                let identity = try ArtifactIdentity.measure(url, modelID: manifest.modelId)
                inventory.append(.object(["platform": .string(tv ? "tvOS" : "iOS"), "available": .bool(true),
                    "artifact": try .encoded(identity), "manifest": try .encoded(manifest),
                    "loadVerified": .bool(false), "trustedDigestComparison": .string("not_performed")]))
            } catch {
                inventory.append(.object(["platform": .string(tv ? "tvOS" : "iOS"), "available": .bool(false),
                    "error": AuditError.wrap(error).json]))
            }
        }
        let failed = inventory.contains { $0["available"]?.boolean == false }
        return .object(["schemaVersion": .number(1), "models": .array(inventory),
            "status": .string(failed ? "degraded" : "available_not_loaded"), "strictFailure": .bool(failed),
            "runtime": .string(ProcessInfo.processInfo.operatingSystemVersionString),
            "focusResourcePresent": .bool(NativeUIModelAsset.focusRingDetectorURL != nil),
                "hardwareDispatch": .string("not_observed"), "requestedComputeUnits": .string("all"),
            "inferencePerformed": .bool(false), "nextCommand": .string("nativeui-audit scan <image> --root <directory> --platform tvOS"),
            "capabilities": .array(["PNG/JPEG", "production_detection", "fused_OCR", "focus_receipt",
                                   "heuristic_audit_warnings"].map(JSON.string))])
    }

    func scan(_ image: CGImage, options: ScanOptions) async throws -> RuntimeScan {
        var effective = options
        if options.platform == "auto" {
            effective.platform = ((image.width == 1920 && image.height == 1080) ||
                (image.width == 3840 && image.height == 2160)) ? "tvOS" : "iOS"
        }
        effective.strict = false // The wrapper owns strict reporting, not inference behavior.
        let tv = effective.platform == "tvOS"
        let cached: Cached
        let cold = sessions[effective] == nil
        let start = ProcessInfo.processInfo.systemUptime
        if let existing = sessions[effective] { cached = existing }
        else {
            if sessions.count >= 4 { sessions.removeAll() }
            let manifest = try NativeUIModelAsset.requiredManifest(forTVOS: tv)
            let url = try NativeUIModelAsset.requiredModelURL(forTVOS: tv)
            let identity = try ArtifactIdentity.measure(url, modelID: manifest.modelId)
            let config = NativeUIDetectionConfiguration(minimumConfidence: effective.minConfidence,
                includesTextRecognition: effective.ocr, platform: tv ? .tvOS : .iOS, recordTimings: true)
            let session = NativeUIDetectionSession(configuration: config)
            try await session.warm(platforms: [tv ? .tvOS : .iOS])
            let after = try ArtifactIdentity.measure(url, modelID: manifest.modelId)
            guard identity.treeSHA256 == after.treeSHA256 else {
                throw AuditError("model_changed", "Model bytes changed during load.")
            }
            cached = Cached(session: session, identity: identity)
            sessions[effective] = cached
        }
        let load = cold ? (ProcessInfo.processInfo.systemUptime - start) * 1000 : 0
        let result = try await cached.session.performDetailed(on: image)
        return RuntimeScan(detector: cached.identity, platform: effective.platform,
            cacheState: cold ? "cold" : "warm", modelLoadMs: load, result: result)
    }
}

actor AuditService {
    let scope: FileScope
    let backend: any AuditBackend
    init(scope: FileScope, backend: any AuditBackend = ProductionBackend()) {
        self.scope = scope; self.backend = backend
    }
    func doctor() async -> JSON { await backend.doctor() }

    func scan(_ path: String, options: ScanOptions) async -> JSON {
        let start = ProcessInfo.processInfo.systemUptime
        do {
            try options.validate()
            let (url, data) = try scope.read(path)
            let image = try decodeImage(data)
            let runtime = try await backend.scan(image, options: options)
            let focus = runtime.result.focusExecution
            let degraded = runtime.result.modalityHealth.hasAnyFailure ||
                (focus?.fallbackReason != nil && focus?.fallbackReason != "disabled") ||
                (focus?.backend == .unavailable) ||
                (focus?.candidates.contains(where: { [.cropRejected, .predictionFailed, .policyRejected].contains($0.disposition) }) ?? false)
            return .object(["schemaVersion": .number(1), "input": .string(url.path),
                "configuration": try .encoded(options),
                "detectorIdentityScope": .string("compiled resource hashed before/after session load; retained with cached model"),
                "inputSHA256": .string(sha256(data)), "width": .number(Double(image.width)),
                "height": .number(Double(image.height)), "status": .string(degraded ? "degraded" : "success"),
                "strictFailure": .bool(options.strict && degraded),
                "strictPolicy": .string("processing-health-only-v1"),
                "auditInterpretation": .string("Warnings require review; screenshot scale is inferred, not verified. No UI defect certification."),
                "coordinates": .string("boundingBox: normalized bottom-left; boundingBoxPixels: pixels top-left"),
                "platformSelection": .string(options.platform == "auto" ? "dimension-heuristic" : "explicit"),
                "requestedComputeUnits": .string("all"), "hardwareDispatch": .string("not_observed"),
                "totalMs": .number((ProcessInfo.processInfo.systemUptime-start)*1000),
                "runtime": try .encoded(runtime)])
        } catch {
            return .object(["schemaVersion": .number(1), "input": .string(path),
                "status": .string("failed"), "strictFailure": .bool(true),
                "error": AuditError.wrap(error).json,
                "nextAction": .string("Check root, input integrity and nativeui-audit doctor; no automatic repair attempted."),
                "totalMs": .number((ProcessInfo.processInfo.systemUptime-start)*1000)])
        }
    }

    func batch(_ directory: String, options: ScanOptions) async throws -> JSON {
        try options.validate()
        let paths = try scope.batch(directory)
        var results: [JSON] = []
        for path in paths { results.append(await scan(path, options: options)) }
        let failed = results.filter { $0["status"]?.string == "failed" }.count
        let degraded = results.filter { $0["status"]?.string == "degraded" }.count
        return .object(["schemaVersion": .number(1), "scope": .string("nonrecursive visible PNG/JPEG entries; sorted paths"),
            "count": .number(Double(results.count)), "failed": .number(Double(failed)), "degraded": .number(Double(degraded)),
            "status": .string(paths.isEmpty ? "empty" : failed > 0 ? "partial_failure" : degraded > 0 ? "degraded" : "success"),
            "strictFailure": .bool(failed > 0 || (options.strict && degraded > 0)), "results": .array(results)])
    }
}
