// StepperTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI stepper + quantity controls template (TASK-5b-19).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// Annotated elements:
//   stepperControl — each Stepper control row
//   label          — the text label describing each stepper's purpose
//   navigationBar  — auto-detected (BP-17)
//
// Stepper value range and current value are seed-derived and deterministic.
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - StepperRowConfig

/// One stepper row in the list.
public struct StepperRowConfig: Sendable {
    public var label: String
    public var currentValue: Int
    public var minValue: Int
    public var maxValue: Int
    public var isDisabled: Bool

    public init(
        label: String,
        currentValue: Int,
        minValue: Int,
        maxValue: Int,
        isDisabled: Bool
    ) {
        self.label = label
        self.currentValue = currentValue
        self.minValue = minValue
        self.maxValue = maxValue
        self.isDisabled = isDisabled
    }
}

// MARK: - StepperConfig

/// Parameterised inputs for a single Stepper rendering.
public struct StepperConfig: Sendable {
    /// Navigation bar title.
    public var title: String
    /// Stepper rows (2–5 items).
    public var rows: [StepperRowConfig]
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(title: String, rows: [StepperRowConfig], colorScheme: ColorScheme) {
        self.title = title
        self.rows = rows
        self.colorScheme = colorScheme
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> StepperConfig {
        var rng = SeededRNG(seed: seed)
        let dark      = rng.next() % 2 == 0
        let rowCount  = 2 + Int(rng.next() % 4)   // 2–5 rows

        var rows: [StepperRowConfig] = []
        for idx in 0..<rowCount {
            let minV     = Int(rng.next() % 5)           // 0–4
            let range    = 5 + Int(rng.next() % 20)      // 5–24
            let maxV     = minV + range
            let currV    = minV + Int(rng.next() % UInt64(range + 1))
            let disabled = rng.next() % 5 == 0           // ~20%
            rows.append(StepperRowConfig(
                label: corpus.listRowTitle(),
                currentValue: currV,
                minValue: minV,
                maxValue: maxV,
                isDisabled: disabled
            ))
            _ = idx  // suppress warning
        }

        return StepperConfig(
            title: corpus.navigationTitle(),
            rows: rows,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - StepperTemplate

/// SwiftUI view rendering a list of stepper controls.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct StepperTemplate: View {
    public let config: StepperConfig

    public init(config: StepperConfig) {
        self.config = config
    }

    public var body: some View {
        NavigationStack {
            ZStack(alignment: .topLeading) {
                List {
                    Section {
                        ForEach(Array(config.rows.enumerated()), id: \.offset) { idx, row in
                            HStack {
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(row.label)
                                        .captureFrame(id: "label_\(idx)")
                                    Text("\(row.currentValue)")
                                        .font(.title2.monospacedDigit().bold())
                                        .foregroundStyle(Color.accentColor)
                                }

                                Spacer()

                                Stepper(
                                    "",
                                    value: .constant(row.currentValue),
                                    in: row.minValue...row.maxValue
                                )
                                .labelsHidden()
                                .disabled(row.isDisabled)
                                .opacity(row.isDisabled ? 0.4 : 1.0)
                                .captureFrame(id: "stepperControl_\(idx)")
                            }
                            .padding(.vertical, 4)
                        }
                    }
                }
                .listStyle(.insetGrouped)
            }
            .ignoresSafeArea(.all)
            .navigationTitle(config.title)
            .navigationBarTitleDisplayMode(.large)
            .colorScheme(config.colorScheme)
        }
        .colorScheme(config.colorScheme)
    }
}
