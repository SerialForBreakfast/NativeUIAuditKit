// tvOSHardNegativesTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Hard-negative template for tvOS OS UI detection.
// Renders aerial screensaver aesthetics, video playback frames without chrome,
// and ambient gradient wallpapers. Produces zero annotated UI elements,
// training the detector to suppress false positives on rich video content.

import SwiftUI

// MARK: - tvOSHardNegativeConfig

public struct tvOSHardNegativeConfig: Sendable {
    public enum Style: Sendable {
        case aerialScreensaver
        case ambientWallpaper
        case videoPlayback
    }

    public var style: Style
    public var hue1: Double
    public var hue2: Double

    public init(style: Style, hue1: Double, hue2: Double) {
        self.style = style
        self.hue1 = hue1
        self.hue2 = hue2
    }

    public static func make(seed: UInt64) -> tvOSHardNegativeConfig {
        var rng = SeededRNG(seed: seed)
        let styles: [Style] = [.aerialScreensaver, .ambientWallpaper, .videoPlayback]
        let st = styles[Int(rng.next() % UInt64(styles.count))]
        let h1 = Double(rng.next() % 1000) / 1000.0
        let h2 = Double(rng.next() % 1000) / 1000.0
        return tvOSHardNegativeConfig(style: st, hue1: h1, hue2: h2)
    }
}

// MARK: - tvOSHardNegativesTemplate View

public struct tvOSHardNegativesTemplate: View {
    public let config: tvOSHardNegativeConfig

    public init(config: tvOSHardNegativeConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            switch config.style {
            case .aerialScreensaver:
                LinearGradient(
                    colors: [
                        Color(hue: config.hue1, saturation: 0.8, brightness: 0.25),
                        Color(hue: config.hue2, saturation: 0.6, brightness: 0.15),
                        Color.black
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            case .ambientWallpaper:
                RadialGradient(
                    gradient: Gradient(colors: [
                        Color(hue: config.hue1, saturation: 0.7, brightness: 0.4),
                        Color(hue: config.hue2, saturation: 0.9, brightness: 0.1),
                        Color.black
                    ]),
                    center: .center,
                    startRadius: 100,
                    endRadius: 900
                )
            case .videoPlayback:
                Color(red: 0.02, green: 0.02, blue: 0.03)
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}
