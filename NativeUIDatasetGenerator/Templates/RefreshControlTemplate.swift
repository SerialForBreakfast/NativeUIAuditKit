// RefreshControlTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI refresh control in list template (TASK-5b-16).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// Annotated elements:
//   navigationBar   — auto-detected (BP-17)
//   listRow         — list content rows
//   refreshControl  — the pull-to-refresh spinner (rendered at the top of the list)
//
// The refresh control is simulated at a fixed position (pulled 80pt down)
// using a manually drawn circle + ProgressView, since UIRefreshControl only
// appears during a live pull gesture. The generator captures the stable
// "refreshing" state (spinner visible, list displaced downward).
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - RefreshControlConfig

/// Parameterised inputs for a single RefreshControl rendering.
public struct RefreshControlConfig: Sendable {
    /// Navigation bar title.
    public var title: String
    /// List row labels (4–8 items).
    public var rowLabels: [String]
    /// When true, the refresh control is in the "refreshing" (spinning) state.
    /// When false, it's the pull indicator (partially pulled).
    public var isRefreshing: Bool
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        title: String,
        rowLabels: [String],
        isRefreshing: Bool,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.rowLabels = rowLabels
        self.isRefreshing = isRefreshing
        self.colorScheme = colorScheme
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> RefreshControlConfig {
        var rng = SeededRNG(seed: seed)
        let dark        = rng.next() % 2 == 0
        let rowCount    = 4 + Int(rng.next() % 5)   // 4–8 rows
        let refreshing  = rng.next() % 2 == 0       // 50% refreshing / 50% pulling

        var rows: [String] = []
        for _ in 0..<rowCount { rows.append(corpus.listRowTitle()) }

        return RefreshControlConfig(
            title: corpus.navigationTitle(),
            rowLabels: rows,
            isRefreshing: refreshing,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - RefreshControlTemplate

/// SwiftUI view rendering a list with visible refresh control.
///
/// The refresh control is rendered as an overlay at a fixed position
/// (pulled 80pt from nav bar bottom) to simulate the UIRefreshControl
/// "refreshing" state. The annotated element covers the spinner area.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct RefreshControlTemplate: View {
    public let config: RefreshControlConfig

    public init(config: RefreshControlConfig) {
        self.config = config
    }

    public var body: some View {
        NavigationStack {
            ZStack(alignment: .top) {
                // List content displaced downward (simulates pulled state)
                List {
                    ForEach(Array(config.rowLabels.enumerated()), id: \.offset) { idx, label in
                        HStack {
                            Image(systemName: "circle.fill")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                            Text(label)
                        }
                        .captureFrame(id: "listRow_\(idx)")
                    }
                }
                .listStyle(.plain)
                .padding(.top, 60)  // displace list to reveal refresh control area

                // Refresh control overlay — fixed at top of content area
                // Renders at a consistent position for annotation accuracy
                VStack(spacing: 4) {
                    if config.isRefreshing {
                        ProgressView()
                            .scaleEffect(0.9)
                            .captureFrame(id: "refreshControl_0")
                    } else {
                        // Pull indicator (arrow down)
                        Image(systemName: "arrow.down")
                            .font(.system(size: 18, weight: .medium))
                            .foregroundStyle(.secondary)
                            .captureFrame(id: "refreshControl_0")
                    }
                }
                .frame(maxWidth: .infinity)
                .frame(height: 56)
                .padding(.top, 0)
            }
            .ignoresSafeArea(.all)
            .navigationTitle(config.title)
            .navigationBarTitleDisplayMode(.inline)
            .colorScheme(config.colorScheme)
        }
        .colorScheme(config.colorScheme)
    }
}
