// TabViewNavigationTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI tab-view-with-navigation template (TASK-5b-1).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
// No platform guards needed — this file never compiles on macOS.
//
// Annotated elements:
//   navigationBar  — auto-detected via UIKit scan in ScreenshotCapture (BP-17)
//   tabBar         — auto-detected via UIKit scan in ScreenshotCapture (BP-17)
//   tabBarItem_N   — auto-detected (N = 0…tabCount-1)
//   homeIndicator  — manual Capsule drawn at safe-area bottom (BP-18)
//   dynamicIsland  — manual pill drawn at safe-area top (BP-18); only when
//                    config.showDynamicIsland == true (i.e. .ios26 profile)
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All element offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout-spacing padding (BP-18)
//
// Parameter sweep: 2 color schemes × navTitleStyle (large/inline) × tabCount (3/5) ×
//                  2 device sizes (ios26/ios17) = 24 structural variants minimum.

import SwiftUI
import UIKit

// MARK: - TabViewNavigationConfig

/// Parameterised inputs for a single TabViewNavigation rendering.
public struct TabViewNavigationConfig: Sendable {
    /// Navigation bar title.
    public var title: String
    /// When true, large title style; when false, inline.
    public var largeTitleStyle: Bool
    /// Number of tab bar items (3 or 5).
    public var tabBarItemCount: Int
    /// Row content for the first tab's list.
    public var rowLabels: [String]
    /// When true, render Dynamic Island pill at top of screen.
    public var showDynamicIsland: Bool
    /// When true, render home indicator pill at bottom of screen.
    public var showHomeIndicator: Bool
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme
    /// Which tab is selected (0-based).
    public var selectedTab: Int

    public init(
        title: String,
        largeTitleStyle: Bool,
        tabBarItemCount: Int,
        rowLabels: [String],
        showDynamicIsland: Bool,
        showHomeIndicator: Bool,
        colorScheme: ColorScheme,
        selectedTab: Int
    ) {
        self.title = title
        self.largeTitleStyle = largeTitleStyle
        self.tabBarItemCount = tabBarItemCount
        self.rowLabels = rowLabels
        self.showDynamicIsland = showDynamicIsland
        self.showHomeIndicator = showHomeIndicator
        self.colorScheme = colorScheme
        self.selectedTab = selectedTab
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(
        seed: UInt64,
        corpus: inout ContentCorpus,
        osProfile: OSVisualProfile
    ) -> TabViewNavigationConfig {
        var rng = SeededRNG(seed: seed)
        let largeTitle  = rng.next() % 2 == 0
        let tabCount    = rng.next() % 2 == 0 ? 3 : 5
        let dark        = rng.next() % 2 == 0
        let rowCount    = 3 + Int(rng.next() % 5)   // 3–7 rows
        let selectedTab = Int(rng.next() % UInt64(tabCount))

        var rows: [String] = []
        for _ in 0..<rowCount { rows.append(corpus.listRowTitle()) }

        return TabViewNavigationConfig(
            title: corpus.navigationTitle(),
            largeTitleStyle: largeTitle,
            tabBarItemCount: tabCount,
            rowLabels: rows,
            showDynamicIsland: osProfile.hasDynamicIsland,
            showHomeIndicator: osProfile.hasHomeIndicator,
            colorScheme: dark ? .dark : .light,
            selectedTab: selectedTab
        )
    }
}

// MARK: - TabViewNavigationTemplate

/// SwiftUI view rendering a tab view with a navigation stack in the first tab.
/// Demonstrates `tabBar`, `navigationBar`, `homeIndicator`, and `dynamicIsland`
/// chrome elements in a realistic multi-tab layout.
///
/// **Platform scope:** iOS GeneratorRunner target only.
///
/// **Chrome note:** `navigationBar`, `tabBar`, and `tabBarItem_N` are captured
/// automatically by `ScreenshotCapture.detectChromeFrames` (BP-17).
/// `homeIndicator` and `dynamicIsland` are manually drawn and annotated here.
public struct TabViewNavigationTemplate: View {
    public let config: TabViewNavigationConfig

    public init(config: TabViewNavigationConfig) {
        self.config = config
    }

    // SF Symbol names for tab items; first tab is always the active content tab.
    private static let tabSymbols3: [(String, String)] = [
        ("house",           "Home"),
        ("magnifyingglass", "Search"),
        ("person",          "Profile"),
    ]
    private static let tabSymbols5: [(String, String)] = [
        ("house",           "Home"),
        ("magnifyingglass", "Search"),
        ("bell",            "Alerts"),
        ("bookmark",        "Saved"),
        ("person",          "Profile"),
    ]

    private var tabItems: [(String, String)] {
        config.tabBarItemCount >= 5 ? Self.tabSymbols5 : Self.tabSymbols3
    }

    public var body: some View {
        ZStack(alignment: .top) {
            TabView(selection: .constant(config.selectedTab)) {
                // Tab 0: Navigation stack with list content
                NavigationStack {
                    ZStack(alignment: .topLeading) {
                        List {
                            ForEach(Array(config.rowLabels.enumerated()), id: \.offset) { idx, label in
                                Text(label)
                                    .captureFrame(id: "listRow_\(idx)")
                            }
                        }
                        .listStyle(.insetGrouped)
                    }
                    .ignoresSafeArea(.all)
                    .navigationTitle(config.title)
                    .navigationBarTitleDisplayMode(
                        config.largeTitleStyle ? .large : .inline
                    )
                    .colorScheme(config.colorScheme)
                }
                .tabItem { Label(tabItems[0].1, systemImage: tabItems[0].0) }
                .tag(0)

                // Remaining tabs: placeholder content
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
                    .tag(idx)
                }
            }
            // tabBar and tabBarItem_N are auto-detected by ScreenshotCapture (BP-17).
            .colorScheme(config.colorScheme)
            .ignoresSafeArea(.all)

            // MARK: Overlay: Dynamic Island pill
            // Drawn over the tab content, centred at the top.
            // captureFrame before any padding (BP-18).
            if config.showDynamicIsland {
                VStack(spacing: 0) {
                    RoundedRectangle(cornerRadius: 18)
                        .fill(Color.black)
                        .frame(width: 126, height: 37)
                        .captureFrame(id: "dynamicIsland")
                        .padding(.top, 14)
                    Spacer()
                }
                .frame(maxWidth: .infinity)
                .allowsHitTesting(false)
            }

            // MARK: Overlay: Home indicator pill
            // Centred, above safe-area bottom.
            // captureFrame before padding (BP-18).
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
