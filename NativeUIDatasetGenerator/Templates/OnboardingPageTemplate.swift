// OnboardingPageTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI onboarding page template (TASK-5b-8).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// Annotated elements:
//   pageControl   — the dot indicator row at the bottom of the hero section
//   primaryButton — "Continue" / "Get Started" CTA
//   imageView     — the hero illustration (large SF Symbol)
//   label         — title and body copy labels
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - OnboardingPageConfig

/// Parameterised inputs for a single OnboardingPage rendering.
public struct OnboardingPageConfig: Sendable {
    /// SF Symbol name for the hero image.
    public var symbolName: String
    /// Hero background hue (0–1).
    public var heroBgHue: Double
    /// Onboarding page title.
    public var title: String
    /// Onboarding page body text.
    public var body: String
    /// Primary button label ("Continue" or "Get Started").
    public var primaryButtonLabel: String
    /// Total number of onboarding pages (for page control dots).
    public var totalPages: Int
    /// Currently active page (0-based).
    public var currentPage: Int
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        symbolName: String,
        heroBgHue: Double,
        title: String,
        body: String,
        primaryButtonLabel: String,
        totalPages: Int,
        currentPage: Int,
        colorScheme: ColorScheme
    ) {
        self.symbolName = symbolName
        self.heroBgHue = heroBgHue
        self.title = title
        self.body = body
        self.primaryButtonLabel = primaryButtonLabel
        self.totalPages = totalPages
        self.currentPage = currentPage
        self.colorScheme = colorScheme
    }

    private static let symbols = [
        "sparkles", "heart.fill", "bolt.fill", "star.fill",
        "globe", "lock.shield.fill", "checkmark.seal.fill",
        "person.3.fill", "chart.bar.fill", "wand.and.stars",
    ]

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> OnboardingPageConfig {
        var rng = SeededRNG(seed: seed)
        let dark        = rng.next() % 2 == 0
        let symIdx      = Int(rng.next() % UInt64(symbols.count))
        let heroBgHue   = Double(rng.next() % 1000) / 1000.0
        let totalPages  = 3 + Int(rng.next() % 3)   // 3–5 pages
        let currentPage = Int(rng.next() % UInt64(totalPages))
        let isLast      = currentPage == totalPages - 1

        return OnboardingPageConfig(
            symbolName: symbols[symIdx],
            heroBgHue: heroBgHue,
            title: corpus.navigationTitle(),
            body: corpus.listRowTitle(),
            primaryButtonLabel: isLast ? "Get Started" : "Continue",
            totalPages: totalPages,
            currentPage: currentPage,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - OnboardingPageTemplate

/// SwiftUI view rendering a single onboarding page with hero illustration,
/// page control, and a primary CTA.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct OnboardingPageTemplate: View {
    public let config: OnboardingPageConfig

    public init(config: OnboardingPageConfig) {
        self.config = config
    }

    private var heroBgColor: Color {
        Color(hue: config.heroBgHue, saturation: 0.6, brightness: 0.80)
    }

    public var body: some View {
        ZStack {
            Color(UIColor.systemBackground).ignoresSafeArea()

            VStack(spacing: 0) {
                // Hero section with gradient background
                ZStack {
                    heroBgColor.ignoresSafeArea(edges: .top)

                    Image(systemName: config.symbolName)
                        .resizable()
                        .scaledToFit()
                        .frame(width: 110, height: 110)
                        .foregroundStyle(.white)
                        .captureFrame(id: "imageView_hero")
                }
                .frame(maxWidth: .infinity)
                .frame(height: UIScreen.main.bounds.height * 0.42)

                // Page control dots — manual implementation using HStack of circles
                // (UIPageControl equivalent).
                HStack(spacing: 8) {
                    ForEach(0..<config.totalPages, id: \.self) { idx in
                        Circle()
                            .fill(idx == config.currentPage
                                ? Color.accentColor
                                : Color.secondary.opacity(0.3))
                            .frame(width: idx == config.currentPage ? 10 : 7,
                                   height: idx == config.currentPage ? 10 : 7)
                    }
                }
                .captureFrame(id: "pageControl_0")
                .padding(.top, 24)

                // Title label
                Text(config.title)
                    .font(.title.bold())
                    .multilineTextAlignment(.center)
                    .captureFrame(id: "label_title")
                    .padding(.horizontal, 32)
                    .padding(.top, 16)

                // Body label
                Text(config.body)
                    .font(.body)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .captureFrame(id: "label_body")
                    .padding(.horizontal, 32)
                    .padding(.top, 10)

                Spacer()

                // Primary button
                Button(config.primaryButtonLabel) {}
                    .frame(maxWidth: .infinity, minHeight: 52)
                    .background(Color.accentColor)
                    .foregroundStyle(.white)
                    .clipShape(RoundedRectangle(cornerRadius: 14))
                    .captureFrame(id: "primaryButton_0")
                    .padding(.horizontal, 32)
                    .padding(.bottom, 48)
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}
