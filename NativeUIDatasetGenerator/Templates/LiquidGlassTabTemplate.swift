// LiquidGlassTabTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI Liquid Glass iOS 26 tab bar template (TASK-5b-14).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// Annotated elements:
//   tabBar        — auto-detected (Liquid Glass pill style on .ios26 profile) (BP-17)
//   tabBarItem_N  — auto-detected (BP-17)
//   navigationBar — auto-detected (BP-17)
//   homeIndicator — manual Capsule at bottom (BP-18)
//
// The Liquid Glass tab bar pill style is rendered by the system on iOS 26.
// This template provides the correct structural context so that auto-detection
// captures the pill-shaped tab bar accurately.
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - LiquidGlassTabConfig

/// Parameterised inputs for a single LiquidGlassTab rendering.
public struct LiquidGlassTabConfig: Sendable {
    /// Navigation bar title for the first tab.
    public var title: String
    /// Row labels in the first tab's list (3–6 items).
    public var rowLabels: [String]
    /// Number of tab items (3 or 5).
    public var tabBarItemCount: Int
    /// When true, render home indicator pill at bottom.
    public var showHomeIndicator: Bool
    /// Background gradient hue (0–1).
    public var hue: Double
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        title: String,
        rowLabels: [String],
        tabBarItemCount: Int,
        showHomeIndicator: Bool,
        hue: Double,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.rowLabels = rowLabels
        self.tabBarItemCount = tabBarItemCount
        self.showHomeIndicator = showHomeIndicator
        self.hue = hue
        self.colorScheme = colorScheme
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(
        seed: UInt64,
        corpus: inout ContentCorpus,
        osProfile: OSVisualProfile
    ) -> LiquidGlassTabConfig {
        var rng = SeededRNG(seed: seed)
        let dark      = rng.next() % 2 == 0
        let tabCount  = rng.next() % 2 == 0 ? 3 : 5
        let rowCount  = 3 + Int(rng.next() % 4)   // 3–6 rows
        let hue       = Double(rng.next() % 1000) / 1000.0

        var rows: [String] = []
        for _ in 0..<rowCount { rows.append(corpus.listRowTitle()) }

        return LiquidGlassTabConfig(
            title: corpus.navigationTitle(),
            rowLabels: rows,
            tabBarItemCount: tabCount,
            showHomeIndicator: osProfile.hasHomeIndicator,
            hue: hue,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - LiquidGlassTabTemplate

/// SwiftUI view rendering a tab view with iOS 26 Liquid Glass tab bar.
///
/// Structurally identical to TabViewNavigationTemplate, but always uses a
/// colourful background gradient to exercise Liquid Glass translucency.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct LiquidGlassTabTemplate: View {
    public let config: LiquidGlassTabConfig

    public init(config: LiquidGlassTabConfig) {
        self.config = config
    }

    private static let tabItems3: [(String, String)] = [
        ("house", "Home"), ("magnifyingglass", "Search"), ("person", "Profile"),
    ]
    private static let tabItems5: [(String, String)] = [
        ("house", "Home"), ("magnifyingglass", "Search"), ("bell", "Alerts"),
        ("bookmark", "Saved"), ("person", "Profile"),
    ]

    private var tabItems: [(String, String)] {
        config.tabBarItemCount >= 5 ? Self.tabItems5 : Self.tabItems3
    }

    public var body: some View {
        ZStack(alignment: .top) {
            TabView {
                // Tab 0: Content with gradient background
                NavigationStack {
                    ZStack(alignment: .topLeading) {
                        LinearGradient(
                            colors: [
                                Color(hue: config.hue, saturation: 0.5, brightness: 0.92),
                                Color(hue: (config.hue + 0.12).truncatingRemainder(dividingBy: 1.0),
                                      saturation: 0.35, brightness: 0.88),
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                        .ignoresSafeArea()

                        List {
                            ForEach(Array(config.rowLabels.enumerated()), id: \.offset) { idx, label in
                                Text(label)
                                    .captureFrame(id: "listRow_\(idx)")
                            }
                        }
                        .scrollContentBackground(.hidden)
                        .listStyle(.insetGrouped)
                    }
                    .ignoresSafeArea(.all)
                    .navigationTitle(config.title)
                    .navigationBarTitleDisplayMode(.large)
                    .colorScheme(config.colorScheme)
                }
                .tabItem { Label(tabItems[0].1, systemImage: tabItems[0].0) }

                // Remaining tabs: placeholder
                ForEach(1..<tabItems.count, id: \.self) { idx in
                    NavigationStack {
                        Text(tabItems[idx].1)
                            .font(.title2)
                            .foregroundStyle(.secondary)
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                            .navigationTitle(tabItems[idx].1)
                            .navigationBarTitleDisplayMode(.inline)
                    }
                    .tabItem { Label(tabItems[idx].1, systemImage: tabItems[idx].0) }
                }
            }
            // tabBar and tabBarItem_N auto-detected by ScreenshotCapture (BP-17).
            .colorScheme(config.colorScheme)
            .ignoresSafeArea(.all)

            // Home indicator pill
            if config.showHomeIndicator {
                VStack(spacing: 0) {
                    Spacer()
                    Capsule()
                        .fill(Color.primary.opacity(0.3))
                        .frame(width: 134, height: 5)
                        .captureFrame(id: "homeIndicator")
                        .padding(.bottom, 8)
                }
                .frame(maxWidth: .infinity)
                .allowsHitTesting(false)
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}
