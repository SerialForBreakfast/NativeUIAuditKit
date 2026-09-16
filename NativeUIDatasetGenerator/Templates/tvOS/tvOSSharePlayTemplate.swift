// tvOSSharePlayTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised SharePlay & FaceTime group activity template for tvOS OS UI detection (TASK-6b-E5).
// Models synchronized playback chrome, FaceTime participant status, and group controls.
//
// Annotated elements:
//   sheet             — the floating SharePlay / FaceTime banner card
//   collectionItem    — participant avatar circles with speaking halos
//   primaryButton     — "Join Together", "Start for Everyone"
//   secondaryButton   — "Mute Microphone", "Camera Switch"
//   destructiveButton — "End for Everyone"
//   cancelAction      — "Leave SharePlay"
//   label             — group status, participant names, call duration
//   imageView         — FaceTime icons, audio waves, SharePlay badge

import SwiftUI

// MARK: - tvOSSharePlayConfig

public struct tvOSSharePlayConfig: Sendable {
    public var groupTitle: String
    public var participants: [(name: String, isSpeaking: Bool, hue: Double)]
    public var callDuration: String
    public var isMuted: Bool
    public var focusedAction: SharePlayFocusAction // 0: primary/join, 1: mute, 2: leave, 3: endForAll, 4..N: avatar
    public var bgHue: Double

    public enum SharePlayFocusAction: Int, Sendable {
        case joinOrResume = 0
        case mute = 1
        case leave = 2
        case endForAll = 3
        case participant0 = 4
        case participant1 = 5
        case participant2 = 6
    }

    public init(
        groupTitle: String = "Movie Night with Family",
        participants: [(name: String, isSpeaking: Bool, hue: Double)] = [
            ("Alex", true, 0.2),
            ("Sarah", false, 0.55),
            ("Mom", false, 0.8)
        ],
        callDuration: String = "32:15",
        isMuted: Bool = false,
        focusedAction: SharePlayFocusAction = .joinOrResume,
        bgHue: Double = 0.65
    ) {
        self.groupTitle = groupTitle
        self.participants = participants
        self.callDuration = callDuration
        self.isMuted = isMuted
        self.focusedAction = focusedAction
        self.bgHue = bgHue
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSSharePlayConfig {
        var rng = SeededRNG(seed: seed)
        let titles = ["Movie Night with Friends", "Family Watch Party", "Workout Session", "Ted Lasso S3 Ep 4"]
        let names = ["Alex", "Sarah", "Liam", "Emma", "Noah", "Olivia", "Lucas"]

        var partList: [(String, Bool, Double)] = []
        let pCount = Int(rng.next() % 3) + 2 // 2 to 4 participants
        for i in 0..<pCount {
            let n = names[Int(rng.next() % UInt64(names.count))]
            let speaking = (i == 0 && rng.next() % 2 == 0)
            let hue = Double(rng.next() % 1000) / 1000.0
            partList.append((n, speaking, hue))
        }

        let focRaw = Int(rng.next() % 4)
        let action = SharePlayFocusAction(rawValue: focRaw) ?? .joinOrResume
        let hue = Double(rng.next() % 1000) / 1000.0

        return tvOSSharePlayConfig(
            groupTitle: titles[Int(rng.next() % UInt64(titles.count))],
            participants: partList,
            callDuration: "24:10",
            isMuted: (rng.next() % 2 == 0),
            focusedAction: action,
            bgHue: hue
        )
    }
}

// MARK: - tvOSSharePlayTemplate View

public struct tvOSSharePlayTemplate: View {
    public let config: tvOSSharePlayConfig

    public init(config: tvOSSharePlayConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack(alignment: .topTrailing) {
            // Underneath movie background with subtle dim
            LinearGradient(
                colors: [
                    Color(hue: config.bgHue, saturation: 0.7, brightness: 0.3),
                    Color.black
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            ).ignoresSafeArea()

            Color.black.opacity(0.45).ignoresSafeArea()

            // Floating SharePlay card overlay (top-right corner)
            VStack(alignment: .leading, spacing: 20) {
                // Header: SharePlay Badge & Duration
                HStack(spacing: 12) {
                    Image(systemName: "shareplay")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.green)
                        .captureFrame(id: "imageView_shareplay_icon")

                    VStack(alignment: .leading, spacing: 2) {
                        Text("SharePlay Active")
                            .font(.system(size: 20, weight: .bold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_shareplay_title")

                        Text(config.groupTitle)
                            .font(.system(size: 16))
                            .foregroundColor(.white.opacity(0.75))
                            .captureFrame(id: "label_group_title")
                    }

                    Spacer()

                    Text(config.callDuration)
                        .font(.system(size: 18, weight: .semibold, design: .monospaced))
                        .foregroundColor(.white.opacity(0.8))
                        .captureFrame(id: "label_call_duration")
                }

                // Participant Avatars Row
                HStack(spacing: 20) {
                    ForEach(Array(config.participants.enumerated()), id: \.offset) { idx, part in
                        let isAvatarFoc = (config.focusedAction.rawValue == 4 + idx)
                        VStack(spacing: 6) {
                            ZStack {
                                Circle()
                                    .fill(Color(hue: part.hue, saturation: 0.6, brightness: 0.6))
                                    .frame(width: 64, height: 64)

                                Text(String(part.name.prefix(1)))
                                    .font(.system(size: 26, weight: .bold))
                                    .foregroundColor(.white)

                                if part.isSpeaking {
                                    Circle()
                                        .stroke(Color.green, lineWidth: 3)
                                        .frame(width: 72, height: 72)
                                }
                            }
                            .scaleEffect(isAvatarFoc ? 1.15 : 1.0)
                            .shadow(color: isAvatarFoc ? Color.white.opacity(0.5) : Color.clear, radius: 10)
                            .captureFrame(id: isAvatarFoc ? "collectionItem_avatar_\(idx)_focused" : "collectionItem_avatar_\(idx)_unfocused")

                            Text(part.name)
                                .font(.system(size: 16, weight: .medium))
                                .foregroundColor(.white.opacity(0.85))
                                .captureFrame(id: "label_participant_\(idx)")
                        }
                    }
                }
                .padding(.vertical, 4)

                // Action Buttons
                HStack(spacing: 16) {
                    // Mute / Unmute
                    let isMuteFoc = (config.focusedAction == .mute)
                    Image(systemName: config.isMuted ? "mic.slash.fill" : "mic.fill")
                        .font(.system(size: 22, weight: .semibold))
                        .foregroundColor(isMuteFoc ? .black : (config.isMuted ? .red : .white))
                        .frame(width: 60, height: 60)
                        .background(isMuteFoc ? Color.white : Color.white.opacity(0.12))
                        .cornerRadius(18)
                        .scaleEffect(isMuteFoc ? 1.08 : 1.0)
                        .shadow(color: isMuteFoc ? Color.white.opacity(0.4) : Color.clear, radius: 10)
                        .captureFrame(id: isMuteFoc ? "secondaryButton_mute_focused" : "secondaryButton_mute_unfocused")

                    // Primary Play Together / Resume
                    let isJoinFoc = (config.focusedAction == .joinOrResume)
                    HStack(spacing: 10) {
                        Image(systemName: "play.fill")
                            .font(.system(size: 18))
                        Text("Play Together")
                            .font(.system(size: 20, weight: .bold))
                    }
                    .foregroundColor(isJoinFoc ? .black : .white)
                    .padding(.horizontal, 24)
                    .frame(height: 60)
                    .background(isJoinFoc ? Color.white : Color.green.opacity(0.4))
                    .cornerRadius(18)
                    .scaleEffect(isJoinFoc ? 1.06 : 1.0)
                    .shadow(color: isJoinFoc ? Color.white.opacity(0.4) : Color.clear, radius: 10)
                    .captureFrame(id: isJoinFoc ? "primaryButton_play_together_focused" : "primaryButton_play_together_unfocused")

                    // Leave SharePlay
                    let isLeaveFoc = (config.focusedAction == .leave)
                    Text("Leave")
                        .font(.system(size: 20, weight: .semibold))
                        .foregroundColor(isLeaveFoc ? .black : .white)
                        .padding(.horizontal, 20)
                        .frame(height: 60)
                        .background(isLeaveFoc ? Color.white : Color.white.opacity(0.12))
                        .cornerRadius(18)
                        .scaleEffect(isLeaveFoc ? 1.06 : 1.0)
                        .shadow(color: isLeaveFoc ? Color.white.opacity(0.4) : Color.clear, radius: 10)
                        .captureFrame(id: isLeaveFoc ? "cancelAction_leave_focused" : "cancelAction_leave_unfocused")

                    // End for Everyone (Destructive)
                    let isEndFoc = (config.focusedAction == .endForAll)
                    Image(systemName: "phone.down.fill")
                        .font(.system(size: 22))
                        .foregroundColor(isEndFoc ? .white : .red)
                        .frame(width: 60, height: 60)
                        .background(isEndFoc ? Color.red : Color.red.opacity(0.2))
                        .cornerRadius(18)
                        .scaleEffect(isEndFoc ? 1.08 : 1.0)
                        .shadow(color: isEndFoc ? Color.red.opacity(0.6) : Color.clear, radius: 10)
                        .captureFrame(id: isEndFoc ? "destructiveButton_end_all_focused" : "destructiveButton_end_all_unfocused")
                }
            }
            .padding(28)
            .frame(width: 620)
            .background(Color(red: 0.12, green: 0.12, blue: 0.16))
            .cornerRadius(24)
            .shadow(color: Color.black.opacity(0.7), radius: 28)
            .padding(.top, 60)
            .padding(.trailing, 80)
            .captureFrame(id: "sheet_shareplay_card")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}
