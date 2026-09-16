// tvOSAudioSubtitlesTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised Audio & Subtitles drawer template for tvOS OS UI detection (TASK-6b-E4).
// Models the in-playback audio routing, language selection, subtitles list, and audio accessibility toggles.
//
// Annotated elements:
//   popover          — the audio & subtitles modal sheet container
//   segmentedControl — Audio / Subtitles tab selector
//   listRow          — language option rows (English, Spanish, French, German, Off)
//   toggle           — "Enhance Dialogue", "Reduce Loud Sounds" toggles
//   label            — panel title, section headers, language names, toggle descriptions
//   imageView        — checkmark icons, audio badges (AD, CC, Dolby Atmos)

import SwiftUI

// MARK: - tvOSAudioSubtitlesConfig

public struct tvOSAudioSubtitlesConfig: Sendable {
    public var selectedSegment: Int // 0: Subtitles, 1: Audio
    public var languages: [(name: String, badge: String?)]
    public var selectedLanguageIndex: Int
    public var isDialogueBoostOn: Bool
    public var isReduceLoudSoundsOn: Bool
    public var focusTarget: AudioSubtitlesFocusTarget // .segment, .language(Int), .dialogueBoost, .reduceLoud

    public enum AudioSubtitlesFocusTarget: Sendable {
        case segment
        case language(Int)
        case dialogueBoost
        case reduceLoud
    }

    public init(
        selectedSegment: Int = 0,
        languages: [(name: String, badge: String?)] = [
            ("Off", nil),
            ("English [CC]", "CC"),
            ("Spanish (Latin America)", nil),
            ("French (France)", nil),
            ("German", nil),
            ("Japanese", nil)
        ],
        selectedLanguageIndex: Int = 1,
        isDialogueBoostOn: Bool = true,
        isReduceLoudSoundsOn: Bool = false,
        focusTarget: AudioSubtitlesFocusTarget = .language(1)
    ) {
        self.selectedSegment = selectedSegment
        self.languages = languages
        self.selectedLanguageIndex = selectedLanguageIndex
        self.isDialogueBoostOn = isDialogueBoostOn
        self.isReduceLoudSoundsOn = isReduceLoudSoundsOn
        self.focusTarget = focusTarget
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSAudioSubtitlesConfig {
        var rng = SeededRNG(seed: seed)
        let seg = Int(rng.next() % 2)
        let langs: [(String, String?)] = seg == 0 ? [
            ("Off", nil),
            ("English [CC]", "CC"),
            ("Spanish", nil),
            ("French", nil),
            ("German", nil),
            ("Italian", nil)
        ] : [
            ("English (Original)", "Dolby Atmos"),
            ("English (Audio Description)", "AD"),
            ("Spanish (Latin America)", "5.1"),
            ("French", "5.1"),
            ("German", "5.1")
        ]

        let selLang = Int(rng.next() % UInt64(langs.count))
        let targetChoice = rng.next() % 10
        let target: AudioSubtitlesFocusTarget
        if targetChoice == 0 {
            target = .segment
        } else if targetChoice == 1 {
            target = .dialogueBoost
        } else if targetChoice == 2 {
            target = .reduceLoud
        } else {
            target = .language(Int(rng.next() % UInt64(langs.count)))
        }

        return tvOSAudioSubtitlesConfig(
            selectedSegment: seg,
            languages: langs,
            selectedLanguageIndex: selLang,
            isDialogueBoostOn: (rng.next() % 2 == 0),
            isReduceLoudSoundsOn: (rng.next() % 2 == 0),
            focusTarget: target
        )
    }
}

// MARK: - tvOSAudioSubtitlesTemplate View

public struct tvOSAudioSubtitlesTemplate: View {
    public let config: tvOSAudioSubtitlesConfig

    public init(config: tvOSAudioSubtitlesConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            // Video background (dimmed)
            Color.black.opacity(0.82).ignoresSafeArea()

            // Centered Audio & Subtitles Panel Card
            VStack(spacing: 24) {
                // Segmented Selector (Subtitles / Audio)
                let isSegFoc: Bool = {
                    if case .segment = config.focusTarget { return true }
                    return false
                }()

                HStack(spacing: 0) {
                    Text("Subtitles")
                        .font(.system(size: 22, weight: config.selectedSegment == 0 ? .bold : .medium))
                        .foregroundColor(config.selectedSegment == 0 ? (isSegFoc ? .white : .black) : (isSegFoc ? .black.opacity(0.6) : .white.opacity(0.7)))
                        .frame(maxWidth: .infinity)
                        .frame(height: 52)
                        .background(config.selectedSegment == 0 ? (isSegFoc ? Color.black : Color.white) : Color.clear)
                        .cornerRadius(12)

                    Text("Audio")
                        .font(.system(size: 22, weight: config.selectedSegment == 1 ? .bold : .medium))
                        .foregroundColor(config.selectedSegment == 1 ? (isSegFoc ? .white : .black) : (isSegFoc ? .black.opacity(0.6) : .white.opacity(0.7)))
                        .frame(maxWidth: .infinity)
                        .frame(height: 52)
                        .background(config.selectedSegment == 1 ? (isSegFoc ? Color.black : Color.white) : Color.clear)
                        .cornerRadius(12)
                }
                .padding(4)
                .frame(width: 640)
                .background(isSegFoc ? Color.white : Color.white.opacity(0.12))
                .cornerRadius(16)
                .scaleEffect(isSegFoc ? 1.03 : 1.0)
                .shadow(color: isSegFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                .captureFrame(id: isSegFoc ? "segmentedControl_panel_tabs_focused" : "segmentedControl_panel_tabs_unfocused")

                // Language Option List
                VStack(spacing: 8) {
                    ForEach(Array(config.languages.enumerated()), id: \.offset) { idx, lang in
                        let isRowFoc: Bool = {
                            if case .language(let lIdx) = config.focusTarget, lIdx == idx { return true }
                            return false
                        }()
                        let isSelected = (idx == config.selectedLanguageIndex)

                        HStack(spacing: 16) {
                            Text(lang.name)
                                .font(.system(size: 22, weight: (isRowFoc || isSelected) ? .bold : .medium))
                                .foregroundColor(isRowFoc ? .black : .white)
                                .captureFrame(id: "label_lang_name_\(idx)")

                            if let badge = lang.badge {
                                Text(badge)
                                    .font(.system(size: 14, weight: .bold))
                                    .foregroundColor(isRowFoc ? .black.opacity(0.8) : .white.opacity(0.8))
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 2)
                                    .background(isRowFoc ? Color.black.opacity(0.15) : Color.white.opacity(0.2))
                                    .cornerRadius(6)
                            }

                            Spacer()

                            if isSelected {
                                Image(systemName: "checkmark")
                                    .font(.system(size: 20, weight: .bold))
                                    .foregroundColor(isRowFoc ? .black : .white)
                                    .captureFrame(id: "imageView_checkmark_\(idx)")
                            }
                        }
                        .padding(.horizontal, 24)
                        .frame(width: 640, height: 60)
                        .background(isRowFoc ? Color.white : (isSelected ? Color.white.opacity(0.15) : Color.white.opacity(0.06)))
                        .cornerRadius(14)
                        .scaleEffect(isRowFoc ? 1.02 : 1.0)
                        .shadow(color: isRowFoc ? Color.white.opacity(0.4) : Color.clear, radius: 10)
                        .captureFrame(id: isRowFoc ? "listRow_lang_\(idx)_focused" : "listRow_lang_\(idx)_unfocused")
                    }
                }

                // Audio Enhancement Toggles
                VStack(spacing: 8) {
                    // Enhance Dialogue
                    let isDiagFoc: Bool = {
                        if case .dialogueBoost = config.focusTarget { return true }
                        return false
                    }()
                    HStack {
                        Text("Enhance Dialogue")
                            .font(.system(size: 20, weight: isDiagFoc ? .bold : .medium))
                            .foregroundColor(isDiagFoc ? .black : .white)
                            .captureFrame(id: "label_dialogue_title")
                        Spacer()
                        Toggle("", isOn: .constant(config.isDialogueBoostOn))
                            .labelsHidden()
                            .captureFrame(id: isDiagFoc ? "toggle_enhance_dialogue_focused" : "toggle_enhance_dialogue_unfocused")
                    }
                    .padding(.horizontal, 24)
                    .frame(width: 640, height: 60)
                    .background(isDiagFoc ? Color.white : Color.white.opacity(0.06))
                    .cornerRadius(14)
                    .scaleEffect(isDiagFoc ? 1.02 : 1.0)
                    .shadow(color: isDiagFoc ? Color.white.opacity(0.4) : Color.clear, radius: 10)
                    .captureFrame(id: isDiagFoc ? "listRow_dialogue_focused" : "listRow_dialogue_unfocused")

                    // Reduce Loud Sounds
                    let isLoudFoc: Bool = {
                        if case .reduceLoud = config.focusTarget { return true }
                        return false
                    }()
                    HStack {
                        Text("Reduce Loud Sounds")
                            .font(.system(size: 20, weight: isLoudFoc ? .bold : .medium))
                            .foregroundColor(isLoudFoc ? .black : .white)
                            .captureFrame(id: "label_reduce_loud_title")
                        Spacer()
                        Toggle("", isOn: .constant(config.isReduceLoudSoundsOn))
                            .labelsHidden()
                            .captureFrame(id: isLoudFoc ? "toggle_reduce_loud_focused" : "toggle_reduce_loud_unfocused")
                    }
                    .padding(.horizontal, 24)
                    .frame(width: 640, height: 60)
                    .background(isLoudFoc ? Color.white : Color.white.opacity(0.06))
                    .cornerRadius(14)
                    .scaleEffect(isLoudFoc ? 1.02 : 1.0)
                    .shadow(color: isLoudFoc ? Color.white.opacity(0.4) : Color.clear, radius: 10)
                    .captureFrame(id: isLoudFoc ? "listRow_reduce_loud_focused" : "listRow_reduce_loud_unfocused")
                }
            }
            .padding(32)
            .background(Color(red: 0.14, green: 0.14, blue: 0.18))
            .cornerRadius(28)
            .shadow(color: Color.black.opacity(0.7), radius: 36)
            .captureFrame(id: "popover_audio_subtitles_card")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}
