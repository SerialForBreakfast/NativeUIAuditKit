// EmptyStateTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI empty state template (TASK-5b-5).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// Annotated elements:
//   primaryButton — main CTA ("Get Started", "Try Again", etc.)
//   imageView     — the hero illustration (SF Symbol glyph in a large frame)
//   label         — title and body copy labels
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - EmptyStateConfig

/// Parameterised inputs for a single EmptyState rendering.
public struct EmptyStateConfig: Sendable {
    /// Large SF Symbol name for the hero image.
    public var symbolName: String
    /// Title text.
    public var title: String
    /// Body copy text.
    public var body: String
    /// Primary button label.
    public var primaryButtonLabel: String
    /// Tint color hue (0–1).
    public var hue: Double
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        symbolName: String,
        title: String,
        body: String,
        primaryButtonLabel: String,
        hue: Double,
        colorScheme: ColorScheme
    ) {
        self.symbolName = symbolName
        self.title = title
        self.body = body
        self.primaryButtonLabel = primaryButtonLabel
        self.hue = hue
        self.colorScheme = colorScheme
    }

    // SF Symbol names varied across seeds.
    private static let symbols = [
        "tray", "folder", "doc", "photo", "bookmark",
        "bell", "star", "magnifyingglass", "cart", "heart",
        "wifi.slash", "cloud", "person.crop.circle", "mappin",
    ]

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> EmptyStateConfig {
        var rng = SeededRNG(seed: seed)
        let dark     = rng.next() % 2 == 0
        let symIdx   = Int(rng.next() % UInt64(symbols.count))
        let hue      = Double(rng.next() % 1000) / 1000.0
        let hasBody  = rng.next() % 4 != 0  // ~75% show body text

        return EmptyStateConfig(
            symbolName: symbols[symIdx],
            title: corpus.navigationTitle(),
            body: hasBody ? corpus.listRowTitle() : "",
            primaryButtonLabel: corpus.buttonLabel(),
            hue: hue,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - EmptyStateTemplate

/// SwiftUI view rendering an empty state screen with hero image, title,
/// body text, and a primary CTA button.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct EmptyStateTemplate: View {
    public let config: EmptyStateConfig

    public init(config: EmptyStateConfig) {
        self.config = config
    }

    private var tintColor: Color {
        Color(hue: config.hue, saturation: 0.7, brightness: 0.85)
    }

    public var body: some View {
        ZStack {
            Color(UIColor.systemBackground).ignoresSafeArea()

            VStack(spacing: 0) {
                Spacer()

                // Hero image — large SF Symbol glyph
                Image(systemName: config.symbolName)
                    .resizable()
                    .scaledToFit()
                    .frame(width: 96, height: 96)
                    .foregroundStyle(tintColor)
                    .captureFrame(id: "imageView_hero")
                    .padding(.bottom, 28)

                // Title label
                Text(config.title)
                    .font(.title2.bold())
                    .multilineTextAlignment(.center)
                    .captureFrame(id: "label_title")
                    .padding(.horizontal, 40)

                // Body label (conditional)
                if !config.body.isEmpty {
                    Text(config.body)
                        .font(.body)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                        .captureFrame(id: "label_body")
                        .padding(.horizontal, 40)
                        .padding(.top, 12)
                }

                Spacer().frame(height: 40)

                // Primary button
                Button(config.primaryButtonLabel) {}
                    .frame(maxWidth: .infinity, minHeight: 50)
                    .background(tintColor)
                    .foregroundStyle(.white)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .captureFrame(id: "primaryButton_0")
                    .padding(.horizontal, 40)

                Spacer()
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}
