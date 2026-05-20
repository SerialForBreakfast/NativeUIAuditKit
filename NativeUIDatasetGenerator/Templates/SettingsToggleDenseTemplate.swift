// SettingsToggleDenseTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised dense toggle-only settings template (TASK-5b-22).
// Structural distinction: whereas SettingsListTemplate mixes multiple element types,
// this template generates a screen dominated by `toggle` controls — maximising
// per-class instance count for `toggle` without co-occurrence bias from other elements.
// Also exercises the on/off label variant and disabled toggle states.
//
// Annotated elements:
//   toggle        — on/off switch controls (6–12 per screen)
//   label         — section header and per-toggle description labels
//   navigationBar — auto-detected
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - ToggleDenseItem

public struct ToggleDenseItem: Sendable {
    public var label: String
    public var subtitle: String
    public var isOn: Bool
    public var isDisabled: Bool
}

// MARK: - SettingsToggleDenseConfig

public struct SettingsToggleDenseConfig: Sendable {
    public var title: String
    /// Two sections of toggles.
    public var section1Header: String
    public var section1Items: [ToggleDenseItem]
    public var section2Header: String
    public var section2Items: [ToggleDenseItem]
    public var colorScheme: ColorScheme

    public init(
        title: String,
        section1Header: String,
        section1Items: [ToggleDenseItem],
        section2Header: String,
        section2Items: [ToggleDenseItem],
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.section1Header = section1Header
        self.section1Items = section1Items
        self.section2Header = section2Header
        self.section2Items = section2Items
        self.colorScheme = colorScheme
    }

    private static let sec1Headers = ["Notifications", "Alerts", "Privacy", "App Permissions"]
    private static let sec2Headers = ["Advanced", "Developer", "Beta Features", "Experimental"]
    private static let labelPool = [
        ("Allow Notifications",       "Receive alerts from this app"),
        ("Sound",                     "Play audio for notifications"),
        ("Vibration",                 "Use haptic feedback"),
        ("Badge App Icon",            "Show unread count on app icon"),
        ("Show in Lock Screen",       "Display on the lock screen"),
        ("Show in History",           "Include in notification history"),
        ("Location Access",           "Use your location for better results"),
        ("Background Refresh",        "Update content when not in use"),
        ("Cellular Data",             "Allow app to use mobile data"),
        ("Automatic Downloads",       "Download new content automatically"),
        ("Sync with iCloud",          "Keep data updated across devices"),
        ("Face ID",                   "Require Face ID to open"),
        ("Analytics",                 "Share usage data to improve the app"),
        ("Crash Reports",             "Send crash reports automatically"),
        ("Haptic Feedback",           "Use haptic responses for actions"),
    ]

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> SettingsToggleDenseConfig {
        var rng   = SeededRNG(seed: seed)
        let dark  = rng.next() % 2 == 0
        let c1    = 3 + Int(rng.next() % 4)   // 3–6 items in section 1
        let c2    = 3 + Int(rng.next() % 4)   // 3–6 items in section 2
        let s1Hi  = Int(rng.next() % UInt64(sec1Headers.count))
        let s2Hi  = Int(rng.next() % UInt64(sec2Headers.count))

        func makeItems(_ count: Int) -> [ToggleDenseItem] {
            var items: [ToggleDenseItem] = []
            for _ in 0..<count {
                let pIdx    = Int(rng.next() % UInt64(labelPool.count))
                let isOn    = rng.next() % 2 == 0
                let disabled = rng.next() % 6 == 0   // ~17% disabled
                items.append(ToggleDenseItem(
                    label: labelPool[pIdx].0,
                    subtitle: labelPool[pIdx].1,
                    isOn: isOn,
                    isDisabled: disabled
                ))
            }
            return items
        }

        return SettingsToggleDenseConfig(
            title: corpus.navigationTitle(),
            section1Header: sec1Headers[s1Hi],
            section1Items: makeItems(c1),
            section2Header: sec2Headers[s2Hi],
            section2Items: makeItems(c2),
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - SettingsToggleDenseTemplate

public struct SettingsToggleDenseTemplate: View {
    public let config: SettingsToggleDenseConfig

    public init(config: SettingsToggleDenseConfig) {
        self.config = config
    }

    @ViewBuilder
    private func toggleSection(header: String, items: [ToggleDenseItem], offset: Int) -> some View {
        Section {
            ForEach(Array(items.enumerated()), id: \.offset) { idx, item in
                HStack {
                    VStack(alignment: .leading, spacing: 1) {
                        Text(item.label)
                            .font(.body)
                            .foregroundStyle(item.isDisabled ? .secondary : .primary)
                            .captureFrame(id: "label_toggle_\(offset + idx)")
                        if !item.subtitle.isEmpty {
                            Text(item.subtitle)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                    Spacer()
                    Toggle("", isOn: .constant(item.isOn))
                        .labelsHidden()
                        .disabled(item.isDisabled)
                        .opacity(item.isDisabled ? 0.45 : 1.0)
                        .captureFrame(id: "toggle_\(offset + idx)")
                }
                .padding(.vertical, 2)
            }
        } header: {
            Text(header)
                .captureFrame(id: "label_section_\(offset)")
        }
    }

    public var body: some View {
        ZStack {
            Color(UIColor.systemGroupedBackground).ignoresSafeArea()

            NavigationStack {
                List {
                    toggleSection(header: config.section1Header,
                                  items: config.section1Items, offset: 0)
                    toggleSection(header: config.section2Header,
                                  items: config.section2Items,
                                  offset: config.section1Items.count)
                }
                .navigationTitle(config.title)
                .navigationBarTitleDisplayMode(.large)
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}
