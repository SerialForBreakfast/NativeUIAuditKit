// PickerDateEntryTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI picker / date entry template (TASK-5b-9).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// Annotated elements:
//   picker        — the date/time picker component
//   navigationBar — auto-detected via UIKit scan (BP-17)
//   primaryButton — confirm / done action
//   cancelAction  — cancel / dismiss action
//
// Picker style variants: wheel (inline), compact, graphical (calendar).
// Date values are fixed by seed — never Date() (prevents content bias).
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - PickerStyle (generator)

/// Picker display style for training variety.
public enum GeneratorPickerStyle: String, Sendable {
    case wheel      // UIDatePickerStyle.wheels
    case compact    // UIDatePickerStyle.compact (single-line badge)
    case graphical  // UIDatePickerStyle.inline (full calendar)
}

// MARK: - PickerDateEntryConfig

/// Parameterised inputs for a single PickerDateEntry rendering.
public struct PickerDateEntryConfig: Sendable {
    /// Navigation bar title.
    public var title: String
    /// The date to show in the picker (fixed, seed-derived).
    public var year: Int
    public var month: Int
    public var day: Int
    public var hour: Int
    public var minute: Int
    /// Picker display style.
    public var pickerStyle: GeneratorPickerStyle
    /// When true, picker shows date + time. When false, date only.
    public var includesTime: Bool
    /// Primary confirm button label.
    public var primaryButtonLabel: String
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        title: String,
        year: Int, month: Int, day: Int,
        hour: Int, minute: Int,
        pickerStyle: GeneratorPickerStyle,
        includesTime: Bool,
        primaryButtonLabel: String,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.pickerStyle = pickerStyle
        self.includesTime = includesTime
        self.primaryButtonLabel = primaryButtonLabel
        self.colorScheme = colorScheme
    }

    /// Computed date from fixed components — deterministic, no Date() reference.
    var pickerDate: Date {
        var comps = DateComponents()
        comps.year = year; comps.month = month; comps.day = day
        comps.hour = hour; comps.minute = minute
        return Calendar.current.date(from: comps) ?? Date(timeIntervalSinceReferenceDate: 0)
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> PickerDateEntryConfig {
        var rng = SeededRNG(seed: seed)
        let dark        = rng.next() % 2 == 0
        let styleChoice = rng.next() % 3
        let style: GeneratorPickerStyle
        switch styleChoice {
        case 0:  style = .wheel
        case 1:  style = .compact
        default: style = .graphical
        }
        // Sweep dates across a 3-year range starting from 2024-01-01.
        let yearOffset  = Int(rng.next() % 3)        // 2024–2026
        let month       = 1 + Int(rng.next() % 12)  // 1–12
        let day         = 1 + Int(rng.next() % 28)  // 1–28
        let hour        = Int(rng.next() % 24)
        let minute      = Int(rng.next() % 60)
        let includesTime = rng.next() % 3 != 0       // ~67%

        return PickerDateEntryConfig(
            title: corpus.navigationTitle(),
            year: 2024 + yearOffset,
            month: month,
            day: day,
            hour: hour,
            minute: minute,
            pickerStyle: style,
            includesTime: includesTime,
            primaryButtonLabel: corpus.buttonLabel(),
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - PickerDateEntryTemplate

/// SwiftUI view rendering a date/time picker sheet.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct PickerDateEntryTemplate: View {
    public let config: PickerDateEntryConfig

    public init(config: PickerDateEntryConfig) {
        self.config = config
    }

    @ViewBuilder
    private var pickerView: some View {
        let components: DatePickerComponents = config.includesTime
            ? [.date, .hourAndMinute]
            : [.date]

        switch config.pickerStyle {
        case .wheel:
            DatePicker("", selection: .constant(config.pickerDate), displayedComponents: components)
                .datePickerStyle(.wheel)
                .labelsHidden()
                .captureFrame(id: "picker_0")
        case .compact:
            DatePicker("Select date", selection: .constant(config.pickerDate), displayedComponents: components)
                .datePickerStyle(.compact)
                .captureFrame(id: "picker_0")
                .padding(.horizontal, 20)
        case .graphical:
            DatePicker("", selection: .constant(config.pickerDate), displayedComponents: components)
                .datePickerStyle(.graphical)
                .captureFrame(id: "picker_0")
                .padding(.horizontal, 12)
        }
    }

    public var body: some View {
        NavigationStack {
            ZStack(alignment: .topLeading) {
                Color(UIColor.systemGroupedBackground).ignoresSafeArea()

                VStack(spacing: 0) {
                    pickerView
                        .padding(.top, 16)

                    Spacer()

                    // Primary button
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
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {}
                        .captureFrame(id: "cancelAction_0")
                }
            }
            .colorScheme(config.colorScheme)
        }
        // navigationBar auto-detected by ScreenshotCapture.detectChromeFrames (BP-17).
        .colorScheme(config.colorScheme)
    }
}
