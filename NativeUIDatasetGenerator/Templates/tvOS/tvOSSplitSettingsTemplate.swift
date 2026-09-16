// tvOSSplitSettingsTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised deep settings hierarchy template for tvOS OS UI detection (TASK-6b-E3).
// Models multi-level master-detail navigation with breadcrumbs, toggles, segmented pickers,
// stepper controls, and sub-drill list rows.
//
// Annotated elements:
//   navigationBar    — top bar with back navigation and screen title
//   secondaryButton  — back button / parent breadcrumb
//   listRow          — category rows and sub-drill navigation items
//   toggle           — setting toggles (e.g. Match Content, Automatic Updates)
//   segmentedControl — multi-option segment selectors (e.g. 4K SDR / HDR / Dolby Vision)
//   stepperControl   — value adjustment steppers (e.g. Sleep Timer, Audio Delay)
//   slider           — brightness/volume adjustment slider
//   label            — titles, subtitles, section headers, footer descriptions
//   imageView        — category icons, checkmarks, disclosure chevrons

import SwiftUI

// MARK: - tvOSSplitSettingsConfig

public struct tvOSSplitSettingsConfig: Sendable {
    public var sectionTitle: String
    public var parentTitle: String
    public var categories: [(title: String, icon: String)]
    public var selectedCategoryIndex: Int
    public var detailOptions: [(title: String, type: DetailOptionType, valueText: String)]
    public var focusPane: FocusPane // .sidebar or .detail
    public var focusedIndex: Int

    public enum FocusPane: Sendable {
        case sidebar
        case detail
    }

    public enum DetailOptionType: Sendable {
        case toggle(isOn: Bool)
        case drillDown
        case segmented(options: [String], selected: Int)
        case stepper(value: Int)
    }

    public init(
        sectionTitle: String,
        parentTitle: String = "Settings",
        categories: [(title: String, icon: String)],
        selectedCategoryIndex: Int = 1,
        detailOptions: [(title: String, type: DetailOptionType, valueText: String)],
        focusPane: FocusPane = .detail,
        focusedIndex: Int = 0
    ) {
        self.sectionTitle = sectionTitle
        self.parentTitle = parentTitle
        self.categories = categories
        self.selectedCategoryIndex = selectedCategoryIndex
        self.detailOptions = detailOptions
        self.focusPane = focusPane
        self.focusedIndex = focusedIndex
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSSplitSettingsConfig {
        var rng = SeededRNG(seed: seed)
        let cats: [(title: String, icon: String)] = [
            ("General", "gear"),
            ("Video and Audio", "tv.and.mediabox"),
            ("AirPlay and HomeKit", "airplayvideo"),
            ("Remotes and Devices", "appletvremote.gen4"),
            ("Network", "network"),
            ("Users and Accounts", "person.2.fill"),
            ("System", "apple.logo")
        ]

        let details: [(title: String, DetailOptionType, String)] = [
            ("Resolution", .drillDown, "4K SDR (60Hz)"),
            ("Match Content", .drillDown, "Range & Frame Rate"),
            ("Format", .segmented(options: ["SDR", "HDR", "Dolby Vision"], selected: 0), ""),
            ("Audio Output", .drillDown, "TV Speakers"),
            ("Reduce Loud Sounds", .toggle(isOn: (rng.next() % 2 == 0)), ""),
            ("Audio Sync Delay", .stepper(value: 20), "20 ms")
        ]

        let selectedCat = Int(rng.next() % UInt64(cats.count))
        let focusInDetail = (rng.next() % 2 == 0)
        let focIdx = focusInDetail ? Int(rng.next() % UInt64(details.count)) : selectedCat

        return tvOSSplitSettingsConfig(
            sectionTitle: cats[selectedCat].title,
            parentTitle: "Settings",
            categories: cats,
            selectedCategoryIndex: selectedCat,
            detailOptions: details,
            focusPane: focusInDetail ? .detail : .sidebar,
            focusedIndex: focIdx
        )
    }
}

// MARK: - tvOSSplitSettingsTemplate View

public struct tvOSSplitSettingsTemplate: View {
    public let config: tvOSSplitSettingsConfig

    public init(config: tvOSSplitSettingsConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack(alignment: .topLeading) {
            Color(red: 0.05, green: 0.05, blue: 0.08).ignoresSafeArea()

            VStack(alignment: .leading, spacing: 16) {
                // Top Navigation Bar
                HStack(spacing: 20) {
                    HStack(spacing: 8) {
                        Image(systemName: "chevron.left")
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(.white.opacity(0.8))
                        Text(config.parentTitle)
                            .font(.system(size: 28, weight: .semibold))
                            .foregroundColor(.white.opacity(0.8))
                    }
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
                    .captureFrame(id: "secondaryButton_back_navigation")

                    Image(systemName: "chevron.right")
                        .foregroundColor(.white.opacity(0.4))
                        .font(.system(size: 20))

                    Text(config.sectionTitle)
                        .font(.system(size: 34, weight: .bold))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_screen_title")

                    Spacer()
                }
                .padding(.horizontal, 90)
                .padding(.top, 40)
                .frame(height: 100)
                .captureFrame(id: "navigationBar_settings_header")

                // Split Content Pane
                HStack(alignment: .top, spacing: 60) {
                    // Left Master Categories
                    VStack(spacing: 12) {
                        ForEach(Array(config.categories.enumerated()), id: \.offset) { idx, cat in
                            let isFoc = (config.focusPane == .sidebar && idx == config.focusedIndex)
                            let isSel = (idx == config.selectedCategoryIndex)

                            HStack(spacing: 20) {
                                Image(systemName: cat.icon)
                                    .font(.system(size: 24))
                                    .foregroundColor(isFoc ? .black : (isSel ? .white : .white.opacity(0.7)))
                                    .frame(width: 32)
                                    .captureFrame(id: "imageView_cat_icon_\(idx)")

                                Text(cat.title)
                                    .font(.system(size: 24, weight: (isFoc || isSel) ? .bold : .medium))
                                    .foregroundColor(isFoc ? .black : .white)
                                    .captureFrame(id: "label_cat_title_\(idx)")

                                Spacer()

                                Image(systemName: "chevron.right")
                                    .font(.system(size: 18))
                                    .foregroundColor(isFoc ? .black.opacity(0.6) : .white.opacity(0.3))
                            }
                            .padding(.horizontal, 24)
                            .frame(width: 520, height: 72)
                            .background(isFoc ? Color.white : (isSel ? Color.white.opacity(0.18) : Color.white.opacity(0.06)))
                            .cornerRadius(16)
                            .scaleEffect(isFoc ? 1.03 : 1.0)
                            .shadow(color: isFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                            .captureFrame(id: isFoc ? "listRow_category_\(idx)_focused" : "listRow_category_\(idx)_unfocused")
                        }
                    }

                    // Right Detail Items Pane
                    VStack(spacing: 14) {
                        ForEach(Array(config.detailOptions.enumerated()), id: \.offset) { idx, opt in
                            let isFoc = (config.focusPane == .detail && idx == config.focusedIndex)

                            HStack(spacing: 20) {
                                Text(opt.title)
                                    .font(.system(size: 24, weight: isFoc ? .bold : .medium))
                                    .foregroundColor(isFoc ? .black : .white)
                                    .captureFrame(id: "label_opt_title_\(idx)")

                                Spacer()

                                switch opt.type {
                                case .toggle(let isOn):
                                    Toggle("", isOn: .constant(isOn))
                                        .labelsHidden()
                                        .captureFrame(id: isFoc ? "toggle_opt_\(idx)_focused" : "toggle_opt_\(idx)_unfocused")

                                case .drillDown:
                                    HStack(spacing: 12) {
                                        Text(opt.valueText)
                                            .font(.system(size: 22))
                                            .foregroundColor(isFoc ? .black.opacity(0.7) : .white.opacity(0.6))
                                            .captureFrame(id: "label_opt_val_\(idx)")
                                        Image(systemName: "chevron.right")
                                            .font(.system(size: 18))
                                            .foregroundColor(isFoc ? .black.opacity(0.5) : .white.opacity(0.4))
                                    }

                                case .segmented(let segs, let sel):
                                    HStack(spacing: 8) {
                                        ForEach(Array(segs.enumerated()), id: \.offset) { sIdx, seg in
                                            let isSegSel = (sIdx == sel)
                                            Text(seg)
                                                .font(.system(size: 18, weight: isSegSel ? .bold : .medium))
                                                .foregroundColor(isSegSel ? (isFoc ? .white : .black) : (isFoc ? .black.opacity(0.7) : .white.opacity(0.7)))
                                                .padding(.horizontal, 14)
                                                .padding(.vertical, 8)
                                                .background(isSegSel ? (isFoc ? Color.black : Color.white) : Color.clear)
                                                .cornerRadius(10)
                                        }
                                    }
                                    .padding(4)
                                    .background(isFoc ? Color.black.opacity(0.15) : Color.white.opacity(0.1))
                                    .cornerRadius(12)
                                    .captureFrame(id: isFoc ? "segmentedControl_opt_\(idx)_focused" : "segmentedControl_opt_\(idx)_unfocused")

                                case .stepper(let val):
                                    HStack(spacing: 16) {
                                        Image(systemName: "minus.circle.fill")
                                            .font(.system(size: 24))
                                            .foregroundColor(isFoc ? .black : .white.opacity(0.7))
                                        Text("\(val) ms")
                                            .font(.system(size: 22, weight: .bold))
                                            .foregroundColor(isFoc ? .black : .white)
                                        Image(systemName: "plus.circle.fill")
                                            .font(.system(size: 24))
                                            .foregroundColor(isFoc ? .black : .white.opacity(0.7))
                                    }
                                    .captureFrame(id: isFoc ? "stepperControl_opt_\(idx)_focused" : "stepperControl_opt_\(idx)_unfocused")
                                }
                            }
                            .padding(.horizontal, 28)
                            .frame(width: 1040, height: 76)
                            .background(isFoc ? Color.white : Color.white.opacity(0.08))
                            .cornerRadius(16)
                            .scaleEffect(isFoc ? 1.02 : 1.0)
                            .shadow(color: isFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                            .captureFrame(id: isFoc ? "listRow_detail_\(idx)_focused" : "listRow_detail_\(idx)_unfocused")
                        }

                        // Explanatory footer text
                        Text("Configuring these settings affects HDMI video and Dolby Atmos output to connected receivers or home theater systems.")
                            .font(.system(size: 18))
                            .foregroundColor(.white.opacity(0.5))
                            .frame(width: 1020, alignment: .leading)
                            .padding(.top, 12)
                            .captureFrame(id: "label_settings_footer")
                    }
                }
                .padding(.horizontal, 90)
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}
