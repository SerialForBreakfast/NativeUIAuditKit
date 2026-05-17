import CoreGraphics
import Foundation

// MARK: - OS visual appearance

/// Parameterized visual profile for a device/OS pairing.
/// Controls which chrome style is rendered — no need to run multiple simulator OS versions.
public struct OSVisualProfile: Codable, Sendable {
    public var tabBarStyle: TabBarStyle
    public var navBarStyle: NavBarStyle
    public var hasDynamicIsland: Bool
    public var hasHomeIndicator: Bool
    public var hasNotch: Bool
    public var navBarIsTranslucent: Bool
    public var safeAreaTopInset: CGFloat
    public var safeAreaBottomInset: CGFloat
    /// Canonical logical screen size in points for this device/OS profile.
    /// Used as the off-screen window size in ScreenshotCapture.capture so that UIKit
    /// chrome (UINavigationBar, UITabBar) is rendered at the correct device geometry.
    /// Do NOT use UIScreen.main.bounds — the simulator may report a different size.
    public var screenSize: CGSize

    public enum TabBarStyle: String, Codable, Sendable {
        case classic       // iOS 17 and earlier — opaque bar at bottom
        case floating      // iOS 18 — elevated pill
        case liquidGlass   // iOS 26 — Liquid Glass pill
    }

    public enum NavBarStyle: String, Codable, Sendable {
        case classic       // Standard opaque or translucent bar
        case liquidGlass   // iOS 26 Liquid Glass material
    }

    // MARK: Predefined profiles

    /// iPhone SE 3rd gen, iOS 17 — notch, home indicator, classic chrome, 375×667pt @2x
    public static let ios17 = OSVisualProfile(
        tabBarStyle: .classic,
        navBarStyle: .classic,
        hasDynamicIsland: false,
        hasHomeIndicator: true,
        hasNotch: true,
        navBarIsTranslucent: true,
        safeAreaTopInset: 47,
        safeAreaBottomInset: 34,
        screenSize: CGSize(width: 375, height: 667)
    )

    /// iPhone 15 Pro, iOS 18 — Dynamic Island, floating tab bar, 393×852pt @3x
    public static let ios18 = OSVisualProfile(
        tabBarStyle: .floating,
        navBarStyle: .classic,
        hasDynamicIsland: true,
        hasHomeIndicator: true,
        hasNotch: false,
        navBarIsTranslucent: true,
        safeAreaTopInset: 59,
        safeAreaBottomInset: 34,
        screenSize: CGSize(width: 393, height: 852)
    )

    /// iPhone 17 Pro, iOS 26 — Liquid Glass chrome, Dynamic Island, 393×852pt @3x
    public static let ios26 = OSVisualProfile(
        tabBarStyle: .liquidGlass,
        navBarStyle: .liquidGlass,
        hasDynamicIsland: true,
        hasHomeIndicator: true,
        hasNotch: false,
        navBarIsTranslucent: true,
        safeAreaTopInset: 62,
        safeAreaBottomInset: 34,
        screenSize: CGSize(width: 393, height: 852)
    )

    /// Apple TV, tvOS 17/18 — no status bar, tab bar at top, no safe-area notch
    public static let tvOS17 = OSVisualProfile(
        tabBarStyle: .classic,
        navBarStyle: .classic,
        hasDynamicIsland: false,
        hasHomeIndicator: false,
        hasNotch: false,
        navBarIsTranslucent: false,
        safeAreaTopInset: 60,   // tvOS overscan margin
        safeAreaBottomInset: 60,
        screenSize: CGSize(width: 1920, height: 1080)
    )

    /// macOS 15 — window chrome, NSToolbar, no safe-area notch
    public static let macOS15 = OSVisualProfile(
        tabBarStyle: .classic,
        navBarStyle: .classic,
        hasDynamicIsland: false,
        hasHomeIndicator: false,
        hasNotch: false,
        navBarIsTranslucent: true,
        safeAreaTopInset: 52,   // title bar + toolbar height
        safeAreaBottomInset: 0,
        screenSize: CGSize(width: 1280, height: 800)
    )
}

// MARK: - Simulator status bar override

/// Maps directly to `xcrun simctl status_bar <udid> override` arguments.
public struct SimulatorStateOverride: Codable, Sendable {
    public var time: String          // "HH:MM" (24-hour)
    public var batteryLevel: Int     // 10, 25, 50, 75, or 100
    public var batteryState: String  // "charging" | "discharging"
    public var cellularBars: Int     // 0, 1, 3, or 5
    public var wifiBars: Int         // 0, 1, or 3
    public var cellularMode: String  // "active" | "notSupported"
    public var operatorName: String  // e.g. "", "AT&T", "Vodafone", "SoftBank"

    public init(
        time: String,
        batteryLevel: Int,
        batteryState: String,
        cellularBars: Int,
        wifiBars: Int,
        cellularMode: String,
        operatorName: String
    ) {
        self.time = time
        self.batteryLevel = batteryLevel
        self.batteryState = batteryState
        self.cellularBars = cellularBars
        self.wifiBars = wifiBars
        self.cellularMode = cellularMode
        self.operatorName = operatorName
    }
}

// MARK: - Color scheme

public enum GeneratorColorScheme: String, Codable, Sendable {
    case light
    case dark
}

// MARK: - Dynamic Type size

public enum GeneratorDynamicTypeSize: String, Codable, Sendable {
    case xSmall
    case small
    case medium
    case large
    case xLarge
    case xxLarge
    case xxxLarge
    case accessibilityMedium
    case accessibilityLarge
    case accessibilityExtraLarge
    case accessibilityExtraExtraLarge
    case accessibilityExtraExtraExtraLarge
}

// MARK: - Layout direction

public enum GeneratorLayoutDirection: String, Codable, Sendable {
    case ltr
    case rtl
}

// MARK: - Accessibility flags

public struct AccessibilityFlags: Codable, Sendable {
    public var reduceTransparency: Bool
    public var increaseContrast: Bool
    public var boldText: Bool
    public var buttonShapes: Bool
    public var onOffLabels: Bool
    public var smartInvert: Bool
    public var classicInvert: Bool

    public init(
        reduceTransparency: Bool = false,
        increaseContrast: Bool = false,
        boldText: Bool = false,
        buttonShapes: Bool = false,
        onOffLabels: Bool = false,
        smartInvert: Bool = false,
        classicInvert: Bool = false
    ) {
        self.reduceTransparency = reduceTransparency
        self.increaseContrast = increaseContrast
        self.boldText = boldText
        self.buttonShapes = buttonShapes
        self.onOffLabels = onOffLabels
        self.smartInvert = smartInvert
        self.classicInvert = classicInvert
    }

    public static let `default` = AccessibilityFlags()
}

// MARK: - Top-level run configuration

/// Configuration for a single generator run. Deterministic: same seed → byte-identical PNG + annotation.
public struct GeneratorRunConfig: Codable, Sendable {
    public var seed: UInt64
    public var templateFamily: String
    public var osProfile: OSVisualProfile
    public var simulatorOverride: SimulatorStateOverride
    public var colorScheme: GeneratorColorScheme
    public var dynamicTypeSize: GeneratorDynamicTypeSize
    public var deviceName: String
    public var pixelScale: Int           // 2 or 3
    public var locale: String            // e.g. "en_US", "ar_SA"
    public var layoutDirection: GeneratorLayoutDirection
    public var accessibilityFlags: AccessibilityFlags
    public var isolationTemplate: Bool   // single-class isolation image
    public var lowDensity: Bool          // fewer than 2 elements (hard-negative territory)

    public init(
        seed: UInt64,
        templateFamily: String,
        osProfile: OSVisualProfile,
        simulatorOverride: SimulatorStateOverride,
        colorScheme: GeneratorColorScheme,
        dynamicTypeSize: GeneratorDynamicTypeSize,
        deviceName: String,
        pixelScale: Int,
        locale: String,
        layoutDirection: GeneratorLayoutDirection,
        accessibilityFlags: AccessibilityFlags = .default,
        isolationTemplate: Bool = false,
        lowDensity: Bool = false
    ) {
        self.seed = seed
        self.templateFamily = templateFamily
        self.osProfile = osProfile
        self.simulatorOverride = simulatorOverride
        self.colorScheme = colorScheme
        self.dynamicTypeSize = dynamicTypeSize
        self.deviceName = deviceName
        self.pixelScale = pixelScale
        self.locale = locale
        self.layoutDirection = layoutDirection
        self.accessibilityFlags = accessibilityFlags
        self.isolationTemplate = isolationTemplate
        self.lowDensity = lowDensity
    }
}
