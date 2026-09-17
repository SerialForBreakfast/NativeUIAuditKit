// tvOSVoiceOverOverlayTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS VoiceOver accessibility overlay template for OS UI detection.
// Models tvOS VoiceOver screen reader activation: high-contrast accessibility cursor
// (thick border) around the focused element, plus the VoiceOver bottom caption speech panel.
//
// Annotated elements:
//   sheet          — VoiceOver caption bar / speech bubble panel at bottom of screen
//   label          — VoiceOver caption spoken text, hint text, and item labels
//   collectionItem — focused item with accessibility cursor overlay

import SwiftUI

// MARK: - tvOSVoiceOverOverlayConfig

public struct tvOSVoiceOverOverlayConfig: Sendable {
    public var spokenText: String
    public var hintText: String
    public var itemTitle: String
    public var itemSubtitle: String
    public var cursorX: CGFloat
    public var cursorY: CGFloat
    public var cursorWidth: CGFloat
    public var cursorHeight: CGFloat

    public init(
        spokenText: String = "Settings, button. Double tap to open.",
        hintText: String = "Actions available",
        itemTitle: String = "Settings",
        itemSubtitle: String = "System Preferences",
        cursorX: CGFloat = 810,
        cursorY: CGFloat = 380,
        cursorWidth: CGFloat = 300,
        cursorHeight: CGFloat = 200
    ) {
        self.spokenText = spokenText
        self.hintText = hintText
        self.itemTitle = itemTitle
        self.itemSubtitle = itemSubtitle
        self.cursorX = cursorX
        self.cursorY = cursorY
        self.cursorWidth = cursorWidth
        self.cursorHeight = cursorHeight
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSVoiceOverOverlayConfig {
        var rng = SeededRNG(seed: seed)
        let utterances = [
            ("Settings, button. Double tap to open.", "Actions available", "Settings", "System Preferences"),
            ("Watch Now, Severance Season 2, Episode 1, button.", "Play episode", "Severance", "Season 2 • Ep 1"),
            ("Photos, button. 1,420 photos.", "Double tap to browse library", "Photos", "1,420 items"),
            ("Search, text field. Double tap to edit.", "Dictation available", "Search", "Find movies & TV")
        ]
        let u = utterances[Int(rng.next() % UInt64(utterances.count))]
        let cx = CGFloat(400 + (rng.next() % 800))
        let cy = CGFloat(200 + (rng.next() % 400))

        return tvOSVoiceOverOverlayConfig(
            spokenText: u.0,
            hintText: u.1,
            itemTitle: u.2,
            itemSubtitle: u.3,
            cursorX: cx,
            cursorY: cy,
            cursorWidth: 320,
            cursorHeight: 220
        )
    }
}

// MARK: - tvOSVoiceOverOverlayTemplate View

public struct tvOSVoiceOverOverlayTemplate: View {
    public let config: tvOSVoiceOverOverlayConfig

    public init(config: tvOSVoiceOverOverlayConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack(alignment: .topLeading) {
            Color.black.opacity(0.92).ignoresSafeArea()

            // Simulated App Item with VoiceOver High-Contrast Cursor
            VStack(spacing: 12) {
                ZStack {
                    RoundedRectangle(cornerRadius: 18)
                        .fill(Color(red: 0.2, green: 0.2, blue: 0.28))
                    Image(systemName: "appletvremote.gen4.fill")
                        .font(.system(size: 64))
                        .foregroundColor(.white)
                        .captureFrame(id: "imageView_vo_item_icon")
                }
                .frame(width: config.cursorWidth - 24, height: config.cursorHeight - 64)

                Text(config.itemTitle)
                    .font(.system(size: 26, weight: .bold))
                    .foregroundColor(.white)
                    .captureFrame(id: "label_vo_item_title")
            }
            .frame(width: config.cursorWidth, height: config.cursorHeight)
            .background(Color.white.opacity(0.08))
            .cornerRadius(22)
            // VoiceOver Accessibility Focus Outline (High-contrast double border)
            .overlay(
                RoundedRectangle(cornerRadius: 22)
                    .strokeBorder(Color.black, lineWidth: 6)
                    .overlay(
                        RoundedRectangle(cornerRadius: 22)
                            .strokeBorder(Color.white, lineWidth: 3)
                    )
            )
            .position(x: config.cursorX, y: config.cursorY)
            .captureFrame(id: "collectionItem_vo_focused_element_focused")

            // VoiceOver Caption Speech Bar at Bottom
            VStack {
                Spacer()
                HStack(spacing: 24) {
                    Image(systemName: "accessibility")
                        .font(.system(size: 32, weight: .semibold))
                        .foregroundColor(.white)
                        .captureFrame(id: "imageView_vo_badge")

                    VStack(alignment: .leading, spacing: 4) {
                        Text(config.spokenText)
                            .font(.system(size: 28, weight: .semibold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_vo_spoken_text")

                        Text(config.hintText)
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
