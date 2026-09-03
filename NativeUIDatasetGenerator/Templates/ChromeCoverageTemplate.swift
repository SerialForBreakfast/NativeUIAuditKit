// ChromeCoverageTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Fills the four taxonomy classes that had 0 boxes in Run 007 (TASK-6a-8):
// statusBar, scrollIndicator, tooltip, unknown. `toolbar` is covered by
// ToolbarActions explicit `toolbar_0`. DS-G8 cannot pass empty classes.
//
// Simulator windows do not include a real UIStatusBar; the bar is painted.
// Scroll indicators and iPad-style tooltips are likewise synthesized.
//
// Annotated elements:
//   statusBar, scrollIndicator, tooltip, unknown, label, listRow
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - ChromeCoverageConfig

/// Parameterised inputs for a single ChromeCoverage rendering.
public struct ChromeCoverageConfig: Sendable {
    public var timeText: String
    public var tooltipText: String
    public var unknownLabel: String
    public var rows: [String]
    public var colorScheme: ColorScheme

    public init(
        timeText: String,
        tooltipText: String,
        unknownLabel: String,
        rows: [String],
        colorScheme: ColorScheme
    ) {
        self.timeText = timeText
        self.tooltipText = tooltipText
        self.unknownLabel = unknownLabel
        self.rows = rows
        self.colorScheme = colorScheme
    }

    private static let times = ["9:41", "12:00", "3:07", "18:22", "7:15"]
    private static let tips = ["Hold to edit", "Drag to reorder", "Double-tap for details", "Pinch to zoom"]
    private static let unknownLabels = ["Live Activity", "Focus Filter", "Stage Manager", "StandBy"]

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> ChromeCoverageConfig {
        var rng = SeededRNG(seed: seed)
        let dark = rng.next() % 2 == 0
        let rowCount = 8 + Int(rng.next() % 5)
        var rows: [String] = []
        for _ in 0..<rowCount {
            rows.append(corpus.listRowTitle())
        }
        return ChromeCoverageConfig(
            timeText: times[Int(rng.next() % UInt64(times.count))],
            tooltipText: tips[Int(rng.next() % UInt64(tips.count))],
            unknownLabel: unknownLabels[Int(rng.next() % UInt64(unknownLabels.count))],
            rows: rows,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - ChromeCoverageTemplate

/// Painted status bar, scroll indicator, tooltip, and an unclassifiable chip.
///
/// **Platform scope:** iOS GeneratorRunner target only.
///
/// No `NavigationStack` — a real nav bar would compete with the painted status bar.
public struct ChromeCoverageTemplate: View {
    public let config: ChromeCoverageConfig

    public init(config: ChromeCoverageConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack(alignment: .top) {
            Color(UIColor.systemBackground).ignoresSafeArea()

            VStack(spacing: 0) {
                statusBar
                    .captureFrame(id: "statusBar_0")

                HStack(alignment: .top, spacing: 0) {
                    ScrollView {
                        VStack(alignment: .leading, spacing: 0) {
                            ForEach(Array(config.rows.enumerated()), id: \.offset) { idx, title in
                                Text(title)
                                    .font(.body)
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                    .padding(.horizontal, 16)
                                    .padding(.vertical, 14)
                                    .captureFrame(id: "listRow_\(idx)")
                                if idx < config.rows.count - 1 {
                                    Divider().padding(.leading, 16)
                                }
                            }
                        }
                    }

                    Capsule()
                        .fill(Color.secondary.opacity(0.45))
                        .frame(width: 3, height: 36)
                        .padding(.trailing, 4)
                        .padding(.top, 24)
                        .captureFrame(id: "scrollIndicator_0")
                }

                Spacer(minLength: 0)
            }

            VStack {
                Spacer().frame(height: 120)
                HStack {
                    Spacer()
                    tooltipBubble
                        .captureFrame(id: "tooltip_0")
                    Spacer().frame(width: 48)
                }
                Spacer()
            }

            VStack {
                Spacer()
                HStack {
                    unknownChip
                        .captureFrame(id: "unknown_0")
                    Spacer()
                }
                .padding(.leading, 16)
                .padding(.bottom, 28)
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }

    /// System-status-bar look-alike. Generator windows do not include UIStatusBar.
    private var statusBar: some View {
        HStack {
            Text(config.timeText)
                .font(.system(size: 15, weight: .semibold, design: .rounded))
                .captureFrame(id: "label_status_time")
            Spacer()
            HStack(spacing: 6) {
                Image(systemName: "cellularbars")
                    .font(.system(size: 13, weight: .semibold))
                Image(systemName: "wifi")
                    .font(.system(size: 13, weight: .semibold))
                Image(systemName: "battery.75percent")
                    .font(.system(size: 14, weight: .semibold))
            }
        }
        .foregroundStyle(.primary)
        .padding(.horizontal, 24)
        .padding(.top, 14)
        .padding(.bottom, 8)
        .frame(maxWidth: .infinity)
        .background(.bar)
    }

    /// iPadOS / macOS-style hover tooltip (painted; pointer hover is not available).
    private var tooltipBubble: some View {
        VStack(spacing: 0) {
            Text(config.tooltipText)
                .font(.caption)
                .foregroundStyle(.primary)
                .padding(.horizontal, 10)
                .padding(.vertical, 6)
                .background(
                    RoundedRectangle(cornerRadius: 6)
                        .fill(Color(UIColor.secondarySystemBackground))
                        .shadow(color: .black.opacity(0.18), radius: 4, y: 2)
                )
            Triangle()
                .fill(Color(UIColor.secondarySystemBackground))
                .frame(width: 10, height: 6)
        }
    }

    /// Native-looking chip that is not a button, toggle, or list row — `unknown`.
    private var unknownChip: some View {
        HStack(spacing: 8) {
            Circle()
                .fill(Color.orange.gradient)
                .frame(width: 22, height: 22)
            Text(config.unknownLabel)
                .font(.caption.weight(.medium))
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(
            Capsule()
                .fill(Color(UIColor.tertiarySystemFill))
        )
    }
}

/// Downward caret for the tooltip bubble. Local to this template.
private struct Triangle: Shape {
    func path(in rect: CGRect) -> Path {
        var path = Path()
        path.move(to: CGPoint(x: rect.midX, y: rect.maxY))
        path.addLine(to: CGPoint(x: rect.minX, y: rect.minY))
        path.addLine(to: CGPoint(x: rect.maxX, y: rect.minY))
        path.closeSubpath()
        return path
    }
}
