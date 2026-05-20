// GenerateDatasetTests.swift
// GeneratorRunnerTests
//
// Hosted XCTest that generates the Phase 3e-1 dataset.
//
// Runs inside the iOS Simulator via `xcodebuild test`. Each test method generates
// 200 images for one template family and writes PNG + annotation JSON files to
// the app's Documents directory. The macOS NativeUIDatasetGenerator orchestrator
// locates the output directory via `xcrun simctl get_app_container` after the
// test run completes and copies the files to the dataset root.
//
// Output layout (inside Documents/dataset/):
//   train/img_NNNNNN.png
//   train/img_NNNNNN.json
//   validation/img_NNNNNN.png
//   validation/img_NNNNNN.json
//   test/img_NNNNNN.png
//   test/img_NNNNNN.json
//   manifest.json
//
// Split ratios: 80% train / 10% validation / 10% test (by imageIndex % 10).
//
// Concurrency: All capture work runs on @MainActor (UIKit requirement).
// The test methods are async and hop to @MainActor via ScreenshotCapture.
//
// Simulator state overrides in annotation metadata:
// The SimulatorStateOverride embedded in each config records 5 distinct time
// values across the sweep, satisfying TASK-3e-1 AC. The macOS orchestrator
// is responsible for actually setting the simulator status bar via
// `xcrun simctl status_bar` before each test run (see SimulatorStateManager).

import XCTest
import SwiftUI
import UIKit

// MARK: - GenerateDatasetTests

/// Generates all Phase 3e-1 training images inside the iOS Simulator.
///
/// Run order (alphabetical): Alert → LoginForm → SettingsList.
/// Each method generates 200 images; 600 total across the three templates.
///
/// **Threading:** Class is `@MainActor` — all SwiftUI rendering must occur on
/// the main thread. `async throws` test methods yield to the run loop between captures.
@MainActor
final class GenerateDatasetTests: XCTestCase {

    // MARK: - Fixtures

    /// Root output directory inside the simulator app's Documents container.
    private let datasetDir: URL = {
        FileManager.default
            .urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appending(path: "dataset", directoryHint: .isDirectory)
    }()

    /// Five distinct simulator state overrides, rotated across the image sweep.
    /// Records different time/battery/cellular values in annotation metadata,
    /// satisfying the TASK-3e-1 AC for ≥5 distinct time values.
    private let simulatorStates: [SimulatorStateOverride] = [
        SimulatorStateOverride(
            time: "09:41", batteryLevel: 100, batteryState: "charging",
            cellularBars: 5, wifiBars: 3, cellularMode: "active", operatorName: ""
        ),
        SimulatorStateOverride(
            time: "12:30", batteryLevel: 75, batteryState: "discharging",
            cellularBars: 3, wifiBars: 3, cellularMode: "active", operatorName: ""
        ),
        SimulatorStateOverride(
            time: "18:05", batteryLevel: 50, batteryState: "discharging",
            cellularBars: 1, wifiBars: 1, cellularMode: "active", operatorName: ""
        ),
        SimulatorStateOverride(
            time: "22:15", batteryLevel: 25, batteryState: "discharging",
            cellularBars: 0, wifiBars: 0, cellularMode: "notSupported", operatorName: ""
        ),
        SimulatorStateOverride(
            time: "07:00", batteryLevel: 10, batteryState: "discharging",
            cellularBars: 5, wifiBars: 3, cellularMode: "active", operatorName: "AT&T"
        ),
    ]

    // MARK: - Set-up

    override func setUp() async throws {
        let fm = FileManager.default
        for split in ["train", "validation", "test"] {
            let dir = datasetDir.appending(path: split, directoryHint: .isDirectory)
            try fm.createDirectory(at: dir, withIntermediateDirectories: true)
        }
    }

    // MARK: - Test methods

    /// Generates 200 alert template images (seeds 2001–2200).
    /// Runs first alphabetically — initialises the manifest.
    func testGenerateAlertImages() async throws {
        try await generateImages(templateFamily: "Alert", count: 200, startSeed: 2001)
    }

    /// Generates 200 login-form template images (seeds 1001–1200).
    func testGenerateLoginFormImages() async throws {
        try await generateImages(templateFamily: "LoginForm", count: 200, startSeed: 1001)
    }

    /// Generates 200 settings-list template images (seeds 3001–3200).
    func testGenerateSettingsListImages() async throws {
        try await generateImages(templateFamily: "SettingsList", count: 200, startSeed: 3001)
    }

    // MARK: - Phase 4: UIKit generator (≥2,000 images, anti-overfitting requirement)

    /// Generates 700 UIKit form (sign-in) template images (seeds 4001–4700).
    /// UIKitFormViewController: navigationBar + label × 2 + textField + secureField +
    /// primaryButton + secondaryButton.
    func testGenerateUIKitFormImages() async throws {
        try await generateUIKitImages(templateFamily: "UIKitForm", count: 700, startSeed: 4001)
    }

    /// Generates 700 UIKit list template images (seeds 5001–5700).
    /// UIKitListViewController: navigationBar + tabBar + tabBarItem × 4 +
    /// listRow × 5 + toggle × 2.
    func testGenerateUIKitListImages() async throws {
        try await generateUIKitImages(templateFamily: "UIKitList", count: 700, startSeed: 5001)
    }

    /// Generates 700 UIKit controls showcase images (seeds 6001–6700).
    /// UIKitControlsViewController: navigationBar + slider + segmentedControl +
    /// activityIndicator + progressView + pageControl + toggle.
    /// Runs last — manifest write after this method includes all 2,700 entries.
    func testGenerateUIKitControlsImages() async throws {
        try await generateUIKitImages(templateFamily: "UIKitControls", count: 700, startSeed: 6001)
    }

    // MARK: - Core generation loop

    /// Generates `count` images for the given template family, appending to the shared manifest.
    ///
    /// - Parameters:
    ///   - templateFamily: `"LoginForm"`, `"SettingsList"`, or `"Alert"`.
    ///   - count: Number of images to generate.
    ///   - startSeed: First seed value; subsequent images use `startSeed + i`.
    private func generateImages(
        templateFamily: String,
        count: Int,
        startSeed: UInt64,
        locale: String = "en_US",
        layoutDirection: GeneratorLayoutDirection = .ltr,
        forceProfile: OSVisualProfile? = nil,
        accessibilityFlags: AccessibilityFlags = .default
    ) async throws {
        let manifestURL = datasetDir.appending(path: "manifest.json")
        var manifest = try DatasetManifest.load(from: manifestURL)

        for i in 0..<count {
            let seed = startSeed + UInt64(i)
            let state = simulatorStates[i % simulatorStates.count]
            var config = makeConfig(seed: seed, index: i, templateFamily: templateFamily, state: state)
            // Apply optional overrides.
            if let profile = forceProfile {
                config.osProfile = profile
                config.deviceName = profile == .ios26 ? "iPhone 17 Pro" : "iPhone SE (3rd generation)"
                config.pixelScale = profile == .ios26 ? 3 : 2
            }
            config.locale = locale
            config.layoutDirection = layoutDirection
            config.accessibilityFlags = accessibilityFlags

            var corpus = ContentCorpus(seed: seed)
            let result = try await capture(templateFamily: templateFamily, seed: seed, config: config, corpus: &corpus)

            let imageIndex = manifest.imageCount + 1
            let split = splitFor(imageIndex: imageIndex)
            let baseName = String(format: "img_%06d", imageIndex)
            let pngName  = baseName + ".png"
            let jsonName = baseName + ".json"

            let splitDir = datasetDir.appending(path: split.rawValue, directoryHint: .isDirectory)
            try result.png.write(to: splitDir.appending(path: pngName))
            try AnnotationWriter.write(
                result: result,
                config: config,
                imageFileName: pngName,
                templateFamily: templateFamily,
                generatorVersion: "0.1.0",
                to: splitDir.appending(path: jsonName)
            )

            let entry = ManifestEntry(
                fileName: "\(split.rawValue)/\(pngName)",
                split: split,
                sha256: result.sha256,
                templateFamily: templateFamily,
                generatorSeed: seed,
                simulatorState: state,
                isolationTemplate: config.isolationTemplate,
                lowDensity: config.lowDensity,
                deviceName: config.deviceName,
                pixelScale: config.pixelScale
            )
            manifest.append(entry, elementTypes: result.elements.map(\.elementType))
        }

        try manifest.save(to: manifestURL)
    }

    // MARK: - Capture dispatch

    /// Calls the correct template's `ScreenshotCapture.capture` for the given family.
    ///
    /// - Parameters:
    ///   - templateFamily: Template to render.
    ///   - seed: Deterministic seed for the config factory.
    ///   - config: `GeneratorRunConfig` passed to `ScreenshotCapture.capture`.
    ///   - corpus: Seeded text corpus (mutated by the factory call).
    /// - Returns: `CaptureResult` with PNG, SHA-256, and element frames.
    /// - Throws: `GenerateDatasetError.unknownTemplateFamily` for unrecognised families.
    private func capture(
        templateFamily: String,
        seed: UInt64,
        config: GeneratorRunConfig,
        corpus: inout ContentCorpus
    ) async throws -> CaptureResult {
        switch templateFamily {
        case "LoginForm":
            let formConfig = LoginFormConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(LoginFormTemplate(config: formConfig), config: config)
        case "SettingsList":
            let listConfig = SettingsListConfig.make(seed: seed, corpus: &corpus, hasHomeIndicator: config.osProfile.hasHomeIndicator)
            return try await ScreenshotCapture.capture(SettingsListTemplate(config: listConfig), config: config)
        case "Alert":
            let alertConfig = AlertConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(AlertTemplate(config: alertConfig), config: config)
        case "TabViewNavigation":
            let tabConfig = TabViewNavigationConfig.make(seed: seed, corpus: &corpus, osProfile: config.osProfile)
            return try await ScreenshotCapture.capture(TabViewNavigationTemplate(config: tabConfig), config: config)
        case "Sheet":
            let sheetConfig = SheetConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(SheetTemplate(config: sheetConfig), config: config)
        case "SearchResults":
            let srConfig = SearchResultsConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(SearchResultsTemplate(config: srConfig), config: config)
        case "FormValidation":
            let fvConfig = FormValidationConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(FormValidationTemplate(config: fvConfig), config: config)
        case "EmptyState":
            let esConfig = EmptyStateConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(EmptyStateTemplate(config: esConfig), config: config)
        case "LoadingSkeleton":
            let lsConfig = LoadingSkeletonConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(LoadingSkeletonTemplate(config: lsConfig), config: config)
        case "MediaCardGrid":
            let mcgConfig = MediaCardGridConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(MediaCardGridTemplate(config: mcgConfig), config: config)
        case "OnboardingPage":
            let obConfig = OnboardingPageConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(OnboardingPageTemplate(config: obConfig), config: config)
        case "PickerDateEntry":
            let pdConfig = PickerDateEntryConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(PickerDateEntryTemplate(config: pdConfig), config: config)
        case "ActionSheet":
            let asConfig = ActionSheetConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(ActionSheetTemplate(config: asConfig), config: config)
        case "Popover":
            let popConfig = PopoverConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(PopoverTemplate(config: popConfig), config: config)
        case "RTLMirror":
            let rtlConfig = RTLMirrorConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(RTLMirrorTemplate(config: rtlConfig), config: config)
        case "LiquidGlassNav":
            let lgnConfig = LiquidGlassNavConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(LiquidGlassNavTemplate(config: lgnConfig), config: config)
        case "LiquidGlassTab":
            let lgtConfig = LiquidGlassTabConfig.make(seed: seed, corpus: &corpus, osProfile: config.osProfile)
            return try await ScreenshotCapture.capture(LiquidGlassTabTemplate(config: lgtConfig), config: config)
        case "SettingsDisclosure":
            let sdConfig = SettingsDisclosureConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(SettingsDisclosureTemplate(config: sdConfig), config: config)
        case "RefreshControl":
            let rcConfig = RefreshControlConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(RefreshControlTemplate(config: rcConfig), config: config)
        case "ContextMenu":
            let cmConfig = ContextMenuConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(ContextMenuTemplate(config: cmConfig), config: config)
        case "MapOverlays":
            let moConfig = MapOverlaysConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(MapOverlaysTemplate(config: moConfig), config: config)
        case "Stepper":
            let stConfig = StepperConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(StepperTemplate(config: stConfig), config: config)
        case "ProgressActivity":
            let paConfig = ProgressActivityConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(ProgressActivityTemplate(config: paConfig), config: config)
        case "ColorPicker":
            let cpConfig = ColorPickerConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(ColorPickerTemplate(config: cpConfig), config: config)
        case "MenuButton":
            let mbConfig = MenuButtonConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(MenuButtonTemplate(config: mbConfig), config: config)
        case "LinkRichText":
            let lrtConfig = LinkRichTextConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(LinkRichTextTemplate(config: lrtConfig), config: config)
        case "SliderPanel":
            let spConfig = SliderPanelConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(SliderPanelTemplate(config: spConfig), config: config)
        case "SegmentedFilter":
            let sfConfig = SegmentedFilterConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(SegmentedFilterTemplate(config: sfConfig), config: config)
        case "CardDetail":
            let cdConfig = CardDetailConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(CardDetailTemplate(config: cdConfig), config: config)
        case "MultiSectionForm":
            let msfConfig = MultiSectionFormConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(MultiSectionFormTemplate(config: msfConfig), config: config)
        case "ToolbarActions":
            let taConfig = ToolbarActionsConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(ToolbarActionsTemplate(config: taConfig), config: config)
        case "WizardStepFlow":
            let wsfConfig = WizardStepFlowConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(WizardStepFlowTemplate(config: wsfConfig), config: config)
        case "NotificationCenter":
            let ncConfig = NotificationCenterConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(NotificationCenterTemplate(config: ncConfig), config: config)
        case "GalleryPage":
            let gpConfig = GalleryPageConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(GalleryPageTemplate(config: gpConfig), config: config)
        case "iPadSidebar":
            let isConfig = iPadSidebarConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(iPadSidebarTemplate(config: isConfig), config: config)
        case "AlertWithTextField":
            let awtConfig = AlertWithTextFieldConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(AlertWithTextFieldTemplate(config: awtConfig), config: config)
        case "SettingsToggleDense":
            let stdConfig = SettingsToggleDenseConfig.make(seed: seed, corpus: &corpus)
            return try await ScreenshotCapture.capture(SettingsToggleDenseTemplate(config: stdConfig), config: config)
        default:
            throw GenerateDatasetError.unknownTemplateFamily(templateFamily)
        }
    }

    // MARK: - Config factory

    /// Builds a `GeneratorRunConfig` for one image, varying device, color scheme,
    /// DynamicType, and simulator state based on `index` and `seed`.
    private func makeConfig(
        seed: UInt64,
        index: Int,
        templateFamily: String,
        state: SimulatorStateOverride
    ) -> GeneratorRunConfig {
        // Alternate between a high-DPI iPhone (@3x) and a compact iPhone (@2x).
        let highDPI = index % 2 == 0
        let osProfile: OSVisualProfile = highDPI ? .ios26 : .ios17
        let deviceName = highDPI ? "iPhone 17 Pro" : "iPhone SE (3rd generation)"
        let pixelScale = highDPI ? 3 : 2

        return GeneratorRunConfig(
            seed: seed,
            templateFamily: templateFamily,
            osProfile: osProfile,
            simulatorOverride: state,
            colorScheme: index % 2 == 0 ? .dark : .light,
            dynamicTypeSize: dynamicTypeSize(for: index),
            deviceName: deviceName,
            pixelScale: pixelScale,
            locale: "en_US",
            layoutDirection: .ltr,
            accessibilityFlags: .default
        )
    }

    // MARK: - UIKit generation loop (Phase 4)

    /// Generates `count` UIKit images for the given template family.
    ///
    /// Mirrors `generateImages` but calls `ScreenshotCapture.captureUIKit` via a UIKit
    /// VC factory instead of the SwiftUI capture path.
    private func generateUIKitImages(
        templateFamily: String,
        count: Int,
        startSeed: UInt64
    ) async throws {
        let manifestURL = datasetDir.appending(path: "manifest.json")
        var manifest = try DatasetManifest.load(from: manifestURL)

        for i in 0..<count {
            let seed = startSeed + UInt64(i)
            let state = simulatorStates[i % simulatorStates.count]
            let config = makeConfig(seed: seed, index: i, templateFamily: templateFamily, state: state)

            let result = try await captureUIKit(templateFamily: templateFamily, seed: seed, config: config)

            let imageIndex = manifest.imageCount + 1
            let split = splitFor(imageIndex: imageIndex)
            let baseName = String(format: "img_%06d", imageIndex)
            let pngName  = baseName + ".png"
            let jsonName = baseName + ".json"

            let splitDir = datasetDir.appending(path: split.rawValue, directoryHint: .isDirectory)
            try result.png.write(to: splitDir.appending(path: pngName))
            try AnnotationWriter.write(
                result: result,
                config: config,
                imageFileName: pngName,
                templateFamily: templateFamily,
                generatorVersion: "0.1.0",
                to: splitDir.appending(path: jsonName)
            )

            let entry = ManifestEntry(
                fileName: "\(split.rawValue)/\(pngName)",
                split: split,
                sha256: result.sha256,
                templateFamily: templateFamily,
                generatorSeed: seed,
                simulatorState: state,
                isolationTemplate: config.isolationTemplate,
                lowDensity: config.lowDensity,
                deviceName: config.deviceName,
                pixelScale: config.pixelScale
            )
            manifest.append(entry, elementTypes: result.elements.map(\.elementType))
        }

        try manifest.save(to: manifestURL)
    }

    /// Dispatches to the correct UIKit VC factory and calls `captureUIKit`.
    private func captureUIKit(
        templateFamily: String,
        seed: UInt64,
        config: GeneratorRunConfig
    ) async throws -> CaptureResult {
        switch templateFamily {
        case "UIKitForm":
            let vc = UIKitFormViewController(seed: seed, config: config)
            return try await ScreenshotCapture.captureUIKit(vc, config: config)
        case "UIKitList":
            let vc = UIKitListViewController(seed: seed, config: config)
            return try await ScreenshotCapture.captureUIKit(vc, config: config)
        case "UIKitControls":
            let vc = UIKitControlsViewController(seed: seed, config: config)
            return try await ScreenshotCapture.captureUIKit(vc, config: config)
        default:
            throw GenerateDatasetError.unknownTemplateFamily(templateFamily)
        }
    }

    // MARK: - Phase 5b: Extended SwiftUI templates

    /// Generates 400 tab-view-navigation template images (seeds 8101–8500).
    /// Annotates tabBar (auto), navigationBar (auto), homeIndicator, dynamicIsland.
    func testGenerateTabViewNavigationImages() async throws {
        try await generateImages(templateFamily: "TabViewNavigation", count: 400, startSeed: 8101)
    }

    /// Generates 400 sheet / half-sheet template images (seeds 8501–8900).
    /// Annotates sheet, primaryButton, cancelAction, label.
    /// Height variants: full (~90%), half (~50%), third (~35%).
    func testGenerateSheetImages() async throws {
        try await generateImages(templateFamily: "Sheet", count: 400, startSeed: 8501)
    }

    /// Generates 400 search results template images (seeds 8901–9300).
    /// Annotates searchField, navigationBar (auto), listRow, label.
    func testGenerateSearchResultsImages() async throws {
        try await generateImages(templateFamily: "SearchResults", count: 400, startSeed: 8901)
    }

    /// Generates 400 form-with-validation template images (seeds 9301–9700).
    /// Annotates textField, secureField, toggle, primaryButton, label.
    /// ~25% of images show inline validation error states.
    func testGenerateFormValidationImages() async throws {
        try await generateImages(templateFamily: "FormValidation", count: 400, startSeed: 9301)
    }

    /// Generates 400 empty state template images (seeds 9701–10100).
    /// Annotates primaryButton, imageView, label.
    func testGenerateEmptyStateImages() async throws {
        try await generateImages(templateFamily: "EmptyState", count: 400, startSeed: 9701)
    }

    /// Generates 400 loading / skeleton state template images (seeds 10101–10500).
    /// Annotates activityIndicator, progressView, listRow (skeleton rows).
    func testGenerateLoadingSkeletonImages() async throws {
        try await generateImages(templateFamily: "LoadingSkeleton", count: 400, startSeed: 10101)
    }

    /// Generates 400 media card grid template images (seeds 10501–10900).
    /// Annotates collectionItem, imageView, label.
    /// Column count varies between 2 and 3; card count 4–9.
    func testGenerateMediaCardGridImages() async throws {
        try await generateImages(templateFamily: "MediaCardGrid", count: 400, startSeed: 10501)
    }

    /// Generates 400 onboarding page template images (seeds 10901–11300).
    /// Annotates pageControl, primaryButton, imageView, label.
    func testGenerateOnboardingPageImages() async throws {
        try await generateImages(templateFamily: "OnboardingPage", count: 400, startSeed: 10901)
    }

    /// Generates 400 picker / date entry template images (seeds 11301–11700).
    /// Annotates picker, navigationBar (auto), primaryButton, cancelAction.
    /// Picker style varies: wheel, compact, graphical.
    func testGeneratePickerDateEntryImages() async throws {
        try await generateImages(templateFamily: "PickerDateEntry", count: 400, startSeed: 11301)
    }

    /// Generates 400 action sheet template images (seeds 11701–12100).
    /// Annotates actionSheet, destructiveButton, cancelAction.
    func testGenerateActionSheetImages() async throws {
        try await generateImages(templateFamily: "ActionSheet", count: 400, startSeed: 11701)
    }

    /// Generates 400 popover template images (seeds 12101–12500).
    /// Annotates popover, label, secondaryButton.
    /// Popover anchor position varies: top, mid, bottom.
    func testGeneratePopoverImages() async throws {
        try await generateImages(templateFamily: "Popover", count: 400, startSeed: 12101)
    }

    /// Generates 400 RTL mirror template images (seeds 12501–12900).
    /// Same elements as Phase 3c templates; forced right-to-left layout.
    /// locale: ar_SA; layoutDirection: .rtl.
    func testGenerateRTLMirrorImages() async throws {
        try await generateImages(
            templateFamily: "RTLMirror", count: 400, startSeed: 12501,
            locale: "ar_SA", layoutDirection: .rtl
        )
    }

    /// Generates 400 Liquid Glass iOS 26 navbar template images (seeds 12901–13300).
    /// Forces .ios26 OSVisualProfile for Liquid Glass rendering.
    func testGenerateLiquidGlassNavImages() async throws {
        try await generateImages(templateFamily: "LiquidGlassNav", count: 400, startSeed: 12901,
                                 forceProfile: .ios26)
    }

    /// Generates 400 Liquid Glass iOS 26 tabbar template images (seeds 13301–13700).
    /// Forces .ios26 OSVisualProfile for Liquid Glass tab bar rendering.
    func testGenerateLiquidGlassTabImages() async throws {
        try await generateImages(templateFamily: "LiquidGlassTab", count: 400, startSeed: 13301,
                                 forceProfile: .ios26)
    }

    /// Generates 400 settings-with-disclosure-groups template images (seeds 13701–14100).
    /// Annotates navigationBar (auto), disclosureGroup, listRow, toggle, label.
    func testGenerateSettingsDisclosureImages() async throws {
        try await generateImages(templateFamily: "SettingsDisclosure", count: 400, startSeed: 13701)
    }

    /// Generates 400 refresh control in list template images (seeds 14101–14500).
    /// Annotates navigationBar (auto), listRow, refreshControl.
    func testGenerateRefreshControlImages() async throws {
        try await generateImages(templateFamily: "RefreshControl", count: 400, startSeed: 14101)
    }

    /// Generates 400 context menu template images (seeds 14501–14900).
    /// Annotates contextMenu, listRow, label.
    func testGenerateContextMenuImages() async throws {
        try await generateImages(templateFamily: "ContextMenu", count: 400, startSeed: 14501)
    }

    /// Generates 400 map with overlays template images (seeds 14901–15300).
    /// Annotates mapView, navigationBar (auto), primaryButton.
    func testGenerateMapOverlaysImages() async throws {
        try await generateImages(templateFamily: "MapOverlays", count: 400, startSeed: 14901)
    }

    /// Generates 400 stepper + quantity controls template images (seeds 15301–15700).
    /// Annotates stepperControl, label, navigationBar (auto).
    func testGenerateStepperImages() async throws {
        try await generateImages(templateFamily: "Stepper", count: 400, startSeed: 15301)
    }

    /// Generates 400 progress + activity combined template images (seeds 15701–16100).
    /// Annotates progressView, activityIndicator, label, cancelAction.
    func testGenerateProgressActivityImages() async throws {
        try await generateImages(templateFamily: "ProgressActivity", count: 400, startSeed: 15701)
    }

    // MARK: - Phase 5b-22: Gap-filling templates (families 38–50, seeds 24001–26600)

    /// Generates 200 color picker / color well images (seeds 24001–24200).
    /// Covers colorWell — a class absent from all prior templates.
    func testGenerateColorPickerImages() async throws {
        try await generateImages(templateFamily: "ColorPicker", count: 200, startSeed: 24001)
    }

    /// Generates 200 menu button (pull-down) template images (seeds 24201–24400).
    /// Covers menuButton — SwiftUI Menu trigger in closed state.
    func testGenerateMenuButtonImages() async throws {
        try await generateImages(templateFamily: "MenuButton", count: 200, startSeed: 24201)
    }

    /// Generates 200 link / rich-text article images (seeds 24401–24600).
    /// Covers link — tappable URL text embedded in scrollable content.
    func testGenerateLinkRichTextImages() async throws {
        try await generateImages(templateFamily: "LinkRichText", count: 200, startSeed: 24401)
    }

    /// Generates 200 multi-slider panel images (seeds 24601–24800).
    /// Covers slider in a SwiftUI-native multi-row panel (distinct from UIKitControls).
    func testGenerateSliderPanelImages() async throws {
        try await generateImages(templateFamily: "SliderPanel", count: 200, startSeed: 24601)
    }

    /// Generates 200 segmented control + filter list images (seeds 24801–25000).
    /// Covers segmentedControl driving a filtered list — SwiftUI Picker(.segmented).
    func testGenerateSegmentedFilterImages() async throws {
        try await generateImages(templateFamily: "SegmentedFilter", count: 200, startSeed: 24801)
    }

    /// Generates 200 card detail (full-bleed header) images (seeds 25001–25200).
    /// No NavigationStack — teaches model to detect elements outside nav-bar context.
    func testGenerateCardDetailImages() async throws {
        try await generateImages(templateFamily: "CardDetail", count: 200, startSeed: 25001)
    }

    /// Generates 200 multi-section form images (seeds 25201–25400).
    /// textField + secureField + picker (inline) + stepperControl + toggle in one screen.
    func testGenerateMultiSectionFormImages() async throws {
        try await generateImages(templateFamily: "MultiSectionForm", count: 200, startSeed: 25201)
    }

    /// Generates 200 toolbar actions images (seeds 25401–25600).
    /// Covers bottom UIToolbar auto-detected alongside navigationBar.
    func testGenerateToolbarActionsImages() async throws {
        try await generateImages(templateFamily: "ToolbarActions", count: 200, startSeed: 25401)
    }

    /// Generates 200 wizard step-flow images (seeds 25601–25800).
    /// Step progress bar (progressView) + textField + primaryButton + secondaryButton.
    func testGenerateWizardStepFlowImages() async throws {
        try await generateImages(templateFamily: "WizardStepFlow", count: 200, startSeed: 25601)
    }

    /// Generates 200 notification-center style images (seeds 25801–26000).
    /// Rounded notification cards (listRow) on a translucent wallpaper background.
    func testGenerateNotificationCenterImages() async throws {
        try await generateImages(templateFamily: "NotificationCenter", count: 200, startSeed: 25801)
    }

    /// Generates 200 gallery page carousel images (seeds 26001–26200).
    /// imageView + pageControl + conditionally primaryButton on last slide.
    func testGenerateGalleryPageImages() async throws {
        try await generateImages(templateFamily: "GalleryPage", count: 200, startSeed: 26001)
    }

    /// Generates 200 iPadOS sidebar split-view images (seeds 26201–26400).
    /// sidebar + listRow (sidebar rows) + imageView (detail hero).
    func testGenerateiPadSidebarImages() async throws {
        try await generateImages(templateFamily: "iPadSidebar", count: 200, startSeed: 26201)
    }

    /// Generates 200 alert-with-textField images (seeds 26401–26600).
    /// alert + textField embedded together — covers the common "input alert" iOS pattern.
    func testGenerateAlertWithTextFieldImages() async throws {
        try await generateImages(templateFamily: "AlertWithTextField", count: 200, startSeed: 26401)
    }

    /// Generates 200 dense toggle-only settings images (seeds 26601–26800).
    /// 6–12 toggles per screen with disabled variants — maximises toggle class instances.
    func testGenerateSettingsToggleDenseImages() async throws {
        try await generateImages(templateFamily: "SettingsToggleDense", count: 200, startSeed: 26601)
    }

    // MARK: - TASK-5b-21: Accessibility variant sweep
    //
    // For every template that includes navigationBar or tabBar, generate variants
    // with a single accessibility flag active. 10 templates × 50 images × 4 flags
    // = 2,000 accessibility-variant images total.
    //
    // Trait overrides applied in ScreenshotCapture.capture():
    //   boldText         → traitOverrides.legibilityWeight = .bold
    //   increaseContrast → traitOverrides.accessibilityContrast = .high
    //   reduceTransparency → traitOverrides.accessibilityContrast = .high
    //                        (nav bar renders with opaque high-contrast material)
    //   buttonShapes     → recorded in annotation metadata; UIKit system buttons
    //                       render with shape backgrounds in future UIKit pass
    //
    // Seed ranges: 20001–20500 (reduceTransparency), 21001–21500 (increaseContrast),
    //              22001–22500 (boldText), 23001–23500 (buttonShapes).
    // Each template family uses a 50-seed block within its range (base + 0*50 … 9*50).

    /// Generates 500 reduce-transparency variants (seeds 20001–20500).
    /// 50 images each for 10 nav/tab-bearing templates.
    /// Nav bar and tab bar materials render with high-contrast opaque backgrounds.
    func testGenerateReduceTransparencyVariants() async throws {
        let flags = AccessibilityFlags(reduceTransparency: true)
        try await generateImages(templateFamily: "TabViewNavigation",  count: 50, startSeed: 20001, accessibilityFlags: flags)
        try await generateImages(templateFamily: "SearchResults",       count: 50, startSeed: 20051, accessibilityFlags: flags)
        try await generateImages(templateFamily: "SettingsList",        count: 50, startSeed: 20101, accessibilityFlags: flags)
        try await generateImages(templateFamily: "PickerDateEntry",     count: 50, startSeed: 20151, accessibilityFlags: flags)
        try await generateImages(templateFamily: "LiquidGlassNav",      count: 50, startSeed: 20201, forceProfile: .ios26, accessibilityFlags: flags)
        try await generateImages(templateFamily: "LiquidGlassTab",      count: 50, startSeed: 20251, forceProfile: .ios26, accessibilityFlags: flags)
        try await generateImages(templateFamily: "SettingsDisclosure",  count: 50, startSeed: 20301, accessibilityFlags: flags)
        try await generateImages(templateFamily: "RefreshControl",      count: 50, startSeed: 20351, accessibilityFlags: flags)
        try await generateImages(templateFamily: "MapOverlays",         count: 50, startSeed: 20401, accessibilityFlags: flags)
        try await generateImages(templateFamily: "Stepper",             count: 50, startSeed: 20451, accessibilityFlags: flags)
    }

    /// Generates 500 increase-contrast variants (seeds 21001–21500).
    /// 50 images each for 10 nav/tab-bearing templates.
    /// UIKit applies high-contrast system colors; nav bar uses opaque material.
    func testGenerateIncreaseContrastVariants() async throws {
        let flags = AccessibilityFlags(increaseContrast: true)
        try await generateImages(templateFamily: "TabViewNavigation",  count: 50, startSeed: 21001, accessibilityFlags: flags)
        try await generateImages(templateFamily: "SearchResults",       count: 50, startSeed: 21051, accessibilityFlags: flags)
        try await generateImages(templateFamily: "SettingsList",        count: 50, startSeed: 21101, accessibilityFlags: flags)
        try await generateImages(templateFamily: "PickerDateEntry",     count: 50, startSeed: 21151, accessibilityFlags: flags)
        try await generateImages(templateFamily: "LiquidGlassNav",      count: 50, startSeed: 21201, forceProfile: .ios26, accessibilityFlags: flags)
        try await generateImages(templateFamily: "LiquidGlassTab",      count: 50, startSeed: 21251, forceProfile: .ios26, accessibilityFlags: flags)
        try await generateImages(templateFamily: "SettingsDisclosure",  count: 50, startSeed: 21301, accessibilityFlags: flags)
        try await generateImages(templateFamily: "RefreshControl",      count: 50, startSeed: 21351, accessibilityFlags: flags)
        try await generateImages(templateFamily: "MapOverlays",         count: 50, startSeed: 21401, accessibilityFlags: flags)
        try await generateImages(templateFamily: "Stepper",             count: 50, startSeed: 21451, accessibilityFlags: flags)
    }

    /// Generates 500 bold-text variants (seeds 22001–22500).
    /// 50 images each for 10 nav/tab-bearing templates.
    /// UIKit renders all system fonts at bold weight via traitOverrides.legibilityWeight.
    func testGenerateBoldTextVariants() async throws {
        let flags = AccessibilityFlags(boldText: true)
        try await generateImages(templateFamily: "TabViewNavigation",  count: 50, startSeed: 22001, accessibilityFlags: flags)
        try await generateImages(templateFamily: "SearchResults",       count: 50, startSeed: 22051, accessibilityFlags: flags)
        try await generateImages(templateFamily: "SettingsList",        count: 50, startSeed: 22101, accessibilityFlags: flags)
        try await generateImages(templateFamily: "PickerDateEntry",     count: 50, startSeed: 22151, accessibilityFlags: flags)
        try await generateImages(templateFamily: "LiquidGlassNav",      count: 50, startSeed: 22201, forceProfile: .ios26, accessibilityFlags: flags)
        try await generateImages(templateFamily: "LiquidGlassTab",      count: 50, startSeed: 22251, forceProfile: .ios26, accessibilityFlags: flags)
        try await generateImages(templateFamily: "SettingsDisclosure",  count: 50, startSeed: 22301, accessibilityFlags: flags)
        try await generateImages(templateFamily: "RefreshControl",      count: 50, startSeed: 22351, accessibilityFlags: flags)
        try await generateImages(templateFamily: "MapOverlays",         count: 50, startSeed: 22401, accessibilityFlags: flags)
        try await generateImages(templateFamily: "Stepper",             count: 50, startSeed: 22451, accessibilityFlags: flags)
    }

    /// Generates 500 button-shapes variants (seeds 23001–23500).
    /// 50 images each for 10 nav/tab-bearing templates.
    /// `buttonShapes: true` is recorded in annotation metadata. Future UIKit templates
    /// will add explicit shape backgrounds; SwiftUI system buttons already show shapes
    /// when legibilityWeight is elevated (co-applied here for maximum visual coverage).
    func testGenerateButtonShapesVariants() async throws {
        let flags = AccessibilityFlags(boldText: true, buttonShapes: true)
        try await generateImages(templateFamily: "TabViewNavigation",  count: 50, startSeed: 23001, accessibilityFlags: flags)
        try await generateImages(templateFamily: "SearchResults",       count: 50, startSeed: 23051, accessibilityFlags: flags)
        try await generateImages(templateFamily: "SettingsList",        count: 50, startSeed: 23101, accessibilityFlags: flags)
        try await generateImages(templateFamily: "PickerDateEntry",     count: 50, startSeed: 23151, accessibilityFlags: flags)
        try await generateImages(templateFamily: "LiquidGlassNav",      count: 50, startSeed: 23201, forceProfile: .ios26, accessibilityFlags: flags)
        try await generateImages(templateFamily: "LiquidGlassTab",      count: 50, startSeed: 23251, forceProfile: .ios26, accessibilityFlags: flags)
        try await generateImages(templateFamily: "SettingsDisclosure",  count: 50, startSeed: 23301, accessibilityFlags: flags)
        try await generateImages(templateFamily: "RefreshControl",      count: 50, startSeed: 23351, accessibilityFlags: flags)
        try await generateImages(templateFamily: "MapOverlays",         count: 50, startSeed: 23401, accessibilityFlags: flags)
        try await generateImages(templateFamily: "Stepper",             count: 50, startSeed: 23451, accessibilityFlags: flags)
    }

    // MARK: - Phase 5a: Known-bad generator (TASK-5a-10)

    /// Generates 60 truncated-label images (seeds 7001–7060).
    /// knownIssues: ["truncatedText"] on every label element.
    func testGenerateTruncatedLabelImages() async throws {
        try await generateKnownBadImages(templateFamily: "TruncatedLabel", count: 60, startSeed: 7001)
    }

    /// Generates 60 clipped-content images (seeds 7101–7160).
    /// knownIssues: ["clippedElement"] on every imageView element.
    func testGenerateClippedContentImages() async throws {
        try await generateKnownBadImages(templateFamily: "ClippedContent", count: 60, startSeed: 7101)
    }

    /// Generates 60 overlapping-controls images (seeds 7201–7260).
    /// No knownIssues — overlap flagged at Phase 7 inference time.
    func testGenerateOverlappingControlsImages() async throws {
        try await generateKnownBadImages(templateFamily: "OverlappingControls", count: 60, startSeed: 7201)
    }

    /// Generates 60 small-hit-target images (seeds 7301–7360).
    /// knownIssues: ["tappableTargetTooSmall"] on buttons with dimensions < 44pt.
    func testGenerateSmallHitTargetImages() async throws {
        try await generateKnownBadImages(templateFamily: "SmallHitTarget", count: 60, startSeed: 7301)
    }

    /// Generates 60 Dynamic Type overflow images (seeds 7401–7460).
    /// knownIssues: ["dynamicTypeOverflow"]. Uses accessibilityExtraExtraExtraLarge DT.
    func testGenerateDynamicTypeOverflowImages() async throws {
        try await generateKnownBadImages(
            templateFamily: "DynamicTypeOverflow", count: 60, startSeed: 7401,
            dynamicTypeOverride: .accessibilityExtraExtraExtraLarge
        )
    }

    /// Generates 40 RTL mirroring failure images (seeds 7501–7540).
    /// knownIssues: ["rtlMirroringFailure"]. Uses RTL layout + ar_SA locale.
    func testGenerateRTLMirroringFailureImages() async throws {
        try await generateKnownBadImages(
            templateFamily: "RTLMirroringFailure", count: 40, startSeed: 7501,
            layoutDirection: .rtl, locale: "ar_SA"
        )
    }

    /// Generates 60 off-screen element images (seeds 7601–7660).
    /// Off-screen rows excluded; partial row annotated via scroll viewport filter.
    func testGenerateOffScreenElementImages() async throws {
        try await generateKnownBadImages(templateFamily: "OffScreenElement", count: 60, startSeed: 7601)
    }

    /// Generates 60 occluded-element images (seeds 7701–7760).
    /// Sheet annotated as `sheet`; partially covered buttons annotated with full frame.
    func testGenerateOccludedElementImages() async throws {
        try await generateKnownBadImages(templateFamily: "OccludedElement", count: 60, startSeed: 7701)
    }

    /// Generates 40 loading-overlay hard-negative images (seeds 7801–7840).
    /// elements: [] — model should produce no detections.
    func testGenerateHardNegativeLoadingImages() async throws {
        try await generateKnownBadImages(
            templateFamily: "HardNegative_1", count: 40, startSeed: 7801,
            hardNegativeSplit: true
        )
    }

    /// Generates 40 WKWebView hard-negative images (seeds 7901–7940).
    /// elements: [webContent] — exactly one webContent annotation.
    func testGenerateHardNegativeWebContentImages() async throws {
        try await generateKnownBadImages(
            templateFamily: "HardNegative_2", count: 40, startSeed: 7901,
            hardNegativeSplit: true
        )
    }

    /// Generates 40 decorative-fill hard-negative images (seeds 8001–8040).
    /// elements: [] — model should produce no detections.
    func testGenerateHardNegativeDecorativeImages() async throws {
        try await generateKnownBadImages(
            templateFamily: "HardNegative_3", count: 40, startSeed: 8001,
            hardNegativeSplit: true
        )
    }

    // MARK: - Known-bad generation loop (Phase 5a)

    /// Generates `count` known-bad UIKit images for the given template family.
    ///
    /// - Parameters:
    ///   - templateFamily: One of the Phase 5a known-bad family names.
    ///   - count: Number of images to generate.
    ///   - startSeed: First seed value.
    ///   - dynamicTypeOverride: If non-nil, use this DT size instead of the standard cycle.
    ///   - layoutDirection: If non-nil, force this layout direction.
    ///   - locale: Locale override (defaults to "en_US").
    ///   - hardNegativeSplit: If true, use 70% train / 30% validation split (no test split).
    private func generateKnownBadImages(
        templateFamily: String,
        count: Int,
        startSeed: UInt64,
        dynamicTypeOverride: GeneratorDynamicTypeSize? = nil,
        layoutDirection: GeneratorLayoutDirection = .ltr,
        locale: String = "en_US",
        hardNegativeSplit: Bool = false
    ) async throws {
        let manifestURL = datasetDir.appending(path: "manifest.json")
        var manifest = try DatasetManifest.load(from: manifestURL)

        for i in 0..<count {
            let seed = startSeed + UInt64(i)
            let state = simulatorStates[i % simulatorStates.count]

            let dtSize = dynamicTypeOverride ?? dynamicTypeSize(for: i)
            let config = makeKnownBadConfig(
                seed: seed, index: i, templateFamily: templateFamily, state: state,
                dynamicTypeSize: dtSize, layoutDirection: layoutDirection, locale: locale
            )

            let result = try await captureKnownBad(
                templateFamily: templateFamily, seed: seed, config: config
            )

            let imageIndex = manifest.imageCount + 1
            let split = hardNegativeSplit
                ? hardNegativeSplitFor(imageIndex: imageIndex)
                : splitFor(imageIndex: imageIndex)
            let baseName = String(format: "img_%06d", imageIndex)
            let pngName  = baseName + ".png"
            let jsonName = baseName + ".json"

            let splitDir = datasetDir.appending(path: split.rawValue, directoryHint: .isDirectory)
            try result.png.write(to: splitDir.appending(path: pngName))
            try AnnotationWriter.write(
                result: result,
                config: config,
                imageFileName: pngName,
                templateFamily: templateFamily,
                generatorVersion: "0.1.0",
                to: splitDir.appending(path: jsonName)
            )

            let entry = ManifestEntry(
                fileName: "\(split.rawValue)/\(pngName)",
                split: split,
                sha256: result.sha256,
                templateFamily: templateFamily,
                generatorSeed: seed,
                simulatorState: state,
                isolationTemplate: config.isolationTemplate,
                lowDensity: config.lowDensity,
                deviceName: config.deviceName,
                pixelScale: config.pixelScale
            )
            manifest.append(entry, elementTypes: result.elements.map(\.elementType))
        }

        try manifest.save(to: manifestURL)
    }

    /// Dispatches to the correct known-bad VC factory.
    private func captureKnownBad(
        templateFamily: String,
        seed: UInt64,
        config: GeneratorRunConfig
    ) async throws -> CaptureResult {
        switch templateFamily {
        case "TruncatedLabel":
            let vc = TruncatedLabelViewController(seed: seed, config: config)
            return try await ScreenshotCapture.captureUIKit(vc, config: config)
        case "ClippedContent":
            let vc = ClippedContentViewController(seed: seed, config: config)
            return try await ScreenshotCapture.captureUIKit(vc, config: config)
        case "OverlappingControls":
            let vc = OverlappingControlsViewController(seed: seed, config: config)
            return try await ScreenshotCapture.captureUIKit(vc, config: config)
        case "SmallHitTarget":
            let vc = SmallHitTargetViewController(seed: seed, config: config)
            return try await ScreenshotCapture.captureUIKit(vc, config: config)
        case "DynamicTypeOverflow":
            let vc = DynamicTypeOverflowViewController(seed: seed, config: config)
            return try await ScreenshotCapture.captureUIKit(vc, config: config)
        case "RTLMirroringFailure":
            let vc = RTLMirroringFailureViewController(seed: seed, config: config)
            return try await ScreenshotCapture.captureUIKit(vc, config: config)
        case "OffScreenElement":
            let vc = OffScreenElementViewController(seed: seed, config: config)
            return try await ScreenshotCapture.captureUIKit(vc, config: config)
        case "OccludedElement":
            let vc = OccludedElementViewController(seed: seed, config: config)
            return try await ScreenshotCapture.captureUIKit(vc, config: config)
        case "HardNegative_1":
            let vc = HardNegativeViewController(type: .loadingOverlay, seed: seed, config: config)
            return try await ScreenshotCapture.captureUIKit(vc, config: config)
        case "HardNegative_2":
            // WKWebView needs extra stabilisation time beyond the standard 150ms.
            // Sleep an additional 500ms before capture to allow HTML to render.
            try await Task.sleep(for: .milliseconds(500))
            let vc = HardNegativeViewController(type: .webContent, seed: seed, config: config)
            return try await ScreenshotCapture.captureUIKit(vc, config: config)
        case "HardNegative_3":
            let vc = HardNegativeViewController(type: .decorativeFill, seed: seed, config: config)
            return try await ScreenshotCapture.captureUIKit(vc, config: config)
        default:
            throw GenerateDatasetError.unknownTemplateFamily(templateFamily)
        }
    }

    /// Builds a `GeneratorRunConfig` for a known-bad template image.
    private func makeKnownBadConfig(
        seed: UInt64,
        index: Int,
        templateFamily: String,
        state: SimulatorStateOverride,
        dynamicTypeSize: GeneratorDynamicTypeSize,
        layoutDirection: GeneratorLayoutDirection,
        locale: String
    ) -> GeneratorRunConfig {
        let highDPI = index % 2 == 0
        let osProfile: OSVisualProfile = highDPI ? .ios26 : .ios17
        let deviceName = highDPI ? "iPhone 17 Pro" : "iPhone SE (3rd generation)"
        let pixelScale = highDPI ? 3 : 2

        return GeneratorRunConfig(
            seed: seed,
            templateFamily: templateFamily,
            osProfile: osProfile,
            simulatorOverride: state,
            colorScheme: index % 2 == 0 ? .dark : .light,
            dynamicTypeSize: dynamicTypeSize,
            deviceName: deviceName,
            pixelScale: pixelScale,
            locale: locale,
            layoutDirection: layoutDirection,
            accessibilityFlags: .default
        )
    }

    /// Hard-negative split: 70% train, 30% validation (no test split).
    /// Per spec: "Hard negatives are distributed evenly: 30% in validation, 70% in train."
    private func hardNegativeSplitFor(imageIndex: Int) -> DatasetSplit {
        // Roughly 3 in 10 go to validation
        return (imageIndex % 10) < 3 ? .validation : .train
    }

    // MARK: - Helpers

    /// Assigns a `DatasetSplit` based on a 10-bucket rotation: 80% train, 10% validation, 10% test.
    private func splitFor(imageIndex: Int) -> DatasetSplit {
        switch imageIndex % 10 {
        case 0:         return .test
        case 9:         return .validation
        default:        return .train
        }
    }

    /// Cycles through 6 `GeneratorDynamicTypeSize` values based on the image index.
    private func dynamicTypeSize(for index: Int) -> GeneratorDynamicTypeSize {
        let sizes: [GeneratorDynamicTypeSize] = [
            .medium, .large, .xLarge,
            .accessibilityMedium, .xxLarge, .small
        ]
        return sizes[index % sizes.count]
    }

    // MARK: - TASK-5b-22: Balance report (runs last alphabetically)

    /// Generates `reports/dataset_balance.md` from the completed manifest.
    ///
    /// Runs last alphabetically so it sees the full manifest from all prior test methods.
    /// Writes `balance_report.md` to the dataset directory for retrieval via
    /// `xcrun simctl get_app_container` after the test run completes.
    func testZZZWriteBalanceReport() throws {
        let manifestURL = datasetDir.appending(path: "manifest.json")
        let manifest = try DatasetManifest.load(from: manifestURL)

        let reportURL = datasetDir.appending(path: "balance_report.md")
        try BalanceReport.write(from: manifest, to: reportURL)

        // Also attach to the test result for inline review in Xcode
        let content = BalanceReport.generate(from: manifest)
        let attachment = XCTAttachment(string: content)
        attachment.name = "dataset_balance.md"
        attachment.lifetime = .keepAlways
        add(attachment)

        // Warn (do not fail) if the imbalance ratio exceeds 5:1.
        // The 5:1 ceiling is a pre-training gate (DS-G1), not a generation gate —
        // subsampling is applied to the training split before Phase 6, not here.
        if let ratio = manifest.imbalanceRatio, ratio > 5.0 {
            let underrep = manifest.underrepresented(floor: BalanceReport.defaultFloor)
            let warning = "⚠️ Imbalance ratio \(String(format: "%.1f", ratio)):1 exceeds 5:1 ceiling. " +
                "Under-represented classes: \(underrep.joined(separator: ", ")). " +
                "Apply subsampling before Phase 6 training (DS-G1)."
            print(warning)
            // Record as an expectation so the warning surfaces in the test report
            // without blocking the CI green status for generation runs.
            XCTExpectFailure(warning) {
                XCTAssertLessThanOrEqual(ratio, 5.0)
            }
        }
    }
}

// MARK: - GenerateDatasetError

/// Errors produced by `GenerateDatasetTests`.
enum GenerateDatasetError: Error, CustomStringConvertible {
    case unknownTemplateFamily(String)

    var description: String {
        switch self {
        case .unknownTemplateFamily(let family):
            return "Unknown template family '\(family)'. Expected: LoginForm, SettingsList, Alert, UIKitForm, UIKitList, UIKitControls, TruncatedLabel, ClippedContent, OverlappingControls, SmallHitTarget, DynamicTypeOverflow, RTLMirroringFailure, OffScreenElement, OccludedElement, HardNegative_1/2/3, TabViewNavigation, Sheet, SearchResults, FormValidation, EmptyState, LoadingSkeleton, MediaCardGrid, OnboardingPage, PickerDateEntry, ActionSheet, Popover, RTLMirror, LiquidGlassNav, LiquidGlassTab, SettingsDisclosure, RefreshControl, ContextMenu, MapOverlays, Stepper, ProgressActivity, ColorPicker, MenuButton, LinkRichText, SliderPanel, SegmentedFilter, CardDetail, MultiSectionForm, ToolbarActions, WizardStepFlow, NotificationCenter, GalleryPage, iPadSidebar, AlertWithTextField, SettingsToggleDense. A11y variants use the same family names."
        }
    }
}
