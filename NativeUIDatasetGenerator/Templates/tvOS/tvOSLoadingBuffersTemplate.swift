// tvOSLoadingBuffersTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised tvOS Loading & Buffering HUD template for OS UI detection.
// Models tvOS system progress spinners, app launching buffers, and content download bars.
//
// Annotated elements:
//   activityIndicator — spinning circular activity wheel / indeterminate spinner
//   progressView      — determinate linear download / buffering progress bar
//   label             — status message ("Loading...", "Downloading update..."), percentage
//   sheet             — modal loading card container

import SwiftUI

// MARK: - tvOSLoadingBuffersConfig

public struct tvOSLoadingBuffersConfig: Sendable {
    public var title: String
    public var subtitle: String
    public var progress: Double // 0.0 .. 1.0 (determinate) or nil (indeterminate)
    public var showDeterminateBar: Bool

    public init(
        title: String = "Loading...",
        subtitle: String = "Please wait while your content is loaded",
        progress: Double = 0.45,
        showDeterminateBar: Bool = true
    ) {
        self.title = title
        self.subtitle = subtitle
        self.progress = progress
        self.showDeterminateBar = showDeterminateBar
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSLoadingBuffersConfig {
        var rng = SeededRNG(seed: seed)
        let messages = [
            ("Loading...", "Preparing video playback..."),
            ("Updating Library...", "Syncing with iCloud..."),
            ("Installing Software Update...", "Apple TV will restart when finished."),
            ("Buffering Stream...", "Optimizing video quality for your network connection.")
        ]
        let item = messages[Int(rng.next() % UInt64(messages.count))]
        let isDeterminate = (rng.next() % 2 == 0)
        let prog = Double(10 + (rng.next() % 85)) / 100.0

        return tvOSLoadingBuffersConfig(
            title: item.0,
            subtitle: item.1,
            progress: prog,
            showDeterminateBar: isDeterminate
        )
    }
}

// MARK: - tvOSLoadingBuffersTemplate View

public struct tvOSLoadingBuffersTemplate: View {
    public let config: tvOSLoadingBuffersConfig

    public init(config: tvOSLoadingBuffersConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            Color.black.opacity(0.88).ignoresSafeArea()

            VStack(spacing: 32) {
                // Activity Indicator Spinner (simulated with circular tick marks)
                ZStack {
                    ForEach(0..<8) { i in
                        RoundedRectangle(cornerRadius: 3)
                            .fill(Color.white.opacity(Double(i + 1) / 8.0))
                            .frame(width: 8, height: 22)
                            .offset(y: -30)
                            .rotationEffect(.degrees(Double(i) * 45.0))
                    }
                }
                .frame(width: 80, height: 80)
                .captureFrame(id: "activityIndicator_system_spinner")

                // Status Texts
                VStack(spacing: 12) {
                    Text(config.title)
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(.white)
                        .captureFrame(id: "label_loading_title")

                    Text(config.subtitle)
                        .font(.system(size: 22))
                        .foregroundColor(.white.opacity(0.7))
                        .captureFrame(id: "label_loading_subtitle")
                }

                // Determinate Progress Bar (if applicable)
                if config.showDeterminateBar {
                    VStack(spacing: 10) {
                        ZStack(alignment: .leading) {
                            RoundedRectangle(cornerRadius: 6)
                                .fill(Color.white.opacity(0.2))
                                .frame(width: 440, height: 10)

                            RoundedRectangle(cornerRadius: 6)
                                .fill(Color.white)
                                .frame(width: 440 * CGFloat(config.progress), height: 10)
                        }
                        .captureFrame(id: "progressView_download_progress")

                        Text("\(Int(config.progress * 100))%")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.white.opacity(0.6))
                            .captureFrame(id: "label_progress_percent")
                    }
                }
            }
            .padding(48)
            .frame(width: 640)
            .background(Color(red: 0.14, green: 0.14, blue: 0.18))
            .cornerRadius(28)
            .shadow(color: Color.black.opacity(0.6), radius: 32)
            .captureFrame(id: "sheet_loading_modal")
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}
