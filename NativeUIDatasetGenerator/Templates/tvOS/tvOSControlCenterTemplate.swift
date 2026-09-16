// tvOSControlCenterTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS Control Center template for OS UI detection (TASK-6b-E2).
// Models the right-hand slide-out drawer on Apple TV with user switcher, audio routing,
// HomeKit cameras/scenes, volume sliders, and quick toggles.
//
// Annotated elements:
//   sidebar         — the slide-out Control Center drawer container
//   collectionItem  — user profile avatars, HomeKit camera cards, scene buttons
//   primaryButton   — quick action buttons (AirPlay, Sleep)
//   secondaryButton — connectivity toggles (Wi-Fi, Bluetooth, Game Controller)
//   toggle          — Do Not Disturb, Game Mode
//   slider          — volume control slider
//   listRow         — audio output destination items
//   label           — user name, time, section headers, card labels
//   imageView       — profile avatars, icons, camera previews

import SwiftUI

// MARK: - tvOSControlCenterConfig

public struct tvOSControlCenterConfig: Sendable {
    public var userName: String
    public var timeString: String
    public var audioDeviceName: String
    public var volumeLevel: Double // 0.0 .. 1.0
    public var isDNDOn: Bool
    public var isAirPlayActive: Bool
    public var homeKitScenes: [String]
    public var focusedElementIndex: Int // 0: User, 1: Sleep, 2: Audio, 3: Volume, 4: DND, 5: Wi-Fi, 6..N: HomeKit
    public var bgHue: Double

    public init(
        userName: String = "Joseph",
        timeString: String = "9:41 PM",
        audioDeviceName: String = "Living Room HomePod",
        volumeLevel: Double = 0.65,
        isDNDOn: Bool = false,
        isAirPlayActive: Bool = true,
        homeKitScenes: [String] = ["Movie Night", "Relax", "All Off"],
        focusedElementIndex: Int = 2,
        bgHue: Double = 0.1
    ) {
        self.userName = userName
        self.timeString = timeString
        self.audioDeviceName = audioDeviceName
        self.volumeLevel = volumeLevel
        self.isDNDOn = isDNDOn
        self.isAirPlayActive = isAirPlayActive
        self.homeKitScenes = homeKitScenes
        self.focusedElementIndex = focusedElementIndex
        self.bgHue = bgHue
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSControlCenterConfig {
        var rng = SeededRNG(seed: seed)
        let names = ["Joseph", "Sarah", "Alex", "Family Room", "Guest"]
        let audioDevices = ["Living Room HomePod", "AirPods Pro", "Apple TV Speakers", "Bedroom HomePod mini"]
        let scenes = ["Movie Night", "Dim Lights", "All Off", "Late Night", "Party"]

        let name = names[Int(rng.next() % UInt64(names.count))]
        let device = audioDevices[Int(rng.next() % UInt64(audioDevices.count))]
        let dnd = (rng.next() % 2 == 0)
        let foc = Int(rng.next() % 8)
        let vol = Double((rng.next() % 80) + 20) / 100.0
        let hue = Double(rng.next() % 1000) / 1000.0

        return tvOSControlCenterConfig(
            userName: name,
            timeString: "09:41",
            audioDeviceName: device,
            volumeLevel: vol,
            isDNDOn: dnd,
            isAirPlayActive: true,
            homeKitScenes: [scenes[0], scenes[1], scenes[2]],
            focusedElementIndex: foc,
            bgHue: hue
        )
    }
}

// MARK: - tvOSControlCenterTemplate View

public struct tvOSControlCenterTemplate: View {
    public let config: tvOSControlCenterConfig

    public init(config: tvOSControlCenterConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack(alignment: .trailing) {
            // Background app view (dimmed by overlay)
            ZStack {
                Color(hue: config.bgHue, saturation: 0.5, brightness: 0.25).ignoresSafeArea()
                Color.black.opacity(0.65).ignoresSafeArea()
            }

            // Slide-out Control Center panel (right side, 680px wide)
            VStack(alignment: .leading, spacing: 20) {
                // Header: User Profile & Sleep Button
                HStack(spacing: 16) {
                    // Profile Chip
                    let isUserFoc = (config.focusedElementIndex == 0)
                    HStack(spacing: 14) {
                        Image(systemName: "person.crop.circle.fill")
                            .font(.system(size: 38))
                            .foregroundColor(isUserFoc ? .black : .white)
                            .captureFrame(id: "imageView_profile_avatar")
                        Text(config.userName)
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(isUserFoc ? .black : .white)
                            .captureFrame(id: "label_profile_name")
                    }
                    .padding(.horizontal, 18)
                    .frame(height: 64)
                    .background(isUserFoc ? Color.white : Color.white.opacity(0.12))
                    .cornerRadius(20)
                    .scaleEffect(isUserFoc ? 1.05 : 1.0)
                    .shadow(color: isUserFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                    .captureFrame(id: isUserFoc ? "collectionItem_profile_focused" : "collectionItem_profile_unfocused")

                    Spacer()

                    // Time Display
                    Text(config.timeString)
                        .font(.system(size: 26, weight: .semibold))
                        .foregroundColor(.white.opacity(0.9))
                        .captureFrame(id: "label_clock_time")

                    // Sleep Button
                    let isSleepFoc = (config.focusedElementIndex == 1)
                    Image(systemName: "power")
                        .font(.system(size: 22, weight: .bold))
                        .foregroundColor(isSleepFoc ? .red : .white)
                        .frame(width: 64, height: 64)
                        .background(isSleepFoc ? Color.white : Color.white.opacity(0.12))
                        .cornerRadius(20)
                        .scaleEffect(isSleepFoc ? 1.05 : 1.0)
                        .shadow(color: isSleepFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                        .captureFrame(id: isSleepFoc ? "cancelAction_sleep_focused" : "cancelAction_sleep_unfocused")
                }

                // Audio Output Destination Tile
                let isAudioFoc = (config.focusedElementIndex == 2)
                VStack(alignment: .leading, spacing: 10) {
                    HStack(spacing: 14) {
                        Image(systemName: "airplayaudio")
                            .font(.system(size: 28))
                            .foregroundColor(isAudioFoc ? .black : .white)
                            .captureFrame(id: "imageView_airplay_icon")
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Audio Destination")
                                .font(.system(size: 16))
                                .foregroundColor(isAudioFoc ? .black.opacity(0.7) : .white.opacity(0.6))
                                .captureFrame(id: "label_audio_header")
                            Text(config.audioDeviceName)
                                .font(.system(size: 22, weight: .bold))
                                .foregroundColor(isAudioFoc ? .black : .white)
                                .captureFrame(id: "label_audio_device")
                        }
                        Spacer()
                    }
                }
                .padding(20)
                .frame(maxWidth: .infinity)
                .background(isAudioFoc ? Color.white : Color.white.opacity(0.1))
                .cornerRadius(20)
                .scaleEffect(isAudioFoc ? 1.03 : 1.0)
                .shadow(color: isAudioFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                .captureFrame(id: isAudioFoc ? "listRow_audio_dest_focused" : "listRow_audio_dest_unfocused")

                // Volume Slider Tile
                let isVolFoc = (config.focusedElementIndex == 3)
                VStack(alignment: .leading, spacing: 10) {
                    HStack {
                        Image(systemName: "speaker.fill")
                            .font(.system(size: 20))
                            .foregroundColor(isVolFoc ? .black : .white)
                            .captureFrame(id: "imageView_vol_low")
                        Spacer()
                        Image(systemName: "speaker.wave.3.fill")
                            .font(.system(size: 20))
                            .foregroundColor(isVolFoc ? .black : .white)
                            .captureFrame(id: "imageView_vol_high")
                    }

                    // Simulated slider track
                    GeometryReader { geo in
                        ZStack(alignment: .leading) {
                            Capsule()
                                .fill(isVolFoc ? Color.black.opacity(0.2) : Color.white.opacity(0.2))
                                .frame(height: 12)
                            Capsule()
                                .fill(isVolFoc ? Color.black : Color.white)
                                .frame(width: geo.size.width * CGFloat(config.volumeLevel), height: 12)
                        }
                    }
                    .frame(height: 12)
                    .captureFrame(id: "slider_volume_control")
                }
                .padding(20)
                .frame(maxWidth: .infinity)
                .background(isVolFoc ? Color.white : Color.white.opacity(0.1))
                .cornerRadius(20)
                .scaleEffect(isVolFoc ? 1.03 : 1.0)
                .shadow(color: isVolFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                .captureFrame(id: isVolFoc ? "primaryButton_volume_tile_focused" : "primaryButton_volume_tile_unfocused")

                // Quick Settings Grid: DND & Wi-Fi
                HStack(spacing: 16) {
                    // DND Toggle Button
                    let isDNDFoc = (config.focusedElementIndex == 4)
                    HStack(spacing: 12) {
                        Image(systemName: config.isDNDOn ? "moon.fill" : "moon")
                            .font(.system(size: 22))
                            .captureFrame(id: "imageView_dnd_icon")
                        Text("Do Not Disturb")
                            .font(.system(size: 20, weight: .semibold))
                            .captureFrame(id: "label_dnd")
                    }
                    .foregroundColor(isDNDFoc ? .black : .white)
                    .padding(.horizontal, 16)
                    .frame(maxWidth: .infinity, maxHeight: 64)
                    .background(isDNDFoc ? Color.white : (config.isDNDOn ? Color.indigo.opacity(0.5) : Color.white.opacity(0.1)))
                    .cornerRadius(18)
                    .scaleEffect(isDNDFoc ? 1.04 : 1.0)
                    .shadow(color: isDNDFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                    .captureFrame(id: isDNDFoc ? "toggle_dnd_focused" : "toggle_dnd_unfocused")

                    // Wi-Fi Button
                    let isWifiFoc = (config.focusedElementIndex == 5)
                    HStack(spacing: 12) {
                        Image(systemName: "wifi")
                            .font(.system(size: 22))
                            .captureFrame(id: "imageView_wifi_icon")
                        Text("Wi-Fi")
                            .font(.system(size: 20, weight: .semibold))
                            .captureFrame(id: "label_wifi")
                    }
                    .foregroundColor(isWifiFoc ? .black : .white)
                    .padding(.horizontal, 16)
                    .frame(maxWidth: .infinity, maxHeight: 64)
                    .background(isWifiFoc ? Color.white : Color.blue.opacity(0.5))
                    .cornerRadius(18)
                    .scaleEffect(isWifiFoc ? 1.04 : 1.0)
                    .shadow(color: isWifiFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                    .captureFrame(id: isWifiFoc ? "secondaryButton_wifi_focused" : "secondaryButton_wifi_unfocused")
                }

                // HomeKit Scenes Section
                VStack(alignment: .leading, spacing: 12) {
                    Text("HomeKit Scenes")
                        .font(.system(size: 22, weight: .bold))
                        .foregroundColor(.white.opacity(0.9))
                        .captureFrame(id: "label_homekit_heading")

                    HStack(spacing: 16) {
                        ForEach(Array(config.homeKitScenes.enumerated()), id: \.offset) { idx, scene in
                            let isSceneFoc = (config.focusedElementIndex == 6 + idx)
                            VStack(alignment: .leading, spacing: 8) {
                                Image(systemName: "lightbulb.fill")
                                    .font(.system(size: 24))
                                    .foregroundColor(isSceneFoc ? .black : .orange)
                                    .captureFrame(id: "imageView_scene_icon_\(idx)")
                                Text(scene)
                                    .font(.system(size: 18, weight: .semibold))
                                    .foregroundColor(isSceneFoc ? .black : .white)
                                    .captureFrame(id: "label_scene_\(idx)")
                            }
                            .padding(16)
                            .frame(width: 176, height: 110, alignment: .topLeading)
                            .background(isSceneFoc ? Color.white : Color.white.opacity(0.1))
                            .cornerRadius(18)
                            .scaleEffect(isSceneFoc ? 1.06 : 1.0)
                            .shadow(color: isSceneFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                            .captureFrame(id: isSceneFoc ? "collectionItem_scene_\(idx)_focused" : "collectionItem_scene_\(idx)_unfocused")
                        }
                    }
                }
                .padding(.top, 8)

                Spacer()
            }
            .padding(32)
            .frame(width: 660, height: 1080)
            .background(Color(red: 0.12, green: 0.12, blue: 0.16))
            .shadow(color: Color.black.opacity(0.7), radius: 30)
            .captureFrame(id: "sidebar_control_center")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}
