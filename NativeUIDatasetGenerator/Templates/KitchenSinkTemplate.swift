// KitchenSinkTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Dense smoke-test template that packs as many element types as possible onto
// one tall canvas. Captured at a custom window height (1100pt) so everything is
// visible in a single PNG — no scroll state to worry about.
//
// Purpose: visually validate that .captureFrame(id:) boxes align with elements
// across every major class before any real dataset generation begins.
//
// Annotated elements:
//   navigationBar, tabBar, homeIndicator
//   label, imageView, link
//   primaryButton, secondaryButton, destructiveButton, cancelAction
//   toggle, slider, stepperControl
//   textField, secureField
//   segmentedControl, picker (inline)
//   menuButton, colorWell
//   activityIndicator, progressView, pageControl
//   listRow, disclosureGroup
//   searchField (inline approximation)
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:)

import SwiftUI

// MARK: - KitchenSinkConfig

public struct KitchenSinkConfig: Sendable {
    public var colorScheme: ColorScheme
    public var disclosureExpanded: Bool
    public var toggleStates: [Bool]          // 3 values
    public var sliderValue: Double
    public var segmentIndex: Int
    public var pickerSelection: Int
    public var stepperValue: Int
    public var rowLabels: [String]           // 3 list row labels
    public var buttonLabel: String
    public var navTitle: String
    public var showHomeIndicator: Bool

    public init(
        colorScheme: ColorScheme,
        disclosureExpanded: Bool,
        toggleStates: [Bool],
        sliderValue: Double,
        segmentIndex: Int,
        pickerSelection: Int,
        stepperValue: Int,
        rowLabels: [String],
        buttonLabel: String,
        navTitle: String,
        showHomeIndicator: Bool
    ) {
        self.colorScheme = colorScheme
        self.disclosureExpanded = disclosureExpanded
        self.toggleStates = toggleStates
        self.sliderValue = sliderValue
        self.segmentIndex = segmentIndex
        self.pickerSelection = pickerSelection
        self.stepperValue = stepperValue
        self.rowLabels = rowLabels
        self.buttonLabel = buttonLabel
        self.navTitle = navTitle
        self.showHomeIndicator = showHomeIndicator
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> KitchenSinkConfig {
        var rng = SeededRNG(seed: seed)
        return KitchenSinkConfig(
            colorScheme: rng.next() % 2 == 0 ? .dark : .light,
            disclosureExpanded: rng.next() % 2 == 0,
            toggleStates: [rng.next() % 2 == 0, rng.next() % 2 == 0, rng.next() % 2 == 0],
            sliderValue: Double(rng.next() % 100) / 100.0,
            segmentIndex: Int(rng.next() % 3),
            pickerSelection: Int(rng.next() % 3),
            stepperValue: Int(rng.next() % 8) + 1,
            rowLabels: [corpus.listRowTitle(), corpus.listRowTitle(), corpus.listRowTitle()],
            buttonLabel: corpus.buttonLabel(),
            navTitle: corpus.navigationTitle(),
            showHomeIndicator: true
        )
    }
}

// MARK: - KitchenSinkTemplate

/// All-in-one template for smoke-testing bounding box capture across element classes.
///
/// Captured at 1100pt tall to fit all elements in one PNG without scroll state.
/// Use `ScreenshotCapture.capture(_:windowSize:config:)` with
/// `windowSize: CGSize(width: 393, height: 1100)`.
public struct KitchenSinkTemplate: View {
    public let config: KitchenSinkConfig

    public init(config: KitchenSinkConfig) {
        self.config = config
    }

    public var body: some View {
        TabView {
            NavigationStack {
                ZStack(alignment: .bottom) {
                    Color(UIColor.systemBackground).ignoresSafeArea()

                    ScrollView(.vertical, showsIndicators: false) {
                        VStack(alignment: .leading, spacing: 0) {
                            sectionHeader("label · imageView · link")
                                .padding(.horizontal, 16)
                                .padding(.top, 12)

                            HStack(spacing: 12) {
                                Text("Body text")
                                    .font(.body)
                                    .captureFrame(id: "label_body")

                                Text("Caption")
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                                    .captureFrame(id: "label_caption")

                                Image(systemName: "photo.fill")
                                    .font(.title3)
                                    .foregroundStyle(.teal)
                                    .captureFrame(id: "imageView_0")

                                Text("Learn more")
                                    .foregroundStyle(.blue)
                                    .underline()
                                    .captureFrame(id: "link_0")
                            }
                            .padding(.horizontal, 16)
                            .padding(.top, 6)

                            divider()

                            // MARK: Buttons
                            sectionHeader("primaryButton · secondaryButton · destructiveButton · cancelAction")
                                .padding(.horizontal, 16)

                            HStack(spacing: 8) {
                                Button(config.buttonLabel) {}
                                    .buttonStyle(.borderedProminent)
                                    .controlSize(.small)
                                    .captureFrame(id: "primaryButton_0")

                                Button("Details") {}
                                    .buttonStyle(.bordered)
                                    .controlSize(.small)
                                    .captureFrame(id: "secondaryButton_0")

                                Button("Delete", role: .destructive) {}
                                    .buttonStyle(.bordered)
                                    .controlSize(.small)
                                    .captureFrame(id: "destructiveButton_0")

                                Button("Cancel", role: .cancel) {}
                                    .controlSize(.small)
                                    .foregroundStyle(.secondary)
                                    .captureFrame(id: "cancelAction_0")
                            }
                            .padding(.horizontal, 16)
                            .padding(.top, 6)

                            divider()

                            // MARK: Toggle / Slider / Stepper
                            sectionHeader("toggle · slider · stepperControl")
                                .padding(.horizontal, 16)

                            HStack(spacing: 20) {
                                Toggle("", isOn: .constant(config.toggleStates[0]))
                                    .labelsHidden()
                                    .captureFrame(id: "toggle_0")

                                Toggle("", isOn: .constant(config.toggleStates[1]))
                                    .labelsHidden()
                                    .captureFrame(id: "toggle_1")

                                Toggle("", isOn: .constant(config.toggleStates[2]))
                                    .labelsHidden()
                                    .captureFrame(id: "toggle_2")

                                Spacer()

                                Stepper("\(config.stepperValue)", value: .constant(config.stepperValue), in: 0...10)
                                    .captureFrame(id: "stepperControl_0")
                            }
                            .padding(.horizontal, 16)
                            .padding(.top, 6)

                            Slider(value: .constant(config.sliderValue))
                                .padding(.horizontal, 16)
                                .padding(.top, 8)
                                .captureFrame(id: "slider_0")

                            divider()

                            // MARK: Text inputs
                            sectionHeader("textField · secureField · searchField")
                                .padding(.horizontal, 16)

                            VStack(spacing: 8) {
                                TextField("Email address", text: .constant(""))
                                    .textFieldStyle(.roundedBorder)
                                    .captureFrame(id: "textField_0")

                                SecureField("Password", text: .constant(""))
                                    .textFieldStyle(.roundedBorder)
                                    .captureFrame(id: "secureField_0")

                                HStack {
                                    Image(systemName: "magnifyingglass").foregroundStyle(.secondary)
                                    Text("Search…").foregroundStyle(.tertiary)
                                    Spacer()
                                }
                                .padding(8)
                                .background(.quaternary)
                                .clipShape(RoundedRectangle(cornerRadius: 10))
                                .captureFrame(id: "searchField_0")
                            }
                            .padding(.horizontal, 16)
                            .padding(.top, 6)

                            divider()

                            // MARK: Segmented control / Picker
                            sectionHeader("segmentedControl · picker")
                                .padding(.horizontal, 16)

                            Picker("View", selection: .constant(config.segmentIndex)) {
                                Text("All").tag(0)
                                Text("Active").tag(1)
                                Text("Done").tag(2)
                            }
                            .pickerStyle(.segmented)
                            .padding(.horizontal, 16)
                            .padding(.top, 6)
                            .captureFrame(id: "segmentedControl_0")

                            Picker("Options", selection: .constant(config.pickerSelection)) {
                                Text("Name").tag(0)
                                Text("Date").tag(1)
                                Text("Size").tag(2)
                            }
                            .pickerStyle(.wheel)
                            .frame(height: 88)
                            .clipped()
                            .padding(.horizontal, 16)
                            .captureFrame(id: "picker_0")

                            divider()

                            // MARK: Indicators / Menu / ColorPicker
                            sectionHeader("activityIndicator · progressView · menuButton · colorWell · pageControl")
                                .padding(.horizontal, 16)

                            HStack(spacing: 20) {
                                ProgressView()
                                    .captureFrame(id: "activityIndicator_0")

                                ProgressView(value: config.sliderValue)
                                    .frame(width: 90)
                                    .captureFrame(id: "progressView_0")

                                Menu("Options ▾") {
                                    Button("Share") {}
                                    Button("Rename") {}
                                    Button("Delete", role: .destructive) {}
                                }
                                .buttonStyle(.bordered)
                                .controlSize(.small)
                                .captureFrame(id: "menuButton_0")

                                ColorPicker("", selection: .constant(.blue))
                                    .labelsHidden()
                                    .captureFrame(id: "colorWell_0")

                                // pageControl approximation — dots row
                                HStack(spacing: 6) {
                                    ForEach(0..<3, id: \.self) { i in
                                        Circle()
                                            .fill(i == config.segmentIndex % 3 ? Color.primary : Color.secondary.opacity(0.4))
                                            .frame(width: 7, height: 7)
                                    }
                                }
                                .captureFrame(id: "pageControl_0")
                            }
                            .padding(.horizontal, 16)
                            .padding(.top, 6)

                            divider()

                            // MARK: List rows
                            sectionHeader("listRow")
                                .padding(.horizontal, 16)

                            VStack(spacing: 0) {
                                ForEach(Array(config.rowLabels.enumerated()), id: \.offset) { idx, label in
                                    HStack {
                                        Image(systemName: "person.circle.fill")
                                            .foregroundStyle(.blue)
                                        Text(label)
                                        Spacer()
                                        Image(systemName: "chevron.right")
                                            .foregroundStyle(.tertiary)
                                            .font(.caption)
                                    }
                                    .padding(.vertical, 10)
                                    .padding(.horizontal, 12)
                                    .captureFrame(id: "listRow_\(idx)")

                                    if idx < config.rowLabels.count - 1 {
                                        Divider().padding(.leading, 44)
                                    }
                                }
                            }
                            .background(Color(UIColor.secondarySystemBackground))
                            .clipShape(RoundedRectangle(cornerRadius: 10))
                            .padding(.horizontal, 16)
                            .padding(.top, 6)

                            divider()

                            // MARK: Disclosure group
                            sectionHeader("disclosureGroup")
                                .padding(.horizontal, 16)

                            DisclosureGroup(
                                isExpanded: .constant(config.disclosureExpanded)
                            ) {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text("Option A")
                                        .captureFrame(id: "label_disclosureA")
                                    Text("Option B")
                                        .captureFrame(id: "label_disclosureB")
                                }
                                .padding(.top, 4)
                            } label: {
                                Text("Advanced Settings")
                            }
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .captureFrame(id: "disclosureGroup_0")

                            // Breathing room so the home indicator doesn't overlap content
                            Spacer().frame(height: 60)
                        }
                    }

                    // MARK: Home indicator pill
                    if config.showHomeIndicator {
                        Capsule()
                            .fill(Color.primary.opacity(0.25))
                            .frame(width: 134, height: 5)
                            .padding(.bottom, 8)
                            .captureFrame(id: "homeIndicator")
                    }
                }
                .ignoresSafeArea(.all)
                .navigationTitle(config.navTitle)
                .navigationBarTitleDisplayMode(.inline)
                .colorScheme(config.colorScheme)
            }
            .captureFrame(id: "navigationBar")
            .tabItem { Label("Home", systemImage: "house") }

            Text("").tabItem { Label("Search", systemImage: "magnifyingglass") }
            Text("").tabItem { Label("Profile", systemImage: "person") }
        }
        .captureFrame(id: "tabBar")
        .colorScheme(config.colorScheme)
    }

    // MARK: - Helpers

    private func sectionHeader(_ text: String) -> some View {
        Text(text)
            .font(.system(size: 9, weight: .semibold, design: .monospaced))
            .foregroundStyle(.secondary)
            .padding(.bottom, 4)
    }

    private func divider() -> some View {
        Divider()
            .padding(.horizontal, 16)
            .padding(.vertical, 10)
    }
}
