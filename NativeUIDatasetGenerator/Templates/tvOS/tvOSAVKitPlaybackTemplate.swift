// tvOSAVKitPlaybackTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised AVKit playback transport bar template for tvOS OS UI detection (TASK-6b-E4).
// Models full-screen media playback chrome: timeline scrubber slider, elapsed/remaining labels,
// play/pause/skip buttons, audio/subtitle selectors, and "Skip Intro" pill overlays.
//
// Annotated elements:
//   toolbar         — bottom playback transport bar overlay container
//   slider          — timeline scrubber slider
//   progressView    — buffered playback range indicator
//   primaryButton   — Play/Pause toggle button
//   secondaryButton — Skip 10s Back, Skip 10s Forward, Audio/Subtitles button, Skip Intro pill
//   label           — media title, episode info, elapsed time ("24:18"), remaining time ("-32:42")
//   imageView       — transport icons, channel badge, rating bug

import SwiftUI

// MARK: - tvOSAVKitPlaybackConfig

public struct tvOSAVKitPlaybackConfig: Sendable {
    public var mediaTitle: String
    public var episodeTitle: String
    public var elapsedTime: String
    public var remainingTime: String
    public var progressFraction: Double // 0.0 .. 1.0
    public var isPlaying: Bool
    public var hasSkipIntroPill: Bool
    public var focusedControl: PlaybackFocusTarget // 0: scrubber, 1: skipBack, 2: play, 3: skipForward, 4: audioSubtitles, 5: skipIntro
    public var videoHue: Double

    public enum PlaybackFocusTarget: Int, Sendable {
        case scrubber = 0
        case skipBack = 1
        case play = 2
        case skipForward = 3
        case audioSubtitles = 4
        case skipIntro = 5
    }

    public init(
        mediaTitle: String = "Severance",
        episodeTitle: String = "S1:E4 • The You You Are",
        elapsedTime: String = "24:18",
        remainingTime: String = "-32:42",
        progressFraction: Double = 0.42,
        isPlaying: Bool = true,
        hasSkipIntroPill: Bool = true,
        focusedControl: PlaybackFocusTarget = .play,
        videoHue: Double = 0.6
    ) {
        self.mediaTitle = mediaTitle
        self.episodeTitle = episodeTitle
        self.elapsedTime = elapsedTime
        self.remainingTime = remainingTime
        self.progressFraction = progressFraction
        self.isPlaying = isPlaying
        self.hasSkipIntroPill = hasSkipIntroPill
        self.focusedControl = focusedControl
        self.videoHue = videoHue
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSAVKitPlaybackConfig {
        var rng = SeededRNG(seed: seed)
        let titles = ["Severance", "Ted Lasso", "Foundation", "The Morning Show", "Silo", "Slow Horses", "Monarch"]
        let episodes = ["S1:E1 • Good News About Hell", "S1:E4 • The You You Are", "S2:E7 • Defiant Jazz", "S1:E9 • The We We Are"]

        let title = titles[Int(rng.next() % UInt64(titles.count))]
        let ep = episodes[Int(rng.next() % UInt64(episodes.count))]
        let frac = Double((rng.next() % 75) + 15) / 100.0
        let hasSkip = (rng.next() % 2 == 0)

        let targetRaw = Int(rng.next() % (hasSkip ? 6 : 5))
        let focus = PlaybackFocusTarget(rawValue: targetRaw) ?? .play
        let hue = Double(rng.next() % 1000) / 1000.0

        return tvOSAVKitPlaybackConfig(
            mediaTitle: title,
            episodeTitle: ep,
            elapsedTime: "18:42",
            remainingTime: "-34:10",
            progressFraction: frac,
            isPlaying: true,
            hasSkipIntroPill: hasSkip,
            focusedControl: focus,
            videoHue: hue
        )
    }
}

// MARK: - tvOSAVKitPlaybackTemplate View

public struct tvOSAVKitPlaybackTemplate: View {
    public let config: tvOSAVKitPlaybackConfig

    public init(config: tvOSAVKitPlaybackConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack(alignment: .bottom) {
            // Simulated video content frame (gradient cinematic scene)
            LinearGradient(
                colors: [
                    Color(hue: config.videoHue, saturation: 0.8, brightness: 0.3),
                    Color(hue: (config.videoHue + 0.1).truncatingRemainder(dividingBy: 1.0), saturation: 0.5, brightness: 0.15)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            ).ignoresSafeArea()

            // Dimming gradient for transport overlay readability
            LinearGradient(
                colors: [Color.clear, Color.black.opacity(0.85)],
                startPoint: .center,
                endPoint: .bottom
            ).ignoresSafeArea()

            // Top Header: Title & Info
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(config.mediaTitle)
                            .font(.system(size: 34, weight: .bold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_media_title")

                        Text(config.episodeTitle)
                            .font(.system(size: 22, weight: .medium))
                            .foregroundColor(.white.opacity(0.75))
                            .captureFrame(id: "label_episode_title")
                    }
                    Spacer()

                    // Rating Bug
                    Text("TV-MA")
                        .font(.system(size: 16, weight: .heavy))
                        .foregroundColor(.white.opacity(0.9))
                        .padding(.horizontal, 10)
                        .padding(.vertical, 4)
                        .background(Color.black.opacity(0.5))
                        .cornerRadius(6)
                        .overlay(RoundedRectangle(cornerRadius: 6).stroke(Color.white.opacity(0.3), lineWidth: 1))
                        .captureFrame(id: "label_rating_bug")
                }
                .padding(.horizontal, 90)
                .padding(.top, 60)

                Spacer()
            }

            // Skip Intro Pill Button (floating bottom-right above transport bar)
            if config.hasSkipIntroPill {
                let isSkipIntroFoc = (config.focusedControl == .skipIntro)
                VStack {
                    Spacer()
                    HStack {
                        Spacer()
                        HStack(spacing: 10) {
                            Text("Skip Intro")
                                .font(.system(size: 22, weight: .bold))
                            Image(systemName: "forward.end.fill")
                                .font(.system(size: 18))
                        }
                        .foregroundColor(isSkipIntroFoc ? .black : .white)
                        .padding(.horizontal, 28)
                        .padding(.vertical, 14)
                        .background(isSkipIntroFoc ? Color.white : Color.black.opacity(0.6))
                        .cornerRadius(24)
                        .overlay(RoundedRectangle(cornerRadius: 24).stroke(Color.white.opacity(0.4), lineWidth: 1))
                        .scaleEffect(isSkipIntroFoc ? 1.08 : 1.0)
                        .shadow(color: isSkipIntroFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                        .captureFrame(id: isSkipIntroFoc ? "secondaryButton_skip_intro_focused" : "secondaryButton_skip_intro_unfocused")
                        .padding(.trailing, 90)
                        .padding(.bottom, 220)
                    }
                }
            }

            // Bottom Transport Bar Container
            VStack(spacing: 24) {
                // Scrubber Section: Elapsed + Slider + Remaining
                let isScrubFoc = (config.focusedControl == .scrubber)
                HStack(spacing: 24) {
                    Text(config.elapsedTime)
                        .font(.system(size: 22, weight: .semibold, design: .monospaced))
                        .foregroundColor(.white.opacity(0.85))
                        .frame(width: 90, alignment: .trailing)
                        .captureFrame(id: "label_elapsed_time")

                    // Scrubber Slider Track
                    GeometryReader { geo in
                        ZStack(alignment: .leading) {
                            // Track background
                            Capsule()
                                .fill(Color.white.opacity(0.25))
                                .frame(height: isScrubFoc ? 14 : 8)

                            // Buffered progress
                            Capsule()
                                .fill(Color.white.opacity(0.4))
                                .frame(width: geo.size.width * CGFloat(min(1.0, config.progressFraction + 0.2)), height: isScrubFoc ? 14 : 8)
                                .captureFrame(id: "progressView_buffer_bar")

                            // Elapsed progress fill
                            Capsule()
                                .fill(isScrubFoc ? Color.white : Color.white.opacity(0.9))
                                .frame(width: geo.size.width * CGFloat(config.progressFraction), height: isScrubFoc ? 14 : 8)

                            // Scrubber Thumb (visible when focused)
                            if isScrubFoc {
                                Circle()
                                    .fill(Color.white)
                                    .frame(width: 24, height: 24)
                                    .shadow(color: .white.opacity(0.8), radius: 8)
                                    .offset(x: geo.size.width * CGFloat(config.progressFraction) - 12)
                            }
                        }
                    }
                    .frame(height: 24)
                    .scaleEffect(isScrubFoc ? 1.02 : 1.0)
                    .captureFrame(id: isScrubFoc ? "slider_timeline_scrubber_focused" : "slider_timeline_scrubber_unfocused")

                    Text(config.remainingTime)
                        .font(.system(size: 22, weight: .semibold, design: .monospaced))
                        .foregroundColor(.white.opacity(0.85))
                        .frame(width: 90, alignment: .leading)
                        .captureFrame(id: "label_remaining_time")
                }

                // Transport Control Buttons
                HStack(spacing: 36) {
                    // Skip 10s Back
                    let isBackFoc = (config.focusedControl == .skipBack)
                    Image(systemName: "gobackward.10")
                        .font(.system(size: 32, weight: .semibold))
                        .foregroundColor(isBackFoc ? .black : .white)
                        .frame(width: 72, height: 72)
                        .background(isBackFoc ? Color.white : Color.white.opacity(0.15))
                        .cornerRadius(20)
                        .scaleEffect(isBackFoc ? 1.1 : 1.0)
                        .shadow(color: isBackFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                        .captureFrame(id: isBackFoc ? "secondaryButton_skip_back_focused" : "secondaryButton_skip_back_unfocused")

                    // Play / Pause (Primary)
                    let isPlayFoc = (config.focusedControl == .play)
                    Image(systemName: config.isPlaying ? "pause.fill" : "play.fill")
                        .font(.system(size: 38, weight: .bold))
                        .foregroundColor(isPlayFoc ? .black : .white)
                        .frame(width: 88, height: 88)
                        .background(isPlayFoc ? Color.white : Color.white.opacity(0.2))
                        .cornerRadius(24)
                        .scaleEffect(isPlayFoc ? 1.12 : 1.0)
                        .shadow(color: isPlayFoc ? Color.white.opacity(0.5) : Color.clear, radius: 16)
                        .captureFrame(id: isPlayFoc ? "primaryButton_play_pause_focused" : "primaryButton_play_pause_unfocused")

                    // Skip 10s Forward
                    let isFwdFoc = (config.focusedControl == .skipForward)
                    Image(systemName: "goforward.10")
                        .font(.system(size: 32, weight: .semibold))
                        .foregroundColor(isFwdFoc ? .black : .white)
                        .frame(width: 72, height: 72)
                        .background(isFwdFoc ? Color.white : Color.white.opacity(0.15))
                        .cornerRadius(20)
                        .scaleEffect(isFwdFoc ? 1.1 : 1.0)
                        .shadow(color: isFwdFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                        .captureFrame(id: isFwdFoc ? "secondaryButton_skip_forward_focused" : "secondaryButton_skip_forward_unfocused")

                    // Audio & Subtitles Button
                    let isSubFoc = (config.focusedControl == .audioSubtitles)
                    Image(systemName: "captions.bubble.fill")
                        .font(.system(size: 30, weight: .semibold))
                        .foregroundColor(isSubFoc ? .black : .white)
                        .frame(width: 72, height: 72)
                        .background(isSubFoc ? Color.white : Color.white.opacity(0.15))
                        .cornerRadius(20)
                        .scaleEffect(isSubFoc ? 1.1 : 1.0)
                        .shadow(color: isSubFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                        .captureFrame(id: isSubFoc ? "secondaryButton_subtitles_focused" : "secondaryButton_subtitles_unfocused")
                }
            }
            .padding(.horizontal, 90)
            .padding(.bottom, 60)
            .frame(maxWidth: .infinity)
            .captureFrame(id: "toolbar_transport_controls")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}
