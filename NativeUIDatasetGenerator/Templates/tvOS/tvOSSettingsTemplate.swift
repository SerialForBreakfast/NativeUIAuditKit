// tvOSSettingsTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS Settings split-view template for OS UI detection.
// Models the Apple TV Settings application: left categories pane, right settings options pane,
// toggles, value labels, and high-contrast solid white focus pill appearance.
//
// Annotated elements:
//   listRow        — settings rows (focused with solid white pill / unfocused)
//   toggle         — setting toggle switches
//   label          — row titles and detail values
//   navigationBar  — right pane section header

import SwiftUI

// MARK: - tvOSSettingRowConfig

public struct tvOSSettingRowConfig: Sendable {
    public var title: String
    public var detailText: String?
    public var hasToggle: Bool
    public var toggleState: Bool
    public var isFocused: Bool

    public init(
        title: String,
        detailText: String? = nil,
        hasToggle: Bool = false,
        toggleState: Bool = false,
        isFocused: Bool = false
    ) {
        self.title = title
        self.detailText = detailText
        self.hasToggle = hasToggle
        self.toggleState = toggleState
        self.isFocused = isFocused
    }
}

// MARK: - tvOSSettingsConfig

public struct tvOSSettingsConfig: Sendable {
    public var sectionTitle: String
    public var categories: [tvOSSettingRowConfig]
    public var settings: [tvOSSettingRowConfig]
    public var colorScheme: ColorScheme

    public init(
        sectionTitle: String,
        categories: [tvOSSettingRowConfig],
        settings: [tvOSSettingRowConfig],
        colorScheme: ColorScheme = .dark
    ) {
        self.sectionTitle = sectionTitle
        self.categories = categories
        self.settings = settings
        self.colorScheme = colorScheme
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSSettingsConfig {
        var rng = SeededRNG(seed: seed)
        let catTitles = [
            "General", "Users and Accounts", "Video and Audio",
            "Remotes and Devices", "Network", "Accessibility", "System"
        ]

        let rightCount = 5 + Int(rng.next() % 4) // 5–8 settings
        let totalCount = catTitles.count + rightCount
        let focusIndex = Int(rng.next() % UInt64(totalCount))

        var categories: [tvOSSettingRowConfig] = []
        for (i, title) in catTitles.enumerated() {
            categories.append(tvOSSettingRowConfig(
                title: title,
                isFocused: (i == focusIndex)
            ))
        }

        var settings: [tvOSSettingRowConfig] = []
        for i in 0..<rightCount {
            let idx = catTitles.count + i
            let hasToggle = (rng.next() % 2 == 0)
            let toggleOn = (rng.next() % 2 == 0)
            let detail = hasToggle ? nil : corpus.listRowSubtitle()
            settings.append(tvOSSettingRowConfig(
                title: corpus.listRowTitle(),
                detailText: detail,
                hasToggle: hasToggle,
                toggleState: toggleOn,
                isFocused: (idx == focusIndex)
            ))
        }

        return tvOSSettingsConfig(
            sectionTitle: "Settings",
            categories: categories,
            settings: settings,
            colorScheme: .dark
        )
    }
}

// MARK: - tvOSSettingsTemplate View

public struct tvOSSettingsTemplate: View {
    public let config: tvOSSettingsConfig

    public init(config: tvOSSettingsConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack(alignment: .topLeading) {
            Color(red: 0.05, green: 0.05, blue: 0.08).ignoresSafeArea()

            VStack(alignment: .leading, spacing: 0) {
                // Navigation Header
                Text(config.sectionTitle)
                    .font(.system(size: 44, weight: .bold))
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 90)
                    .padding(.top, 60)
                    .padding(.bottom, 30)
                    .captureFrame(id: "navigationBar_settings_title")

                // Split View Layout
                HStack(alignment: .top, spacing: 80) {
                    // Left Column: Categories
                    VStack(spacing: 12) {
                        ForEach(Array(config.categories.enumerated()), id: \.offset) { idx, cat in
                            HStack {
                                Text(cat.title)
                                    .font(.system(size: 26, weight: cat.isFocused ? .bold : .medium))
                                    .foregroundColor(cat.isFocused ? .black : .white)
                                    .captureFrame(id: "label_cat_\(idx)")
                                Spacer()
                                Image(systemName: "chevron.right")
                                    .font(.system(size: 20))
                                    .foregroundColor(cat.isFocused ? .black.opacity(0.6) : .white.opacity(0.4))
                            }
                            .padding(.horizontal, 28)
                            .frame(width: 580, height: 74)
                            .background(cat.isFocused ? Color.white : Color.white.opacity(0.08))
                            .cornerRadius(16)
                            .shadow(color: cat.isFocused ? Color.white.opacity(0.4) : Color.clear, radius: 16)
                            .captureFrame(id: cat.isFocused ? "listRow_cat_\(idx)_focused" : "listRow_cat_\(idx)_unfocused")
                        }
                    }

                    // Right Column: Settings Rows
                    VStack(spacing: 14) {
                        ForEach(Array(config.settings.enumerated()), id: \.offset) { idx, item in
                            HStack {
                                Text(item.title)
                                    .font(.system(size: 26, weight: item.isFocused ? .bold : .medium))
                                    .foregroundColor(item.isFocused ? .black : .white)
                                    .captureFrame(id: "label_item_\(idx)")

                                Spacer()

                                if item.hasToggle {
                                    Toggle("", isOn: .constant(item.toggleState))
                                        .labelsHidden()
                                        .toggleStyle(SwitchToggleStyle(tint: item.isFocused ? .black : .blue))
                                        .captureFrame(id: "toggle_setting_\(idx)")
                                } else if let detail = item.detailText {
                                    Text(detail)
                                        .font(.system(size: 24))
                                        .foregroundColor(item.isFocused ? .black.opacity(0.7) : .white.opacity(0.5))
                                        .captureFrame(id: "label_detail_\(idx)")
                                }
                            }
                            .padding(.horizontal, 28)
                            .frame(width: 980, height: 78)
                            .background(item.isFocused ? Color.white : Color.white.opacity(0.06))
                            .cornerRadius(16)
                            .shadow(color: item.isFocused ? Color.white.opacity(0.5) : Color.clear, radius: 20)
                            .captureFrame(id: item.isFocused ? "listRow_setting_\(idx)_focused" : "listRow_setting_\(idx)_unfocused")
                        }
                    }
                }
                .padding(.horizontal, 90)
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}
