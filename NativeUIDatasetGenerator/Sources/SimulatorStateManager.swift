import Foundation

/// Manages `xcrun simctl status_bar` overrides for a specific simulator device.
///
/// Apply a `SimulatorStateOverride` before each generation batch and call `clear()`
/// afterward to prevent simulator state from leaking into subsequent batches.
/// All methods are async to allow off-main-thread use; the actor enforces serial access.
public actor SimulatorStateManager {

    public let deviceUDID: String

    public init(deviceUDID: String) {
        self.deviceUDID = deviceUDID
    }

    // MARK: - Public API

    /// Apply simulator status bar overrides. Maps directly to `xcrun simctl status_bar <udid> override ...`.
    public func apply(_ override: SimulatorStateOverride) async throws {
        let args = Self.overrideArguments(udid: deviceUDID, override: override)
        try await runXcrun(arguments: args)
    }

    /// Clear all status bar overrides for this device.
    public func clear() async throws {
        try await runXcrun(arguments: ["simctl", "status_bar", deviceUDID, "clear"])
    }

    // MARK: - Seeded random override generation

    /// Generates a deterministic `SimulatorStateOverride` using a seeded RNG.
    /// Same seed + batchIndex → same output, always.
    public static func randomOverride(seed: UInt64, batchIndex: Int) -> SimulatorStateOverride {
        var rng = SeededRNG(seed: seed &+ UInt64(bitPattern: Int64(batchIndex) &* 6_364_136_223_846_793_005))

        let timeSlots: [String] = (0..<96).map { i in
            let hour = i / 4
            let minute = (i % 4) * 15
            return String(format: "%02d:%02d", hour, minute)
        }
        let batteryLevels = [10, 25, 50, 75, 100]
        let cellularBarsOptions = [0, 1, 3, 5]
        let wifiBarsOptions = [0, 1, 3]
        let operatorNames = ["", "AT&T", "Vodafone", "SoftBank"]

        let time        = timeSlots.randomElement(using: &rng)!
        let battery     = batteryLevels.randomElement(using: &rng)!
        let charging    = rng.next() % 2 == 0
        let cellular    = cellularBarsOptions.randomElement(using: &rng)!
        let wifi        = wifiBarsOptions.randomElement(using: &rng)!
        let mode        = cellular > 0 ? "active" : "notSupported"
        let carrier     = operatorNames.randomElement(using: &rng)!

        return SimulatorStateOverride(
            time: time,
            batteryLevel: battery,
            batteryState: charging ? "charging" : "discharging",
            cellularBars: cellular,
            wifiBars: wifi,
            cellularMode: mode,
            operatorName: carrier
        )
    }

    // MARK: - Argument construction (testable without running xcrun)

    /// Constructs the exact `xcrun simctl status_bar <udid> override` argument array.
    /// Separated from `apply` so unit tests can inspect arguments without spawning a process.
    static func overrideArguments(udid: String, override: SimulatorStateOverride) -> [String] {
        var args = ["simctl", "status_bar", udid, "override"]
        args += ["--time", override.time]
        args += ["--batteryLevel", String(override.batteryLevel)]
        args += ["--batteryState", override.batteryState]
        args += ["--cellularBars", String(override.cellularBars)]
        args += ["--wifiBars", String(override.wifiBars)]
        args += ["--cellularMode", override.cellularMode]
        if !override.operatorName.isEmpty {
            args += ["--operatorName", override.operatorName]
        }
        return args
    }

    // MARK: - Process execution

    private func runXcrun(arguments: [String]) async throws {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/xcrun")
        process.arguments = arguments

        let pipe = Pipe()
        process.standardError = pipe

        try process.run()
        process.waitUntilExit()

        guard process.terminationStatus == 0 else {
            let errData = pipe.fileHandleForReading.readDataToEndOfFile()
            let errMsg = String(data: errData, encoding: .utf8) ?? "(no stderr output)"
            throw SimulatorStateError.xcrunFailed(
                arguments: arguments,
                status: process.terminationStatus,
                stderr: errMsg
            )
        }
    }
}

// MARK: - Error type

public enum SimulatorStateError: Error, CustomStringConvertible {
    case xcrunFailed(arguments: [String], status: Int32, stderr: String)

    public var description: String {
        switch self {
        case .xcrunFailed(let args, let status, let stderr):
            return "xcrun \(args.joined(separator: " ")) failed (exit \(status)): \(stderr)"
        }
    }
}

