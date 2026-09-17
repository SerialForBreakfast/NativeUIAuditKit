// tvOSConferenceRoomTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS Conference Room Display template for OS UI detection.
// Models Apple TV Conference Room Display mode (waiting for AirPlay connections in meeting rooms):
// instructions card, Wi-Fi SSID, Apple TV name, and AirPlay badge.
//
// Annotated elements:
//   sheet     — Conference Room Display card container
//   label     — "Conference Room Display", Wi-Fi network, Apple TV name, AirPlay code
//   imageView — AirPlay icon glyph, Wi-Fi icon, Apple TV graphic

import SwiftUI

// MARK: - tvOSConferenceRoomConfig

public struct tvOSConferenceRoomConfig: Sendable {
    public var roomName: String
    public var wifiNetwork: String
    public var airplayCode: String
    public var customMessage: String
    public var bgHue: Double

    public init(
        roomName: String = "Boardroom Apple TV",
        wifiNetwork: String = "Corporate-Guest",
        airplayCode: String = "4912",
        customMessage: String = "Connect to Wi-Fi to present wirelessly.",
        bgHue: Double = 0.62
    ) {
        self.roomName = roomName
        self.wifiNetwork = wifiNetwork
        self.airplayCode = airplayCode
        self.customMessage = customMessage
        self.bgHue = bgHue
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSConferenceRoomConfig {
        var rng = SeededRNG(seed: seed)
        let rooms = [
            ("Executive Conference Room", "Apple-Guest"),
            ("Design Studio Apple TV", "Studio-5GHz"),
            ("Engineering All-Hands", "Corp-WPA3"),
            ("Briefing Center 4K", "Guest-Wireless")
        ]
        let r = rooms[Int(rng.next() % UInt64(rooms.count))]
        let code = String(format: "%04d", rng.next() % 10000)

        return tvOSConferenceRoomConfig(
            roomName: r.0,
            wifiNetwork: r.1,
            airplayCode: code,
            customMessage: "To present, connect your Apple device to Wi-Fi and choose AirPlay.",
            bgHue: Double(rng.next() % 1000) / 1000.0
        )
    }
}

// MARK: - tvOSConferenceRoomTemplate View

public struct tvOSConferenceRoomTemplate: View {
    public let config: tvOSConferenceRoomConfig

    public init(config: tvOSConferenceRoomConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            // Elegant subtle wallpaper background
            LinearGradient(
                colors: [
                    Color(hue: config.bgHue, saturation: 0.5, brightness: 0.25),
                    Color(hue: (config.bgHue + 0.1).truncatingRemainder(dividingBy: 1.0), saturation: 0.4, brightness: 0.15),
                    Color.black
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            ).ignoresSafeArea()

            // Centered Conference Room Connection Card
            VStack(spacing: 36) {
                // AirPlay Icon Badge
                ZStack {
                    Circle()
                        .fill(Color.white.opacity(0.15))
                    Image(systemName: "airplayvideo")
                        .font(.system(size: 64))
                        .foregroundColor(.white)
                }
                .frame(width: 120, height: 120)
                .captureFrame(id: "imageView_conference_airplay_icon")

                // Main Heading
                VStack(spacing: 8) {
                    Text("AirPlay to")
                        .font(.system(size: 26, weight: .medium))
                        .foregroundColor(.white.opacity(0.7))
                        .captureFrame(id: "label_airplay_to_prefix")

                    Text(config.roomName)
                        .font(.system(size: 44, weight: .bold))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_room_name")
                }

                // Instructions & Network Info Box
                VStack(spacing: 16) {
                    HStack(spacing: 16) {
                        Image(systemName: "wifi")
                            .font(.system(size: 24))
                            .foregroundColor(.white.opacity(0.8))
                            .captureFrame(id: "imageView_wifi_icon")

                        Text("Wi-Fi: \(config.wifiNetwork)")
                            .font(.system(size: 26, weight: .semibold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_wifi_network")
                    }

                    Text(config.customMessage)
                        .font(.system(size: 22))
                        .foregroundColor(.white.opacity(0.75))
                        .multilineTextAlignment(.center)
                        .frame(maxWidth: 600)
                        .captureFrame(id: "label_instructions")
                }
                .padding(28)
                .background(Color.white.opacity(0.08))
                .cornerRadius(20)

                // AirPlay Code Box
                VStack(spacing: 8) {
                    Text("AIRPLAY CODE")
                        .font(.system(size: 18, weight: .bold))
                        .foregroundColor(.white.opacity(0.6))
                        .captureFrame(id: "label_code_heading")

                    Text(config.airplayCode)
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
