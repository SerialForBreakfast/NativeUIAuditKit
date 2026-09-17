// tvOSNowPlayingLyricsTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS Music Now Playing & Real-time Lyrics template for OS UI detection.
// Models Apple Music full-screen synchronized lyrics view on tvOS:
// active lyric highlighting, album artwork, playback scrubber slider, and control buttons.
//
// Annotated elements:
//   listRow         — synchronized lyrics line rows (focused/active vs unfocused)
//   label           — lyrics text, song title, artist name, duration timestamps
//   slider          — playback scrubber bar
//   imageView       — album cover artwork thumbnail
//   secondaryButton — playback control toggles (lyrics, airplay, queue)

import SwiftUI

// MARK: - tvOSNowPlayingLyricsConfig

public struct tvOSNowPlayingLyricsConfig: Sendable {
    public var songTitle: String
    public var artistName: String
    public var lyricsLines: [String]
    public var activeLyricIndex: Int
    public var progress: Double // 0.0 .. 1.0
    public var bgHue: Double

    public init(
        songTitle: String = "Midnight City",
        artistName: String = "M83 • Hurry Up, We're Dreaming",
        lyricsLines: [String] = [
            "Waiting in a car",
            "Waiting for a ride in the dark",
            "The night city grows",
            "Look and see her eyes, they keep the score",
            "The city is my church",
            "It wraps me in the blinding twilight"
        ],
        activeLyricIndex: Int = 2,
        progress: Double = 0.45,
        bgHue: Double = 0.72
    ) {
        self.songTitle = songTitle
        self.artistName = artistName
        self.lyricsLines = lyricsLines
        self.activeLyricIndex = activeLyricIndex
        self.progress = progress
        self.bgHue = bgHue
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSNowPlayingLyricsConfig {
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

        return tvOSNowPlayingLyricsConfig(
            songTitle: s.0,
            artistName: s.1,
            lyricsLines: lines,
            activeLyricIndex: activeIdx,
            progress: prog,
            bgHue: Double(rng.next() % 1000) / 1000.0
        )
    }
}

// MARK: - tvOSNowPlayingLyricsTemplate View

public struct tvOSNowPlayingLyricsTemplate: View {
    public let config: tvOSNowPlayingLyricsConfig

    public init(config: tvOSNowPlayingLyricsConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            // Dynamic colorful animated gradient background
            LinearGradient(
                colors: [
                    Color(hue: config.bgHue, saturation: 0.7, brightness: 0.25),
                    Color(hue: (config.bgHue + 0.2).truncatingRemainder(dividingBy: 1.0), saturation: 0.6, brightness: 0.15),
                    Color.black
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            ).ignoresSafeArea()

            HStack(spacing: 80) {
                // Left Column: Album Art & Track Info
                VStack(alignment: .leading, spacing: 28) {
                    Spacer()

                    // Album Artwork
                    ZStack {
                        RoundedRectangle(cornerRadius: 24)
                            .fill(LinearGradient(
                                colors: [Color(hue: config.bgHue, saturation: 0.8, brightness: 0.6), Color.black.opacity(0.8)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ))
                        Image(systemName: "music.note")
                            .font(.system(size: 96))
                            .foregroundColor(.white.opacity(0.9))
                    }
                    .frame(width: 440, height: 440)
                    .shadow(color: Color.black.opacity(0.6), radius: 30)
                    .captureFrame(id: "imageView_album_art")

                    // Track Title & Artist
                    VStack(alignment: .leading, spacing: 10) {
                        Text(config.songTitle)
                            .font(.system(size: 38, weight: .bold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_song_title")

                        Text(config.artistName)
                            .font(.system(size: 24))
                            .foregroundColor(.white.opacity(0.7))
                            .captureFrame(id: "label_artist_name")
                    }

                    // Scrubber Bar (slider)
                    VStack(spacing: 12) {
                        GeometryReader { geo in
                            ZStack(alignment: .leading) {
                                RoundedRectangle(cornerRadius: 4)
                                    .fill(Color.white.opacity(0.2))
                                    .frame(height: 8)

                                RoundedRectangle(cornerRadius: 4)
                                    .fill(Color.white)
                                    .frame(width: geo.size.width * CGFloat(config.progress), height: 8)

                                Circle()
                                    .fill(Color.white)
                                    .frame(width: 20, height: 20)
                                    .offset(x: geo.size.width * CGFloat(config.progress) - 10)
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

                    // Controls Row
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

                // Right Column: Synchronized Lyrics List
                VStack(alignment: .leading, spacing: 32) {
                    Spacer()

                    ForEach(Array(config.lyricsLines.enumerated()), id: \.offset) { idx, line in
                        let isActive = (idx == config.activeLyricIndex)

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
