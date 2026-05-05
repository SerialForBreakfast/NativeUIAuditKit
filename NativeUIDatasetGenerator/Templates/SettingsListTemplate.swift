// SettingsListTemplate.swift
// NativeUIDatasetGenerator — Phase 3c-2
//
// Parameterised SwiftUI settings list template.
// Produces training images containing:
//   navigationBar, tabBar, toggle, listRow, disclosureGroup, label, homeIndicator
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:)
//
// Parameter sweep: 2 color schemes × 3 DynamicType sizes × 2 device sizes = 12 variants.

import SwiftUI

// MARK: - SettingsListConfig

/// Parameterised inputs for a single SettingsList rendering.
public struct SettingsListConfig: Sendable {
    /// Navigation bar title.
    public var title: String
    /// Labels for the toggle rows (2–5 items).
    public var toggleRowLabels: [String]
    /// Labels for the plain list rows (3–8 items).
    public var listRowLabels: [String]
    /// Labels for items in the DisclosureGroup.
    public var disclosureGroupItems: [String]
    /// When `true`, the DisclosureGroup is rendered in expanded state.
    public var disclosureGroupExpanded: Bool
    /// Number of items in the tab bar (3 or 5).
    public var tabBarItemCount: Int
    /// When `true`, a home indicator pill is drawn at the bottom.
    public var showHomeIndicator: Bool
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        title: String,
        toggleRowLabels: [String],
        listRowLabels: [String],
        disclosureGroupItems: [String],
        disclosureGroupExpanded: Bool,
        tabBarItemCount: Int,
        showHomeIndicator: Bool,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.toggleRowLabels = toggleRowLabels
        self.listRowLabels = listRowLabels
        self.disclosureGroupItems = disclosureGroupItems
        self.disclosureGroupExpanded = disclosureGroupExpanded
        self.tabBarItemCount = tabBarItemCount
        self.showHomeIndicator = showHomeIndicator
        self.colorScheme = colorScheme
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(
        seed: UInt64,
        corpus: inout ContentCorpus,
        hasHomeIndicator: Bool
    ) -> SettingsListConfig {
        var rng = SeededRNG(seed: seed)

        let toggleCount = 2 + Int(rng.next() % 4)   // 2–5
        let listCount   = 3 + Int(rng.next() % 6)   // 3–8
        let expanded    = rng.next() % 2 == 0
        let tabCount    = rng.next() % 2 == 0 ? 3 : 5
        let dark        = rng.next() % 2 == 0

        var toggleLabels: [String] = []
        for _ in 0..<toggleCount { toggleLabels.append(corpus.listRowTitle()) }

        var rowLabels: [String] = []
        for _ in 0..<listCount { rowLabels.append(corpus.listRowTitle()) }

        let disclosureItems = [corpus.listRowTitle(), corpus.listRowTitle(), corpus.listRowTitle()]

        return SettingsListConfig(
            title: corpus.navigationTitle(),
            toggleRowLabels: toggleLabels,
            listRowLabels: rowLabels,
            disclosureGroupItems: disclosureItems,
            disclosureGroupExpanded: expanded,
            tabBarItemCount: tabCount,
            showHomeIndicator: hasHomeIndicator,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - SettingsListTemplate

/// SwiftUI view rendering a settings screen and annotating UI elements via `.captureFrame(id:)`.
///
/// **Annotated elements:** `navigationBar`, `tabBar`, `toggle`, `listRow`,
/// `disclosureGroup`, `label`, `homeIndicator` (when device has one).
public struct SettingsListTemplate: View {
    public let config: SettingsListConfig

    public init(config: SettingsListConfig) {
        self.config = config
    }

    #if canImport(UIKit)
    public var body: some View {
        TabView {
            NavigationStack {
                ZStack(alignment: .topLeading) {
                    List {
                        // Toggle rows
                        Section {
                            ForEach(Array(config.toggleRowLabels.enumerated()), id: \.offset) { idx, label in
                                HStack {
                                    Text(label)
                                        .captureFrame(id: "label_toggle_\(idx)")
                                    Spacer()
                                    Toggle("", isOn: .constant(idx % 2 == 0))
                                        .labelsHidden()
                                        .captureFrame(id: "toggle_\(idx)")
                                }
                                .captureFrame(id: "listRow_toggle_\(idx)")
                            }
                        }

                        // Disclosure group
                        Section {
                            DisclosureGroup(
                                isExpanded: .constant(config.disclosureGroupExpanded)
                            ) {
                                ForEach(
                                    Array(config.disclosureGroupItems.enumerated()),
                                    id: \.offset
                                ) { idx, item in
                                    Text(item)
                                        .captureFrame(id: "listRow_disclosureItem_\(idx)")
                                }
                            } label: {
                                Text("More Options")
                                    .captureFrame(id: "label_disclosureHeader")
                            }
                            .captureFrame(id: "disclosureGroup_0")
                        }

                        // Plain list rows
                        Section {
                            ForEach(Array(config.listRowLabels.enumerated()), id: \.offset) { idx, label in
                                Text(label)
                                    .captureFrame(id: "listRow_plain_\(idx)")
                            }
                        }
                    }
                    #if os(iOS)
                    .listStyle(.insetGrouped)
                    #endif

                    // Home indicator pill (when device profile has one)
                    if config.showHomeIndicator {
                        VStack {
                            Spacer()
                            Capsule()
                                .fill(Color.primary.opacity(0.3))
                                .frame(width: 134, height: 5)
                                .padding(.bottom, 8)
                                .captureFrame(id: "homeIndicator")
                        }
                        .frame(maxWidth: .infinity)
                    }
                }
                .ignoresSafeArea(.all)
                .navigationTitle(config.title)
                #if os(iOS)
                .navigationBarTitleDisplayMode(.large)
                #endif
                .colorScheme(config.colorScheme)
            }
            .captureFrame(id: "navigationBar")
            .tabItem {
                Label("Settings", systemImage: "gear")
            }

            if config.tabBarItemCount >= 5 {
                Text("").tabItem { Label("Home",    systemImage: "house") }
                Text("").tabItem { Label("Search",  systemImage: "magnifyingglass") }
                Text("").tabItem { Label("Profile", systemImage: "person") }
                Text("").tabItem { Label("More",    systemImage: "ellipsis") }
            } else {
                Text("").tabItem { Label("Home",    systemImage: "house") }
                Text("").tabItem { Label("Profile", systemImage: "person") }
            }
        }
        .captureFrame(id: "tabBar")
        .colorScheme(config.colorScheme)
    }
    #else
    // macOS compilation stub — SettingsListTemplate runs only in iOS Simulator context.
    public var body: some View { EmptyView() }
    #endif
}
