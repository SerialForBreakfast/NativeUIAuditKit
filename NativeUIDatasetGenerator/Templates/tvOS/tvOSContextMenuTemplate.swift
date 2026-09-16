// tvOSContextMenuTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS Context Menu template for OS UI detection (TASK-6b-E1).
// Models long-press contextual action popups on Apple TV (e.g. on Home screen or TV app tiles).
//
// Annotated elements:
//   contextMenu       — the contextual pop-up menu card
//   collectionItem    — the underlying target tile (movie poster / app card)
//   primaryButton     — primary action inside the menu (e.g. "Play Next")
//   secondaryButton   — secondary actions (e.g. "Mark as Watched", "Share...")
//   destructiveButton — destructive action (e.g. "Delete / Hide")
//   label             — action labels and tile titles
//   imageView         — poster artwork and menu action icons

import SwiftUI

// MARK: - tvOSContextMenuConfig

public struct tvOSContextMenuConfig: Sendable {
    public var targetTitle: String
    public var targetSubtitle: String
    public var menuActions: [(title: String, icon: String, isDestructive: Bool, isPrimary: Bool)]
    public var focusedIndex: Int // -1: target tile focused, 0..N: menu action focused
    public var targetHue: Double

    public init(
        targetTitle: String,
        targetSubtitle: String,
        menuActions: [(title: String, icon: String, isDestructive: Bool, isPrimary: Bool)],
        focusedIndex: Int = 0,
        targetHue: Double = 0.6
    ) {
        self.targetTitle = targetTitle
        self.targetSubtitle = targetSubtitle
        self.menuActions = menuActions
        self.focusedIndex = focusedIndex
        self.targetHue = targetHue
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSContextMenuConfig {
        var rng = SeededRNG(seed: seed)
        let actions: [(title: String, icon: String, isDestructive: Bool, isPrimary: Bool)] = [
            ("Play Next", "play.fill", false, true),
            ("Mark as Watched", "checkmark.circle", false, false),
            ("Remove from Up Next", "minus.circle", false, false),
            ("Share...", "square.and.arrow.up", false, false),
            ("Hide / Delete", "trash.fill", true, false)
        ]

        let foc = Int(rng.next() % UInt64(actions.count))
        let hue = Double(rng.next() % 1000) / 1000.0

        return tvOSContextMenuConfig(
            targetTitle: corpus.navigationTitle(),
            targetSubtitle: corpus.listRowTitle(),
            menuActions: actions,
            focusedIndex: foc,
            targetHue: hue
        )
    }
}

// MARK: - tvOSContextMenuTemplate View

public struct tvOSContextMenuTemplate: View {
    public let config: tvOSContextMenuConfig

    public init(config: tvOSContextMenuConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            // Dimmed dark background with blur simulation
            Color.black.opacity(0.88).ignoresSafeArea()

            HStack(spacing: 64) {
                // 1. Target Card (underlying poster item)
                VStack(alignment: .leading, spacing: 16) {
                    ZStack {
                        RoundedRectangle(cornerRadius: 20)
                            .fill(LinearGradient(
                                colors: [Color(hue: config.targetHue, saturation: 0.65, brightness: 0.5), Color.black.opacity(0.7)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ))
                        Image(systemName: "film.fill")
                            .font(.system(size: 72))
                            .foregroundColor(.white.opacity(0.9))
                            .captureFrame(id: "imageView_target_poster")
                    }
                    .frame(width: 440, height: 660)
                    .overlay(
                        RoundedRectangle(cornerRadius: 20)
                            .stroke(config.focusedIndex == -1 ? Color.white : Color.white.opacity(0.2), lineWidth: config.focusedIndex == -1 ? 4 : 1)
                    )
                    .shadow(color: config.focusedIndex == -1 ? Color.white.opacity(0.4) : Color.black.opacity(0.5), radius: 24)
                    .captureFrame(id: config.focusedIndex == -1 ? "collectionItem_target_focused" : "collectionItem_target_unfocused")

                    VStack(alignment: .leading, spacing: 6) {
                        Text(config.targetTitle)
                            .font(.system(size: 32, weight: .bold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_target_title")
                        Text(config.targetSubtitle)
                            .font(.system(size: 22))
                            .foregroundColor(.white.opacity(0.7))
                            .captureFrame(id: "label_target_subtitle")
                    }
                    .frame(width: 440, alignment: .leading)
                }

                // 2. Context Menu Pop-up Card
                VStack(spacing: 8) {
                    ForEach(Array(config.menuActions.enumerated()), id: \.offset) { idx, act in
                        let isFoc = (idx == config.focusedIndex)
                        let isDestructive = act.isDestructive
                        let isPrimary = act.isPrimary

                        HStack(spacing: 20) {
                            Text(act.title)
                                .font(.system(size: 24, weight: isFoc ? .bold : .medium))
                                .foregroundColor(isFoc ? (isDestructive ? Color.red : Color.black) : (isDestructive ? Color.red.opacity(0.9) : Color.white))
                                .captureFrame(id: "label_menu_item_\(idx)")
                            Spacer()
                            Image(systemName: act.icon)
                                .font(.system(size: 22))
                                .foregroundColor(isFoc ? (isDestructive ? Color.red : Color.black) : (isDestructive ? Color.red.opacity(0.8) : Color.white.opacity(0.7)))
                                .captureFrame(id: "imageView_menu_icon_\(idx)")
                        }
                        .padding(.horizontal, 28)
                        .frame(width: 520, height: 68)
                        .background(isFoc ? Color.white : Color.white.opacity(0.08))
                        .cornerRadius(16)
                        .shadow(color: isFoc ? Color.white.opacity(0.35) : Color.clear, radius: 12)
                        .captureFrame(id: isDestructive
                            ? (isFoc ? "destructiveButton_action_\(idx)_focused" : "destructiveButton_action_\(idx)_unfocused")
                            : (isPrimary
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
