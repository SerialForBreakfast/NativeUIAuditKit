// SliderPanelTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI multi-slider panel template (TASK-5b-22).
// Covers multiple `slider` instances in a SwiftUI-native context (UIKitControls has
// sliders via UIKit; this template gives SwiftUI slider training data).
//
// Annotated elements:
//   slider       — SwiftUI Slider instances (2–4 sliders)
//   label        — slider row labels and value readouts
//   navigationBar — auto-detected
//   toggle       — optional "enabled" toggle per slider row
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - SliderRowConfig

public struct SliderRowConfig: Sendable {
    public var label: String
    public var value: Double          // 0.0–1.0
    public var isDisabled: Bool
    public var iconName: String       // SF Symbol for the slider row icon
}

// MARK: - SliderPanelConfig

public struct SliderPanelConfig: Sendable {
    public var title: String
    public var rows: [SliderRowConfig]
    public var colorScheme: ColorScheme

    public init(title: String, rows: [SliderRowConfig], colorScheme: ColorScheme) {
        self.title = title
        self.rows = rows
        self.colorScheme = colorScheme
    }

    private static let rowDefs: [(label: String, icon: String)] = [
        ("Brightness", "sun.max.fill"),
        ("Volume", "speaker.wave.2.fill"),
        ("Playback Speed", "speedometer"),
        ("Opacity", "circle.lefthalf.filled"),
        ("Zoom Level", "magnifyingglass"),
        ("Font Size", "textformat.size"),
        ("Sensitivity", "dial.low"),
        ("Balance", "slider.horizontal.3"),
    ]

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> SliderPanelConfig {
        var rng = SeededRNG(seed: seed)
        let dark      = rng.next() % 2 == 0
        let count     = 2 + Int(rng.next() % 3)   // 2–4 sliders

        // Pick `count` distinct rows from the pool
        var pool = rowDefs.shuffled(using: &rng)
        pool = Array(pool.prefix(count))

        var rows: [SliderRowConfig] = []
        for def in pool {
            let value    = Double(rng.next() % 1000) / 1000.0
            let disabled = rng.next() % 5 == 0   // ~20% disabled
            rows.append(SliderRowConfig(label: def.label, value: value,
                                        isDisabled: disabled, iconName: def.icon))
        }

        return SliderPanelConfig(
            title: corpus.navigationTitle(),
            rows: rows,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - SliderPanelTemplate

public struct SliderPanelTemplate: View {
    public let config: SliderPanelConfig

    public init(config: SliderPanelConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            Color(UIColor.systemGroupedBackground).ignoresSafeArea()

            NavigationStack {
                List {
                    Section {
                        ForEach(Array(config.rows.enumerated()), id: \.offset) { idx, row in
                            VStack(alignment: .leading, spacing: 8) {
                                HStack {
                                    Image(systemName: row.iconName)
                                        .foregroundStyle(Color.accentColor)
                                        .frame(width: 24)
                                        .opacity(row.isDisabled ? 0.35 : 1.0)
                                    Text(row.label)
                                        .font(.body)
                                        .foregroundStyle(row.isDisabled ? Color.secondary : Color.primary)
                                        .captureFrame(id: "label_slider_\(idx)")
                                    Spacer()
                                    Text("\(Int(row.value * 100))%")
                                        .font(.subheadline.monospacedDigit())
                                        .foregroundStyle(Color.secondary)
                                }
                                Slider(value: .constant(row.value))
                                    .tint(Color.accentColor)
                                    .disabled(row.isDisabled)
                                    .opacity(row.isDisabled ? 0.45 : 1.0)
                                    .captureFrame(id: "slider_\(idx)")
                            }
                            .padding(.vertical, 6)
                        }
                    } header: {
                        Text("Adjustments")
                            .captureFrame(id: "label_section_header")
                    } footer: {
                        Text("Changes take effect immediately.")
                            .captureFrame(id: "label_section_footer")
                    }
                }
                .navigationTitle(config.title)
                .navigationBarTitleDisplayMode(.large)
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}

// MARK: - Array+shuffled(using:)

private extension Array {
    /// Returns a shuffled copy using a SeededRNG.
    func shuffled(using rng: inout SeededRNG) -> [Element] {
        var copy = self
        for i in stride(from: copy.count - 1, through: 1, by: -1) {
            let j = Int(rng.next() % UInt64(i + 1))
            copy.swapAt(i, j)
        }
        return copy
    }
}
