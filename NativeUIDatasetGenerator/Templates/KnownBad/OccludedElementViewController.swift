// OccludedElementViewController.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// TASK-5a-8: Known-bad template — occluded element failure mode.
//
// Renders a base layer of UIButton controls partially covered by a sheet-style
// UIView. Demonstrates the "sheet occludes underlying controls" pattern.
//
// Occlusion tiers (per Phase 1 rules P2/P3):
//   Tier A — 20–80% visible: annotated with occluded: true, clipped box
//             (captureUIKit computes actual visible frame via convert)
//   Tier B — <20% visible: excluded: true, exclusionReason: "insufficient_visible_area"
//   Sheet itself: annotated normally as `sheet`
//
// Layout:
//   - 4 base UIButton rows stacked from top
//   - A half-height sheet UIView covers the bottom 55% of the screen
//     → Row 0 (topmost): fully visible (annotated normally, no occluded flag)
//     → Row 1: partially visible, ~40% height shows (Tier A — occluded)
//     → Row 2: very little visible, ~8% (Tier B — excluded from annotation)
//     → Row 3: fully covered (excluded)
//   - Sheet view is added on top of buttons
//
// Since UIKitCaptureSupport reads frames via UIView.convert(_:to:), the returned
// frame for each button is its full layout frame (not clipped). The annotation
// layer must mark partial buttons as occluded=true and clip the box to the screen
// boundary. For Tier B, we simply omit the element from annotatedViews.
//
// Implementation note: We detect occlusion at annotation time by comparing each
// button's frame to the sheet's top edge. The sheet's top edge is known at layout.
//
// Annotated elements:
//   primaryButton (×1) — fully visible, no occluded flag
//   primaryButton (×1) — Tier A occluded (20–80% visible), returned from annotatedViews
//                         but with a note; occluded=true set by GeneratorRunner post-process
//   sheet (×1)         — the sheet itself, annotated normally

import UIKit

// MARK: - OccludedElementViewController

@MainActor
public final class OccludedElementViewController: UIViewController, UIKitAnnotatable {

    // MARK: - Types

    private enum OcclusionTier {
        case fullyVisible       // annotate normally
        case partiallyVisible   // 20–80% visible — annotate as occluded
        case mostlyCovered      // <20% visible — exclude
        case fullyCovered       // 0% visible — exclude
    }

    private struct ButtonRow {
        let button: UIButton
        let title: String
        var tier: OcclusionTier = .fullyVisible
    }

    // MARK: - State

    private let seed: UInt64
    private let runConfig: GeneratorRunConfig
    private var buttonRows: [ButtonRow] = []
    private var sheetView: UIView!
    private var sheetTopY: CGFloat = 0

    private static let rowCount = 4
    private static let rowHeight: CGFloat = 56
    private static let rowGap: CGFloat = 16

    // MARK: - Init

    public init(seed: UInt64, config: GeneratorRunConfig) {
        self.seed = seed
        self.runConfig = config
        super.init(nibName: nil, bundle: nil)
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) { fatalError("init(coder:) not used") }

    // MARK: - UIViewController

    public override func viewDidLoad() {
        super.viewDidLoad()
        UIView.setAnimationsEnabled(false)
        overrideUserInterfaceStyle = runConfig.colorScheme == .dark ? .dark : .light
        view.backgroundColor = .systemBackground
        setupButtons()
        setupSheet()
    }

    public override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        layoutContent()
    }

    // MARK: - UIKitAnnotatable

    public var annotatedViews: [UIKitAnnotatedView] {
        var result: [UIKitAnnotatedView] = []

        for (i, row) in buttonRows.enumerated() {
            switch row.tier {
            case .fullyVisible, .partiallyVisible:
                // Both tiers are included in annotatedViews.
                // The captureUIKit frame calculation returns the full button frame.
                // The GeneratorRunner post-process step sets occluded=true for partiallyVisible.
                // For this VC we annotate both; the distinction is in the tier metadata.
                result.append(UIKitAnnotatedView(
                    id: "primaryButton_occluded_\(i)",
                    elementType: "primaryButton",
                    view: row.button,
                    visibleText: row.title,
                    knownIssues: []
                ))
            case .mostlyCovered, .fullyCovered:
                // Tier B + fully covered: exclude per P3 rule (< 20% visible)
                break
            }
        }

        // Sheet is always annotated (it's the occluding element, fully visible)
        if let sheet = sheetView {
            result.append(UIKitAnnotatedView(
                id: "sheet_occluder",
                elementType: "sheet",
                view: sheet,
                knownIssues: []
            ))
        }

        return result
    }

    // MARK: - Setup

    private func setupButtons() {
        var corpus = ContentCorpus(seed: seed)
        let hues: [CGFloat] = [0.55, 0.10, 0.33, 0.70]

        for i in 0..<Self.rowCount {
            let tint = UIColor(hue: hues[i], saturation: 0.75, brightness: 0.85, alpha: 1)
            let title = corpus.personName()

            var cfg = UIButton.Configuration.filled()
            cfg.baseBackgroundColor = tint
            cfg.baseForegroundColor = .white
            cfg.title = title
            cfg.cornerStyle = .fixed

            let button = UIButton(configuration: cfg)
            button.layer.cornerRadius = 8
            button.clipsToBounds = true
            view.addSubview(button)

            buttonRows.append(ButtonRow(button: button, title: title))
        }
    }

    private func setupSheet() {
        sheetView = UIView()
        sheetView.backgroundColor = runConfig.colorScheme == .dark
            ? UIColor.systemGray5
            : UIColor.systemBackground
        sheetView.layer.cornerRadius = 16
        sheetView.layer.maskedCorners = [.layerMinXMinYCorner, .layerMaxXMinYCorner]
        sheetView.layer.shadowColor = UIColor.black.cgColor
        sheetView.layer.shadowOpacity = 0.15
        sheetView.layer.shadowRadius = 8
        sheetView.layer.shadowOffset = CGSize(width: 0, height: -2)

        // Add drag handle
        let handle = UIView()
        handle.backgroundColor = UIColor.systemGray3
        handle.layer.cornerRadius = 2.5
        sheetView.addSubview(handle)
        handle.frame = CGRect(x: 0, y: 0, width: 36, height: 5)

        // Add a visible title label inside the sheet
        let titleLabel = UILabel()
        titleLabel.text = "Sheet Content"
        titleLabel.font = .systemFont(ofSize: 17, weight: .semibold)
        titleLabel.textColor = .label
        titleLabel.textAlignment = .center
        sheetView.addSubview(titleLabel)

        view.addSubview(sheetView)  // on top of buttons
    }

    // MARK: - Layout

    private func layoutContent() {
        let safeTop = runConfig.osProfile.safeAreaTopInset
        let screenW = view.bounds.width
        let screenH = view.bounds.height
        let buttonW = screenW - 32

        // Layout buttons from top of safe area
        var y = safeTop + 24

        for i in 0..<buttonRows.count {
            buttonRows[i].button.frame = CGRect(
                x: 16, y: y,
                width: buttonW, height: Self.rowHeight
            )
            y += Self.rowHeight + Self.rowGap
        }

        // Sheet covers bottom 55% of screen
        let sheetH = screenH * 0.55
        sheetTopY = screenH - sheetH
        sheetView.frame = CGRect(x: 0, y: sheetTopY, width: screenW, height: sheetH)

        // Update drag handle and title positions
        if let handle = sheetView.subviews.first {
            handle.frame = CGRect(
                x: (screenW - 36) / 2, y: 10,
                width: 36, height: 5
            )
        }
        if let titleLabel = sheetView.subviews.last as? UILabel {
            titleLabel.frame = CGRect(x: 16, y: 28, width: screenW - 32, height: 24)
        }

        // Compute occlusion tiers based on how much of each button is below sheetTopY
        for i in 0..<buttonRows.count {
            let btnFrame = buttonRows[i].button.frame
            let btnBottom = btnFrame.maxY
            let btnTop    = btnFrame.minY

            if btnBottom <= sheetTopY {
                buttonRows[i].tier = .fullyVisible
            } else if btnTop >= sheetTopY {
                // Entire button is below sheet top → fully covered (0% visible)
                buttonRows[i].tier = .fullyCovered
            } else {
                // Partially covered: visible fraction = (sheetTopY - btnTop) / rowHeight
                let visibleH = sheetTopY - btnTop
                let visibleFraction = visibleH / btnFrame.height
                buttonRows[i].tier = visibleFraction >= 0.20 ? .partiallyVisible : .mostlyCovered
            }
        }
    }
}
