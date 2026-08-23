// AnalyticsDashboardTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Generalization holdout template — deliberately NOT part of the main dataset (never
// registered in GenerateDatasetTests' dispatcher, never contributes to train/validation/
// test manifest entries). Exists solely so the already-trained model can be evaluated
// against a genuinely unseen template family/layout. See GeneralizationHoldoutTest.swift
// and Research/ExperimentLog.md for methodology and results.
//
// Structural distinction from all 51 existing families: a 2-column metric-card grid with
// toggles embedded inside cards (not list rows), a search textField pinned directly under
// the nav bar (not inside a form), and a floating circular primaryButton (FAB) — none of
// the existing templates combine these three patterns.
//
// Annotated elements (5-class Phase 6 taxonomy):
//   navigationBar  — auto-detected via NavigationStack chrome
//   textField      — search bar under the nav bar
//   toggle         — ×2, embedded inside metric cards
//   primaryButton  — ×1, floating action button (bottom-right)

import SwiftUI
import UIKit

// MARK: - AnalyticsDashboardConfig

public struct AnalyticsDashboardConfig: Sendable {
    public var title: String
    public var searchPlaceholder: String
    public var cards: [(title: String, value: String, hasToggle: Bool)]
    public var colorScheme: ColorScheme

    public init(
        title: String,
        searchPlaceholder: String,
        cards: [(title: String, value: String, hasToggle: Bool)],
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.searchPlaceholder = searchPlaceholder
        self.cards = cards
        self.colorScheme = colorScheme
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> AnalyticsDashboardConfig {
        var rng = SeededRNG(seed: seed)
        let dark = rng.next() % 2 == 0

        let metricLabels = ["Revenue", "Active Users", "Sessions", "Conversion"]
        var cards: [(title: String, value: String, hasToggle: Bool)] = []
        for (i, label) in metricLabels.enumerated() {
            let value = i % 2 == 0
                ? "$\(1 + Int(rng.next() % 99))k"
                : "\(1 + Int(rng.next() % 999))"
            cards.append((title: label, value: value, hasToggle: i < 2))
        }

        return AnalyticsDashboardConfig(
            title: corpus.navigationTitle(),
            searchPlaceholder: "Search dashboards",
            cards: cards,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - AnalyticsDashboardTemplate

public struct AnalyticsDashboardTemplate: View {
    public let config: AnalyticsDashboardConfig

    public init(config: AnalyticsDashboardConfig) {
        self.config = config
    }

    private let columns = [GridItem(.flexible()), GridItem(.flexible())]

    public var body: some View {
        ZStack {
            Color(UIColor.systemGroupedBackground).ignoresSafeArea()

            NavigationStack {
                ZStack(alignment: .bottomTrailing) {
                    ScrollView {
                        VStack(spacing: 16) {
                            // Search bar pinned directly under the nav bar (not inside a Form)
                            HStack {
                                Image(systemName: "magnifyingglass")
                                    .foregroundStyle(.secondary)
                                Text(config.searchPlaceholder)
                                    .foregroundStyle(.secondary)
                                Spacer()
                            }
                            .padding(10)
                            .background(Color(UIColor.secondarySystemGroupedBackground))
                            .clipShape(RoundedRectangle(cornerRadius: 10))
                            .captureFrame(id: "textField_0")
                            .padding(.horizontal, 16)
                            .padding(.top, 12)

                            // 2-column metric card grid
                            LazyVGrid(columns: columns, spacing: 12) {
                                ForEach(Array(config.cards.enumerated()), id: \.offset) { idx, card in
                                    VStack(alignment: .leading, spacing: 8) {
                                        Text(card.title)
                                            .font(.caption)
                                            .foregroundStyle(.secondary)
                                        Text(card.value)
                                            .font(.title2.bold())
                                        if card.hasToggle {
                                            HStack(spacing: 6) {
                                                Text("Auto-refresh")
                                                    .font(.caption2)
                                                    .foregroundStyle(.secondary)
                                                    .captureFrame(id: "label_toggle_caption_\(idx)")
                                                Toggle("", isOn: .constant(idx == 0))
                                                    .labelsHidden()
                                                    .captureFrame(id: "toggle_\(idx)")
                                            }
                                        }
                                    }
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                    .padding(12)
                                    .background(Color(UIColor.secondarySystemGroupedBackground))
                                    .clipShape(RoundedRectangle(cornerRadius: 12))
                                }
                            }
                            .padding(.horizontal, 16)

                            Spacer(minLength: 80)
                        }
                    }

                    // Floating action button — bottom-right, distinct from every
                    // existing full-width/list-embedded primaryButton pattern.
                    Button(action: {}) {
                        Image(systemName: "plus")
                            .font(.title2.weight(.semibold))
                            .foregroundStyle(.white)
                            .frame(width: 56, height: 56)
                            .background(Color.accentColor)
                            .clipShape(Circle())
                            .shadow(radius: 4)
                    }
                    .captureFrame(id: "primaryButton_0")
                    .padding(.trailing, 20)
                    .padding(.bottom, 20)
                }
                .navigationTitle(config.title)
                .navigationBarTitleDisplayMode(.inline)
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}
