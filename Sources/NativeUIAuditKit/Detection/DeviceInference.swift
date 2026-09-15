// DeviceInference.swift
// NativeUIAuditKit
//
// Heuristic and metadata-driven Apple device and platform inference.

import CoreGraphics
import Foundation

/// Engine for inferring device model, platform, and OS version from screenshots and UI observations.
public enum DeviceInference {

    /// Infers device model, platform, and OS version from image dimensions, detected UI elements, and optional sidecar metadata.
    public static func inferDevice(
        imageSize: CGSize,
        observations: [NativeUIElementObservation] = [],
        sidecar: NativeUISidecar? = nil
    ) -> NativeUIDeviceInference {

        // 1. Sidecar Fast-Path: authoritative metadata available
        if let sidecar = sidecar {
            let platform = parsePlatform(sidecar.platform)
            let osVersion = parseOSVersion(sidecar.osVersion)
            let topCandidate = NativeUIDeviceCandidate(
                deviceFamily: sidecar.deviceName,
                confidence: 1.0
            )
            return NativeUIDeviceInference(
                platform: platform,
                deviceCandidates: [topCandidate],
                inferredOSMajorVersion: osVersion,
                confidence: 1.0
            )
        }

        // 2. Pixel Heuristics Path
        let w = Int(imageSize.width)
        let h = Int(imageSize.height)

        let matchingDimensions = DeviceDimensionDatabase.lookup(width: w, height: h)

        if !matchingDimensions.isEmpty {
            return inferFromDimensions(
                dimensions: matchingDimensions,
                observations: observations
            )
        }

        // 3. Fallback Path for uncatalogued/custom resolutions
        return inferFallback(imageSize: imageSize, observations: observations)
    }

    // MARK: - Pixel Chrome Refinement

    private static func inferFromDimensions(
        dimensions: [DeviceDimension],
        observations: [NativeUIElementObservation]
    ) -> NativeUIDeviceInference {

        let hasDynamicIsland = observations.contains { $0.elementType == .dynamicIsland }
        let hasHomeIndicator = observations.contains { $0.elementType == .homeIndicator }

        var filtered = dimensions

        // If Dynamic Island is detected, isolate devices with Dynamic Island
        if hasDynamicIsland {
            let islandDims = filtered.filter { $0.hasDynamicIsland }
            if !islandDims.isEmpty {
                filtered = islandDims
            }
        }

        // If Home Indicator is detected, isolate gesture-based devices
        if hasHomeIndicator {
            let gestureDims = filtered.filter { $0.hasHomeIndicator }
            if !gestureDims.isEmpty {
                filtered = gestureDims
            }
        }

        let primaryPlatform = filtered.first?.platform ?? .iOS

        // Collect unique candidate model names
        var candidateNames: [String] = []
        for dim in filtered {
            for c in dim.candidates where !candidateNames.contains(c) {
                candidateNames.append(c)
            }
        }

        if candidateNames.isEmpty {
            candidateNames = ["Apple Device"]
        }

        // Distribute confidence evenly across candidate models
        let perCandidateConf = Double(1.0) / Double(candidateNames.count)
        let roundedConf = (perCandidateConf * 100).rounded() / 100.0

        let candidates = candidateNames.map {
            NativeUIDeviceCandidate(deviceFamily: $0, confidence: roundedConf)
        }

        // Inferred OS version heuristics
        var osMajor: Int? = nil
        if hasDynamicIsland {
            osMajor = 17 // Dynamic Island standardizes on iOS 16/17+
        } else if primaryPlatform == .iOS {
            osMajor = 17
        } else if primaryPlatform == .macOS {
            osMajor = 14
        } else if primaryPlatform == .tvOS {
            osMajor = 17
        }

        let topConf = candidates.first?.confidence ?? 0.5

        return NativeUIDeviceInference(
            platform: primaryPlatform,
            deviceCandidates: candidates,
            inferredOSMajorVersion: osMajor,
            confidence: topConf
        )
    }

    // MARK: - Fallback

    private static func inferFallback(
        imageSize: CGSize,
        observations: [NativeUIElementObservation]
    ) -> NativeUIDeviceInference {
        let w = imageSize.width
        let h = imageSize.height
        let aspect = max(w, h) / max(1.0, min(w, h))

        let platform: NativeUIPlatform
        let name: String

        if observations.contains(where: { $0.elementType == .dynamicIsland || $0.elementType == .homeIndicator }) {
            platform = .iOS
            name = "iPhone (Unlisted Resolution)"
        } else if aspect >= 1.9 {
            platform = .iOS
            name = "iPhone (Unlisted Aspect)"
        } else if aspect >= 1.3 && aspect <= 1.45 {
            platform = .iPadOS
            name = "iPad (Unlisted Resolution)"
        } else if w > h && w >= 1200 {
            platform = .macOS
            name = "Mac (Custom Display)"
        } else {
            platform = .unknown
            name = "Unknown Apple Device"
        }

        return NativeUIDeviceInference(
            platform: platform,
            deviceCandidates: [NativeUIDeviceCandidate(deviceFamily: name, confidence: 0.30)],
            inferredOSMajorVersion: nil,
            confidence: 0.30
        )
    }

    // MARK: - Helpers

    private static func parsePlatform(_ str: String) -> NativeUIPlatform {
        switch str.lowercased() {
        case "ios": return .iOS
        case "ipados": return .iPadOS
        case "tvos": return .tvOS
        case "macos": return .macOS
        case "visionos": return .visionOS
        default: return .unknown
        }
    }

    private static func parseOSVersion(_ str: String) -> Int? {
        let parts = str.components(separatedBy: ".")
        if let first = parts.first, let val = Int(first) {
            return val
        }
        return nil
    }
}
