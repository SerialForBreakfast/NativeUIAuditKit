// tvOSLiveBroadcastHUDTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS Live Sports & Broadcast HUD template for OS UI detection.
// Models Apple TV live sports and television overlays:
// red "LIVE" badge, live score card, channel switcher rail, and multi-view/stats segmented control.
//
// Annotated elements:
//   label            — "LIVE" badge, team names, score readouts, channel title
//   segmentedControl — view mode switcher (Scores, Stats, Camera Angles)
//   collectionItem   — live channel switcher rail cards
//   toolbar          — bottom broadcast controls container
//   imageView        — broadcaster logo / team emblem

import SwiftUI

// MARK: - tvOSLiveBroadcastHUDConfig

public struct tvOSLiveBroadcastHUDConfig: Sendable {
    public var homeTeam: String
    public var awayTeam: String
    public var homeScore: Int
    public var awayScore: Int
    public var gameClock: String
    public var selectedSegment: Int
    public var focusedChannelIndex: Int
    public var bgHue: Double

    public init(
        homeTeam: String = "LAD",
        awayTeam: String = "NYY",
        homeScore: Int = 4,
        awayScore: Int = 3,
        gameClock: String = "Top 8th • 1 Out",
        selectedSegment: Int = 0,
        focusedChannelIndex: Int = 0,
        bgHue: Double = 0.58
    ) {
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.homeScore = homeScore
        self.awayScore = awayScore
        self.gameClock = gameClock
        self.selectedSegment = selectedSegment
        self.focusedChannelIndex = focusedChannelIndex
        self.bgHue = bgHue
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSLiveBroadcastHUDConfig {
        var rng = SeededRNG(seed: seed)
        let matchups = [
            ("LAD", "NYY", 4, 3, "Top 8th • 1 Out"),
            ("BOS", "PHI", 2, 5, "Bottom 6th • 2 Outs"),
            ("GSW", "LAL", 108, 102, "4th Qtr • 2:45"),
            ("MIA", "BOS", 89, 94, "3rd Qtr • 0:12")
        ]
        let m = matchups[Int(rng.next() % UInt64(matchups.count))]
        return tvOSLiveBroadcastHUDConfig(
            homeTeam: m.0,
            awayTeam: m.1,
            homeScore: m.2,
            awayScore: m.3,
            gameClock: m.4,
            selectedSegment: Int(rng.next() % 3),
            focusedChannelIndex: Int(rng.next() % 4),
            bgHue: Double(rng.next() % 1000) / 1000.0
        )
    }
}

// MARK: - tvOSLiveBroadcastHUDTemplate View

public struct tvOSLiveBroadcastHUDTemplate: View {
    public let config: tvOSLiveBroadcastHUDConfig

    public init(config: tvOSLiveBroadcastHUDConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack(alignment: .topLeading) {
            // Simulated live broadcast video
            LinearGradient(
                colors: [Color(hue: config.bgHue, saturation: 0.6, brightness: 0.2), Color.black],
                startPoint: .top,
                endPoint: .bottom
            ).ignoresSafeArea()

            // Top-Left Live Score Bug
            HStack(spacing: 20) {
                // Red LIVE Badge
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

                // Score Display
                HStack(spacing: 16) {
                    Text("\(config.homeTeam) \(config.homeScore)")
                        .font(.system(size: 26, weight: .heavy))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_home_score")

                    Text("-")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.white.opacity(0.6))

                    Text("\(config.awayScore) \(config.awayTeam)")
                        .font(.system(size: 26, weight: .heavy))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_away_score")
                }

                // Clock
                Text(config.gameClock)
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

            // Bottom Rail & Controls
            VStack {
                Spacer()

                // Segmented Mode Switcher (Stats, Multiview, Audio)
                HStack(spacing: 0) {
                    let segments = ["Game Cast", "Box Score", "Multiview"]
                    ForEach(Array(segments.enumerated()), id: \.offset) { idx, seg in
                        let isSel = (idx == config.selectedSegment)
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

                // Live Channel Switcher Rail (collectionItem)
                HStack(spacing: 32) {
                    ForEach(0..<4) { idx in
                        let isFoc = (idx == config.focusedChannelIndex)

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
                            .captureFrame(id: isFoc ? "collectionItem_channel_\(idx)_focused" : "collectionItem_channel_\(idx)_unfocused")

                            Text("Channel \(idx + 1)")
                                .font(.system(size: 20, weight: isFoc ? .bold : .medium))
                                .foregroundColor(isFoc ? .white : .white.opacity(0.7))
                                .captureFrame(id: "label_channel_name_\(idx)")
                        }
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
