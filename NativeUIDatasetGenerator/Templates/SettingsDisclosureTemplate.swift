// SettingsDisclosureTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI settings-with-disclosure-groups template (TASK-5b-15).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// Annotated elements:
//   navigationBar    — auto-detected (BP-17)
//   disclosureGroup  — each expandable section header row
//   listRow          — items inside expanded disclosure groups + plain rows
//   toggle           — toggle controls in settings rows
//   label            — section headers and row text labels
//
// Distinct from SettingsListTemplate: focuses on multiple nested disclosure groups
// in both expanded and collapsed states, more variety in expansion patterns.
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - DisclosureGroupConfig

/// One expandable section in the settings list.
public struct DisclosureGroupConfig: Sendable {
    public var header: String
    public var items: [String]
    public var isExpanded: Bool

    public init(header: String, items: [String], isExpanded: Bool) {
        self.header = header
        self.items = items
        self.isExpanded = isExpanded
    }
}

// MARK: - SettingsDisclosureConfig

/// Parameterised inputs for a single SettingsDisclosure rendering.
public struct SettingsDisclosureConfig: Sendable {
    /// Navigation bar title.
    public var title: String
    /// Disclosure group sections (2–4 groups).
    public var groups: [DisclosureGroupConfig]
    /// Standalone toggle labels at the top (1–3 items).
    public var toggleLabels: [String]
    /// Whether standalone toggles are on/off (index-based).
    public var toggleStates: [Bool]
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        title: String,
        groups: [DisclosureGroupConfig],
        toggleLabels: [String],
        toggleStates: [Bool],
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.groups = groups
        self.toggleLabels = toggleLabels
        self.toggleStates = toggleStates
        self.colorScheme = colorScheme
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> SettingsDisclosureConfig {
        var rng = SeededRNG(seed: seed)
        let dark         = rng.next() % 2 == 0
        let groupCount   = 2 + Int(rng.next() % 3)   // 2–4 groups
        let toggleCount  = 1 + Int(rng.next() % 3)   // 1–3 toggles

        var groups: [DisclosureGroupConfig] = []
        for _ in 0..<groupCount {
            let itemCount = 2 + Int(rng.next() % 3)   // 2–4 items
            let expanded  = rng.next() % 2 == 0
            var items: [String] = []
            for _ in 0..<itemCount { items.append(corpus.listRowTitle()) }
            groups.append(DisclosureGroupConfig(
                header: corpus.listRowTitle(),
                items: items,
                isExpanded: expanded
            ))
        }

        var toggleLabels: [String] = []
        var toggleStates: [Bool] = []
        for idx in 0..<toggleCount {
            toggleLabels.append(corpus.listRowTitle())
            toggleStates.append(idx % 2 == 0)
        }

        return SettingsDisclosureConfig(
            title: corpus.navigationTitle(),
            groups: groups,
            toggleLabels: toggleLabels,
            toggleStates: toggleStates,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - SettingsDisclosureTemplate

/// SwiftUI view rendering a settings screen with multiple disclosure groups.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct SettingsDisclosureTemplate: View {
    public let config: SettingsDisclosureConfig

    public init(config: SettingsDisclosureConfig) {
        self.config = config
    }

    public var body: some View {
        NavigationStack {
            ZStack(alignment: .topLeading) {
                List {
                    // Standalone toggle section
                    Section {
                        ForEach(Array(config.toggleLabels.enumerated()), id: \.offset) { idx, label in
                            HStack {
                                Text(label)
                                    .captureFrame(id: "label_toggle_\(idx)")
                                Spacer()
                                Toggle("", isOn: .constant(config.toggleStates[idx]))
                                    .labelsHidden()
                                    .captureFrame(id: "toggle_\(idx)")
                            }
                            .captureFrame(id: "listRow_toggle_\(idx)")
                        }
                    }

                    // Disclosure group sections
                    ForEach(Array(config.groups.enumerated()), id: \.offset) { gIdx, group in
                        Section {
                            DisclosureGroup(
                                isExpanded: .constant(group.isExpanded)
                            ) {
                                ForEach(Array(group.items.enumerated()), id: \.offset) { iIdx, item in
                                    Text(item)
                                        .captureFrame(id: "listRow_g\(gIdx)_\(iIdx)")
                                }
                            } label: {
                                Text(group.header)
                                    .captureFrame(id: "label_group_\(gIdx)")
                            }
                            .captureFrame(id: "disclosureGroup_\(gIdx)")
                        }
                    }
                }
                .listStyle(.insetGrouped)
            }
            .ignoresSafeArea(.all)
            .navigationTitle(config.title)
            .navigationBarTitleDisplayMode(.large)
            .colorScheme(config.colorScheme)
        }
        .colorScheme(config.colorScheme)
    }
}
