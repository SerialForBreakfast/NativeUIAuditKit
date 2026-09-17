// tvOSFitnessHUDTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS Apple Fitness+ / Workout HUD overlay template for OS UI detection.
// Models the on-screen workout metrics overlay on tvOS:
// active calories, heart rate with pulse icon, elapsed workout timer, and activity rings (progressView).
//
// Annotated elements:
//   progressView      — workout activity rings (Move / Exercise / Stand) and Burn Bar
//   activityIndicator — heart rate live pulse indicator
//   label             — timer readout, calorie count, BPM value, workout coach name
//   imageView         — fitness flame icon and heart glyph

import SwiftUI

// MARK: - tvOSFitnessHUDConfig

public struct tvOSFitnessHUDConfig: Sendable {
    public var calories: Int
    public var heartRate: Int
    public var timerText: String
    public var coachName: String
    public var workoutType: String
    public var ringProgress: Double

    public init(
        calories: Int = 342,
        heartRate: Int = 156,
        timerText: String = "18:42",
        coachName: String = "Bakari • HIIT",
        workoutType: String = "High Intensity Interval Training",
        ringProgress: Double = 0.75
    ) {
        self.calories = calories
        self.heartRate = heartRate
        self.timerText = timerText
        self.coachName = coachName
        self.workoutType = workoutType
        self.ringProgress = ringProgress
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSFitnessHUDConfig {
        var rng = SeededRNG(seed: seed)
        let workouts = [
            ("Bakari • HIIT", "High Intensity Interval Training"),
            ("Jessica • Yoga", "Slow Flow Yoga"),
            ("Tyrell • Cycling", "Pure Dance Cycling"),
            ("Sam • Strength", "Upper Body Strength")
        ]
        let w = workouts[Int(rng.next() % UInt64(workouts.count))]
        let cal = Int(150 + (rng.next() % 400))
        let bpm = Int(110 + (rng.next() % 65))
        let min = Int(rng.next() % 45)
        let sec = Int(rng.next() % 60)

        return tvOSFitnessHUDConfig(
            calories: cal,
            heartRate: bpm,
            timerText: String(format: "%02d:%02d", min, sec),
            coachName: w.0,
            workoutType: w.1,
            ringProgress: Double(40 + (rng.next() % 50)) / 100.0
        )
    }
}

// MARK: - tvOSFitnessHUDTemplate View

public struct tvOSFitnessHUDTemplate: View {
    public let config: tvOSFitnessHUDConfig

    public init(config: tvOSFitnessHUDConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack(alignment: .topLeading) {
            // Simulated video background (dark workout stage)
            LinearGradient(
                colors: [Color(red: 0.05, green: 0.05, blue: 0.08), Color(red: 0.1, green: 0.05, blue: 0.12)],
                startPoint: .top,
                endPoint: .bottom
            ).ignoresSafeArea()

            // Top-Left Workout Metrics HUD
            VStack(alignment: .leading, spacing: 18) {
                // Workout Type & Coach
                VStack(alignment: .leading, spacing: 4) {
                    Text(config.coachName)
                        .font(.system(size: 26, weight: .bold))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_fitness_coach")

                    Text(config.workoutType)
                        .font(.system(size: 18))
                        .foregroundColor(.white.opacity(0.6))
                        .captureFrame(id: "label_fitness_type")
                }

                // Timer
                Text(config.timerText)
                    .font(.system(size: 52, weight: .heavy, design: .rounded))
                    .foregroundColor(.white)
                    .captureFrame(id: "label_fitness_timer")

                // Calories Metric
                HStack(spacing: 12) {
                    Image(systemName: "flame.fill")
                        .font(.system(size: 26))
                        .foregroundColor(.red)
                        .captureFrame(id: "imageView_flame_icon")

                    HStack(alignment: .lastTextBaseline, spacing: 6) {
                        Text("\(config.calories)")
                            .font(.system(size: 38, weight: .bold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_calorie_count")

                        Text("CAL")
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.white.opacity(0.6))
                            .captureFrame(id: "label_cal_unit")
                    }
                }

                // Heart Rate Metric
                HStack(spacing: 12) {
                    Image(systemName: "heart.fill")
                        .font(.system(size: 24))
                        .foregroundColor(.red)
                        .captureFrame(id: "activityIndicator_heart_pulse")

                    HStack(alignment: .lastTextBaseline, spacing: 6) {
                        Text("\(config.heartRate)")
                            .font(.system(size: 38, weight: .bold))
                            .foregroundColor(.white)
                            .captureFrame(id: "label_heart_rate_bpm")

                        Text("BPM")
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.white.opacity(0.6))
                            .captureFrame(id: "label_bpm_unit")
                    }
                }

                // Burn Bar Progress Bar
                VStack(alignment: .leading, spacing: 6) {
                    Text("BURN BAR")
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.white.opacity(0.6))
                        .captureFrame(id: "label_burn_bar_title")

                    ZStack(alignment: .leading) {
                        RoundedRectangle(cornerRadius: 6)
                            .fill(Color.white.opacity(0.15))
                            .frame(width: 280, height: 12)

                        RoundedRectangle(cornerRadius: 6)
                            .fill(LinearGradient(colors: [.yellow, .orange, .red], startPoint: .leading, endPoint: .trailing))
                            .frame(width: 280 * CGFloat(config.ringProgress), height: 12)
                    }
                    .captureFrame(id: "progressView_burn_bar")
                }
            }
            .padding(32)
            .background(Color.black.opacity(0.65))
            .cornerRadius(24)
            .padding(.leading, 80)
            .padding(.top, 60)

            // Top-Right Activity Rings HUD
            VStack {
                HStack {
                    Spacer()
                    ZStack {
                        // Outer Ring (Move)
                        Circle()
                            .stroke(Color.red.opacity(0.25), lineWidth: 14)
                        Circle()
                            .trim(from: 0, to: CGFloat(config.ringProgress))
                            .stroke(Color.red, style: StrokeStyle(lineWidth: 14, lineCap: .round))
                            .rotationEffect(.degrees(-90))

                        // Middle Ring (Exercise)
                        Circle()
                            .stroke(Color.green.opacity(0.25), lineWidth: 14)
                            .frame(width: 100, height: 100)
                        Circle()
                            .trim(from: 0, to: CGFloat(config.ringProgress * 0.85))
                            .stroke(Color.green, style: StrokeStyle(lineWidth: 14, lineCap: .round))
                            .frame(width: 100, height: 100)
                            .rotationEffect(.degrees(-90))

                        // Inner Ring (Stand)
                        Circle()
                            .stroke(Color.blue.opacity(0.25), lineWidth: 14)
                            .frame(width: 68, height: 68)
                        Circle()
                            .trim(from: 0, to: CGFloat(config.ringProgress * 0.95))
                            .stroke(Color.blue, style: StrokeStyle(lineWidth: 14, lineCap: .round))
                            .frame(width: 68, height: 68)
                            .rotationEffect(.degrees(-90))
                    }
                    .frame(width: 132, height: 132)
                    .padding(24)
                    .background(Color.black.opacity(0.65))
                    .cornerRadius(24)
                    .padding(.trailing, 80)
                    .padding(.top, 60)
                    .captureFrame(id: "progressView_activity_rings")
                }
                Spacer()
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}
