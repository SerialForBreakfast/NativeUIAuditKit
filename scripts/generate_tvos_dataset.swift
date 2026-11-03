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
    /// Records the frame only when `on` is true. Use it to move a capture outside a `scaleEffect` (PILLS560 R6).
    func captureFrame(id: String, if on: Bool) -> some View {
        background(
            GeometryReader { geo in
                Color.clear.preference(key: FramePreference.self, value: on ? [id: geo.frame(in: .global)] : [:])
            }
        )
    }

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

// MARK: - Seeded variation (CELLS558 S2)

/// Seed-driven content and style choices. Low-variation families use it so that each seed draws a different screen.
struct Variation {
    private var rng: SeededRNG
    init(seed: UInt64, salt: UInt64) { rng = SeededRNG(seed: seed ^ salt) }
    mutating func int(_ range: ClosedRange<Int>) -> Int { range.lowerBound + Int(rng.next() % UInt64(range.count)) }
    mutating func chance(_ p: Double) -> Bool { Double(rng.next() % 10_000) / 10_000.0 < p }
    mutating func pick<T>(_ items: [T]) -> T { items[Int(rng.next() % UInt64(items.count))] }
    mutating func sample<T>(_ items: [T], _ n: Int) -> [T] {
        var pool = items, out: [T] = []
        for _ in 0..<min(n, items.count) { out.append(pool.remove(at: Int(rng.next() % UInt64(pool.count)))) }
        return out
    }

    static let tabWords = ["Home", "Movies", "Shows", "Sports", "Kids", "News", "Live", "Music", "Library", "Search",
                           "For You", "Store", "Channels", "Watch Now", "Explore", "Downloads", "Favorites", "Top Charts",
                           "Comedy", "Drama", "Docs", "Family", "Local", "World", "Business", "Science", "Health", "Gaming"]
    static let headlines = ["Featured Collection", "Continue Watching", "New This Week", "Top Picks", "Trending Now",
                            "Recently Added", "Because You Watched", "Staff Favorites", "Editors' Choice", "Coming Soon"]
    static let menuItems: [(String, String)] = [("Search", "magnifyingglass"), ("Home", "house.fill"), ("Movies", "film.fill"),
        ("TV Shows", "tv.fill"), ("Sports", "sportscourt.fill"), ("Library", "square.stack.3d.up.fill"), ("Music", "music.note"),
        ("Kids", "figure.child"), ("News", "newspaper.fill"), ("Settings", "gearshape.fill"), ("Downloads", "arrow.down.circle.fill")]
    static let languages = ["English [CC]", "Spanish", "French", "German", "Italian", "Japanese", "Portuguese", "Korean", "Off"]
    static let settingValues = ["On", "Off", "Automatic", "4K SDR (60Hz)", "1080p", "Dolby Atmos", "Never", "15 Minutes", "English"]
    static let alertButtons = ["Not Now", "Learn More", "Settings", "Try Again", "Details"]
}

/// Light or dark colors for the varied templates. tvOS shows focus as a raised white surface in both themes.
struct Palette {
    let background, surface, selected, text, secondary: Color
    static func make(light: Bool) -> Palette {
        light ? Palette(background: Color(white: 0.90), surface: Color.black.opacity(0.06), selected: Color.black.opacity(0.14),
                        text: Color(white: 0.08), secondary: Color(white: 0.30))
              : Palette(background: Color(red: 0.05, green: 0.05, blue: 0.08), surface: Color.white.opacity(0.08),
                        selected: Color.white.opacity(0.18), text: .white, secondary: Color.white.opacity(0.65))
    }
}

/// Class of a top tab item. Pending maintainer decision (CELLS558): `primaryButton` (current generator) or `secondaryButton` (TTR Fixture).
let tabItemClass = "primaryButton"

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

                            Text(app.title)
                                .font(.system(size: 20, weight: app.isFocused ? .bold : .medium))
                                .foregroundColor(app.isFocused ? .white : .white.opacity(0.7))
                                .frame(width: 308)
                                .captureFrame(id: "label_app_\(idx)")
                        }
                        // Whole-cell box: artwork plus title (Research 5.2.1).
                        .captureFrame(id: app.isFocused ? "collectionItem_app_\(idx)_focused" : "collectionItem_app_\(idx)_unfocused")
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
        var v = Variation(seed: seed, salt: 0x5E77)
        let categories = v.sample(["General", "Users and Accounts", "Video and Audio", "Remotes and Devices", "Network",
                                   "System", "Apps", "AirPlay and HomeKit", "Accessibility", "Privacy and Security"], v.int(4...8))
        let focusIdx = v.int(0...(categories.count - 1))
        let rows = v.sample(["Wi-Fi", "Bluetooth", "Audio Output", "Subtitles and Captioning", "Siri", "Software Updates",
                             "Sleep After", "Screensaver", "Language", "Resolution", "Match Content", "Reduce Loud Sounds"], v.int(3...6))
        let toggles = rows.map { _ in v.chance(0.5) }
        let values = rows.map { _ in v.pick(Variation.settingValues) }
        let p = Palette.make(light: v.chance(0.3))

        ZStack(alignment: .topLeading) {
            p.background.ignoresSafeArea()

            VStack(alignment: .leading, spacing: 20) {
                Text("Settings")
                    .font(.system(size: 44, weight: .bold))
                    .foregroundColor(p.text)
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
                                    .foregroundColor(isFoc ? .black : p.text)
                                    .captureFrame(id: "label_cat_\(idx)")
                                Spacer()
                                Image(systemName: "chevron.right")
                                    .foregroundColor(isFoc ? .black.opacity(0.6) : p.secondary)
                            }
                            .padding(.horizontal, 28)
                            .frame(width: 580, height: 74)
                            .background(isFoc ? Color.white : p.surface)
                            .cornerRadius(16)
                            .shadow(color: isFoc ? Color.black.opacity(0.3) : Color.clear, radius: 10)
                            .captureFrame(id: isFoc ? "listRow_cat_\(idx)_focused" : "listRow_cat_\(idx)_unfocused")
                        }
                    }

                    VStack(spacing: 14) {
                        ForEach(0..<rows.count, id: \.self) { idx in
                            HStack {
                                Text(rows[idx])
                                    .font(.system(size: 26))
                                    .foregroundColor(p.text)
                                    .captureFrame(id: "label_opt_\(idx)")
                                Spacer()
                                if toggles[idx] {
                                    Toggle("", isOn: .constant(idx % 2 == 0))
                                        .labelsHidden()
                                        .captureFrame(id: "toggle_setting_\(idx)")
                                } else {
                                    Text(values[idx])
                                        .font(.system(size: 24))
                                        .foregroundColor(p.secondary)
                                        .captureFrame(id: "label_value_\(idx)")
                                }
                            }
                            .padding(.horizontal, 28)
                            .frame(width: 980, height: 78)
                            .background(p.surface)
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
        var v = Variation(seed: seed, salt: 0xA1E7)
        var c = ContentCorpus(seed: seed ^ 0xA1E8)
        let title = c.alertTitle()
        let message = c.alertMessage()
        let primary = v.pick(["Continue", "OK", "Update Now", "Allow", "Sign In", "Connect"])
        let extra = v.chance(0.5) ? v.pick(Variation.alertButtons) : nil
        let count = extra == nil ? 2 : 3
        let focusBtn = v.int(0...(count - 1)) // 0 primary, last cancel, middle extra
        let light = v.chance(0.3)
        let p = Palette.make(light: light)
        let width = CGFloat(v.int(640...860))
        let dialog = light ? Color(white: 0.97) : Color(red: 0.16, green: 0.16, blue: 0.20)

        ZStack {
            (light ? Color.black.opacity(0.35) : Color.black.opacity(0.85)).ignoresSafeArea()

            VStack(spacing: 28) {
                VStack(spacing: 12) {
                    Text(title)
                        .font(.system(size: 34, weight: .bold))
                        .foregroundColor(p.text)
                        .captureFrame(id: "label_alert_title")
                    Text(message)
                        .font(.system(size: 22))
                        .foregroundColor(p.secondary)
                        .padding(.horizontal, 32)
                        .multilineTextAlignment(.center)
                        .captureFrame(id: "label_alert_message")
                }
                .padding(.top, 40)

                VStack(spacing: 16) {
                    ForEach(0..<count, id: \.self) { idx in
                        let isFoc = (idx == focusBtn)
                        let isCancel = (idx == count - 1)
                        let kind = idx == 0 ? "primaryButton_action" : (isCancel ? "cancelAction_dismiss" : "secondaryButton_extra")
                        Text(idx == 0 ? primary : (isCancel ? "Cancel" : (extra ?? "")))
                            .font(.system(size: 24, weight: isFoc ? .bold : .medium))
                            .foregroundColor(isFoc ? .black : p.text)
                            .frame(width: width - 100, height: 68)
                            .background(isFoc ? Color.white : p.surface)
                            .cornerRadius(16)
                            .shadow(color: isFoc ? Color.black.opacity(0.3) : Color.clear, radius: 10)
                            .captureFrame(id: isFoc ? "\(kind)_focused" : "\(kind)_unfocused")
                    }
                }
                .padding(.bottom, 36)
            }
            .frame(width: width)
            .background(dialog)
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
        var v = Variation(seed: seed, salt: 0x7AB0)
        let tabs = v.sample(Variation.tabWords, v.int(3...8))
        let focIdx = v.int(0...(tabs.count - 1))
        // Selected but not focused looks like focus. Keep it in at least 30% of screens as a hard negative.
        let selIdx = v.chance(0.45) ? v.int(0...(tabs.count - 1)) : focIdx
        let style = v.int(0...2) // 0 filled pill, 1 underline, 2 raised text
        let p = Palette.make(light: v.chance(0.3))
        let fontSize = CGFloat(v.int(21...28))
        let topPad = CGFloat(v.int(10...40))
        let headline = v.pick(Variation.headlines)

        ZStack(alignment: .top) {
            p.background.ignoresSafeArea()

            VStack(spacing: 0) {
                TabRow(tabs: tabs, focIdx: focIdx, selIdx: selIdx, style: style, fontSize: fontSize,
                       spacing: CGFloat(v.int(4...30)), padH: CGFloat(v.int(18...32)), padV: CGFloat(v.int(8...14)), p: p, row: 0,
                       platter: TabRow.plainFocus(seed: seed, row: 0).platter, lift: TabRow.plainFocus(seed: seed, row: 0).lift)
                    .frame(maxWidth: .infinity, alignment: v.chance(0.5) ? .leading : .center)
                    .padding(.horizontal, 90)
                .frame(maxWidth: .infinity)
                .frame(height: 110)
                .background(p.surface)
                .captureFrame(id: "tabBar_top_navigation")
                .padding(.top, topPad)

                VStack(alignment: .leading, spacing: 20) {
                    Text(headline)
                        .font(.system(size: 48, weight: .heavy))
                        .foregroundColor(p.text)
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
                // Whole-cell box: poster plus title (Research 5.2.1).
                .captureFrame(id: "collectionItem_target_poster_unfocused")

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
        var v = Variation(seed: seed, salt: 0x51DE)
        let items = v.sample(Array(Variation.menuItems.dropFirst()), v.int(4...7))
        let selectedNav = v.int(0...(items.count - 1))
        let focusNav: Int? = v.chance(0.5) ? (v.chance(0.6) ? selectedNav : v.int(0...(items.count - 1))) : nil
        let cardCount = v.int(2...4)
        let cardHeight = CGFloat(v.int(300...580))
        let p = Palette.make(light: v.chance(0.3))

        ZStack(alignment: .topLeading) {
            p.background.ignoresSafeArea()

            HStack(spacing: 0) {
                // Left Navigation Sidebar
                VStack(alignment: .leading, spacing: 14) {
                    HStack(spacing: 16) {
                        Image(systemName: "magnifyingglass").foregroundColor(p.secondary)
                        Text("Search").font(.system(size: 24)).foregroundColor(p.secondary)
                        Spacer()
                    }
                    .padding(.horizontal, 20)
                    .frame(width: 380, height: 60)
                    .background(p.surface)
                    .cornerRadius(16)
                    .captureFrame(id: "searchField_nav_search")
                    .padding(.bottom, 12)

                    ForEach(Array(items.enumerated()), id: \.offset) { idx, item in
                        let isFoc = (focusNav == idx)
                        let isSel = (idx == selectedNav)

                        HStack(spacing: 18) {
                            Image(systemName: item.1)
                                .font(.system(size: 22))
                                .foregroundColor(isFoc ? .black : (isSel ? p.text : p.secondary))
                                .frame(width: 28)
                                .captureFrame(id: "imageView_nav_icon_\(idx)")
                            Text(item.0)
                                .font(.system(size: 24, weight: (isFoc || isSel) ? .bold : .medium))
                                .foregroundColor(isFoc ? .black : p.text)
                                .captureFrame(id: "label_nav_title_\(idx)")
                            Spacer()
                        }
                        .padding(.horizontal, 20)
                        .frame(width: 380, height: 64)
                        .background(isFoc ? Color.white : (isSel ? p.selected : Color.clear))
                        .cornerRadius(16)
                        .scaleEffect(isFoc ? 1.04 : 1.0)
                        .shadow(color: isFoc ? Color.black.opacity(0.35) : Color.clear, radius: 12)
                        .captureFrame(id: isFoc ? "listRow_nav_\(idx)_focused" : "listRow_nav_\(idx)_unfocused")
                    }

                    Spacer()
                }
                .padding(32)
                .frame(width: 440, height: 1080)
                .background(p.surface)
                .captureFrame(id: "sidebar_main_nav")

                // Right Content Pane
                VStack(alignment: .leading, spacing: 24) {
                    Text(items[selectedNav].0)
                        .font(.system(size: 44, weight: .bold))
                        .foregroundColor(p.text)
                        .captureFrame(id: "label_section_header")

                    HStack(spacing: 36) {
                        ForEach(0..<cardCount, id: \.self) { cIdx in
                            let isCardFoc = (focusNav == nil && cIdx == 0)
                            VStack(alignment: .leading, spacing: 12) {
                                RoundedRectangle(cornerRadius: 18)
                                    .fill(Color(hue: Double((Int(seed) + cIdx * 7) % 20) / 20.0, saturation: 0.5, brightness: 0.55))
                                    .frame(width: 1240 / CGFloat(cardCount) - 36, height: cardHeight)
                                    .scaleEffect(isCardFoc ? 1.08 : 1.0)
                                    .overlay(RoundedRectangle(cornerRadius: 18).stroke(isCardFoc ? Color.white : Color.clear, lineWidth: 3))
                                    .shadow(color: isCardFoc ? Color.white.opacity(0.4) : Color.clear, radius: 16)

                                Text("\(items[selectedNav].0) Title \(cIdx + 1)")
                                    .font(.system(size: 22, weight: isCardFoc ? .bold : .medium))
                                    .foregroundColor(p.text)
                                    .captureFrame(id: "label_card_\(cIdx)")
                            }
                            // Whole-cell box: artwork plus title (Research 5.2.1).
                            .captureFrame(id: isCardFoc ? "collectionItem_card_\(cIdx)_focused" : "collectionItem_card_\(cIdx)_unfocused")
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

                                Text("Show Episode \(idx + 1)")
                                    .font(.system(size: 20, weight: isFoc ? .bold : .medium))
                                    .foregroundColor(isFoc ? .white : .white.opacity(0.7))
                                    .captureFrame(id: "label_shelf_card_\(idx)")
                            }
                            // Whole-cell box: artwork plus title (Research 5.2.1).
                            .captureFrame(id: isFoc ? "collectionItem_shelf_\(idx)_focused" : "collectionItem_shelf_\(idx)_unfocused")
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
        var v = Variation(seed: seed, salt: 0x5B11)
        let focRow = v.int(0...4) // 4: focus stays in the category list
        let cats = v.sample(["Video and Audio", "General", "Remotes", "Network", "Users", "Apps", "AirPlay", "Accessibility", "System"], v.int(4...7))
        let resolution = v.pick(["4K SDR (60Hz)", "4K HDR (60Hz)", "1080p SDR (60Hz)", "Automatic"])
        let delay = "\(v.int(0...12) * 10) ms"
        let format = v.chance(0.5)

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
                    Text(cats[0]).font(.system(size: 34, weight: .bold)).foregroundColor(.white)
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
                            Text(resolution).foregroundColor(focRow == 0 ? .black.opacity(0.7) : .white.opacity(0.6))
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
                            Toggle("", isOn: .constant(format)).labelsHidden()
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
                                Text(delay).font(.system(size: 22, weight: .bold))
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
        var v = Variation(seed: seed, salt: 0xA0D1)
        let langs = v.sample(Variation.languages, v.int(2...5))
        let checked = v.int(0...(langs.count - 1))
        let foc = v.int(0...(langs.count + 1)) // 0 segment, 1...n languages, n+1 dialogue toggle
        let segFirst = v.pick(["Subtitles", "Audio"])
        let segSecond = segFirst == "Audio" ? "Subtitles" : "Audio"
        let light = v.chance(0.25)
        let p = Palette.make(light: light)
        let card = light ? Color(white: 0.97) : Color(red: 0.14, green: 0.14, blue: 0.18)

        ZStack {
            (light ? Color.black.opacity(0.3) : Color.black.opacity(0.82)).ignoresSafeArea()

            VStack(spacing: 24) {
                // Segmented Selector
                let isSegFoc = (foc == 0)
                HStack(spacing: 0) {
                    Text(segFirst).font(.system(size: 22, weight: .bold)).foregroundColor(.black)
                        .frame(maxWidth: .infinity).frame(height: 52).background(Color.white).cornerRadius(12)
                    Text(segSecond).font(.system(size: 22)).foregroundColor(p.secondary)
                        .frame(maxWidth: .infinity).frame(height: 52)
                }
                .padding(4).frame(width: 640).background(isSegFoc ? Color.white : p.surface).cornerRadius(16)
                .captureFrame(id: isSegFoc ? "segmentedControl_tabs_focused" : "segmentedControl_tabs_unfocused")

                // Language Rows
                VStack(spacing: 8) {
                    ForEach(0..<langs.count, id: \.self) { idx in
                        let isFoc = (foc == idx + 1)
                        HStack {
                            Text(langs[idx]).font(.system(size: 22, weight: isFoc ? .bold : .medium))
                                .foregroundColor(isFoc ? .black : p.text)
                                .captureFrame(id: "label_lang_\(idx)")
                            Spacer()
                            if idx == checked {
                                Image(systemName: "checkmark").foregroundColor(isFoc ? .black : p.text)
                                    .captureFrame(id: "imageView_checkmark_\(idx)")
                            }
                        }
                        .padding(.horizontal, 24).frame(width: 640, height: 60)
                        .background(isFoc ? Color.white : (idx == checked ? p.selected : p.surface)).cornerRadius(14)
                        .captureFrame(id: isFoc ? "listRow_lang_\(idx)_focused" : "listRow_lang_\(idx)_unfocused")
                    }
                }

                // Dialogue Boost Toggle
                let isDiagFoc = (foc == langs.count + 1)
                HStack {
                    Text(v.pick(["Enhance Dialogue", "Reduce Loud Sounds", "Mono Audio"])).font(.system(size: 20, weight: isDiagFoc ? .bold : .medium))
                        .foregroundColor(isDiagFoc ? .black : p.text)
                        .captureFrame(id: "label_dialogue_title")
                    Spacer()
                    Toggle("", isOn: .constant(v.chance(0.5))).labelsHidden()
                        .captureFrame(id: isDiagFoc ? "toggle_enhance_dialogue_focused" : "toggle_enhance_dialogue_unfocused")
                }
                .padding(.horizontal, 24).frame(width: 640, height: 60)
                .background(isDiagFoc ? Color.white : p.surface).cornerRadius(14)
                .captureFrame(id: isDiagFoc ? "listRow_dialogue_focused" : "listRow_dialogue_unfocused")
            }
            .padding(32).background(card).cornerRadius(28)
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
                            Text("Person \(idx + 1)").font(.system(size: 16)).foregroundColor(.white.opacity(0.85))
                                .captureFrame(id: "label_part_\(idx)")
                        }
                        // Whole-cell box: avatar plus name (Research 5.2.1).
                        .captureFrame(id: "collectionItem_avatar_\(idx)_unfocused")
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

// MARK: - Template 26: Content Cells (CELLS558 S3)

/// One row of cells. Variants: 0 poster, 1 article, 2 overlay title, 3 text panel, 4 hero with button, 5 scrolled shelf.
struct CellRowSpec {
    let variant: Int, count: Int, width: CGFloat, artHeight: CGFloat, offset: CGFloat, height: CGFloat
    let heading: String, titles: [String], summaries: [String], metas: [String], hues: [Double]

    static let adjectives = ["Hidden", "Last", "Silent", "Bright", "Northern", "Golden", "Lost", "Wild", "Final", "Secret", "Open", "Distant"]
    static let nouns = ["Harbor", "Signal", "Summit", "River", "Garden", "Station", "Island", "Road", "Archive", "Season", "Circuit", "Valley"]
    static let phrases = ["A new look at an old question.", "Experts weigh the next steps.", "What changes this week and why.",
                          "Behind the scenes of a long project.", "Five things to know before you start.", "The story so far, in brief.",
                          "Results arrive after months of work.", "A guide for first-time viewers.", "Plans move ahead despite delays."]

    static func rows(seed: UInt64) -> (rows: [CellRowSpec], focusRow: Int, focusCell: Int, light: Bool) {
        var v = Variation(seed: seed, salt: 0xCE11)
        let light = v.chance(0.3)
        var rows: [CellRowSpec] = []
        var y: CGFloat = 130
        for _ in 0..<v.int(1...3) {
            let variant = v.int(0...5)
            let count = variant == 4 ? v.int(1...2) : v.int(2...6)
            let spacing: CGFloat = 40
            let shown = variant == 5 ? CGFloat(count) - 0.6 : CGFloat(count)
            let width = (1760 - spacing * (shown - 1)) / shown
            let aspect: CGFloat = variant == 0 ? CGFloat(v.int(130...150)) / 100 : CGFloat(v.int(50...62)) / 100
            let artHeight = min(variant == 3 ? 0 : width * aspect, 420)
            let lines: CGFloat = variant == 0 ? 2 : (variant == 1 || variant == 3 || variant == 5 ? 6 : 1)
            let height = artHeight + lines * 30 + (variant == 4 ? 80 : 20) + 50
            if y + height > 1040 { break }
            y += height + 30
            func title() -> String { "\(v.pick(adjectives)) \(v.pick(nouns))" + (v.chance(0.4) ? " \(v.pick(nouns))" : "") }
            rows.append(CellRowSpec(variant: variant, count: count, width: width, artHeight: artHeight,
                                    offset: variant == 5 ? -width * 0.3 : 0, height: height, heading: v.pick(Variation.headlines),
                                    titles: (0..<count).map { _ in title() },
                                    summaries: (0..<count).map { _ in v.pick(phrases) + (v.chance(0.5) ? " " + v.pick(phrases) : "") },
                                    metas: (0..<count).map { _ in "\(v.int(1...59)) min · \(v.pick(["Live", "New", "Season \(v.int(1...6))", "Updated", "4K"]))" },
                                    hues: (0..<count).map { _ in Double(v.int(0...99)) / 100 }))
        }
        if rows.isEmpty {
            rows.append(CellRowSpec(variant: 0, count: 4, width: 410, artHeight: 420, offset: 0, height: 530, heading: "Top Picks",
                                    titles: ["Open Road", "Last Signal", "Wild Garden", "Silent River"], summaries: ["", "", "", ""],
                                    metas: ["", "", "", ""], hues: [0.1, 0.3, 0.5, 0.7]))
        }
        let focusRow = v.int(0...(rows.count - 1))
        return (rows, focusRow, v.int(0...(rows[focusRow].count - 1)), light)
    }
}

struct ContentCellsView: View {
    let seed: UInt64

    var body: some View {
        let spec = CellRowSpec.rows(seed: seed)
        let p = Palette.make(light: spec.light)

        ZStack(alignment: .topLeading) {
            p.background.ignoresSafeArea()

            VStack(alignment: .leading, spacing: 30) {
                ForEach(0..<spec.rows.count, id: \.self) { r in
                    let row = spec.rows[r]
                    VStack(alignment: .leading, spacing: 14) {
                        Text(row.heading).font(.system(size: 30, weight: .bold)).foregroundColor(p.text)
                            .captureFrame(id: "label_row_\(r)")
                        HStack(alignment: .top, spacing: 40) {
                            ForEach(0..<row.count, id: \.self) { i in
                                let isFoc = (r == spec.focusRow && i == spec.focusCell)
                                cell(row: row, r: r, i: i, isFoc: isFoc, p: p)
                            }
                        }
                        .offset(x: row.offset)
                    }
                }
            }
            .padding(.horizontal, 80)
            .padding(.top, 60)
        }
        .frame(width: 1920, height: 1080)
        .clipped()
        .ignoresSafeArea(.all)
    }

    /// A focused cell lifts by 1.06. Its boxes are captured on an invisible unscaled copy, so they stay the frame (§5.2.1, PILLS560 R6).
    func cell(row: CellRowSpec, r: Int, i: Int, isFoc: Bool, p: Palette) -> some View {
        cellBody(row: row, r: r, i: i, isFoc: isFoc, p: p, capture: !isFoc)
            .scaleEffect(isFoc ? 1.06 : 1.0)
            .shadow(color: isFoc ? Color.white.opacity(0.45) : Color.clear, radius: isFoc ? 18 : 0)
            .overlay {
                if isFoc { cellBody(row: row, r: r, i: i, isFoc: isFoc, p: p, capture: true).opacity(0) }
            }
    }

    @ViewBuilder
    func cellBody(row: CellRowSpec, r: Int, i: Int, isFoc: Bool, p: Palette, capture: Bool) -> some View {
        let art = Color(hue: row.hues[i], saturation: 0.55, brightness: spec_brightness(p))
        let titleColor = (isFoc && row.variant == 3) ? Color.black : p.text
        VStack(alignment: .leading, spacing: 8) {
            if row.variant != 3 {
                ZStack(alignment: .bottomLeading) {
                    RoundedRectangle(cornerRadius: 14).fill(art)
                    if row.variant == 2 {
                        LinearGradient(colors: [.clear, Color.black.opacity(0.7)], startPoint: .center, endPoint: .bottom)
                            .clipShape(RoundedRectangle(cornerRadius: 14))
                        Text(row.titles[i]).font(.system(size: 26, weight: .bold)).foregroundColor(.white).padding(16)
                            .captureFrame(id: "label_cell_title_\(r)_\(i)", if: capture)
                    }
                    if row.variant == 4 {
                        Text("Play").font(.system(size: 22, weight: .bold)).foregroundColor(.black)
                            .padding(.horizontal, 30).padding(.vertical, 12).background(Color.white).cornerRadius(12).padding(20)
                            .captureFrame(id: isFoc ? "primaryButton_cell_play_\(r)_\(i)_focused" : "primaryButton_cell_play_\(r)_\(i)_unfocused", if: capture)
                    }
                }
                .frame(width: row.width, height: row.artHeight)
            }
            if row.variant != 2 {
                Text(row.titles[i]).font(.system(size: row.variant == 0 ? 22 : 26, weight: .semibold)).foregroundColor(titleColor)
                    .lineLimit(2).frame(width: row.width - (row.variant == 3 ? 40 : 0), alignment: .leading)
                    .captureFrame(id: "label_cell_title_\(r)_\(i)", if: capture)
            }
            if row.variant == 1 || row.variant == 3 || row.variant == 5 {
                Text(row.summaries[i]).font(.system(size: 20)).foregroundColor(isFoc && row.variant == 3 ? Color.black.opacity(0.75) : p.secondary)
                    .lineLimit(3).frame(width: row.width - (row.variant == 3 ? 40 : 0), alignment: .leading)
                    .captureFrame(id: "label_cell_summary_\(r)_\(i)", if: capture)
                Text(row.metas[i]).font(.system(size: 18)).foregroundColor(isFoc && row.variant == 3 ? Color.black.opacity(0.6) : p.secondary)
                    .captureFrame(id: "label_cell_meta_\(r)_\(i)", if: capture)
            }
        }
        .padding(row.variant == 3 ? 20 : 0)
        .background(row.variant == 3 ? (isFoc ? Color.white : p.surface) : Color.clear)
        .cornerRadius(row.variant == 3 ? 16 : 0)
        // Whole-cell box: artwork and all text inside the cell (Research 5.2.1). No nested imageView for the artwork.
        .captureFrame(id: isFoc ? "collectionItem_cell_\(r)_\(i)_focused" : "collectionItem_cell_\(r)_\(i)_unfocused", if: capture)
    }

    func spec_brightness(_ p: Palette) -> Double { 0.55 }
}

// PILLS560: 1 tab row. Pill box = the padded pill (underline excluded); the tab text keeps a nested `label` box (Research 5.2.1).
struct TabRow: View {
    let tabs: [String], focIdx: Int, selIdx: Int, style: Int, fontSize: CGFloat, spacing: CGFloat, padH: CGFloat, padV: CGFloat
    let p: Palette, row: Int
    // PILLS560 R5: tvOS `.buttonStyle(.plain)` focus. The system platter extends `platter` beyond the button frame, and the box stays the frame (§5.2.1).
    var platter: CGSize = .zero
    var lift: CGFloat = 1.0

    var body: some View {
        HStack(spacing: spacing) {
            ForEach(0..<tabs.count, id: \.self) { idx in
                let isFoc = (idx == focIdx)
                let isSel = (idx == selIdx) && !isFoc
                let plain = isFoc && platter != .zero
                // Style 2 lifts the focused tab by 1.1. Capture its boxes outside the scale, so they stay the frame (§5.2.1).
                let scaled = isFoc && style == 2 && !plain
                let buttonID = isFoc ? "\(tabItemClass)_tab_\(row)_\(idx)_focused" : "\(tabItemClass)_tab_\(row)_\(idx)_unfocused"
                let font = Font.system(size: fontSize, weight: isFoc || isSel ? .bold : .medium)
                Text(tabs[idx])
                    .font(font)
                    .foregroundColor(isFoc && (style == 0 || plain) ? .black : (isFoc || isSel ? p.text : p.secondary))
                    .captureFrame(id: "label_tab_\(row)_\(idx)", if: !scaled)
                    .padding(.horizontal, padH)
                    .padding(.vertical, padV)
                    .background(isFoc && style == 0 && !plain ? Color.white : (isSel ? p.selected : Color.clear))
                    .cornerRadius(22)
                    .overlay(alignment: .bottom) {
                        Rectangle().fill(isFoc && style == 1 && !plain ? p.text : Color.clear).frame(height: 3).padding(.horizontal, padH).offset(y: 6)
                    }
                    .background {
                        if plain {
                            RoundedRectangle(cornerRadius: 22 + platter.height).fill(Color.white)
                                .padding(.horizontal, -platter.width).padding(.vertical, -platter.height)
                        }
                    }
                    .captureFrame(id: buttonID, if: !scaled)
                    .scaleEffect(plain ? lift : (scaled ? 1.1 : 1.0))
                    .shadow(color: isFoc && (style != 1 || plain) ? Color.black.opacity(0.35) : Color.clear, radius: 10)
                    .captureFrame(id: buttonID, if: scaled)
                    .overlay {
                        if scaled {
                            Text(tabs[idx]).font(font).captureFrame(id: "label_tab_\(row)_\(idx)")
                                .padding(.horizontal, padH).padding(.vertical, padV).opacity(0)
                        }
                    }
            }
        }
    }

    /// Half of focused rows use the `.plain` platter. A separate salt keeps every other random draw unchanged.
    static func plainFocus(seed: UInt64, row: Int) -> (platter: CGSize, lift: CGFloat) {
        var f = Variation(seed: seed, salt: 0xF0C5 &+ UInt64(row))
        guard f.chance(0.5) else { return (.zero, 1.0) }
        // No lift: `captureFrame` reads the frame after `scaleEffect`, so a scale would also scale the label.
        return (CGSize(width: CGFloat(f.int(14...32)), height: CGFloat(f.int(12...18))), 1.0)
    }
}

// PILLS560: 1–2 tab rows above 1 content shelf. Most screens focus a cell or a tab; unfocused rows are plain text.
struct TabRowsView: View {
    let seed: UInt64

    var body: some View {
        var v = Variation(seed: seed, salt: 0x7AB5)
        let spec = CellRowSpec.rows(seed: seed)
        let shelf = spec.rows[0]
        let p = Palette.make(light: v.chance(0.3))
        let rows = v.chance(0.6) ? 2 : 1
        let where_ = v.int(0...9) // 0–2 row 1 tab, 3–5 row 2 tab, else a cell
        let focusRow = where_ < 3 ? 0 : (where_ < 6 && rows == 2 ? 1 : -1)
        let lead = v.chance(0.7)
        let tabs = (0..<rows).map { r in v.sample(Variation.tabWords, v.int(r == 0 ? 3...7 : 4...9)) }
        let sel = tabs.map { v.int(0...($0.count - 1)) }
        let foc = (0..<rows).map { r in r == focusRow ? v.int(0...(tabs[r].count - 1)) : -1 }
        let styles = (0..<rows).map { _ in v.chance(0.75) ? 0 : v.int(1...2) }
        let sizes = (0..<rows).map { r in CGFloat(r == 0 ? v.int(24...30) : v.int(20...26)) }
        let spacing = (0..<rows).map { _ in CGFloat(v.int(4...30)) }
        let padH = (0..<rows).map { _ in CGFloat(v.int(18...32)) }
        let padV = (0..<rows).map { _ in CGFloat(v.int(8...14)) }
        let top = CGFloat(v.int(30...110))
        let focusCell = focusRow < 0 ? v.int(0...(shelf.count - 1)) : -1

        ZStack(alignment: .topLeading) {
            p.background.ignoresSafeArea()
            VStack(alignment: .leading, spacing: CGFloat(v.int(14...40))) {
                ForEach(0..<rows, id: \.self) { r in
                    TabRow(tabs: tabs[r], focIdx: foc[r], selIdx: sel[r], style: styles[r], fontSize: sizes[r],
                           spacing: spacing[r], padH: padH[r], padV: padV[r], p: p, row: r,
                           platter: TabRow.plainFocus(seed: seed, row: r).platter, lift: TabRow.plainFocus(seed: seed, row: r).lift)
                        .frame(maxWidth: .infinity, alignment: lead ? .leading : .center)
                }
                HStack(alignment: .top, spacing: 40) {
                    ForEach(0..<shelf.count, id: \.self) { i in
                        ContentCellsView(seed: seed).cell(row: shelf, r: 0, i: i, isFoc: i == focusCell, p: p)
                    }
                }
                .offset(x: shelf.offset)
                .padding(.top, 20)
            }
            .padding(.horizontal, 80)
            .padding(.top, top)
        }
        .frame(width: 1920, height: 1080)
        .clipped()
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

// MARK: - Template 16: App Switcher Multitasking Carousel

struct AppSwitcherView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let appData: [(title: String, icon: String)] = [
            ("TV", "play.tv.fill"),
            ("Photos", "photo.on.rectangle.angled"),
            ("Music", "music.note"),
            ("Fitness", "flame.fill"),
            ("Settings", "gearshape.fill"),
            ("Arcade", "gamecontroller.fill")
        ]
        let count = 4
        let startIdx = Int(rng.next() % UInt64(appData.count - count + 1))
        let foc = Int(rng.next() % UInt64(count))
        let showCloseHint = (rng.next() % 2 == 0)

        ZStack {
            Color(red: 0.06, green: 0.06, blue: 0.09).ignoresSafeArea()

            VStack(spacing: 40) {
                Spacer()
                HStack(spacing: 50) {
                    ForEach(0..<count, id: \.self) { idx in
                        let item = appData[(startIdx + idx) % appData.count]
                        let isFoc = (idx == foc)
                        let hue = Double((rng.next() &+ UInt64(idx * 173)) % 1000) / 1000.0

                        VStack(spacing: 20) {
                            ZStack {
                                RoundedRectangle(cornerRadius: 24)
                                    .fill(LinearGradient(
                                        colors: [Color(hue: hue, saturation: 0.6, brightness: 0.35), Color.black.opacity(0.85)],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    ))
                                Image(systemName: item.icon)
                                    .font(.system(size: 80))
                                    .foregroundColor(.white.opacity(0.85))
                                    .captureFrame(id: "imageView_app_preview_\(idx)")
                            }
                            .frame(width: isFoc ? 520 : 420, height: isFoc ? 330 : 270)
                            .overlay(
                                RoundedRectangle(cornerRadius: 24)
                                    .stroke(isFoc ? Color.white : Color.white.opacity(0.15), lineWidth: isFoc ? 5 : 1)
                            )
                            .shadow(color: isFoc ? Color.white.opacity(0.35) : Color.black.opacity(0.6), radius: isFoc ? 30 : 12)

                            HStack(spacing: 14) {
                                ZStack {
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(Color.white.opacity(0.2))
                                    Image(systemName: item.icon)
                                        .font(.system(size: 18))
                                        .foregroundColor(.white)
                                }
                                .frame(width: 36, height: 36)
                                .captureFrame(id: "imageView_app_icon_\(idx)")

                                Text(item.title)
                                    .font(.system(size: 26, weight: isFoc ? .bold : .medium))
                                    .foregroundColor(isFoc ? .white : .white.opacity(0.7))
                                    .captureFrame(id: "label_app_title_\(idx)")
                            }
                        }
                        // Whole-cell box: preview plus icon and title (Research 5.2.1).
                        .captureFrame(id: isFoc ? "collectionItem_app_card_\(idx)_focused" : "collectionItem_app_card_\(idx)_unfocused")
                        .scaleEffect(isFoc ? 1.05 : 0.95)
                    }
                }
                Spacer()

                if showCloseHint {
                    HStack(spacing: 12) {
                        Image(systemName: "chevron.up")
                            .font(.system(size: 20, weight: .bold))
                            .foregroundColor(.white.opacity(0.6))
                        Text("Swipe up on the clickpad to close")
                            .font(.system(size: 22, weight: .medium))
                            .foregroundColor(.white.opacity(0.6))
                    }
                    .padding(.bottom, 40)
                    .captureFrame(id: "label_close_hint")
                }
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 17: PIN & AirPlay Passcode Entry

struct PINEntryView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let prompts = [
            ("AirPlay Passcode", "Enter the passcode displayed on your Apple TV to connect."),
            ("Enter Restrictions Passcode", "Enter the 4-digit passcode to access restricted content."),
            ("Purchase Passcode", "Enter your passcode to authorize this purchase."),
            ("Conference Room PIN", "Enter the PIN displayed on the conference room display.")
        ]
        let p = prompts[Int(rng.next() % UInt64(prompts.count))]
        let length = (rng.next() % 2 == 0) ? 4 : 6
        let filled = Int(rng.next() % UInt64(length))
        let foc = Int(rng.next() % 11) // 0..9 digits, 10 cancel

        ZStack {
            Color.black.opacity(0.85).ignoresSafeArea()

            VStack(spacing: 36) {
                VStack(spacing: 12) {
                    Text(p.0)
                        .font(.system(size: 40, weight: .bold))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_pin_title")

                    Text(p.1)
                        .font(.system(size: 24))
                        .foregroundColor(.white.opacity(0.7))
                        .captureFrame(id: "label_pin_subtitle")
                }

                HStack(spacing: 24) {
                    ForEach(0..<length, id: \.self) { idx in
                        let isFilled = idx < filled
                        ZStack {
                            RoundedRectangle(cornerRadius: 16)
                                .fill(Color.white.opacity(0.12))
                                .frame(width: 64, height: 74)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 16)
                                        .stroke(Color.white.opacity(0.3), lineWidth: 2)
                                )

                            if isFilled {
                                Circle()
                                    .fill(Color.white)
                                    .frame(width: 20, height: 20)
                            }
                        }
                        .captureFrame(id: "secureField_pin_slot_\(idx)")
                    }
                }
                .padding(.vertical, 10)

                VStack(spacing: 16) {
                    ForEach(0..<3) { row in
                        HStack(spacing: 20) {
                            ForEach(0..<3) { col in
                                let digit = row * 3 + col + 1
                                let isFoc = (foc == digit)
                                Text("\(digit)")
                                    .font(.system(size: 32, weight: isFoc ? .bold : .medium))
                                    .foregroundColor(isFoc ? Color.black : Color.white)
                                    .frame(width: 100, height: 68)
                                    .background(isFoc ? Color.white : Color.white.opacity(0.12))
                                    .cornerRadius(16)
                                    .shadow(color: isFoc ? Color.white.opacity(0.35) : Color.clear, radius: 12)
                                    .captureFrame(id: isFoc ? "collectionItem_keypad_\(digit)_focused" : "collectionItem_keypad_\(digit)_unfocused")
                            }
                        }
                    }

                    HStack(spacing: 20) {
                        let isCancelFoc = (foc == 10)
                        Text("Cancel")
                            .font(.system(size: 24, weight: isCancelFoc ? .bold : .medium))
                            .foregroundColor(isCancelFoc ? Color.black : Color.white)
                            .frame(width: 100, height: 68)
                            .background(isCancelFoc ? Color.white : Color.white.opacity(0.12))
                            .cornerRadius(16)
                            .shadow(color: isCancelFoc ? Color.white.opacity(0.35) : Color.clear, radius: 12)
                            .captureFrame(id: isCancelFoc ? "cancelAction_pin_cancel_focused" : "cancelAction_pin_cancel_unfocused")

                        let isZeroFoc = (foc == 0)
                        Text("0")
                            .font(.system(size: 32, weight: isZeroFoc ? .bold : .medium))
                            .foregroundColor(isZeroFoc ? Color.black : Color.white)
                            .frame(width: 100, height: 68)
                            .background(isZeroFoc ? Color.white : Color.white.opacity(0.12))
                            .cornerRadius(16)
                            .shadow(color: isZeroFoc ? Color.white.opacity(0.35) : Color.clear, radius: 12)
                            .captureFrame(id: isZeroFoc ? "collectionItem_keypad_0_focused" : "collectionItem_keypad_0_unfocused")

                        Image(systemName: "delete.left")
                            .font(.system(size: 26))
                            .foregroundColor(Color.white)
                            .frame(width: 100, height: 68)
                            .background(Color.white.opacity(0.12))
                            .cornerRadius(16)
                            .captureFrame(id: "collectionItem_keypad_delete_unfocused")
                    }
                }
            }
            .padding(48)
            .background(Color(red: 0.12, green: 0.12, blue: 0.16))
            .cornerRadius(32)
            .shadow(color: Color.black.opacity(0.7), radius: 40)
            .captureFrame(id: "sheet_pin_dialog")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 18: VoiceOver Accessibility Overlay

struct VoiceOverOverlayView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let utterances = [
            ("Settings, button. Double tap to open.", "Actions available", "Settings"),
            ("Watch Now, Severance Season 2, Episode 1, button.", "Play episode", "Severance"),
            ("Photos, button. 1,420 photos.", "Double tap to browse library", "Photos"),
            ("Search, text field. Double tap to edit.", "Dictation available", "Search")
        ]
        let u = utterances[Int(rng.next() % UInt64(utterances.count))]
        let cx = CGFloat(400 + (rng.next() % 800))
        let cy = CGFloat(200 + (rng.next() % 400))

        ZStack(alignment: .topLeading) {
            Color.black.opacity(0.92).ignoresSafeArea()

            VStack(spacing: 12) {
                ZStack {
                    RoundedRectangle(cornerRadius: 18)
                        .fill(Color(red: 0.2, green: 0.2, blue: 0.28))
                    Image(systemName: "appletvremote.gen4.fill")
                        .font(.system(size: 64))
                        .foregroundColor(.white)
                        .captureFrame(id: "imageView_vo_item_icon")
                }
                .frame(width: 296, height: 156)

                Text(u.2)
                    .font(.system(size: 26, weight: .bold))
                    .foregroundColor(.white)
                    .captureFrame(id: "label_vo_item_title")
            }
            .frame(width: 320, height: 220)
            .background(Color.white.opacity(0.08))
            .cornerRadius(22)
            .overlay(
                RoundedRectangle(cornerRadius: 22)
                    .strokeBorder(Color.black, lineWidth: 6)
                    .overlay(
                        RoundedRectangle(cornerRadius: 22)
                            .strokeBorder(Color.white, lineWidth: 3)
                    )
            )
            .position(x: cx, y: cy)
            .captureFrame(id: "collectionItem_vo_focused_element_focused")

            VStack {
                Spacer()
                HStack(spacing: 24) {
                    Image(systemName: "accessibility")
                        .font(.system(size: 32, weight: .semibold))
                        .foregroundColor(.white)
                        .captureFrame(id: "imageView_vo_badge")

                    VStack(alignment: .leading, spacing: 4) {
                        Text(u.0)
                            .font(.system(size: 28, weight: .semibold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_vo_spoken_text")

                        Text(u.1)
                            .font(.system(size: 20))
                            .foregroundColor(.white.opacity(0.7))
                            .captureFrame(id: "label_vo_hint_text")
                    }
                    Spacer()
                }
                .padding(.horizontal, 36)
                .frame(width: 1400, height: 96)
                .background(Color.black.opacity(0.9))
                .cornerRadius(24)
                .overlay(
                    RoundedRectangle(cornerRadius: 24)
                        .stroke(Color.white.opacity(0.35), lineWidth: 1.5)
                )
                .padding(.bottom, 48)
                .captureFrame(id: "sheet_vo_caption_bar")
            }
            .frame(width: 1920, height: 1080)
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 19: Now Playing & Synchronized Lyrics

struct NowPlayingLyricsView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let songs = [
            ("Starboy", "The Weeknd • Starboy"),
            ("Blinding Lights", "The Weeknd • After Hours"),
            ("Cruel Summer", "Taylor Swift • Lover"),
            ("As It Was", "Harry Styles • Harry's House")
        ]
        let s = songs[Int(rng.next() % UInt64(songs.count))]
        let lines = [
            "Waiting for the right moment",
            "Running through the city lights",
            "I look into the mirror and see it all",
            "Nothing compares to this feeling",
            "Holding on until tomorrow comes",
            "Every heartbeat keeps the rhythm"
        ]
        let activeIdx = Int(rng.next() % UInt64(lines.count))
        let prog = Double(20 + (rng.next() % 60)) / 100.0
        let hue = Double(rng.next() % 1000) / 1000.0

        ZStack {
            LinearGradient(
                colors: [
                    Color(hue: hue, saturation: 0.7, brightness: 0.25),
                    Color(hue: (hue + 0.2).truncatingRemainder(dividingBy: 1.0), saturation: 0.6, brightness: 0.15),
                    Color.black
                ],
                startPoint: .topLeading, endPoint: .bottomTrailing
            ).ignoresSafeArea()

            HStack(spacing: 80) {
                VStack(alignment: .leading, spacing: 28) {
                    Spacer()
                    ZStack {
                        RoundedRectangle(cornerRadius: 24)
                            .fill(LinearGradient(
                                colors: [Color(hue: hue, saturation: 0.8, brightness: 0.6), Color.black.opacity(0.8)],
                                startPoint: .topLeading, endPoint: .bottomTrailing
                            ))
                        Image(systemName: "music.note")
                            .font(.system(size: 96))
                            .foregroundColor(.white.opacity(0.9))
                    }
                    .frame(width: 440, height: 440)
                    .shadow(color: Color.black.opacity(0.6), radius: 30)
                    .captureFrame(id: "imageView_album_art")

                    VStack(alignment: .leading, spacing: 10) {
                        Text(s.0)
                            .font(.system(size: 38, weight: .bold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_song_title")

                        Text(s.1)
                            .font(.system(size: 24))
                            .foregroundColor(.white.opacity(0.7))
                            .captureFrame(id: "label_artist_name")
                    }

                    VStack(spacing: 12) {
                        GeometryReader { geo in
                            ZStack(alignment: .leading) {
                                RoundedRectangle(cornerRadius: 4)
                                    .fill(Color.white.opacity(0.2))
                                    .frame(height: 8)

                                RoundedRectangle(cornerRadius: 4)
                                    .fill(Color.white)
                                    .frame(width: geo.size.width * CGFloat(prog), height: 8)
                            }
                        }
                        .frame(width: 440, height: 20)
                        .captureFrame(id: "slider_music_scrubber")

                        HStack {
                            Text("1:42")
                                .font(.system(size: 18))
                                .foregroundColor(.white.opacity(0.6))
                                .captureFrame(id: "label_elapsed_time")
                            Spacer()
                            Text("-2:18")
                                .font(.system(size: 18))
                                .foregroundColor(.white.opacity(0.6))
                                .captureFrame(id: "label_remaining_time")
                        }
                        .frame(width: 440)
                    }

                    HStack(spacing: 32) {
                        Image(systemName: "quote.bubble.fill")
                            .font(.system(size: 24))
                            .foregroundColor(.white)
                            .frame(width: 56, height: 56)
                            .background(Color.white.opacity(0.2))
                            .cornerRadius(14)
                            .captureFrame(id: "secondaryButton_lyrics_toggle_unfocused")

                        Image(systemName: "airplayaudio")
                            .font(.system(size: 24))
                            .foregroundColor(.white)
                            .frame(width: 56, height: 56)
                            .background(Color.white.opacity(0.12))
                            .cornerRadius(14)
                            .captureFrame(id: "secondaryButton_airplay_toggle_unfocused")
                    }
                    Spacer()
                }
                .padding(.leading, 100)

                VStack(alignment: .leading, spacing: 32) {
                    Spacer()
                    ForEach(Array(lines.enumerated()), id: \.offset) { idx, line in
                        let isActive = (idx == activeIdx)
                        Text(line)
                            .font(.system(size: isActive ? 42 : 32, weight: isActive ? .bold : .medium))
                            .foregroundColor(isActive ? Color.white : Color.white.opacity(0.35))
                            .scaleEffect(isActive ? 1.03 : 1.0, anchor: .leading)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.vertical, 8)
                            .captureFrame(id: isActive ? "listRow_lyric_\(idx)_focused" : "listRow_lyric_\(idx)_unfocused")
                    }
                    Spacer()
                }
                .padding(.trailing, 100)
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 20: App Store Product Page

struct AppStoreProductView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let apps = [
            ("Zwift: Ride and Run", "Zwift, Inc.", "Health & Fitness • 4+", "Immersive indoor cycling and running workouts.", "Get"),
            ("Infuse — Video Player", "FireCore", "Entertainment • 12+", "Ignite your video content on Apple TV with beautiful artwork.", "Open"),
            ("Asphalt 8: Airborne", "Gameloft", "Games • 12+", "High-octane arcade racing with MFi controller support.", "Get"),
            ("Streaks Workout", "Crunchy Bagel", "Health • 4+", "Quick personal daily workouts in your living room.", "Install")
        ]
        let item = apps[Int(rng.next() % UInt64(apps.count))]
        let foc = Int(rng.next() % 5)
        let hue = Double(rng.next() % 1000) / 1000.0

        ZStack {
            Color(red: 0.08, green: 0.08, blue: 0.12).ignoresSafeArea()

            VStack(alignment: .leading, spacing: 36) {
                HStack(alignment: .top, spacing: 40) {
                    ZStack {
                        RoundedRectangle(cornerRadius: 32)
                            .fill(LinearGradient(
                                colors: [Color(hue: hue, saturation: 0.7, brightness: 0.6), Color.black.opacity(0.8)],
                                startPoint: .topLeading, endPoint: .bottomTrailing
                            ))
                        Image(systemName: "app.gift.fill")
                            .font(.system(size: 80))
                            .foregroundColor(.white.opacity(0.9))
                    }
                    .frame(width: 220, height: 220)
                    .shadow(color: Color.black.opacity(0.5), radius: 20)
                    .captureFrame(id: "imageView_app_store_icon")

                    VStack(alignment: .leading, spacing: 14) {
                        Text(item.0)
                            .font(.system(size: 44, weight: .bold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_app_name")

                        Text(item.1)
                            .font(.system(size: 24, weight: .medium))
                            .foregroundColor(.white.opacity(0.7))
                            .captureFrame(id: "label_developer_name")

                        Text(item.2)
                            .font(.system(size: 20))
                            .foregroundColor(.white.opacity(0.5))
                            .captureFrame(id: "label_category_rating")

                        Spacer().frame(height: 10)

                        HStack(spacing: 24) {
                            let isPrimaryFoc = (foc == 0)
                            Text(item.4)
                                .font(.system(size: 26, weight: .bold))
                                .foregroundColor(isPrimaryFoc ? Color.black : Color.white)
                                .frame(width: 180, height: 64)
                                .background(isPrimaryFoc ? Color.white : Color.white.opacity(0.15))
                                .cornerRadius(16)
                                .shadow(color: isPrimaryFoc ? Color.white.opacity(0.4) : Color.clear, radius: 14)
                                .captureFrame(id: isPrimaryFoc ? "primaryButton_get_app_focused" : "primaryButton_get_app_unfocused")

                            let isSecFoc = (foc == 1)
                            Image(systemName: "ellipsis")
                                .font(.system(size: 24))
                                .foregroundColor(isSecFoc ? Color.black : Color.white)
                                .frame(width: 64, height: 64)
                                .background(isSecFoc ? Color.white : Color.white.opacity(0.12))
                                .cornerRadius(16)
                                .shadow(color: isSecFoc ? Color.white.opacity(0.4) : Color.clear, radius: 14)
                                .captureFrame(id: isSecFoc ? "secondaryButton_app_more_focused" : "secondaryButton_app_more_unfocused")
                        }
                    }
                    Spacer()
                }
                .padding(.top, 60)
                .padding(.horizontal, 90)

                Text(item.3)
                    .font(.system(size: 24))
                    .foregroundColor(.white.opacity(0.8))
                    .lineLimit(2)
                    .padding(.horizontal, 90)
                    .captureFrame(id: "label_app_description")

                VStack(alignment: .leading, spacing: 16) {
                    Text("Screenshots")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.white)
                        .padding(.horizontal, 90)
                        .captureFrame(id: "label_screenshots_heading")

                    HStack(spacing: 36) {
                        ForEach(0..<3) { idx in
                            let targetIdx = idx + 2
                            let isFoc = (foc == targetIdx)

                            ZStack {
                                RoundedRectangle(cornerRadius: 18)
                                    .fill(LinearGradient(
                                        colors: [Color(hue: (hue + Double(idx) * 0.1).truncatingRemainder(dividingBy: 1.0), saturation: 0.5, brightness: 0.4), Color.black.opacity(0.7)],
                                        startPoint: .topLeading, endPoint: .bottomTrailing
                                    ))
                                Image(systemName: "photo.fill")
                                    .font(.system(size: 48))
                                    .foregroundColor(.white.opacity(0.6))
                                    .captureFrame(id: "imageView_screenshot_\(idx)")
                            }
                            .frame(width: 530, height: 300)
                            .overlay(
                                RoundedRectangle(cornerRadius: 18)
                                    .stroke(isFoc ? Color.white : Color.clear, lineWidth: 4)
                            )
                            .shadow(color: isFoc ? Color.white.opacity(0.4) : Color.black.opacity(0.4), radius: isFoc ? 20 : 8)
                            .captureFrame(id: isFoc ? "collectionItem_screenshot_\(idx)_focused" : "collectionItem_screenshot_\(idx)_unfocused")
                        }
                    }
                    .padding(.horizontal, 90)
                }
                Spacer()
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 21: Sign In With Apple / QR Code Modal

struct SignInWithAppleView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let titles = [
            ("Sign In with iPhone", "Bring your iPhone or iPad near this Apple TV to sign in automatically."),
            ("Authorize TVTestRig", "Scan the code with your registered developer device to permit automation."),
            ("Apple Account Setup", "Open Camera on an Apple device running iOS 17 or later and scan.")
        ]
        let item = titles[Int(rng.next() % UInt64(titles.count))]
        let code = String(format: "%03d - %03d", rng.next() % 1000, rng.next() % 1000)
        let foc = Int(rng.next() % 2)

        ZStack {
            Color.black.opacity(0.85).ignoresSafeArea()

            HStack(spacing: 64) {
                ZStack {
                    RoundedRectangle(cornerRadius: 24)
                        .fill(Color.white)
                    Image(systemName: "qrcode")
                        .font(.system(size: 200))
                        .foregroundColor(.black)
                }
                .frame(width: 320, height: 320)
                .captureFrame(id: "imageView_signin_qrcode")

                VStack(alignment: .leading, spacing: 20) {
                    HStack(spacing: 14) {
                        Image(systemName: "applelogo")
                            .font(.system(size: 32))
                            .foregroundColor(.white)
                            .captureFrame(id: "imageView_apple_logo")

                        Text(item.0)
                            .font(.system(size: 38, weight: .bold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_signin_title")
                    }

                    Text(item.1)
                        .font(.system(size: 22))
                        .foregroundColor(.white.opacity(0.75))
                        .lineLimit(3)
                        .frame(maxWidth: 580, alignment: .leading)
                        .captureFrame(id: "label_signin_subtitle")

                    HStack(spacing: 12) {
                        Text("Code:")
                            .font(.system(size: 20, weight: .medium))
                            .foregroundColor(.white.opacity(0.5))
                            .captureFrame(id: "label_code_prefix")

                        Text(code)
                            .font(.system(size: 30, weight: .bold, design: .monospaced))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_pairing_code")
                    }
                    .padding(.vertical, 8)

                    Text("apple.com/appleid")
                        .font(.system(size: 20))
                        .foregroundColor(Color.blue)
                        .underline()
                        .captureFrame(id: "link_appleid_help")

                    Spacer().frame(height: 12)

                    HStack(spacing: 24) {
                        let isSecFoc = (foc == 0)
                        Text("Use Remote Instead")
                            .font(.system(size: 22, weight: isSecFoc ? .bold : .medium))
                            .foregroundColor(isSecFoc ? Color.black : Color.white)
                            .padding(.horizontal, 28)
                            .frame(height: 60)
                            .background(isSecFoc ? Color.white : Color.white.opacity(0.12))
                            .cornerRadius(14)
                            .shadow(color: isSecFoc ? Color.white.opacity(0.35) : Color.clear, radius: 10)
                            .captureFrame(id: isSecFoc ? "secondaryButton_use_remote_focused" : "secondaryButton_use_remote_unfocused")

                        let isCancelFoc = (foc == 1)
                        Text("Cancel")
                            .font(.system(size: 22, weight: isCancelFoc ? .bold : .medium))
                            .foregroundColor(isCancelFoc ? Color.black : Color.white)
                            .padding(.horizontal, 28)
                            .frame(height: 60)
                            .background(isCancelFoc ? Color.white : Color.white.opacity(0.12))
                            .cornerRadius(14)
                            .shadow(color: isCancelFoc ? Color.white.opacity(0.35) : Color.clear, radius: 10)
                            .captureFrame(id: isCancelFoc ? "cancelAction_signin_cancel_focused" : "cancelAction_signin_cancel_unfocused")
                    }
                }
            }
            .padding(56)
            .background(Color(red: 0.12, green: 0.12, blue: 0.16))
            .cornerRadius(32)
            .shadow(color: Color.black.opacity(0.7), radius: 40)
            .captureFrame(id: "sheet_signin_modal")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 22: Fitness & Workout HUD

struct FitnessHUDView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let workouts = [
            ("Bakari • HIIT", "High Intensity Interval Training"),
            ("Jessica • Yoga", "Slow Flow Yoga"),
            ("Tyrell • Cycling", "Pure Dance Cycling"),
            ("Sam • Strength", "Upper Body Strength")
        ]
        let w = workouts[Int(rng.next() % UInt64(workouts.count))]
        let cal = Int(150 + (rng.next() % 400))
        let bpm = Int(110 + (rng.next() % 65))
        let min = Int(rng.next() % 45)
        let sec = Int(rng.next() % 60)
        let prog = Double(40 + (rng.next() % 50)) / 100.0

        ZStack(alignment: .topLeading) {
            LinearGradient(
                colors: [Color(red: 0.05, green: 0.05, blue: 0.08), Color(red: 0.1, green: 0.05, blue: 0.12)],
                startPoint: .top, endPoint: .bottom
            ).ignoresSafeArea()

            VStack(alignment: .leading, spacing: 18) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(w.0)
                        .font(.system(size: 26, weight: .bold))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_fitness_coach")

                    Text(w.1)
                        .font(.system(size: 18))
                        .foregroundColor(.white.opacity(0.6))
                        .captureFrame(id: "label_fitness_type")
                }

                Text(String(format: "%02d:%02d", min, sec))
                    .font(.system(size: 52, weight: .heavy, design: .rounded))
                    .foregroundColor(.white)
                    .captureFrame(id: "label_fitness_timer")

                HStack(spacing: 12) {
                    Image(systemName: "flame.fill")
                        .font(.system(size: 26))
                        .foregroundColor(.red)
                        .captureFrame(id: "imageView_flame_icon")

                    HStack(alignment: .lastTextBaseline, spacing: 6) {
                        Text("\(cal)")
                            .font(.system(size: 38, weight: .bold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_calorie_count")

                        Text("CAL")
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.white.opacity(0.6))
                            .captureFrame(id: "label_cal_unit")
                    }
                }

                HStack(spacing: 12) {
                    Image(systemName: "heart.fill")
                        .font(.system(size: 24))
                        .foregroundColor(.red)
                        .captureFrame(id: "activityIndicator_heart_pulse")

                    HStack(alignment: .lastTextBaseline, spacing: 6) {
                        Text("\(bpm)")
                            .font(.system(size: 38, weight: .bold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_heart_rate_bpm")

                        Text("BPM")
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.white.opacity(0.6))
                            .captureFrame(id: "label_bpm_unit")
                    }
                }

                VStack(alignment: .leading, spacing: 6) {
                    Text("BURN BAR")
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.white.opacity(0.6))
                        .captureFrame(id: "label_burn_bar_title")

                    ZStack(alignment: .leading) {
                        RoundedRectangle(cornerRadius: 6)
                            .fill(Color.white.opacity(0.15))
                            .frame(width: 280, height: 12)

                        RoundedRectangle(cornerRadius: 6)
                            .fill(LinearGradient(colors: [.yellow, .orange, .red], startPoint: .leading, endPoint: .trailing))
                            .frame(width: 280 * CGFloat(prog), height: 12)
                    }
                    .captureFrame(id: "progressView_burn_bar")
                }
            }
            .padding(32)
            .background(Color.black.opacity(0.65))
            .cornerRadius(24)
            .padding(.leading, 80)
            .padding(.top, 60)

            VStack {
                HStack {
                    Spacer()
                    ZStack {
                        Circle()
                            .stroke(Color.red.opacity(0.25), lineWidth: 14)
                        Circle()
                            .trim(from: 0, to: CGFloat(prog))
                            .stroke(Color.red, style: StrokeStyle(lineWidth: 14, lineCap: .round))
                            .rotationEffect(.degrees(-90))

                        Circle()
                            .stroke(Color.green.opacity(0.25), lineWidth: 14)
                            .frame(width: 100, height: 100)
                        Circle()
                            .trim(from: 0, to: CGFloat(prog * 0.85))
                            .stroke(Color.green, style: StrokeStyle(lineWidth: 14, lineCap: .round))
                            .frame(width: 100, height: 100)
                            .rotationEffect(.degrees(-90))

                        Circle()
                            .stroke(Color.blue.opacity(0.25), lineWidth: 14)
                            .frame(width: 68, height: 68)
                        Circle()
                            .trim(from: 0, to: CGFloat(prog * 0.95))
                            .stroke(Color.blue, style: StrokeStyle(lineWidth: 14, lineCap: .round))
                            .frame(width: 68, height: 68)
                            .rotationEffect(.degrees(-90))
                    }
                    .frame(width: 132, height: 132)
                    .padding(24)
                    .background(Color.black.opacity(0.65))
                    .cornerRadius(24)
                    .padding(.trailing, 80)
                    .padding(.top, 60)
                    .captureFrame(id: "progressView_activity_rings")
                }
                Spacer()
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 23: Loading & Buffering HUD

struct LoadingBuffersView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let messages = [
            ("Loading...", "Preparing video playback..."),
            ("Updating Library...", "Syncing with iCloud..."),
            ("Installing Software Update...", "Apple TV will restart when finished."),
            ("Buffering Stream...", "Optimizing video quality for your network connection.")
        ]
        let item = messages[Int(rng.next() % UInt64(messages.count))]
        let isDeterminate = (rng.next() % 2 == 0)
        let prog = Double(10 + (rng.next() % 85)) / 100.0

        ZStack {
            Color.black.opacity(0.88).ignoresSafeArea()

            VStack(spacing: 32) {
                ZStack {
                    ForEach(0..<8) { i in
                        RoundedRectangle(cornerRadius: 3)
                            .fill(Color.white.opacity(Double(i + 1) / 8.0))
                            .frame(width: 8, height: 22)
                            .offset(y: -30)
                            .rotationEffect(.degrees(Double(i) * 45.0))
                    }
                }
                .frame(width: 80, height: 80)
                .captureFrame(id: "activityIndicator_system_spinner")

                VStack(spacing: 12) {
                    Text(item.0)
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_loading_title")

                    Text(item.1)
                        .font(.system(size: 22))
                        .foregroundColor(.white.opacity(0.7))
                        .captureFrame(id: "label_loading_subtitle")
                }

                if isDeterminate {
                    VStack(spacing: 10) {
                        ZStack(alignment: .leading) {
                            RoundedRectangle(cornerRadius: 6)
                                .fill(Color.white.opacity(0.2))
                                .frame(width: 440, height: 10)

                            RoundedRectangle(cornerRadius: 6)
                                .fill(Color.white)
                                .frame(width: 440 * CGFloat(prog), height: 10)
                        }
                        .captureFrame(id: "progressView_download_progress")

                        Text("\(Int(prog * 100))%")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.white.opacity(0.6))
                            .captureFrame(id: "label_progress_percent")
                    }
                }
            }
            .padding(48)
            .frame(width: 640)
            .background(Color(red: 0.14, green: 0.14, blue: 0.18))
            .cornerRadius(28)
            .shadow(color: Color.black.opacity(0.6), radius: 32)
            .captureFrame(id: "sheet_loading_modal")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 24: Live Broadcast & Sports HUD

struct LiveBroadcastHUDView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let matchups = [
            ("LAD", "NYY", 4, 3, "Top 8th • 1 Out"),
            ("BOS", "PHI", 2, 5, "Bottom 6th • 2 Outs"),
            ("GSW", "LAL", 108, 102, "4th Qtr • 2:45"),
            ("MIA", "BOS", 89, 94, "3rd Qtr • 0:12")
        ]
        let m = matchups[Int(rng.next() % UInt64(matchups.count))]
        let selSeg = Int(rng.next() % 3)
        let focChan = Int(rng.next() % 4)
        let hue = Double(rng.next() % 1000) / 1000.0

        ZStack(alignment: .topLeading) {
            LinearGradient(
                colors: [Color(hue: hue, saturation: 0.6, brightness: 0.2), Color.black],
                startPoint: .top, endPoint: .bottom
            ).ignoresSafeArea()

            HStack(spacing: 20) {
                HStack(spacing: 6) {
                    Circle()
                        .fill(Color.white)
                        .frame(width: 8, height: 8)
                    Text("LIVE")
                        .font(.system(size: 16, weight: .black))
                        .foregroundColor(.white)
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(Color.red)
                .cornerRadius(8)
                .captureFrame(id: "label_live_badge")

                HStack(spacing: 16) {
                    Text("\(m.0) \(m.2)")
                        .font(.system(size: 26, weight: .heavy))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_home_score")

                    Text("-")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.white.opacity(0.6))

                    Text("\(m.3) \(m.1)")
                        .font(.system(size: 26, weight: .heavy))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_away_score")
                }

                Text(m.4)
                    .font(.system(size: 20, weight: .medium))
                    .foregroundColor(.white.opacity(0.8))
                    .captureFrame(id: "label_game_clock")
            }
            .padding(.horizontal, 24)
            .padding(.vertical, 14)
            .background(Color.black.opacity(0.75))
            .cornerRadius(18)
            .padding(.leading, 80)
            .padding(.top, 60)

            VStack {
                Spacer()
                HStack(spacing: 0) {
                    let segments = ["Game Cast", "Box Score", "Multiview"]
                    ForEach(Array(segments.enumerated()), id: \.offset) { idx, seg in
                        let isSel = (idx == selSeg)
                        Text(seg)
                            .font(.system(size: 20, weight: isSel ? .bold : .medium))
                            .foregroundColor(isSel ? Color.black : Color.white)
                            .padding(.horizontal, 24)
                            .padding(.vertical, 10)
                            .background(isSel ? Color.white : Color.clear)
                            .cornerRadius(12)
                    }
                }
                .padding(6)
                .background(Color.white.opacity(0.12))
                .cornerRadius(16)
                .captureFrame(id: "segmentedControl_sports_modes")
                .padding(.bottom, 20)

                HStack(spacing: 32) {
                    ForEach(0..<4) { idx in
                        let isFoc = (idx == focChan)

                        VStack(alignment: .leading, spacing: 10) {
                            ZStack {
                                RoundedRectangle(cornerRadius: 16)
                                    .fill(Color.white.opacity(0.15))
                                Image(systemName: "tv.fill")
                                    .font(.system(size: 40))
                                    .foregroundColor(.white.opacity(0.7))
                            }
                            .frame(width: 320, height: 180)
                            .overlay(
                                RoundedRectangle(cornerRadius: 16)
                                    .stroke(isFoc ? Color.white : Color.clear, lineWidth: 4)
                            )
                            .shadow(color: isFoc ? Color.white.opacity(0.35) : Color.clear, radius: 16)

                            Text("Channel \(idx + 1)")
                                .font(.system(size: 20, weight: isFoc ? .bold : .medium))
                                .foregroundColor(isFoc ? .white : .white.opacity(0.7))
                                .captureFrame(id: "label_channel_name_\(idx)")
                        }
                        // Whole-cell box: artwork plus name (Research 5.2.1).
                        .captureFrame(id: isFoc ? "collectionItem_channel_\(idx)_focused" : "collectionItem_channel_\(idx)_unfocused")
                    }
                }
                .padding(.bottom, 48)
            }
            .frame(width: 1920)
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// MARK: - Template 25: Conference Room Display

struct ConferenceRoomView: View {
    let seed: UInt64
    var corpus: ContentCorpus

    var body: some View {
        var rng = SeededRNG(seed: seed)
        let rooms = [
            ("Executive Conference Room", "Apple-Guest"),
            ("Design Studio Apple TV", "Studio-5GHz"),
            ("Engineering All-Hands", "Corp-WPA3"),
            ("Briefing Center 4K", "Guest-Wireless")
        ]
        let r = rooms[Int(rng.next() % UInt64(rooms.count))]
        let code = String(format: "%04d", rng.next() % 10000)
        let hue = Double(rng.next() % 1000) / 1000.0

        ZStack {
            LinearGradient(
                colors: [
                    Color(hue: hue, saturation: 0.5, brightness: 0.25),
                    Color(hue: (hue + 0.1).truncatingRemainder(dividingBy: 1.0), saturation: 0.4, brightness: 0.15),
                    Color.black
                ],
                startPoint: .topLeading, endPoint: .bottomTrailing
            ).ignoresSafeArea()

            VStack(spacing: 36) {
                ZStack {
                    Circle()
                        .fill(Color.white.opacity(0.15))
                    Image(systemName: "airplayvideo")
                        .font(.system(size: 64))
                        .foregroundColor(.white)
                }
                .frame(width: 120, height: 120)
                .captureFrame(id: "imageView_conference_airplay_icon")

                VStack(spacing: 8) {
                    Text("AirPlay to")
                        .font(.system(size: 26, weight: .medium))
                        .foregroundColor(.white.opacity(0.7))
                        .captureFrame(id: "label_airplay_to_prefix")

                    Text(r.0)
                        .font(.system(size: 44, weight: .bold))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_room_name")
                }

                VStack(spacing: 16) {
                    HStack(spacing: 16) {
                        Image(systemName: "wifi")
                            .font(.system(size: 24))
                            .foregroundColor(.white.opacity(0.8))
                            .captureFrame(id: "imageView_wifi_icon")

                        Text("Wi-Fi: \(r.1)")
                            .font(.system(size: 26, weight: .semibold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_wifi_network")
                    }

                    Text("To present, connect your Apple device to Wi-Fi and choose AirPlay.")
                        .font(.system(size: 22))
                        .foregroundColor(.white.opacity(0.75))
                        .multilineTextAlignment(.center)
                        .frame(maxWidth: 600)
                        .captureFrame(id: "label_instructions")
                }
                .padding(28)
                .background(Color.white.opacity(0.08))
                .cornerRadius(20)

                VStack(spacing: 8) {
                    Text("AIRPLAY CODE")
                        .font(.system(size: 18, weight: .bold))
                        .foregroundColor(.white.opacity(0.6))
                        .captureFrame(id: "label_code_heading")

                    Text(code)
                        .font(.system(size: 48, weight: .heavy, design: .monospaced))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_airplay_code")
                }
            }
            .padding(56)
            .frame(width: 820)
            .background(Color(red: 0.12, green: 0.12, blue: 0.16))
            .cornerRadius(32)
            .shadow(color: Color.black.opacity(0.7), radius: 40)
            .captureFrame(id: "sheet_conference_card")
        }
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
            ("tvOSAppSwitcher", 1),
            ("tvOSPINEntry", 1),
            ("tvOSVoiceOverOverlay", 1),
            ("tvOSNowPlayingLyrics", 1),
            ("tvOSAppStoreProduct", 1),
            ("tvOSSignInWithApple", 1),
            ("tvOSFitnessHUD", 1),
            ("tvOSLoadingBuffers", 1),
            ("tvOSLiveBroadcastHUD", 1),
            ("tvOSConferenceRoom", 1),
            ("tvOSHardNegatives", 1),
            ("tvOSContentCells", 1),
            ("tvOSTabRows", 1)
        ]
    } else {
        // Distribute proportionally across all 25 template families
        let baseCount = max(1, targetCount / 25)
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
            ("tvOSAppSwitcher", baseCount),
            ("tvOSPINEntry", baseCount),
            ("tvOSVoiceOverOverlay", baseCount),
            ("tvOSNowPlayingLyrics", baseCount),
            ("tvOSAppStoreProduct", baseCount),
            ("tvOSSignInWithApple", baseCount),
            ("tvOSFitnessHUD", baseCount),
            ("tvOSLoadingBuffers", baseCount),
            ("tvOSLiveBroadcastHUD", baseCount),
            ("tvOSConferenceRoom", baseCount),
            ("tvOSHardNegatives", max(1, targetCount - (baseCount * 24))),
            // CELLS558 S3: real-like cells, added on top of the original 25-family counts.
            ("tvOSContentCells", baseCount * 2),
            // PILLS560: tab rows above content, added last so earlier families keep their pixels.
            ("tvOSTabRows", baseCount * 2)
        ]
    }

    let totalTarget = counts.reduce(0) { $0 + $1.count }
    print("Generating \(totalTarget) tvOS OS UI images across \(counts.count) families at 1920x1080 into \(outDir.path)...")
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
            case "tvOSAppSwitcher":
                renderAndSave(view: AppSwitcherView(seed: s, corpus: corpus), family: family)
            case "tvOSPINEntry":
                renderAndSave(view: PINEntryView(seed: s, corpus: corpus), family: family)
            case "tvOSVoiceOverOverlay":
                renderAndSave(view: VoiceOverOverlayView(seed: s, corpus: corpus), family: family)
            case "tvOSNowPlayingLyrics":
                renderAndSave(view: NowPlayingLyricsView(seed: s, corpus: corpus), family: family)
            case "tvOSAppStoreProduct":
                renderAndSave(view: AppStoreProductView(seed: s, corpus: corpus), family: family)
            case "tvOSSignInWithApple":
                renderAndSave(view: SignInWithAppleView(seed: s, corpus: corpus), family: family)
            case "tvOSFitnessHUD":
                renderAndSave(view: FitnessHUDView(seed: s, corpus: corpus), family: family)
            case "tvOSLoadingBuffers":
                renderAndSave(view: LoadingBuffersView(seed: s, corpus: corpus), family: family)
            case "tvOSLiveBroadcastHUD":
                renderAndSave(view: LiveBroadcastHUDView(seed: s, corpus: corpus), family: family)
            case "tvOSConferenceRoom":
                renderAndSave(view: ConferenceRoomView(seed: s, corpus: corpus), family: family)
            case "tvOSHardNegatives":
                renderAndSave(view: HardNegativeView(seed: s), family: family)
            case "tvOSContentCells":
                renderAndSave(view: ContentCellsView(seed: s), family: family)
            case "tvOSTabRows":
                renderAndSave(view: TabRowsView(seed: s), family: family)
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
