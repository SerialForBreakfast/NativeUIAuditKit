// LiquidGlassNavTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI Liquid Glass iOS 26 navbar template (TASK-5b-13).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// Annotated elements:
//   navigationBar (auto-detected, Liquid Glass profile) — BP-17
//   primaryButton — action button in the content area
//   label         — content labels below the navbar
//
// This template uses .ios26 OSVisualProfile to exercise the Liquid Glass
// navigation bar visual style (tabBarStyle: .liquidGlass, navBarStyle: .liquidGlass).
// The training-data strategy mandates ≥10 dedicated Liquid Glass templates
// (Research/TrainingDataStrategy.md Section 5).
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - LiquidGlassNavConfig

/// Parameterised inputs for a single LiquidGlassNav rendering.
public struct LiquidGlassNavConfig: Sendable {
    /// Navigation bar title.
    public var title: String
    /// Content area labels (3–6 items).
    public var contentLabels: [String]
    /// Primary button label.
    public var primaryButtonLabel: String
    /// Tint color hue (0–1) — drives accent colour + background image tint.
    public var hue: Double
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        title: String,
        contentLabels: [String],
        primaryButtonLabel: String,
        hue: Double,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.contentLabels = contentLabels
        self.primaryButtonLabel = primaryButtonLabel
        self.hue = hue
        self.colorScheme = colorScheme
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> LiquidGlassNavConfig {
        var rng = SeededRNG(seed: seed)
        let dark       = rng.next() % 2 == 0
        let labelCount = 3 + Int(rng.next() % 4)   // 3–6 labels
        let hue        = Double(rng.next() % 1000) / 1000.0

        var labels: [String] = []
        for _ in 0..<labelCount { labels.append(corpus.listRowTitle()) }

        return LiquidGlassNavConfig(
            title: corpus.navigationTitle(),
            contentLabels: labels,
            primaryButtonLabel: corpus.buttonLabel(),
            hue: hue,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - LiquidGlassNavTemplate

/// SwiftUI view rendering a content screen with iOS 26 Liquid Glass navigation bar.
///
/// The Liquid Glass visual style is applied when rendered on the .ios26 OSVisualProfile.
/// From a generator perspective the view is structurally identical to a standard
/// NavigationStack — the visual difference (blur, translucency, rounded pill) is
/// provided by the system at render time.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct LiquidGlassNavTemplate: View {
    public let config: LiquidGlassNavConfig

    public init(config: LiquidGlassNavConfig) {
        self.config = config
    }

    private var accentColor: Color {
        Color(hue: config.hue, saturation: 0.7, brightness: 0.85)
    }

    public var body: some View {
        NavigationStack {
            ZStack(alignment: .topLeading) {
                // Colourful background gradient — exercises Liquid Glass translucency
                LinearGradient(
                    colors: [
                        Color(hue: config.hue, saturation: 0.4, brightness: 0.95),
                        Color(hue: (config.hue + 0.15).truncatingRemainder(dividingBy: 1.0),
                              saturation: 0.3, brightness: 0.90),
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()

                VStack(alignment: .leading, spacing: 0) {
                    ForEach(Array(config.contentLabels.enumerated()), id: \.offset) { idx, label in
                        Text(label)
                            .font(.body)
                            .captureFrame(id: "label_\(idx)")
                            .padding(.horizontal, 20)
                            .padding(.top, 16)
                    }

                    Spacer()

                    Button(config.primaryButtonLabel) {}
                        .frame(maxWidth: .infinity, minHeight: 50)
                        .background(accentColor)
                        .foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                        .captureFrame(id: "primaryButton_0")
                        .padding(.horizontal, 20)
                        .padding(.bottom, 40)
                }
            }
            .ignoresSafeArea(.all)
            .navigationTitle(config.title)
            .navigationBarTitleDisplayMode(.large)
            .colorScheme(config.colorScheme)
        }
        // navigationBar auto-detected by ScreenshotCapture.detectChromeFrames (BP-17).
        .colorScheme(config.colorScheme)
    }
}
