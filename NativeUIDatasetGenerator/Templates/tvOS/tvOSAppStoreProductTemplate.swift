// tvOSAppStoreProductTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS App Store Product Page template for OS UI detection.
// Models Apple TV App Store app detail view:
// large app icon, title/developer, Get/Open primary button, screenshots gallery, and descriptions.
//
// Annotated elements:
//   primaryButton   — "Get" / "Open" action button (focused or unfocused)
//   secondaryButton — "Share" / "More" action buttons
//   collectionItem  — preview screenshot tiles in carousel
//   label           — app name, developer, category/age rating, descriptions
//   imageView       — app icon artwork and screenshot images

import SwiftUI

// MARK: - tvOSAppStoreProductConfig

public struct tvOSAppStoreProductConfig: Sendable {
    public var appName: String
    public var developer: String
    public var categoryRating: String
    public var descriptionText: String
    public var buttonTitle: String
    public var focusedTarget: Int // 0: primary button, 1: secondary button, 2..4: screenshot tiles
    public var appHue: Double

    public init(
        appName: String = "Flighty — Flight Tracker",
        developer: String = "Flighty LLC",
        categoryRating: String = "Travel • 4+ • Free with In-App Purchases",
        descriptionText: String = "Live flight tracking with real-time delays, aircraft radar, and gate changes on your Apple TV.",
        buttonTitle: String = "Get",
        focusedTarget: Int = 0,
        appHue: Double = 0.58
    ) {
        self.appName = appName
        self.developer = developer
        self.categoryRating = categoryRating
        self.descriptionText = descriptionText
        self.buttonTitle = buttonTitle
        self.focusedTarget = focusedTarget
        self.appHue = appHue
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSAppStoreProductConfig {
        var rng = SeededRNG(seed: seed)
        let apps = [
            ("Zwift: Ride and Run", "Zwift, Inc.", "Health & Fitness • 4+", "Immersive indoor cycling and running workouts.", "Get"),
            ("Infuse — Video Player", "FireCore", "Entertainment • 12+", "Ignite your video content on Apple TV with beautiful artwork.", "Open"),
            ("Asphalt 8: Airborne", "Gameloft", "Games • 12+", "High-octane arcade racing with MFi controller support.", "Get"),
            ("Streaks Workout", "Crunchy Bagel", "Health • 4+", "Quick personal daily workouts in your living room.", "Install")
        ]
        let item = apps[Int(rng.next() % UInt64(apps.count))]
        let foc = Int(rng.next() % 5)

        return tvOSAppStoreProductConfig(
            appName: item.0,
            developer: item.1,
            categoryRating: item.2,
            descriptionText: item.3,
            buttonTitle: item.4,
            focusedTarget: foc,
            appHue: Double(rng.next() % 1000) / 1000.0
        )
    }
}

// MARK: - tvOSAppStoreProductTemplate View

public struct tvOSAppStoreProductTemplate: View {
    public let config: tvOSAppStoreProductConfig

    public init(config: tvOSAppStoreProductConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            Color(red: 0.08, green: 0.08, blue: 0.12).ignoresSafeArea()

            VStack(alignment: .leading, spacing: 36) {
                // Header Row: App Icon + Metadata + Action Buttons
                HStack(alignment: .top, spacing: 40) {
                    // App Icon
                    ZStack {
                        RoundedRectangle(cornerRadius: 32)
                            .fill(LinearGradient(
                                colors: [Color(hue: config.appHue, saturation: 0.7, brightness: 0.6), Color.black.opacity(0.8)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ))
                        Image(systemName: "app.gift.fill")
                            .font(.system(size: 80))
                            .foregroundColor(.white.opacity(0.9))
                    }
                    .frame(width: 220, height: 220)
                    .shadow(color: Color.black.opacity(0.5), radius: 20)
                    .captureFrame(id: "imageView_app_store_icon")

                    // Titles & Buttons
                    VStack(alignment: .leading, spacing: 14) {
                        Text(config.appName)
                            .font(.system(size: 44, weight: .bold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_app_name")

                        Text(config.developer)
                            .font(.system(size: 24, weight: .medium))
                            .foregroundColor(.white.opacity(0.7))
                            .captureFrame(id: "label_developer_name")

                        Text(config.categoryRating)
                            .font(.system(size: 20))
                            .foregroundColor(.white.opacity(0.5))
                            .captureFrame(id: "label_category_rating")

                        Spacer().frame(height: 10)

                        HStack(spacing: 24) {
                            // Primary Download/Get Button
                            let isPrimaryFoc = (config.focusedTarget == 0)
                            Text(config.buttonTitle)
                                .font(.system(size: 26, weight: .bold))
                                .foregroundColor(isPrimaryFoc ? Color.black : Color.white)
                                .frame(width: 180, height: 64)
                                .background(isPrimaryFoc ? Color.white : Color.white.opacity(0.15))
                                .cornerRadius(16)
                                .shadow(color: isPrimaryFoc ? Color.white.opacity(0.4) : Color.clear, radius: 14)
                                .captureFrame(id: isPrimaryFoc ? "primaryButton_get_app_focused" : "primaryButton_get_app_unfocused")

                            // Secondary Action Button
                            let isSecFoc = (config.focusedTarget == 1)
                            Image(systemName: "ellipsis")
                                .font(.system(size: 24))
                                .foregroundColor(isSecFoc ? Color.black : Color.white)
                                .frame(width: 64, height: 64)
                                .background(isSecFoc ? Color.white : Color.white.opacity(0.12))
                                .cornerRadius(16)
                                .shadow(color: isSecFoc ? Color.white.opacity(0.4) : Color.clear, radius: 14)
                                .captureFrame(id: isSecFoc ? "secondaryButton_app_more_focused" : "secondaryButton_app_more_unfocused")
                        }
                    }

                    Spacer()
                }
                .padding(.top, 60)
                .padding(.horizontal, 90)

                // Description
                Text(config.descriptionText)
                    .font(.system(size: 24))
                    .foregroundColor(.white.opacity(0.8))
                    .lineLimit(2)
                    .padding(.horizontal, 90)
                    .captureFrame(id: "label_app_description")

                // Screenshots Carousel
                VStack(alignment: .leading, spacing: 16) {
                    Text("Screenshots")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.white)
                        .padding(.horizontal, 90)
                        .captureFrame(id: "label_screenshots_heading")

                    HStack(spacing: 36) {
                        ForEach(0..<3) { idx in
                            let targetIdx = idx + 2
                            let isFoc = (config.focusedTarget == targetIdx)

                            ZStack {
                                RoundedRectangle(cornerRadius: 18)
                                    .fill(LinearGradient(
                                        colors: [Color(hue: (config.appHue + Double(idx) * 0.1).truncatingRemainder(dividingBy: 1.0), saturation: 0.5, brightness: 0.4), Color.black.opacity(0.7)],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    ))
                                Image(systemName: "photo.fill")
                                    .font(.system(size: 48))
                                    .foregroundColor(.white.opacity(0.6))
                                    .captureFrame(id: "imageView_screenshot_\(idx)")
                            }
                            .frame(width: 530, height: 300)
                            .overlay(
                                RoundedRectangle(cornerRadius: 18)
                                    .stroke(isFoc ? Color.white : Color.clear, lineWidth: 4)
                            )
                            .shadow(color: isFoc ? Color.white.opacity(0.4) : Color.black.opacity(0.4), radius: isFoc ? 20 : 8)
                            .captureFrame(id: isFoc ? "collectionItem_screenshot_\(idx)_focused" : "collectionItem_screenshot_\(idx)_unfocused")
                        }
                    }
                    .padding(.horizontal, 90)
                }

                Spacer()
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}
