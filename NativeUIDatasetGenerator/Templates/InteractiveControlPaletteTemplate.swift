// InteractiveControlPaletteTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised interactive control palette template for the 41-class holdout addon.
// Covers interactive controls and disclosure containers previously missing from holdout:
//   colorWell, menuButton, segmentedControl, slider, disclosureGroup,
//   toggle, stepperControl, navigationBar, listRow, label.
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset() (BP-01)
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - InteractiveControlPaletteConfig

public struct InteractiveControlPaletteConfig: Sendable {
    public var title: String
    public var selectedSegment: Int
    public var sliderValue1: Double
    public var sliderValue2: Double
    public var isToggleOn: Bool
    public var stepperValue: Int
    public var isDisclosureExpanded: Bool
    public var colorScheme: ColorScheme

    public init(
        title: String,
        selectedSegment: Int,
        sliderValue1: Double,
        sliderValue2: Double,
        isToggleOn: Bool,
        stepperValue: Int,
        isDisclosureExpanded: Bool,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.selectedSegment = selectedSegment
        self.sliderValue1 = sliderValue1
        self.sliderValue2 = sliderValue2
        self.isToggleOn = isToggleOn
        self.stepperValue = stepperValue
        self.isDisclosureExpanded = isDisclosureExpanded
        self.colorScheme = colorScheme
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> InteractiveControlPaletteConfig {
        var rng = SeededRNG(seed: seed)
        let isDark = (rng.next() % 2) == 0
        let segment = Int(rng.next() % 3)
        let s1 = Double(20 + (rng.next() % 70)) / 100.0
        let s2 = Double(10 + (rng.next() % 85)) / 100.0
        let toggleOn = (rng.next() % 2) == 0
        let stepper = 1 + Int(rng.next() % 9)
        let expanded = (rng.next() % 2) == 0

        let titles = ["Preferences", "Display & Audio", "Editor Settings", "Controls Setup", "Customization"]
        let title = titles[Int(rng.next() % UInt64(titles.count))]

        return InteractiveControlPaletteConfig(
            title: title,
            selectedSegment: segment,
            sliderValue1: s1,
            sliderValue2: s2,
            isToggleOn: toggleOn,
            stepperValue: stepper,
            isDisclosureExpanded: expanded,
            colorScheme: isDark ? .dark : .light
        )
    }
}

// MARK: - InteractiveControlPaletteTemplate View

public struct InteractiveControlPaletteTemplate: View {
    public let config: InteractiveControlPaletteConfig

    public init(config: InteractiveControlPaletteConfig) {
        self.config = config
    }

    private var isDark: Bool { config.colorScheme == .dark }
    private var bgColor: Color { isDark ? Color.black : Color(white: 0.95) }
    private var cardBg: Color { isDark ? Color(white: 0.16) : Color.white }
    private var textColor: Color { isDark ? .white : .black }
    private var subtextColor: Color { isDark ? Color(white: 0.65) : Color(white: 0.45) }

    public var body: some View {
        ZStack(alignment: .top) {
            bgColor.ignoresSafeArea(.all)

            VStack(spacing: 0) {
                // Top Navigation Bar
                HStack {
                    Text(config.title)
                        .font(.title2.weight(.bold))
                        .foregroundColor(textColor)
                        .captureFrame(id: "label_headerTitle")

                    Spacer()

                    Button(action: {}) {
                        Text("Reset")
                            .font(.body)
                            .foregroundColor(.blue)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 54)
                .padding(.bottom, 12)
                .background(isDark ? Color(white: 0.12) : Color(white: 0.98))
                .captureFrame(id: "navigationBar_controlsHeader")

                ScrollView {
                    VStack(spacing: 16) {
                        // 1. Segmented Control row
                        renderSegmentedControl()

                        // 2. Sliders Panel
                        renderSlidersPanel()

                        // 3. ColorWell & MenuButton Panel
                        renderColorAndMenuPanel()

                        // 4. Toggle & Stepper Panel
                        renderToggleAndStepperPanel()

                        // 5. Disclosure Group Section
                        renderDisclosureSection()
                    }
                    .padding(.horizontal, 16)
                    .padding(.top, 16)
                    .padding(.bottom, 40)
                }
            }
        }
        .preferredColorScheme(config.colorScheme)
    }

    // MARK: - Component Rows

    @ViewBuilder
    private func renderSegmentedControl() -> some View {
        HStack(spacing: 0) {
            ForEach(["Standard", "Compact", "Expanded"], id: \.self) { segment in
                let selected = (segment == "Standard" && config.selectedSegment == 0) ||
                               (segment == "Compact" && config.selectedSegment == 1) ||
                               (segment == "Expanded" && config.selectedSegment == 2)
                Text(segment)
                    .font(.footnote.weight(selected ? .semibold : .regular))
                    .foregroundColor(selected ? textColor : subtextColor)
                    .frame(maxWidth: .infinity, minHeight: 32)
                    .background(selected ? cardBg : Color.clear)
                    .cornerRadius(7)
                    .padding(2)
            }
        }
        .padding(2)
        .background(isDark ? Color(white: 0.25) : Color(white: 0.88))
        .cornerRadius(9)
        .captureFrame(id: "segmentedControl_modeSelector")
    }

    @ViewBuilder
    private func renderSlidersPanel() -> some View {
        VStack(spacing: 14) {
            // Slider 1: Brightness
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    Image(systemName: "sun.max.fill").foregroundColor(.orange)
                    Text("Brightness")
                        .font(.subheadline)
                        .foregroundColor(textColor)
                        .captureFrame(id: "label_sliderLabel1")
                    Spacer()
                    Text("\(Int(config.sliderValue1 * 100))%")
                        .font(.footnote)
                        .foregroundColor(subtextColor)
                }

                // Slider visual representation
                GeometryReader { geo in
                    ZStack(alignment: .leading) {
                        Capsule().fill(Color.gray.opacity(0.3)).frame(height: 6)
                        Capsule().fill(Color.blue).frame(width: geo.size.width * CGFloat(config.sliderValue1), height: 6)
                        Circle().fill(Color.white).shadow(radius: 2).frame(width: 24, height: 24)
                            .padding(.leading, max(0, geo.size.width * CGFloat(config.sliderValue1) - 12))
                    }
                }
                .frame(height: 28)
                .captureFrame(id: "slider_brightness")
            }

            Divider()

            // Slider 2: Audio Volume
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    Image(systemName: "speaker.wave.3.fill").foregroundColor(.blue)
                    Text("Master Volume")
                        .font(.subheadline)
                        .foregroundColor(textColor)
                        .captureFrame(id: "label_sliderLabel2")
                    Spacer()
                    Text("\(Int(config.sliderValue2 * 100))%")
                        .font(.footnote)
                        .foregroundColor(subtextColor)
                }

                GeometryReader { geo in
                    ZStack(alignment: .leading) {
                        Capsule().fill(Color.gray.opacity(0.3)).frame(height: 6)
                        Capsule().fill(Color.blue).frame(width: geo.size.width * CGFloat(config.sliderValue2), height: 6)
                        Circle().fill(Color.white).shadow(radius: 2).frame(width: 24, height: 24)
                            .padding(.leading, max(0, geo.size.width * CGFloat(config.sliderValue2) - 12))
                    }
                }
                .frame(height: 28)
                .captureFrame(id: "slider_volume")
            }
        }
        .padding(14)
        .background(cardBg)
        .cornerRadius(12)
        .captureFrame(id: "listRow_sliderGroup")
    }

    @ViewBuilder
    private func renderColorAndMenuPanel() -> some View {
        VStack(spacing: 0) {
            // ColorWell Row
            HStack {
                Text("Theme Accent Color")
                    .font(.body)
                    .foregroundColor(textColor)
                    .captureFrame(id: "label_colorWellTitle")

                Spacer()

                // ColorWell element
                Circle()
                    .fill(LinearGradient(colors: [.indigo, .purple, .pink], startPoint: .topLeading, endPoint: .bottomTrailing))
                    .frame(width: 28, height: 28)
                    .overlay(Circle().stroke(Color.white, lineWidth: 2).shadow(radius: 1))
                    .captureFrame(id: "colorWell_accentPicker")
            }
            .padding(14)

            Divider()

            // MenuButton Row
            HStack {
                Text("Export Quality")
                    .font(.body)
                    .foregroundColor(textColor)
                    .captureFrame(id: "label_menuTitle")

                Spacer()

                // Menu button pill
                HStack(spacing: 4) {
                    Text("ProRes 422")
                        .font(.subheadline)
                        .foregroundColor(.blue)
                    Image(systemName: "chevron.up.chevron.down")
                        .font(.caption2)
                        .foregroundColor(.blue)
                }
                .padding(.horizontal, 10)
                .padding(.vertical, 6)
                .background(Color.blue.opacity(0.12))
                .cornerRadius(8)
                .captureFrame(id: "menuButton_qualitySelector")
            }
            .padding(14)
        }
        .background(cardBg)
        .cornerRadius(12)
        .captureFrame(id: "listRow_pickerMenuRow")
    }

    @ViewBuilder
    private func renderToggleAndStepperPanel() -> some View {
        VStack(spacing: 0) {
            // Toggle
            HStack {
                Text("Enable Background Sync")
                    .font(.body)
                    .foregroundColor(textColor)
                    .captureFrame(id: "label_toggleText")

                Spacer()

                Capsule()
                    .fill(config.isToggleOn ? Color.green : Color.gray.opacity(0.4))
                    .frame(width: 51, height: 31)
                    .overlay(
                        Circle().fill(Color.white).shadow(radius: 1).frame(width: 27, height: 27)
                            .padding(.leading, config.isToggleOn ? 20 : 2),
                        alignment: .leading
                    )
                    .captureFrame(id: "toggle_syncSwitch")
            }
            .padding(14)

            Divider()

            // StepperControl
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Retain Copies")
                        .font(.body)
                        .foregroundColor(textColor)
                        .captureFrame(id: "label_stepperTitle")
                    Text("\(config.stepperValue) items saved")
                        .font(.caption)
                        .foregroundColor(subtextColor)
                }

                Spacer()

                HStack(spacing: 0) {
                    Button(action: {}) {
                        Image(systemName: "minus")
                            .frame(width: 44, height: 32)
                            .foregroundColor(.blue)
                    }
                    Divider().frame(height: 20)
                    Button(action: {}) {
                        Image(systemName: "plus")
                            .frame(width: 44, height: 32)
                            .foregroundColor(.blue)
                    }
                }
                .background(isDark ? Color(white: 0.25) : Color(white: 0.90))
                .cornerRadius(8)
                .captureFrame(id: "stepperControl_copyCount")
            }
            .padding(14)
        }
        .background(cardBg)
        .cornerRadius(12)
        .captureFrame(id: "listRow_toggleStepperRow")
    }

    @ViewBuilder
    private func renderDisclosureSection() -> some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Image(systemName: config.isDisclosureExpanded ? "chevron.down" : "chevron.right")
                    .font(.footnote.weight(.semibold))
                    .foregroundColor(.blue)

                Text("Advanced Diagnostics & Logs")
                    .font(.subheadline.weight(.medium))
                    .foregroundColor(textColor)
                    .captureFrame(id: "label_disclosureTitle")

                Spacer()
            }
            .padding(14)
            .background(cardBg)
            .cornerRadius(12)
            .captureFrame(id: "disclosureGroup_diagnostics")

            if config.isDisclosureExpanded {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Device logs and traces are active.")
                        .font(.caption)
                        .foregroundColor(subtextColor)
                    Text("Storage used: 142.6 MB of cache.")
                        .font(.caption)
                        .foregroundColor(subtextColor)
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
            }
        }
    }
}
