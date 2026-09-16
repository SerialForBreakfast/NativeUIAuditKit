#!/usr/bin/env swift
// generate_tvos_dataset.swift
// NativeUIAuditKit — High-throughput tvOS OS UI Synthetic Dataset Generator
//
// Renders 1080p (1920×1080) tvOS OS UI screenshots directly via SwiftUI ImageRenderer
// on macOS without requiring simulator execution or host app harnesses.
// Generates schema v1.0 annotations with exact pixel bounding boxes and focus states.
//
// Covers all 15 tvOS template families:
//   1.  tvOSHomeScreen         — Top Shelf banner, dock, app icon grid, focus scale/shadow
//   2.  tvOSSettings           — Settings 2-column view with categories and options
//   3.  tvOSSplitSettings      — Deep hierarchy settings: breadcrumb navBar, segmented controls, steppers
//   4.  tvOSAlert              — Confirmation dialogs and permission alerts
//   5.  tvOSTopTabBar          — Apple TV top navigation bar and featured cards
//   6.  tvOSContextMenu        — Long-press contextual action cards (play next, mark watched, delete)
//   7.  tvOSSidebarMenu        — Split navigation sidebar with search field and content grid
//   8.  tvOSTopShelfHero       — Full-bleed hero banner carousel with Watch Now / Trailer buttons and tags
//   9.  tvOSControlCenter      — Right-hand slide-out drawer with user switcher, volume slider, DND, HomeKit
//   10. tvOSAVKitPlayback      — Video transport chrome: timeline scrubber slider, play/pause, skip intro
//   11. tvOSAudioSubtitles     — In-playback audio and subtitles panel with language list and toggles
//   12. tvOSSharePlay          — FaceTime / SharePlay group playback overlay with participant avatars
//   13. tvOSKeyboard           — On-screen character grid keyboard, search field, space, delete, dictation
//   14. tvOSSiriOverlay        — Siri voice card, transcribed speech text, Siri orb glow, result cards
//   15. tvOSHardNegatives      — Synthetic abstract gradients with zero UI elements
//
// Usage:
//   swift scripts/generate_tvos_dataset.swift [--count 2000] [--output dataset/tvos_dataset] [--sample]

import Foundation
import CoreGraphics
import ImageIO
import CryptoKit
import SwiftUI
import UniformTypeIdentifiers

// MARK: - FramePreference & Modifier

public struct FramePreference: PreferenceKey {
    public static var defaultValue: [String: CGRect] { [:] }
    public static func reduce(value: inout [String: CGRect], nextValue: () -> [String: CGRect]) {
        value.merge(nextValue()) { _, new in new }
    }
}

public extension View {
    func captureFrame(id: String) -> some View {
        background(
            GeometryReader { geo in
                Color.clear.preference(
                    key: FramePreference.self,
                    value: [id: geo.frame(in: .global)]
                )
            }
        )
    }
}

// MARK: - Seeded RNG

public struct SeededRNG {
    private var state: UInt64
    public init(seed: UInt64) { self.state = seed != 0 ? seed : 0xDEADBEEFCAFEBABE }
    public mutating func next() -> UInt64 {
        state &+= 0x9E3779B97F4A7C15
        var z = state
        z = (z ^ (z >> 30)) &* 0xBF58476D1CE4E5B9
        z = (z ^ (z >> 27)) &* 0x94D049BB133111EB
        return z ^ (z >> 31)
    }
}

// MARK: - Content Corpus

public struct ContentCorpus {
    private var rng: SeededRNG
    public init(seed: UInt64) { self.rng = SeededRNG(seed: seed) }

    private let appTitles = [
        "Photos", "Music", "TV", "Podcasts", "Arcade", "App Store",
        "Settings", "Fitness", "News", "Books", "Calculator", "Weather",
        "Home", "Files", "Notes", "Reminders", "Maps", "Clock",
        "TVTestRig", "FixtureApp", "SpeedTest", "YouTube", "Netflix", "Prime Video"
    ]

    private let navTitles = [
        "Home", "Settings", "Library", "Search", "General", "Accounts",
        "Network", "Video and Audio", "Accessibility", "System", "Remotes"
    ]

    private let settingRows = [
        "Wi-Fi", "Bluetooth", "AirPlay and HomeKit", "Audio Output",
        "Subtitles and Captioning", "Siri", "Software Updates", "Sleep After",
        "Screensaver", "Language", "Legal & Regulatory", "Reset"
    ]

    private let alertTitles = [
        "Software Update Available", "Sign In to Apple TV", "Allow TVTestRig Access?",
        "Erase All Content and Settings?", "Remote Battery Low", "AirPlay Passcode Required"
    ]

    private let alertMessages = [
        "A new tvOS version is ready to install. Do you want to download and update now?",
        "Enter your Apple Account password to continue.",
        "TVTestRig is attempting to inspect screen elements for test automation.",
        "This will restore your Apple TV to factory settings. This action cannot be undone.",
        "Connect your Siri Remote to a charger soon.",
        "Enter the code displayed on your TV to continue connecting."
    ]

    public mutating func appTitle() -> String {
        appTitles[Int(rng.next() % UInt64(appTitles.count))]
    }
    public mutating func navTitle() -> String {
        navTitles[Int(rng.next() % UInt64(navTitles.count))]
    }
    public mutating func settingRow() -> String {
        settingRows[Int(rng.next() % UInt64(settingRows.count))]
    }
    public mutating func alertTitle() -> String {
        alertTitles[Int(rng.next() % UInt64(alertTitles.count))]
    }
    public mutating func alertMessage() -> String {
        alertMessages[Int(rng.next() % UInt64(alertMessages.count))]
    }
}

// MARK: - Template 1: Home Screen

struct HomeScreenView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let focusIdx = Int(rng.next() % 10)
        let apps = (0..<10).map { i -> (title: String, hue: Double, isFocused: Bool) in
            let hue = Double(rng.next() % 1000) / 1000.0
            return (appsList[i % appsList.count], hue, i == focusIdx)
        }
        let columns = [
            GridItem(.fixed(308), spacing: 48),
            GridItem(.fixed(308), spacing: 48),
            GridItem(.fixed(308), spacing: 48),
            GridItem(.fixed(308), spacing: 48),
            GridItem(.fixed(308), spacing: 48)
        ]

        ZStack(alignment: .topLeading) {
            LinearGradient(
                colors: [Color(red: 0.08, green: 0.08, blue: 0.12), Color.black],
                startPoint: .top, endPoint: .bottom
            ).ignoresSafeArea()

            VStack(alignment: .leading, spacing: 32) {
                // Top shelf
                ZStack {
                    RoundedRectangle(cornerRadius: 24)
                        .fill(Color.blue.opacity(0.35))
                    HStack(spacing: 24) {
                        Image(systemName: "tv.fill").font(.system(size: 64)).foregroundColor(.white)
                            .captureFrame(id: "imageView_shelf_icon")
                        Text("Featured on Apple TV")
                            .font(.system(size: 38, weight: .bold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_shelf_title")
                    }
                }
                .frame(width: 1720, height: 340)
                .captureFrame(id: "collectionItem_shelf_0_unfocused")
                .padding(.top, 40)
                .padding(.leading, 100)

                // Grid
                LazyVGrid(columns: columns, spacing: 36) {
                    ForEach(0..<10, id: \.self) { idx in
                        let app = apps[idx]
                        VStack(spacing: 12) {
                            ZStack {
                                RoundedRectangle(cornerRadius: 16)
                                    .fill(Color(hue: app.hue, saturation: 0.7, brightness: 0.6))
                                Image(systemName: "app.fill")
                                    .font(.system(size: 44)).foregroundColor(.white)
                            }
                            .frame(width: 308, height: 175)
                            .scaleEffect(app.isFocused ? 1.15 : 1.0)
                            .overlay(RoundedRectangle(cornerRadius: 16).stroke(app.isFocused ? Color.white : Color.clear, lineWidth: 3))
                            .shadow(color: app.isFocused ? Color.white.opacity(0.6) : Color.clear, radius: 20)
                            .captureFrame(id: app.isFocused ? "collectionItem_app_\(idx)_focused" : "collectionItem_app_\(idx)_unfocused")

                            Text(app.title)
                                .font(.system(size: 20, weight: app.isFocused ? .bold : .medium))
                                .foregroundColor(app.isFocused ? .white : .white.opacity(0.7))
                                .frame(width: 308)
                                .captureFrame(id: "label_app_\(idx)")
                        }
                    }
                }
                .padding(.leading, 100)
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }

    private let appsList = [
        "Photos", "Music", "TV", "Podcasts", "Arcade",
        "Settings", "Fitness", "YouTube", "FixtureApp", "TVTestRig"
    ]
}

// MARK: - Template 2: Settings Split-View

struct SettingsView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let focusIdx = Int(rng.next() % 6)
        let categories = ["General", "Users", "Video and Audio", "Remotes", "Network", "System"]

        ZStack(alignment: .topLeading) {
            Color(red: 0.05, green: 0.05, blue: 0.08).ignoresSafeArea()

            VStack(alignment: .leading, spacing: 20) {
                Text("Settings")
                    .font(.system(size: 44, weight: .bold))
                    .foregroundColor(.white)
                    .padding(.horizontal, 90)
                    .padding(.top, 50)
                    .captureFrame(id: "navigationBar_title")

                HStack(alignment: .top, spacing: 80) {
                    VStack(spacing: 12) {
                        ForEach(0..<categories.count, id: \.self) { idx in
                            let isFoc = (idx == focusIdx)
                            HStack {
                                Text(categories[idx])
                                    .font(.system(size: 26, weight: isFoc ? .bold : .medium))
                                    .foregroundColor(isFoc ? .black : .white)
                                    .captureFrame(id: "label_cat_\(idx)")
                                Spacer()
                                Image(systemName: "chevron.right")
                                    .foregroundColor(isFoc ? .black.opacity(0.6) : .white.opacity(0.4))
                            }
                            .padding(.horizontal, 28)
                            .frame(width: 580, height: 74)
                            .background(isFoc ? Color.white : Color.white.opacity(0.08))
                            .cornerRadius(16)
                            .captureFrame(id: isFoc ? "listRow_cat_\(idx)_focused" : "listRow_cat_\(idx)_unfocused")
                        }
                    }

                    VStack(spacing: 14) {
                        ForEach(0..<5, id: \.self) { idx in
                            HStack {
                                Text("Option \(idx + 1)")
                                    .font(.system(size: 26))
                                    .foregroundColor(.white)
                                    .captureFrame(id: "label_opt_\(idx)")
                                Spacer()
                                Toggle("", isOn: .constant(idx % 2 == 0))
                                    .labelsHidden()
                                    .captureFrame(id: "toggle_setting_\(idx)")
                            }
                            .padding(.horizontal, 28)
                            .frame(width: 980, height: 78)
                            .background(Color.white.opacity(0.06))
                            .cornerRadius(16)
                            .captureFrame(id: "listRow_setting_\(idx)_unfocused")
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

// MARK: - Template 3: Alert Modal

struct AlertView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let focusBtn = Int(rng.next() % 2) // 0: primary, 1: cancel

        ZStack {
            Color.black.opacity(0.85).ignoresSafeArea()

            VStack(spacing: 28) {
                VStack(spacing: 12) {
                    Text("Allow TVTestRig Access?")
                        .font(.system(size: 34, weight: .bold))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_alert_title")
                    Text("This allows TVTestRig to automate Apple TV navigation.")
                        .font(.system(size: 22))
                        .foregroundColor(.white.opacity(0.8))
                        .padding(.horizontal, 32)
                        .multilineTextAlignment(.center)
                        .captureFrame(id: "label_alert_message")
                }
                .padding(.top, 40)

                VStack(spacing: 16) {
                    Text("Continue")
                        .font(.system(size: 24, weight: focusBtn == 0 ? .bold : .medium))
                        .foregroundColor(focusBtn == 0 ? .black : .white)
                        .frame(width: 660, height: 68)
                        .background(focusBtn == 0 ? Color.white : Color.white.opacity(0.12))
                        .cornerRadius(16)
                        .captureFrame(id: focusBtn == 0 ? "primaryButton_action_focused" : "primaryButton_action_unfocused")

                    Text("Cancel")
                        .font(.system(size: 24, weight: focusBtn == 1 ? .bold : .medium))
                        .foregroundColor(focusBtn == 1 ? .black : .white)
                        .frame(width: 660, height: 68)
                        .background(focusBtn == 1 ? Color.white : Color.white.opacity(0.12))
                        .cornerRadius(16)
                        .captureFrame(id: focusBtn == 1 ? "cancelAction_dismiss_focused" : "cancelAction_dismiss_unfocused")
                }
                .padding(.bottom, 36)
            }
            .frame(width: 760)
            .background(Color(red: 0.16, green: 0.16, blue: 0.20))
            .cornerRadius(28)
            .captureFrame(id: "alert_dialog_box")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 4: Top Tab Bar

struct TabBarView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let tabs = ["Apple TV+", "Store", "Library", "Search"]
        let focIdx = Int(rng.next() % UInt64(tabs.count))

        ZStack(alignment: .top) {
            Color(red: 0.04, green: 0.04, blue: 0.06).ignoresSafeArea()

            VStack(spacing: 0) {
                HStack(spacing: 24) {
                    ForEach(0..<tabs.count, id: \.self) { idx in
                        let isFoc = (idx == focIdx)
                        Text(tabs[idx])
                            .font(.system(size: 24, weight: isFoc ? .bold : .medium))
                            .foregroundColor(isFoc ? .black : .white.opacity(0.8))
                            .padding(.horizontal, 28)
                            .padding(.vertical, 12)
                            .background(isFoc ? Color.white : Color.clear)
                            .cornerRadius(20)
                            .captureFrame(id: isFoc ? "primaryButton_tab_\(idx)_focused" : "primaryButton_tab_\(idx)_unfocused")
                    }
                }
                .frame(maxWidth: .infinity)
                .frame(height: 110)
                .background(Color.black.opacity(0.3))
                .captureFrame(id: "tabBar_top_navigation")
                .padding(.top, 20)

                VStack(alignment: .leading, spacing: 20) {
                    Text("Featured Collection")
                        .font(.system(size: 48, weight: .heavy))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_featured_title")

                    RoundedRectangle(cornerRadius: 24)
                        .fill(Color.purple.opacity(0.4))
                        .frame(width: 1740, height: 680)
                        .captureFrame(id: "collectionItem_featured_card_unfocused")
                }
                .padding(.horizontal, 90)
                .padding(.top, 40)
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 5: Context Menu

struct ContextMenuView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let actions: [(title: String, icon: String, isDestructive: Bool, isPrimary: Bool)] = [
            ("Play Next", "play.fill", false, true),
            ("Mark as Watched", "checkmark.circle", false, false),
            ("Remove from Up Next", "minus.circle", false, false),
            ("Share...", "square.and.arrow.up", false, false),
            ("Delete", "trash.fill", true, false)
        ]
        let foc = Int(rng.next() % UInt64(actions.count))
        let hue = Double(rng.next() % 1000) / 1000.0

        ZStack {
            Color.black.opacity(0.88).ignoresSafeArea()

            HStack(spacing: 64) {
                // Target Poster Card
                VStack(alignment: .leading, spacing: 16) {
                    ZStack {
                        RoundedRectangle(cornerRadius: 20)
                            .fill(LinearGradient(
                                colors: [Color(hue: hue, saturation: 0.65, brightness: 0.5), Color.black.opacity(0.7)],
                                startPoint: .topLeading, endPoint: .bottomTrailing
                            ))
                        Image(systemName: "film.fill")
                            .font(.system(size: 72))
                            .foregroundColor(.white.opacity(0.9))
                            .captureFrame(id: "imageView_target_poster")
                    }
                    .frame(width: 440, height: 660)
                    .overlay(RoundedRectangle(cornerRadius: 20).stroke(Color.white.opacity(0.2), lineWidth: 1))
                    .captureFrame(id: "collectionItem_target_poster_unfocused")

                    VStack(alignment: .leading, spacing: 6) {
                        Text("Severance")
                            .font(.system(size: 32, weight: .bold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_target_title")
                        Text("Season 1 • Thriller")
                            .font(.system(size: 22))
                            .foregroundColor(.white.opacity(0.7))
                            .captureFrame(id: "label_target_subtitle")
                    }
                    .frame(width: 440, alignment: .leading)
                }

                // Context Menu Card
                VStack(spacing: 8) {
                    ForEach(Array(actions.enumerated()), id: \.offset) { idx, act in
                        let isFoc = (idx == foc)
                        HStack(spacing: 20) {
                            Text(act.title)
                                .font(.system(size: 24, weight: isFoc ? .bold : .medium))
                                .foregroundColor(isFoc ? (act.isDestructive ? Color.red : Color.black) : (act.isDestructive ? Color.red : Color.white))
                                .captureFrame(id: "label_menu_item_\(idx)")
                            Spacer()
                            Image(systemName: act.icon)
                                .font(.system(size: 22))
                                .foregroundColor(isFoc ? (act.isDestructive ? Color.red : Color.black) : (act.isDestructive ? Color.red : Color.white.opacity(0.7)))
                                .captureFrame(id: "imageView_menu_icon_\(idx)")
                        }
                        .padding(.horizontal, 28)
                        .frame(width: 520, height: 68)
                        .background(isFoc ? Color.white : Color.white.opacity(0.08))
                        .cornerRadius(16)
                        .scaleEffect(isFoc ? 1.04 : 1.0)
                        .shadow(color: isFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                        .captureFrame(id: act.isDestructive
                            ? (isFoc ? "destructiveButton_action_\(idx)_focused" : "destructiveButton_action_\(idx)_unfocused")
                            : (act.isPrimary
                                ? (isFoc ? "primaryButton_action_\(idx)_focused" : "primaryButton_action_\(idx)_unfocused")
                                : (isFoc ? "secondaryButton_action_\(idx)_focused" : "secondaryButton_action_\(idx)_unfocused")))
                    }
                }
                .padding(24)
                .background(Color(red: 0.14, green: 0.14, blue: 0.18))
                .cornerRadius(24)
                .shadow(color: Color.black.opacity(0.6), radius: 32)
                .captureFrame(id: "contextMenu_actions_popup")
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 6: Sidebar Navigation Menu

struct SidebarMenuView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let items: [(title: String, icon: String)] = [
            ("Search", "magnifyingglass"),
            ("Home", "house.fill"),
            ("Movies", "film.fill"),
            ("TV Shows", "tv.fill"),
            ("Sports", "sportscourt.fill"),
            ("Library", "square.stack.3d.up.fill")
        ]
        let selectedNav = Int(rng.next() % UInt64(items.count))
        let focusNav = (rng.next() % 2 == 0) ? selectedNav : nil

        ZStack(alignment: .topLeading) {
            Color(red: 0.05, green: 0.05, blue: 0.08).ignoresSafeArea()

            HStack(spacing: 0) {
                // Left Navigation Sidebar
                VStack(alignment: .leading, spacing: 14) {
                    HStack(spacing: 16) {
                        Image(systemName: "magnifyingglass").foregroundColor(.white.opacity(0.8))
                        Text("Search").font(.system(size: 24)).foregroundColor(.white.opacity(0.6))
                        Spacer()
                    }
                    .padding(.horizontal, 20)
                    .frame(width: 380, height: 60)
                    .background(Color.white.opacity(0.08))
                    .cornerRadius(16)
                    .captureFrame(id: "searchField_nav_search")
                    .padding(.bottom, 12)

                    ForEach(Array(items.enumerated()), id: \.offset) { idx, item in
                        let isFoc = (focusNav == idx)
                        let isSel = (idx == selectedNav)

                        HStack(spacing: 18) {
                            Image(systemName: item.icon)
                                .font(.system(size: 22))
                                .foregroundColor(isFoc ? .black : (isSel ? .white : .white.opacity(0.7)))
                                .frame(width: 28)
                                .captureFrame(id: "imageView_nav_icon_\(idx)")
                            Text(item.title)
                                .font(.system(size: 24, weight: (isFoc || isSel) ? .bold : .medium))
                                .foregroundColor(isFoc ? .black : .white)
                                .captureFrame(id: "label_nav_title_\(idx)")
                            Spacer()
                        }
                        .padding(.horizontal, 20)
                        .frame(width: 380, height: 64)
                        .background(isFoc ? Color.white : (isSel ? Color.white.opacity(0.18) : Color.clear))
                        .cornerRadius(16)
                        .scaleEffect(isFoc ? 1.04 : 1.0)
                        .shadow(color: isFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                        .captureFrame(id: isFoc ? "listRow_nav_\(idx)_focused" : "listRow_nav_\(idx)_unfocused")
                    }

                    Spacer()
                }
                .padding(32)
                .frame(width: 440, height: 1080)
                .background(Color.black.opacity(0.4))
                .captureFrame(id: "sidebar_main_nav")

                // Right Content Pane
                VStack(alignment: .leading, spacing: 24) {
                    Text(items[selectedNav].title)
                        .font(.system(size: 44, weight: .bold))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_section_header")

                    HStack(spacing: 36) {
                        ForEach(0..<3, id: \.self) { cIdx in
                            let isCardFoc = (focusNav == nil && cIdx == 0)
                            VStack(alignment: .leading, spacing: 12) {
                                RoundedRectangle(cornerRadius: 18)
                                    .fill(Color.blue.opacity(0.4))
                                    .frame(width: 420, height: 580)
                                    .scaleEffect(isCardFoc ? 1.08 : 1.0)
                                    .overlay(RoundedRectangle(cornerRadius: 18).stroke(isCardFoc ? Color.white : Color.clear, lineWidth: 3))
                                    .shadow(color: isCardFoc ? Color.white.opacity(0.4) : Color.clear, radius: 16)
                                    .captureFrame(id: isCardFoc ? "collectionItem_card_\(cIdx)_focused" : "collectionItem_card_\(cIdx)_unfocused")

                                Text("Show Title \(cIdx + 1)")
                                    .font(.system(size: 22, weight: isCardFoc ? .bold : .medium))
                                    .foregroundColor(.white)
                                    .captureFrame(id: "label_card_\(cIdx)")
                            }
                        }
                    }
                }
                .padding(60)
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 7: Top Shelf Hero Carousel

struct TopShelfHeroView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let titles = ["Foundation", "Severance", "Ted Lasso", "The Morning Show", "Slow Horses"]
        let title = titles[Int(rng.next() % UInt64(titles.count))]
        let focTarget = Int(rng.next() % 5) // 0: Play, 1: Trailer, 2..4: shelf
        let hue = Double(rng.next() % 1000) / 1000.0

        ZStack(alignment: .topLeading) {
            LinearGradient(
                colors: [Color(hue: hue, saturation: 0.7, brightness: 0.35), Color(red: 0.06, green: 0.06, blue: 0.09)],
                startPoint: .topTrailing, endPoint: .bottomLeading
            ).ignoresSafeArea()

            VStack(alignment: .leading, spacing: 24) {
                // Hero Header
                VStack(alignment: .leading, spacing: 16) {
                    Text(title)
                        .font(.system(size: 56, weight: .heavy))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_hero_title")

                    HStack(spacing: 16) {
                        Text("Season 2 • Sci-Fi")
                            .font(.system(size: 24, weight: .semibold))
                            .foregroundColor(.white.opacity(0.9))
                            .captureFrame(id: "label_hero_subtitle")

                        Text("4K HDR")
                            .font(.system(size: 16, weight: .bold))
                            .foregroundColor(.white)
                            .padding(.horizontal, 10).padding(.vertical, 4)
                            .background(Color.white.opacity(0.2)).cornerRadius(6)
                            .captureFrame(id: "label_tag_hdr")

                        Text("TV-MA")
                            .font(.system(size: 16, weight: .bold))
                            .foregroundColor(.white)
                            .padding(.horizontal, 10).padding(.vertical, 4)
                            .background(Color.white.opacity(0.2)).cornerRadius(6)
                            .captureFrame(id: "label_tag_tvma")
                    }

                    Text("A complex saga following humans scattered on planets throughout the galaxy under the rule of the Galactic Empire.")
                        .font(.system(size: 22))
                        .foregroundColor(.white.opacity(0.8))
                        .frame(maxWidth: 960, alignment: .leading)
                        .captureFrame(id: "label_hero_synopsis")

                    HStack(spacing: 24) {
                        let isPlayFoc = (focTarget == 0)
                        HStack(spacing: 12) {
                            Image(systemName: "play.fill")
                            Text("Watch Now").font(.system(size: 24, weight: .bold))
                        }
                        .foregroundColor(isPlayFoc ? .black : .white)
                        .padding(.horizontal, 36).frame(height: 68)
                        .background(isPlayFoc ? Color.white : Color.white.opacity(0.2))
                        .cornerRadius(18)
                        .scaleEffect(isPlayFoc ? 1.08 : 1.0)
                        .shadow(color: isPlayFoc ? Color.white.opacity(0.5) : Color.clear, radius: 16)
                        .captureFrame(id: isPlayFoc ? "primaryButton_play_focused" : "primaryButton_play_unfocused")

                        let isTrailerFoc = (focTarget == 1)
                        HStack(spacing: 12) {
                            Image(systemName: "film")
                            Text("Trailer").font(.system(size: 22, weight: .semibold))
                        }
                        .foregroundColor(isTrailerFoc ? .black : .white)
                        .padding(.horizontal, 28).frame(height: 68)
                        .background(isTrailerFoc ? Color.white : Color.white.opacity(0.15))
                        .cornerRadius(18)
                        .scaleEffect(isTrailerFoc ? 1.08 : 1.0)
                        .shadow(color: isTrailerFoc ? Color.white.opacity(0.5) : Color.clear, radius: 16)
                        .captureFrame(id: isTrailerFoc ? "secondaryButton_trailer_focused" : "secondaryButton_trailer_unfocused")
                    }
                    .padding(.top, 8)
                }
                .padding(.horizontal, 90).padding(.top, 70)

                Spacer()

                // Shelf Carousel
                VStack(alignment: .leading, spacing: 16) {
                    Text("Related Shows")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_shelf_heading")

                    HStack(spacing: 36) {
                        ForEach(0..<4, id: \.self) { idx in
                            let isFoc = (focTarget == 2 + idx)
                            VStack(alignment: .leading, spacing: 10) {
                                RoundedRectangle(cornerRadius: 16)
                                    .fill(Color.purple.opacity(0.4))
                                    .frame(width: 400, height: 230)
                                    .scaleEffect(isFoc ? 1.12 : 1.0)
                                    .overlay(RoundedRectangle(cornerRadius: 16).stroke(isFoc ? Color.white : Color.clear, lineWidth: 3))
                                    .shadow(color: isFoc ? Color.white.opacity(0.5) : Color.clear, radius: 16)
                                    .captureFrame(id: isFoc ? "collectionItem_shelf_\(idx)_focused" : "collectionItem_shelf_\(idx)_unfocused")

                                Text("Show Episode \(idx + 1)")
                                    .font(.system(size: 20, weight: isFoc ? .bold : .medium))
                                    .foregroundColor(isFoc ? .white : .white.opacity(0.7))
                                    .captureFrame(id: "label_shelf_card_\(idx)")
                            }
                        }
                    }
                }
                .padding(.horizontal, 90).padding(.bottom, 60)
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 8: Control Center Drawer

struct ControlCenterView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let foc = Int(rng.next() % 6)
        let hue = Double(rng.next() % 1000) / 1000.0

        ZStack(alignment: .trailing) {
            Color(hue: hue, saturation: 0.5, brightness: 0.2).ignoresSafeArea()
            Color.black.opacity(0.65).ignoresSafeArea()

            VStack(alignment: .leading, spacing: 20) {
                // Profile & Sleep
                HStack(spacing: 16) {
                    let isUserFoc = (foc == 0)
                    HStack(spacing: 14) {
                        Image(systemName: "person.crop.circle.fill").font(.system(size: 38))
                            .foregroundColor(isUserFoc ? .black : .white)
                            .captureFrame(id: "imageView_profile_avatar")
                        Text("Joseph").font(.system(size: 24, weight: .bold))
                            .foregroundColor(isUserFoc ? .black : .white)
                            .captureFrame(id: "label_profile_name")
                    }
                    .padding(.horizontal, 18).frame(height: 64)
                    .background(isUserFoc ? Color.white : Color.white.opacity(0.12))
                    .cornerRadius(20)
                    .captureFrame(id: isUserFoc ? "collectionItem_profile_focused" : "collectionItem_profile_unfocused")

                    Spacer()

                    Text("09:41").font(.system(size: 26, weight: .semibold))
                        .foregroundColor(.white.opacity(0.9)).captureFrame(id: "label_clock_time")

                    let isSleepFoc = (foc == 1)
                    Image(systemName: "power").font(.system(size: 22, weight: .bold))
                        .foregroundColor(isSleepFoc ? .red : .white)
                        .frame(width: 64, height: 64)
                        .background(isSleepFoc ? Color.white : Color.white.opacity(0.12))
                        .cornerRadius(20)
                        .captureFrame(id: isSleepFoc ? "cancelAction_sleep_focused" : "cancelAction_sleep_unfocused")
                }

                // Audio Output
                let isAudioFoc = (foc == 2)
                VStack(alignment: .leading, spacing: 4) {
                    Text("Audio Destination").font(.system(size: 16)).foregroundColor(isAudioFoc ? .black.opacity(0.7) : .white.opacity(0.6))
                        .captureFrame(id: "label_audio_header")
                    Text("Living Room HomePod").font(.system(size: 22, weight: .bold))
                        .foregroundColor(isAudioFoc ? .black : .white)
                        .captureFrame(id: "label_audio_device")
                }
                .padding(20).frame(maxWidth: .infinity, alignment: .leading)
                .background(isAudioFoc ? Color.white : Color.white.opacity(0.1)).cornerRadius(20)
                .captureFrame(id: isAudioFoc ? "listRow_audio_dest_focused" : "listRow_audio_dest_unfocused")

                // Volume Slider
                let isVolFoc = (foc == 3)
                VStack(spacing: 8) {
                    HStack {
                        Image(systemName: "speaker.fill").foregroundColor(isVolFoc ? .black : .white)
                        Spacer()
                        Image(systemName: "speaker.wave.3.fill").foregroundColor(isVolFoc ? .black : .white)
                    }
                    Capsule().fill(isVolFoc ? Color.black : Color.white).frame(height: 12)
                        .captureFrame(id: "slider_volume_control")
                }
                .padding(20).frame(maxWidth: .infinity)
                .background(isVolFoc ? Color.white : Color.white.opacity(0.1)).cornerRadius(20)
                .captureFrame(id: isVolFoc ? "primaryButton_vol_tile_focused" : "primaryButton_vol_tile_unfocused")

                // Toggles
                HStack(spacing: 16) {
                    let isDNDFoc = (foc == 4)
                    HStack(spacing: 12) {
                        Image(systemName: "moon.fill")
                        Text("Do Not Disturb").font(.system(size: 20, weight: .semibold))
                    }
                    .foregroundColor(isDNDFoc ? .black : .white)
                    .padding(.horizontal, 16).frame(maxWidth: .infinity, maxHeight: 64)
                    .background(isDNDFoc ? Color.white : Color.white.opacity(0.1)).cornerRadius(18)
                    .captureFrame(id: isDNDFoc ? "toggle_dnd_focused" : "toggle_dnd_unfocused")

                    let isWifiFoc = (foc == 5)
                    HStack(spacing: 12) {
                        Image(systemName: "wifi")
                        Text("Wi-Fi").font(.system(size: 20, weight: .semibold))
                    }
                    .foregroundColor(isWifiFoc ? .black : .white)
                    .padding(.horizontal, 16).frame(maxWidth: .infinity, maxHeight: 64)
                    .background(isWifiFoc ? Color.white : Color.blue.opacity(0.5)).cornerRadius(18)
                    .captureFrame(id: isWifiFoc ? "secondaryButton_wifi_focused" : "secondaryButton_wifi_unfocused")
                }

                Spacer()
            }
            .padding(32).frame(width: 660, height: 1080)
            .background(Color(red: 0.12, green: 0.12, blue: 0.16))
            .captureFrame(id: "sidebar_control_center")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 9: Split Settings Hierarchy

struct SplitSettingsView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let focRow = Int(rng.next() % 5)
        let cats = ["Video and Audio", "General", "Remotes", "Network", "Users"]

        ZStack(alignment: .topLeading) {
            Color(red: 0.05, green: 0.05, blue: 0.08).ignoresSafeArea()

            VStack(alignment: .leading, spacing: 16) {
                // Header Bar
                HStack(spacing: 16) {
                    HStack(spacing: 8) {
                        Image(systemName: "chevron.left").font(.system(size: 24, weight: .bold))
                        Text("Settings").font(.system(size: 28, weight: .semibold))
                    }
                    .padding(.horizontal, 16).padding(.vertical, 8)
                    .captureFrame(id: "secondaryButton_back_nav")

                    Image(systemName: "chevron.right").foregroundColor(.white.opacity(0.4))
                    Text("Video and Audio").font(.system(size: 34, weight: .bold)).foregroundColor(.white)
                        .captureFrame(id: "label_screen_title")
                    Spacer()
                }
                .padding(.horizontal, 90).padding(.top, 40).frame(height: 100)
                .captureFrame(id: "navigationBar_settings_header")

                // Split Pane
                HStack(alignment: .top, spacing: 60) {
                    VStack(spacing: 12) {
                        ForEach(0..<cats.count, id: \.self) { idx in
                            HStack {
                                Text(cats[idx]).font(.system(size: 24, weight: idx == 0 ? .bold : .medium)).foregroundColor(.white)
                                Spacer()
                                Image(systemName: "chevron.right").foregroundColor(.white.opacity(0.4))
                            }
                            .padding(.horizontal, 24).frame(width: 520, height: 72)
                            .background(idx == 0 ? Color.white.opacity(0.18) : Color.white.opacity(0.06)).cornerRadius(16)
                            .captureFrame(id: "listRow_cat_\(idx)_unfocused")
                        }
                    }

                    VStack(spacing: 14) {
                        // Resolution row
                        HStack {
                            Text("Resolution").font(.system(size: 24, weight: focRow == 0 ? .bold : .medium))
                                .foregroundColor(focRow == 0 ? .black : .white)
                            Spacer()
                            Text("4K SDR (60Hz)").foregroundColor(focRow == 0 ? .black.opacity(0.7) : .white.opacity(0.6))
                        }
                        .padding(.horizontal, 28).frame(width: 1040, height: 76)
                        .background(focRow == 0 ? Color.white : Color.white.opacity(0.08)).cornerRadius(16)
                        .captureFrame(id: focRow == 0 ? "listRow_resolution_focused" : "listRow_resolution_unfocused")

                        // Segmented control format
                        HStack {
                            Text("Format").font(.system(size: 24, weight: focRow == 1 ? .bold : .medium))
                                .foregroundColor(focRow == 1 ? .black : .white)
                            Spacer()
                            HStack(spacing: 6) {
                                Text("SDR").font(.system(size: 18, weight: .bold)).padding(.horizontal, 14).padding(.vertical, 6)
                                    .background(Color.black).foregroundColor(.white).cornerRadius(8)
                                Text("HDR").font(.system(size: 18)).padding(.horizontal, 14).padding(.vertical, 6).foregroundColor(.white.opacity(0.7))
                            }
                            .padding(4).background(Color.white.opacity(0.12)).cornerRadius(12)
                            .captureFrame(id: focRow == 1 ? "segmentedControl_format_focused" : "segmentedControl_format_unfocused")
                        }
                        .padding(.horizontal, 28).frame(width: 1040, height: 76)
                        .background(focRow == 1 ? Color.white : Color.white.opacity(0.08)).cornerRadius(16)
                        .captureFrame(id: focRow == 1 ? "listRow_format_focused" : "listRow_format_unfocused")

                        // Match Content toggle
                        HStack {
                            Text("Match Content").font(.system(size: 24, weight: focRow == 2 ? .bold : .medium))
                                .foregroundColor(focRow == 2 ? .black : .white)
                            Spacer()
                            Toggle("", isOn: .constant(true)).labelsHidden()
                                .captureFrame(id: focRow == 2 ? "toggle_match_content_focused" : "toggle_match_content_unfocused")
                        }
                        .padding(.horizontal, 28).frame(width: 1040, height: 76)
                        .background(focRow == 2 ? Color.white : Color.white.opacity(0.08)).cornerRadius(16)
                        .captureFrame(id: focRow == 2 ? "listRow_match_focused" : "listRow_match_unfocused")

                        // Audio Delay stepper
                        HStack {
                            Text("Audio Sync Delay").font(.system(size: 24, weight: focRow == 3 ? .bold : .medium))
                                .foregroundColor(focRow == 3 ? .black : .white)
                            Spacer()
                            HStack(spacing: 16) {
                                Image(systemName: "minus.circle.fill")
                                Text("20 ms").font(.system(size: 22, weight: .bold))
                                Image(systemName: "plus.circle.fill")
                            }
                            .foregroundColor(focRow == 3 ? .black : .white)
                            .captureFrame(id: focRow == 3 ? "stepperControl_delay_focused" : "stepperControl_delay_unfocused")
                        }
                        .padding(.horizontal, 28).frame(width: 1040, height: 76)
                        .background(focRow == 3 ? Color.white : Color.white.opacity(0.08)).cornerRadius(16)
                        .captureFrame(id: focRow == 3 ? "listRow_delay_focused" : "listRow_delay_unfocused")
                    }
                }
                .padding(.horizontal, 90)
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 10: AVKit Playback Chrome

struct AVKitPlaybackView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let foc = Int(rng.next() % 5) // 0: scrubber, 1: back, 2: play, 3: fwd, 4: skipIntro
        let hue = Double(rng.next() % 1000) / 1000.0

        ZStack(alignment: .bottom) {
            LinearGradient(
                colors: [Color(hue: hue, saturation: 0.8, brightness: 0.3), Color.black],
                startPoint: .topLeading, endPoint: .bottomTrailing
            ).ignoresSafeArea()

            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Severance").font(.system(size: 34, weight: .bold)).foregroundColor(.white)
                            .captureFrame(id: "label_media_title")
                        Text("S1:E4 • The You You Are").font(.system(size: 22)).foregroundColor(.white.opacity(0.75))
                            .captureFrame(id: "label_episode_title")
                    }
                    Spacer()
                    Text("TV-MA").font(.system(size: 16, weight: .heavy)).foregroundColor(.white)
                        .padding(6).background(Color.black.opacity(0.6)).cornerRadius(6)
                        .captureFrame(id: "label_rating_bug")
                }
                .padding(.horizontal, 90).padding(.top, 60)
                Spacer()
            }

            // Skip Intro pill
            VStack {
                Spacer()
                HStack {
                    Spacer()
                    let isSkipFoc = (foc == 4)
                    HStack(spacing: 8) {
                        Text("Skip Intro").font(.system(size: 22, weight: .bold))
                        Image(systemName: "forward.end.fill")
                    }
                    .foregroundColor(isSkipFoc ? .black : .white)
                    .padding(.horizontal, 28).padding(.vertical, 14)
                    .background(isSkipFoc ? Color.white : Color.black.opacity(0.6)).cornerRadius(24)
                    .captureFrame(id: isSkipFoc ? "secondaryButton_skip_intro_focused" : "secondaryButton_skip_intro_unfocused")
                    .padding(.trailing, 90).padding(.bottom, 220)
                }
            }

            // Bottom Transport Toolbar
            VStack(spacing: 24) {
                let isScrubFoc = (foc == 0)
                HStack(spacing: 24) {
                    Text("24:18").font(.system(size: 22, design: .monospaced)).foregroundColor(.white.opacity(0.85))
                        .captureFrame(id: "label_elapsed_time")

                    Capsule().fill(isScrubFoc ? Color.white : Color.white.opacity(0.5)).frame(height: 12)
                        .captureFrame(id: isScrubFoc ? "slider_scrubber_focused" : "slider_scrubber_unfocused")

                    Text("-32:42").font(.system(size: 22, design: .monospaced)).foregroundColor(.white.opacity(0.85))
                        .captureFrame(id: "label_remaining_time")
                }

                HStack(spacing: 36) {
                    let isBackFoc = (foc == 1)
                    Image(systemName: "gobackward.10").font(.system(size: 32))
                        .foregroundColor(isBackFoc ? .black : .white).frame(width: 72, height: 72)
                        .background(isBackFoc ? Color.white : Color.white.opacity(0.15)).cornerRadius(20)
                        .captureFrame(id: isBackFoc ? "secondaryButton_skip_back_focused" : "secondaryButton_skip_back_unfocused")

                    let isPlayFoc = (foc == 2)
                    Image(systemName: "pause.fill").font(.system(size: 38, weight: .bold))
                        .foregroundColor(isPlayFoc ? .black : .white).frame(width: 88, height: 88)
                        .background(isPlayFoc ? Color.white : Color.white.opacity(0.2)).cornerRadius(24)
                        .captureFrame(id: isPlayFoc ? "primaryButton_play_pause_focused" : "primaryButton_play_pause_unfocused")

                    let isFwdFoc = (foc == 3)
                    Image(systemName: "goforward.10").font(.system(size: 32))
                        .foregroundColor(isFwdFoc ? .black : .white).frame(width: 72, height: 72)
                        .background(isFwdFoc ? Color.white : Color.white.opacity(0.15)).cornerRadius(20)
                        .captureFrame(id: isFwdFoc ? "secondaryButton_skip_forward_focused" : "secondaryButton_skip_forward_unfocused")
                }
            }
            .padding(.horizontal, 90).padding(.bottom, 60).frame(maxWidth: .infinity)
            .captureFrame(id: "toolbar_transport_controls")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 11: Audio & Subtitles Drawer

struct AudioSubtitlesView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let foc = Int(rng.next() % 4) // 0: segment, 1: lang1, 2: lang2, 3: dialogue

        ZStack {
            Color.black.opacity(0.82).ignoresSafeArea()

            VStack(spacing: 24) {
                // Segmented Selector
                let isSegFoc = (foc == 0)
                HStack(spacing: 0) {
                    Text("Subtitles").font(.system(size: 22, weight: .bold)).foregroundColor(.black)
                        .frame(maxWidth: .infinity).frame(height: 52).background(Color.white).cornerRadius(12)
                    Text("Audio").font(.system(size: 22)).foregroundColor(.white.opacity(0.7))
                        .frame(maxWidth: .infinity).frame(height: 52)
                }
                .padding(4).frame(width: 640).background(isSegFoc ? Color.white : Color.white.opacity(0.12)).cornerRadius(16)
                .captureFrame(id: isSegFoc ? "segmentedControl_tabs_focused" : "segmentedControl_tabs_unfocused")

                // Language Rows
                VStack(spacing: 8) {
                    let isL1Foc = (foc == 1)
                    HStack {
                        Text("English [CC]").font(.system(size: 22, weight: isL1Foc ? .bold : .medium))
                            .foregroundColor(isL1Foc ? .black : .white)
                            .captureFrame(id: "label_lang_0")
                        Spacer()
                        Image(systemName: "checkmark").foregroundColor(isL1Foc ? .black : .white)
                            .captureFrame(id: "imageView_checkmark_0")
                    }
                    .padding(.horizontal, 24).frame(width: 640, height: 60)
                    .background(isL1Foc ? Color.white : Color.white.opacity(0.15)).cornerRadius(14)
                    .captureFrame(id: isL1Foc ? "listRow_lang_0_focused" : "listRow_lang_0_unfocused")

                    let isL2Foc = (foc == 2)
                    HStack {
                        Text("Spanish").font(.system(size: 22, weight: isL2Foc ? .bold : .medium))
                            .foregroundColor(isL2Foc ? .black : .white)
                            .captureFrame(id: "label_lang_1")
                        Spacer()
                    }
                    .padding(.horizontal, 24).frame(width: 640, height: 60)
                    .background(isL2Foc ? Color.white : Color.white.opacity(0.06)).cornerRadius(14)
                    .captureFrame(id: isL2Foc ? "listRow_lang_1_focused" : "listRow_lang_1_unfocused")
                }

                // Dialogue Boost Toggle
                let isDiagFoc = (foc == 3)
                HStack {
                    Text("Enhance Dialogue").font(.system(size: 20, weight: isDiagFoc ? .bold : .medium))
                        .foregroundColor(isDiagFoc ? .black : .white)
                        .captureFrame(id: "label_dialogue_title")
                    Spacer()
                    Toggle("", isOn: .constant(true)).labelsHidden()
                        .captureFrame(id: isDiagFoc ? "toggle_enhance_dialogue_focused" : "toggle_enhance_dialogue_unfocused")
                }
                .padding(.horizontal, 24).frame(width: 640, height: 60)
                .background(isDiagFoc ? Color.white : Color.white.opacity(0.06)).cornerRadius(14)
                .captureFrame(id: isDiagFoc ? "listRow_dialogue_focused" : "listRow_dialogue_unfocused")
            }
            .padding(32).background(Color(red: 0.14, green: 0.14, blue: 0.18)).cornerRadius(28)
            .captureFrame(id: "popover_audio_subtitles_card")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 12: SharePlay Group Chrome

struct SharePlayView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let foc = Int(rng.next() % 4) // 0: join, 1: mute, 2: leave, 3: endForAll
        let hue = Double(rng.next() % 1000) / 1000.0

        ZStack(alignment: .topTrailing) {
            LinearGradient(
                colors: [Color(hue: hue, saturation: 0.7, brightness: 0.3), Color.black],
                startPoint: .topLeading, endPoint: .bottomTrailing
            ).ignoresSafeArea()
            Color.black.opacity(0.45).ignoresSafeArea()

            VStack(alignment: .leading, spacing: 20) {
                HStack(spacing: 12) {
                    Image(systemName: "shareplay").font(.system(size: 24, weight: .bold)).foregroundColor(.green)
                        .captureFrame(id: "imageView_shareplay_icon")
                    VStack(alignment: .leading, spacing: 2) {
                        Text("SharePlay Active").font(.system(size: 20, weight: .bold)).foregroundColor(.white)
                            .captureFrame(id: "label_shareplay_title")
                        Text("Movie Night with Family").font(.system(size: 16)).foregroundColor(.white.opacity(0.75))
                            .captureFrame(id: "label_group_title")
                    }
                    Spacer()
                    Text("32:15").font(.system(size: 18, design: .monospaced)).foregroundColor(.white.opacity(0.8))
                        .captureFrame(id: "label_call_duration")
                }

                // Avatars
                HStack(spacing: 20) {
                    ForEach(0..<3, id: \.self) { idx in
                        VStack(spacing: 6) {
                            Circle().fill(Color.blue.opacity(0.6)).frame(width: 64, height: 64)
                                .captureFrame(id: "collectionItem_avatar_\(idx)_unfocused")
                            Text("Person \(idx + 1)").font(.system(size: 16)).foregroundColor(.white.opacity(0.85))
                                .captureFrame(id: "label_part_\(idx)")
                        }
                    }
                }

                HStack(spacing: 16) {
                    let isMuteFoc = (foc == 1)
                    Image(systemName: "mic.fill").font(.system(size: 22))
                        .foregroundColor(isMuteFoc ? .black : .white).frame(width: 60, height: 60)
                        .background(isMuteFoc ? Color.white : Color.white.opacity(0.12)).cornerRadius(18)
                        .captureFrame(id: isMuteFoc ? "secondaryButton_mute_focused" : "secondaryButton_mute_unfocused")

                    let isJoinFoc = (foc == 0)
                    Text("Play Together").font(.system(size: 20, weight: .bold))
                        .foregroundColor(isJoinFoc ? .black : .white).padding(.horizontal, 24).frame(height: 60)
                        .background(isJoinFoc ? Color.white : Color.green.opacity(0.4)).cornerRadius(18)
                        .captureFrame(id: isJoinFoc ? "primaryButton_join_focused" : "primaryButton_join_unfocused")

                    let isLeaveFoc = (foc == 2)
                    Text("Leave").font(.system(size: 20, weight: .semibold))
                        .foregroundColor(isLeaveFoc ? .black : .white).padding(.horizontal, 20).frame(height: 60)
                        .background(isLeaveFoc ? Color.white : Color.white.opacity(0.12)).cornerRadius(18)
                        .captureFrame(id: isLeaveFoc ? "cancelAction_leave_focused" : "cancelAction_leave_unfocused")

                    let isEndFoc = (foc == 3)
                    Image(systemName: "phone.down.fill").font(.system(size: 22))
                        .foregroundColor(isEndFoc ? .white : .red).frame(width: 60, height: 60)
                        .background(isEndFoc ? Color.red : Color.red.opacity(0.2)).cornerRadius(18)
                        .captureFrame(id: isEndFoc ? "destructiveButton_end_focused" : "destructiveButton_end_unfocused")
                }
            }
            .padding(28).frame(width: 620)
            .background(Color(red: 0.12, green: 0.12, blue: 0.16)).cornerRadius(24)
            .padding(.top, 60).padding(.trailing, 80)
            .captureFrame(id: "sheet_shareplay_card")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 13: On-Screen Keyboard

struct KeyboardView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let keys = [
            ["A", "B", "C", "D", "E", "F", "G"],
            ["H", "I", "J", "K", "L", "M", "N"],
            ["O", "P", "Q", "R", "S", "T", "U"],
            ["V", "W", "X", "Y", "Z", "1", "2"]
        ]
        let focR = Int(rng.next() % 4)
        let focC = Int(rng.next() % 7)

        ZStack(alignment: .top) {
            Color(red: 0.06, green: 0.06, blue: 0.09).ignoresSafeArea()

            VStack(spacing: 36) {
                // Search Input Box
                HStack(spacing: 16) {
                    Image(systemName: "magnifyingglass").font(.system(size: 26)).foregroundColor(.white.opacity(0.6))
                        .captureFrame(id: "imageView_search_icon")
                    Text("Ted Lasso").font(.system(size: 30, weight: .semibold)).foregroundColor(.white)
                        .captureFrame(id: "label_query_text")
                    Spacer()
                    Image(systemName: "xmark.circle.fill").font(.system(size: 24)).foregroundColor(.white.opacity(0.5))
                        .captureFrame(id: "cancelAction_clear_query")
                }
                .padding(.horizontal, 28).frame(width: 1080, height: 76)
                .background(Color.white.opacity(0.1)).cornerRadius(20)
                .captureFrame(id: "searchField_keyboard_input")
                .padding(.top, 70)

                // Key Grid & Actions
                HStack(alignment: .top, spacing: 48) {
                    VStack(spacing: 12) {
                        ForEach(0..<keys.count, id: \.self) { r in
                            HStack(spacing: 12) {
                                ForEach(0..<keys[r].count, id: \.self) { c in
                                    let isFoc = (r == focR && c == focC)
                                    let ch = keys[r][c]
                                    Text(ch).font(.system(size: 26, weight: isFoc ? .bold : .medium))
                                        .foregroundColor(isFoc ? .black : .white).frame(width: 68, height: 64)
                                        .background(isFoc ? Color.white : Color.white.opacity(0.08)).cornerRadius(14)
                                        .scaleEffect(isFoc ? 1.12 : 1.0)
                                        .shadow(color: isFoc ? Color.white.opacity(0.5) : Color.clear, radius: 10)
                                        .captureFrame(id: isFoc ? "collectionItem_key_\(ch)_focused" : "collectionItem_key_\(ch)_unfocused")
                                }
                            }
                        }
                    }

                    VStack(spacing: 12) {
                        HStack(spacing: 10) {
                            Image(systemName: "mic.fill")
                            Text("Dictate").font(.system(size: 20, weight: .semibold))
                        }
                        .foregroundColor(.white).frame(width: 220, height: 64)
                        .background(Color.white.opacity(0.08)).cornerRadius(14)
                        .captureFrame(id: "secondaryButton_dictate_unfocused")

                        Text("Space").font(.system(size: 20, weight: .semibold)).foregroundColor(.white)
                            .frame(width: 220, height: 64).background(Color.white.opacity(0.08)).cornerRadius(14)
                            .captureFrame(id: "secondaryButton_space_unfocused")

                        HStack(spacing: 10) {
                            Image(systemName: "delete.left")
                            Text("Delete").font(.system(size: 20, weight: .semibold))
                        }
                        .foregroundColor(.white).frame(width: 220, height: 64)
                        .background(Color.white.opacity(0.08)).cornerRadius(14)
                        .captureFrame(id: "secondaryButton_delete_unfocused")

                        Text("Search").font(.system(size: 22, weight: .bold)).foregroundColor(.black)
                            .frame(width: 220, height: 64).background(Color.white).cornerRadius(14)
                            .captureFrame(id: "primaryButton_search_action_unfocused")
                    }
                }
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 14: Siri Voice Dictation Overlay

struct SiriOverlayView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let focCard = Int(rng.next() % 4)
        let hue = Double(rng.next() % 1000) / 1000.0

        ZStack(alignment: .bottom) {
            LinearGradient(
                colors: [Color(hue: hue, saturation: 0.6, brightness: 0.3), Color.black],
                startPoint: .topLeading, endPoint: .bottomTrailing
            ).ignoresSafeArea()
            Color.black.opacity(0.6).ignoresSafeArea()

            VStack(spacing: 24) {
                HStack(spacing: 20) {
                    Circle().fill(LinearGradient(colors: [.purple, .cyan, .pink], startPoint: .topLeading, endPoint: .bottomTrailing))
                        .frame(width: 52, height: 52)
                        .captureFrame(id: "imageView_siri_orb")

                    VStack(alignment: .leading, spacing: 4) {
                        Text("What's the weather today?").font(.system(size: 26, weight: .bold)).foregroundColor(.white)
                            .captureFrame(id: "label_siri_query")
                        Text("It's currently 72° and sunny in Cupertino.").font(.system(size: 22)).foregroundColor(.white.opacity(0.8))
                            .captureFrame(id: "label_siri_response")
                    }
                    Spacer()
                }

                HStack(spacing: 20) {
                    ForEach(["Today", "Wed", "Thu", "Fri"], id: \.self) { day in
                        let idx = ["Today", "Wed", "Thu", "Fri"].firstIndex(of: day)!
                        let isFoc = (idx == focCard)
                        VStack(spacing: 12) {
                            Text(day).font(.system(size: 20, weight: isFoc ? .bold : .medium))
                                .foregroundColor(isFoc ? .black : .white.opacity(0.8))
                                .captureFrame(id: "label_day_\(idx)")
                            Image(systemName: "sun.max.fill").font(.system(size: 32))
                                .foregroundColor(isFoc ? .black : .yellow)
                                .captureFrame(id: "imageView_weather_\(idx)")
                            Text("72°").font(.system(size: 24, weight: .bold)).foregroundColor(isFoc ? .black : .white)
                                .captureFrame(id: "label_temp_\(idx)")
                        }
                        .frame(width: 170, height: 160)
                        .background(isFoc ? Color.white : Color.white.opacity(0.1)).cornerRadius(20)
                        .scaleEffect(isFoc ? 1.08 : 1.0)
                        .shadow(color: isFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                        .captureFrame(id: isFoc ? "collectionItem_forecast_\(idx)_focused" : "collectionItem_forecast_\(idx)_unfocused")
                    }
                }

                HStack {
                    Spacer()
                    HStack(spacing: 10) {
                        Image(systemName: "arrow.up.forward.app.fill")
                        Text("Open Weather").font(.system(size: 22, weight: .bold))
                    }
                    .foregroundColor(.white).padding(.horizontal, 28).padding(.vertical, 14)
                    .background(Color.white.opacity(0.15)).cornerRadius(18)
                    .captureFrame(id: "primaryButton_open_app_unfocused")
                }
            }
            .padding(32).frame(width: 860)
            .background(Color(red: 0.12, green: 0.12, blue: 0.16)).cornerRadius(28)
            .padding(.bottom, 60)
            .captureFrame(id: "popover_siri_card")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 15: Hard Negative

struct HardNegativeView: View {
    let seed: UInt64

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let hue1 = Double(rng.next() % 1000) / 1000.0
        let hue2 = Double(rng.next() % 1000) / 1000.0

        LinearGradient(
            colors: [Color(hue: hue1, saturation: 0.8, brightness: 0.3), Color(hue: hue2, saturation: 0.7, brightness: 0.1), Color.black],
            startPoint: .topLeading, endPoint: .bottomTrailing
        )
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Generator Orchestrator

@MainActor
func generateDataset() async {
    var targetCount = 2000
    var outPath = "dataset/tvos_dataset"
    var sampleOnly = false

    var args = CommandLine.arguments.dropFirst()
    while let arg = args.first {
        args = args.dropFirst()
        if arg == "--count", let countStr = args.first, let c = Int(countStr) {
            targetCount = c
            args = args.dropFirst()
        } else if arg == "--output", let p = args.first {
            outPath = p
            args = args.dropFirst()
        } else if arg == "--sample" {
            sampleOnly = true
        }
    }

    let outDir = URL(fileURLWithPath: outPath)
    let fm = FileManager.default
    for split in ["train", "validation", "test"] {
        let dir = outDir.appendingPathComponent(split)
        try? fm.removeItem(at: dir)
        try? fm.createDirectory(at: dir, withIntermediateDirectories: true)
    }

    let counts: [(name: String, count: Int)]
    if sampleOnly {
        counts = [
            ("tvOSHomeScreen", 1),
            ("tvOSSettings", 1),
            ("tvOSSplitSettings", 1),
            ("tvOSAlert", 1),
            ("tvOSTopTabBar", 1),
            ("tvOSContextMenu", 1),
            ("tvOSSidebarMenu", 1),
            ("tvOSTopShelfHero", 1),
            ("tvOSControlCenter", 1),
            ("tvOSAVKitPlayback", 1),
            ("tvOSAudioSubtitles", 1),
            ("tvOSSharePlay", 1),
            ("tvOSKeyboard", 1),
            ("tvOSSiriOverlay", 1),
            ("tvOSHardNegatives", 1)
        ]
    } else {
        // Distribute proportionally across all 15 template families
        let baseCount = max(1, targetCount / 15)
        counts = [
            ("tvOSHomeScreen", baseCount),
            ("tvOSSettings", baseCount),
            ("tvOSSplitSettings", baseCount),
            ("tvOSAlert", baseCount),
            ("tvOSTopTabBar", baseCount),
            ("tvOSContextMenu", baseCount),
            ("tvOSSidebarMenu", baseCount),
            ("tvOSTopShelfHero", baseCount),
            ("tvOSControlCenter", baseCount),
            ("tvOSAVKitPlayback", baseCount),
            ("tvOSAudioSubtitles", baseCount),
            ("tvOSSharePlay", baseCount),
            ("tvOSKeyboard", baseCount),
            ("tvOSSiriOverlay", baseCount),
            ("tvOSHardNegatives", max(1, targetCount - (baseCount * 14)))
        ]
    }

    let totalTarget = counts.reduce(0) { $0 + $1.count }
    print("Generating \(totalTarget) tvOS OS UI images across 15 families at 1920x1080 into \(outDir.path)...")
    let start = Date()

    var globalIndex = 0

    func renderAndSave<V: View>(view: V, family: String) {
        var capturedFrames: [String: CGRect] = [:]
        let wrapped = view.onPreferenceChange(FramePreference.self) { prefs in
            capturedFrames = prefs
        }

        let renderer = ImageRenderer(content: wrapped)
        renderer.scale = 1.0
        guard let cgImg = renderer.cgImage else {
            fputs("WARNING: Failed to render image for \(family)_\(globalIndex)\n", stderr)
            return
        }

        // Split: 80% train, 10% validation, 10% test
        let split: String
        let mod = globalIndex % 10
        if mod == 9 { split = "test" }
        else if mod == 8 { split = "validation" }
        else { split = "train" }

        let fileBase = String(format: "img_%06d", globalIndex)
        let pngURL = outDir.appendingPathComponent(split).appendingPathComponent("\(fileBase).png")
        let jsonURL = outDir.appendingPathComponent(split).appendingPathComponent("\(fileBase).json")

        // Save PNG
        guard let dest = CGImageDestinationCreateWithURL(pngURL as CFURL, UTType.png.identifier as CFString, 1, nil) else { return }
        CGImageDestinationAddImage(dest, cgImg, nil)
        CGImageDestinationFinalize(dest)

        let pngData = (try? Data(contentsOf: pngURL)) ?? Data()
        let sha256 = SHA256.hash(data: pngData).map { String(format: "%02x", $0) }.joined()

        // Build Elements
        var elements: [[String: Any]] = []
        for (id, frame) in capturedFrames {
            let elemType = id.components(separatedBy: "_").first ?? id
            let isFocused = id.contains("_focused") ? true : (id.contains("_unfocused") ? false : nil)

            let xNorm = max(0.0, min(1.0, frame.minX / 1920.0))
            let yNorm = max(0.0, min(1.0, 1.0 - (frame.minY + frame.height) / 1080.0))
            let wNorm = max(0.0, min(1.0 - xNorm, frame.width / 1920.0))
            let hNorm = max(0.0, min(1.0 - yNorm, frame.height / 1080.0))

            var stateDict: [String: Any] = ["isEnabled": true, "isSelected": false]
            if let f = isFocused { stateDict["isFocused"] = f }

            let elemDict: [String: Any] = [
                "id": id,
                "elementType": elemType,
                "framework": "SwiftUI",
                "boundsPixels": ["x": frame.minX, "y": frame.minY, "width": frame.width, "height": frame.height],
                "boundsPoints": ["x": frame.minX, "y": frame.minY, "width": frame.width, "height": frame.height],
                "boundsVisionNormalized": ["x": xNorm, "y": yNorm, "width": wNorm, "height": hNorm],
                "visibleText": NSNull(),
                "accessibilityLabel": NSNull(),
                "traits": [] as [String],
                "state": stateDict,
                "occluded": false,
                "excluded": false,
                "knownIssues": [] as [String]
            ]
            elements.append(elemDict)
        }

        let sidecar: [String: Any] = [
            "schemaVersion": "1.0",
            "imageSHA256": sha256,
            "image": [
                "fileName": "\(fileBase).png",
                "pixelWidth": 1920,
                "pixelHeight": 1080,
                "scale": 1,
                "platform": "tvOS",
                "osVersion": "tvOS 17.2",
                "deviceName": "Apple TV 4K",
                "interfaceIdiom": "tv",
                "orientation": "landscape",
                "colorScheme": "dark",
                "dynamicTypeSize": "large",
                "locale": "en_US",
                "layoutDirection": "ltr",
                "safeAreaInsets": ["top": 60, "left": 90, "bottom": 60, "right": 90],
                "reduceTransparency": false,
                "increaseContrast": false,
                "boldText": false,
                "buttonShapes": false,
                "onOffLabels": false,
                "smartInvert": false
            ],
            "generatorProfile": [
                "templateFamily": family,
                "seed": globalIndex,
                "generatorVersion": "tvos-2.0",
                "isolationTemplate": false,
                "lowDensity": false,
                "simulatorState": [
                    "time": "09:41",
                    "batteryLevel": 100,
                    "batteryState": "charging",
                    "cellularBars": 0,
                    "wifiBars": 3,
                    "operatorName": ""
                ]
            ],
            "elements": elements
        ]

        if let jsonBytes = try? JSONSerialization.data(withJSONObject: sidecar, options: [.prettyPrinted, .sortedKeys]) {
            try? jsonBytes.write(to: jsonURL)
        }

        globalIndex += 1
        if globalIndex % 100 == 0 || globalIndex == totalTarget {
            let el = max(0.001, Date().timeIntervalSince(start))
            print("  Progress: \(globalIndex)/\(totalTarget) images generated (\(String(format: "%.1f", Double(globalIndex) / el)) fps)...")
        }
    }

    var corpus = ContentCorpus(seed: 42)

    for (family, count) in counts {
        for i in 0..<count {
            let s = UInt64(globalIndex * 1000 + i)
            switch family {
            case "tvOSHomeScreen":
                renderAndSave(view: HomeScreenView(seed: s, corpus: corpus), family: family)
            case "tvOSSettings":
                renderAndSave(view: SettingsView(seed: s, corpus: corpus), family: family)
            case "tvOSSplitSettings":
                renderAndSave(view: SplitSettingsView(seed: s, corpus: corpus), family: family)
            case "tvOSAlert":
                renderAndSave(view: AlertView(seed: s, corpus: corpus), family: family)
            case "tvOSTopTabBar":
                renderAndSave(view: TabBarView(seed: s, corpus: corpus), family: family)
            case "tvOSContextMenu":
                renderAndSave(view: ContextMenuView(seed: s, corpus: corpus), family: family)
            case "tvOSSidebarMenu":
                renderAndSave(view: SidebarMenuView(seed: s, corpus: corpus), family: family)
            case "tvOSTopShelfHero":
                renderAndSave(view: TopShelfHeroView(seed: s, corpus: corpus), family: family)
            case "tvOSControlCenter":
                renderAndSave(view: ControlCenterView(seed: s, corpus: corpus), family: family)
            case "tvOSAVKitPlayback":
                renderAndSave(view: AVKitPlaybackView(seed: s, corpus: corpus), family: family)
            case "tvOSAudioSubtitles":
                renderAndSave(view: AudioSubtitlesView(seed: s, corpus: corpus), family: family)
            case "tvOSSharePlay":
                renderAndSave(view: SharePlayView(seed: s, corpus: corpus), family: family)
            case "tvOSKeyboard":
                renderAndSave(view: KeyboardView(seed: s, corpus: corpus), family: family)
            case "tvOSSiriOverlay":
                renderAndSave(view: SiriOverlayView(seed: s, corpus: corpus), family: family)
            case "tvOSHardNegatives":
                renderAndSave(view: HardNegativeView(seed: s), family: family)
            default:
                break
            }
        }
    }

    let elapsed = max(0.001, Date().timeIntervalSince(start))
    print("Complete! Generated \(globalIndex) images in \(String(format: "%.1f", elapsed))s (\(String(format: "%.1f", Double(globalIndex) / elapsed)) fps).")

    // Write manifest
    var templateCounts: [String: Int] = [:]
    for c in counts { templateCounts[c.name] = c.count }

    let manifest: [String: Any] = [
        "generatorVersion": "tvos-2.0",
        "generatedAt": ISO8601DateFormatter().string(from: Date()),
        "totalImages": globalIndex,
        "resolution": "1920x1080",
        "platform": "tvOS",
        "templateCounts": templateCounts
    ]
    if let mData = try? JSONSerialization.data(withJSONObject: manifest, options: [.prettyPrinted, .sortedKeys]) {
        try? mData.write(to: outDir.appendingPathComponent("manifest.json"))
    }
}

Task { @MainActor in
    await generateDataset()
    exit(0)
}
RunLoop.main.run()
