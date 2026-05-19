// RTLMirrorTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI RTL mirror template (TASK-5b-12).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// This template renders the same element classes as Phase 3c templates but
// forces right-to-left layout direction — satisfying the 15% RTL coverage
// requirement from Research/TrainingDataStrategy.md Section 9.
//
// Annotated elements:
//   navigationBar (auto), listRow, toggle, label, textField, primaryButton
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)
//
// RTL is applied via .environment(\.layoutDirection, .rightToLeft) on the root view.

import SwiftUI
import UIKit

// MARK: - RTLMirrorConfig

/// Parameterised inputs for a single RTLMirror rendering.
public struct RTLMirrorConfig: Sendable {
    /// Navigation bar title.
    public var title: String
    /// List row labels (4–8 items).
    public var rowLabels: [String]
    /// Toggle row labels (2–3 items).
    public var toggleLabels: [String]
    /// Text field placeholder.
    public var placeholder: String
    /// Primary button label.
    public var primaryButtonLabel: String
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        title: String,
        rowLabels: [String],
        toggleLabels: [String],
        placeholder: String,
        primaryButtonLabel: String,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.rowLabels = rowLabels
        self.toggleLabels = toggleLabels
        self.placeholder = placeholder
        self.primaryButtonLabel = primaryButtonLabel
        self.colorScheme = colorScheme
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> RTLMirrorConfig {
        var rng = SeededRNG(seed: seed)
        let dark       = rng.next() % 2 == 0
        let rowCount   = 4 + Int(rng.next() % 5)   // 4–8 rows
        let toggleCount = 2 + Int(rng.next() % 2)  // 2–3 toggles

        var rows: [String] = []
        for _ in 0..<rowCount { rows.append(corpus.listRowTitle()) }
        var toggles: [String] = []
        for _ in 0..<toggleCount { toggles.append(corpus.listRowTitle()) }

        return RTLMirrorConfig(
            title: corpus.navigationTitle(),
            rowLabels: rows,
            toggleLabels: toggles,
            placeholder: corpus.email(),
            primaryButtonLabel: corpus.buttonLabel(),
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - RTLMirrorTemplate

/// SwiftUI view rendering a standard settings-style list in RTL layout.
///
/// The `.environment(\.layoutDirection, .rightToLeft)` modifier mirrors all
/// standard SwiftUI chrome: navigation back arrow appears on right, list
/// leading edges on right, HStack items reverse direction.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct RTLMirrorTemplate: View {
    public let config: RTLMirrorConfig

    public init(config: RTLMirrorConfig) {
        self.config = config
    }

    public var body: some View {
        NavigationStack {
            ZStack(alignment: .topLeading) {
                List {
                    // Text field section
                    Section {
                        TextField(config.placeholder, text: .constant(""))
                            .textContentType(.emailAddress)
                            .captureFrame(id: "textField_0")
                    }

                    // Toggle rows
                    Section {
                        ForEach(Array(config.toggleLabels.enumerated()), id: \.offset) { idx, label in
                            HStack {
                                Text(label)
                                    .captureFrame(id: "label_toggle_\(idx)")
                                Spacer()
                                Toggle("", isOn: .constant(idx % 2 == 0))
                                    .labelsHidden()
                                    .captureFrame(id: "toggle_\(idx)")
                            }
                            .captureFrame(id: "listRow_toggle_\(idx)")
                        }
                    }

                    // Plain list rows
                    Section {
                        ForEach(Array(config.rowLabels.enumerated()), id: \.offset) { idx, label in
                            Text(label)
                                .captureFrame(id: "label_row_\(idx)")
                                .captureFrame(id: "listRow_\(idx)")
                        }
                    }
                }
                .listStyle(.insetGrouped)

                // Primary button pinned to bottom
                VStack {
                    Spacer()
                    Button(config.primaryButtonLabel) {}
                        .frame(maxWidth: .infinity, minHeight: 50)
                        .background(Color.accentColor)
                        .foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                        .captureFrame(id: "primaryButton_0")
                        .padding(.horizontal, 20)
                        .padding(.bottom, 32)
                }
            }
            .ignoresSafeArea(.all)
            .navigationTitle(config.title)
            .navigationBarTitleDisplayMode(.large)
            .colorScheme(config.colorScheme)
        }
        // Force right-to-left layout for this entire template (RTL coverage).
        .environment(\.layoutDirection, .rightToLeft)
        .colorScheme(config.colorScheme)
    }
}
