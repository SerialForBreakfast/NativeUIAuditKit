// DeviceDimensionDatabase.swift
// NativeUIAuditKit
//
// Lookup database of known Apple device screenshot dimensions and hardware profiles.

import Foundation

/// A known Apple device dimension profile.
public struct DeviceDimension: Sendable, Equatable {
    public let widthPx: Int
    public let heightPx: Int
    public let scale: Int
    public let candidates: [String]
    public let platform: NativeUIPlatform
    public let hasHomeIndicator: Bool
    public let hasDynamicIsland: Bool
    public let hasNotch: Bool

    public init(
        widthPx: Int,
        heightPx: Int,
        scale: Int,
        candidates: [String],
        platform: NativeUIPlatform,
        hasHomeIndicator: Bool = true,
        hasDynamicIsland: Bool = false,
        hasNotch: Bool = false
    ) {
        self.widthPx = widthPx
        self.heightPx = heightPx
        self.scale = scale
        self.candidates = candidates
        self.platform = platform
        self.hasHomeIndicator = hasHomeIndicator
        self.hasDynamicIsland = hasDynamicIsland
        self.hasNotch = hasNotch
    }
}

/// Database of standard Apple device display dimensions, scale factors, and hardware features.
public enum DeviceDimensionDatabase {

    public static let allDimensions: [DeviceDimension] = [
        // MARK: - iPhones (Dynamic Island)
        DeviceDimension(
            widthPx: 1179, heightPx: 2556, scale: 3,
            candidates: ["iPhone 14 Pro", "iPhone 15", "iPhone 15 Pro", "iPhone 16"],
            platform: .iOS, hasHomeIndicator: true, hasDynamicIsland: true, hasNotch: false
        ),
        DeviceDimension(
            widthPx: 1290, heightPx: 2796, scale: 3,
            candidates: ["iPhone 14 Pro Max", "iPhone 15 Plus", "iPhone 15 Pro Max", "iPhone 16 Plus"],
            platform: .iOS, hasHomeIndicator: true, hasDynamicIsland: true, hasNotch: false
        ),
        DeviceDimension(
            widthPx: 1206, heightPx: 2622, scale: 3,
            candidates: ["iPhone 16 Pro"],
            platform: .iOS, hasHomeIndicator: true, hasDynamicIsland: true, hasNotch: false
        ),
        DeviceDimension(
            widthPx: 1320, heightPx: 2868, scale: 3,
            candidates: ["iPhone 16 Pro Max"],
            platform: .iOS, hasHomeIndicator: true, hasDynamicIsland: true, hasNotch: false
        ),

        // MARK: - iPhones (Notch & Face ID)
        DeviceDimension(
            widthPx: 1170, heightPx: 2532, scale: 3,
            candidates: ["iPhone 12", "iPhone 12 Pro", "iPhone 13", "iPhone 13 Pro", "iPhone 14"],
            platform: .iOS, hasHomeIndicator: true, hasDynamicIsland: false, hasNotch: true
        ),
        DeviceDimension(
            widthPx: 1284, heightPx: 2778, scale: 3,
            candidates: ["iPhone 12 Pro Max", "iPhone 13 Pro Max", "iPhone 14 Plus"],
            platform: .iOS, hasHomeIndicator: true, hasDynamicIsland: false, hasNotch: true
        ),
        DeviceDimension(
            widthPx: 1080, heightPx: 2340, scale: 3,
            candidates: ["iPhone 12 mini", "iPhone 13 mini"],
            platform: .iOS, hasHomeIndicator: true, hasDynamicIsland: false, hasNotch: true
        ),
        DeviceDimension(
            widthPx: 1125, heightPx: 2436, scale: 3,
            candidates: ["iPhone X", "iPhone XS", "iPhone 11 Pro"],
            platform: .iOS, hasHomeIndicator: true, hasDynamicIsland: false, hasNotch: true
        ),
        DeviceDimension(
            widthPx: 828, heightPx: 1792, scale: 2,
            candidates: ["iPhone XR", "iPhone 11"],
            platform: .iOS, hasHomeIndicator: true, hasDynamicIsland: false, hasNotch: true
        ),
        DeviceDimension(
            widthPx: 1242, heightPx: 2688, scale: 3,
            candidates: ["iPhone XS Max", "iPhone 11 Pro Max"],
            platform: .iOS, hasHomeIndicator: true, hasDynamicIsland: false, hasNotch: true
        ),

        // MARK: - iPhones (Home Button / Touch ID)
        DeviceDimension(
            widthPx: 750, heightPx: 1334, scale: 2,
            candidates: ["iPhone 6", "iPhone 6s", "iPhone 7", "iPhone 8", "iPhone SE (2nd gen)", "iPhone SE (3rd gen)"],
            platform: .iOS, hasHomeIndicator: false, hasDynamicIsland: false, hasNotch: false
        ),
        DeviceDimension(
            widthPx: 1242, heightPx: 2208, scale: 3,
            candidates: ["iPhone 6 Plus", "iPhone 6s Plus", "iPhone 7 Plus", "iPhone 8 Plus"],
            platform: .iOS, hasHomeIndicator: false, hasDynamicIsland: false, hasNotch: false
        ),
        DeviceDimension(
            widthPx: 1080, heightPx: 1920, scale: 3,
            candidates: ["iPhone 6 Plus", "iPhone 7 Plus", "iPhone 8 Plus"],
            platform: .iOS, hasHomeIndicator: false, hasDynamicIsland: false, hasNotch: false
        ),
        DeviceDimension(
            widthPx: 640, heightPx: 1136, scale: 2,
            candidates: ["iPhone 5", "iPhone 5s", "iPhone 5c", "iPhone SE (1st gen)"],
            platform: .iOS, hasHomeIndicator: false, hasDynamicIsland: false, hasNotch: false
        ),

        // MARK: - iPads
        DeviceDimension(
            widthPx: 2048, heightPx: 2732, scale: 2,
            candidates: ["iPad Pro 12.9-inch", "iPad Pro 13-inch (M4)", "iPad Air 13-inch (M2)"],
            platform: .iPadOS, hasHomeIndicator: true, hasDynamicIsland: false, hasNotch: false
        ),
        DeviceDimension(
            widthPx: 1668, heightPx: 2388, scale: 2,
            candidates: ["iPad Pro 11-inch", "iPad Air 11-inch (M2)"],
            platform: .iPadOS, hasHomeIndicator: true, hasDynamicIsland: false, hasNotch: false
        ),
        DeviceDimension(
            widthPx: 1640, heightPx: 2360, scale: 2,
            candidates: ["iPad Air (4th gen)", "iPad Air (5th gen)", "iPad (10th gen)"],
            platform: .iPadOS, hasHomeIndicator: true, hasDynamicIsland: false, hasNotch: false
        ),
        DeviceDimension(
            widthPx: 1620, heightPx: 2160, scale: 2,
            candidates: ["iPad (7th gen)", "iPad (8th gen)", "iPad (9th gen)"],
            platform: .iPadOS, hasHomeIndicator: false, hasDynamicIsland: false, hasNotch: false
        ),
        DeviceDimension(
            widthPx: 1536, heightPx: 2048, scale: 2,
            candidates: ["iPad (5th gen)", "iPad (6th gen)", "iPad mini (4th gen)", "iPad mini (5th gen)", "iPad Air 2"],
            platform: .iPadOS, hasHomeIndicator: false, hasDynamicIsland: false, hasNotch: false
        ),
        DeviceDimension(
            widthPx: 1488, heightPx: 2266, scale: 2,
            candidates: ["iPad mini (6th gen)"],
            platform: .iPadOS, hasHomeIndicator: true, hasDynamicIsland: false, hasNotch: false
        ),
        DeviceDimension(
            widthPx: 1668, heightPx: 2224, scale: 2,
            candidates: ["iPad Pro 10.5-inch", "iPad Air (3rd gen)"],
            platform: .iPadOS, hasHomeIndicator: false, hasDynamicIsland: false, hasNotch: false
        ),

        // MARK: - Apple TV / tvOS
        DeviceDimension(
            widthPx: 1920, heightPx: 1080, scale: 1,
            candidates: ["Apple TV HD", "Apple TV 4K (1080p)"],
            platform: .tvOS, hasHomeIndicator: false, hasDynamicIsland: false, hasNotch: false
        ),
        DeviceDimension(
            widthPx: 3840, heightPx: 2160, scale: 2,
            candidates: ["Apple TV 4K (2160p)"],
            platform: .tvOS, hasHomeIndicator: false, hasDynamicIsland: false, hasNotch: false
        ),

        // MARK: - macOS
        DeviceDimension(
            widthPx: 1440, heightPx: 900, scale: 1,
            candidates: ["MacBook Air (13-inch)", "MacBook Pro (15-inch standard)"],
            platform: .macOS, hasHomeIndicator: false, hasDynamicIsland: false, hasNotch: false
        ),
        DeviceDimension(
            widthPx: 2560, heightPx: 1600, scale: 2,
            candidates: ["MacBook Air (Retina 13-inch)", "MacBook Pro (13-inch)"],
            platform: .macOS, hasHomeIndicator: false, hasDynamicIsland: false, hasNotch: false
        ),
        DeviceDimension(
            widthPx: 2880, heightPx: 1800, scale: 2,
            candidates: ["MacBook Pro (15-inch Retina)"],
            platform: .macOS, hasHomeIndicator: false, hasDynamicIsland: false, hasNotch: false
        ),
        DeviceDimension(
            widthPx: 3024, heightPx: 1964, scale: 2,
            candidates: ["MacBook Pro (14-inch)"],
            platform: .macOS, hasHomeIndicator: false, hasDynamicIsland: false, hasNotch: true
        ),
        DeviceDimension(
            widthPx: 3456, heightPx: 2234, scale: 2,
            candidates: ["MacBook Pro (16-inch)"],
            platform: .macOS, hasHomeIndicator: false, hasDynamicIsland: false, hasNotch: true
        ),
        DeviceDimension(
            widthPx: 2560, heightPx: 1440, scale: 1,
            candidates: ["iMac (27-inch)", "External QHD Display"],
            platform: .macOS, hasHomeIndicator: false, hasDynamicIsland: false, hasNotch: false
        ),
        DeviceDimension(
            widthPx: 5120, heightPx: 2880, scale: 2,
            candidates: ["iMac (27-inch 5K)", "Studio Display (5K)"],
            platform: .macOS, hasHomeIndicator: false, hasDynamicIsland: false, hasNotch: false
        )
    ]

    /// Looks up device candidates matching screenshot pixel dimensions (portrait or landscape).
    public static func lookup(width: Int, height: Int) -> [DeviceDimension] {
        allDimensions.filter { dim in
            // Direct match
            if dim.widthPx == width && dim.heightPx == height {
                return true
            }
            // Landscape/portrait rotated match
            if dim.widthPx == height && dim.heightPx == width {
                return true
            }
            return false
        }
    }
}
