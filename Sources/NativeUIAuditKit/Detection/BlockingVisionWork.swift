// BlockingVisionWork.swift
// NativeUIAuditKit
//
// Runs synchronous Vision and Core ML work off the Swift cooperative thread pool.
//
// Why: `VNImageRequestHandler.perform` blocks its thread. Inside it, VNRecognizeTextRequest
// waits for internal work that needs a free cooperative thread. When `Task.detached` ran this
// work, about 10 concurrent blocking calls (one per CPU core) filled the pool and every thread
// waited for another: the full `swift test` run hung on 2026-11-22 (BP-120).
// A dedicated GCD queue keeps the cooperative pool free while the caller awaits the result.

import Dispatch

enum BlockingVisionWork {
    private static let queue = DispatchQueue(
        label: "NativeUIAuditKit.blocking-vision-work",
        qos: .userInitiated,
        attributes: .concurrent
    )

    /// Run `work` on the dedicated queue and resume the caller with its result or error.
    static func run<T: Sendable>(_ work: @escaping @Sendable () throws -> T) async throws -> T {
        try await withCheckedThrowingContinuation { continuation in
            queue.async {
                continuation.resume(with: Result { try work() })
            }
        }
    }
}
