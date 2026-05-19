// ProgressActivityTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI progress + activity combined template (TASK-5b-20).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// Annotated elements:
//   progressView      — linear progress bars (1–3 of them)
//   activityIndicator — spinning activity indicators (1–2)
//   label             — descriptive text for each progress/activity item
//   cancelAction      — cancel / stop button
//
// This template targets training diversity for progress-related elements which
// often appear together in download/upload/processing screens.
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - ProgressActivityConfig

/// Parameterised inputs for a single ProgressActivity rendering.
public struct ProgressActivityConfig: Sendable {
    /// Screen title.
    public var title: String
    /// Progress bar items (1–3 items, each with a label and fractional value).
    public var progressItems: [(label: String, fraction: Double)]
    /// Activity items (1–2 items with labels).
    public var activityItems: [String]
    /// Cancel button label.
    public var cancelLabel: String
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        title: String,
        progressItems: [(label: String, fraction: Double)],
        activityItems: [String],
        cancelLabel: String,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.progressItems = progressItems
        self.activityItems = activityItems
        self.cancelLabel = cancelLabel
        self.colorScheme = colorScheme
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> ProgressActivityConfig {
        var rng = SeededRNG(seed: seed)
        let dark          = rng.next() % 2 == 0
        let progressCount = 1 + Int(rng.next() % 3)   // 1–3 progress bars
        let activityCount = 1 + Int(rng.next() % 2)   // 1–2 spinners

        var progressItems: [(label: String, fraction: Double)] = []
        for _ in 0..<progressCount {
            let fraction = Double(rng.next() % 1000) / 1000.0
            progressItems.append((label: corpus.listRowTitle(), fraction: fraction))
        }

        var activityItems: [String] = []
        for _ in 0..<activityCount {
            activityItems.append(corpus.listRowTitle())
        }

        return ProgressActivityConfig(
            title: corpus.navigationTitle(),
            progressItems: progressItems,
            activityItems: activityItems,
            cancelLabel: "Cancel",
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - ProgressActivityTemplate

/// SwiftUI view rendering a progress/activity monitoring screen.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct ProgressActivityTemplate: View {
    public let config: ProgressActivityConfig

    public init(config: ProgressActivityConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            Color(UIColor.systemGroupedBackground).ignoresSafeArea()

            VStack(alignment: .leading, spacing: 0) {
                // Screen title
                Text(config.title)
                    .font(.title2.bold())
                    .padding(.horizontal, 20)
                    .padding(.top, 48)
                    .padding(.bottom, 24)

                // Progress bar items
                VStack(alignment: .leading, spacing: 20) {
                    ForEach(Array(config.progressItems.enumerated()), id: \.offset) { idx, item in
                        VStack(alignment: .leading, spacing: 6) {
                            HStack {
                                Text(item.label)
                                    .font(.subheadline)
                                    .captureFrame(id: "label_progress_\(idx)")
                                Spacer()
                                Text("\(Int(item.fraction * 100))%")
                                    .font(.subheadline.monospacedDigit())
                                    .foregroundStyle(.secondary)
                            }
                            ProgressView(value: item.fraction)
                                .tint(Color.accentColor)
                                .captureFrame(id: "progressView_\(idx)")
                        }
                        .padding(.horizontal, 20)
                    }
                }
                .padding(.vertical, 16)
                .background(Color(UIColor.systemBackground))
                .clipShape(RoundedRectangle(cornerRadius: 12))
                .padding(.horizontal, 16)

                // Activity indicator items
                VStack(alignment: .leading, spacing: 0) {
                    ForEach(Array(config.activityItems.enumerated()), id: \.offset) { idx, item in
                        HStack(spacing: 16) {
                            ProgressView()
                                .scaleEffect(0.85)
                                .captureFrame(id: "activityIndicator_\(idx)")

                            Text(item)
                                .font(.body)
                                .captureFrame(id: "label_activity_\(idx)")

                            Spacer()
                        }
                        .padding(.horizontal, 20)
                        .padding(.vertical, 14)

                        if idx < config.activityItems.count - 1 {
                            Divider().padding(.leading, 60)
                        }
                    }
                }
                .background(Color(UIColor.systemBackground))
                .clipShape(RoundedRectangle(cornerRadius: 12))
                .padding(.horizontal, 16)
                .padding(.top, 16)

                Spacer()

                // Cancel button
                Button(config.cancelLabel) {}
                    .frame(maxWidth: .infinity, minHeight: 50)
                    .background(Color.secondary.opacity(0.15))
                    .foregroundStyle(.primary)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .captureFrame(id: "cancelAction_0")
                    .padding(.horizontal, 20)
                    .padding(.bottom, 48)
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}
