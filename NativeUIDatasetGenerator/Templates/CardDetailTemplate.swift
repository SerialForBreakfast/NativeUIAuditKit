// CardDetailTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI card detail screen (TASK-5b-22).
// Structural distinction: full-bleed hero image at top, no NavigationStack wrapper —
// the back button and title are rendered inline (custom nav chrome) so the model sees
// imageView + label + primaryButton + secondaryButton in a non-nav-bar context.
//
// Annotated elements:
//   imageView      — full-bleed hero at top of screen
//   label          — title, subtitle, body text
//   primaryButton  — primary action (e.g. "Get", "Buy")
//   secondaryButton — secondary action (e.g. "Share", "Save")
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - CardDetailConfig

public struct CardDetailConfig: Sendable {
    public var heroHue: Double
    public var heroIconName: String
    public var title: String
    public var subtitle: String
    public var bodyText: String
    public var primaryActionLabel: String
    public var secondaryActionLabel: String
    /// Price or rating badge text shown next to title (may be empty).
    public var badgeText: String
    public var colorScheme: ColorScheme

    public init(
        heroHue: Double,
        heroIconName: String,
        title: String,
        subtitle: String,
        bodyText: String,
        primaryActionLabel: String,
        secondaryActionLabel: String,
        badgeText: String,
        colorScheme: ColorScheme
    ) {
        self.heroHue = heroHue
        self.heroIconName = heroIconName
        self.title = title
        self.subtitle = subtitle
        self.bodyText = bodyText
        self.primaryActionLabel = primaryActionLabel
        self.secondaryActionLabel = secondaryActionLabel
        self.badgeText = badgeText
        self.colorScheme = colorScheme
    }

    private static let heroIcons = [
        "mountain.2.fill", "flame.fill", "leaf.fill", "drop.fill",
        "star.fill", "moon.fill", "cloud.fill", "bolt.fill",
        "globe.americas.fill", "heart.fill",
    ]
    private static let primaryLabels = ["Get", "Buy Now", "Install", "Download", "Subscribe", "Join"]
    private static let secondaryLabels = ["Share", "Save", "Bookmark", "Add to List", "Preview"]
    private static let bodies = [
        "A complete solution for professionals who need precise control and fast results.",
        "Designed from the ground up with simplicity in mind. Everything you need, nothing you don't.",
        "Award-winning performance with best-in-class accuracy across all supported platforms.",
        "Trusted by over a million users worldwide. Continuously updated with new features.",
    ]

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> CardDetailConfig {
        var rng = SeededRNG(seed: seed)
        let dark    = rng.next() % 2 == 0
        let heroHue = Double(rng.next() % 1000) / 1000.0
        let icon    = heroIcons[Int(rng.next() % UInt64(heroIcons.count))]
        let primary = primaryLabels[Int(rng.next() % UInt64(primaryLabels.count))]
        let secondary = secondaryLabels[Int(rng.next() % UInt64(secondaryLabels.count))]
        let body    = bodies[Int(rng.next() % UInt64(bodies.count))]
        let hasBadge = rng.next() % 2 == 0
        let badge   = hasBadge ? corpus.price(currency: .usd) : ""
        return CardDetailConfig(
            heroHue: heroHue,
            heroIconName: icon,
            title: corpus.listRowTitle(),
            subtitle: corpus.companyName(),
            bodyText: body,
            primaryActionLabel: primary,
            secondaryActionLabel: secondary,
            badgeText: badge,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - CardDetailTemplate

public struct CardDetailTemplate: View {
    public let config: CardDetailConfig

    public init(config: CardDetailConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            Color(UIColor.systemBackground).ignoresSafeArea()

            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // Full-bleed hero image
                    ZStack {
                        Color(hue: config.heroHue, saturation: 0.55, brightness: 0.65)
                        Image(systemName: config.heroIconName)
                            .font(.system(size: 72))
                            .foregroundStyle(.white.opacity(0.8))
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 260)
                    .captureFrame(id: "imageView_hero")

                    // Detail content
                    VStack(alignment: .leading, spacing: 12) {
                        // Title + badge row
                        HStack(alignment: .firstTextBaseline) {
                            Text(config.title)
                                .font(.title2.bold())
                                .captureFrame(id: "label_title")
                            Spacer()
                            if !config.badgeText.isEmpty {
                                Text(config.badgeText)
                                    .font(.subheadline.bold())
                                    .foregroundStyle(Color.accentColor)
                                    .captureFrame(id: "label_badge")
                            }
                        }

                        Text(config.subtitle)
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                            .captureFrame(id: "label_subtitle")

                        Divider()

                        Text(config.bodyText)
                            .font(.body)
                            .foregroundStyle(.primary.opacity(0.85))
                            .captureFrame(id: "label_body")

                        // Action buttons
                        HStack(spacing: 12) {
                            Button(config.primaryActionLabel) {}
                                .font(.body.bold())
                                .frame(maxWidth: .infinity, minHeight: 50)
                                .background(Color.accentColor)
                                .foregroundStyle(.white)
                                .clipShape(RoundedRectangle(cornerRadius: 12))
                                .captureFrame(id: "primaryButton_0")

                            Button(config.secondaryActionLabel) {}
                                .font(.body)
                                .frame(maxWidth: .infinity, minHeight: 50)
                                .background(Color.secondary.opacity(0.15))
                                .foregroundStyle(.primary)
                                .clipShape(RoundedRectangle(cornerRadius: 12))
                                .captureFrame(id: "secondaryButton_0")
                        }
                        .padding(.top, 4)
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 20)
                    .padding(.bottom, 48)
                }
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}
