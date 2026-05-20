// ColorPickerTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI color picker / color well template (TASK-5b-22, class: colorWell).
// Covers UIColorWell / SwiftUI ColorPicker — a class not represented in any prior template.
//
// Annotated elements:
//   colorWell    — ColorPicker swatch (the tappable well)
//   label        — section header and item labels
//   navigationBar — auto-detected
//   primaryButton — Save / Apply button at bottom
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - ColorPickerConfig

public struct ColorPickerConfig: Sendable {
    public var title: String
    /// Primary color picker label.
    public var primaryLabel: String
    /// Selected color (hue 0–1, stored for determinism).
    public var primaryHue: Double
    /// Whether a second color picker is shown (accent color).
    public var showAccentPicker: Bool
    public var accentLabel: String
    public var accentHue: Double
    /// Save button label.
    public var saveLabel: String
    public var colorScheme: ColorScheme

    public init(
        title: String,
        primaryLabel: String,
        primaryHue: Double,
        showAccentPicker: Bool,
        accentLabel: String,
        accentHue: Double,
        saveLabel: String,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.primaryLabel = primaryLabel
        self.primaryHue = primaryHue
        self.showAccentPicker = showAccentPicker
        self.accentLabel = accentLabel
        self.accentHue = accentHue
        self.saveLabel = saveLabel
        self.colorScheme = colorScheme
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> ColorPickerConfig {
        var rng = SeededRNG(seed: seed)
        let dark       = rng.next() % 2 == 0
        let showAccent = rng.next() % 3 != 0   // ~67% show a second picker
        let hue1 = Double(rng.next() % 1000) / 1000.0
        let hue2 = Double(rng.next() % 1000) / 1000.0
        return ColorPickerConfig(
            title: corpus.navigationTitle(),
            primaryLabel: "Primary Color",
            primaryHue: hue1,
            showAccentPicker: showAccent,
            accentLabel: "Accent Color",
            accentHue: hue2,
            saveLabel: "Apply",
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - ColorPickerTemplate

public struct ColorPickerTemplate: View {
    public let config: ColorPickerConfig

    public init(config: ColorPickerConfig) {
        self.config = config
    }

    /// Binding-compatible color from hue (deterministic, opaque).
    private func color(from hue: Double) -> Color {
        Color(hue: hue, saturation: 0.75, brightness: 0.85)
    }

    public var body: some View {
        ZStack {
            Color(UIColor.systemGroupedBackground).ignoresSafeArea()

            NavigationStack {
                List {
                    // Primary color picker section
                    Section {
                        HStack {
                            Text(config.primaryLabel)
                                .font(.body)
                                .captureFrame(id: "label_primary")
                            Spacer()
                            // ColorPicker renders a color well swatch tappable by the user.
                            // The swatch itself is the `colorWell` annotation target.
                            ColorPicker("", selection: .constant(color(from: config.primaryHue)),
                                        supportsOpacity: false)
                                .labelsHidden()
                                .frame(width: 28, height: 28)
                                .captureFrame(id: "colorWell_0")
                        }
                        .padding(.vertical, 4)
                    } header: {
                        Text("Appearance")
                            .captureFrame(id: "label_section_appearance")
                    }

                    // Optional accent color picker section
                    if config.showAccentPicker {
                        Section {
                            HStack {
                                Text(config.accentLabel)
                                    .font(.body)
                                    .captureFrame(id: "label_accent")
                                Spacer()
                                ColorPicker("", selection: .constant(color(from: config.accentHue)),
                                            supportsOpacity: false)
                                    .labelsHidden()
                                    .frame(width: 28, height: 28)
                                    .captureFrame(id: "colorWell_1")
                            }
                            .padding(.vertical, 4)
                        } header: {
                            Text("Accent")
                                .captureFrame(id: "label_section_accent")
                        }
                    }

                    // Preview swatch section
                    Section {
                        HStack(spacing: 12) {
                            RoundedRectangle(cornerRadius: 8)
                                .fill(color(from: config.primaryHue))
                                .frame(width: 44, height: 44)
                            VStack(alignment: .leading, spacing: 2) {
                                Text("Preview")
                                    .font(.headline)
                                    .captureFrame(id: "label_preview_title")
                                Text("Color will apply to all themes")
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                                    .captureFrame(id: "label_preview_subtitle")
                            }
                        }
                        .padding(.vertical, 6)
                    }

                    // Save button as a full-width list row
                    Section {
                        Button(config.saveLabel) {}
                            .font(.body.bold())
                            .frame(maxWidth: .infinity, alignment: .center)
                            .foregroundStyle(Color.accentColor)
                            .captureFrame(id: "primaryButton_0")
                    }
                }
                .navigationTitle(config.title)
                .navigationBarTitleDisplayMode(.inline)
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}
