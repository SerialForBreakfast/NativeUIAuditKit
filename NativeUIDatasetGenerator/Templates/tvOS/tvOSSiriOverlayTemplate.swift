// tvOSSiriOverlayTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised Siri voice & dictation overlay template for tvOS OS UI detection (TASK-6b-E6).
// Models Siri floating card, transcribed speech text, Siri orb glow, and result action cards.
//
// Annotated elements:
//   popover        — the floating Siri card overlay container
//   collectionItem — Siri result cards (e.g. weather forecast days, search results)
//   primaryButton  — primary result action (e.g. "Open Weather", "Play")
//   cancelAction   — dismiss button
//   label          — transcribed user speech, Siri response text, temperature, card details
//   imageView      — Siri orb glow icon, weather condition icons

import SwiftUI

// MARK: - tvOSSiriOverlayConfig

public struct tvOSSiriOverlayConfig: Sendable {
    public var queryText: String
    public var responseText: String
    public var forecastCards: [(day: String, temp: String, icon: String)]
    public var focusedCardIndex: Int // -1: action button focused, 0..N: card focused
    public var bgHue: Double

    public init(
        queryText: String = "What's the weather today?",
        responseText: String = "It's currently 72° and sunny in Cupertino.",
        forecastCards: [(day: String, temp: String, icon: String)] = [
            ("Today", "72°", "sun.max.fill"),
            ("Wed", "68°", "cloud.sun.fill"),
            ("Thu", "65°", "cloud.rain.fill"),
            ("Fri", "70°", "sun.max.fill")
        ],
        focusedCardIndex: Int = 0,
        bgHue: Double = 0.55
    ) {
        self.queryText = queryText
        self.responseText = responseText
        self.forecastCards = forecastCards
        self.focusedCardIndex = focusedCardIndex
        self.bgHue = bgHue
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSSiriOverlayConfig {
        var rng = SeededRNG(seed: seed)
        let queries = [
            ("What's the weather today?", "It's currently 72° and sunny in Cupertino."),
            ("Show me action movies", "Here are popular action movies on Apple TV:"),
            ("What time does the game start?", "The game starts tonight at 7:00 PM."),
            ("Who stars in Severance?", "Severance stars Adam Scott, Zach Cherry, and Britt Lower.")
        ]

        let q = queries[Int(rng.next() % UInt64(queries.count))]
        let foc = Int(rng.next() % 4)
        let hue = Double(rng.next() % 1000) / 1000.0

        let cards: [(day: String, temp: String, icon: String)] = [
            ("Today", "72°", "sun.max.fill"),
            ("Wed", "68°", "cloud.sun.fill"),
            ("Thu", "65°", "cloud.rain.fill"),
            ("Fri", "70°", "sun.max.fill")
        ]

        return tvOSSiriOverlayConfig(
            queryText: q.0,
            responseText: q.1,
            forecastCards: cards,
            focusedCardIndex: foc,
            bgHue: hue
        )
    }
}

// MARK: - tvOSSiriOverlayTemplate View

public struct tvOSSiriOverlayTemplate: View {
    public let config: tvOSSiriOverlayConfig

    public init(config: tvOSSiriOverlayConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack(alignment: .bottom) {
            // Background app view (dimmed)
            LinearGradient(
                colors: [Color(hue: config.bgHue, saturation: 0.6, brightness: 0.3), Color.black],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            ).ignoresSafeArea()

            Color.black.opacity(0.6).ignoresSafeArea()

            // Floating Siri Card Overlay (bottom centered)
            VStack(spacing: 24) {
                // Header: Siri Orb & Speech Transcription
                HStack(spacing: 20) {
                    // Siri Glow Orb
                    ZStack {
                        Circle()
                            .fill(LinearGradient(
                                colors: [Color.purple, Color.cyan, Color.pink],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ))
                            .frame(width: 52, height: 52)
                            .blur(radius: 2)

                        Image(systemName: "sparkles")
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(.white)
                    }
                    .captureFrame(id: "imageView_siri_orb")

                    VStack(alignment: .leading, spacing: 4) {
                        Text(config.queryText)
                            .font(.system(size: 26, weight: .bold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_siri_query")

                        Text(config.responseText)
                            .font(.system(size: 22))
                            .foregroundColor(.white.opacity(0.8))
                            .captureFrame(id: "label_siri_response")
                    }

                    Spacer()
                }

                // Result Cards Row (e.g. Weather forecast cards)
                HStack(spacing: 20) {
                    ForEach(Array(config.forecastCards.enumerated()), id: \.offset) { idx, card in
                        let isFoc = (idx == config.focusedCardIndex)

                        VStack(spacing: 12) {
                            Text(card.day)
                                .font(.system(size: 20, weight: isFoc ? .bold : .medium))
                                .foregroundColor(isFoc ? .black : .white.opacity(0.8))
                                .captureFrame(id: "label_card_day_\(idx)")

                            Image(systemName: card.icon)
                                .font(.system(size: 32))
                                .foregroundColor(isFoc ? .black : (card.icon.contains("sun") ? .yellow : .cyan))
                                .captureFrame(id: "imageView_card_weather_\(idx)")

                            Text(card.temp)
                                .font(.system(size: 24, weight: .bold))
                                .foregroundColor(isFoc ? .black : .white)
                                .captureFrame(id: "label_card_temp_\(idx)")
                        }
                        .frame(width: 170, height: 160)
                        .background(isFoc ? Color.white : Color.white.opacity(0.1))
                        .cornerRadius(20)
                        .scaleEffect(isFoc ? 1.08 : 1.0)
                        .shadow(color: isFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                        .captureFrame(id: isFoc ? "collectionItem_forecast_\(idx)_focused" : "collectionItem_forecast_\(idx)_unfocused")
                    }
                }

                // Primary Action Button (e.g. "Open Weather App")
                HStack {
                    Spacer()
                    let isBtnFoc = (config.focusedCardIndex == -1)
                    HStack(spacing: 10) {
                        Image(systemName: "arrow.up.forward.app.fill")
                            .font(.system(size: 20))
                        Text("Open Weather")
                            .font(.system(size: 22, weight: .bold))
                    }
                    .foregroundColor(isBtnFoc ? .black : .white)
                    .padding(.horizontal, 28)
                    .padding(.vertical, 14)
                    .background(isBtnFoc ? Color.white : Color.white.opacity(0.15))
                    .cornerRadius(18)
                    .scaleEffect(isBtnFoc ? 1.08 : 1.0)
                    .shadow(color: isBtnFoc ? Color.white.opacity(0.4) : Color.clear, radius: 12)
                    .captureFrame(id: isBtnFoc ? "primaryButton_open_app_focused" : "primaryButton_open_app_unfocused")
                }
            }
            .padding(32)
            .frame(width: 860)
            .background(Color(red: 0.12, green: 0.12, blue: 0.16))
            .cornerRadius(28)
            .shadow(color: Color.black.opacity(0.8), radius: 36)
            .padding(.bottom, 60)
            .captureFrame(id: "popover_siri_card")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}
